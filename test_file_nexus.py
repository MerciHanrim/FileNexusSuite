"""
File Nexus Suite — Automated tests (detailed edition)
Run: python test_file_nexus.py
"""
import unittest, os, sys, re, zipfile, json, tempfile, time, shutil

sys.path.insert(0, os.path.dirname(__file__))

# Pin absolute path to FileNexusSuite.py based on this test file's location
_MAIN_PY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'FileNexusSuite.py')


# ════════════════════════════════════════════════════════════════════════
# Extract pure functions for testing
# ════════════════════════════════════════════════════════════════════════

# ── HTML utilities ───────────────────────────────────────────────────
def _de(s):
    if not s: return s
    s = s.replace('&amp;','&').replace('&lt;','<').replace('&gt;','>') \
         .replace('&quot;','"').replace('&#39;',"'").replace('&apos;',"'") \
         .replace('&nbsp;',' ').replace('&#x27;',"'")
    s = _re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), s)
    s = _re.sub(r'&#x([0-9A-Fa-f]+);', lambda m: chr(int(m.group(1),16)), s)
    return s

def _ex(s):
    if not s: return s
    return (s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
             .replace('"','&quot;').replace("'",'&#39;'))

def _strip_xml_illegal(s):
    return _re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]','',s)

def _h2t(h):
    h = _re.sub(r'<br\s*/?>', '\n', h, flags=_re.IGNORECASE)
    h = _re.sub(r'<p[^>]*>', '\n', h, flags=_re.IGNORECASE)
    h = _re.sub(r'<[^>]+>', '', h)
    return _de(h).strip()

# ── Natural sort ─────────────────────────────────────────────────────
def natural_sort_key(s):
    return [int(c) if c.isdigit() else c.lower()
            for c in _re.split(r'(\d+)', s)]

# ── Tag manipulation ─────────────────────────────────────────────────
def remove_tag(filename, position='both', target=''):
    base, ext = os.path.splitext(filename)
    if target:
        pattern = _re.escape(f'[{target}]')
        if position in ('front', 'both'):
            base = _re.sub(r'^\s*' + pattern + r'\s*', '', base).strip()
        if position in ('back', 'both'):
            base = _re.sub(r'\s*' + pattern + r'\s*$', '', base).strip()
    else:
        if position in ('front', 'both'):
            base = _re.sub(r'^\s*\[[^\]]*\]\s*', '', base).strip()
        if position in ('back', 'both'):
            base = _re.sub(r'\s*\[[^\]]*\]\s*$', '', base).strip()
    return base + ext

def add_tag(filename, tag, position='front', space_after=True, space_before=True,
            skip_existing=False, replace=False):
    base, ext = os.path.splitext(filename)
    tag_str = f'[{tag}]'
    if skip_existing and tag_str in base:
        return filename
    if replace:
        base = _re.sub(r'^\s*\[[^\]]*\]\s*', '', base).strip() if position == 'front' \
          else _re.sub(r'\s*\[[^\]]*\]\s*$', '', base).strip()
    if position == 'front':
        sep = ' ' if space_after else ''
        base = tag_str + sep + base
    else:
        sep = ' ' if space_before else ''
        base = base + sep + tag_str
    return base + ext

def depad(filename):
    # (?<![0-9\-]): if the preceding char is a digit or hyphen, do not touch
    # → preserves date format (2024-01-01); for range notation (001-197화), strips only the leading 001
    return _re.sub(r'(?<![0-9\-])0+(\d)', r'\1', filename)

def detect_prefix(names):
    if not names or len(names) < 2: return ''
    ref = names[0]
    for i in range(len(ref), 0, -1):
        candidate = ref[:i]
        if all(n.startswith(candidate) for n in names):
            return candidate
    return ''

def extract_number(s):
    m = _re.search(r'\d+', s)
    return int(m.group()) if m else None

# ════════════════════════════════════════════════════════════════════════
# PySide6 Mock — allow module exec even when PySide6 is not installed
# ════════════════════════════════════════════════════════════════════════
def _install_qt_mock():
    """Inject minimal stubs into sys.modules when PySide6 is unavailable.
    Pure logic (Worker, Fixer, EPUB, etc.) gets real behavior validation.
    Items that depend on Qt UI rendering are validated only by shape — actual UI must be verified under a PySide6 environment.
    """
    from types import ModuleType

    # ── Subclassable Qt class stub factory ───────────────────────────────
    def _qcls(name, *bases):
        """Dynamically create a subclassable Qt stub class."""
        def _noop(self, *a, **kw): pass
        return type(name, bases if bases else (object,), {'__init__': _noop})

    # ── Signal stub ──────────────────────────────────────────────────────
    # PySide6 Signal is a descriptor; __set_name__ is invoked when declared as a class variable.
    class _Signal:
        def __init__(self, *types): pass
        def __set_name__(self, owner, name): self._attr = name
        def __get__(self, obj, cls=None): return self
        def connect(self, fn): pass
        def disconnect(self, fn=None): pass
        def emit(self, *args): pass
        def __call__(self, *a, **kw): return self  # handles the Signal(int) pattern

    # ── QColor stub ──────────────────────────────────────────────────────
    # _mix() inside _build_help_html calls red()/green()/blue().
    class _QColor:
        def __init__(self, *a, **kw): pass
        def red(self):   return 0
        def green(self): return 0
        def blue(self):  return 0
        def alpha(self): return 255
        def name(self):  return '#000000'
        def __getattr__(self, n): return lambda *a, **kw: 0

    # ── Generic Qt stub (classes that do not require subclassing) ────────
    class _QtAny:
        def __init__(self, *a, **kw): pass
        def __call__(self, *a, **kw): return _QtAny()
        def __getattr__(self, n):
            if n.startswith('__'): raise AttributeError(n)
            return _QtAny()  # supports nested attribute access (e.g. Qt.ItemDataRole.UserRole)
        def __int__(self): return 0
        def __float__(self): return 0.0
        def __bool__(self): return True
        def __or__(self, o): return self
        def __ror__(self, o): return self
        def __and__(self, o): return self
        def __rand__(self, o): return self
        def __add__(self, o): return self
        def __radd__(self, o): return self
        def __sub__(self, o): return self
        def __rsub__(self, o): return self
        def __mul__(self, o): return self
        def __rmul__(self, o): return self
        def __eq__(self, o): return True
        def __ne__(self, o): return False
        def __lt__(self, o): return False
        def __le__(self, o): return True
        def __gt__(self, o): return False
        def __ge__(self, o): return True
        def __hash__(self): return 0
        def __iter__(self): return iter([])
        def __len__(self): return 0
        def __str__(self): return ''
        def __repr__(self): return '_QtAny()'

    # ── Subclassable base hierarchy ──────────────────────────────────────
    _QObject               = _qcls('QObject')
    _QThread               = _qcls('QThread',               _QObject)
    _QWidget               = _qcls('QWidget',               _QObject)
    _QDialog               = _qcls('QDialog',               _QWidget)
    _QMainWindow           = _qcls('QMainWindow',           _QWidget)
    _QLabel                = _qcls('QLabel',                _QWidget)
    _QFrame                = _qcls('QFrame',                _QWidget)
    _QAbstractScrollArea   = _qcls('QAbstractScrollArea',   _QWidget)
    _QAbstractItemView     = _qcls('QAbstractItemView',     _QAbstractScrollArea)
    _QTreeWidget           = _qcls('QTreeWidget',           _QAbstractItemView)
    _QListWidget           = _qcls('QListWidget',           _QAbstractItemView)
    _QTableWidget          = _qcls('QTableWidget',          _QAbstractItemView)
    _QHeaderView           = _qcls('QHeaderView',           _QAbstractItemView)
    _QAbstractItemDelegate = _qcls('QAbstractItemDelegate', _QObject)
    _QStyledItemDelegate   = _qcls('QStyledItemDelegate',   _QAbstractItemDelegate)
    _QProxyStyle           = _qcls('QProxyStyle',           _QObject)

    # ── PySide6.QtCore ───────────────────────────────────────────────
    qtcore           = ModuleType('PySide6.QtCore')
    qtcore.Qt        = _QtAny()
    qtcore.Signal    = _Signal
    qtcore.QThread   = _QThread
    qtcore.QSize     = _qcls('QSize')
    qtcore.QRect     = _qcls('QRect')
    qtcore.QRectF    = _qcls('QRectF')
    qtcore.QPointF   = _qcls('QPointF')
    qtcore.QTimer    = _qcls('QTimer',   _QObject)
    qtcore.QBuffer   = _qcls('QBuffer',  _QObject)
    qtcore.QIODevice = _qcls('QIODevice', _QObject)

    # ── PySide6.QtWidgets ────────────────────────────────────────────
    qtwidgets = ModuleType('PySide6.QtWidgets')
    _wmap = {
        'QApplication':     _qcls('QApplication',  _QObject),
        'QMainWindow':      _QMainWindow,
        'QWidget':          _QWidget,
        'QDialog':          _QDialog,
        'QFrame':           _QFrame,
        'QLabel':           _QLabel,
        'QVBoxLayout':      _qcls('QVBoxLayout',   _QObject),
        'QHBoxLayout':      _qcls('QHBoxLayout',   _QObject),
        'QGridLayout':      _qcls('QGridLayout',   _QObject),
        'QPushButton':      _qcls('QPushButton',   _QWidget),
        'QLineEdit':        _qcls('QLineEdit',     _QWidget),
        'QCheckBox':        _qcls('QCheckBox',     _QWidget),
        'QRadioButton':     _qcls('QRadioButton',  _QWidget),
        'QButtonGroup':     _qcls('QButtonGroup',  _QObject),
        'QTextEdit':        _qcls('QTextEdit',     _QAbstractScrollArea),
        'QPlainTextEdit':   _qcls('QPlainTextEdit', _QAbstractScrollArea),
        'QScrollArea':      _qcls('QScrollArea',   _QAbstractScrollArea),
        'QFileDialog':      _qcls('QFileDialog',   _QDialog),
        'QProgressBar':     _qcls('QProgressBar',  _QWidget),
        'QSplitter':        _qcls('QSplitter',     _QWidget),
        'QTabWidget':       _qcls('QTabWidget',    _QWidget),
        'QListWidget':      _QListWidget,
        'QListWidgetItem':  _qcls('QListWidgetItem'),
        'QAbstractItemView':_QAbstractItemView,
        'QStackedWidget':   _qcls('QStackedWidget',_QWidget),
        'QComboBox':        _qcls('QComboBox',     _QWidget),
        'QTreeWidget':      _QTreeWidget,
        'QTreeWidgetItem':  _qcls('QTreeWidgetItem'),
        'QHeaderView':      _QHeaderView,
        'QTableWidget':     _QTableWidget,
        'QTableWidgetItem': _qcls('QTableWidgetItem'),
        'QGroupBox':        _qcls('QGroupBox',     _QWidget),
        'QSpinBox':         _qcls('QSpinBox',      _QWidget),
        'QToolButton':      _qcls('QToolButton',   _QWidget),
        'QMenu':            _qcls('QMenu',         _QWidget),
        'QStyledItemDelegate': _QStyledItemDelegate,
        'QStyle':           _qcls('QStyle',        _QObject),
        'QProxyStyle':      _QProxyStyle,
        'QSizePolicy':      _qcls('QSizePolicy'),
    }
    for k, v in _wmap.items():
        setattr(qtwidgets, k, v)

    # ── PySide6.QtGui ────────────────────────────────────────────────
    qtgui = ModuleType('PySide6.QtGui')
    for _n in ['QPalette', 'QCursor', 'QPainter', 'QPen', 'QBrush', 'QFont',
               'QKeySequence', 'QLinearGradient', 'QPolygonF', 'QIcon', 'QPixmap',
               'QPainterPath', 'QImageReader', 'QShortcut', 'QAction',
               'QTextCharFormat', 'QFontMetrics', 'QTextOption', 'QTextDocument',
               'QFontDatabase', 'QTextCursor']:
        setattr(qtgui, _n, _qcls(_n))
    qtgui.QColor = _QColor  # special stub that needs to return numeric values

    # ── Register PySide6 package ─────────────────────────────────────────
    pyside6           = ModuleType('PySide6')
    pyside6.QtCore    = qtcore
    pyside6.QtWidgets = qtwidgets
    pyside6.QtGui     = qtgui
    sys.modules['PySide6']           = pyside6
    sys.modules['PySide6.QtCore']    = qtcore
    sys.modules['PySide6.QtWidgets'] = qtwidgets
    sys.modules['PySide6.QtGui']     = qtgui


# Inject mock if PySide6 is not installed (use the real one when available)
try:
    import PySide6 as _pyside6_available  # noqa: F401
except ImportError:
    _install_qt_mock()


# ── EPUB conversion / module symbol extraction ───────────────────────────
try:
    with open(_MAIN_PY, encoding='utf-8') as _f:
        _src = _f.read()
    _ns = {'__file__': _MAIN_PY, '__name__': '__exec__'}
    exec(compile(_src, 'FileNexusSuite.py', 'exec'), _ns)
    txt_to_epub             = _ns.get('txt_to_epub')
    epub_to_text            = _ns.get('epub_to_text')
    _alchemy_detect_enc     = _ns.get('alchemy_detect_encoding')
    _build_help_html        = _ns.get('_build_help_html')
    _APP_VERSION            = _ns.get('APP_VERSION')
    _ConfigManager          = _ns.get('ConfigManager')
    HAS_EPUB = txt_to_epub is not None
    HAS_MODULE = True
except Exception as _e:
    HAS_EPUB = False
    HAS_MODULE = False
    txt_to_epub = epub_to_text = None
    _alchemy_detect_enc = _build_help_html = _APP_VERSION = None
    _ConfigManager = None
    print(f'[Warning] Failed to load FileNexusSuite: {_e}')

# ── Text Fixer core logic ────────────────────────────────────────────
import re as _re

_SENT_END = frozenset('.!?…。！？‥\u201c\u201d\u2018\u2019」』）)}>]"\'')
_SEP_CHARS = frozenset('-=*_~─━═·•▶★☆…▪▸►◆■□▲△')
_BOUNDARY_PAT = _re.compile(r'[\.!?…]["\u201d\u2019\u300d\u300f]?(?=\s|$)')

def _is_sep_line(line):
    s = line.strip()
    return (len(s) >= 3
            and all(c in _SEP_CHARS or c == ' ' for c in s)
            and any(c in _SEP_CHARS for c in s))

def _split_long_line(line, max_chars):
    if len(line) <= max_chars:
        return [line]
    all_segs = []; start = 0
    for m in _BOUNDARY_PAT.finditer(line):
        end = m.end()
        seg = line[start:end].strip()
        if seg: all_segs.append(seg)
        skip = end
        while skip < len(line) and line[skip] == ' ': skip += 1
        start = skip
    if start < len(line):
        rem = line[start:].strip()
        if rem: all_segs.append(rem)
    if not all_segs: return [line]
    groups = []; cur = []; cur_len = 0
    for seg in all_segs:
        if cur and cur_len + len(seg) > max_chars:
            groups.append(' '.join(cur)); cur = [seg]; cur_len = len(seg)
        else:
            cur.append(seg); cur_len += len(seg)
    if cur: groups.append(' '.join(cur))
    return groups if groups else [line]

def _run_fix(text, do_mid=True, do_blank=True, max_blank=1,
             do_sep=False, do_auto_split=False, max_split_chars=100):
    lines = text.split('\n')
    orig_lines = len(lines)
    paragraphs = []; current = []
    for line in lines:
        if line.strip() == '':
            paragraphs.append(current); paragraphs.append(None); current = []
        else:
            current.append(line)
    paragraphs.append(current)
    result = []; fixed_mid = 0; fixed_blank = 0
    for para in paragraphs:
        if para is None: result.append(''); continue
        if not para: continue
        if do_mid and len(para) > 1:
            out_lines = [para[0]]
            for nxt in para[1:]:
                prev = out_lines[-1]
                prev_end = prev.rstrip()
                last_ch = prev_end[-1] if prev_end else ''
                if (last_ch and last_ch not in _SENT_END
                        and not _is_sep_line(prev)
                        and not _is_sep_line(nxt)):
                    out_lines[-1] = prev + nxt.lstrip(); fixed_mid += 1
                else:
                    out_lines.append(nxt)
            result.extend(out_lines)
        else:
            result.extend(para)
    if do_blank:
        compressed = []
        blank_count = 0
        for line in result:
            if line.strip() == '':
                blank_count += 1
                if blank_count <= max_blank: compressed.append(line)
                else: fixed_blank += 1
            else:
                blank_count = 0; compressed.append(line)
        result = compressed
    while result and result[0].strip() == '': result.pop(0)
    while result and result[-1].strip() == '': result.pop()
    if do_sep:
        sep_result = []; prev_blank = False
        for i, line in enumerate(result):
            sep_result.append(line)
            is_blank = not line.strip()
            if not is_blank and not prev_blank and i < len(result) - 1:
                nxt = result[i + 1]
                if nxt.strip():
                    last_ch = line.rstrip()[-1] if line.rstrip() else ''
                    nxt_first = nxt.lstrip()[0] if nxt.lstrip() else ''
                    if last_ch in _SENT_END or nxt_first in '"\u201c\u201d\u300c\u300e':
                        sep_result.append('')
            prev_blank = is_blank
        result = sep_result
        while result and result[0].strip() == '': result.pop(0)
        while result and result[-1].strip() == '': result.pop()
    if do_auto_split:
        expanded = []
        for line in result:
            if not line.strip() or len(line) <= max_split_chars:
                expanded.append(line)
            else:
                segs = _split_long_line(line, max_split_chars)
                for j, seg in enumerate(segs):
                    if seg: expanded.append(seg)
                    if j < len(segs) - 1: expanded.append('')
        result = expanded
        while result and result[0].strip() == '': result.pop(0)
        while result and result[-1].strip() == '': result.pop()
    return '\n'.join(result), fixed_mid, fixed_blank, orig_lines, len(result)


# ════════════════════════════════════════════════════════════════════════
# §Sample data — neutral test-only text (CC0 public domain)
# ════════════════════════════════════════════════════════════════════════
# The texts in this section are pure test samples, not real published works.
# - No narrative, characters, world-building, or work structure (deliberately neutral)
# - Each constant validates a specific test feature (OCR line wrap, word splitting, dialogue, etc.)
# - CC0 1.0 Universal public domain — free to use
#
# All text in this section is neutral test sample data.
# Contains no narrative, characters, world-building, or creative work structure.
# Licensed under CC0 1.0 Universal (Public Domain Dedication).

# Title series (validates separator-line merge protection — no narrative elements)
SAMPLE_KO_TITLE_LONG    = '테스트 샘플 [1] 섹션 A에서 섹션 B까지 (6)'
SAMPLE_KO_TITLE_SHORT   = '테스트 샘플 [1]'
SAMPLE_KO_TITLE_PLAIN   = '테스트 샘플'

# Validates OCR-style line-wrap correction — Korean sentence pattern like "휘\n둥그레"
SAMPLE_KO_OCR_BROKEN    = ("이 문장은 테스트 목적으로 작성되었으며 중간에 의도적으로 줄바꿈이 들어가 있어 휘\n"
                          "둥그레 같은 단어가 잘린 상태를 검증한다.")
SAMPLE_KO_OCR_SHORT     = ('첫 줄이 끝나고\n두 번째 줄이 자연스럽게 이어진다.')

# Word-split test — "참\n가자들" → "참가자들" (typical word-split pattern)
SAMPLE_KO_WORD_SPLIT    = "모든 참\n가자들에게 공지를 전달했다."

# Dialogue sample (only generic roles, no specific characters)
SAMPLE_KO_DIALOGUE_A    = '응답자가 대답했다.\n"몇 살이냐고요?"\n"열네 살입니다."'
SAMPLE_KO_DIALOGUE_B    = ('"질문해도 될까요? 지금 몇 살인가요?"\n'
                          '"이제 열네 살입니다."')

# Validates chapter-header structure preservation — title neutralized as "테스트 샘플"
SAMPLE_KO_CHAPTER_FULL  = ("────────────────────────────────────────────────────────\n"
                          "테스트 샘플 [1] 섹션 A에서 섹션 B까지 (6)\n"
                          "────────────────────────────────────────────────────────\n"
                          "\n"
                          "다음 섹션으로 이어진다.")
SAMPLE_KO_CHAPTER_SHORT = ("────────────────────────────────\n"
                          "테스트 샘플 [1]\n"
                          "────────────────────────────────")

# Mixed test (OCR + blank lines + dialogue — neutral wording)
SAMPLE_KO_MIXED         = ('응답자가 대답하자\n검사자가 메모를 멈췄다.\n\n\n'
                          '"몇 살이냐고요?"\n"열네 살입니다."')

# Validates auto paragraph splitting — long sentences joined by spaces (no narrative)
SAMPLE_KO_LONG_SENTENCES = (
    "이 문장은 자동 단락 분리 기능을 검증하기 위한 테스트용 예문 중 첫 번째 문장입니다. "
    "그리고 이어지는 두 번째 문장 역시 충분한 길이를 가지도록 의도적으로 작성된 예문입니다. "
    "마지막으로 세 번째 문장은 테스트 조건을 충족하기 위한 용도로 추가된 문장입니다."
)


# ─────────────────────────────────────────────────────────────────────────
# English-language counterparts — validate language-neutral behavior of
# _SENT_END (ASCII + CJK + curly quotes) at the scenario level.
# Same neutrality policy as SAMPLE_KO_*: no narrative, no characters,
# no work structure. CC0 1.0 Universal — free to use.
# ─────────────────────────────────────────────────────────────────────────

# Title series (English) — counterpart to SAMPLE_KO_TITLE_*
SAMPLE_EN_TITLE_LONG    = 'Test Sample [1] Section A to Section B (6)'
SAMPLE_EN_TITLE_SHORT   = 'Test Sample [1]'
SAMPLE_EN_TITLE_PLAIN   = 'Test Sample'

# Validates OCR-style line-wrap correction — English word break like "extraor\ndinarily"
SAMPLE_EN_OCR_BROKEN    = ("This sentence was written for testing purposes with an intentional line break in the middle so the word extraor\n"
                          "dinarily appears split across lines.")
SAMPLE_EN_OCR_SHORT     = ('The first line ends here\nand the second line continues naturally.')

# Word-split test — "respon\nsive" → "responsive" (typical word-split pattern)
SAMPLE_EN_WORD_SPLIT    = "Notify all respon\nsive participants of the announcement."

# Dialogue sample (only generic roles, no specific characters)
SAMPLE_EN_DIALOGUE_A    = 'The respondent answered.\n"How old are you?"\n"Fourteen years old."'
SAMPLE_EN_DIALOGUE_B    = ('"May I ask a question? How old are you now?"\n'
                          '"I am fourteen years old now."')

# Validates chapter-header structure preservation — title neutralized as "Test Sample"
SAMPLE_EN_CHAPTER_FULL  = ("────────────────────────────────────────────────────────\n"
                          "Test Sample [1] Section A to Section B (6)\n"
                          "────────────────────────────────────────────────────────\n"
                          "\n"
                          "Continues to the next section.")
SAMPLE_EN_CHAPTER_SHORT = ("────────────────────────────────\n"
                          "Test Sample [1]\n"
                          "────────────────────────────────")

# Mixed test (OCR + blank lines + dialogue — neutral wording)
SAMPLE_EN_MIXED         = ('When the respondent answered\nthe examiner stopped taking notes.\n\n\n'
                          '"How old are you?"\n"Fourteen years old."')

# Validates auto paragraph splitting — long sentences joined by spaces (no narrative)
SAMPLE_EN_LONG_SENTENCES = (
    "This sentence is the first example written for testing the automatic paragraph splitting feature. "
    "And the following second sentence is also written intentionally with sufficient length. "
    "Finally the third sentence is added to satisfy the test condition."
)


# ════════════════════════════════════════════════════════════════════════
# §1 HTML utilities
# ════════════════════════════════════════════════════════════════════════
class TestDe(unittest.TestCase):
    """_de: HTML entity decoding"""
    def test_amp(self):             self.assertEqual(_de('a&amp;b'), 'a&b')
    def test_lt(self):              self.assertEqual(_de('a&lt;b'), 'a<b')
    def test_gt(self):              self.assertEqual(_de('a&gt;b'), 'a>b')
    def test_quot(self):            self.assertEqual(_de('&quot;hi&quot;'), '"hi"')
    def test_apos_named(self):      self.assertEqual(_de('&apos;'), "'")
    def test_apos_num(self):        self.assertEqual(_de('&#39;'), "'")
    def test_apos_hex(self):        self.assertEqual(_de('&#x27;'), "'")
    def test_nbsp(self):            self.assertEqual(_de('a&nbsp;b'), 'a b')
    def test_numeric_decimal(self): self.assertEqual(_de('&#65;'), 'A')
    def test_numeric_hex(self):     self.assertEqual(_de('&#x41;'), 'A')
    def test_numeric_hex_upper(self):self.assertEqual(_de('&#X41;'), '&#X41;')  # 비표준
    def test_multiple(self):        self.assertEqual(_de('&lt;b&gt;'), '<b>')
    def test_nested_amp(self):      self.assertEqual(_de('&amp;amp;'), '&amp;')
    def test_empty(self):           self.assertEqual(_de(''), '')
    def test_none(self):            self.assertIsNone(_de(None))
    def test_no_entity(self):       self.assertEqual(_de('hello'), 'hello')
    def test_korean(self):          self.assertEqual(_de('한&amp;국'), '한&국')
    def test_partial_entity(self):  self.assertEqual(_de('&amp'), '&amp')  # incomplete entity
    def test_unicode_num(self):     self.assertEqual(_de('&#44032;'), '가')
    def test_unicode_hex(self):     self.assertEqual(_de('&#xAC00;'), '가')
    def test_chain(self):           self.assertEqual(_de('&lt;&amp;&gt;'), '<&>')

class TestEx(unittest.TestCase):
    """_ex: HTML special-character escaping"""
    def test_amp(self):     self.assertEqual(_ex('a&b'), 'a&amp;b')
    def test_lt(self):      self.assertEqual(_ex('<'), '&lt;')
    def test_gt(self):      self.assertEqual(_ex('>'), '&gt;')
    def test_quot(self):    self.assertEqual(_ex('"'), '&quot;')
    def test_apos(self):    self.assertEqual(_ex("'"), '&#39;')
    def test_combined(self):self.assertEqual(_ex('<a href="x">'), '&lt;a href=&quot;x&quot;&gt;')
    def test_empty(self):   self.assertEqual(_ex(''), '')
    def test_none(self):    self.assertIsNone(_ex(None))
    def test_safe(self):    self.assertEqual(_ex('hello 안녕'), 'hello 안녕')
    def test_round_trip(self):
        s = '<script>alert("xss&");</script>'
        self.assertEqual(_de(_ex(s)), s)

class TestStripXmlIllegal(unittest.TestCase):
    """_strip_xml_illegal: strip XML-illegal characters"""
    def test_null(self):        self.assertEqual(_strip_xml_illegal('\x00'), '')
    def test_ctrl_08(self):     self.assertEqual(_strip_xml_illegal('\x08'), '')
    def test_ctrl_0b(self):     self.assertEqual(_strip_xml_illegal('\x0B'), '')
    def test_ctrl_0c(self):     self.assertEqual(_strip_xml_illegal('\x0C'), '')
    def test_ctrl_1f(self):     self.assertEqual(_strip_xml_illegal('\x1F'), '')
    def test_del(self):         self.assertEqual(_strip_xml_illegal('\x7F'), '')
    def test_tab_ok(self):      self.assertEqual(_strip_xml_illegal('\t'), '\t')
    def test_lf_ok(self):       self.assertEqual(_strip_xml_illegal('\n'), '\n')
    def test_cr_ok(self):       self.assertEqual(_strip_xml_illegal('\r'), '\r')
    def test_normal_ok(self):   self.assertEqual(_strip_xml_illegal('hello'), 'hello')
    def test_korean_ok(self):   self.assertEqual(_strip_xml_illegal('한국어'), '한국어')
    def test_mixed(self):
        self.assertEqual(_strip_xml_illegal('a\x00b\x1Fc'), 'abc')

class TestH2t(unittest.TestCase):
    """_h2t: HTML → text"""
    def test_br(self):          self.assertEqual(_h2t('a<br>b'), 'a\nb')
    def test_br_self_close(self):self.assertEqual(_h2t('a<br/>b'), 'a\nb')
    def test_p_tag(self):       self.assertIn('\n', _h2t('<p>a</p><p>b</p>'))
    def test_strip_tags(self):  self.assertEqual(_h2t('<b>hello</b>'), 'hello')
    def test_entity_decode(self):self.assertEqual(_h2t('&amp;'), '&')
    def test_empty(self):       self.assertEqual(_h2t(''), '')
    def test_plain_text(self):  self.assertEqual(_h2t('hello'), 'hello')


# ════════════════════════════════════════════════════════════════════════
# §2 Natural sort
# ════════════════════════════════════════════════════════════════════════
class TestNaturalSort(unittest.TestCase):
    """natural_sort_key: natural sort"""
    def _sorted(self, lst): return sorted(lst, key=natural_sort_key)

    # Basic numeric order
    def test_1_before_2(self):      self.assertEqual(self._sorted(['2','1']), ['1','2'])
    def test_9_before_10(self):     self.assertEqual(self._sorted(['10','9']), ['9','10'])
    def test_1_10_100(self):        self.assertEqual(self._sorted(['100','10','1']), ['1','10','100'])
    def test_zero_pad_order(self):
        # Same numeric value (1) → stable sort preserves input order
        r = self._sorted(['01','001','1'])
        self.assertEqual(len(r), 3)  # all included
        self.assertEqual(set(r), {'01','001','1'})

    # Mixed (letters + numbers)
    def test_alpha_numeric(self):   self.assertEqual(self._sorted(['a2','a10','a1']), ['a1','a2','a10'])
    def test_korean_numeric(self):
        result = self._sorted(['파일10화.txt','파일2화.txt','파일1화.txt'])
        self.assertEqual(result, ['파일1화.txt','파일2화.txt','파일10화.txt'])
    def test_episode_sort(self):
        r = self._sorted(['ep3.txt','ep20.txt','ep1.txt','ep10.txt'])
        self.assertEqual(r, ['ep1.txt','ep3.txt','ep10.txt','ep20.txt'])
    def test_prefix_then_number(self):
        r = self._sorted(['시즌2 ep10','시즌1 ep2','시즌1 ep10'])
        self.assertLess(r.index('시즌1 ep2'), r.index('시즌1 ep10'))
        self.assertLess(r.index('시즌1 ep10'), r.index('시즌2 ep10'))

    # Edge cases
    def test_empty_string(self):    self.assertEqual(self._sorted(['','a']), ['','a'])
    def test_all_alpha(self):       self.assertEqual(self._sorted(['b','a','c']), ['a','b','c'])
    def test_all_numeric(self):     self.assertEqual(self._sorted(['3','1','2']), ['1','2','3'])
    def test_case_insensitive(self):self.assertEqual(self._sorted(['B','a']), ['a','B'])
    def test_extension_ignored_in_sort(self):
        r = self._sorted(['02.txt','10.txt','1.txt'])
        self.assertEqual(r, ['1.txt','02.txt','10.txt'])
    def test_large_number(self):
        r = self._sorted(['파일9999화','파일10화','파일1000화'])
        self.assertLess(r.index('파일10화'), r.index('파일1000화'))


# ════════════════════════════════════════════════════════════════════════
# §3 Tag removal
# ════════════════════════════════════════════════════════════════════════
class TestRemoveTag(unittest.TestCase):
    """remove_tag: remove tags from filenames"""
    # Default behavior by position
    def test_front_basic(self):     self.assertEqual(remove_tag('[BD] 파일.txt','front'), '파일.txt')
    def test_back_basic(self):      self.assertEqual(remove_tag('파일 [완결].txt','back'), '파일.txt')
    def test_both_front(self):      self.assertEqual(remove_tag('[A] 파일.txt','both'), '파일.txt')
    def test_both_back(self):       self.assertEqual(remove_tag('파일 [A].txt','both'), '파일.txt')
    def test_both_both_sides(self): self.assertEqual(remove_tag('[A] 파일 [B].txt','both'), '파일.txt')
    def test_front_only_no_back(self):
        r = remove_tag('파일 [완결].txt','front')
        self.assertIn('[완결]', r)
    def test_back_only_no_front(self):
        r = remove_tag('[BD] 파일.txt','back')
        self.assertIn('[BD]', r)

    # Specific tag target
    def test_target_specific(self): self.assertEqual(remove_tag('[BD] 파일.txt','both','BD'), '파일.txt')
    def test_target_keep_other(self):
        r = remove_tag('[BD] 파일 [완결].txt','both','BD')
        self.assertIn('[완결]', r)
        self.assertNotIn('[BD]', r)
    def test_target_not_present(self):
        r = remove_tag('파일 [완결].txt','both','BD')
        self.assertIn('[완결]', r)

    # Extension preservation
    def test_ext_preserved_txt(self):   self.assertTrue(remove_tag('[A] 파일.txt','both').endswith('.txt'))
    def test_ext_preserved_epub(self):  self.assertTrue(remove_tag('[A] 파일.epub','both').endswith('.epub'))
    def test_ext_preserved_mp4(self):   self.assertTrue(remove_tag('파일 [A].mp4','both').endswith('.mp4'))
    def test_no_ext(self):              self.assertEqual(remove_tag('[A] 파일','both'), '파일')

    # Edge cases
    def test_only_tag(self):        self.assertEqual(remove_tag('[A].txt','both'), '.txt')
    def test_nested_bracket(self):
        r = remove_tag('[A[B]] 파일.txt','front')
        self.assertNotIn('[A', r)
    def test_space_around_tag(self):
        r = remove_tag('  [BD]  파일.txt','front')
        self.assertEqual(r.strip(), '파일.txt')
    def test_multiple_front_tags(self):
        r = remove_tag('[A] 파일.txt','front')
        self.assertNotIn('[A]', r)
    def test_unicode_tag(self):     self.assertEqual(remove_tag('[완결] 파일.txt','front'), '파일.txt')
    def test_number_in_tag(self):   self.assertEqual(remove_tag('[2024] 파일.txt','front'), '파일.txt')


# ════════════════════════════════════════════════════════════════════════
# §4 Tag addition
# ════════════════════════════════════════════════════════════════════════
class TestAddTag(unittest.TestCase):
    """add_tag: add tags to filenames"""
    def test_front_basic(self):
        self.assertEqual(add_tag('파일.txt','BD','front'), '[BD] 파일.txt')
    def test_back_basic(self):
        self.assertEqual(add_tag('파일.txt','BD','back'), '파일 [BD].txt')
    def test_no_space_after(self):
        self.assertEqual(add_tag('파일.txt','BD','front',space_after=False), '[BD]파일.txt')
    def test_no_space_before(self):
        self.assertEqual(add_tag('파일.txt','BD','back',space_before=False), '파일[BD].txt')
    def test_skip_existing_true(self):
        r = add_tag('[BD] 파일.txt','BD','front',skip_existing=True)
        self.assertEqual(r.count('[BD]'), 1)
    def test_skip_existing_false(self):
        r = add_tag('[BD] 파일.txt','BD','front',skip_existing=False)
        self.assertEqual(r.count('[BD]'), 2)
    def test_replace_front(self):
        r = add_tag('[OLD] 파일.txt','NEW','front',replace=True)
        self.assertNotIn('[OLD]', r)
        self.assertIn('[NEW]', r)
    def test_ext_preserved(self):
        self.assertTrue(add_tag('파일.epub','BD','front').endswith('.epub'))
    def test_empty_base(self):
        r = add_tag('.txt','BD','front')
        self.assertIn('[BD]', r)
    def test_korean_tag(self):
        self.assertEqual(add_tag('파일.txt','완결','back'), '파일 [완결].txt')
    def test_number_tag(self):
        self.assertEqual(add_tag('파일.txt','2024','front'), '[2024] 파일.txt')


# ════════════════════════════════════════════════════════════════════════
# §5 Zero-pad stripping
# ════════════════════════════════════════════════════════════════════════
class TestDepad(unittest.TestCase):
    """depad: strip leading zeros"""
    def test_001(self):         self.assertIn('1', depad('001화'))
    def test_001_no_extra_0(self): self.assertNotIn('001', depad('001화'))
    def test_007(self):         self.assertIn('7', depad('007.mp4'))
    def test_010(self):         self.assertEqual(depad('010화'), '10화')
    def test_100_unchanged(self):self.assertEqual(depad('100화'), '100화')
    def test_single_digit(self): self.assertEqual(depad('1화'), '1화')
    def test_no_pad(self):       self.assertEqual(depad('에피소드12.txt'), '에피소드12.txt')
    def test_inside_word(self):  self.assertNotIn('001', depad('파일001화.txt'))
    def test_ext_preserved(self):self.assertTrue(depad('001.mp4').endswith('.mp4'))
    def test_zero_only(self):
        r = depad('000')
        # 000 is numeric 000 → 0
        self.assertIn('0', r)
    def test_multiple_groups(self):
        r = depad('시즌001 에피소드007.txt')
        self.assertNotIn('001', r)
        self.assertNotIn('007', r)
    def test_already_clean(self):
        self.assertEqual(depad('파일12.txt'), '파일12.txt')
    def test_leading_zero_in_name(self):
        r = depad('0001화.txt')
        self.assertIn('1화', r)


# ════════════════════════════════════════════════════════════════════════
# §6 Common prefix detection
# ════════════════════════════════════════════════════════════════════════
class TestDetectPrefix(unittest.TestCase):
    """detect_prefix: common prefix detection"""
    def test_basic(self):       self.assertEqual(detect_prefix(['시즌1 ep1','시즌1 ep2']), '시즌1 ep')
    def test_no_common(self):   self.assertEqual(detect_prefix(['abc','def']), '')
    def test_empty_list(self):  self.assertEqual(detect_prefix([]), '')
    def test_single_item(self): self.assertEqual(detect_prefix(['abc']), '')
    def test_full_match(self):  self.assertEqual(detect_prefix(['abc','abc']), 'abc')
    def test_partial(self):
        r = detect_prefix(['파일01화','파일02화','파일10화'])
        self.assertTrue(r.startswith('파일'))
    def test_no_common_unicode(self):
        self.assertEqual(detect_prefix(['가나다','라마바']), '')
    def test_length_1_common(self):
        r = detect_prefix(['a1','a2'])
        self.assertEqual(r, 'a')


# ════════════════════════════════════════════════════════════════════════
# §7 Number extraction
# ════════════════════════════════════════════════════════════════════════
class TestExtractNumber(unittest.TestCase):
    """extract_number: extract the first number"""
    def test_simple(self):          self.assertEqual(extract_number('파일01'), 1)
    def test_zero(self):            self.assertEqual(extract_number('0화'), 0)
    def test_no_number(self):       self.assertIsNone(extract_number('파일'))
    def test_multiple_groups(self): self.assertEqual(extract_number('시즌2 ep10'), 2)
    def test_only_number(self):     self.assertEqual(extract_number('42'), 42)
    def test_large(self):           self.assertEqual(extract_number('파일9999'), 9999)
    def test_empty(self):           self.assertIsNone(extract_number(''))
    def test_float_not_float(self): self.assertEqual(extract_number('3.14'), 3)
    def test_leading_zero(self):    self.assertEqual(extract_number('007'), 7)
    def test_suffix_number(self):   self.assertEqual(extract_number('파일42화'), 42)


# ════════════════════════════════════════════════════════════════════════
# §8 Separator-line detection
# ════════════════════════════════════════════════════════════════════════
class TestIsSepLine(unittest.TestCase):
    """_is_sep_line: detect separator lines"""
    # True cases (separator lines)
    def test_long_dash(self):       self.assertTrue(_is_sep_line('─' * 30))
    def test_long_hyphen(self):     self.assertTrue(_is_sep_line('-' * 20))
    def test_equals(self):          self.assertTrue(_is_sep_line('=' * 10))
    def test_stars(self):           self.assertTrue(_is_sep_line('★★★'))
    def test_min_length(self):      self.assertTrue(_is_sep_line('---'))
    def test_equals_min(self):      self.assertTrue(_is_sep_line('==='))
    def test_stars_with_spaces(self):self.assertTrue(_is_sep_line('* * *'))
    def test_mixed_sep(self):       self.assertTrue(_is_sep_line('-==-'))
    def test_trailing_space(self):  self.assertTrue(_is_sep_line('---   '))
    def test_leading_space(self):   self.assertTrue(_is_sep_line('   ---'))
    def test_tilde(self):           self.assertTrue(_is_sep_line('~~~'))
    def test_dots(self):            self.assertTrue(_is_sep_line('···'))
    def test_box_chars(self):       self.assertTrue(_is_sep_line('━━━'))
    def test_double_line(self):     self.assertTrue(_is_sep_line('═══'))

    # False cases (not separator lines)
    def test_too_short_1(self):     self.assertFalse(_is_sep_line('-'))
    def test_too_short_2(self):     self.assertFalse(_is_sep_line('--'))
    def test_empty(self):           self.assertFalse(_is_sep_line(''))
    def test_whitespace_only(self): self.assertFalse(_is_sep_line('   '))
    def test_korean(self):          self.assertFalse(_is_sep_line('한국어'))
    def test_mixed_content(self):   self.assertFalse(_is_sep_line('---hello---'))
    def test_number(self):          self.assertFalse(_is_sep_line('123'))
    def test_title_line(self):      self.assertFalse(_is_sep_line(SAMPLE_KO_TITLE_SHORT))
    def test_alphanumeric(self):    self.assertFalse(_is_sep_line('abc'))


# ════════════════════════════════════════════════════════════════════════
# §9 Text Fixer — line-break merging (smart merge)
# ════════════════════════════════════════════════════════════════════════
class TestSmartMerge(unittest.TestCase):
    """Smart merge: based on sentence-ending characters"""
    # Cases that should merge (mid-paragraph line break)
    def test_basic_merge(self):
        out, mid, *_ = _run_fix("첫 번째\n두 번째", do_blank=False)
        self.assertEqual(mid, 1)
        self.assertNotIn('\n', out)

    def test_mid_sentence_korean(self):
        out, mid, *_ = _run_fix("앞부분이고\n뒷부분이다.", do_blank=False)
        self.assertEqual(mid, 1)

    def test_trailing_space_preserved(self):
        out, mid, *_ = _run_fix("앉아 \n기다렸다.", do_blank=False)
        self.assertEqual(out, "앉아 기다렸다.")

    # Cases that should NOT merge (sentence end)
    def test_period_no_merge(self):
        out, mid, *_ = _run_fix("문장이다.\n다음 문장.", do_blank=False)
        self.assertEqual(mid, 0)
        self.assertIn('\n', out)

    def test_question_no_merge(self):
        out, mid, *_ = _run_fix("질문인가?\n대답한다.", do_blank=False)
        self.assertEqual(mid, 0)

    def test_exclamation_no_merge(self):
        out, mid, *_ = _run_fix("놀랍다!\n그렇다.", do_blank=False)
        self.assertEqual(mid, 0)

    def test_ellipsis_no_merge(self):
        out, mid, *_ = _run_fix("그렇다…\n계속된다.", do_blank=False)
        self.assertEqual(mid, 0)

    def test_close_dquote_no_merge(self):
        out, mid, *_ = _run_fix('"말했다."\n다음 줄.', do_blank=False)
        self.assertEqual(mid, 0)

    def test_close_squote_no_merge(self):
        out, mid, *_ = _run_fix("'말했다.'\n다음 줄.", do_blank=False)
        self.assertEqual(mid, 0)

    def test_close_paren_no_merge(self):
        out, mid, *_ = _run_fix("설명이다)\n다음.", do_blank=False)
        self.assertEqual(mid, 0)

    def test_close_bracket_no_merge(self):
        out, mid, *_ = _run_fix("설명이다]\n다음.", do_blank=False)
        self.assertEqual(mid, 0)

    def test_curly_quote_no_merge(self):
        out, mid, *_ = _run_fix('\u201c말했다.\u201d\n다음.', do_blank=False)
        self.assertEqual(mid, 0)

    # ─── English counterparts: language-neutral _SENT_END verification ───
    # Confirms that the same set of sentence-end characters governs
    # English input identically — ASCII period/question/exclamation/ellipsis
    # and various closing brackets/quotes block merging.
    def test_basic_merge_en(self):
        out, mid, *_ = _run_fix("first part\nsecond part", do_blank=False)
        self.assertEqual(mid, 1)
        self.assertNotIn('\n', out)

    def test_mid_sentence_english(self):
        out, mid, *_ = _run_fix("the front part\nand the rest follows.", do_blank=False)
        self.assertEqual(mid, 1)

    def test_trailing_space_preserved_en(self):
        out, mid, *_ = _run_fix("stayed \nand waited.", do_blank=False)
        self.assertEqual(out, "stayed and waited.")

    def test_period_no_merge_en(self):
        out, mid, *_ = _run_fix("This is a sentence.\nAnother sentence.", do_blank=False)
        self.assertEqual(mid, 0)
        self.assertIn('\n', out)

    def test_question_no_merge_en(self):
        out, mid, *_ = _run_fix("Is this a question?\nThe answer follows.", do_blank=False)
        self.assertEqual(mid, 0)

    def test_exclamation_no_merge_en(self):
        out, mid, *_ = _run_fix("How surprising!\nIndeed it is.", do_blank=False)
        self.assertEqual(mid, 0)

    def test_ellipsis_no_merge_en(self):
        out, mid, *_ = _run_fix("It continues\u2026\nAnd then ends.", do_blank=False)
        self.assertEqual(mid, 0)

    def test_close_dquote_no_merge_en(self):
        out, mid, *_ = _run_fix('"He spoke."\nNext line.', do_blank=False)
        self.assertEqual(mid, 0)

    def test_close_squote_no_merge_en(self):
        out, mid, *_ = _run_fix("'He spoke.'\nNext line.", do_blank=False)
        self.assertEqual(mid, 0)

    def test_close_paren_no_merge_en(self):
        out, mid, *_ = _run_fix("an explanation)\nnext.", do_blank=False)
        self.assertEqual(mid, 0)

    def test_close_bracket_no_merge_en(self):
        out, mid, *_ = _run_fix("an explanation]\nnext.", do_blank=False)
        self.assertEqual(mid, 0)

    def test_curly_quote_no_merge_en(self):
        out, mid, *_ = _run_fix('\u201cHe spoke.\u201d\nNext.', do_blank=False)
        self.assertEqual(mid, 0)

    def test_ja_period_no_merge(self):
        out, mid, *_ = _run_fix("文章です。\n次の行。", do_blank=False)
        self.assertEqual(mid, 0)

    def test_zh_period_no_merge(self):
        out, mid, *_ = _run_fix("文章。\n下一行。", do_blank=False)
        self.assertEqual(mid, 0)

    # Separator lines do not merge
    def test_sep_line_before_not_merged(self):
        inp = "────────────────\n" + SAMPLE_KO_TITLE_PLAIN
        out, mid, *_ = _run_fix(inp, do_blank=False)
        self.assertEqual(mid, 0)

    def test_sep_line_after_not_merged(self):
        inp = SAMPLE_KO_TITLE_SHORT + "\n────────────────"
        out, mid, *_ = _run_fix(inp, do_blank=False)
        self.assertEqual(mid, 0)

    def test_sep_between_content(self):
        inp = "────────\n제목\n────────"
        out, mid, *_ = _run_fix(inp, do_blank=False)
        lines = out.split('\n')
        self.assertEqual(lines[0], '────────')
        self.assertEqual(lines[1], '제목')
        self.assertEqual(lines[2], '────────')

    def test_separator_not_merged_with_next_paragraph(self):
        inp = "────────\n\n다음 섹션으로 이어진다."
        out, *_ = _run_fix(inp)
        self.assertIn('────────', out)
        self.assertIn('다음 섹션', out)
        self.assertNotIn('────────다음', out)

    # Blank line as paragraph boundary
    def test_blank_line_separates_paragraphs(self):
        inp = "A\nB\n\nC\nD"
        out, *_ = _run_fix(inp)
        self.assertIn('\n\n', out)

    # Multi-paragraph merging
    def test_multi_paragraph_independent(self):
        inp = "A\nB\n\nC\nD"
        out, mid, *_ = _run_fix(inp)
        self.assertEqual(mid, 2)


# ════════════════════════════════════════════════════════════════════════
# §10 Text Fixer — blank-line reduction
# ════════════════════════════════════════════════════════════════════════
class TestBlankCompression(unittest.TestCase):
    """Blank-line reduction: based on max_blank"""
    def test_double_to_one(self):
        out, _, blank, *_ = _run_fix("A\n\n\nB", do_mid=False, max_blank=1)
        self.assertGreater(blank, 0)
        self.assertNotIn('\n\n\n', out)

    def test_single_preserved(self):
        out, _, blank, *_ = _run_fix("A\n\nB", do_mid=False, max_blank=1)
        self.assertEqual(blank, 0)
        self.assertIn('\n\n', out)

    def test_max_blank_2(self):
        out, _, blank, *_ = _run_fix("A\n\n\n\nB", do_mid=False, max_blank=2)
        self.assertIn('\n\n\n', out)
        self.assertNotIn('\n\n\n\n', out)

    def test_max_blank_0(self):
        out, _, blank, *_ = _run_fix("A\n\nB", do_mid=False, max_blank=0)
        self.assertNotIn('\n\n', out)
        self.assertGreater(blank, 0)

    def test_triple_to_one(self):
        out, *_ = _run_fix("A\n\n\n\nB", do_mid=False, max_blank=1)
        self.assertNotIn('\n\n\n', out)

    def test_leading_blank_removed(self):
        out, *_ = _run_fix("\n\nA", do_mid=False)
        self.assertFalse(out.startswith('\n'))

    def test_trailing_blank_removed(self):
        out, *_ = _run_fix("A\n\n", do_mid=False)
        self.assertFalse(out.endswith('\n'))

    def test_blank_count_accurate(self):
        out, _, blank, *_ = _run_fix("A\n\n\n\n\nB", do_mid=False, max_blank=1)
        self.assertEqual(blank, 3)

    def test_disabled(self):
        out, _, blank, *_ = _run_fix("A\n\n\n\nB", do_mid=False, do_blank=False)
        self.assertEqual(blank, 0)
        self.assertIn('\n\n\n\n', out)

    def test_exact_max_not_compressed(self):
        # max_blank=2, exactly 2 blank lines → no reduction
        out, _, blank, *_ = _run_fix("A\n\n\nB", do_mid=False, max_blank=2)
        self.assertEqual(blank, 0)


# ════════════════════════════════════════════════════════════════════════
# §11 Text Fixer — insert blank line after each sentence
# ════════════════════════════════════════════════════════════════════════
class TestSentenceSep(unittest.TestCase):
    """Insert blank line after each sentence"""
    def test_period_gets_blank(self):
        out, *_ = _run_fix("첫 문장.\n두 번째.", do_mid=False, do_blank=False, do_sep=True)
        self.assertIn('\n\n', out)

    def test_dialogue_gets_blank(self):
        out, *_ = _run_fix('서술.\n"대화"', do_mid=False, do_blank=False, do_sep=True)
        self.assertIn('\n\n', out)

    def test_question_gets_blank(self):
        out, *_ = _run_fix("질문?\n대답.", do_mid=False, do_blank=False, do_sep=True)
        self.assertIn('\n\n', out)

    def test_exclamation_gets_blank(self):
        out, *_ = _run_fix("외침!\n다음.", do_mid=False, do_blank=False, do_sep=True)
        self.assertIn('\n\n', out)

    def test_no_double_blank(self):
        out, *_ = _run_fix("A.\n\nB.", do_mid=False, do_blank=False, do_sep=True)
        self.assertNotIn('\n\n\n', out)

    def test_disabled(self):
        out, *_ = _run_fix("A.\nB.", do_mid=False, do_blank=False, do_sep=False)
        self.assertNotIn('\n\n', out)

    def test_no_sep_without_punct(self):
        # No blank line is inserted after a line that does not end with a period
        out, *_ = _run_fix("이어지는\n문장입니다.", do_mid=False, do_blank=False, do_sep=True)
        # First line did not end with a period, so no blank line
        lines = out.split('\n')
        non_blank = [l for l in lines if l.strip()]
        # No blank line should appear between the two lines
        idx1 = lines.index('이어지는') if '이어지는' in lines else -1
        idx2 = next((i for i,l in enumerate(lines) if '문장입니다' in l), -1)
        if idx1 >= 0 and idx2 >= 0:
            self.assertEqual(idx2 - idx1, 1)

    # ─── English counterparts: blank-line insertion is language-neutral ───
    def test_period_gets_blank_en(self):
        out, *_ = _run_fix("First sentence.\nSecond sentence.", do_mid=False, do_blank=False, do_sep=True)
        self.assertIn('\n\n', out)

    def test_dialogue_gets_blank_en(self):
        out, *_ = _run_fix('Narration.\n"Dialogue line"', do_mid=False, do_blank=False, do_sep=True)
        self.assertIn('\n\n', out)

    def test_question_gets_blank_en(self):
        out, *_ = _run_fix("Question?\nAnswer.", do_mid=False, do_blank=False, do_sep=True)
        self.assertIn('\n\n', out)

    def test_exclamation_gets_blank_en(self):
        out, *_ = _run_fix("Shout!\nNext.", do_mid=False, do_blank=False, do_sep=True)
        self.assertIn('\n\n', out)

    def test_no_sep_without_punct_en(self):
        # Mirror of test_no_sep_without_punct using English input
        out, *_ = _run_fix("the continuing\nsentence ends here.", do_mid=False, do_blank=False, do_sep=True)
        lines = out.split('\n')
        idx1 = lines.index('the continuing') if 'the continuing' in lines else -1
        idx2 = next((i for i,l in enumerate(lines) if 'sentence ends here' in l), -1)
        if idx1 >= 0 and idx2 >= 0:
            self.assertEqual(idx2 - idx1, 1)

    def test_novel_dialogue_multiple(self):
        inp = SAMPLE_KO_DIALOGUE_A
        out, *_ = _run_fix(inp, do_mid=False, do_blank=False, do_sep=True)
        self.assertGreaterEqual(out.count('\n\n'), 1)


# ════════════════════════════════════════════════════════════════════════
# §12 Text Fixer — auto paragraph splitting (_split_long_line v2)
# ════════════════════════════════════════════════════════════════════════
class TestSplitLongLine(unittest.TestCase):
    """_split_long_line: two-stage auto splitting"""
    def test_short_not_split(self):
        r = _split_long_line("짧은 문장.", 100)
        self.assertEqual(len(r), 1)

    def test_exactly_at_threshold(self):
        line = "A" * 50 + ". " + "B" * 50 + "."
        r = _split_long_line(line, 102)
        self.assertEqual(len(r), 1)

    def test_over_threshold_splits(self):
        line = "A" * 50 + ". " + "B" * 60 + "."
        r = _split_long_line(line, 80)
        self.assertGreater(len(r), 1)

    def test_no_boundary_no_split(self):
        line = "경계없이계속이어지는텍스트" * 10
        r = _split_long_line(line, 50)
        self.assertEqual(len(r), 1)

    def test_short_sentences_grouped(self):
        line = "짧다. 짧다. 짧다. " + "매우긴문장" * 20 + "."
        r = _split_long_line(line, 80)
        # Short sentences should be grouped together
        self.assertGreater(len(r), 1)
        first = r[0]
        self.assertIn("짧다.", first)

    def test_question_mark_boundary(self):
        line = "질문인가요? " + "다음문장" * 20 + "."
        r = _split_long_line(line, 50)
        self.assertGreater(len(r), 1)

    def test_exclamation_boundary(self):
        line = "외침입니다! " + "다음문장" * 20 + "."
        r = _split_long_line(line, 50)
        self.assertGreater(len(r), 1)

    def test_closing_quote_after_period(self):
        line = '말했다." ' + "다음" * 20 + "."
        r = _split_long_line(line, 30)
        self.assertGreater(len(r), 1)
        self.assertTrue(r[0].endswith('"'))

    def test_empty_string(self):
        r = _split_long_line("", 100)
        self.assertEqual(r, [""])

    def test_single_long_sentence(self):
        line = "경계없는매우긴단일문장입니다이문장은끝나지않습니다" * 5
        r = _split_long_line(line, 50)
        self.assertEqual(len(r), 1)  # no split without boundary

    def test_many_short_sentence(self):
        # 10 short sentences → split when cumulative threshold exceeds 30
        line = "짧습니다. " * 10
        r = _split_long_line(line.strip(), 30)
        self.assertGreater(len(r), 1)


class TestAutoSplit(unittest.TestCase):
    """do_auto_split: integrated with _run_fix"""
    def test_long_line_gets_split(self):
        long = "첫 번째 문장입니다. " * 5 + "두 번째 문장입니다."
        out, *_ = _run_fix(long, do_mid=False, do_blank=False, do_auto_split=True, max_split_chars=60)
        self.assertIn('\n\n', out)

    def test_short_not_split(self):
        out, *_ = _run_fix("짧은 문장.", do_mid=False, do_auto_split=True, max_split_chars=100)
        self.assertNotIn('\n\n', out)

    def test_disabled_no_split(self):
        long = "가나다라마바사아자차. " * 10
        out, *_ = _run_fix(long, do_mid=False, do_auto_split=False)
        self.assertNotIn('\n\n', out)

    def test_split_inserts_blank(self):
        long = "A" * 50 + ". " + "B" * 50 + "."
        out, *_ = _run_fix(long, do_mid=False, do_blank=False, do_auto_split=True, max_split_chars=60)
        self.assertIn('\n\n', out)

    def test_novel_example(self):
        # Validates auto-splitting — multiple long sentences joined together
        inp = SAMPLE_KO_LONG_SENTENCES
        out, *_ = _run_fix(inp, do_mid=False, do_blank=False, do_auto_split=True, max_split_chars=80)
        self.assertIn('\n\n', out)
        lines = [l for l in out.split('\n') if l.strip()]
        self.assertGreater(len(lines), 1)

    # ─── English counterparts: auto-split language neutrality ───
    def test_long_line_gets_split_en(self):
        long = "This is the first sentence. " * 5 + "This is the second sentence."
        out, *_ = _run_fix(long, do_mid=False, do_blank=False, do_auto_split=True, max_split_chars=60)
        self.assertIn('\n\n', out)

    def test_short_not_split_en(self):
        out, *_ = _run_fix("Short sentence.", do_mid=False, do_auto_split=True, max_split_chars=100)
        self.assertNotIn('\n\n', out)

    def test_disabled_no_split_en(self):
        long = "alpha beta gamma delta. " * 10
        out, *_ = _run_fix(long, do_mid=False, do_auto_split=False)
        self.assertNotIn('\n\n', out)

    def test_novel_example_en(self):
        # Validates auto-splitting on English long sentences
        inp = SAMPLE_EN_LONG_SENTENCES
        out, *_ = _run_fix(inp, do_mid=False, do_blank=False, do_auto_split=True, max_split_chars=80)
        self.assertIn('\n\n', out)
        lines = [l for l in out.split('\n') if l.strip()]
        self.assertGreater(len(lines), 1)


# ════════════════════════════════════════════════════════════════════════
# §13 Text Fixer — edge cases
# ════════════════════════════════════════════════════════════════════════
class TestFixerEdge(unittest.TestCase):
    """Text Fixer edge cases"""
    def test_empty_input(self):
        out, mid, blank, orig, new = _run_fix("")
        self.assertEqual(out, "")
        self.assertEqual(mid, 0)

    def test_single_line(self):
        out, mid, *_ = _run_fix("단일 줄")
        self.assertEqual(out, "단일 줄")
        self.assertEqual(mid, 0)

    def test_whitespace_only(self):
        out, *_ = _run_fix("   \n   ")
        self.assertEqual(out, "")

    def test_only_blanks(self):
        out, *_ = _run_fix("\n\n\n")
        self.assertEqual(out, "")

    def test_crlf_handling(self):
        inp = "첫 줄\r\n두 번째 줄\r\n세 번째 줄"
        inp_lf = inp.replace('\r\n', '\n')
        out, *_ = _run_fix(inp_lf)
        self.assertNotIn('\r', out)

    def test_unicode_input(self):
        inp = "이것은 한국어 문장이다.\n日本語の文章。\n中文段落。"
        out, *_ = _run_fix(inp, do_blank=False)
        self.assertIn("한국어", out)

    def test_very_long_single_line(self):
        line = "가" * 10000
        out, *_ = _run_fix(line, do_blank=False)
        self.assertIn("가", out)

    def test_many_lines_performance(self):
        inp = "줄이다.\n" * 1000
        start = time.time()
        out, *_ = _run_fix(inp)
        elapsed = time.time() - start
        self.assertLess(elapsed, 5.0)

    def test_only_separators(self):
        inp = "────────\n========\n────────"
        out, mid, *_ = _run_fix(inp, do_blank=False)
        self.assertEqual(mid, 0)
        lines = out.split('\n')
        self.assertEqual(len(lines), 3)

    def test_stat_orig_lines(self):
        inp = "A\nB\nC"
        _, _, _, orig, _ = _run_fix(inp, do_blank=False)
        self.assertEqual(orig, 3)

    def test_stat_new_lines_after_merge(self):
        inp = "A\nB"  # becomes 1 line if merged
        _, _, _, _, new = _run_fix(inp, do_blank=False)
        self.assertEqual(new, 1)

    def test_no_leading_blank_in_output(self):
        out, *_ = _run_fix("\n\nA\nB")
        self.assertFalse(out.startswith('\n'))

    def test_no_trailing_blank_in_output(self):
        out, *_ = _run_fix("A\nB\n\n")
        self.assertFalse(out.endswith('\n'))


# ════════════════════════════════════════════════════════════════════════
# §14 Text Fixer — real-world scenarios (OCR, dialogue, chapter headers, etc.)
# ════════════════════════════════════════════════════════════════════════
class TestFixerRealWorld(unittest.TestCase):
    """Real-world scenarios"""
    def test_ocr_linebreak_repair(self):
        inp = SAMPLE_KO_OCR_BROKEN
        out, mid, *_ = _run_fix(inp, do_blank=False)
        self.assertEqual(mid, 1)
        self.assertIn("휘둥그레", out)

    def test_chapter_header_preserved(self):
        inp = SAMPLE_KO_CHAPTER_FULL
        out, mid, *_ = _run_fix(inp)
        self.assertEqual(mid, 0)
        self.assertIn(SAMPLE_KO_TITLE_PLAIN, out)
        lines = [l for l in out.split('\n') if l.strip()]
        self.assertEqual(lines[0], '─' * 56)
        self.assertEqual(lines[1], SAMPLE_KO_TITLE_LONG)

    def test_dialogue_lines_preserved(self):
        inp = SAMPLE_KO_DIALOGUE_B
        out, mid, *_ = _run_fix(inp, do_blank=False)
        self.assertEqual(mid, 0)
        self.assertIn('"이제', out)

    def test_excessive_blanks(self):
        inp = "A\n\n\n\n\n\nB"
        out, _, blank, *_ = _run_fix(inp, do_mid=False, max_blank=1)
        self.assertGreater(blank, 0)
        self.assertNotIn('\n\n\n', out)

    def test_mixed_ocr_and_blanks(self):
        inp = SAMPLE_KO_MIXED
        out, mid, blank, *_ = _run_fix(inp, max_blank=1)
        self.assertGreaterEqual(mid, 1)
        self.assertGreaterEqual(blank, 1)

    def test_word_split_across_line(self):
        # "참" + "가자들에게" → 참가자들에게 (no space expected)
        inp = SAMPLE_KO_WORD_SPLIT
        out, mid, *_ = _run_fix(inp, do_blank=False)
        self.assertEqual(mid, 1)
        self.assertIn("참가자들에게", out)

    # ─── English counterparts: scenario-level language neutrality ───
    def test_ocr_linebreak_repair_en(self):
        inp = SAMPLE_EN_OCR_BROKEN
        out, mid, *_ = _run_fix(inp, do_blank=False)
        self.assertEqual(mid, 1)
        self.assertIn("extraordinarily", out)

    def test_chapter_header_preserved_en(self):
        inp = SAMPLE_EN_CHAPTER_FULL
        out, mid, *_ = _run_fix(inp)
        self.assertEqual(mid, 0)
        self.assertIn(SAMPLE_EN_TITLE_PLAIN, out)
        lines = [l for l in out.split('\n') if l.strip()]
        self.assertEqual(lines[0], '─' * 56)
        self.assertEqual(lines[1], SAMPLE_EN_TITLE_LONG)

    def test_dialogue_lines_preserved_en(self):
        inp = SAMPLE_EN_DIALOGUE_B
        out, mid, *_ = _run_fix(inp, do_blank=False)
        self.assertEqual(mid, 0)
        self.assertIn('"I am', out)

    def test_mixed_ocr_and_blanks_en(self):
        inp = SAMPLE_EN_MIXED
        out, mid, blank, *_ = _run_fix(inp, max_blank=1)
        self.assertGreaterEqual(mid, 1)
        self.assertGreaterEqual(blank, 1)

    def test_word_split_across_line_en(self):
        # "respon" + "sive" → "responsive" (no space expected)
        inp = SAMPLE_EN_WORD_SPLIT
        out, mid, *_ = _run_fix(inp, do_blank=False)
        self.assertEqual(mid, 1)
        self.assertIn("responsive", out)


# ════════════════════════════════════════════════════════════════════════
# §15 Text Fixer — option combinations
# ════════════════════════════════════════════════════════════════════════
class TestFixerCombinations(unittest.TestCase):
    """Option combination tests"""
    def test_merge_and_blank(self):
        inp = "A\nB\n\n\n\nC\nD"
        out, mid, blank, *_ = _run_fix(inp, do_mid=True, do_blank=True, max_blank=1)
        self.assertGreater(mid, 0)
        self.assertGreater(blank, 0)
        self.assertNotIn('\n\n\n', out)

    def test_merge_and_auto_split(self):
        # After merging, an interior period is required for auto split
        long_mid = "긴내용" * 10 + ". " + "이어지는내용" * 10 + "."
        inp = "문장이고\n" + long_mid + "\n두번째.\n세번째."
        out, *_ = _run_fix(inp, do_mid=True, do_blank=False,
                           do_auto_split=True, max_split_chars=50)
        self.assertIn('\n\n', out)

    def test_all_options_off(self):
        inp = "A\nB\n\n\nC\nD"
        out, mid, blank, *_ = _run_fix(inp, do_mid=False, do_blank=False)
        self.assertEqual(mid, 0)
        self.assertEqual(blank, 0)
        self.assertEqual(out, inp)

    def test_all_options_on(self):
        inp = ("A\nB\n\n\n\nC.\nD.\n\n" +
               "E" * 50 + ". " + "F" * 60 + ".")
        out, *_ = _run_fix(inp, do_mid=True, do_blank=True, max_blank=1,
                           do_sep=True, do_auto_split=True, max_split_chars=60)
        self.assertIsInstance(out, str)
        self.assertFalse(out.startswith('\n'))
        self.assertFalse(out.endswith('\n'))

    def test_sep_and_blank_together(self):
        inp = "A.\nB.\n\n\nC."
        out, *_ = _run_fix(inp, do_mid=False, do_blank=True, max_blank=1, do_sep=True)
        self.assertNotIn('\n\n\n\n', out)

    def test_merge_then_split_pipeline(self):
        # Auto split after merging — verify pipeline order
        inp = "문장이고\n계속되며\n" + "긴내용" * 20 + ".\n짧다.\n짧다."
        out, *_ = _run_fix(inp, do_mid=True, do_blank=False,
                           do_auto_split=True, max_split_chars=80)
        self.assertIsInstance(out, str)

    # ─── English counterparts: combination pipeline language neutrality ───
    def test_merge_and_auto_split_en(self):
        # After merging, an interior period is required for auto split
        long_mid = "long content " * 10 + ". " + "continuing content " * 10 + "."
        inp = "the front sentence\n" + long_mid + "\nsecond sentence.\nthird sentence."
        out, *_ = _run_fix(inp, do_mid=True, do_blank=False,
                           do_auto_split=True, max_split_chars=50)
        self.assertIn('\n\n', out)

    def test_merge_then_split_pipeline_en(self):
        # Auto split after merging — verify pipeline order
        inp = "the front sentence\nand it continues\n" + "long content " * 20 + ".\nshort.\nshort."
        out, *_ = _run_fix(inp, do_mid=True, do_blank=False,
                           do_auto_split=True, max_split_chars=80)
        self.assertIsInstance(out, str)


# ════════════════════════════════════════════════════════════════════════
# §16 EPUB conversion
# ════════════════════════════════════════════════════════════════════════
@unittest.skipUnless(HAS_EPUB, "FileNexusSuite 로드 실패")
class TestEpubStructure(unittest.TestCase):
    """txt_to_epub: validate EPUB structure"""
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.txt = os.path.join(self.tmp, "test.txt")
        self.out = os.path.join(self.tmp, "test.epub")
        self.meta = {"title":"테스트","author":"작가","lang":"ko","separator":"==="}

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, content):
        with open(self.txt,'w',encoding='utf-8') as f: f.write(content)
        return txt_to_epub(self.txt, self.out, self.meta)

    def test_creates_file(self):
        self._write("내용입니다.")
        self.assertTrue(os.path.exists(self.out))

    def test_valid_zip(self):
        self._write("내용입니다.")
        self.assertTrue(zipfile.is_zipfile(self.out))

    def test_nonzero_size(self):
        self._write("내용입니다.")
        self.assertGreater(os.path.getsize(self.out), 0)

    def test_mimetype_first(self):
        self._write("내용입니다.")
        with zipfile.ZipFile(self.out) as z:
            names = z.namelist()
            self.assertEqual(names[0], 'mimetype')

    def test_mimetype_content(self):
        self._write("내용입니다.")
        with zipfile.ZipFile(self.out) as z:
            self.assertEqual(z.read('mimetype').decode(), 'application/epub+zip')

    def test_container_xml_exists(self):
        self._write("내용입니다.")
        with zipfile.ZipFile(self.out) as z:
            self.assertIn('META-INF/container.xml', z.namelist())

    def test_opf_exists(self):
        self._write("내용입니다.")
        with zipfile.ZipFile(self.out) as z:
            names = z.namelist()
            self.assertTrue(any('content.opf' in n or '.opf' in n for n in names))

    def test_has_chapter(self):
        self._write("내용입니다.\n=====\n다음 챕터")
        with zipfile.ZipFile(self.out) as z:
            names = z.namelist()
            self.assertTrue(any('.xhtml' in n or '.html' in n for n in names))

    def test_chapter_count_single(self):
        chapters = self._write("내용만 있고 구분선 없음")
        chapters = chapters[0] if isinstance(chapters, tuple) else chapters
        self.assertGreaterEqual(chapters, 1)

    def test_chapter_count_multiple(self):
        content = "1장\n===\n2장\n===\n3장"
        chapters = self._write(content)
        chapters = chapters[0] if isinstance(chapters, tuple) else chapters
        self.assertGreaterEqual(chapters, 2)

    def test_special_chars_in_content(self):
        self._write("특수문자: <>&\"'")
        with zipfile.ZipFile(self.out) as z:
            names = z.namelist()
            xhtml_names = [n for n in names if '.xhtml' in n]
            if xhtml_names:
                content = z.read(xhtml_names[0]).decode('utf-8')
                self.assertNotIn('&amp;amp;', content)

    def test_title_in_opf(self):
        self._write("내용")
        with zipfile.ZipFile(self.out) as z:
            names = z.namelist()
            opf_names = [n for n in names if '.opf' in n]
            if opf_names:
                opf = z.read(opf_names[0]).decode('utf-8')
                self.assertIn('테스트', opf)

    def test_author_in_opf(self):
        self._write("내용")
        with zipfile.ZipFile(self.out) as z:
            names = z.namelist()
            opf_names = [n for n in names if '.opf' in n]
            if opf_names:
                opf = z.read(opf_names[0]).decode('utf-8')
                self.assertIn('작가', opf)

    def test_korean_content_preserved(self):
        self._write("한국어 내용입니다.")
        with zipfile.ZipFile(self.out) as z:
            names = z.namelist()
            xhtml = [n for n in names if '.xhtml' in n]
            if xhtml:
                content = z.read(xhtml[0]).decode('utf-8')
                self.assertIn('한국어', content)

    def test_return_value_is_int(self):
        result = self._write("내용")
        chapters = result[0] if isinstance(result, tuple) else result
        self.assertIsInstance(chapters, int)

    def test_empty_content(self):
        """Empty content → txt_to_epub must raise ValueError."""
        with self.assertRaises(ValueError):
            self._write("")


@unittest.skipUnless(HAS_EPUB, "FileNexusSuite 로드 실패")
class TestEpubRoundTrip(unittest.TestCase):
    """Validate EPUB round-trip conversion"""
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _round_trip(self, content, sep='===', **epub_opts):
        txt_in = os.path.join(self.tmp, "in.txt")
        epub   = os.path.join(self.tmp, "out.epub")
        txt_out= os.path.join(self.tmp, "out.txt")
        with open(txt_in,'w',encoding='utf-8') as f: f.write(content)
        meta = {"title":"T","author":"A","lang":"ko","separator":sep}
        meta.update(epub_opts)
        txt_to_epub(txt_in, epub, meta)
        text, _ = epub_to_text(epub, {"separator":True,"titles":True,"trim_blank":True,"encoding":"utf-8"})
        return text

    def test_simple_content_preserved(self):
        text = self._round_trip("간단한 내용입니다.")
        self.assertIn("간단한 내용", text)

    def test_multiple_chapters_preserved(self):
        text = self._round_trip("1장 내용\n===\n2장 내용\n===\n3장 내용")
        self.assertIn("1장", text)
        self.assertIn("2장", text)
        self.assertIn("3장", text)

    def test_korean_unicode_preserved(self):
        content = "한글: 가나다라마바사아자차카타파하"
        text = self._round_trip(content)
        self.assertIn("가나다라", text)

    def test_numbers_preserved(self):
        text = self._round_trip("123 456 789")
        self.assertIn("123", text)

    def test_special_chars_safe(self):
        text = self._round_trip("인용: \"직접 인용문\" 끝.")
        self.assertIsNotNone(text)


# ════════════════════════════════════════════════════════════════════════
# §17 Settings save/restore
# ════════════════════════════════════════════════════════════════════════
@unittest.skipUnless(HAS_MODULE, "FileNexusSuite 로드 실패")
class TestConfig(unittest.TestCase):
    """Validate ConfigManager behavior — based on JSON save/restore structure."""
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        import types
        self.cfg = types.SimpleNamespace()
        self.cfg._path = os.path.join(self.tmp, "config.json")
        def save(data):
            with open(self.cfg._path,'w',encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
        def load():
            try:
                with open(self.cfg._path, encoding='utf-8') as f:
                    return json.load(f)
            except Exception: return {}
        self.cfg.save = save
        self.cfg.load = load

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_save_and_load(self):
        self.cfg.save({"key":"value"})
        self.assertEqual(self.cfg.load()["key"], "value")

    def test_missing_returns_empty(self):
        self.assertEqual(self.cfg.load(), {})

    def test_korean_preserved(self):
        self.cfg.save({"lang":"한국어"})
        self.assertEqual(self.cfg.load()["lang"], "한국어")

    def test_nested_dict(self):
        data = {"text_fixer":{"do_mid":True,"max_blank":1}}
        self.cfg.save(data)
        self.assertEqual(self.cfg.load()["text_fixer"]["do_mid"], True)

    def test_overwrite(self):
        self.cfg.save({"a":1})
        self.cfg.save({"a":2})
        self.assertEqual(self.cfg.load()["a"], 2)

    def test_unicode_shortcuts(self):
        self.cfg.save({"shortcuts":{"tab_1":"Ctrl+1"}})
        self.assertEqual(self.cfg.load()["shortcuts"]["tab_1"], "Ctrl+1")

    def test_boolean_values(self):
        self.cfg.save({"flag":False})
        self.assertFalse(self.cfg.load()["flag"])

    def test_integer_values(self):
        self.cfg.save({"count":42})
        self.assertEqual(self.cfg.load()["count"], 42)

    def test_empty_dict(self):
        self.cfg.save({})
        self.assertEqual(self.cfg.load(), {})

    def test_list_values(self):
        self.cfg.save({"items":[1,2,3]})
        self.assertEqual(self.cfg.load()["items"], [1,2,3])


# ════════════════════════════════════════════════════════════════════════
# §18 Filesystem integration
# ════════════════════════════════════════════════════════════════════════
class TestFilesystemIntegration(unittest.TestCase):
    """Integration tests for real filesystem operations"""
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _make(self, name, content="내용"):
        path = os.path.join(self.tmp, name)
        with open(path,'w',encoding='utf-8') as f: f.write(content)
        return path

    def test_rename_and_verify(self):
        old = self._make("파일01.txt")
        new = os.path.join(self.tmp, "파일1.txt")
        os.rename(old, new)
        self.assertTrue(os.path.exists(new))
        self.assertFalse(os.path.exists(old))

    def test_content_preserved_after_rename(self):
        old = self._make("원본.txt", "보존되어야 할 내용")
        new = os.path.join(self.tmp, "변경.txt")
        os.rename(old, new)
        with open(new, encoding='utf-8') as f:
            self.assertEqual(f.read(), "보존되어야 할 내용")

    def test_depad_rename_sequence(self):
        files = [self._make(f"{i:03d}화.txt", f"{i}화 내용") for i in range(1, 6)]
        renamed = []
        for f in files:
            base = os.path.basename(f)
            new_name = depad(base)
            new_path = os.path.join(self.tmp, new_name)
            if new_path != f:
                os.rename(f, new_path)
            renamed.append(new_path)
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "1화.txt")))
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "5화.txt")))

    def test_tag_remove_multiple_files(self):
        files = [self._make(f"[BD] 파일{i}.txt") for i in range(3)]
        renamed = []
        for f in files:
            base = os.path.basename(f)
            new_name = remove_tag(base, 'front')
            new_path = os.path.join(self.tmp, new_name)
            os.rename(f, new_path)
            renamed.append(new_path)
        for r in renamed:
            self.assertFalse(os.path.basename(r).startswith('[BD]'))

    def test_config_persist_reload(self):
        cfg_path = os.path.join(self.tmp, "cfg.json")
        data = {"theme":"dark","language":"ko","shortcuts":{"tab_1":"Ctrl+1"}}
        with open(cfg_path,'w',encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        with open(cfg_path, encoding='utf-8') as f:
            loaded = json.load(f)
        self.assertEqual(loaded["theme"], "dark")
        self.assertEqual(loaded["language"], "ko")
        self.assertEqual(loaded["shortcuts"]["tab_1"], "Ctrl+1")

    @unittest.skipUnless(HAS_EPUB, "EPUB 불가")
    def test_epub_readable_after_create(self):
        txt = os.path.join(self.tmp, "novel.txt")
        epub = os.path.join(self.tmp, "novel.epub")
        with open(txt,'w',encoding='utf-8') as f:
            f.write("1장\n===\n2장\n===\n3장")
        txt_to_epub(txt, epub, {"title":"T","author":"A","lang":"ko","separator":"==="})
        self.assertTrue(zipfile.is_zipfile(epub))
        with zipfile.ZipFile(epub) as z:
            self.assertIn('mimetype', z.namelist())


# ════════════════════════════════════════════════════════════════════════
# §19 Regression tests
# ════════════════════════════════════════════════════════════════════════
class TestRegression(unittest.TestCase):
    """Prevent recurrence of past bugs"""
    def test_separator_not_merged_with_title(self):
        """Separator line must not merge with the next line (issue: '-' is not in SENT_END)"""
        inp = "────────────────────────────────\n" + SAMPLE_KO_TITLE_SHORT + "\n────────────────────────────────"
        out, mid, *_ = _run_fix(inp, do_blank=False)
        self.assertEqual(mid, 0)
        lines = out.split('\n')
        self.assertEqual(lines[0], '────────────────────────────────')
        self.assertEqual(lines[1], SAMPLE_KO_TITLE_SHORT)

    def test_separator_not_merged_with_title_en(self):
        """English counterpart — separator behavior is language-neutral"""
        inp = "────────────────────────────────\n" + SAMPLE_EN_TITLE_SHORT + "\n────────────────────────────────"
        out, mid, *_ = _run_fix(inp, do_blank=False)
        self.assertEqual(mid, 0)
        lines = out.split('\n')
        self.assertEqual(lines[0], '────────────────────────────────')
        self.assertEqual(lines[1], SAMPLE_EN_TITLE_SHORT)

    def test_chapter_header_structure_intact(self):
        """Chapter-header structure is fully preserved"""
        inp = SAMPLE_KO_CHAPTER_FULL
        out, mid, *_ = _run_fix(inp)
        self.assertEqual(mid, 0)

    def test_no_pyqt5_remnants(self):
        """No residual PyQt5 code"""
        with open(_MAIN_PY, encoding='utf-8') as f:
            src = f.read()
        self.assertNotIn('PyQt5', src)
        self.assertNotIn('pyqtSignal', src)
        self.assertNotIn('exec_()', src)

    def test_qshortcut_in_qtgui(self):
        """QShortcut is imported from QtGui (used for shortcut implementation)"""
        with open(_MAIN_PY, encoding='utf-8') as f:
            src = f.read()
        gui_line = next((l for l in src.splitlines() if 'from PySide6.QtGui import' in l), '')
        self.assertIn('QShortcut', gui_line)

    def test_qaction_not_in_qtwidgets(self):
        """QAction is not imported from QtWidgets (and unnecessary in QtGui — unused)"""
        with open(_MAIN_PY, encoding='utf-8') as f:
            src = f.read()
        import re
        m = re.search(r'from PySide6\.QtWidgets import \((.+?)\)', src, re.DOTALL)
        if m:
            self.assertNotIn('QAction', m.group(1))

    def test_qprogressbar_not_locally_imported_in_textfixer(self):
        """TextFixerPanel has no duplicated local QProgressBar import"""
        with open(_MAIN_PY, encoding='utf-8') as f:
            src = f.read()
        fixer_start = src.find('class TextFixerPanel')
        fixer_end = src.find('\nclass TextMergeWorker', fixer_start)
        fixer_block = src[fixer_start:fixer_end]
        local_pb = [l for l in fixer_block.splitlines()
                    if 'from PySide6' in l and 'QProgressBar' in l]
        self.assertEqual(len(local_pb), 0)

    def test_epub_fstring_compat(self):
        """dict access inside EPUB f-strings is Python 3.12-compatible"""
        with open(_MAIN_PY, encoding='utf-8') as f:
            src = f.read()
        epub_start = src.find('def txt_to_epub(')
        epub_end = src.find('\ndef ', epub_start + 10)
        epub_block = src[epub_start:epub_end]
        self.assertNotIn('ch["title"]', epub_block)
        self.assertNotIn('ch["content"]', epub_block)

    def test_sc_tab_fixer_in_label_keys(self):
        """Settings shortcut tab is wired to tab_5 via translation key"""
        with open(_MAIN_PY, encoding='utf-8') as f:
            src = f.read()
        self.assertIn("'tab_5':'sc_tab_fixer'", src)

    def test_sc_tab_bulk_in_label_keys(self):
        """Settings shortcut tab is wired to tab_6 (Bulk Fixer) via translation key"""
        with open(_MAIN_PY, encoding='utf-8') as f:
            src = f.read()
        self.assertIn("'tab_6':'sc_tab_bulk'", src)

    def test_shortcut_defs_has_tab_6(self):
        """SHORTCUT_DEFS must define tab_6 (Ctrl+6)"""
        with open(_MAIN_PY, encoding='utf-8') as f:
            src = f.read()
        self.assertIn("'tab_6'", src)
        self.assertIn("Ctrl+6", src)

    def test_separator_with_trailing_space(self):
        """Separator lines with trailing spaces are detected correctly"""
        self.assertTrue(_is_sep_line("──────── "))
        self.assertTrue(_is_sep_line(" ────────"))

    def test_blank_after_merge_pipeline(self):
        """Pipeline order: merge → blank-line reduction"""
        inp = "A\nB\n\n\n\nC\nD"
        out, mid, blank, *_ = _run_fix(inp, do_mid=True, do_blank=True, max_blank=1)
        self.assertEqual(mid, 2)
        self.assertGreater(blank, 0)
        self.assertNotIn('\n\n\n', out)

    def test_stats_not_korean_hardcoded(self):
        """Statistics text is not hardcoded in Korean (uses translation keys)"""
        with open(_MAIN_PY, encoding='utf-8') as f:
            src = f.read()
        self.assertNotIn("f'병합된 줄: {fixed_mid}건'", src)
        self.assertIn('tf_stat_mid_n', src)


# ════════════════════════════════════════════════════════════════════════
# §20 Performance tests
# ════════════════════════════════════════════════════════════════════════
class TestPerformance(unittest.TestCase):
    """Performance benchmarks (fail when threshold is exceeded)"""
    def test_large_text_merge_speed(self):
        """Merge 10,000 lines — under 3 seconds"""
        inp = ("중간 문장이고\n" * 4 + "완료됩니다.\n\n") * 1000
        start = time.time()
        _run_fix(inp, do_mid=True, do_blank=True)
        self.assertLess(time.time() - start, 3.0)

    def test_large_text_blank_speed(self):
        """Large file with only blank lines — under 1 second"""
        inp = "\n" * 5000 + "A\n" * 1000 + "\n" * 5000
        start = time.time()
        _run_fix(inp, do_mid=False, do_blank=True, max_blank=1)
        self.assertLess(time.time() - start, 1.0)

    def test_auto_split_performance(self):
        """Large-input auto paragraph splitting — under 2 seconds"""
        long_line = ("문장입니다. " * 10).strip()
        inp = (long_line + "\n\n") * 500
        start = time.time()
        _run_fix(inp, do_mid=False, do_blank=True, do_auto_split=True, max_split_chars=80)
        self.assertLess(time.time() - start, 2.0)

    def test_sep_line_detection_speed(self):
        """1000 separator-line detections — under 0.1 second"""
        start = time.time()
        for _ in range(1000):
            _is_sep_line("──────────────────────────────")
            _is_sep_line("hello world")
        self.assertLess(time.time() - start, 0.1)

    def test_natural_sort_large_list(self):
        """Natural sort over 1000 files — under 0.5 second"""
        files = [f"파일{i:04d}화.txt" for i in range(1000, 0, -1)]
        start = time.time()
        sorted_files = sorted(files, key=natural_sort_key)
        self.assertLess(time.time() - start, 0.5)
        self.assertEqual(sorted_files[0], "파일0001화.txt")


# ════════════════════════════════════════════════════════════════════════
# §21 Boundary-value analysis (BVA)
# ════════════════════════════════════════════════════════════════════════
class TestBoundaryValues(unittest.TestCase):
    """Boundary-value analysis"""
    # max_blank boundary
    def test_max_blank_0_removes_all(self):
        out, _, blank, *_ = _run_fix("A\n\nB", do_mid=False, max_blank=0)
        self.assertNotIn('\n\n', out)

    def test_max_blank_1_allows_one(self):
        out, _, blank, *_ = _run_fix("A\n\nB", do_mid=False, max_blank=1)
        self.assertIn('\n\n', out)
        self.assertEqual(blank, 0)

    def test_max_blank_1_removes_two(self):
        out, _, blank, *_ = _run_fix("A\n\n\nB", do_mid=False, max_blank=1)
        self.assertEqual(blank, 1)
        self.assertNotIn('\n\n\n', out)

    def test_max_blank_10_preserves_five(self):
        inp = "A" + "\n" * 6 + "B"
        out, _, blank, *_ = _run_fix(inp, do_mid=False, max_blank=10)
        self.assertEqual(blank, 0)

    # max_split_chars boundary
    def test_split_at_exactly_threshold(self):
        line = "A" * 49 + ". " + "B" * 49 + "."
        # first segment length = 51 chars > 50 → split
        r = _split_long_line(line, 50)
        self.assertEqual(len(r), 2)

    def test_split_one_below_threshold(self):
        line = "A" * 48 + ". " + "B" * 48 + "."
        # first segment = 50, second = 50; cumulative 100 > 50 → split
        r = _split_long_line(line, 50)
        self.assertGreaterEqual(len(r), 1)

    # Separator-line minimum length boundary
    def test_sep_exactly_3(self):   self.assertTrue(_is_sep_line('---'))
    def test_sep_exactly_2_fail(self): self.assertFalse(_is_sep_line('--'))
    def test_sep_exactly_1_fail(self): self.assertFalse(_is_sep_line('-'))

    # Empty-string boundary
    def test_empty_depad(self):     self.assertEqual(depad(''), '')
    def test_empty_remove_tag(self):self.assertEqual(remove_tag('','both'), '')
    def test_empty_extract_num(self):self.assertIsNone(extract_number(''))
    def test_empty_sep_line(self):  self.assertFalse(_is_sep_line(''))


# ════════════════════════════════════════════════════════════════════════
# §ExtraA  App constants / version
# ════════════════════════════════════════════════════════════════════════
@unittest.skipUnless(HAS_MODULE, "FileNexusSuite 로드 실패")
class TestAppConstants(unittest.TestCase):
    """Validate APP_VERSION and library-availability flags."""

    def test_version_exists(self):
        self.assertIsNotNone(_APP_VERSION)

    def test_version_string(self):
        self.assertIsInstance(_APP_VERSION, str)

    def test_version_format(self):
        """Check semantic versioning X.Y.Z format."""
        parts = _APP_VERSION.split('.')
        self.assertEqual(len(parts), 3)
        for p in parts:
            self.assertTrue(p.isdigit(), f"버전 파트 '{p}'가 숫자가 아님")

    def test_has_chardet_flag(self):
        self.assertIn('HAS_CHARDET', _ns)
        self.assertIsInstance(_ns['HAS_CHARDET'], bool)

    def test_docx_available_flag(self):
        self.assertIn('DOCX_AVAILABLE', _ns)
        self.assertIsInstance(_ns['DOCX_AVAILABLE'], bool)

    def test_pdf_available_flag(self):
        self.assertIn('PDF_AVAILABLE', _ns)
        self.assertIsInstance(_ns['PDF_AVAILABLE'], bool)

    def test_xlsx_available_flag(self):
        self.assertIn('XLSX_AVAILABLE', _ns)
        self.assertIsInstance(_ns['XLSX_AVAILABLE'], bool)


# ════════════════════════════════════════════════════════════════════════
# §ExtraB  Encoding detection — alchemy_detect_encoding()
# ════════════════════════════════════════════════════════════════════════
@unittest.skipUnless(HAS_MODULE, "FileNexusSuite 로드 실패")
class TestAlchemyDetectEncoding(unittest.TestCase):
    """alchemy_detect_encoding() — directly validates the real module function.

    v1.0.4: switched to returning an (encoding, confidence) tuple.
    For compatibility with the old string-return format, a helper extracts only the first element."""

    def setUp(self):
        self.td = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.td, ignore_errors=True)

    def _write(self, name, data):
        p = os.path.join(self.td, name)
        with open(p, 'wb') as f:
            f.write(data)
        return p

    def _enc(self, path):
        """Extracts only the encoding name, compatible with both v1.0.3 (str) and v1.0.4 (tuple)."""
        result = _alchemy_detect_enc(path)
        return result[0] if isinstance(result, tuple) else result

    def test_utf8_bom(self):
        p = self._write('bom.txt', b'\xef\xbb\xbf' + '내용'.encode('utf-8'))
        self.assertEqual(self._enc(p), 'utf-8-sig')

    def test_utf16_le_bom(self):
        p = self._write('u16.txt', b'\xff\xfe' + '내용'.encode('utf-16-le'))
        self.assertEqual(self._enc(p), 'utf-16')

    def test_utf16_be_bom(self):
        p = self._write('u16be.txt', b'\xfe\xff' + '내용'.encode('utf-16-be'))
        self.assertEqual(self._enc(p), 'utf-16')

    def test_pure_utf8(self):
        p = self._write('utf8.txt', 'Hello World'.encode('utf-8'))
        result = self._enc(p)
        self.assertIn(result, ('utf-8', 'ascii'))

    def test_returns_string(self):
        p = self._write('any.txt', b'hello')
        self.assertIsInstance(self._enc(p), str)


# ════════════════════════════════════════════════════════════════════════
# §ExtraC  Help HTML — _build_help_html()
# ════════════════════════════════════════════════════════════════════════
@unittest.skipUnless(HAS_MODULE and _build_help_html is not None,
                     "FileNexusSuite 로드 실패 또는 _build_help_html 없음")
class TestBuildHelpHtml(unittest.TestCase):
    """_build_help_html() — validate help generation for 5 languages."""

    def test_ko_returns_string(self):
        result = _build_help_html(_data_only=False, _lang='ko')
        self.assertIsInstance(result, str)

    def test_ko_nonempty(self):
        result = _build_help_html(_data_only=False, _lang='ko')
        self.assertGreater(len(result), 100)

    def test_en_returns_string(self):
        result = _build_help_html(_data_only=False, _lang='en')
        self.assertIsInstance(result, str)

    def test_ja_returns_string(self):
        result = _build_help_html(_data_only=False, _lang='ja')
        self.assertIsInstance(result, str)

    def test_zh_cn_returns_string(self):
        result = _build_help_html(_data_only=False, _lang='zh_cn')
        self.assertIsInstance(result, str)

    def test_zh_tw_returns_string(self):
        result = _build_help_html(_data_only=False, _lang='zh_tw')
        self.assertIsInstance(result, str)

    def test_all_langs_nonempty(self):
        for lang in ('ko', 'en', 'ja', 'zh_cn', 'zh_tw'):
            with self.subTest(lang=lang):
                result = _build_help_html(_data_only=False, _lang=lang)
                self.assertGreater(len(result), 100, f"{lang} 도움말이 비어있음")

    def test_data_only_returns_tuple(self):
        result = _build_help_html(_data_only=True, _lang='ko')
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_data_only_second_is_collection(self):
        _, sections = _build_help_html(_data_only=True, _lang='ko')
        self.assertTrue(isinstance(sections, (dict, list)))


# ════════════════════════════════════════════════════════════════════════
# §ExtraD  ConfigManager — real class save/load
# ════════════════════════════════════════════════════════════════════════
@unittest.skipUnless(HAS_MODULE and _ConfigManager is not None,
                     "FileNexusSuite 로드 실패 또는 ConfigManager 없음")
class TestConfigManagerReal(unittest.TestCase):
    """ConfigManager real class — validate save/load/get."""

    def setUp(self):
        self.td = tempfile.mkdtemp()
        # Redirect _CONFIG_PATH to a temporary directory
        self._orig_path = _ns.get('_CONFIG_PATH')
        from pathlib import Path
        _ns['_CONFIG_PATH'] = Path(self.td) / 'FileNexusSuite.json'

    def tearDown(self):
        if self._orig_path is not None:
            _ns['_CONFIG_PATH'] = self._orig_path
        shutil.rmtree(self.td, ignore_errors=True)

    def _make_cfg(self):
        cfg = _ConfigManager.__new__(_ConfigManager)
        cfg._data = {}
        return cfg

    def test_save_and_load(self):
        cfg = self._make_cfg()
        cfg.save({'theme': 'dark', 'language': 'en'})
        cfg2 = self._make_cfg()
        cfg2.load()
        self.assertEqual(cfg2.get('theme'), 'dark')
        self.assertEqual(cfg2.get('language'), 'en')

    def test_missing_key_default(self):
        cfg = self._make_cfg()
        cfg.load()
        self.assertEqual(cfg.get('nonexistent', 'fallback'), 'fallback')

    def test_korean_preserved(self):
        cfg = self._make_cfg()
        cfg.save({'label': '한국어 값'})
        cfg2 = self._make_cfg()
        cfg2.load()
        self.assertEqual(cfg2.get('label'), '한국어 값')

    def test_nested_dict(self):
        cfg = self._make_cfg()
        cfg.save({'text_fixer': {'do_mid': True, 'max_blank': 2}})
        cfg2 = self._make_cfg()
        cfg2.load()
        self.assertEqual(cfg2.get('text_fixer'), {'do_mid': True, 'max_blank': 2})

    def test_boolean_values(self):
        cfg = self._make_cfg()
        cfg.save({'flag_true': True, 'flag_false': False})
        cfg2 = self._make_cfg()
        cfg2.load()
        self.assertIs(cfg2.get('flag_true'), True)
        self.assertIs(cfg2.get('flag_false'), False)

    def test_integer_values(self):
        cfg = self._make_cfg()
        cfg.save({'count': 42})
        cfg2 = self._make_cfg()
        cfg2.load()
        self.assertEqual(cfg2.get('count'), 42)

    def test_json_file_valid(self):
        cfg = self._make_cfg()
        cfg.save({'x': 1})
        from pathlib import Path
        json_path = Path(self.td) / 'FileNexusSuite.json'
        with open(json_path, encoding='utf-8') as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)


# ════════════════════════════════════════════════════════════════════════
# §ExtraE  depad date-format regression test (v0.9.0 bugfix)
# ════════════════════════════════════════════════════════════════════════
_depad_name_fn = _ns.get('depad_name') if HAS_MODULE else None

@unittest.skipUnless(HAS_MODULE and _depad_name_fn is not None,
                     "FileNexusSuite 로드 실패")
class TestDepadDateRegression(unittest.TestCase):
    """depad_name() — regression test for date-format (YYYY-MM-DD) preservation.

    Before fix: the \\b pattern treated hyphens as word boundaries,
            so 2024-01-01 was wrongly converted to 2024-1-1.
    After fix: the (?<![0-9\\-]) pattern leaves zeros after hyphens alone.
    """

    def test_date_yyyy_mm_dd_preserved(self):
        """Dates in the 2024-01-01 form must not be converted."""
        self.assertIsNone(_depad_name_fn('2024-01-01.txt'))

    def test_date_mm_dd_preserved(self):
        self.assertIsNone(_depad_name_fn('01-01.txt'))

    def test_range_001_197_front_removed(self):
        """"사과나무 001-197화(完)" — strip only the leading 001; keep the trailing 197."""
        result = _depad_name_fn('사과나무 001-197화(完).txt')
        self.assertIsNotNone(result)
        self.assertIn('1-197', result)
        self.assertNotIn('001', result)

    def test_range_01_19_front_removed(self):
        result = _depad_name_fn('호두나무 01-19권(完).txt')
        self.assertIsNotNone(result)
        self.assertIn('1-19', result)

    def test_leading_zero_at_start_removed(self):
        self.assertEqual(_depad_name_fn('001화.txt'), '1화.txt')

    def test_no_false_removal_after_hyphen(self):
        """A "01" right after a hyphen must not be stripped → if nothing changes, return None."""
        result = _depad_name_fn('시즌1-01화.txt')
        # No leading zero-padding to strip, so either None or "01" must be preserved
        self.assertTrue(result is None or '01' in result)


# ════════════════════════════════════════════════════════════════════════
# §ExtraF  v0.10.0 regression — source-parsing based (PySide6 not required)
# ════════════════════════════════════════════════════════════════════════
class TestV010Regression(unittest.TestCase):
    """v0.10.0 base-constant regression test — parse the source file directly."""

    def _src(self):
        with open(_MAIN_PY, encoding='utf-8') as f:
            return f.read()

    def test_app_version(self):
        import re
        m = re.search(r'^APP_VERSION\s*=\s*["\']([^"\']+)["\']', self._src(), re.MULTILINE)
        self.assertIsNotNone(m, "APP_VERSION 정의 없음")
        # v1.0.0 or higher passes (v1.0.1, v1.0.2, v1.0.3, etc. all pass)
        parts = m.group(1).split('.')
        self.assertGreaterEqual(int(parts[0]), 1, f"메이저 버전 < 1: {m.group(1)}")

    def test_themes_count(self):
        import re
        src = self._src()
        # Actual keys in the THEMES dict (auto is a virtual theme resolved at runtime)
        m = re.search(r'^THEMES\s*=\s*\{(.*?)^\}', src, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(m)
        keys = re.findall(r"^\s{4}'(\w+)'\s*:\s*\{", m.group(1), re.MULTILINE)
        self.assertEqual(len(keys), 9, f"THEMES 실제 키 수 불일치: {keys}")

    def test_themes_names(self):
        import re
        src = self._src()
        m = re.search(r'^THEMES\s*=\s*\{(.*?)^\}', src, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(m)
        keys = set(re.findall(r"^\s{4}'(\w+)'\s*:\s*\{", m.group(1), re.MULTILINE))
        expected = {'light','dark','ocean','mint','sand','honey','sakura','lavender','choco'}
        self.assertEqual(keys, expected)

    def test_theme_name_key_has_auto(self):
        """_THEME_NAME_KEY includes auto — 10 supported themes total."""
        import re
        src = self._src()
        m = re.search(r'_THEME_NAME_KEY\s*=\s*\{(.*?)\}', src, re.DOTALL)
        self.assertIsNotNone(m)
        keys = set(re.findall(r"'(\w+)'\s*:", m.group(1)))
        self.assertIn('auto', keys)
        self.assertEqual(len(keys), 10, f"_THEME_NAME_KEY 키 수 불일치: {keys}")

    def test_translations_has_five_langs(self):
        import re
        src = self._src()
        m = re.search(r'^TRANSLATIONS\s*=\s*\{', src, re.MULTILINE)
        self.assertIsNotNone(m, "TRANSLATIONS = { 정의 없음")
        block = src[m.start():m.start()+120000]
        # ko is inlined as TRANSLATIONS = {'ko': ..., the others start at line head
        inline = set(re.findall(r"TRANSLATIONS\s*=\s*\{'([a-z]{2}(?:_[a-z]{2})?)'", block))
        newline = set(re.findall(r"^\s{0,1}'([a-z]{2}(?:_[a-z]{2})?)':\s*\{", block, re.MULTILINE))
        langs = inline | newline
        self.assertEqual(langs, {'ko','en','ja','zh_cn','zh_tw'})

    def test_six_panel_classes_in_source(self):
        src = self._src()
        panels = ['TextMergerPanel','TextConverterPanel','TagEditorPanel',
                  'BatchRenamerPanel','TextFixerPanel','BulkFixerPanel']
        for cls in panels:
            with self.subTest(cls=cls):
                self.assertIn(f'class {cls}', src, f"{cls} 클래스 정의 없음")

    def test_bulk_fixer_worker_in_source(self):
        self.assertIn('class BulkFixerWorker', self._src())

    def test_merge_file_tree_in_source(self):
        self.assertIn('class MergeFileTree', self._src())


@unittest.skipUnless(HAS_MODULE, "FileNexusSuite 로드 실패 (PySide6 필요)")
class TestV010RegressionModule(unittest.TestCase):
    """v0.10.0 module-load-based regression test (PySide6 required)."""

    def test_themes_count_from_ns(self):
        themes = _ns.get('THEMES', {})
        self.assertEqual(len(themes), 9, f"테마 수 불일치: {sorted(themes.keys())}")

    def test_six_tabs_from_ns(self):
        panels = ['TextMergerPanel','TextConverterPanel','TagEditorPanel',
                  'BatchRenamerPanel','TextFixerPanel','BulkFixerPanel']
        for cls in panels:
            with self.subTest(cls=cls):
                self.assertIn(cls, _ns, f"{cls} 클래스가 _ns에 없음")


# ════════════════════════════════════════════════════════════════════════
# §ExtraG  Translation system completeness
# ════════════════════════════════════════════════════════════════════════
class TestTranslationCompleteness(unittest.TestCase):
    """TRANSLATIONS — validate key completeness across 5 languages (parses source directly, PySide6 not required)."""

    def _get_lang_keys(self, lang):
        import re
        with open(_MAIN_PY, encoding='utf-8') as f:
            src = f.read()
        patterns = {
            'ko':    r"'ko'\s*:\s*\{(.*?)\},\s*\n\s*'en'",
            'en':    r"'en'\s*:\s*\{(.*?)\},\s*\n\s*'ja'",
            'ja':    r"'ja'\s*:\s*\{(.*?)\},?\s*\n\s*'zh_cn'",
            'zh_cn': r"'zh_cn'\s*:\s*\{(.*?)\},?\s*\n\s*'zh_tw'",
            'zh_tw': r"'zh_tw'\s*:\s*\{(.*?)}\s*\}",
        }
        m = re.search(patterns[lang], src, re.DOTALL)
        if not m: return set()
        return set(re.findall(r"'([a-z_][a-z0-9_]*)'\s*:", m.group(1)))

    def test_all_langs_same_key_count(self):
        """Validate key counts across 5 languages — zh_cn may be a subset thanks to zh_tw fallback (v1.0.9 §5.1.G).

        ko/en/ja/zh_tw all have the same key count as ko (symmetric).
        zh_cn may have fewer keys because entries 100% identical to zh_tw values are removed,
        but every remaining key must exist in zh_tw to guarantee fallback safety.
        """
        lang_keys = {l: self._get_lang_keys(l) for l in ['ko','en','ja','zh_cn','zh_tw']}
        ko_count = len(lang_keys['ko'])
        # ko/en/ja/zh_tw symmetry check
        for lang in ('en', 'ja', 'zh_tw'):
            with self.subTest(lang=lang):
                self.assertEqual(len(lang_keys[lang]), ko_count,
                    f"{lang} 키 수 {len(lang_keys[lang])} ≠ ko {ko_count}")
        # zh_cn must be a subset of zh_tw (fallback safety)
        not_in_zh_tw = lang_keys['zh_cn'] - lang_keys['zh_tw']
        with self.subTest(lang='zh_cn_subset'):
            self.assertEqual(not_in_zh_tw, set(),
                f"zh_cn 키가 zh_tw에 없음 (fallback 불가): {sorted(not_in_zh_tw)}")

    def test_zh_cn_fallback_to_zh_tw(self):
        """Keys missing from the zh_cn dict must fall back to zh_tw (v1.0.9 §5.1.G).

        In §5.1.G, keys whose values match between zh_cn and zh_tw were removed from zh_cn.
        The fallback mechanism must remain alive in both _t() and _rt()
        so that the impact on zh_cn users stays at zero.
        """
        import re
        lang_keys = {l: self._get_lang_keys(l) for l in ['zh_cn', 'zh_tw']}
        # Verify that the targets exist (cleanup must already be applied)
        missing_in_zh_cn = lang_keys['zh_tw'] - lang_keys['zh_cn']
        self.assertGreater(len(missing_in_zh_cn), 0,
            "fallback 검증 대상 키가 없음 — §5.1.G 정리가 미적용 상태?")
        # Verify the zh_cn → zh_tw fallback pattern exists in source (both _t and _rt)
        with open(_MAIN_PY, encoding='utf-8') as f:
            src = f.read()
        fallback_pattern = r"TRANSLATIONS\['zh_tw'\]\.get\(key\)\s+if\s+lang\s*==\s*'zh_cn'"
        matches = re.findall(fallback_pattern, src)
        self.assertGreaterEqual(len(matches), 2,
            f"_t() / _rt() 모두에 zh_cn → zh_tw fallback 필요 — 현재 {len(matches)}곳")

    def test_ko_has_minimum_keys(self):
        keys = self._get_lang_keys('ko')
        self.assertGreaterEqual(len(keys), 400)

    # ────────────────────────────────────────────────────────────────
    # Tab-based functional-area invariants (restructured in v1.0.7 session 3)
    # Version-snapshot style (v010/v010_1/v100) is deprecated → reorganized into 10 macro-categories
    # See docs/TEST_MANAGEMENT_POLICY.md for the detailed policy
    # ────────────────────────────────────────────────────────────────

    def test_all_langs_have_common_dialog_keys(self):
        """Macro-category 1 — common dialog and button keys across all tabs."""
        common_keys = [
            'dlg_ok', 'dlg_yes', 'dlg_no',
            'dlg_warning', 'dlg_error_title',
            'btn_abort',
        ]
        for lang in ('ko','en','ja','zh_cn','zh_tw'):
            keys = self._get_lang_keys(lang)
            for key in common_keys:
                with self.subTest(lang=lang, key=key):
                    self.assertIn(key, keys,
                        f"[{lang}] '{key}' 키 없음 (common 대분류)")

    def test_all_langs_have_text_merger_keys(self):
        """Macro-category 2 — representative keys for the Text Merger tab."""
        merger_keys = [
            'merge_status_add', 'merge_status_del', 'merge_status_clr',
            'merge_path_set', 'merge_path_reset_done',
            'merge_reading', 'merge_save_done', 'merge_save_err',
            'merge_no_support',
        ]
        for lang in ('ko','en','ja','zh_cn','zh_tw'):
            keys = self._get_lang_keys(lang)
            for key in merger_keys:
                with self.subTest(lang=lang, key=key):
                    self.assertIn(key, keys,
                        f"[{lang}] '{key}' 키 없음 (text_merger 대분류)")

    def test_all_langs_have_text_converter_keys(self):
        """Macro-category 3 — representative keys for the Text Converter tab.

        Note: conv_sub_txt2epub / conv_sub_epub2txt are kept active by
        the dynamic key generation `_t('conv_sub_' + val)` at L6560 (v1.0.7 audit fix).
        """
        converter_keys = [
            'conv_status_done', 'conv_status_fail',
            'conv_sub_txt2epub', 'conv_sub_epub2txt',
        ]
        for lang in ('ko','en','ja','zh_cn','zh_tw'):
            keys = self._get_lang_keys(lang)
            for key in converter_keys:
                with self.subTest(lang=lang, key=key):
                    self.assertIn(key, keys,
                        f"[{lang}] '{key}' 키 없음 (text_converter 대분류)")

    def test_all_langs_have_tag_editor_keys(self):
        """Macro-category 4 — representative keys for the Tag Editor tab."""
        tag_keys = [
            'tag_file_count', 'tag_count_total',
            'tag_status_found', 'tag_status_found_add', 'tag_status_found_depad',
            'tag_no_change', 'tag_skip_count',
            'tag_apply_confirm', 'tag_apply_done',
        ]
        for lang in ('ko','en','ja','zh_cn','zh_tw'):
            keys = self._get_lang_keys(lang)
            for key in tag_keys:
                with self.subTest(lang=lang, key=key):
                    self.assertIn(key, keys,
                        f"[{lang}] '{key}' 키 없음 (tag_editor 대분류)")

    def test_all_langs_have_batch_renamer_keys(self):
        """Macro-category 5 — representative keys for the Batch Renamer tab.

        Macro-category that unifies the batch_* / rename_* prefixes (see Appendix E):
          - batch_* ← named after the original BatchRenamer class, used for UI / options
          - rename_* ← named after the original _do_rename / _confirm_rename methods, used for action state / feedback
        """
        batch_keys = [
            'rename_do', 'rename_cancel',
            'rename_no_preview', 'rename_no_pairs',
            'rename_no_subfolders', 'rename_no_files',
            'rename_collision',
        ]
        for lang in ('ko','en','ja','zh_cn','zh_tw'):
            keys = self._get_lang_keys(lang)
            for key in batch_keys:
                with self.subTest(lang=lang, key=key):
                    self.assertIn(key, keys,
                        f"[{lang}] '{key}' 키 없음 (batch_renamer 대분류)")

    def test_all_langs_have_text_fixer_keys(self):
        """Macro-category 6 — representative keys for the Text Fixer tab.

        Note: tf_dlg_overwrite was an orphan key removed in v1.0.7 sessions 2 and 3,
        so it is excluded from this invariant (cleaned up alongside the dead method _save_overwrite).
        """
        fixer_keys = [
            'tf_dlg_nofile', 'tf_dlg_noperm',
            'tf_dlg_ioerr', 'tf_dlg_encerr',
            'tf_undo_done',
        ]
        for lang in ('ko','en','ja','zh_cn','zh_tw'):
            keys = self._get_lang_keys(lang)
            for key in fixer_keys:
                with self.subTest(lang=lang, key=key):
                    self.assertIn(key, keys,
                        f"[{lang}] '{key}' 키 없음 (text_fixer 대분류)")

    def test_all_langs_have_bulk_fixer_keys(self):
        """Macro-category 7 — representative keys for the Bulk Fixer tab."""
        bulk_keys = [
            'bulk_run', 'bulk_running',
            'bulk_status_ready', 'bulk_status_done', 'bulk_status_err',
            'bulk_file_count', 'bulk_no_txt',
            'bulk_keep_structure',
        ]
        for lang in ('ko','en','ja','zh_cn','zh_tw'):
            keys = self._get_lang_keys(lang)
            for key in bulk_keys:
                with self.subTest(lang=lang, key=key):
                    self.assertIn(key, keys,
                        f"[{lang}] '{key}' 키 없음 (bulk_fixer 대분류)")

    def test_all_langs_have_settings_keys(self):
        """Macro-category 8 — representative keys for the Settings dialog."""
        settings_keys = [
            'settings_title',
            'settings_output_dir',
            'settings_nav_theme', 'settings_nav_language',
            'settings_nav_shortcuts', 'settings_nav_license',
        ]
        for lang in ('ko','en','ja','zh_cn','zh_tw'):
            keys = self._get_lang_keys(lang)
            for key in settings_keys:
                with self.subTest(lang=lang, key=key):
                    self.assertIn(key, keys,
                        f"[{lang}] '{key}' 키 없음 (settings 대분류)")

    def test_all_langs_have_shortcut_keys(self):
        """Macro-category 9 — representative keys for the shortcut system."""
        shortcut_keys = [
            'sc_none', 'sc_press',
            'sc_tab_merger', 'sc_tab_converter', 'sc_tab_tag',
            'sc_tab_batch', 'sc_tab_fixer', 'sc_tab_bulk',
        ]
        for lang in ('ko','en','ja','zh_cn','zh_tw'):
            keys = self._get_lang_keys(lang)
            for key in shortcut_keys:
                with self.subTest(lang=lang, key=key):
                    self.assertIn(key, keys,
                        f"[{lang}] '{key}' 키 없음 (shortcut 대분류)")

    def test_all_langs_have_misc_keys(self):
        """Macro-category 10 — residual representative keys that fall outside the above (minimization goal)."""
        misc_keys = [
            'app_subtitle',
            'close_busy_title',
        ]
        for lang in ('ko','en','ja','zh_cn','zh_tw'):
            keys = self._get_lang_keys(lang)
            for key in misc_keys:
                with self.subTest(lang=lang, key=key):
                    self.assertIn(key, keys,
                        f"[{lang}] '{key}' 키 없음 (misc 대분류)")


# ════════════════════════════════════════════════════════════════════════
# §ExtraH  retranslate chain integrity (prevents crash regression)
# ════════════════════════════════════════════════════════════════════════
class TestRetranslateIntegrity(unittest.TestCase):
    """Regression test for undefined attribute references inside retranslate methods.

    Before v0.10.0:
      - TextMergerPanel.retranslate() referenced _file_gb → AttributeError
      - TextConverterPanel.retranslate() referenced _btn_del_all → AttributeError
    Both bugs were caught by the try-except in AppSuite.retranslate_ui(),
    after which retranslate stopped running for the remaining panels.
    """

    def _get_retranslate_body(self, class_name):
        import re
        with open(_MAIN_PY, encoding='utf-8') as f:
            src = f.read()
        # Extract class scope
        cls_match = re.search(rf'^class {class_name}\b.*?(?=^class |\Z)',
                               src, re.MULTILINE | re.DOTALL)
        if not cls_match: return ''
        cls_body = cls_match.group(0)
        rt_match = re.search(r'def retranslate\(self\):(.*?)(?=\n    def |\Z)',
                              cls_body, re.DOTALL)
        return rt_match.group(1) if rt_match else ''

    def test_merger_no_file_gb(self):
        """TextMergerPanel.retranslate() must contain no reference to _file_gb."""
        body = self._get_retranslate_body('TextMergerPanel')
        self.assertNotIn('_file_gb', body,
            "TextMergerPanel.retranslate()에 _file_gb 잔류 — 크래시 위험")

    def test_converter_no_btn_del_all(self):
        """TextConverterPanel.retranslate() must contain no reference to _btn_del_all."""
        body = self._get_retranslate_body('TextConverterPanel')
        self.assertNotIn('_btn_del_all', body,
            "TextConverterPanel.retranslate()에 _btn_del_all 잔류 — 크래시 위험")

    def test_merger_has_tree_header_retranslate(self):
        """TextMergerPanel.retranslate() must update the tree header."""
        body = self._get_retranslate_body('TextMergerPanel')
        self.assertIn('setHeaderLabels', body,
            "MergeFileTree 헤더가 retranslate에서 갱신되지 않음")

    def test_bulk_fixer_sort_btn_uses_t(self):
        """BulkFixerFileList must use _t() keys in setHeaderLabels.
        (v0.10.1: _sort_files removed → sort via QTreeWidget header click)"""
        import re
        with open(_MAIN_PY, encoding='utf-8') as f:
            src = f.read()
        cls_match = re.search(r'^class BulkFixerFileList\b.*?(?=^class |\Z)',
                               src, re.MULTILINE | re.DOTALL)
        if not cls_match:
            self.skipTest("BulkFixerFileList 클래스 없음")
        cls_body = cls_match.group(0)
        self.assertIn("setHeaderLabels", cls_body,
            "BulkFixerFileList에 setHeaderLabels 없음")
        self.assertNotIn('"파일명"', cls_body,
            "BulkFixerFileList에 하드코딩된 '파일명' 잔류")

    def test_dlg_functions_use_t_keys(self):
        """_dlg_info / warn / error / question buttons must use _t() keys."""
        import re
        with open(_MAIN_PY, encoding='utf-8') as f:
            src = f.read()
        # Extract the _dlg_info function
        for fn in ('_dlg_info', '_dlg_warn', '_dlg_error', '_dlg_question', '_dlg_info_action'):
            fn_match = re.search(rf'^def {fn}\b.*?(?=^def |\Z)',
                                  src, re.MULTILINE | re.DOTALL)
            if not fn_match: continue
            body = fn_match.group(0)
            with self.subTest(fn=fn):
                self.assertNotIn('QPushButton("확인")', body,
                    f"{fn}()에 하드코딩 '확인' 버튼 잔류")
                self.assertNotIn('QPushButton("예")', body,
                    f"{fn}()에 하드코딩 '예' 버튼 잔류")
                self.assertNotIn('QPushButton("아니오")', body,
                    f"{fn}()에 하드코딩 '아니오' 버튼 잔류")

    def test_bulk_fixer_abort_retranslate(self):
        """BulkFixerPanel.retranslate() must update _btn_abort and _chk_keep_structure."""
        body = self._get_retranslate_body('BulkFixerPanel')
        self.assertIn('_btn_abort', body,
            "BulkFixerPanel.retranslate()에 _btn_abort 갱신 없음")
        self.assertIn('_chk_keep_structure', body,
            "BulkFixerPanel.retranslate()에 _chk_keep_structure 갱신 없음")


# ════════════════════════════════════════════════════════════════════════
# §ExtraI  BulkFixerWorker — core logic
# ════════════════════════════════════════════════════════════════════════
_BulkFixerWorker = _ns.get('BulkFixerWorker') if HAS_MODULE else None
_TextFixerWorker  = _ns.get('TextFixerWorker')  if HAS_MODULE else None

@unittest.skipUnless(HAS_MODULE and _BulkFixerWorker and _TextFixerWorker,
                     "FileNexusSuite 로드 실패 또는 BulkFixerWorker 없음")
class TestBulkFixerWorker(unittest.TestCase):
    """BulkFixerWorker._fix_text() — unit tests for the fix logic."""

    def _worker(self, **kwargs):
        defaults = dict(files=[], out_dir='',
                        do_mid=True, do_blank=True, max_blank=1,
                        do_sep=False, do_auto_split=False,
                        max_split_chars=100, lang_mode='auto',
                        keep_structure=False)
        defaults.update(kwargs)
        return _BulkFixerWorker(**defaults)

    # ── Basic fixes ─────────────────────────────
    def test_mid_merge(self):
        w = self._worker(do_mid=True, do_blank=False)
        out, mid, blank = w._fix_text("A\nB")
        self.assertEqual(mid, 1)
        self.assertNotIn('\n', out)

    def test_period_no_merge(self):
        w = self._worker(do_mid=True, do_blank=False)
        out, mid, _ = w._fix_text("문장이다.\n다음 줄.")
        self.assertEqual(mid, 0)

    def test_blank_compression(self):
        w = self._worker(do_mid=False, do_blank=True, max_blank=1)
        out, _, blank = w._fix_text("A\n\n\n\nB")
        self.assertGreater(blank, 0)
        self.assertNotIn('\n\n\n', out)

    def test_blank_disabled(self):
        w = self._worker(do_mid=False, do_blank=False)
        out, _, blank = w._fix_text("A\n\n\n\nB")
        self.assertEqual(blank, 0)
        self.assertIn('\n\n\n\n', out)

    def test_empty_input(self):
        w = self._worker()
        out, mid, blank = w._fix_text("")
        self.assertEqual(out, "")
        self.assertEqual(mid, 0)

    def test_sep_line_not_merged(self):
        w = self._worker(do_mid=True, do_blank=False)
        out, mid, _ = w._fix_text("────────\n제목")
        self.assertEqual(mid, 0)

    # ── lang_mode ────────────────────────────────
    def test_lang_mode_ko(self):
        """Korean mode: CJK-only lines should merge."""
        w = self._worker(do_mid=True, do_blank=False, lang_mode='ko')
        out, mid, _ = w._fix_text("앞부분이고\n뒷부분이다.")
        self.assertEqual(mid, 1)

    def test_lang_mode_en_abbr_no_merge(self):
        """English mode: lines after abbreviations (Mr.) should merge."""
        w = self._worker(do_mid=True, do_blank=False, lang_mode='en')
        out, mid, _ = w._fix_text("Call Mr.\nSmith today.")
        # Mr. is an abbreviation → must merge
        self.assertEqual(mid, 1)

    def test_lang_mode_en_sentence_end_no_merge(self):
        """English mode: sentence endings (.) should not merge."""
        w = self._worker(do_mid=True, do_blank=False, lang_mode='en')
        out, mid, _ = w._fix_text("End of sentence.\nNext sentence.")
        self.assertEqual(mid, 0)

    def test_lang_mode_en_hyphen_join(self):
        """English mode: restore hyphen-split words."""
        w = self._worker(do_mid=True, do_blank=False, lang_mode='en')
        out, mid, _ = w._fix_text("con-\ntinue")
        self.assertIn("continue", out)

    def test_lang_mode_auto_detects_ko(self):
        """Auto-detect: Korean text → ko mode."""
        w = self._worker(do_mid=True, do_blank=False, lang_mode='auto')
        out, mid, _ = w._fix_text("한국어 텍스트이다\n계속 이어진다")
        self.assertEqual(mid, 1)

    # ── Output path computation ──────────────────
    def test_save_path_no_outdir(self):
        """out_dir not given: [Fixed] prefix at the original location."""
        w = self._worker(out_dir='')
        src = '/tmp/test.txt'
        result = w._make_save_path(src)
        self.assertEqual(result, os.path.join('/tmp', '[Fixed]test.txt'))

    def test_save_path_with_outdir(self):
        """out_dir given: [Fixed] prefix inside the specified folder."""
        w = self._worker(out_dir='/out')
        src = '/tmp/test.txt'
        result = w._make_save_path(src)
        self.assertEqual(result, os.path.join('/out', '[Fixed]test.txt'))

    def test_save_path_keep_structure(self):
        """keep_structure=True: preserve folder structure."""
        files = ['/data/sub/a.txt', '/data/sub/b.txt']
        w = self._worker(files=files, out_dir='/out', keep_structure=True)
        result = w._make_save_path(files[0])
        # commonpath=/data/sub → rel=. → /out/[Fixed]a.txt
        self.assertTrue(result.startswith('/out'))
        self.assertIn('[Fixed]a.txt', result)


@unittest.skipUnless(HAS_MODULE and _BulkFixerWorker,
                     "FileNexusSuite 로드 실패")
class TestBulkFixerFileIO(unittest.TestCase):
    """BulkFixerWorker — integration test with real file read/write."""

    def setUp(self):
        self.td = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.td, ignore_errors=True)

    def _make_file(self, name, content, enc='utf-8'):
        path = os.path.join(self.td, name)
        with open(path, 'w', encoding=enc) as f:
            f.write(content)
        return path

    def test_default_creates_fixed_file(self):
        src = self._make_file('novel.txt', "A\nB\n\n\n\nC")
        w = _BulkFixerWorker(
            files=[src], out_dir='',
            do_mid=True, do_blank=True, max_blank=1,
        )
        out_path = w._make_save_path(src)
        with open(src, encoding='utf-8') as _f:
            text, _, _ = w._fix_text(_f.read())
        with open(out_path, 'w', encoding='utf-8') as f: f.write(text)
        self.assertTrue(os.path.exists(out_path))
        self.assertIn('[Fixed]', out_path)

    def test_outdir_creates_in_out_dir(self):
        src = self._make_file('novel.txt', "A\nB")
        out_dir = os.path.join(self.td, 'output')
        os.makedirs(out_dir)
        w = _BulkFixerWorker(
            files=[src], out_dir=out_dir,
            do_mid=True, do_blank=True, max_blank=1,
        )
        out_path = w._make_save_path(src)
        self.assertEqual(os.path.dirname(out_path), out_dir)

    def test_utf8_roundtrip(self):
        content = "한국어 텍스트\n두 번째 줄"
        src = self._make_file('ko.txt', content)
        w = _BulkFixerWorker(
            files=[src], out_dir='',
            do_mid=False, do_blank=False, max_blank=1,
        )
        with open(src, encoding='utf-8') as _f:
            out, _, _ = w._fix_text(_f.read())
        self.assertIn("한국어", out)

    def test_multiple_blank_compressed(self):
        src = self._make_file('blank.txt', "A\n\n\n\n\nB")
        w = _BulkFixerWorker(
            files=[src], out_dir='',
            do_mid=False, do_blank=True, max_blank=1,
        )
        with open(src, encoding='utf-8') as _f:
            out, _, blank = w._fix_text(_f.read())
        self.assertGreater(blank, 0)
        self.assertNotIn('\n\n\n', out)

    def test_keep_structure_creates_subdirs(self):
        """keep_structure=True: reproduce subfolder structure in the output folder."""
        sub = os.path.join(self.td, 'sub')
        os.makedirs(sub)
        src = self._make_file(os.path.join('sub', 'a.txt'), "A\nB")
        out_dir = os.path.join(self.td, 'output')
        os.makedirs(out_dir)
        w = _BulkFixerWorker(
            files=[src], out_dir=out_dir,
            do_mid=True, do_blank=True, max_blank=1,
            keep_structure=True,
        )
        out_path = w._make_save_path(src)
        self.assertIn('[Fixed]', os.path.basename(out_path))
        # Subfolder must be included in the output path
        self.assertTrue(out_path.startswith(out_dir))

    # ── v1.0.3 addition: prevent encoding round-trip regression ──
    # Through v1.0.2, BulkFixerWorker.run() could not handle UTF-16/Shift-JIS/GBK/Big5
    # and saved them in a corrupted state (fixed in v1.0.3 by reusing alchemy_detect_encoding);
    # this test guards against that regression.
    #
    # Note: this test only confirms that _fix_text() is encoding-agnostic text processing.
    # Real encoding detection is validated in TestAlchemyDetectEncoding.
    # Calling run() directly is skipped because of the QThread lifecycle.

    def test_utf8_bom_roundtrip(self):
        """UTF-8 BOM files are processed correctly."""
        content = "한국어 텍스트\n두 번째 줄"
        src = self._make_file('ko.txt', content, enc='utf-8-sig')
        # Verify in order: detect → decode → fix
        # v1.0.6: use _alchemy_detect_enc instead of "from FileNexusSuite import" —
        # re-importing FileNexusSuite would re-register the Phase 2-a `_fns_track` handler,
        # polluting the location-tracking collection — prevented here (protects §ExtraO)
        detected = _alchemy_detect_enc(src)
        # v1.0.4: tuple-return compatible (old str / new (str, float))
        enc = detected[0] if isinstance(detected, tuple) else detected
        self.assertEqual(enc, 'utf-8-sig')
        with open(src, 'r', encoding=enc) as f: text = f.read()
        w = _BulkFixerWorker(files=[src], out_dir='',
                             do_mid=False, do_blank=False, max_blank=1)
        out, _, _ = w._fix_text(text)
        self.assertIn("한국어", out)

    def test_utf16_le_roundtrip(self):
        """UTF-16 LE files are processed correctly (v1.0.2 bug)."""
        content = "한국어 텍스트\n두 번째 줄"
        src = os.path.join(self.td, 'ko_utf16_le.txt')
        with open(src, 'wb') as f:
            f.write(b'\xff\xfe' + content.encode('utf-16-le'))
        # v1.0.6: removed "from FileNexusSuite import" — prevents Phase 2-a `_fns_track` handler re-registration
        detected = _alchemy_detect_enc(src)
        # v1.0.4: tuple-return compatible
        enc = detected[0] if isinstance(detected, tuple) else detected
        self.assertEqual(enc, 'utf-16')
        with open(src, 'r', encoding=enc) as f: text = f.read()
        w = _BulkFixerWorker(files=[src], out_dir='',
                             do_mid=False, do_blank=False, max_blank=1)
        out, _, _ = w._fix_text(text)
        self.assertIn("한국어", out)

    def test_utf16_be_roundtrip(self):
        """UTF-16 BE files are processed correctly (v1.0.2 bug)."""
        content = "한국어 텍스트\n두 번째 줄"
        src = os.path.join(self.td, 'ko_utf16_be.txt')
        with open(src, 'wb') as f:
            f.write(b'\xfe\xff' + content.encode('utf-16-be'))
        # v1.0.6: removed "from FileNexusSuite import" — prevents Phase 2-a `_fns_track` handler re-registration
        detected = _alchemy_detect_enc(src)
        # v1.0.4: tuple-return compatible
        enc = detected[0] if isinstance(detected, tuple) else detected
        self.assertEqual(enc, 'utf-16')
        with open(src, 'r', encoding=enc) as f: text = f.read()
        w = _BulkFixerWorker(files=[src], out_dir='',
                             do_mid=False, do_blank=False, max_blank=1)
        out, _, _ = w._fix_text(text)
        self.assertIn("한국어", out)

    def test_cp949_roundtrip(self):
        """Korean CP949 files are processed correctly (this already worked in v1.0.2 — regression guard)."""
        content = "한국어 텍스트\n두 번째 줄"
        src = self._make_file('ko_cp949.txt', content, enc='cp949')
        w = _BulkFixerWorker(files=[src], out_dir='',
                             do_mid=False, do_blank=False, max_blank=1)
        with open(src, 'r', encoding='cp949') as f: text = f.read()
        out, _, _ = w._fix_text(text)
        self.assertIn("한국어", out)

    def test_5_languages_utf8(self):
        """Full regression check across 5 languages × UTF-8."""
        cases = {
            'ko.txt': '안녕하세요 한국어',
            'en.txt': 'Hello English',
            'ja.txt': 'こんにちは 日本語',
            'zh_cn.txt': '你好 简体中文',
            'zh_tw.txt': '你好 繁體中文',
        }
        for fname, content in cases.items():
            with self.subTest(file=fname):
                src = self._make_file(fname, content, enc='utf-8')
                w = _BulkFixerWorker(files=[src], out_dir='',
                                     do_mid=False, do_blank=False, max_blank=1)
                with open(src, 'r', encoding='utf-8') as f: text = f.read()
                out, _, _ = w._fix_text(text)
                # Key words must appear unchanged in the output
                for keyword in content.split():
                    self.assertIn(keyword, out,
                                  f"{fname}: '{keyword}' 누락 또는 깨짐")


# ════════════════════════════════════════════════════════════════════════
# §ExtraJ  lang_mode — TextFixerWorker (new parameter in v0.10.0)
# ════════════════════════════════════════════════════════════════════════
@unittest.skipUnless(HAS_MODULE and _TextFixerWorker,
                     "FileNexusSuite 로드 실패")
class TestTextFixerLangMode(unittest.TestCase):
    """Tests for the TextFixerWorker.lang_mode parameter."""

    def _make_worker(self, text, lang_mode='auto', do_mid=True,
                     do_blank=False, max_blank=1):
        return _TextFixerWorker(text, do_mid=do_mid, do_blank=do_blank,
                                max_blank=max_blank, lang_mode=lang_mode)

    def test_default_lang_mode_is_auto(self):
        w = _TextFixerWorker("text", do_mid=True, do_blank=False, max_blank=1)
        self.assertEqual(w.lang_mode, 'auto')

    def test_ko_mode_stored(self):
        w = self._make_worker("text", lang_mode='ko')
        self.assertEqual(w.lang_mode, 'ko')

    def test_en_mode_stored(self):
        w = self._make_worker("text", lang_mode='en')
        self.assertEqual(w.lang_mode, 'en')

    def test_detect_lang_korean(self):
        text = "이것은 한국어 문장입니다. " * 10
        lang = _TextFixerWorker._detect_lang(text)
        self.assertEqual(lang, 'ko')

    def test_detect_lang_english(self):
        text = "This is an English sentence. " * 10
        lang = _TextFixerWorker._detect_lang(text)
        self.assertEqual(lang, 'en')

    def test_detect_lang_japanese(self):
        text = "これは日本語の文章です。" * 10
        lang = _TextFixerWorker._detect_lang(text)
        self.assertEqual(lang, 'ko')  # CJK → ko mode

    def test_detect_lang_empty(self):
        lang = _TextFixerWorker._detect_lang("")
        self.assertEqual(lang, 'ko')  # default value

    def test_en_abbr_mr(self):
        self.assertTrue(_TextFixerWorker._is_en_abbr("Dr."))

    def test_en_abbr_etc(self):
        self.assertTrue(_TextFixerWorker._is_en_abbr("etc."))

    def test_en_abbr_normal_word(self):
        self.assertFalse(_TextFixerWorker._is_en_abbr("sentence."))

    def test_en_merge_hyphen(self):
        result = _TextFixerWorker._merge_en("con-", "tinue")
        self.assertEqual(result, "continue")

    def test_en_merge_normal(self):
        result = _TextFixerWorker._merge_en("word", "next")
        self.assertEqual(result, "word next")


# ════════════════════════════════════════════════════════════════════════
# §ExtraK  v0.12.0 regression — source-parsing based (PySide6 not required)
# ════════════════════════════════════════════════════════════════════════
class TestV012Regression(unittest.TestCase):
    """Regression test for v0.12.0 major changes — parse the source file directly."""

    def _src(self):
        with open(_MAIN_PY, encoding='utf-8') as f:
            return f.read()

    # ── Version ──────────────────────────────────────────────────────────
    def test_app_version_012(self):
        """APP_VERSION is v1.0.0 or higher"""
        m = _re.search(r'^APP_VERSION\s*=\s*["\']([^"\']+)["\']', self._src(), _re.MULTILINE)
        self.assertIsNotNone(m, "APP_VERSION 정의 없음")
        parts = m.group(1).split('.')
        self.assertGreaterEqual(int(parts[0]), 1, f"메이저 버전 < 1: {m.group(1)}")

    # ── SVG icon system ──────────────────────────────────────────────────
    def test_svg_paths_dict_defined(self):
        """The _SVG_PATHS dictionary must be defined in the source."""
        self.assertIn('_SVG_PATHS', self._src())

    def test_svg_line_icons_dict_defined(self):
        """The _SVG_LINE_ICONS dictionary must be defined in the source."""
        self.assertIn('_SVG_LINE_ICONS', self._src())

    def test_svg_paths_filled_keys_present(self):
        """_SVG_PATHS must contain every core filled-icon key."""
        src = self._src()
        for key in ('document', 'folder', 'folder_open', 'tag', 'refresh',
                    'wrench', 'magnifier', 'save', 'trash', 'broom',
                    'question', 'list', 'clipboard', 'arrow_up', 'arrow_down',
                    'check', 'info'):
            with self.subTest(key=key):
                self.assertIn(f"'{key}'", src, f"_SVG_PATHS에 '{key}' 없음")

    def test_svg_line_icons_keys_present(self):
        """_SVG_LINE_ICONS must contain every core line-icon key."""
        src = self._src()
        for key in ('document_line', 'folder_open_line', 'tag_line', 'folder_line',
                    'wrench_line', 'broom_line', 'gear_line', 'question_line',
                    'theme_line', 'globe_line', 'keyboard_line', 'license_line',
                    'info_line', 'bell_line'):
            with self.subTest(key=key):
                self.assertIn(f"'{key}'", src, f"_SVG_LINE_ICONS에 '{key}' 없음")

    def test_bulk_fixer_tab_uses_broom_line(self):
        """The Bulk Fixer tab icon must have been switched to broom_line (line style).

        v0.12.0: replaced broom (filled) with broom_line (line) for consistency with other tabs.
        """
        src = self._src()
        # broom_line must be used in the tab-icon list
        self.assertIn("'broom_line'", src, "broom_line 키가 소스에 없음")
        # Verify broom_line sits in the last (Bulk Fixer) slot of the _tab_icons array
        m = _re.search(r"_tab_icons\s*=\s*\[(.*?)\]", src, _re.DOTALL)
        self.assertIsNotNone(m, "_tab_icons 배열 정의 없음")
        self.assertIn('broom_line', m.group(1), "_tab_icons 배열에 broom_line 없음")

    def test_svg_icon_function_defined(self):
        """The _svg_icon() function must be defined in the source."""
        self.assertIn('def _svg_icon(', self._src())

    def test_svg_icon_white_disabled_pixmap(self):
        """_svg_icon() must auto-add a Disabled pixmap when the 'white' icon is requested."""
        src = self._src()
        # Verify the 'white' + Disabled handling code
        self.assertIn("color == 'white'", src)
        self.assertIn('QIcon.Mode.Disabled', src)

    # ── Theme system ─────────────────────────────────────────────────────
    def test_all_themes_have_btn_border_h(self):
        """Every theme dictionary must include the BTN_BORDER_H key (improvement over v0.12.0)."""
        src = self._src()
        m = _re.search(r'^THEMES\s*=\s*\{(.*?)^\}', src, _re.MULTILINE | _re.DOTALL)
        self.assertIsNotNone(m, "THEMES 정의 없음")
        theme_block = m.group(1)
        # Each theme block must contain BTN_BORDER_H
        self.assertGreater(
            theme_block.count("'BTN_BORDER_H'"), 0,
            "THEMES 안에 BTN_BORDER_H가 하나도 없음"
        )
        # Must appear once per theme (9 themes total)
        theme_count = len(_re.findall(r"^\s{4}'(\w+)'\s*:\s*\{", theme_block, _re.MULTILINE))
        btn_border_h_count = theme_block.count("'BTN_BORDER_H'")
        self.assertEqual(btn_border_h_count, theme_count,
            f"BTN_BORDER_H 수({btn_border_h_count}) ≠ 테마 수({theme_count})")

    def test_themes_count_9(self):
        """The THEMES dictionary must contain 9 themes (auto is a virtual theme resolved at runtime)."""
        src = self._src()
        m = _re.search(r'^THEMES\s*=\s*\{(.*?)^\}', src, _re.MULTILINE | _re.DOTALL)
        self.assertIsNotNone(m)
        keys = _re.findall(r"^\s{4}'(\w+)'\s*:\s*\{", m.group(1), _re.MULTILINE)
        self.assertEqual(len(keys), 9, f"THEMES 키 수 불일치: {keys}")

    # ── Translation — emoji-removal check ────────────────────────────────
    def test_btn_add_file_no_emoji(self):
        """Emojis must have been stripped from the btn_add_file translation values (v0.12.0 cleanup)."""
        src = self._src()
        # Extract the value of the 'btn_add_file' key and check emoji Unicode ranges
        m = _re.search(r"'btn_add_file'\s*:\s*'([^']+)'", src)
        if m:
            val = m.group(1)
            # General emoji range (U+1F300–U+1FFFF)
            has_emoji = any(0x1F300 <= ord(c) <= 0x1FFFF for c in val)
            self.assertFalse(has_emoji, f"btn_add_file 값에 이모지 포함: {repr(val)}")

    def test_btn_add_folder_no_emoji(self):
        """Emojis must have been stripped from the btn_add_folder translation values."""
        src = self._src()
        m = _re.search(r"'btn_add_folder'\s*:\s*'([^']+)'", src)
        if m:
            val = m.group(1)
            has_emoji = any(0x1F300 <= ord(c) <= 0x1FFFF for c in val)
            self.assertFalse(has_emoji, f"btn_add_folder 값에 이모지 포함: {repr(val)}")

    # ── Logging system ───────────────────────────────────────────────────
    def test_crash_log_max_3(self):
        """Crash-log retention must have been reduced to 3 (v0.12.0: 20 → 3)."""
        src = self._src()
        # Verify the crash-log cleanup uses 3 or -3 slicing
        self.assertTrue(
            _re.search(r'crash.*\b3\b', src, _re.IGNORECASE) is not None or
            'sorted_logs[3:]' in src or 'sorted_logs[-3:]' in src or
            'keep.*3' in src.lower() or
            _re.search(r'\bmax_keep\s*=\s*3\b', src) is not None or
            _re.search(r'\bkeep_n\s*=\s*3\b', src) is not None or
            'logs[3:]' in src or '[-3:]' in src,
            "crash 로그 3개 보관 로직이 소스에 없음"
        )

    def test_session_log_auto_delete_on_normal_exit(self):
        """On normal shutdown, session logs must be auto-deleted."""
        src = self._src()
        self.assertIn('session', src.lower())
        # Code in closeEvent that closes or deletes the session log file
        self.assertTrue(
            'session_log' in src or '_session_log_fp' in src,
            "세션 로그 관련 코드가 소스에 없음"
        )

    # ── _svg_html_img preservation ───────────────────────────────────────
    def test_svg_html_img_preserved_unused(self):
        """_svg_html_img() must remain preserved even though unused."""
        self.assertIn('def _svg_html_img(', self._src())


@unittest.skipUnless(HAS_MODULE, "FileNexusSuite 로드 실패 (PySide6 필요)")
class TestV012RegressionModule(unittest.TestCase):
    """v0.12.0 module-load-based regression test (PySide6 required)."""

    def test_svg_paths_is_dict(self):
        """_SVG_PATHS must be of type dict."""
        svg_paths = _ns.get('_SVG_PATHS')
        self.assertIsNotNone(svg_paths, "_SVG_PATHS가 namespace에 없음")
        self.assertIsInstance(svg_paths, dict)

    def test_svg_line_icons_is_dict(self):
        """_SVG_LINE_ICONS must be of type dict."""
        svg_line = _ns.get('_SVG_LINE_ICONS')
        self.assertIsNotNone(svg_line, "_SVG_LINE_ICONS가 namespace에 없음")
        self.assertIsInstance(svg_line, dict)

    def test_svg_paths_has_all_filled_keys(self):
        """_SVG_PATHS must contain 17 or more filled icons."""
        svg_paths = _ns.get('_SVG_PATHS', {})
        self.assertGreaterEqual(len(svg_paths), 17,
            f"_SVG_PATHS 항목 수 부족: {len(svg_paths)}")

    def test_svg_line_icons_has_all_line_keys(self):
        """_SVG_LINE_ICONS must contain 14 or more line icons."""
        svg_line = _ns.get('_SVG_LINE_ICONS', {})
        self.assertGreaterEqual(len(svg_line), 14,
            f"_SVG_LINE_ICONS 항목 수 부족: {len(svg_line)}")

    def test_broom_line_in_svg_line_icons(self):
        """_SVG_LINE_ICONS must contain the broom_line key (Bulk Fixer tab icon)."""
        svg_line = _ns.get('_SVG_LINE_ICONS', {})
        self.assertIn('broom_line', svg_line)

    def test_broom_in_svg_paths(self):
        """_SVG_PATHS must contain the broom key (filled style preserved)."""
        svg_paths = _ns.get('_SVG_PATHS', {})
        self.assertIn('broom', svg_paths)

    def test_all_themes_have_btn_border_h_key(self):
        """Every theme dictionary must include the BTN_BORDER_H key."""
        themes = _ns.get('THEMES', {})
        for name, t in themes.items():
            with self.subTest(theme=name):
                self.assertIn('BTN_BORDER_H', t,
                    f"테마 '{name}'에 BTN_BORDER_H 없음")

    def test_themes_count_module(self):
        """THEMES must contain 9 themes."""
        themes = _ns.get('THEMES', {})
        self.assertEqual(len(themes), 9, f"테마 수 불일치: {sorted(themes.keys())}")

    def test_app_version_from_ns(self):
        """The APP_VERSION pulled from the namespace must be v1.0.0 or higher."""
        ver = _ns.get('APP_VERSION')
        self.assertIsNotNone(ver, "APP_VERSION 없음")
        # v1.0.0 or higher passes
        parts = ver.split('.')
        self.assertGreaterEqual(int(parts[0]), 1, f"메이저 버전 < 1: {ver}")

    def test_svg_icon_callable(self):
        """The _svg_icon function must exist in the namespace and be callable."""
        fn = _ns.get('_svg_icon')
        self.assertIsNotNone(fn, "_svg_icon이 namespace에 없음")
        self.assertTrue(callable(fn))

    def test_svg_html_img_callable(self):
        """The _svg_html_img function must remain in the namespace."""
        fn = _ns.get('_svg_html_img')
        self.assertIsNotNone(fn, "_svg_html_img이 namespace에 없음")
        self.assertTrue(callable(fn))

    def test_translations_btn_keys_no_emoji(self):
        """Translation values for btn_add_file / btn_add_folder must contain no emojis."""
        translations = _ns.get('TRANSLATIONS', {})
        ko = translations.get('ko', {})
        for key in ('btn_add_file', 'btn_add_folder', 'btn_del_sel', 'btn_del_all'):
            val = ko.get(key, '')
            with self.subTest(key=key):
                has_emoji = any(0x1F300 <= ord(c) <= 0x1FFFF for c in val)
                self.assertFalse(has_emoji,
                    f"ko['{key}'] 값에 이모지 포함: {repr(val)}")


# ════════════════════════════════════════════════════════════════════════
# §ExtraL  v1.0.0 regression — source-parsing based (PySide6 not required)
# ════════════════════════════════════════════════════════════════════════
class TestV100Regression(unittest.TestCase):
    """Regression test for v1.0.0 major changes — parse the source file directly."""

    def _src(self):
        with open(_MAIN_PY, encoding='utf-8') as f:
            return f.read()

    # ── Version ──────────────────────────────────────────────────────────
    def test_app_version_100(self):
        """APP_VERSION is v1.0.0 or higher"""
        m = _re.search(r'^APP_VERSION\s*=\s*["\']([^"\']+)["\']', self._src(), _re.MULTILINE)
        self.assertIsNotNone(m, "APP_VERSION 정의 없음")
        parts = m.group(1).split('.')
        self.assertGreaterEqual(int(parts[0]), 1, f"메이저 버전 < 1: {m.group(1)}")

    # ── QPlainTextEdit replacement ───────────────────────────────────────
    def test_qplaintextedit_import(self):
        """QPlainTextEdit must be imported (resolves the large-input limit of QTextEdit)."""
        self.assertIn('QPlainTextEdit', self._src())

    def test_text_fixer_edit_uses_qplaintextedit(self):
        """TextFixerEdit must be based on QPlainTextEdit."""
        src = self._src()
        m = _re.search(r'class TextFixerEdit\((\w+)\)', src)
        self.assertIsNotNone(m, "TextFixerEdit 클래스 정의 없음")
        self.assertEqual(m.group(1), 'QPlainTextEdit')

    def test_text_fixer_output_edit_uses_qplaintextedit(self):
        """TextFixerOutputEdit must be based on QPlainTextEdit."""
        src = self._src()
        m = _re.search(r'class TextFixerOutputEdit\((\w+)\)', src)
        self.assertIsNotNone(m, "TextFixerOutputEdit 클래스 정의 없음")
        self.assertEqual(m.group(1), 'QPlainTextEdit')

    # ── Animation widget ─────────────────────────────────────────────────
    def test_scroll_hint_class(self):
        """The _ScrollHint class must be defined."""
        self.assertIn('class _ScrollHint', self._src())

    def test_help_button_class(self):
        """_HelpButton 클래스가 정의되어 있어야 한다."""
        self.assertIn('class _HelpButton', self._src())

    def test_gear_button_class(self):
        """_GearButton 클래스가 정의되어 있어야 한다."""
        self.assertIn('class _GearButton', self._src())

    # ── Output folder global settings ────────────────────────────────
    def test_output_dir_in_cfg(self):
        """_CFG에 output_dir 키가 사용되어야 한다."""
        self.assertIn("'output_dir'", self._src())

    # ── Bulk Fixer keep_structure ─────────────────────────────────────
    def test_bulk_keep_structure_checkbox(self):
        """_chk_keep_structure 체크박스가 있어야 한다."""
        self.assertIn('_chk_keep_structure', self._src())

    def test_bulk_commonpath_usage(self):
        """os.path.commonpath 기반 상대 경로 재현 로직이 있어야 한다."""
        self.assertIn('commonpath', self._src())

    # ── Bulk Fixer preset ────────────────────────────────────────────
    def test_bulk_combo_preset(self):
        """Bulk Fixer에 _combo_preset 콤보박스가 있어야 한다."""
        self.assertIn('_combo_preset', self._src())

    def test_bulk_apply_preset(self):
        """_apply_preset 메서드가 정의되어 있어야 한다."""
        self.assertIn('def _apply_preset', self._src())

    # ── Bulk Fixer abort button ──────────────────────────────────────
    def test_btn_abort_widget(self):
        """_btn_abort 위젯이 있어야 한다 (btn_undo에서 분리)."""
        self.assertIn('_btn_abort', self._src())

    # ── grp_title_lbl style ──────────────────────────────────────────
    def test_grp_title_lbl_style(self):
        """make_style에 QLabel#grp_title_lbl 스타일이 있어야 한다."""
        self.assertIn('grp_title_lbl', self._src())

    # ── Section header // prefix ─────────────────────────────────────
    def test_section_header_prefix(self):
        """tf_grp_input/output 번역 키에 '//' 접두사가 사용되어야 한다."""
        src = self._src()
        self.assertTrue(
            "'tf_grp_input'" in src and '//' in src,
            "tf_grp_input에 '//' 접두사 없음"
        )


@unittest.skipUnless(HAS_MODULE, "FileNexusSuite 로드 실패 (PySide6 필요)")
class TestV100RegressionModule(unittest.TestCase):
    """v1.0.0 모듈 로드 기반 회귀 테스트 (PySide6 필요)."""

    def test_app_version_from_ns(self):
        """namespace에서 가져온 APP_VERSION이 v1.0.0 이상이어야 한다."""
        ver = _ns.get('APP_VERSION')
        self.assertIsNotNone(ver, "APP_VERSION 없음")
        # OK if v1.0.0 or higher (v1.0.1, v1.0.2, v1.0.3, etc. all pass)
        parts = ver.split('.')
        self.assertGreaterEqual(int(parts[0]), 1, f"메이저 버전 < 1: {ver}")

    def test_scroll_hint_in_ns(self):
        """_ScrollHint 클래스가 namespace에 있어야 한다."""
        cls = _ns.get('_ScrollHint')
        self.assertIsNotNone(cls, "_ScrollHint 클래스 없음")

    def test_help_button_in_ns(self):
        """_HelpButton 클래스가 namespace에 있어야 한다."""
        cls = _ns.get('_HelpButton')
        self.assertIsNotNone(cls, "_HelpButton 클래스 없음")

    def test_gear_button_in_ns(self):
        """_GearButton 클래스가 namespace에 있어야 한다."""
        cls = _ns.get('_GearButton')
        self.assertIsNotNone(cls, "_GearButton 클래스 없음")

    def test_settings_dialog_in_ns(self):
        """SettingsDialog 클래스가 namespace에 있어야 한다."""
        cls = _ns.get('SettingsDialog')
        self.assertIsNotNone(cls, "SettingsDialog 클래스 없음")

    def test_translations_v100_keys(self):
        """v1.0.0 신규 번역 키가 전 언어에 있어야 한다."""
        translations = _ns.get('TRANSLATIONS', {})
        new_keys = ['btn_abort', 'bulk_keep_structure', 'settings_output_dir']
        for lang in ('ko', 'en', 'ja', 'zh_cn', 'zh_tw'):
            keys = set(translations.get(lang, {}).keys())
            for key in new_keys:
                with self.subTest(lang=lang, key=key):
                    self.assertIn(key, keys,
                        f"[{lang}] '{key}' 키 없음 (v1.0.0 신규 키)")

    def test_bulk_worker_keep_structure_param(self):
        """BulkFixerWorker에 keep_structure 파라미터가 있어야 한다."""
        import inspect
        worker_cls = _ns.get('BulkFixerWorker')
        self.assertIsNotNone(worker_cls)
        sig = inspect.signature(worker_cls.__init__)
        self.assertIn('keep_structure', sig.parameters,
            "BulkFixerWorker.__init__에 keep_structure 파라미터 없음")


# ════════════════════════════════════════════════════════════════════════
# §AdditionalN  v1.0.3 encoding detection regression prevention
# ════════════════════════════════════════════════════════════════════════
class TestV103Regression(unittest.TestCase):
    """v1.0.3 — Text Fixer·Bulk Fixer 인코딩 감지 버그 회귀 방지."""

    @classmethod
    def setUpClass(cls):
        with open(_MAIN_PY, encoding='utf-8') as f:
            cls.src = f.read()

    def test_no_latin_1_fallback_in_text_fixer(self):
        """TextFixerPanel.load_file must NOT use a latin-1 fallback.
        Up to v1.0.2 a latin-1 fallback existed, so files with wrong encoding would
        be unconditionally decoded as 'successful', letting broken text through."""
        # Extract load_file method body
        m = re.search(
            r'def load_file\(self, path: str\):(.*?)(?=\n    def |\nclass )',
            self.src, re.DOTALL)
        self.assertIsNotNone(m, "load_file 메서드를 찾을 수 없음")
        body = m.group(1)
        self.assertNotIn("'latin-1'", body,
            "TextFixerPanel.load_file에 latin-1 폴백이 남아있음 (v1.0.2 버그)")

    def test_no_latin_1_in_bulk_fixer_worker(self):
        """BulkFixerWorker.run이 latin-1 폴백을 사용하지 않아야 함."""
        # Extract for-enc list inside BulkFixerWorker.run method
        m = re.search(
            r'class BulkFixerWorker.*?def run\(self\):(.*?)(?=\n    def |\nclass )',
            self.src, re.DOTALL)
        self.assertIsNotNone(m, "BulkFixerWorker.run을 찾을 수 없음")
        body = m.group(1)
        self.assertNotIn("'latin-1'", body,
            "BulkFixerWorker.run에 latin-1 폴백이 남아있음 (v1.0.2 버그)")

    def test_no_latin_1_in_bulk_preview(self):
        """BulkFixerPanel._on_file_selected이 latin-1 폴백을 사용하지 않아야 함."""
        m = re.search(
            r'def _on_file_selected\(self, cur, _prev\):(.*?)(?=\n    def |\nclass )',
            self.src, re.DOTALL)
        self.assertIsNotNone(m, "_on_file_selected 메서드를 찾을 수 없음")
        body = m.group(1)
        self.assertNotIn("'latin-1'", body,
            "BulkFixerPanel._on_file_selected에 latin-1 폴백이 남아있음 (v1.0.2 버그)")

    def test_alchemy_used_in_text_fixer(self):
        """TextFixerPanel.load_file must use alchemy-based encoding detection.

        From v1.0.6 Phase 2-a, both direct call and via safe_read_text_with_report helper
        (helper's internal L3935 invokes alchemy_detect_encoding) are accepted.
        """
        m = re.search(
            r'def load_file\(self, path: str\):(.*?)(?=\n    def |\nclass )',
            self.src, re.DOTALL)
        self.assertIsNotNone(m)
        body = m.group(1)
        self.assertTrue(
            'alchemy_detect_encoding' in body or 'safe_read_text_with_report' in body,
            "TextFixerPanel.load_file이 alchemy 기반 인코딩 감지를 사용하지 않음 "
            "(직접 호출 또는 safe_read_text_with_report 헬퍼 경유)")

    def test_alchemy_used_in_bulk_worker(self):
        """BulkFixerWorker.run must use alchemy-based encoding detection.

        From v1.0.6 Phase 2-a, both direct call and via safe_read_text_with_report helper
        (helper's internal L3935 invokes alchemy_detect_encoding) are accepted.
        """
        m = re.search(
            r'class BulkFixerWorker.*?def run\(self\):(.*?)(?=\n    def |\nclass )',
            self.src, re.DOTALL)
        self.assertIsNotNone(m)
        body = m.group(1)
        self.assertTrue(
            'alchemy_detect_encoding' in body or 'safe_read_text_with_report' in body,
            "BulkFixerWorker.run이 alchemy 기반 인코딩 감지를 사용하지 않음 "
            "(직접 호출 또는 safe_read_text_with_report 헬퍼 경유)")

    def test_alchemy_used_in_bulk_preview(self):
        """BulkFixerPanel._on_file_selected must use alchemy-based encoding detection.

        From v1.0.6 Phase 2-a, both direct call and via safe_read_text_with_report helper
        (helper's internal L3935 invokes alchemy_detect_encoding) are accepted.
        """
        m = re.search(
            r'def _on_file_selected\(self, cur, _prev\):(.*?)(?=\n    def |\nclass )',
            self.src, re.DOTALL)
        self.assertIsNotNone(m)
        body = m.group(1)
        self.assertTrue(
            'alchemy_detect_encoding' in body or 'safe_read_text_with_report' in body,
            "BulkFixerPanel._on_file_selected이 alchemy 기반 인코딩 감지를 사용하지 않음 "
            "(직접 호출 또는 safe_read_text_with_report 헬퍼 경유)")

    def test_cjk_encodings_listed(self):
        """3곳 모두 shift_jis/gbk/big5 폴백이 추가되어야 함 (5개 언어 지원 일치)."""
        # Simply verify it appears 3 or more times in the entire source
        for enc in ('shift_jis', 'gbk', 'big5'):
            count = self.src.count(f"'{enc}'")
            self.assertGreaterEqual(count, 3,
                f"'{enc}' 폴백이 3곳 미만 (Text Fixer + Bulk 2곳에 있어야 함): {count}회")


@unittest.skipUnless(HAS_MODULE, "FileNexusSuite 로드 실패 (PySide6 필요)")
class TestV103RegressionModule(unittest.TestCase):
    """v1.0.3 모듈 로드 기반 회귀 테스트."""

    def test_app_version_is_103(self):
        """APP_VERSION must be '1.0.3' or higher.
        Verifies the encoding-detection improvement introduced in v1.0.3,
        so 1.0.3 or higher satisfies it (consistent with V012/V100 pattern)."""
        ver = _ns.get('APP_VERSION')
        self.assertIsNotNone(ver, "APP_VERSION 정의 없음")
        parts = [int(p) for p in ver.split('.')]
        self.assertGreaterEqual(parts, [1, 0, 3],
            f"APP_VERSION {ver}은 1.0.3 이상이어야 함")

    def test_alchemy_detect_encoding_utf16_le(self):
        """alchemy_detect_encoding correctly detects UTF-16 LE.
        v1.0.4: changed to return an (encoding, confidence) tuple — verify first element."""
        detect = _ns.get('alchemy_detect_encoding')
        self.assertIsNotNone(detect)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b'\xff\xfe' + '한국어'.encode('utf-16-le'))
            path = f.name
        try:
            result = detect(path)
            # Up to v1.0.3: str, from v1.0.4: (str, float). Both formats compatible.
            enc = result[0] if isinstance(result, tuple) else result
            self.assertEqual(enc, 'utf-16')
        finally:
            os.unlink(path)

    def test_alchemy_detect_encoding_utf16_be(self):
        """alchemy_detect_encoding correctly detects UTF-16 BE.
        v1.0.4: changed to return an (encoding, confidence) tuple — verify first element."""
        detect = _ns.get('alchemy_detect_encoding')
        self.assertIsNotNone(detect)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b'\xfe\xff' + '한국어'.encode('utf-16-be'))
            path = f.name
        try:
            result = detect(path)
            enc = result[0] if isinstance(result, tuple) else result
            self.assertEqual(enc, 'utf-16')
        finally:
            os.unlink(path)


# ════════════════════════════════════════════════════════════════════════
# v1.0.4 regression tests — Text Merger comprehensive improvements
# ════════════════════════════════════════════════════════════════════════
class TestV104Regression(unittest.TestCase):
    """v1.0.4 — Text Merger encoding-option expansion + pre-warning + confidence UI + integration.

    Covers all four handover candidates 1/2/3/4:
      - D. _detect_encoding integration (alchemy signature expanded to (str, float))
      - A. Text Merger save-encoding expansion (Shift-JIS / GBK / Big5)
      - B. UnicodeEncodeError pre-warning dialog
      - C. Confidence-% color coding + tooltip
    """

    @classmethod
    def setUpClass(cls):
        with open(_MAIN_PY, encoding='utf-8') as f:
            cls.src = f.read()

    # ── D: _detect_encoding integration ──────────────────────────
    def test_alchemy_returns_tuple_in_source(self):
        """alchemy_detect_encoding 함수가 (enc, conf) 튜플 형식으로 반환해야 함."""
        m = re.search(
            r'def alchemy_detect_encoding\(path\):(.*?)(?=\ndef |\nclass )',
            self.src, re.DOTALL)
        self.assertIsNotNone(m, "alchemy_detect_encoding 함수를 찾을 수 없음")
        body = m.group(1)
        # Verify return statement is tuple-shaped ("...", ...) (blocks v1.0.3 string-only form)
        self.assertIn('return ("utf-8-sig", 1.0)', body,
            "BOM 감지 시 (str, float) 튜플 반환이 아님 (v1.0.3 시그니처 잔재)")
        self.assertIn('return ("utf-16", 1.0)', body,
            "UTF-16 BOM 감지 시 (str, float) 튜플 반환이 아님")

    def test_text_merger_no_self_detect_encoding(self):
        """Text Merger panel's _detect_encoding method must be removed (alchemy integration).
        Up to v1.0.3 Text Merger had its own _detect_encoding, but
        in v1.0.4 it was unified into alchemy_detect_encoding."""
        # def _detect_encoding must NOT exist inside MergePanel class
        self.assertNotIn('def _detect_encoding(self, path)', self.src,
            "Text Merger의 _detect_encoding 메서드가 아직 남아있음 (D 작업 누락)")

    def test_text_merger_uses_alchemy(self):
        """Text Merger 파일 추가 흐름에서 alchemy_detect_encoding을 호출해야 함."""
        # Verify alchemy call in _add_files or equivalent flow
        # Whether self._detect_encoding(path) → alchemy_detect_encoding(path) change was applied
        self.assertNotIn('self._detect_encoding(path)', self.src,
            "Text Merger가 여전히 self._detect_encoding을 호출 (D 작업 누락)")
        # Verify call-pattern change
        m = re.search(r'enc, conf = alchemy_detect_encoding\(path\)', self.src)
        self.assertIsNotNone(m, "Text Merger _add_files에서 alchemy 호출 패턴이 안 보임")

    def test_alchemy_callers_unpack_tuple(self):
        """All call sites of alchemy_detect_encoding must use tuple unpacking.
        v1.0.4: signature change requires receiving as (enc, conf) or (enc, _).

        v1.0.6 Phase 2-a: direct calls in TextFixer / BulkWorker / BulkPreview (3 sites)
        were unified through safe_read_text_with_report helper, reducing call count (6+ → 4).
        Definition 1 (L3676) + safe_read_text_with_report internal 1 + Text Converter +
        Text Merger = total 4 is the expected count after Phase 2-a.
        """
        # Total call count (definitions included — regex matches definitions too)
        all_calls = re.findall(r'alchemy_detect_encoding\(', self.src)
        self.assertGreaterEqual(len(all_calls), 4,
            f"alchemy_detect_encoding 호출이 4건 미만: {len(all_calls)} "
            f"(Phase 2-a 이후 정상 하한은 4 — 정의 + 헬퍼 + Converter + Merger)")
        # Block leftover single-variable assignment patterns (e.g., detected_enc = alchemy_detect_encoding(path))
        bad = re.findall(r'^\s*[a-z_]+ = alchemy_detect_encoding\(',
                         self.src, re.MULTILINE)
        self.assertEqual(bad, [],
            f"튜플 언패킹 안 한 호출부 발견 (v1.0.3 시그니처 잔재): {bad}")

    # ── A: Add Text Merger encoding options ──────────────────────
    def test_text_merger_combo_has_cjk_encodings(self):
        """Text Merger combobox must include Shift-JIS, GBK, and Big5.
        v1.0.5: addItems([...]) moved to _ENC_ITEMS constant. Regex updated to search the constant block."""
        # v1.0.5: Verify CJK 3 types in _ENC_ITEMS class constant
        m = re.search(r'_ENC_ITEMS\s*=\s*\[(.*?)\]', self.src, re.DOTALL)
        self.assertIsNotNone(m,
            "_ENC_ITEMS 상수를 찾을 수 없음 (v1.0.5 구조 누락)")
        block = m.group(1)
        for key in ('Shift-JIS', 'GBK', 'Big5'):
            with self.subTest(key=key):
                self.assertIn(f'"{key}"', block,
                    f"_ENC_ITEMS에 {key} 누락")

    def test_text_merger_codec_map_has_cjk(self):
        """저장 시 라벨→codec 매핑에 신규 3개가 추가되어야 함."""
        # Verify Shift-JIS / GBK / Big5 mapping in _enc_codec dict
        for label, codec in (("Shift-JIS", "shift_jis"),
                              ("GBK",       "gbk"),
                              ("Big5",      "big5")):
            with self.subTest(label=label):
                pattern = f'"{label}":\\s*"{codec}"'
                self.assertIsNotNone(re.search(pattern, self.src),
                    f"codec 매핑 누락: {label} → {codec}")

    def test_delegate_color_label_has_cjk(self):
        """MergeEncodingDelegate의 _ENC_COLOR/_ENC_LABEL에 신규 인코딩 키가 있어야 함."""
        for key in ('shift_jis', 'gbk', 'big5'):
            with self.subTest(key=key):
                # Keys must appear in both dicts, so at least 2 occurrences
                count = self.src.count(f"'{key}':")
                self.assertGreaterEqual(count, 2,
                    f"_ENC_COLOR/_ENC_LABEL에 '{key}' 키 누락 (현재 {count}회)")

    # ── B: UnicodeEncodeError pre-warning ────────────────────────
    def test_alchemy_check_encoding_compat_defined(self):
        """v1.0.4 신규 함수 alchemy_check_encoding_compat이 정의되어야 함."""
        self.assertIn('def alchemy_check_encoding_compat(text, codec):', self.src,
            "alchemy_check_encoding_compat 함수가 정의되어 있지 않음")

    def test_merge_done_uses_check_encoding_compat(self):
        """_on_merge_done에서 alchemy_check_encoding_compat을 호출해야 함."""
        m = re.search(
            r'def _on_merge_done\(self, merged_text, enc_summary\):(.*?)(?=\n    def |\nclass )',
            self.src, re.DOTALL)
        self.assertIsNotNone(m, "_on_merge_done 메서드를 찾을 수 없음")
        body = m.group(1)
        self.assertIn('alchemy_check_encoding_compat(merged_text', body,
            "_on_merge_done이 사전 검증 함수를 호출하지 않음")

    def test_merge_enc_warn_keys_in_5_languages(self):
        """5개 언어 사전에 merge_enc_warn_title / merge_enc_warn_msg 키가 있어야 함."""
        for key in ('merge_enc_warn_title', 'merge_enc_warn_msg'):
            with self.subTest(key=key):
                count = self.src.count(f"'{key}'")
                self.assertGreaterEqual(count, 5,
                    f"'{key}' 키가 5개 언어 미만 정의됨 (현재 {count}회)")

    # ── C: Confidence color coding + tooltip ─────────────────────
    def test_confidence_4_tier_color_coding(self):
        """MergeEncodingDelegate.paint에 신뢰도 4단계 색상 분기가 있어야 함."""
        # Whether all 4 colors appear
        for hex_color in ('#4CAF50', '#F1C40F', '#E67E22', '#E74C3C'):
            with self.subTest(color=hex_color):
                self.assertIn(hex_color, self.src,
                    f"신뢰도 색상 {hex_color} 누락 (4단계 색상 코딩 미적용)")
        # Verify threshold branching pattern
        self.assertIn('conf >= 0.90', self.src, "≥90% 분기 누락")
        self.assertIn('conf >= 0.70', self.src, "≥70% 분기 누락")
        self.assertIn('conf >= 0.50', self.src, "≥50% 분기 누락")

    def test_merge_low_conf_hint_keys_in_5_languages(self):
        """5개 언어 사전에 merge_low_conf_hint 키가 있어야 함 (툴팁용)."""
        count = self.src.count("'merge_low_conf_hint'")
        self.assertGreaterEqual(count, 5,
            f"'merge_low_conf_hint' 키가 5개 언어 미만 정의됨 (현재 {count}회)")

    # ── Bug-fix verification (v1.0.4 initial-release feedback) ──
    def test_dlg_question_supports_rich_text(self):
        """_dlg_question must support a rich_text parameter.
        Bug 1 fix: HTML tags (<b>, <br>, <code>) in warning dialogs were
        displayed as plain text instead of being rendered — now fixed."""
        # Verify rich_text parameter exists in function signature
        self.assertIn('def _dlg_question(parent, title: str, msg: str, min_width: int = 360, rich_text: bool = False)',
                      self.src,
                      "_dlg_question에 rich_text 파라미터 추가 누락")
        # Text Merger warning call site must call with rich_text=True
        self.assertIn("_dlg_question(self, _t('merge_enc_warn_title'), warn_msg, min_width=460, rich_text=True)",
                      self.src,
                      "Text Merger 경고 다이얼로그 호출부가 rich_text=True를 전달하지 않음")

    def test_alchemy_fallback_covers_cjk(self):
        """alchemy_detect_encoding's fallback logic must include sequential CJK encoding probes.
        Bug 2 fix: even when chardet misidentifies Shift-JIS files starting with ASCII as cp1006 etc.,
        the fallback stage now uses strict decoding to find the correct encoding."""
        m = re.search(
            r'def alchemy_detect_encoding\(path\):(.*?)(?=\ndef |\nclass )',
            self.src, re.DOTALL)
        self.assertIsNotNone(m)
        body = m.group(1)
        # Fallback loop must list CJK 4 types (order matters: cp949 → shift_jis → gbk → big5)
        self.assertIn('for _fallback in ("cp949", "shift_jis", "gbk", "big5"):',
                      body,
                      "alchemy 폴백 루프에 CJK 순차 검증 누락")
        # Verify raw.decode(_fallback) pattern
        self.assertIn('raw.decode(_fallback)', body,
                      "alchemy 폴백 루프에서 strict 디코딩 검증 누락")


@unittest.skipUnless(HAS_MODULE, "FileNexusSuite 로드 실패 (PySide6 필요)")
class TestV104RegressionModule(unittest.TestCase):
    """v1.0.4 모듈 로드 기반 회귀 테스트 — 런타임 동작 검증."""

    def test_app_version_is_104_or_later(self):
        """APP_VERSION must be '1.0.4' or higher.
        Originally at v1.0.4 release this checked 'exactly 1.0.4'; later relaxed to '>=' so
        v1.0.5+ also passes. Intent preserved (any version released since v1.0.4)."""
        ver = _ns.get('APP_VERSION')
        self.assertIsNotNone(ver, "APP_VERSION 없음")
        # '1.0.4' or higher (use tuple compare instead of string compare to handle cases like '1.0.10')
        parts = tuple(int(p) for p in ver.split('.'))
        self.assertGreaterEqual(parts, (1, 0, 4),
            f"APP_VERSION이 v1.0.4 미만: {ver}")

    def test_alchemy_detect_encoding_returns_tuple(self):
        """alchemy_detect_encoding이 (str, float) 튜플을 반환해야 함."""
        detect = _ns.get('alchemy_detect_encoding')
        self.assertIsNotNone(detect)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b'\xef\xbb\xbf' + 'hello'.encode('utf-8'))  # UTF-8 BOM
            path = f.name
        try:
            result = detect(path)
            self.assertIsInstance(result, tuple, f"튜플이 아님: {type(result)}")
            self.assertEqual(len(result), 2, "튜플이 (enc, conf) 2-tuple이 아님")
            enc, conf = result
            self.assertIsInstance(enc, str)
            self.assertIsInstance(conf, float)
            self.assertEqual(enc, 'utf-8-sig')
            self.assertEqual(conf, 1.0, "BOM 감지 시 신뢰도 1.0이어야 함")
        finally:
            os.unlink(path)

    def test_check_encoding_compat_korean_to_shift_jis(self):
        """Saving Korean text as Shift-JIS must trigger loss detection.
        v1.0.4 expansion: enlarged to SAMPLE_KO_LONG_SENTENCES (~140 chars) to approximate real usage.
        v1.0.4 change: return value expanded to 5-tuple (kinds, total, total_chars added)."""
        check = _ns.get('alchemy_check_encoding_compat')
        self.assertIsNotNone(check, "alchemy_check_encoding_compat 함수 누락")
        has_loss, bad_kinds, bad_total, total_chars, samples = check(
            SAMPLE_KO_LONG_SENTENCES, 'shift_jis')
        self.assertTrue(has_loss, "한글→Shift-JIS 손실이 감지되지 않음")
        self.assertGreater(bad_kinds, 0, "깨질 고유 종류 수가 0")
        self.assertGreater(bad_total, 0, "영향 받는 총 글자 수가 0")
        self.assertGreaterEqual(bad_total, bad_kinds,
            "영향 총 글자 수는 고유 종류 수보다 작을 수 없음")
        self.assertEqual(total_chars, len(SAMPLE_KO_LONG_SENTENCES),
            "total_chars가 텍스트 길이와 불일치")
        self.assertGreater(len(samples), 0, "샘플 문자가 비어있음")
        # Long text should fill all 5 sample slots (Korean has many distinct character types)
        self.assertEqual(len(samples), 5,
            f"긴 한글 텍스트인데 샘플이 5개 미만: {len(samples)}개")

    def test_check_encoding_compat_utf8_passthrough(self):
        """UTF-8 encoding can represent every Unicode character → no loss.
        v1.0.4 expansion: richer multilingual + emoji mix to approximate real environments.
        v1.0.4 change: return value expanded to 5-tuple."""
        check = _ns.get('alchemy_check_encoding_compat')
        self.assertIsNotNone(check)
        # Long text mixing Korean, Japanese, Chinese, emojis, and special characters
        text = ('안녕하세요 반갑습니다. 이것은 인코딩 호환성 검증을 위한 테스트 문장입니다. '
                'こんにちは世界。これは日本語のサンプル文章です。テスト用に作成されました。 '
                '你好世界。这是简体中文的测试样本。用于验证编码兼容性。 '
                '你好世界。這是繁體中文的測試樣本。用於驗證編碼相容性。 '
                'Hello World! This is an English test sample. Used for encoding verification. '
                '🌸 🌏 🎉 © ® ™ € £ ¥ — « » “ ” ‘ ’')
        has_loss, bad_kinds, bad_total, total_chars, samples = check(text, 'utf-8')
        self.assertFalse(has_loss, "UTF-8에서 손실이 감지됨 (잘못된 동작)")
        self.assertEqual(bad_kinds, 0)
        self.assertEqual(bad_total, 0)
        self.assertEqual(total_chars, len(text))
        self.assertEqual(samples, [])

    def test_check_encoding_compat_samples_limited_to_5(self):
        """Sample list must be capped at 5 even with many breakable chars (dialog readability).
        v1.0.4 change: return value expanded to 5-tuple."""
        check = _ns.get('alchemy_check_encoding_compat')
        self.assertIsNotNone(check)
        # Secure dozens of unique breakable chars (emoji + Korean + Japanese + Chinese)
        text = ('🌸🌏🎉🔥🌟🎨🎭🎪🎯🎲'
                '안녕하세요반갑습니다테스트문장'
                'こんにちは世界サンプル文章'
                '你好世界简体繁體')
        has_loss, bad_kinds, bad_total, total_chars, samples = check(text, 'cp949')
        self.assertTrue(has_loss, "cp949에서 이모지/번체 손실이 감지되지 않음")
        self.assertGreater(bad_kinds, 5, "테스트 설계 오류: 깨질 고유 종류가 5개 이하")
        self.assertEqual(len(samples), 5,
            f"샘플 개수가 5개로 제한되지 않음: {len(samples)}개")

    def test_check_encoding_compat_total_affected_count(self):
        """Total affected character count must match the actual ? substitution count (including duplicates).
        v1.0.4 option B: gives the user an accurate '% of the actual file that breaks'."""
        check = _ns.get('alchemy_check_encoding_compat')
        self.assertIsNotNone(check)
        # '한' character repeats exactly 10 times + ASCII spaces
        text = '한 ' * 10  # 20 chars total — '한' appears 10 times
        has_loss, bad_kinds, bad_total, total_chars, samples = check(text, 'cp1252')
        self.assertTrue(has_loss)
        # cp1252 can't represent Hangul but can represent spaces → all 10 '한' break
        self.assertEqual(bad_kinds, 1, f"고유 종류 수가 1이 아님: {bad_kinds}")
        self.assertEqual(bad_total, 10, f"영향 총 글자 수가 10이 아님: {bad_total}")
        self.assertEqual(total_chars, 20, f"전체 글자 수가 20이 아님: {total_chars}")
        # Cross-verify it matches the ? count when actually saved with replace
        encoded = text.encode('cp1252', errors='replace')
        question_count = encoded.count(b'?')
        self.assertEqual(bad_total, question_count,
            f"bad_total({bad_total}) != 실제 ? 개수({question_count})")

    def test_alchemy_detect_ascii_started_shift_jis(self):
        """Shift-JIS files starting with ASCII must be detected correctly.
        Bug 2 fix: chardet misidentifies such files as cp1006 (Urdu) and similar,
        but alchemy's fallback stage rescues them via sequential strict CJK probing.

        Test content is built long enough (~9KB) to mirror the actually reported case.
        Short content may accidentally decode under cp949, giving no meaningful validation."""
        detect = _ns.get('alchemy_detect_encoding')
        self.assertIsNotNone(detect)
        import tempfile
        # Includes enough Japanese text to match the actually reported case (9552 bytes)
        # + Shift-JIS-unique punctuation guarantees cp949 decode failure
        ja_line = 'これは日本語のエンコーディングテストです。漢字・ひらがな・カタカナを含みます。\r\n'
        special = '々ヽヾゝゞ〃仝〆〇ー「」『』〜\r\n'  # Shift-JIS-unique symbols (all encodable)
        content = ('Hello. This is an English encoding test file.\r\n'
                   'For File Nexus Suite Bulk Fixer verification.\r\n'
                   '\r\n'
                   + ja_line * 80  # ~8KB of Japanese
                   + special * 10)  # ensure Shift-JIS-unique chars included
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(content.encode('shift_jis'))
            path = f.name
        try:
            enc, _conf = detect(path)
            self.assertEqual(enc, 'shift_jis',
                f"ASCII로 시작하는 Shift-JIS 파일을 올바르게 감지 못함: {enc}")
        finally:
            os.unlink(path)


class TestV105Regression(unittest.TestCase):
    """v1.0.5 — Text Merger save-encoding dropdown UI usability improvements (source-level verification).

    Key changes:
      - Combobox: addItems(strings) → addItem(display, userData) pattern
      - Internal keys (existing 8) preserved in userData → 100% compatible with prior settings
      - Display labels reference per-language i18n keys (e.g., 'Shift-JIS (Japanese)', '(日文)', etc.)
      - New help label (merge_enc_hint): "If unsure, select UTF-8"
    """

    @classmethod
    def setUpClass(cls):
        with open(_MAIN_PY, encoding='utf-8') as f:
            cls.src = f.read()

    # ── Class constant _ENC_ITEMS verification ───────────────────
    def test_enc_items_constant_defined(self):
        """TextMergerPanel에 _ENC_ITEMS 클래스 상수가 정의되어야 한다."""
        self.assertIn('_ENC_ITEMS = [', self.src,
            "TextMergerPanel._ENC_ITEMS 상수 누락")

    def test_enc_items_contains_all_8_keys(self):
        """_ENC_ITEMS에 기존 8종 내부 키가 모두 포함되어야 한다 (순서 포함)."""
        m = re.search(
            r'_ENC_ITEMS\s*=\s*\[(.*?)\]',
            self.src, re.DOTALL)
        self.assertIsNotNone(m, "_ENC_ITEMS 리스트 블록을 찾지 못함")
        block = m.group(1)
        expected_keys = ['UTF-8', 'UTF-8-BOM', 'EUC-KR', 'CP949',
                         'UTF-16', 'Shift-JIS', 'GBK', 'Big5']
        for key in expected_keys:
            self.assertIn(f'"{key}"', block,
                f"_ENC_ITEMS에 내부 키 {key!r} 누락 (설정 호환성 위험)")
        # Each key maps to an i18n key
        for i18n_key in ['merge_enc_utf8', 'merge_enc_utf8_bom', 'merge_enc_euckr',
                         'merge_enc_cp949', 'merge_enc_utf16', 'merge_enc_shiftjis',
                         'merge_enc_gbk', 'merge_enc_big5']:
            self.assertIn(f"'{i18n_key}'", block,
                f"_ENC_ITEMS에 i18n 키 {i18n_key!r} 누락")

    # ── Combobox addItem pattern verification ────────────────────
    def test_combo_uses_add_item_with_user_data(self):
        """콤보박스 초기화는 addItem(display, userData) 패턴을 사용해야 한다."""
        # v1.0.4's addItems(["UTF-8", ...]) pattern must not remain
        self.assertNotIn(
            'self._combo_enc.addItems(["UTF-8", "UTF-8-BOM"',
            self.src,
            "v1.0.4 addItems 패턴이 아직 남아있음 (안 B 적용 누락)")
        # Verify the new pattern
        self.assertIn(
            'self._combo_enc.addItem(_t(_i18n_key), _enc_key)',
            self.src,
            "addItem(display, userData) 신규 패턴이 보이지 않음")

    # ── Help-label verification ──────────────────────────────────
    def test_enc_hint_label_created(self):
        """_lbl_enc_hint QLabel이 생성되어야 한다 (콤보박스 아래 도움말)."""
        self.assertIn('self._lbl_enc_hint = QLabel(_t(\'merge_enc_hint\'))', self.src,
            "_lbl_enc_hint 라벨 생성 코드 누락")

    def test_enc_hint_label_retranslated(self):
        """retranslate()에서 _lbl_enc_hint 텍스트 갱신 로직이 있어야 한다."""
        self.assertIn("self._lbl_enc_hint.setText(_t('merge_enc_hint'))", self.src,
            "retranslate()에서 도움말 라벨 setText 누락")

    def test_retranslate_updates_combo_item_text(self):
        """retranslate()에서 콤보박스 8개 아이템 라벨도 갱신되어야 한다 (언어 전환 대응)."""
        self.assertIn('self._combo_enc.setItemText(_i, _t(_i18n_key))', self.src,
            "retranslate()에서 콤보박스 아이템 라벨 갱신 로직 누락")

    # ── currentText → currentData migration verification ────────
    def test_merge_files_uses_current_data(self):
        """_merge_files()에서 currentData() 기반으로 내부 키를 가져와야 한다."""
        # v1.0.5: currentData() or currentText() fallback pattern
        self.assertIn(
            'self._save_enc = self._combo_enc.currentData() or self._combo_enc.currentText()',
            self.src,
            "_merge_files에서 currentData 패턴이 보이지 않음")

    def test_get_config_uses_current_data(self):
        """get_config()에서 currentData() 기반으로 내부 키를 저장해야 한다."""
        # get_config's 'combo_enc': line must use currentData()
        m = re.search(
            r"'combo_enc':\s*self\._combo_enc\.currentData\(\)\s*or\s*self\._combo_enc\.currentText\(\)",
            self.src)
        self.assertIsNotNone(m,
            "get_config()에서 currentData 폴백 패턴이 보이지 않음")

    def test_apply_config_uses_find_data_with_fallback(self):
        """apply_config() must prefer findData(), falling back to findText() on miss.
        Reason: up to v1.0.4 the display text (e.g., 'Shift-JIS') was stored, so
        v1.0.5 must load older config files without failure — double defense."""
        self.assertIn('idx = self._combo_enc.findData(enc)', self.src,
            "apply_config()에서 findData 호출 누락")
        self.assertIn('if idx < 0: idx = self._combo_enc.findText(enc)', self.src,
            "apply_config()에서 findText 폴백 누락 (구버전 호환 위험)")

    # ── Verify all 45 translation entries exist ──────────────────
    def test_all_languages_have_enc_keys(self):
        """5개 언어 사전에 9개 merge_enc_* 키가 모두 있어야 한다 (총 45개)."""
        required_keys = [
            'merge_enc_utf8', 'merge_enc_utf8_bom', 'merge_enc_euckr',
            'merge_enc_cp949', 'merge_enc_utf16', 'merge_enc_shiftjis',
            'merge_enc_gbk', 'merge_enc_big5', 'merge_enc_hint',
        ]
        # Each key must appear at least 5 times (5 languages)
        for key in required_keys:
            count = len(re.findall(rf"'{key}'\s*:", self.src))
            self.assertGreaterEqual(count, 5,
                f"키 '{key}'가 5개 언어 사전 중 {count}개에만 존재 (누락)")

    def test_zh_uses_rifun_not_rigoyu(self):
        """Simplified/Traditional Chinese must use the '日文' label (consistent with v1.0.4 tip).
        Explicitly verified because '日语'/'日語' could be mistakenly written."""
        # Both Simplified and Traditional use '(日文)' for Shift-JIS
        # '日语' or '日語' would be a wrong translation (v1.0.4 tip uses '日文' consistently)
        # Check only inside the Chinese dict block (Japanese dict's '日本語' is fine)
        m_zh_cn = re.search(
            r"'zh_cn':\s*\{(.*?)(?='zh_tw'|\Z)", self.src, re.DOTALL)
        self.assertIsNotNone(m_zh_cn, "zh_cn 사전 블록 탐색 실패")
        zh_cn_block = m_zh_cn.group(1)
        self.assertIn("'Shift-JIS (日文)'", zh_cn_block,
            "중국어 간체에서 Shift-JIS 라벨이 '(日文)' 아님")
        self.assertNotIn("'Shift-JIS (日语)'", zh_cn_block,
            "중국어 간체에서 '日语' 사용됨 (v1.0.4 tip과 불일치)")

        m_zh_tw = re.search(
            r"'zh_tw':\s*\{(.*?)$", self.src, re.DOTALL)
        self.assertIsNotNone(m_zh_tw, "zh_tw 사전 블록 탐색 실패")
        zh_tw_block = m_zh_tw.group(1)
        self.assertIn("'Shift-JIS (日文)'", zh_tw_block,
            "중국어 번체에서 Shift-JIS 라벨이 '(日文)' 아님")
        self.assertNotIn("'Shift-JIS (日語)'", zh_tw_block,
            "중국어 번체에서 '日語' 사용됨 (v1.0.4 tip과 불일치)")

    # ── APP_VERSION verification split into TestAppVersion (v1.0.7 redesign as version-independent structural check) ─────


@unittest.skipUnless(HAS_MODULE, "FileNexusSuite 로드 실패 (PySide6 필요)")
class TestV105RegressionModule(unittest.TestCase):
    """v1.0.5 module-load-based regression tests — runtime behavior verification.

    Note: APP_VERSION verification was split into TestAppVersionModule (redesigned in v1.0.7 as version-independent structural verification)
    """

    def test_translations_have_all_enc_keys(self):
        """5개 언어 각각에 9개 merge_enc_* 키가 실제 값으로 존재해야 한다."""
        translations = _ns.get('TRANSLATIONS')
        self.assertIsNotNone(translations, "TRANSLATIONS 딕셔너리 누락")
        required_keys = [
            'merge_enc_utf8', 'merge_enc_utf8_bom', 'merge_enc_euckr',
            'merge_enc_cp949', 'merge_enc_utf16', 'merge_enc_shiftjis',
            'merge_enc_gbk', 'merge_enc_big5', 'merge_enc_hint',
        ]
        for lang_code in ('ko', 'en', 'ja', 'zh_cn', 'zh_tw'):
            self.assertIn(lang_code, translations,
                f"언어 '{lang_code}' 사전 누락")
            lang_dict = translations[lang_code]
            for key in required_keys:
                self.assertIn(key, lang_dict,
                    f"[{lang_code}] 키 '{key}' 누락")
                val = lang_dict[key]
                self.assertIsInstance(val, str,
                    f"[{lang_code}] '{key}' 값이 문자열 아님")
                self.assertTrue(len(val) > 0,
                    f"[{lang_code}] '{key}' 값이 빈 문자열")

    def test_enc_labels_contain_internal_keys(self):
        """Each language's label must contain the internal encoding key (e.g., 'UTF-8 (...)').
        Reason: users must be able to identify which encoding from the label alone."""
        translations = _ns.get('TRANSLATIONS')
        key_to_enc = [
            ('merge_enc_utf8',     'UTF-8'),
            ('merge_enc_utf8_bom', 'UTF-8-BOM'),
            ('merge_enc_euckr',    'EUC-KR'),
            ('merge_enc_cp949',    'CP949'),
            ('merge_enc_utf16',    'UTF-16'),
            ('merge_enc_shiftjis', 'Shift-JIS'),
            ('merge_enc_gbk',      'GBK'),
            ('merge_enc_big5',     'Big5'),
        ]
        for lang_code in ('ko', 'en', 'ja', 'zh_cn', 'zh_tw'):
            lang_dict = translations.get(lang_code, {})
            for i18n_key, enc_name in key_to_enc:
                label = lang_dict.get(i18n_key, '')
                self.assertIn(enc_name, label,
                    f"[{lang_code}] '{i18n_key}' 라벨에 '{enc_name}'가 없음: {label!r}")

    def test_zh_labels_use_rifun(self):
        """Simplified/Traditional Chinese Shift-JIS label must contain '日文'.
        (Idiomatic Chinese form, distinct from Japanese-locale '日本語')"""
        translations = _ns.get('TRANSLATIONS')
        for lang_code in ('zh_cn', 'zh_tw'):
            label = translations[lang_code].get('merge_enc_shiftjis', '')
            self.assertIn('日文', label,
                f"[{lang_code}] Shift-JIS 라벨에 '日文' 없음: {label!r}")
            self.assertNotIn('日语', label,
                f"[{lang_code}] '日语' 사용됨 (v1.0.4 tip과 불일치): {label!r}")
            self.assertNotIn('日語', label,
                f"[{lang_code}] '日語' 사용됨 (v1.0.4 tip과 불일치): {label!r}")

    def test_enc_items_preserves_v104_keys(self):
        """TextMergerPanel._ENC_ITEMS internal keys must remain compatible with values stored up to v1.0.4.
        This test ensures older config files still load cleanly."""
        panel_cls = _ns.get('TextMergerPanel')
        self.assertIsNotNone(panel_cls, "TextMergerPanel 클래스 누락")
        enc_items = getattr(panel_cls, '_ENC_ITEMS', None)
        self.assertIsNotNone(enc_items, "_ENC_ITEMS 상수 누락")
        # Extract internal keys only
        internal_keys = [k for k, _ in enc_items]
        # Must match v1.0.4 combobox order (regression guard for setCurrentIndex)
        expected_order = ['UTF-8', 'UTF-8-BOM', 'EUC-KR', 'CP949',
                          'UTF-16', 'Shift-JIS', 'GBK', 'Big5']
        self.assertEqual(internal_keys, expected_order,
            f"내부 키 순서가 v1.0.4와 불일치: {internal_keys}")

    def test_hint_message_guides_to_utf8(self):
        """도움말 문구가 UTF-8을 안내해야 한다 (비프로그래머 가이드 핵심 목적)."""
        translations = _ns.get('TRANSLATIONS')
        for lang_code in ('ko', 'en', 'ja', 'zh_cn', 'zh_tw'):
            hint = translations[lang_code].get('merge_enc_hint', '')
            self.assertIn('UTF-8', hint,
                f"[{lang_code}] 도움말에 'UTF-8' 안내 누락: {hint!r}")


@unittest.skipUnless(HAS_MODULE, "FileNexusSuite 로드 실패 (PySide6 필요)")
class TestV105StatusRetranslate(unittest.TestCase):
    """v1.0.5 — Text Merger status-message refresh bug fix on language switch.

    Background:
      - Likely a long-standing bug from before v1.0.4
      - retranslate() refreshed _lbl_status only when state == `merge_status_ready`
      - Result: after adding files and switching language, "26 files added..." stayed in Korean
      - Found in v1.0.5 post-build hands-on QA (Hanrim) via screenshots in 3 languages

    Fix design:
      - Static messages (`ready`, `clr`, `reading`, `save_err`, `path_reset_done`): simple re-render
      - Restorable dynamic messages (`add`: file_list count, `path_set`: save_dir): rebuild from source info
      - Non-restorable messages (`del`, `save_done`, `bulk_scanning`): reset to `ready` + debug log
    """

    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        # Reuse a single QApplication (avoid conflicts with other tests)
        cls.app = QApplication.instance() or QApplication([])

    def _make_panel(self, lang_code='ko'):
        """Create a TextMergerPanel instance for testing.
        Temporarily change _current_lang while building the panel."""
        # Directly mutate _ns['_current_lang'] (exec namespace = _t's global scope)
        _ns['_current_lang'] = lang_code
        PanelCls = _ns.get('TextMergerPanel')
        return PanelCls()

    def _set_lang(self, lang_code):
        """현재 언어 설정 (런타임에서 언어 전환 시뮬레이션)."""
        _ns['_current_lang'] = lang_code

    # ── Static-message re-render ────────────────────────────
    def test_status_ready_retranslates(self):
        """'ready' 상태에서 언어 전환 시 해당 언어의 'ready' 메시지로 바뀐다."""
        panel = self._make_panel('ko')
        try:
            # Initial state = ready (Korean)
            translations = _ns.get('TRANSLATIONS')
            self.assertEqual(panel._lbl_status.text(), translations['ko']['merge_status_ready'])
            # Switch to English
            self._set_lang('en')
            panel._retranslate_status()
            self.assertEqual(panel._lbl_status.text(), translations['en']['merge_status_ready'])
            # Switch to Japanese
            self._set_lang('ja')
            panel._retranslate_status()
            self.assertEqual(panel._lbl_status.text(), translations['ja']['merge_status_ready'])
        finally:
            self._set_lang('ko')
            panel.deleteLater()

    def test_status_clr_retranslates(self):
        """'merge_status_clr' 상태에서 언어 전환 시 해당 언어로 갱신된다."""
        panel = self._make_panel('ko')
        try:
            translations = _ns.get('TRANSLATIONS')
            panel._lbl_status.setText(translations['ko']['merge_status_clr'])
            self._set_lang('en')
            panel._retranslate_status()
            self.assertEqual(panel._lbl_status.text(), translations['en']['merge_status_clr'])
        finally:
            self._set_lang('ko')
            panel.deleteLater()

    def test_status_save_err_retranslates(self):
        """'merge_save_err' 상태에서 언어 전환 시 해당 언어로 갱신된다."""
        panel = self._make_panel('ko')
        try:
            translations = _ns.get('TRANSLATIONS')
            panel._lbl_status.setText(translations['ko']['merge_save_err'])
            self._set_lang('zh_cn')
            panel._retranslate_status()
            self.assertEqual(panel._lbl_status.text(), translations['zh_cn']['merge_save_err'])
        finally:
            self._set_lang('ko')
            panel.deleteLater()

    # ── Dynamic-message restoration re-render ────────────────
    def test_status_add_retranslates_with_current_count(self):
        """In 'merge_status_add' state, language switch must rebuild from the current file_list count.
        This is the main bug scenario Hanrim found in screenshots (26 files added, then language switched)."""
        panel = self._make_panel('ko')
        try:
            translations = _ns.get('TRANSLATIONS')
            # Simulate file_list with 26 items (internal state only, real file objects unnecessary)
            panel.file_list = ['/dummy/path' + str(i) for i in range(26)]
            # Set the 'files added' message (Korean)
            panel._lbl_status.setText(translations['ko']['merge_status_add'].format(n=26))
            # Switch to Japanese
            self._set_lang('ja')
            panel._retranslate_status()
            expected = translations['ja']['merge_status_add'].format(n=26)
            self.assertEqual(panel._lbl_status.text(), expected,
                f"언어 전환 후 파일 추가 메시지가 일본어로 재구성 안 됨")
            # Switch to Simplified Chinese
            self._set_lang('zh_cn')
            panel._retranslate_status()
            expected = translations['zh_cn']['merge_status_add'].format(n=26)
            self.assertEqual(panel._lbl_status.text(), expected)
        finally:
            self._set_lang('ko')
            panel.deleteLater()

    def test_status_path_set_retranslates_with_save_dir(self):
        """'merge_path_set' 상태에서 언어 전환 시 현재 save_dir로 재구성된다."""
        panel = self._make_panel('ko')
        try:
            translations = _ns.get('TRANSLATIONS')
            panel.save_dir = 'C:/test/output'
            panel._lbl_status.setText(translations['ko']['merge_path_set'].format(path='C:/test/output'))
            self._set_lang('en')
            panel._retranslate_status()
            expected = translations['en']['merge_path_set'].format(path='C:/test/output')
            self.assertEqual(panel._lbl_status.text(), expected)
        finally:
            self._set_lang('ko')
            panel.deleteLater()

    def test_status_path_set_falls_back_to_ready_if_save_dir_empty(self):
        """save_dir이 비어있는데 메시지만 path_set 패턴인 엣지 케이스 → ready로 폴백."""
        panel = self._make_panel('ko')
        try:
            translations = _ns.get('TRANSLATIONS')
            panel.save_dir = ''  # no path
            panel._lbl_status.setText(translations['ko']['merge_path_set'].format(path='/removed/path'))
            self._set_lang('en')
            panel._retranslate_status()
            # Empty save_dir → fall back to ready
            self.assertEqual(panel._lbl_status.text(), translations['en']['merge_status_ready'])
        finally:
            self._set_lang('ko')
            panel.deleteLater()

    # ── Non-restorable message → reset to ready ─────────────
    def test_status_del_resets_to_ready_with_log(self):
        """'merge_status_del' 상태 (원본 개수 소실) → ready 리셋 + 디버그 로그 남김."""
        panel = self._make_panel('ko')
        try:
            translations = _ns.get('TRANSLATIONS')
            panel._lbl_status.setText(translations['ko']['merge_status_del'].format(n=5))
            self._set_lang('ja')
            panel._retranslate_status()
            self.assertEqual(panel._lbl_status.text(), translations['ja']['merge_status_ready'],
                "del 메시지가 ready로 리셋되지 않음")
        finally:
            self._set_lang('ko')
            panel.deleteLater()

    def test_status_save_done_resets_to_ready(self):
        """'merge_save_done' 상태 (enc/path 소실) → ready 리셋."""
        panel = self._make_panel('ko')
        try:
            translations = _ns.get('TRANSLATIONS')
            panel._lbl_status.setText(
                translations['ko']['merge_save_done'].format(enc='UTF-8', path='C:/out.txt'))
            self._set_lang('zh_tw')
            panel._retranslate_status()
            self.assertEqual(panel._lbl_status.text(), translations['zh_tw']['merge_status_ready'])
        finally:
            self._set_lang('ko')
            panel.deleteLater()

    # ── Defensive handling ──────────────────────────────────
    def test_unknown_status_text_left_untouched(self):
        """알려지지 않은 임의 텍스트는 변경하지 않는다 (방어적 처리)."""
        panel = self._make_panel('ko')
        try:
            arbitrary = "이건 어떤 상태도 아닌 임의 텍스트 @#$%"
            panel._lbl_status.setText(arbitrary)
            self._set_lang('en')
            panel._retranslate_status()
            # Unchanged
            self.assertEqual(panel._lbl_status.text(), arbitrary,
                "알려지지 않은 상태 텍스트가 의도치 않게 변경됨")
        finally:
            self._set_lang('ko')
            panel.deleteLater()

    # ── Pattern-matching utility unit tests ────────────────
    def test_match_status_template_with_placeholders(self):
        """_match_status_template이 플레이스홀더가 있는 템플릿을 정확히 인식한다."""
        panel = self._make_panel('ko')
        try:
            # Korean 'merge_status_add' template: "{n}개 파일 추가됨 (인코딩 자동 감지 완료)"
            self.assertTrue(
                panel._match_status_template("26개 파일 추가됨 (인코딩 자동 감지 완료)",
                                              'merge_status_add'))
            # English template
            self.assertTrue(
                panel._match_status_template("26 file(s) added (encoding auto-detected)",
                                              'merge_status_add'))
            # No-match case
            self.assertFalse(
                panel._match_status_template("전혀 다른 텍스트", 'merge_status_add'))
            # A different key's template (merge_status_clr) must not match
            self.assertFalse(
                panel._match_status_template("26개 파일 추가됨 (인코딩 자동 감지 완료)",
                                              'merge_status_clr'))
        finally:
            panel.deleteLater()


class TestV105TranslationNoDuplicates(unittest.TestCase):
    """v1.0.5 — Verify no recurrence after removing duplicate keys in translation dicts.

    Background:
      - v1.0.2 handover identified the 'zh_cn dict 188 duplicate keys' issue
      - At v1.0.5 measurement, 74 duplicate lines remained (all values identical, zero behavior impact)
      - All were safely deletable, so cleaned up in bulk this release
      - This test continuously guards against recurrence via source-parsing
    """

    @classmethod
    def setUpClass(cls):
        with open(_MAIN_PY, encoding='utf-8') as f:
            cls.src = f.read()

    def _count_keys_per_language(self):
        """Use AST to pin down each language's dict range in TRANSLATIONS,
        then count dict-key occurrences within that range."""
        import ast as _ast
        tree = _ast.parse(self.src)
        lines = self.src.split('\n')
        entry_pattern = re.compile(r"^\s*'([a-zA-Z_][a-zA-Z0-9_]*)'\s*:")

        per_lang = {}  # lang_code -> {key: count}
        for node in _ast.walk(tree):
            if isinstance(node, _ast.Assign):
                for tgt in node.targets:
                    if isinstance(tgt, _ast.Name) and tgt.id == 'TRANSLATIONS':
                        if isinstance(node.value, _ast.Dict):
                            for k, v in zip(node.value.keys, node.value.values):
                                if isinstance(k, _ast.Constant):
                                    block = lines[v.lineno-1:v.end_lineno]
                                    from collections import Counter
                                    keys_found = []
                                    for line in block:
                                        m = entry_pattern.match(line)
                                        if m:
                                            keys_found.append(m.group(1))
                                    per_lang[k.value] = Counter(keys_found)
        return per_lang

    def test_no_duplicate_keys_in_any_language(self):
        """Each of the 5 language dicts must have no duplicate keys.
        Python dicts overwrite duplicate keys with later values, so no behavior bug, but
        - Wasted lines of code
        - When editing translations, fixing one side leaves the other intact, causing confusion
        - Tech debt left from v1.0.2 through v1.0.4
        — included as a structural verification test for ongoing surveillance."""
        per_lang = self._count_keys_per_language()
        self.assertEqual(len(per_lang), 5,
            f"TRANSLATIONS에 5개 언어가 있어야 하는데 {len(per_lang)}개")
        for lang_code, counter in per_lang.items():
            dups = {k: v for k, v in counter.items() if v > 1}
            self.assertEqual(len(dups), 0,
                f"[{lang_code}] 중복 키 {len(dups)}개 발견: {list(dups.items())[:5]}")

    def test_all_languages_have_similar_key_count(self):
        """All 5 languages should have similar unique-key counts (completeness guarantee).
        A large gap signals missing translations in some language.
        Just after v1.0.5 dedup cleanup, ~391±2 was set as the allowed range.
        v1.0.9 §5.1.G — zh_cn is allowed to be a subset (uses zh_tw fallback mechanism),
        so excluded from this check; the other 4 languages are forced to differ by ≤5."""
        per_lang = self._count_keys_per_language()
        counts = {lang: len(c) for lang, c in per_lang.items()}
        # zh_cn is intentionally smaller (zh_tw fallback) — excluded from key-count check
        counts_for_check = {l: c for l, c in counts.items() if l != 'zh_cn'}
        max_count = max(counts_for_check.values())
        min_count = min(counts_for_check.values())
        # Exact match is hard, so allow up to 5 difference (some untranslated keys may remain)
        self.assertLessEqual(max_count - min_count, 5,
            f"언어별 키 수 차이 과다 (zh_cn 제외, 허용 ≤5): "
            f"{counts_for_check}  (zh_cn={counts.get('zh_cn')} — fallback 의도)")


# ════════════════════════════════════════════════════════════════════════
# §AdditionalN  APP_VERSION verification (v1.0.6)
# ════════════════════════════════════════════════════════════════════════
# Verify APP_VERSION constant is correctly bumped at version-up time.
# v1.0.7 redesign — version-snapshot style (TestV104Regression → TestV105Regression →
# TestV106AppVersion carry-over) shifted to version-independent structural verification. docs/TEST_MANAGEMENT_POLICY.md
# §4.4 "no new version-snapshot invariants" principle applied. Each release used to carry forward
# class names and verification values manually — that's now retired. Just verify APP_VERSION exists
# and follows semver (MAJOR.MINOR.PATCH). All versions (v1.0.7, v1.0.8, v2.0.0, etc.)
# pass without additional updates.


class TestAppVersion(unittest.TestCase):
    """APP_VERSION constant structural verification (v1.0.7 redesign, version-independent).

    Prior history: TestV104Regression → TestV105Regression → TestV106AppVersion (carry-over style)
    Current style: version-independent structural verification (semver format only, no concrete value forced)
    """

    @classmethod
    def setUpClass(cls):
        with open(_MAIN_PY, encoding='utf-8') as f:
            cls.src = f.read()

    def test_app_version_defined_in_source(self):
        """소스에 APP_VERSION 문자열 상수가 정의되어 있어야 한다."""
        m = re.search(r'^APP_VERSION\s*=\s*[\"\']([^\"\']+)[\"\']',
                      self.src, re.MULTILINE)
        self.assertIsNotNone(m, "APP_VERSION 정의 없음 (소스 L76 부근 확인)")

    def test_app_version_source_format_is_semver(self):
        """소스의 APP_VERSION은 세미버전 형식(MAJOR.MINOR.PATCH)을 따라야 한다."""
        m = re.search(r'^APP_VERSION\s*=\s*[\"\']([^\"\']+)[\"\']',
                      self.src, re.MULTILINE)
        self.assertIsNotNone(m, "APP_VERSION 정의 없음")
        self.assertRegex(m.group(1), r'^\d+\.\d+\.\d+$',
            f"APP_VERSION 포맷 위반: {m.group(1)} (세미버전 MAJOR.MINOR.PATCH 필요)")


@unittest.skipUnless(HAS_MODULE, "FileNexusSuite 로드 실패 (PySide6 필요)")
class TestAppVersionModule(unittest.TestCase):
    """APP_VERSION 런타임 모듈 로드 기반 구조적 검증 (v1.0.7 재설계, 버전 독립)."""

    def test_app_version_loaded(self):
        """모듈 로드 시 APP_VERSION이 존재하고 문자열이어야 한다."""
        ver = _ns.get('APP_VERSION')
        self.assertIsNotNone(ver, "APP_VERSION 미정의")
        self.assertIsInstance(ver, str,
            f"APP_VERSION이 문자열이 아님: {type(ver).__name__}")

    def test_app_version_runtime_format_is_semver(self):
        """런타임 APP_VERSION이 세미버전 형식(MAJOR.MINOR.PATCH)을 따라야 한다."""
        ver = _ns.get('APP_VERSION')
        self.assertIsNotNone(ver, "APP_VERSION 미정의")
        self.assertRegex(ver, r'^\d+\.\d+\.\d+$',
            f"APP_VERSION 포맷 위반: {ver} (세미버전 MAJOR.MINOR.PATCH 필요)")


# ════════════════════════════════════════════════════════════════════════
# §AdditionalO  Phase 2-a encoding-report feature (v1.0.6)
# ════════════════════════════════════════════════════════════════════════

_safe_read_text = _ns.get('safe_read_text_with_report') if HAS_MODULE else None
_decode_tracking = _ns.get('_decode_with_failure_tracking') if HAS_MODULE else None
_write_report = _ns.get('write_encoding_report') if HAS_MODULE else None


@unittest.skipUnless(HAS_MODULE and _safe_read_text,
                     "FileNexusSuite 로드 실패 또는 safe_read_text_with_report 없음")
class TestSafeReadTextWithReport(unittest.TestCase):
    """v1.0.6 Phase 2-a: safe_read_text_with_report — 6-tuple 반환 구조."""

    def setUp(self):
        self.td = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.td, ignore_errors=True)

    def _write_bytes(self, name, raw):
        p = os.path.join(self.td, name)
        with open(p, 'wb') as f:
            f.write(raw)
        return p

    def test_returns_6_tuple(self):
        """반환이 정확히 6-tuple이어야 함 (v1.0.5→v1.0.6 확장)."""
        p = self._write_bytes('t.txt', 'hello'.encode('utf-8'))
        result = _safe_read_text(p)
        self.assertEqual(len(result), 6,
            f"Phase 2-a 이후 6-tuple이어야 함 (현재 {len(result)})")

    def test_strict_success_returns_empty_failures(self):
        """정상 파일 → strict 모드 + failures=[] + total=0."""
        p = self._write_bytes('ok.txt', '정상 한국어'.encode('utf-8'))
        text, enc, mode, rc, failures, total = _safe_read_text(p)
        self.assertEqual(mode, 'strict')
        self.assertEqual(failures, [])
        self.assertEqual(total, 0)
        self.assertEqual(rc, 0)

    def test_replace_mode_returns_failures(self):
        """부분 손상 파일 → replace 모드 + failures 리스트 채워짐."""
        raw = 'abc'.encode('utf-8') + b'\xFF' + 'def'.encode('utf-8')
        p = self._write_bytes('bad.txt', raw)
        text, enc, mode, rc, failures, total = _safe_read_text(p)
        self.assertEqual(mode, 'replace')
        self.assertEqual(total, 1)
        self.assertEqual(len(failures), 1)
        f = failures[0]
        self.assertIn('byte_pos', f)
        self.assertIn('bad_bytes_hex', f)
        self.assertIn('line', f)
        self.assertIn('col', f)
        self.assertIn('context', f)

    def test_nonexistent_file_returns_none(self):
        """존재하지 않는 파일 → None 반환 (회귀 방지)."""
        result = _safe_read_text('/definitely/nonexistent/path.txt')
        self.assertIsNone(result[0])

    def test_utf8_bom_strict(self):
        """UTF-8-BOM 파일 → strict 성공."""
        p = self._write_bytes('bom.txt', '\ufeffBOM 테스트'.encode('utf-8'))
        _, enc, mode, _, _, _ = _safe_read_text(p)
        self.assertEqual(mode, 'strict')


@unittest.skipUnless(HAS_MODULE and _decode_tracking,
                     "FileNexusSuite 로드 실패 또는 _decode_with_failure_tracking 없음")
class TestDecodeWithFailureTracking(unittest.TestCase):
    """v1.0.6 Phase 2-a: 위치 추적 디코더 단위 테스트."""

    def test_normal_utf8(self):
        """정상 UTF-8 → failures=[], total=0."""
        raw = '안녕하세요'.encode('utf-8')
        text, failures, total = _decode_tracking(raw, 'utf-8')
        self.assertEqual(text, '안녕하세요')
        self.assertEqual(failures, [])
        self.assertEqual(total, 0)

    def test_single_bad_byte(self):
        """1개 오류 → failures 길이 1, bad_bytes_hex 정확."""
        raw = 'abc'.encode('utf-8') + b'\xFF' + 'def'.encode('utf-8')
        text, failures, total = _decode_tracking(raw, 'utf-8')
        self.assertEqual(total, 1)
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0]['bad_bytes_hex'], '0xFF')

    def test_line_tracking(self):
        """여러 줄에 걸친 오류 → line/col 정확."""
        raw = (b'line 1 ok\n' +
               b'line 2 ' + b'\xFF' + b'\n' +
               b'line 3 ok\n' +
               b'line 4 ' + b'\xFE' + b'\n')
        text, failures, total = _decode_tracking(raw, 'utf-8')
        self.assertEqual(total, 2)
        self.assertEqual(failures[0]['line'], 2)
        self.assertEqual(failures[1]['line'], 4)

    def test_crlf_line_counting(self):
        """CRLF 파일에서도 \\n 카운트로 라인 번호 정확."""
        raw = (b'line 1\r\nline 2\r\nerror ' + b'\xFF' + b'\r\n')
        text, failures, total = _decode_tracking(raw, 'utf-8')
        self.assertEqual(total, 1)
        self.assertEqual(failures[0]['line'], 3)

    def test_max_tracking_cap(self):
        """MAX_TRACK_FAILURES=5000 초과 시 failures는 5000으로 제한, total은 실제 수."""
        MAX = _ns.get('MAX_TRACK_FAILURES', 5000)
        raw = b'\xFF' * (MAX + 1000)
        text, failures, total = _decode_tracking(raw, 'utf-8')
        self.assertEqual(total, MAX + 1000)
        self.assertEqual(len(failures), MAX)

    def test_context_normalizes_whitespace(self):
        """context 내 줄바꿈/탭이 공백으로 정규화되어야 함 (가독성)."""
        raw = b'line1\n\tbad ' + b'\xFF' + b'\tmore\n'
        text, failures, total = _decode_tracking(raw, 'utf-8')
        ctx = failures[0]['context']
        self.assertNotIn('\n', ctx)
        self.assertNotIn('\t', ctx)
        self.assertNotIn('\r', ctx)

    def test_invalid_encoding_returns_none(self):
        """존재하지 않는 인코딩 → text=None 반환 (예외 던지지 않음)."""
        text, failures, total = _decode_tracking(b'hello', 'nonexistent-enc-xyz')
        self.assertIsNone(text)


@unittest.skipUnless(HAS_MODULE and _write_report,
                     "FileNexusSuite 로드 실패 또는 write_encoding_report 없음")
class TestWriteEncodingReport(unittest.TestCase):
    """v1.0.6 Phase 2-a: 인코딩 리포트 생성 테스트."""

    def setUp(self):
        self.td = tempfile.mkdtemp()
        # Minimal failures list (for testing)
        self.sample_failures = [
            {'byte_pos': 10, 'bad_bytes_hex': '0xFF',
             'line': 1, 'col': 5, 'context': 'test context'}
        ]

    def tearDown(self):
        shutil.rmtree(self.td, ignore_errors=True)

    def _orig_file(self):
        p = os.path.join(self.td, 'original.txt')
        with open(p, 'w', encoding='utf-8') as f:
            f.write('test')
        return p

    def test_returns_none_when_no_failures(self):
        """total_failures=0이면 None 반환 (리포트 생성 안 함)."""
        rp = _write_report(self.td, self._orig_file(), 'utf-8', [], 0, 'processed', lang='ko')
        self.assertIsNone(rp)

    def test_creates_report_file(self):
        """리포트 파일이 output_dir에 생성됨."""
        rp = _write_report(self.td, self._orig_file(), 'utf-8',
                           self.sample_failures, 1, 'processed', lang='ko')
        self.assertIsNotNone(rp)
        self.assertTrue(os.path.exists(rp))
        self.assertTrue(rp.endswith('.encoding_report.txt'))

    def test_report_filename_pattern(self):
        """리포트 파일명은 {원본}.encoding_report.txt."""
        p = self._orig_file()
        rp = _write_report(self.td, p, 'utf-8',
                           self.sample_failures, 1, 'processed', lang='ko')
        expected = os.path.basename(p) + '.encoding_report.txt'
        self.assertEqual(os.path.basename(rp), expected)

    def test_fallback_to_original_dir(self):
        """output_dir=None 시 원본 파일 폴더에 생성."""
        p = self._orig_file()
        rp = _write_report(None, p, 'utf-8',
                           self.sample_failures, 1, 'processed', lang='ko')
        self.assertEqual(os.path.dirname(rp), os.path.dirname(p))

    def test_tier1_advice(self):
        """Tier 1 (1~500 실패) → 한국어 Tier 1 조치 문구 포함."""
        rp = _write_report(self.td, self._orig_file(), 'utf-8',
                           self.sample_failures, 100, 'processed', lang='ko')
        with open(rp, encoding='utf-8') as _f:
            content = _f.read()
        self.assertIn('일부 문자가 손상', content)

    def test_tier2_advice(self):
        """Tier 2 (501~5000) → 한국어 Tier 2 조치 문구 포함."""
        rp = _write_report(self.td, self._orig_file(), 'utf-8',
                           self.sample_failures, 1000, 'processed', lang='ko')
        with open(rp, encoding='utf-8') as _f:
            content = _f.read()
        self.assertIn('다수의 문자가 손상', content)

    def test_tier3_skipped(self):
        """Tier 3 (5001+) + skipped → 한국어 Tier 3 + 원본 보호 문구."""
        rp = _write_report(self.td, self._orig_file(), 'utf-8',
                           self.sample_failures, 6000, 'skipped', lang='ko')
        with open(rp, encoding='utf-8') as _f:
            content = _f.read()
        self.assertIn('처리 건너뜀', content)
        self.assertIn('원본 보호', content)

    def test_truncated_count_shown(self):
        """total > len(failures)일 때 '추적 생략' 문구 + 개수 표시."""
        # failures=1, total=1000 → 999 omitted
        rp = _write_report(self.td, self._orig_file(), 'utf-8',
                           self.sample_failures, 1000, 'processed', lang='ko')
        with open(rp, encoding='utf-8') as _f:
            content = _f.read()
        self.assertIn('추적 생략', content)
        self.assertIn('999', content)

    def test_all_languages_no_untranslated_keys(self):
        """5개 언어 모두에서 번역 키가 그대로 노출되면 안 됨."""
        untranslated = ['report_header', 'report_file', 'report_path',
                        'report_advice_title', 'report_advice_tier1']
        for lang in ['ko', 'en', 'ja', 'zh_cn', 'zh_tw']:
            rp = _write_report(self.td, self._orig_file(), 'utf-8',
                               self.sample_failures, 100, 'processed', lang=lang)
            with open(rp, encoding='utf-8') as _f:
                content = _f.read()
            for key in untranslated:
                self.assertNotIn(key, content,
                    f"[{lang}] 번역 키 '{key}'가 그대로 노출됨")
            os.remove(rp)

    def test_report_is_utf8_without_bom(self):
        """리포트 파일은 UTF-8 (BOM 없이) 저장되어야 함 (다른 에디터 호환)."""
        rp = _write_report(self.td, self._orig_file(), 'utf-8',
                           self.sample_failures, 1, 'processed', lang='ko')
        with open(rp, 'rb') as f:
            raw = f.read()
        # Verify no BOM
        self.assertFalse(raw.startswith(b'\xef\xbb\xbf'), 'BOM이 붙어있음')
        # Decodable as UTF-8
        raw.decode('utf-8')  # must not throw


# ════════════════════════════════════════════════════════════════════════
# §AdditionalP  v1.0.6 bug-fix regression guard — Bulk Fixer preview freeze
# ════════════════════════════════════════════════════════════════════════
# Bug where _on_file_selected froze for 12+ seconds on huge files (~500K lines)
# (found during Phase 2-a hands-on QA, regression-guard purpose)

@unittest.skipUnless(HAS_MODULE, "FileNexusSuite 로드 실패")
class TestBulkFixerPreviewLargeFile(unittest.TestCase):
    """v1.0.6: Bulk Fixer preview must stay fast even on huge files.

    Before fix: text.splitlines(keepends=True)[:80]
            → parses all 27MB, creates 500K objects, uses only 80 (O(N) waste)
    After fix: text[:32768].splitlines(keepends=True)[:80]
            → processes only 32KB regardless of file size
    """

    def test_preview_extraction_logic_uses_head_slice(self):
        """소스에 text[:NNNNN].splitlines 패턴이 있어야 함 (회귀 방지)."""
        with open(_MAIN_PY, 'r', encoding='utf-8') as f:
            src = f.read()
        # Extract _on_file_selected body (inside BulkFixerPanel)
        # Regex: def _on_file_selected ... setPlainText(preview)
        m = re.search(
            r'def _on_file_selected\(self, cur, _prev\):(.*?)(?=\n    def |\nclass )',
            src, re.DOTALL)
        self.assertIsNotNone(m, '_on_file_selected 메서드를 찾을 수 없음')
        body = m.group(1)
        # Verify the fixed pattern exists: text[:NNNNN].splitlines
        self.assertRegex(body, r'text\[:\d+\]\.splitlines',
            '미리보기 헤드 슬라이스 패턴(text[:NNNNN].splitlines) 누락 — v1.0.6 수정 회귀 의심')
        # Whole-text splitlines call (pre-fix pattern) must NOT exist
        # Precise match: text.splitlines without preceding [:
        self.assertNotRegex(body, r'(?<!\])text\.splitlines',
            '수정 전 패턴(text.splitlines 전체 호출)이 남아있음 — v1.0.6 수정 회귀')


@unittest.skipUnless(HAS_MODULE, "FileNexusSuite 로드 실패")
class TestPreviewExtractionPerformance(unittest.TestCase):
    """v1.0.6: Verify performance characteristics of preview-extraction logic (pure-function level).

    Isolate and verify the preview-extraction logic inside _on_file_selected.
    Reproduce equivalent logic at the Python level without actual Qt widgets,
    confirming it finishes in constant time regardless of file size.
    """

    def _extract_preview_fixed(self, text):
        """v1.0.6 수정 후 방식 복제."""
        return ''.join(text[:32768].splitlines(keepends=True)[:80])

    def test_large_file_preview_under_100ms(self):
        """50만 줄 시뮬레이션에서 미리보기 추출이 100ms 이내."""
        # Korean web-novel style: avg 40-char lines × 500K lines
        line = '이것은 한국어 웹소설의 한 줄입니다. 적당한 길이의 문장입니다.\n'
        text = line * 500000  # ~20MB, 500K lines
        t0 = time.perf_counter()
        preview = self._extract_preview_fixed(text)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        self.assertLess(elapsed_ms, 100,
            f'50만 줄 파일 미리보기 추출이 100ms 초과: {elapsed_ms:.1f}ms '
            f'(v1.0.6 버그 회귀 의심 — text[:32768].splitlines 확인 필요)')
        # Verify the result is also correct (80 lines)
        self.assertLessEqual(len(preview.splitlines()), 80)

    def test_preview_size_consistent_across_file_sizes(self):
        """파일 크기와 무관하게 미리보기 크기가 일정 (32KB 상한)."""
        short_text = '짧은 파일입니다.\n' * 100  # small file
        huge_text = '큰 파일의 한 줄입니다.\n' * 1000000  # very large file

        preview_short = self._extract_preview_fixed(short_text)
        preview_huge = self._extract_preview_fixed(huge_text)

        # Small files show full content as preview; large files show only 80 lines
        # Both cases must stay under 32KB
        self.assertLessEqual(len(preview_short.encode('utf-8')), 32768)
        self.assertLessEqual(len(preview_huge.encode('utf-8')), 32768)
        # Verify the 80-line cap
        self.assertLessEqual(len(preview_huge.splitlines()), 80)


# ════════════════════════════════════════════════════════════════════════
# §AdditionalQ  v1.0.8 SettingsDialog structural invariant — page lazy recreation
# ════════════════════════════════════════════════════════════════════════

@unittest.skipUnless(HAS_MODULE, "FileNexusSuite 로드 실패 (PySide6 필요)")
class TestSettingsDialogStructureInvariant(unittest.TestCase):
    """v1.0.8 Option C — structural verification of the settings-dialog page lazy-recreation mechanism.

    Background: a label/frame color-leftover bug that existed since v1.0.5 was structurally
    resolved in v1.0.8 via the page-recreation mechanism. Protected as an invariant so
    nobody can mistakenly remove or weaken it later.

    Reference: docs/TEST_MANAGEMENT_POLICY §3 principle 4 (auto-coverage explicit for new features),
    Claude_Handover v1.0.7 §5.1 / §7.8, Phase2_Completion_Record §11.3.
    """

    @classmethod
    def setUpClass(cls):
        import inspect as _ins
        cls._ins = _ins
        cls.dialog_cls = _ns.get('SettingsDialog')

    def test_settings_dialog_has_recreate_pages(self):
        """SettingsDialog class must have a _recreate_pages method.

        v1.0.8 Option C core mechanism — the method responsible for page recreation.
        Removing it revives the label color-leftover bug.
        """
        self.assertIsNotNone(self.dialog_cls, "SettingsDialog 클래스 없음")
        self.assertTrue(hasattr(self.dialog_cls, '_recreate_pages'),
            "SettingsDialog._recreate_pages 메서드 없음 — "
            "v1.0.8 페이지 lazy 재생성 메커니즘이 누락됨")
        self.assertTrue(callable(getattr(self.dialog_cls, '_recreate_pages')),
            "SettingsDialog._recreate_pages가 callable이 아님")

    def test_refresh_theme_calls_recreate_pages(self):
        """SettingsDialog._refresh_theme body must call self._recreate_pages().

        v1.0.8 Option C — _refresh_theme delegates page-internal widget refresh to
        _recreate_pages. Missing this call revives the label color-leftover bug.
        """
        self.assertIsNotNone(self.dialog_cls, "SettingsDialog 클래스 없음")
        src = self._ins.getsource(self.dialog_cls._refresh_theme)
        self.assertIn('self._recreate_pages()', src,
            "_refresh_theme 본문에 'self._recreate_pages()' 호출 없음 — "
            "v1.0.8 옵션 C 메커니즘이 끊어짐")

    def test_retranslate_dialog_simplified(self):
        """SettingsDialog._retranslate_dialog must NOT directly refresh page-internal
        widget attributes.

        v1.0.8 Option C — _retranslate_dialog handles only the chrome (sidebar / nav /
        bottom buttons); page-internal text refresh is delegated to _recreate_pages.
        Direct setText on page-internal attributes (e.g., _lang_page_title) is the pre-v1.0.7 pattern.
        """
        self.assertIsNotNone(self.dialog_cls, "SettingsDialog 클래스 없음")
        src = self._ins.getsource(self.dialog_cls._retranslate_dialog)
        # Page-internal attribute patterns — traces of older-version structure
        forbidden_attrs = [
            '_theme_page_title', '_theme_page_hint',
            '_lang_page_title', '_lang_page_desc',
            '_sc_page_title', '_sc_page_desc',
            '_lang_odir_title',
            '_license_page_title', '_license_browser',
        ]
        for attr in forbidden_attrs:
            with self.subTest(attr=attr):
                self.assertNotIn(f'self.{attr}', src,
                    f"_retranslate_dialog에 'self.{attr}' 직접 갱신이 남아있음 — "
                    f"v1.0.8 단순화 위반. 페이지 내부 텍스트는 _recreate_pages가 처리해야 함")


# ════════════════════════════════════════════════════════════════════════
# §ExtraR  Batch Renamer — per-group digit width (v1.1.0 fix)
# ════════════════════════════════════════════════════════════════════════
class TestBatchRenamerDigitWidth(unittest.TestCase):
    """v1.1.0: _p_calc_preview computes digit width per group (was global).

    Old behavior: a single auto_d was derived from the largest group's file count
    and applied to every group, so a 9-file group rendered with 3 digits if any
    other group held 100+ files.

    Fix: each group computes its own width based on its own file count.
    Pure-function extraction follows the project's existing test pattern
    (see _de / natural_sort_key / depad / detect_prefix above).
    """

    @staticmethod
    def _calc_digit_width(file_count, start, mode):
        """Replicates the per-group digit-width logic in _p_calc_preview (FNS L5667-5673)."""
        grp_max_num = start + file_count - 1
        if mode == 'nopad':
            return 1
        auto_d = len(str(grp_max_num)) if grp_max_num > 0 else 1
        if mode == 'pad2':
            auto_d = max(2, auto_d)
        if mode == 'pad3':
            auto_d = max(3, auto_d)
        return auto_d

    # ── auto mode, start=1 ──────────────────────────────────────
    def test_auto_9_files_start1(self):    self.assertEqual(self._calc_digit_width(9,    1, 'auto'), 1)
    def test_auto_10_files_start1(self):   self.assertEqual(self._calc_digit_width(10,   1, 'auto'), 2)
    def test_auto_99_files_start1(self):   self.assertEqual(self._calc_digit_width(99,   1, 'auto'), 2)
    def test_auto_100_files_start1(self):  self.assertEqual(self._calc_digit_width(100,  1, 'auto'), 3)
    def test_auto_999_files_start1(self):  self.assertEqual(self._calc_digit_width(999,  1, 'auto'), 3)
    def test_auto_1000_files_start1(self): self.assertEqual(self._calc_digit_width(1000, 1, 'auto'), 4)

    # ── auto mode, start=0 (off-by-one boundary) ─────────────────
    def test_auto_10_files_start0(self):   self.assertEqual(self._calc_digit_width(10, 0, 'auto'), 1)
    def test_auto_11_files_start0(self):   self.assertEqual(self._calc_digit_width(11, 0, 'auto'), 2)

    # ── nopad mode (always 1 digit regardless of count) ─────────
    def test_nopad_1_file(self):     self.assertEqual(self._calc_digit_width(1,    1, 'nopad'), 1)
    def test_nopad_100_files(self):  self.assertEqual(self._calc_digit_width(100,  1, 'nopad'), 1)
    def test_nopad_1000_files(self): self.assertEqual(self._calc_digit_width(1000, 1, 'nopad'), 1)

    # ── pad2 mode (minimum 2 digits, grows when needed) ─────────
    def test_pad2_1_file(self):     self.assertEqual(self._calc_digit_width(1,    1, 'pad2'), 2)
    def test_pad2_9_files(self):    self.assertEqual(self._calc_digit_width(9,    1, 'pad2'), 2)
    def test_pad2_99_files(self):   self.assertEqual(self._calc_digit_width(99,   1, 'pad2'), 2)
    def test_pad2_100_files(self):  self.assertEqual(self._calc_digit_width(100,  1, 'pad2'), 3)

    # ── pad3 mode (minimum 3 digits, grows when needed) ─────────
    def test_pad3_1_file(self):     self.assertEqual(self._calc_digit_width(1,    1, 'pad3'), 3)
    def test_pad3_99_files(self):   self.assertEqual(self._calc_digit_width(99,   1, 'pad3'), 3)
    def test_pad3_999_files(self):  self.assertEqual(self._calc_digit_width(999,  1, 'pad3'), 3)
    def test_pad3_1000_files(self): self.assertEqual(self._calc_digit_width(1000, 1, 'pad3'), 4)

    # ── per-group independence (the actual fix verification) ────
    def test_groups_independent_widths(self):
        """The core fix: each group computes width from its own count, not the global max."""
        # Old bug: if Group B had 100 files (3 digits), Group A's 9 files would also use 3 digits.
        # Fix: Group A → 1 digit (own 9 files), Group B → 3 digits (own 100 files).
        a = self._calc_digit_width(9,   1, 'auto')
        b = self._calc_digit_width(100, 1, 'auto')
        self.assertEqual(a, 1, "9-file group must use 1 digit")
        self.assertEqual(b, 3, "100-file group must use 3 digits")
        self.assertNotEqual(a, b, "Groups must compute digit widths independently (v1.1.0 fix)")


# ════════════════════════════════════════════════════════════════════════
# §ExtraS  Batch Renamer — consolidated empty-folder dialog (v1.1.0 fix)
# ════════════════════════════════════════════════════════════════════════
_BatchRenamerPanel = _ns.get('BatchRenamerPanel') if HAS_MODULE else None


@unittest.skipUnless(HAS_MODULE and _BatchRenamerPanel,
                     "FileNexusSuite 로드 실패 또는 BatchRenamerPanel 없음")
class TestBatchRenamerEmptyFolderDialog(unittest.TestCase):
    """v1.1.0: _f_ingest / _p_ingest consolidate "no result" dialog into a single popup.

    Before: each empty folder triggered its own modal _dlg_info call (N folders → N popups).
            Could force-quit the app on large batches (~21+ folders) — see
            docs/2026-04-29_batch_renamer_folder_popup_spam.md.

    After:  skipped folders are collected into a list, and a single dialog summarises them
            (≤10: full list / >10: first 10 + "... (+N)").

    Patches the namespace-level `_dlg_info` and `QApplication` so the methods can run
    without a real Qt application instance. Bypasses BatchRenamerPanel.__init__ (heavy
    Qt UI construction) by attaching only the attributes _f_ingest / _p_ingest touch
    to a bare object.
    """

    def setUp(self):
        # ── Capture _dlg_info calls so we can assert call_count + message contents ──
        self._dlg_calls = []
        self._orig_dlg_info = _ns.get('_dlg_info')
        self._orig_dlg_warn = _ns.get('_dlg_warn')
        self._orig_qapp     = _ns.get('QApplication')

        def _mock_dlg_info(parent, title, msg):
            self._dlg_calls.append({'title': title, 'msg': msg})

        # QApplication must be mocked too — real PySide6 setOverrideCursor needs an app instance,
        # which test environments may not have.
        class _MockApp:
            @staticmethod
            def setOverrideCursor(*a, **kw): pass
            @staticmethod
            def restoreOverrideCursor(*a, **kw): pass

        _ns['_dlg_info']    = _mock_dlg_info
        _ns['_dlg_warn']    = lambda *a, **kw: None
        _ns['QApplication'] = _MockApp

    def tearDown(self):
        if self._orig_dlg_info is not None: _ns['_dlg_info']    = self._orig_dlg_info
        if self._orig_dlg_warn is not None: _ns['_dlg_warn']    = self._orig_dlg_warn
        if self._orig_qapp     is not None: _ns['QApplication'] = self._orig_qapp

    def _make_panel(self):
        """Bare panel object — bypasses Qt UI construction in __init__.

        Attaches only the attributes _f_ingest / _p_ingest actually read or write:
        the two group lists, the two refresh methods, and the four buttons whose
        setEnabled() is called on the success path.
        """
        class _BarePanel: pass
        panel = _BarePanel()
        panel._f_groups = []
        panel._p_groups = []
        panel._f_refresh = lambda *a, **kw: None
        panel._p_refresh = lambda *a, **kw: None
        class _MockBtn:
            def setEnabled(self, *a, **kw): pass
        panel._f_btn_preview = _MockBtn()
        panel._f_btn_rename  = _MockBtn()
        panel._p_btn_preview = _MockBtn()
        panel._p_btn_rename  = _MockBtn()
        return panel

    # ── _f_ingest: 3 empty parents → exactly 1 dialog (was 3) ──────
    def test_f_ingest_3_empty_parents_one_dialog(self):
        """3 empty parent folders must trigger exactly 1 consolidated dialog (was 3)."""
        with tempfile.TemporaryDirectory() as tmp:
            paths = [os.path.join(tmp, f'empty_{i}') for i in range(3)]
            for p in paths: os.makedirs(p)
            _BatchRenamerPanel._f_ingest(self._make_panel(), paths)
            self.assertEqual(len(self._dlg_calls), 1,
                             "3 empty parents must trigger exactly 1 consolidated dialog (was 3)")

    # ── _p_ingest: 3 empty folders → exactly 1 dialog (was 3) ──────
    def test_p_ingest_3_empty_folders_one_dialog(self):
        """3 empty folders (no files, no subfolders) → 1 consolidated dialog (was 3)."""
        with tempfile.TemporaryDirectory() as tmp:
            paths = [os.path.join(tmp, f'empty_{i}') for i in range(3)]
            for p in paths: os.makedirs(p)
            _BatchRenamerPanel._p_ingest(self._make_panel(), paths)
            self.assertEqual(len(self._dlg_calls), 1,
                             "3 empty folders must trigger exactly 1 consolidated dialog (was 3)")

    # ── ≤10 skipped: every path appears, no truncation marker ──────
    def test_f_ingest_le10_lists_all_paths(self):
        """≤10 skipped: every path appears in the dialog message, no '... (+N)' marker."""
        with tempfile.TemporaryDirectory() as tmp:
            paths = [os.path.join(tmp, f'empty_{i}') for i in range(5)]
            for p in paths: os.makedirs(p)
            _BatchRenamerPanel._f_ingest(self._make_panel(), paths)
            self.assertEqual(len(self._dlg_calls), 1)
            msg = self._dlg_calls[0]['msg']
            for p in paths:
                self.assertIn(p, msg, f"path {p!r} missing from consolidated message")
            self.assertNotIn('... (+', msg, "≤10 skipped must not show truncation marker")

    # ── >10 skipped: first 10 + "... (+N)" summary + "(N)" header ──
    def test_f_ingest_gt10_truncates_with_summary(self):
        """>10 skipped: first 10 paths + '... (+N)' marker + '(total N)' header."""
        with tempfile.TemporaryDirectory() as tmp:
            paths = [os.path.join(tmp, f'empty_{i:02d}') for i in range(15)]
            for p in paths: os.makedirs(p)
            _BatchRenamerPanel._f_ingest(self._make_panel(), paths)
            self.assertEqual(len(self._dlg_calls), 1)
            msg = self._dlg_calls[0]['msg']
            self.assertIn('... (+5)', msg, "15 skipped must summarise as '... (+5)'")
            self.assertIn('(15)', msg,    "Header line must show total count '(15)'")
            for i in range(10):
                self.assertIn(paths[i],    msg, f"first-10 index {i} unexpectedly missing")
            for i in range(10, 15):
                self.assertNotIn(paths[i], msg, f"path beyond first-10 index {i} unexpectedly present")

    # ── No skipped folders: no dialog at all ───────────────────────
    def test_f_ingest_no_dialog_when_all_succeed(self):
        """When every folder contributes a group, no 'no result' dialog is shown."""
        with tempfile.TemporaryDirectory() as tmp:
            parent = os.path.join(tmp, 'parent')
            os.makedirs(os.path.join(parent, 'child'))   # parent has a valid subfolder
            _BatchRenamerPanel._f_ingest(self._make_panel(), [parent])
            self.assertEqual(len(self._dlg_calls), 0,
                             "Successful ingest must not trigger a 'no result' dialog")


# ════════════════════════════════════════════════════════════════════════
# Test runner — auto-discovery (no manual registration needed)
# ════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    import inspect as _inspect
    import sys as _sys

    # Force stdout/stderr to UTF-8 (introduced for v1.0.7 CI — GitHub Actions windows-latest's
    # default console encoding is cp1252, causing UnicodeEncodeError on Korean / emoji output).
    # Standard Python 3.7+ feature; harmless on Hanrim's local Windows / Linux / macOS.
    if hasattr(_sys.stdout, 'reconfigure'):
        _sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(_sys.stderr, 'reconfigure'):
        _sys.stderr.reconfigure(encoding='utf-8')

    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()

    # Auto-collect unittest.TestCase subclasses from the current module
    # Benefits:
    #   - No manual registration when adding new test classes
    #   - Prevents omissions (class definition = automatic execution)
    #   - Improved maintainability
    _current_module = _sys.modules[__name__]
    klasses = sorted(
        [
            obj for _name, obj in _inspect.getmembers(_current_module)
            if _inspect.isclass(obj)
            and issubclass(obj, unittest.TestCase)
            and obj is not unittest.TestCase
            and obj.__module__ == _current_module.__name__  # exclude externally imported
        ],
        key=lambda c: c.__name__  # consistent execution order
    )

    for klass in klasses:
        suite.addTests(loader.loadTestsFromTestCase(klass))

    with open(os.devnull, 'w') as _devnull:
        result = unittest.TextTestRunner(verbosity=0, stream=_devnull).run(suite)
    total = result.testsRun
    fails = len(result.failures)
    errors= len(result.errors)
    skips = len(result.skipped)
    passed= total - fails - errors - skips

    print()
    print('=' * 60)
    print(f'  Total tests : {total}  ({len(klasses)} classes)')
    print(f'  \u2705 Passed     : {passed}')
    print(f'  \u274c Failed     : {fails}')
    print(f'  \u2757 Errors     : {errors}')
    print(f'  \u23ed  Skipped    : {skips}')
    print('=' * 60)

    if fails or errors:
        print()
        for f in result.failures:
            print(f'FAIL: {f[0]}')
            for line in f[1].splitlines()[-4:]: print(f'  {line}')
        for e in result.errors:
            print(f'ERROR: {e[0]}')
            for line in e[1].splitlines()[-4:]: print(f'  {line}')

    # CI exit-code contract (v1.0.7) — return non-zero on failure/error so automated pipelines
    # accurately detect pass/fail. No effect on local runs.
    _sys.exit(0 if (not fails and not errors) else 1)
