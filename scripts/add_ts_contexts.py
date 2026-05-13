"""add_ts_contexts.py — Reorganize .ts files so messages live under their
enclosing-class context (matching what self.tr() passes at runtime).

Reads <location filename=... line=N/> in each <message>, looks up the enclosing
class via Python AST, and re-buckets every <message> into a <context name="...">
block. Module-level code stays under context name "FileNexusSuite" (for
FileNexusSuite.py) or "fns_help" (for fns_help.py) — the module name passed by
QCoreApplication.translate when no class context is available.

Context resolution priority (per message location):
  1. Explicit context from QCoreApplication.translate('Ctx', 'Source') — the
     'Ctx' argument is collected via AST and takes precedence. This is the
     developer's stated intent and survives regardless of enclosing scope.
  2. Enclosing class from line_to_class map — used for self.tr() and
     QT_TR_NOOP() calls, where the runtime context equals the class name.
  3. Module-level fallback — 'FileNexusSuite' / 'fns_help' / 'preview_ui'
     based on the source filename, used only when no class encloses the line
     AND no explicit translate() context is provided.

Handles two .ts groups via per-file allowed/excluded context filters:
  - fns_*.ts:  holds all contexts derived from FileNexusSuite.py and fns_help.py
               EXCEPT HelpDialog. HelpDialog self.tr() calls are also picked up
               here because fns_help.py is scanned for fns_*.ts as well (so
               LicenseDialog lands in fns_*.ts), but HelpDialog itself belongs
               to help_*.ts and is dropped via excluded_contexts.
  - help_*.ts: keeps only HelpDialog. fns_help.py also contains LicenseDialog
               self.tr() calls, but those belong to fns_*.ts and are dropped
               here via allowed_contexts.
"""

import xml.etree.ElementTree as ET
import ast
import os
import sys


def build_line_to_class(py_path):
    """Return dict: line_no → enclosing class name (or '' if module-level)."""
    with open(py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    tree = ast.parse(content)

    # For each top-level ClassDef, mark every line in [lineno, end_lineno]
    # Walk recursively so nested classes (rare in FNS) win over outer
    line_to_class = {}

    def walk(node, current=''):
        if isinstance(node, ast.ClassDef):
            new_current = node.name
            for line in range(node.lineno, (node.end_lineno or node.lineno) + 1):
                line_to_class[line] = new_current
            for child in ast.iter_child_nodes(node):
                walk(child, new_current)
        else:
            for child in ast.iter_child_nodes(node):
                walk(child, current)

    walk(tree)
    return line_to_class


def build_line_to_explicit_ctx(py_path):
    """Return dict: line_no → explicit context name from
    QCoreApplication.translate('Ctx', 'Source') calls.

    lupdate uses the first argument of QCoreApplication.translate() as the
    message context. For module-level functions where no enclosing class
    exists, this explicit context is the developer's stated intent and must
    be preserved instead of falling back to the module name.

    All lines spanned by the call expression are mapped so the result is
    robust to multi-line calls.
    """
    with open(py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    tree = ast.parse(content)

    line_to_ctx = {}

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        # Match QCoreApplication.translate('Ctx', 'Source', ...)
        func = node.func
        if not (isinstance(func, ast.Attribute)
                and func.attr == 'translate'
                and isinstance(func.value, ast.Name)
                and func.value.id == 'QCoreApplication'):
            continue
        if not node.args:
            continue
        first_arg = node.args[0]
        if not (isinstance(first_arg, ast.Constant)
                and isinstance(first_arg.value, str)):
            continue
        ctx_name = first_arg.value
        start = node.lineno
        end = getattr(node, 'end_lineno', None) or start
        for ln in range(start, end + 1):
            line_to_ctx[ln] = ctx_name

    return line_to_ctx


def reorganize_ts(ts_path, line_maps, explicit_maps=None,
                  allowed_contexts=None, excluded_contexts=None):
    """Re-bucket all <message> elements into their proper class <context>.

    A single source string can appear at multiple locations across different
    classes (e.g. 'Settings' is used in both SettingsDialog and AppSuite).
    For each such message, we duplicate it into each unique context.

    Context resolution per location:
      1. explicit_maps lookup — QCoreApplication.translate('Ctx', ...) wins
      2. line_maps lookup — enclosing class for self.tr() / QT_TR_NOOP()
      3. Module-level fallback by filename

    explicit_maps: dict {filename → {line_no → explicit ctx name}} collected
    from QCoreApplication.translate() AST analysis. None disables this lookup.

    allowed_contexts: optional set of context names to keep (whitelist). None
    means unrestricted. Used for help_*.ts where only HelpDialog should remain.

    excluded_contexts: optional set of context names to drop (blacklist). None
    means none excluded. Used for fns_*.ts to drop HelpDialog entries that
    lupdate picks up when scanning fns_help.py — HelpDialog belongs to
    help_*.ts only.

    Both filters can be combined: allowed first (keep), then excluded (drop).
    Messages whose every candidate context is filtered out are themselves
    dropped.
    """
    import copy
    tree = ET.parse(ts_path)
    root = tree.getroot()

    # Collect (context_name, message_element) pairs
    bucketed = {}  # ctx_name → list[message Element]
    # Track (ctx, source) to dedupe — Qt requires each (ctx, source) be unique
    seen = set()

    for context in list(root.findall('context')):
        old_ctx_name = context.find('name').text if context.find('name') is not None else 'FileNexusSuite'
        for message in context.findall('message'):
            s = message.find('source')
            source_text = s.text if s is not None else ''

            # Recover preserved translations:
            #   vanished:   source no longer found by lupdate (location stripped),
            #               but translation text was preserved across runs
            #   unfinished: typically Same-text heuristic match from sibling .ts
            # If translation text is intact, strip the type so Qt loads the entry.
            t = message.find('translation')
            if t is not None:
                ttype = t.attrib.get('type')
                if ttype in ('vanished', 'unfinished') and t.text:
                    del t.attrib['type']
                elif ttype == 'vanished':
                    # Truly vanished, no translation — drop
                    continue

            locs = message.findall('location')
            if not locs:
                # No location — fall back to the existing context name. This
                # mainly hits recovered-vanished entries, whose old ctx came
                # from a previous add_ts_contexts.py run and is still correct.
                ctx_set = {old_ctx_name}
            else:
                ctx_set = set()
                for loc in locs:
                    fname = os.path.basename(loc.attrib.get('filename', ''))
                    line = int(loc.attrib.get('line', '0'))
                    # Priority 1: explicit context from QCoreApplication.translate()
                    explicit_map = (explicit_maps or {}).get(fname, {})
                    if line in explicit_map:
                        ctx = explicit_map[line]
                    else:
                        # Priority 2: enclosing class
                        line_map = line_maps.get(fname, {})
                        ctx = line_map.get(line, '')
                        if not ctx:
                            # Priority 3: module-level fallback per file
                            if fname == 'FileNexusSuite.py':
                                ctx = 'FileNexusSuite'
                            elif fname == 'fns_help.py':
                                ctx = 'fns_help'
                            else:
                                ctx = 'preview_ui'
                    ctx_set.add(ctx)

            # Whitelist filter: drop contexts not in allowed_contexts.
            if allowed_contexts is not None:
                ctx_set &= allowed_contexts
            # Blacklist filter: drop contexts that are explicitly excluded.
            if excluded_contexts is not None:
                ctx_set -= excluded_contexts
            # If the resulting set is empty, the message itself is dropped.
            if not ctx_set:
                continue

            # Duplicate the message into each context, but skip duplicates of
            # (ctx, source) — Qt requires unique source per context.
            for ctx in ctx_set:
                key = (ctx, source_text)
                if key in seen:
                    continue
                seen.add(key)
                if len(ctx_set) == 1:
                    bucketed.setdefault(ctx, []).append(message)
                else:
                    bucketed.setdefault(ctx, []).append(copy.deepcopy(message))
        # Remove old context
        root.remove(context)

    # Re-emit <context> blocks in sorted order
    for ctx_name in sorted(bucketed.keys()):
        ctx_el = ET.SubElement(root, 'context')
        name_el = ET.SubElement(ctx_el, 'name')
        name_el.text = ctx_name
        for msg in bucketed[ctx_name]:
            ctx_el.append(msg)

    tree.write(ts_path, encoding='utf-8', xml_declaration=True)
    return {ctx: len(msgs) for ctx, msgs in bucketed.items()}


def main():
    py_files = ['FileNexusSuite.py', 'fns_help.py']
    line_maps = {}
    explicit_maps = {}
    for py in py_files:
        if not os.path.exists(py):
            print(f'ERROR: {py} not found')
            sys.exit(1)
        line_maps[py] = build_line_to_class(py)
        explicit_maps[py] = build_line_to_explicit_ctx(py)
        print(f'  {py}: {len(line_maps[py])} lines mapped, '
              f'{len(explicit_maps[py])} explicit translate() context(s)')

    ts_dir = 'translations_ts'
    # ts_groups: list of (prefix, allowed_contexts, excluded_contexts) tuples
    # - allowed_contexts: keep only these (whitelist), None = unrestricted
    # - excluded_contexts: drop these (blacklist), None = none excluded
    # fns_*.ts excludes HelpDialog because lupdate scans fns_help.py for both
    # .ts groups; HelpDialog entries belong to help_*.ts only.
    ts_groups = [
        ('fns',  None,            {'HelpDialog'}),
        ('help', {'HelpDialog'},  None),
    ]
    print(f'\nReorganizing .ts files in {ts_dir}/...')
    for prefix, allowed, excluded in ts_groups:
        header = f'  ── {prefix}_*.ts'
        parts = []
        if allowed is not None:
            parts.append(f'allowed: {sorted(allowed)}')
        if excluded is not None:
            parts.append(f'excluded: {sorted(excluded)}')
        if parts:
            header += f'  ({" / ".join(parts)})'
        print(header)
        for lang in ['ko', 'en', 'ja', 'zh_cn', 'zh_tw']:
            ts_path = os.path.join(ts_dir, f'{prefix}_{lang}.ts')
            if not os.path.exists(ts_path):
                print(f'    {lang}: SKIP (file not found)')
                continue
            ctx_counts = reorganize_ts(ts_path, line_maps,
                                       explicit_maps=explicit_maps,
                                       allowed_contexts=allowed,
                                       excluded_contexts=excluded)
            total = sum(ctx_counts.values())
            n_contexts = len(ctx_counts)
            print(f'    {lang}: {total} messages across {n_contexts} contexts')
            # Show top 5 contexts by message count
            for ctx, n in sorted(ctx_counts.items(), key=lambda x: -x[1])[:5]:
                print(f'        {n:4d}  {ctx}')


if __name__ == '__main__':
    main()
