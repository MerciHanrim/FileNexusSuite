# Copyright © 2026 Hanrim
# Licensed under the MIT License.
# Free to use, modify, redistribute, and sell, provided that the copyright notice is retained.

"""File Nexus Suite — utility helpers (Phase 2a, v1.1.0 modularization track).

Pure Python utility functions extracted from FileNexusSuite.py. These helpers
have no dependencies on PySide6, TRANSLATIONS, ConfigManager, or any other
FNS-specific module — they can be reused independently and tested without a
running Qt application.

Contents:
  - Number / natural-sort utilities (_pad, extract_number, _get_leading_num,
    extract_number_auto, auto_width_for_group, detect_common_prefix,
    natural_sort_key, _SKIP_FILES)
  - Tag Editor core logic (remove_tag_from_name, _build_tag_str,
    add_tag_to_name, depad_name, apply_renames)
  - HTML escape / unescape utilities (_de, _h2t, _strip_xml_illegal, _ex)

The Text Converter panel's epub_to_text / txt_to_epub remain in the main
module since they belong to the Text Converter logic rather than to the
utility layer; they import the HTML helpers above from this module.
"""

# ── Standard Library ─────────────────────
import os
import re

# ═══════════════════════════════════════════════
# Number / natural-sort utilities
# ═══════════════════════════════════════════════
def _pad(s):
    try:
        if s.isdigit() and int(s) < 10: return s.zfill(2)
    except ValueError: pass
    return s

def extract_number(name):
    if not name: return name
    m = re.search(r'\d[\d.\-~]*', name)
    if not m: return name
    raw = m.group().rstrip(".-~")
    if '~' in raw: return '~'.join(_pad(p) for p in raw.split('~'))
    elif '-' in raw:
        head, tail = raw.split('-', 1); return f"{_pad(head)}-{tail}"
    elif '.' in raw:
        head, tail = raw.split('.', 1); return f"{_pad(head)}.{tail}"
    return _pad(raw)

def _get_leading_num(name):
    m = re.search(r'\d+', name)
    return int(m.group()) if m else 0

def extract_number_auto(name, width):
    if not name: return name
    m = re.search(r'\d[\d.\-~]*', name)
    if not m: return name
    raw = m.group().rstrip(".-~")
    def pad(s): return str(int(s)).zfill(width) if s.isdigit() else s
    if '~' in raw: return '~'.join(pad(p) for p in raw.split('~'))
    elif '-' in raw:
        head, tail = raw.split('-', 1); return f"{pad(head)}-{tail}"
    elif '.' in raw:
        head, tail = raw.split('.', 1); return f"{pad(head)}.{tail}"
    return pad(raw)

def auto_width_for_group(trimmed_names):
    nums = [n for n in (_get_leading_num(name) for name in trimmed_names) if n > 0]
    return len(str(max(nums))) if nums else 1

def detect_common_prefix(names):
    if not names: return ""
    prefix = names[0]
    for n in names[1:]:
        while prefix and not n.startswith(prefix): prefix = prefix[:-1]
        if not prefix: return ""
    if prefix and prefix[0].isdigit(): return ""
    m = re.search(r'\d', prefix)
    return prefix if not m else prefix[:m.start()]

def natural_sort_key(path):
    name = os.path.basename(path).lower()
    parts = re.split(r'(\d+)', name)
    return [int(p) if p.isdigit() else p for p in parts]

_SKIP_FILES = {'desktop.ini', 'thumbs.db', 'thumbs.db:encryptable'}

# ═══════════════════════════════════════════════
# Tag Editor core logic
# ═══════════════════════════════════════════════
def remove_tag_from_name(filename, position="front", target_tag=None):
    name, ext = os.path.splitext(filename)
    # \[+[^\]]+ \]+ pattern: handles both [tag] and [[tag]] double brackets
    _TAG = r'\[+[^\]]+\]+'
    if target_tag:
        # remove only a specific tag — strip that tag pattern regardless of position
        _SPECIFIC = r'\s*\[+' + re.escape(target_tag.strip()) + r'\]+\s*'
        name = re.sub(_SPECIFIC, ' ', name).strip()
    else:
        if position in ("front", "both"):
            while True:
                trimmed = re.sub(r'^\s*' + _TAG + r'\s*', '', name)
                if trimmed == name: break
                name = trimmed
        if position in ("back", "both"):
            while True:
                trimmed = re.sub(r'\s*' + _TAG + r'\s*$', '', name)
                if trimmed == name: break
                name = trimmed
    name = name.strip()
    if not name: return None
    new = name + ext
    return None if new == filename else new

def _build_tag_str(raw_tag, fmt):
    return fmt.replace("{tag}", raw_tag)

def add_tag_to_name(filename, tags, fmt, position, skip_exist,
                    replace_exist, space_after=True, space_before=True):
    if not tags: return None
    name, ext = os.path.splitext(filename)
    tag_str = _build_tag_str(tags[0], fmt)
    exists = bool(re.search(re.escape(tag_str), name))
    if exists and skip_exist: return None
    if exists and replace_exist:
        name = re.sub(r'\[' + re.escape(tags[0]) + r'\]', '', name).strip()
    sp_a = " " if space_after else ""
    sp_b = " " if space_before else ""
    if position == "front": new = f"{tag_str}{sp_a}{name}"
    else: new = f"{name}{sp_b}{tag_str}"
    new = new.strip() + ext
    return None if new == filename else new

def depad_name(filename):
    name, ext = os.path.splitext(filename)
    # date-format guard: leave unchanged if the entire filename is a pure date pattern
    # e.g., 2024-01-01, 01-01 → None (no change)
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}|\d{2}-\d{2}', name):
        return None
    new = re.sub(r'(?<![0-9\-])0+(\d)', r'\1', name)
    new = new + ext
    return None if new == filename else new

def apply_renames(targets):
    success, errors = 0, []
    for dirpath, old_name, new_name in targets:
        old_p = os.path.join(dirpath, old_name)
        new_p = os.path.join(dirpath, new_name)
        try:
            os.rename(old_p, new_p); success += 1
        except OSError as e:
            errors.append(f"{old_name}: {e}")
    return success, errors

# ═══════════════════════════════════════════════
# HTML utilities
# ═══════════════════════════════════════════════
def _de(s):
    s = s.replace("&amp;","&").replace("&lt;","<").replace("&gt;",">") \
         .replace("&quot;",'"').replace("&apos;","'").replace("&#39;","'").replace("&nbsp;"," ")
    def _safe_chr(n):
        try: return chr(n) if 0x20<=n<=0x10FFFF and not(0xD800<=n<=0xDFFF) else ""
        except Exception: return ""
    s = re.sub(r"&#(\d+);", lambda m: _safe_chr(int(m.group(1))), s)
    s = re.sub(r"&#x([0-9a-fA-F]+);", lambda m: _safe_chr(int(m.group(1),16)), s)
    return re.sub(r"&[a-z]+;","",s)

def _h2t(html, keep):
    html = re.sub(r"<script[\s\S]*?</script>","",html,flags=re.I)
    html = re.sub(r"<style[\s\S]*?</style>","",html,flags=re.I)
    if keep:
        def _hfmt(m): return "\n\n■ "+re.sub(r"<[^>]+>","",m.group(2)).strip()+"\n\n"
        html = re.sub(r"<h([1-6])\b[^>]*>([\s\S]*?)</h\1>",_hfmt,html,flags=re.I)
    else:
        html = re.sub(r"<h[1-6]\b[^>]*>[\s\S]*?</h[1-6]>","\n",html,flags=re.I)
    html = re.sub(r"<(p|div|br|section|li|tr)\b[^>]*>","\n",html,flags=re.I)
    html = re.sub(r"<[^>]+>","",html)
    html = _de(html)
    return re.sub(r"[ \t]+"," ",html).strip()

def _strip_xml_illegal(s):
    return re.sub(r'[^\x09\x0A\x0D\x20-\uD7FF\uE000-\uFFFD\U00010000-\U0010FFFF]','',s)

def _ex(s):
    s=_strip_xml_illegal(s)
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;") \
             .replace('"',"&quot;").replace("'","&apos;")
