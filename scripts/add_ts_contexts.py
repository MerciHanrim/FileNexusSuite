"""add_ts_contexts.py — Reorganize .ts files so messages live under their
enclosing-class context (matching what self.tr() passes at runtime).

Reads <location filename=... line=N/> in each <message>, looks up the enclosing
class via Python AST, and re-buckets every <message> into a <context name="...">
block. Module-level code stays under context name "FileNexusSuite" (the module
name passed by QCoreApplication.translate when no class context is available).
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


def reorganize_ts(ts_path, line_maps):
    """Re-bucket all <message> elements into their proper class <context>.

    A single source string can appear at multiple locations across different
    classes (e.g. 'Settings' is used in both SettingsDialog and AppSuite).
    For each such message, we duplicate it into each unique context.
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
                    line_map = line_maps.get(fname, {})
                    ctx = line_map.get(line, '')
                    if not ctx:
                        ctx = 'FileNexusSuite' if fname == 'FileNexusSuite.py' else 'preview_ui'
                    ctx_set.add(ctx)

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
    py_files = ['FileNexusSuite.py']
    line_maps = {}
    for py in py_files:
        if not os.path.exists(py):
            print(f'ERROR: {py} not found')
            sys.exit(1)
        line_maps[py] = build_line_to_class(py)
        print(f'  {py}: {len(line_maps[py])} lines mapped')

    ts_dir = 'translations_ts'
    print(f'\nReorganizing .ts files in {ts_dir}/...')
    for lang in ['ko', 'en', 'ja', 'zh_cn', 'zh_tw']:
        ts_path = os.path.join(ts_dir, f'fns_{lang}.ts')
        ctx_counts = reorganize_ts(ts_path, line_maps)
        total = sum(ctx_counts.values())
        n_contexts = len(ctx_counts)
        print(f'  {lang}: {total} messages across {n_contexts} contexts')
        # Show top 5 contexts by message count
        for ctx, n in sorted(ctx_counts.items(), key=lambda x: -x[1])[:5]:
            print(f'      {n:4d}  {ctx}')


if __name__ == '__main__':
    main()
