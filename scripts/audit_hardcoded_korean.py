"""Audit hardcoded Korean string literals in FileNexusSuite.py.

Reports string literals containing Korean characters (U+AC00..U+D7A3)
that are NOT wrapped in tr()/self.tr()/QT_TR_NOOP/QCoreApplication.translate().
Such strings will not be translated at runtime and represent i18n defects.

Excludes:
  - Docstrings (module, class, function)
  - String literals that ARE arguments to translation calls
  - Strings inside Korean-named variables that look like data dicts (best effort)
"""
import ast
import re
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / 'FileNexusSuite.py'
KOREAN_RE = re.compile(r'[\uAC00-\uD7A3]')

TRANSLATION_CALLS = {
    'tr',           # self.tr(), tr()
    'QT_TR_NOOP',   # QT_TR_NOOP(...)
    'translate',    # QCoreApplication.translate(...)
}


def is_translation_call(node):
    """Check if a Call node is a translation function/method."""
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if isinstance(func, ast.Attribute):
        return func.attr in TRANSLATION_CALLS
    if isinstance(func, ast.Name):
        return func.id in TRANSLATION_CALLS
    return False


def collect_translated_strings(tree):
    """Collect ids of Constant nodes that are arguments to translation calls."""
    translated = set()  # id() of ast.Constant nodes

    class Visitor(ast.NodeVisitor):
        def visit_Call(self, node):
            if is_translation_call(node):
                # All string literal args are considered translated
                # For translate(): args are (context, source, ...); source is arg[1]
                # For tr()/QT_TR_NOOP: source is arg[0]
                # Either way, all string constants in args are wrapped
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        translated.add(id(arg))
                    # Also handle JoinedStr (f-strings) — they shouldn't be in
                    # tr() calls normally, but if they are, mark them too
            self.generic_visit(node)

    Visitor().visit(tree)
    return translated


def collect_docstring_nodes(tree):
    """Collect ids of Constant nodes that are docstrings."""
    docstring_ids = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            if (node.body and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)):
                docstring_ids.add(id(node.body[0].value))
    return docstring_ids


def find_enclosing_class_func(tree, lineno):
    """Find the nearest enclosing class.function for a given line."""
    best_cls = None
    best_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if hasattr(node, 'end_lineno') and node.lineno <= lineno <= node.end_lineno:
                best_cls = node.name
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if hasattr(node, 'end_lineno') and node.lineno <= lineno <= node.end_lineno:
                best_func = node.name
    return best_cls, best_func


def main():
    src = TARGET.read_text(encoding='utf-8')
    tree = ast.parse(src)

    translated_ids = collect_translated_strings(tree)
    docstring_ids = collect_docstring_nodes(tree)

    defects = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        if not KOREAN_RE.search(node.value):
            continue
        if id(node) in translated_ids:
            continue
        if id(node) in docstring_ids:
            continue
        defects.append(node)

    # Sort by line number
    defects.sort(key=lambda n: n.lineno)

    print(f"FileNexusSuite.py — Korean hardcode audit (Phase 3, v1.1.1)")
    print(f"=" * 70)
    print(f"Total defects: {len(defects)}\n")

    # Group by enclosing class.function for readability
    from collections import defaultdict
    by_scope = defaultdict(list)
    for node in defects:
        cls, func = find_enclosing_class_func(tree, node.lineno)
        scope = f"{cls or '<module>'}.{func or '<top>'}"
        by_scope[scope].append(node)

    for scope in sorted(by_scope.keys()):
        nodes = by_scope[scope]
        print(f"\n── {scope}  ({len(nodes)} defect{'s' if len(nodes) != 1 else ''}) ──")
        for node in nodes:
            preview = node.value
            if len(preview) > 80:
                preview = preview[:77] + '...'
            preview = preview.replace('\n', '\\n')
            print(f"  L{node.lineno:>5}: {preview!r}")

    print(f"\n{'=' * 70}")
    print(f"Summary: {len(defects)} hardcoded Korean strings missing self.tr() wrap")
    print(f"Across {len(by_scope)} class.function scopes")


if __name__ == '__main__':
    main()
