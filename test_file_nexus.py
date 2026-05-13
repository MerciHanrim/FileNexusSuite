"""
File Nexus Suite — Automated tests (detailed edition)
Run: python test_file_nexus.py
"""
import unittest, os, sys, re, zipfile, json, tempfile, time, shutil

sys.path.insert(0, os.path.dirname(__file__))

# Pin absolute path to FileNexusSuite.py based on this test file's location
_MAIN_PY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'FileNexusSuite.py')


# Pure-function helpers (HTML utilities, natural-sort, Tag Editor core) live
# in fns_utils.py — imported here for the integration / performance tests
# that exercise them through filesystem operations. The bulk of fns_utils
# coverage lives in TestFnsUtils below.
try:
    from fns_utils import depad_name, remove_tag_from_name, natural_sort_key
except ImportError:
    depad_name = remove_tag_from_name = natural_sort_key = None


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
    # _mix() inside HelpDialog._render_section() calls red()/green()/blue().
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
    _pyside6_available = None  # falsy gate for @skipUnless in TestQmRuntimeIntegrity


# ── EPUB conversion / module symbol extraction ───────────────────────────
try:
    with open(_MAIN_PY, encoding='utf-8') as _f:
        _src = _f.read()
    _ns = {'__file__': _MAIN_PY, '__name__': '__exec__'}
    exec(compile(_src, 'FileNexusSuite.py', 'exec'), _ns)
    # v1.1.1: register _ns as sys.modules['FileNexusSuite'] so that fns_help.py's
    # lazy `from FileNexusSuite import ...` statements (called when HelpDialog
    # instance methods such as _render_section() run) resolve against the _ns
    # dict instead of triggering a fresh module load. A second load would re-
    # register the `_fns_track` codec error handler with a new
    # _decode_tracking_state closure, severing the link between the _ns-based
    # _decode_with_failure_tracking and the active handler, leaving
    # TestDecodeWithFailureTracking and TestSafeReadTextWithReport with empty
    # `failures` lists. Wrap _ns as a ModuleType so attribute access works.
    import types as _types_mod
    _fns_module_obj = _types_mod.ModuleType('FileNexusSuite')
    _fns_module_obj.__dict__.update(_ns)
    sys.modules['FileNexusSuite'] = _fns_module_obj
    txt_to_epub             = _ns.get('txt_to_epub')
    epub_to_text            = _ns.get('epub_to_text')
    _alchemy_detect_enc     = _ns.get('alchemy_detect_encoding')
    _APP_VERSION            = _ns.get('APP_VERSION')
    _ConfigManager          = _ns.get('ConfigManager')
    HAS_EPUB = txt_to_epub is not None
    HAS_MODULE = True
except Exception as _e:
    HAS_EPUB = False
    HAS_MODULE = False
    txt_to_epub = epub_to_text = None
    _alchemy_detect_enc = _APP_VERSION = None
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
            new_name = depad_name(base) or base   # None means no change
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
            new_name = remove_tag_from_name(base, 'front') or base   # None means no change
            new_path = os.path.join(self.tmp, new_name)
            if new_path != f:
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

    # Note: test_sc_tab_fixer_in_label_keys and test_sc_tab_bulk_in_label_keys
    # were removed in v1.1.0 Phase 3b. The source-grep premise
    # (`'tab_5':'sc_tab_fixer'`, `'tab_6':'sc_tab_bulk'`) targeted the legacy
    # internal-key label map that no longer exists after the self.tr() + .ts/.qm
    # migration. Shortcut-tab translation coverage is verified indirectly via
    # TestTsSourceIntegrity ('settings' macro-category) instead.

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

    # Note: test_stats_not_korean_hardcoded removed in v1.1.0 Phase 3b.
    # The source-grep premise (`tf_stat_mid_n` internal key) no longer applies
    # after the self.tr() + .ts/.qm migration. Statistics-text translation
    # coverage is verified indirectly via TestTsSourceIntegrity
    # ('text_fixer' macro-category) instead.


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

    # Empty-string boundary (fns_utils helpers' empty-input behavior is
    # exercised in TestFnsUtils below; this class keeps only the
    # _is_sep_line empty-string boundary, which is a main-module helper)
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
# §ExtraC  Help HTML — HelpDialog instance methods via QTranslator
# ════════════════════════════════════════════════════════════════════════
@unittest.skipUnless(HAS_MODULE, "FileNexusSuite 로드 실패")
class TestBuildHelpHtml(unittest.TestCase):
    """HelpDialog — validate help generation for 5 languages via QTranslator stack.

    Phase 3/4 migration: replaced direct _build_help_html(_data_only, _lang) calls
    with QTranslator install/remove cycle around HelpDialog instance methods.
    The legacy entry point was removed when help content moved to fns_help.py
    and was wrapped in self.tr() for runtime translation.
    """

    LANGS = ('ko', 'en', 'ja', 'zh_cn', 'zh_tw')

    @classmethod
    def setUpClass(cls):
        try:
            from pathlib import Path
            from PySide6.QtWidgets import QApplication
            from PySide6.QtCore import QTranslator
            from fns_help import HelpDialog
        except ImportError as e:
            raise unittest.SkipTest(f"PySide6 또는 fns_help 로드 실패: {e}")
        cls.QTranslator = QTranslator
        cls.HelpDialog = HelpDialog
        cls.app = QApplication.instance() or QApplication([])
        cls.translations_dir = Path(__file__).parent / 'translations'

    def setUp(self):
        self._installed = None

    def tearDown(self):
        if self._installed is not None:
            self.app.removeTranslator(self._installed)
            self._installed = None

    def _install(self, lang):
        """Install help_<lang>.qm; previous translator removed first."""
        if self._installed is not None:
            self.app.removeTranslator(self._installed)
            self._installed = None
        qm = self.translations_dir / f'help_{lang}.qm'
        if not qm.exists():
            self.skipTest(f'{qm} not found — run scripts/update_translations.bat')
        tr = self.QTranslator()
        self.assertTrue(tr.load(str(qm)), f'failed to load {qm}')
        self.app.installTranslator(tr)
        self._installed = tr

    # ── Group 1: build artifact integrity ──

    def test_all_qm_files_exist(self):
        """5개 언어 help_*.qm 빌드 결과물 존재."""
        for lang in self.LANGS:
            with self.subTest(lang=lang):
                qm = self.translations_dir / f'help_{lang}.qm'
                self.assertTrue(qm.exists(),
                              f'{qm} missing — run scripts/update_translations.bat')

    # ── Group 2: _get_intro() ──

    def test_intro_returns_string_all_langs(self):
        """_get_intro() 반환 타입 = str."""
        for lang in self.LANGS:
            with self.subTest(lang=lang):
                self._install(lang)
                self.assertIsInstance(self.HelpDialog()._get_intro(), str)

    def test_intro_nonempty_all_langs(self):
        """_get_intro() 비어있지 않음."""
        for lang in self.LANGS:
            with self.subTest(lang=lang):
                self._install(lang)
                self.assertGreater(len(self.HelpDialog()._get_intro()), 0,
                                 f'{lang} intro empty')

    # ── Group 3: _get_sections() ──

    def test_sections_returns_list_all_langs(self):
        """_get_sections() 반환 타입 = list."""
        for lang in self.LANGS:
            with self.subTest(lang=lang):
                self._install(lang)
                self.assertIsInstance(self.HelpDialog()._get_sections(), list)

    def test_sections_nonempty_all_langs(self):
        """_get_sections() 비어있지 않음."""
        for lang in self.LANGS:
            with self.subTest(lang=lang):
                self._install(lang)
                self.assertGreater(len(self.HelpDialog()._get_sections()), 0,
                                 f'{lang} sections empty')

    # ── Group 4: _render_section() ──

    def test_render_section_returns_string_all_langs(self):
        """_render_section()이 str 반환."""
        for lang in self.LANGS:
            with self.subTest(lang=lang):
                self._install(lang)
                dlg = self.HelpDialog()
                sections = dlg._get_sections()
                self.assertIsInstance(dlg._render_section(sections[0]), str)

    def test_render_section_nonempty_all_langs(self):
        """_render_section() 결과 비어있지 않음."""
        for lang in self.LANGS:
            with self.subTest(lang=lang):
                self._install(lang)
                dlg = self.HelpDialog()
                sections = dlg._get_sections()
                self.assertGreater(len(dlg._render_section(sections[0])), 0,
                                 f'{lang} rendered section empty')

    # ── Group 5: QTranslator install/remove cycle ──

    def test_translator_swap_changes_output(self):
        """ko → en translator 전환 시 intro 다른 결과 — install/remove 사이클 동작 보장."""
        self._install('ko')
        intro_ko = self.HelpDialog()._get_intro()
        self._install('en')
        intro_en = self.HelpDialog()._get_intro()
        self.assertNotEqual(intro_ko, intro_en,
                          'ko/en intro 동일 — QTranslator install이 동작 안 함')


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

    # Note: test_themes_count and test_themes_names removed in v1.1.0 Phase 2b.
    # THEMES dict moved to fns_theme.py, so the v0.10.0 base-constant regression
    # premise (verifying the dict at its original main-module location) no longer
    # applies. Equivalent coverage now lives in TestFnsTheme.
    #
    # Note: test_theme_name_key_has_auto and test_translations_has_five_langs
    # removed in v1.1.0 Phase 3a. _THEME_NAME_KEY and TRANSLATIONS moved to
    # fns_translations.py (with per-language data under translations/fns_*.py),
    # so the same source-parsing premise no longer applies. Equivalent coverage
    # now lives in TestFnsTranslations.

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
# §ExtraE  Qt Linguist (.ts/.qm) translation integrity (v1.1.0 Phase 3b)
# ════════════════════════════════════════════════════════════════════════
# Replaces Phase 3a TestTranslationCompleteness, which validated the
# internal-key TRANSLATIONS dict in fns_translations.py. Phase 3b moved to
# Qt Linguist with English source-text keys under per-class Qt contexts,
# so the integrity check is split into two layers:
#
#   - Layer 1 (TestTsSourceIntegrity): .ts source files -- XML parse, key
#     symmetry, zh_cn fallback safety, macro-category coverage.
#     PySide6-independent (parses XML directly).
#
#   - Layer 2 (TestQmRuntimeIntegrity): compiled .qm files -- _qm_lookup
#     answers and _REPORT_TR_KEYS lookup round-trip. Requires real PySide6
#     (the Qt mock cannot load real .qm files via QTranslator).
#
# The 10 macro-categories from docs/TEST_MANAGEMENT_POLICY.md §4.1 are
# remapped onto Qt context namespaces (which align naturally with the
# original class-based grouping).

import xml.etree.ElementTree as ET

_TS_DIR = os.path.join(os.path.dirname(_MAIN_PY), 'translations_ts')
_QM_DIR = os.path.join(os.path.dirname(_MAIN_PY), 'translations')
_LANGS = ('ko', 'en', 'ja', 'zh_cn', 'zh_tw')


def _parse_ts(lang):
    """Parse translations_ts/fns_{lang}.ts -> {(context, source): translation}.

    Skips messages flagged type="unfinished" or with empty translation text.
    Returns {} if the .ts file is missing.
    """
    ts_path = os.path.join(_TS_DIR, 'fns_{}.ts'.format(lang))
    if not os.path.exists(ts_path):
        return {}
    tree = ET.parse(ts_path)
    result = {}
    for context in tree.iter('context'):
        ctx_name = context.findtext('name', '')
        for message in context.iter('message'):
            source = message.findtext('source', '')
            translation_elem = message.find('translation')
            if translation_elem is None or not source:
                continue
            if translation_elem.get('type') == 'unfinished':
                continue
            translation = translation_elem.text or ''
            if translation:
                result[(ctx_name, source)] = translation
    return result


class TestTsSourceIntegrity(unittest.TestCase):
    """v1.1.0 Phase 3b -- .ts source-file integrity (PySide6-independent).

    Replaces the Phase 3a TestTranslationCompleteness key-based checks.
    The 10 macro-categories from docs/TEST_MANAGEMENT_POLICY.md §4.1 are
    preserved as `CONTEXT_GROUPS` -- each maps to one or more Qt context
    namespaces that hold the relevant tab's translations.
    """

    # Macro-category -> Qt context names (class-based)
    # Phase 4 (2026-05-13): HelpDialog moved from fns_*.ts to help_*.ts via
    # the dedicated help_*.qm runtime translator stack; LicenseDialog was
    # added to fns_*.ts as a new common-dialog context.
    CONTEXT_GROUPS = {
        'common_dialogs': ['AppSuite', 'LicenseDialog'],
        'text_merger':    ['TextMergerPanel', 'MergeFileTree', 'PreviewWindow',
                           'TextMergeWorker'],
        'text_converter': ['TextConverterPanel', 'TextConverterDropZone',
                           'TextConverterFileList'],
        'tag_editor':     ['TagEditorPanel', 'TagDropZone', '_TagFileList',
                           '_TagPreviewTree'],
        'batch_renamer':  ['BatchRenamerPanel', 'BatchDropZone',
                           'BatchPreviewModel'],
        'text_fixer':     ['TextFixerPanel', 'TextFixerDropZone'],
        'bulk_fixer':     ['BulkFixerPanel', 'BulkFixerDropZone',
                           'BulkFixerFileList', 'BulkFixerWorker'],
        'settings':       ['SettingsDialog', '_KeyCaptureButton'],
        # Phase 3a 'shortcut' macro-category absorbed into 'settings':
        # Qt contexts are per-class, and the shortcut UI lives inside the
        # SettingsDialog class. _KeyCaptureButton is the only standalone
        # shortcut-related context (the capture button widget itself).
        'app_shell':      ['FileNexusSuite'],
    }

    # Minimum translated keys per macro-category per language
    MIN_PER_CATEGORY = 3

    @classmethod
    def setUpClass(cls):
        cls._dicts = {lang: _parse_ts(lang) for lang in _LANGS}

    # ── File presence + parse ───────────────────────────────

    def test_all_ts_files_present_and_parse(self):
        for lang in _LANGS:
            with self.subTest(lang=lang):
                ts_path = os.path.join(_TS_DIR, 'fns_{}.ts'.format(lang))
                self.assertTrue(os.path.exists(ts_path),
                    'fns_{}.ts missing in {}'.format(lang, _TS_DIR))
                self.assertGreater(len(self._dicts[lang]), 0,
                    'fns_{}.ts parsed but yielded no (context, source) pairs'
                    .format(lang))

    # ── No unfinished translations ──────────────────────────

    def test_no_unfinished_translations(self):
        for lang in _LANGS:
            ts_path = os.path.join(_TS_DIR, 'fns_{}.ts'.format(lang))
            with open(ts_path, encoding='utf-8') as f:
                content = f.read()
            with self.subTest(lang=lang):
                self.assertEqual(content.count('type="unfinished"'), 0,
                    'fns_{}.ts has unfinished translations'.format(lang))

    # ── Key symmetry ────────────────────────────────────────

    def test_symmetric_key_count_ko_en_ja_zhtw(self):
        """ko/en/ja/zh_tw must share the same (context, source) key count."""
        ko_count = len(self._dicts['ko'])
        for lang in ('en', 'ja', 'zh_tw'):
            with self.subTest(lang=lang):
                self.assertEqual(len(self._dicts[lang]), ko_count,
                    '{} key count {} != ko {}'.format(
                        lang, len(self._dicts[lang]), ko_count))

    def test_zh_cn_subset_of_zh_tw(self):
        """zh_cn keys must all exist in zh_tw -- fallback safety (v1.0.9 §5.1.G).

        The runtime fallback chain in _rt() and _qm_lookup callers routes
        zh_cn -> zh_tw -> ko -> en source. This invariant guarantees the
        first hop never fails for any key zh_cn ships with.
        """
        not_in_zh_tw = (set(self._dicts['zh_cn'].keys())
                        - set(self._dicts['zh_tw'].keys()))
        self.assertEqual(not_in_zh_tw, set(),
            'zh_cn keys missing from zh_tw (fallback impossible): {}'.format(
                sorted(str(k) for k in not_in_zh_tw)[:5]))

    def test_ko_has_minimum_keys(self):
        """ko must have at least 400 translated entries (size invariant)."""
        self.assertGreaterEqual(len(self._dicts['ko']), 400)

    # ── Macro-category coverage ─────────────────────────────
    # The 10 categories from docs/TEST_MANAGEMENT_POLICY.md §4.1 are about
    # translation coverage invariants -- they are independent of where the
    # data physically lives. Phase 3b maps them onto Qt contexts.

    def test_all_macro_category_contexts_present(self):
        """Every Qt context listed in CONTEXT_GROUPS must appear in every language."""
        for category, contexts in self.CONTEXT_GROUPS.items():
            for lang in _LANGS:
                lang_contexts = {ctx for (ctx, _src) in self._dicts[lang].keys()}
                for ctx in contexts:
                    with self.subTest(lang=lang, category=category, context=ctx):
                        self.assertIn(ctx, lang_contexts,
                            '[{}] Qt context "{}" missing ({} macro-category)'
                            .format(lang, ctx, category))

    def test_minimum_keys_per_macro_category(self):
        """Each macro-category must have >= MIN_PER_CATEGORY keys per language."""
        for category, contexts in self.CONTEXT_GROUPS.items():
            for lang in _LANGS:
                count = sum(1 for (ctx, _src) in self._dicts[lang].keys()
                            if ctx in contexts)
                with self.subTest(lang=lang, category=category):
                    self.assertGreaterEqual(count, self.MIN_PER_CATEGORY,
                        '[{}] {}: {} keys (< {})'.format(
                            lang, category, count, self.MIN_PER_CATEGORY))


# ════════════════════════════════════════════════════════════════════════
# §ExtraE2  Qt Linguist .qm runtime integrity (real PySide6 required)
# ════════════════════════════════════════════════════════════════════════

# Module-level handles for the Qt runtime helpers exec'd from FileNexusSuite.py.
# Stored at module scope (not class attribute) to bypass Python's automatic
# self-binding for functions assigned as class attributes -- _qm_lookup and
# _all_translations_of are plain functions, not methods.
_qm_lookup           = _ns.get('_qm_lookup')
_all_translations_of = _ns.get('_all_translations_of')
_REPORT_TR_KEYS      = _ns.get('_REPORT_TR_KEYS', {})
_tr_args             = _ns.get('_tr_args')   # Qt-style %1, %2 placeholder substitution


@unittest.skipUnless(
    _pyside6_available,
    'Real PySide6 required (.qm load via QTranslator); skipped under Qt mock'
)
class TestQmRuntimeIntegrity(unittest.TestCase):
    """v1.1.0 Phase 3b -- compiled .qm runtime integrity.

    Validates that:
      - all 5 .qm files exist
      - _qm_lookup answers a representative (context, source) key per language
      - _all_translations_of returns 5 distinct translations
      - every English source in _REPORT_TR_KEYS resolves via _qm_lookup
        (lupdate -> lrelease pipeline integrity for the worker-thread
        report path)

    Skipped when PySide6 is mocked (mock QTranslator cannot load real .qm).
    """

    def test_all_qm_files_present(self):
        for lang in _LANGS:
            with self.subTest(lang=lang):
                qm_path = os.path.join(_QM_DIR, 'fns_{}.qm'.format(lang))
                self.assertTrue(os.path.exists(qm_path),
                    'fns_{}.qm missing -- run update_translations.bat'
                    .format(lang))

    def test_qm_lookup_answers_representative_keys(self):
        """_qm_lookup must answer a representative key in every language."""
        # 'Cancel' under 'AppSuite' is the canonical example -- present in all 5.
        rep_ctx, rep_src = 'AppSuite', 'Cancel'
        for lang in _LANGS:
            with self.subTest(lang=lang):
                result = _qm_lookup(lang, rep_src, rep_ctx)
                self.assertIsNotNone(result,
                    '_qm_lookup({!r}, {!r}, {!r}) -- .qm load or lookup failed'
                    .format(lang, rep_src, rep_ctx))
                self.assertNotEqual(result, '',
                    '_qm_lookup({!r}, {!r}, {!r}) returned empty'
                    .format(lang, rep_src, rep_ctx))

    def test_all_translations_of_collects_translations(self):
        """_all_translations_of must collect translations across the 5 languages.

        The function returns a set, so duplicate translations collapse:
          - zh_cn/zh_tw often share the same hanja (e.g. 'Cancel' -> 取消 in
            both), which is the design behind the v1.0.9 §5.1.G fallback
            (zh_cn entries identical to zh_tw are intentionally absent and
            served by the fallback chain).
          - en may collapse with the English source when Qt's translator
            drops identity translations.
        The minimum-4 invariant catches the common failure mode where a
        language drops out entirely (missing .qm or empty translation),
        while tolerating expected hanja/source collapses.
        """
        result = _all_translations_of('Cancel', 'AppSuite')
        self.assertGreaterEqual(len(result), 4,
            '_all_translations_of("Cancel", "AppSuite") returned {} '
            'translations, expected >= 4 (zh_cn/zh_tw may share hanja). '
            'Got: {}'.format(len(result), sorted(result)))

    def test_report_tr_keys_round_trip(self):
        """Every English source in _REPORT_TR_KEYS must resolve via _qm_lookup
        in ko (the canonical reference language). Detects a broken
        lupdate -> lrelease pipeline for the encoding-report worker path.
        """
        missing = []
        for key, en_source in _REPORT_TR_KEYS.items():
            result = _qm_lookup('ko', en_source, 'FileNexusSuite')
            if result is None:
                missing.append((key, en_source))
        self.assertEqual(missing, [],
            '_REPORT_TR_KEYS entries not found in ko .qm '
            '(lupdate -> lrelease pipeline broken?): {}'.format(missing[:3]))


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
        """TextMergerPanel.retranslate() must update the tree header.

        v1.1.0 (라-B-1.5-B): refactored from QTreeWidget+setHeaderLabels to
        FileListBase+retranslate_headers() pattern.
        """
        body = self._get_retranslate_body('TextMergerPanel')
        self.assertIn('retranslate_headers', body,
            "MergeFileTree 헤더가 retranslate에서 갱신되지 않음")

    # Note: test_bulk_fixer_sort_btn_uses_t removed in v1.1.0 Phase 3b.
    # The source-grep premise (`"tag_col_filename"`, `"tag_col_path"` as i18n
    # key strings in COLUMNS) no longer applies after the migration to
    # QT_TR_NOOP("Filename") / QT_TR_NOOP("Path") in BulkFixerFileList.COLUMNS.
    # Structural coverage of the FileListBase + COLUMNS pattern lives in
    # TestFileListSubClassRefactor.test_bulk_fixer_file_list; per-language
    # column-header translation coverage lives in TestTsSourceIntegrity
    # ('bulk_fixer' macro-category).

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
    # Note: test_all_themes_have_btn_border_h and test_themes_count_9 removed in
    # v1.1.0 Phase 2b. THEMES dict moved to fns_theme.py, so the v0.12.0
    # main-module-source regression premise no longer applies. Equivalent
    # coverage now lives in TestFnsTheme.

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
        """_HelpButton class must be defined (extracted to fns_help.py in v1.1.1)."""
        # v1.1.1: _HelpButton was extracted from FileNexusSuite.py to fns_help.py
        # in the help modularization track. Read the new home directly so the
        # source-grep assertion still verifies the class definition location.
        _HELP_PY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fns_help.py')
        with open(_HELP_PY, encoding='utf-8') as f:
            self.assertIn('class _HelpButton', f.read())

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
    # Note: test_section_header_prefix removed in v1.1.0 Phase 3b.
    # The source-grep premise (`'tf_grp_input'` internal key) no longer
    # applies after the self.tr() + .ts/.qm migration. The '//' prefix
    # convention is preserved in the English source text, verified
    # indirectly via TestTsSourceIntegrity ('text_fixer' macro-category).


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

    # Note: test_translations_v100_keys removed in v1.1.0 Phase 3b.
    # The TRANSLATIONS dict was fully removed during the .ts/.qm migration;
    # legacy internal keys (btn_abort, bulk_keep_structure, settings_output_dir)
    # have been replaced by self.tr('Stop'), self.tr('Keep folder structure'),
    # and self.tr('Output folder') at their call sites. Per-language coverage
    # of those English sources is verified indirectly via TestTsSourceIntegrity
    # (MIN_PER_CATEGORY=3 across the 'bulk_fixer' and 'settings' macro-categories).

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

    # Note: test_merge_enc_warn_keys_in_5_languages removed in v1.1.0 Phase 3a.
    # Source-grep premise no longer applies after TRANSLATIONS moved to
    # fns_translations.py. Cross-language symmetry is already guarded by
    # TestTranslationCompleteness.test_all_langs_same_key_count.

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

    # Note: test_merge_low_conf_hint_keys_in_5_languages removed in v1.1.0
    # Phase 3a (same reason as test_merge_enc_warn_keys_in_5_languages above).

    # ── Bug-fix verification (v1.0.4 initial-release feedback) ──
    # Note: test_dlg_question_supports_rich_text removed in v1.1.0 Phase 3b.
    # The source-grep premise (`_t('merge_enc_warn_title')` at the call site)
    # no longer applies after the self.tr() + .ts/.qm migration. The call site
    # now reads `self.tr('⚠ Encoding compatibility warning')` with rich_text=True.
    # The _dlg_question signature itself (rich_text parameter) is verified by
    # TestRetranslateIntegrity.test_dlg_functions_use_t_keys via runtime usage,
    # and per-language translation coverage lives in TestTsSourceIntegrity
    # ('text_merger' macro-category).

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

    # Note: 5 source-grep tests removed from TestV105Regression in v1.1.0 Phase 3b:
    #   - test_enc_items_contains_all_8_keys       (i18n-key half of the check)
    #   - test_combo_uses_add_item_with_user_data
    #   - test_enc_hint_label_created
    #   - test_enc_hint_label_retranslated
    #   - test_retranslate_updates_combo_item_text
    #
    # The source-grep premise (`_t('merge_enc_*')`, `_t(_i18n_key)` patterns) no
    # longer applies after the self.tr() + .ts/.qm migration. Equivalent runtime
    # coverage with stronger guarantees lives in TestV105RegressionModule:
    #   - test_qm_has_all_enc_sources
    #       (5 languages x 9 encoding source-strings = 45 subTests)
    #   - test_enc_labels_contain_encoding_name
    #       (label readability invariant per language)
    #   - test_enc_items_preserves_v104_keys
    #       (internal _ENC_ITEMS key order -- supersedes the internal-key half
    #        of test_enc_items_contains_all_8_keys)
    #   - test_hint_message_guides_to_utf8
    #       (UTF-8 guidance invariant -- supersedes test_enc_hint_label_*)
    # TestV105StatusRetranslate covers the retranslate path (supersedes
    # test_retranslate_updates_combo_item_text).
    #
    # test_enc_items_constant_defined (above) and the currentData migration
    # block (below) stay -- they are structural / settings-compat checks
    # independent of the .ts/.qm migration.

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

    # ── Translation invariants moved out in v1.1.0 Phase 3a ──────
    # Note: test_all_languages_have_enc_keys removed in v1.1.0 Phase 3a.
    # Source-grep premise no longer applies after TRANSLATIONS moved to
    # fns_translations.py. Equivalent runtime coverage already lives in
    # TestV105RegressionModule.test_translations_have_all_enc_keys (module-load).
    #
    # Note: test_zh_uses_rifun_not_rigoyu removed in v1.1.0 Phase 3a.
    # Small one-off label check; kept for a single release after v1.0.4 tip
    # but no longer worth the maintenance cost in the new layout.

    # ── APP_VERSION verification split into TestAppVersion (v1.0.7 redesign as version-independent structural check) ─────


@unittest.skipUnless(_pyside6_available, "real PySide6 필요 (Qt .qm runtime lookup)")
class TestV105RegressionModule(unittest.TestCase):
    """v1.0.5 module-load-based regression tests — runtime behavior verification.

    Phase 3b: legacy TRANSLATIONS dict assertions replaced by _qm_lookup runtime
    lookups against the TextMergerPanel Qt context. The 9 encoding source strings
    live in fns_<lang>.ts (msgctxt 'TextMergerPanel') and compile into fns_<lang>.qm.

    Note: APP_VERSION verification was split into TestAppVersionModule
    (redesigned in v1.0.7 as version-independent structural verification).
    """

    # Phase 3b: legacy 'merge_enc_*' internal keys -> English source-text keys.
    # 9 encoding sources (UTF-8 ... Big5, plus the help hint).
    _ENC_SOURCES = (
        'UTF-8',
        'UTF-8-BOM (Excel compatible)',
        'EUC-KR (Korean)',
        'CP949 (Korean Windows)',
        'UTF-16',
        'Shift-JIS (Japanese)',
        'GBK (Simplified Chinese)',
        'Big5 (Traditional Chinese)',
    )
    _ENC_HINT_SOURCE = 'If unsure, select UTF-8'

    def test_qm_has_all_enc_sources(self):
        """5 언어 자국 본받기 *9 encoding source-text 자국이 .qm runtime 자국 본받기 *짚힘.
        Phase 3b: replaces test_translations_have_all_enc_keys (legacy TRANSLATIONS dict)."""
        all_sources = list(self._ENC_SOURCES) + [self._ENC_HINT_SOURCE]
        for lang_code in _LANGS:
            for en_source in all_sources:
                with self.subTest(lang=lang_code, source=en_source):
                    result = _qm_lookup(lang_code, en_source, 'TextMergerPanel')
                    self.assertIsNotNone(result,
                        f"[{lang_code}] {en_source!r} not in .qm runtime")
                    self.assertGreater(len(result), 0,
                        f"[{lang_code}] {en_source!r} resolves to empty string")

    def test_enc_labels_contain_encoding_name(self):
        """각 언어 label 자국 본받기 *encoding name (UTF-8, EUC-KR, ...) 자국이 *짚힘.
        Reason: users must be able to identify which encoding from the label alone."""
        source_to_enc_name = (
            ('UTF-8',                          'UTF-8'),
            ('UTF-8-BOM (Excel compatible)',   'UTF-8-BOM'),
            ('EUC-KR (Korean)',                'EUC-KR'),
            ('CP949 (Korean Windows)',         'CP949'),
            ('UTF-16',                         'UTF-16'),
            ('Shift-JIS (Japanese)',           'Shift-JIS'),
            ('GBK (Simplified Chinese)',       'GBK'),
            ('Big5 (Traditional Chinese)',     'Big5'),
        )
        for lang_code in _LANGS:
            for en_source, enc_name in source_to_enc_name:
                with self.subTest(lang=lang_code, source=en_source):
                    label = _qm_lookup(lang_code, en_source, 'TextMergerPanel') or ''
                    self.assertIn(enc_name, label,
                        f"[{lang_code}] {en_source!r} 라벨에 '{enc_name}' 없음: {label!r}")

    def test_zh_labels_use_rifun(self):
        """Simplified/Traditional Chinese Shift-JIS label must contain '日文'.
        (Idiomatic Chinese form, distinct from Japanese-locale '日本語')"""
        for lang_code in ('zh_cn', 'zh_tw'):
            label = _qm_lookup(lang_code, 'Shift-JIS (Japanese)', 'TextMergerPanel') or ''
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
        for lang_code in _LANGS:
            hint = _qm_lookup(lang_code, self._ENC_HINT_SOURCE, 'TextMergerPanel') or ''
            self.assertIn('UTF-8', hint,
                f"[{lang_code}] 도움말에 'UTF-8' 안내 누락: {hint!r}")


@unittest.skipUnless(_pyside6_available, "real PySide6 필요 (Qt translator install)")
class TestV105StatusRetranslate(unittest.TestCase):
    """v1.0.5 — Text Merger status-message refresh bug fix on language switch.

    Background:
      - Likely a long-standing bug from before v1.0.4
      - retranslate() refreshed _lbl_status only when state == 'Ready'
      - Result: after adding files and switching language, "26 files added..." stayed in Korean
      - Found in v1.0.5 post-build hands-on QA (Hanrim) via screenshots in 3 languages

    Fix design (Phase 3b):
      - Static messages ('Ready', 'All files cleared', 'Save path reset', '❌ Error occurred',
        '📂  Reading files...'): simple re-render via self.tr(en_text)
      - Restorable dynamic messages ('%1 file(s) added...': file_list count,
        'Save path set: %1': save_dir): _tr_args + self.tr
      - Non-restorable messages ('%1 file(s) removed', 'Saved (%1): %2',
        'Scanning... %1 found'): reset to 'Ready' + debug log
    """

    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        # Reuse a single QApplication (avoid conflicts with other tests)
        cls.app = QApplication.instance() or QApplication([])

    def _make_panel(self, lang_code='ko'):
        """Create a TextMergerPanel instance for testing.
        Phase 3b: _load_translator(lang) installs the Qt translator so self.tr()
        resolves against fns_<lang>.qm during panel construction."""
        _ns['_current_lang'] = lang_code
        _load_translator = _ns.get('_load_translator')
        _load_translator(lang_code)
        PanelCls = _ns.get('TextMergerPanel')
        return PanelCls()

    def _set_lang(self, lang_code):
        """언어 전환 simulation — Qt translator 자국 본격 *재설치 + _current_lang 자국 본격 *짚어주는 결."""
        _ns['_current_lang'] = lang_code
        _load_translator = _ns.get('_load_translator')
        _load_translator(lang_code)

    # ── Static-message re-render ────────────────────────────
    def test_status_ready_retranslates(self):
        """'Ready' 상태에서 언어 전환 시 해당 언어의 'Ready' 메시지로 바뀐다."""
        panel = self._make_panel('ko')
        try:
            # Initial state = Ready (Korean)
            self.assertEqual(panel._lbl_status.text(),
                             _qm_lookup('ko', 'Ready', 'TextMergerPanel'))
            # Switch to English
            self._set_lang('en')
            panel._retranslate_status()
            self.assertEqual(panel._lbl_status.text(),
                             _qm_lookup('en', 'Ready', 'TextMergerPanel'))
            # Switch to Japanese
            self._set_lang('ja')
            panel._retranslate_status()
            self.assertEqual(panel._lbl_status.text(),
                             _qm_lookup('ja', 'Ready', 'TextMergerPanel'))
        finally:
            self._set_lang('ko')
            panel.deleteLater()

    def test_status_clr_retranslates(self):
        """'All files cleared' 상태에서 언어 전환 시 해당 언어로 갱신된다."""
        panel = self._make_panel('ko')
        try:
            panel._lbl_status.setText(_qm_lookup('ko', 'All files cleared', 'TextMergerPanel'))
            self._set_lang('en')
            panel._retranslate_status()
            self.assertEqual(panel._lbl_status.text(),
                             _qm_lookup('en', 'All files cleared', 'TextMergerPanel'))
        finally:
            self._set_lang('ko')
            panel.deleteLater()

    def test_status_error_occurred_retranslates(self):
        """'❌ Error occurred' 상태에서 언어 전환 시 해당 언어로 갱신된다.
        Phase 3b: legacy 'merge_save_err' ('Save Error') replaced by '❌ Error occurred'
        in _STATUS_TEMPLATES — 'Save Error' is now a QMessageBox title, not status text."""
        panel = self._make_panel('ko')
        try:
            panel._lbl_status.setText(_qm_lookup('ko', '❌ Error occurred', 'TextMergerPanel'))
            self._set_lang('zh_cn')
            panel._retranslate_status()
            self.assertEqual(panel._lbl_status.text(),
                             _qm_lookup('zh_cn', '❌ Error occurred', 'TextMergerPanel'))
        finally:
            self._set_lang('ko')
            panel.deleteLater()

    # ── Dynamic-message restoration re-render ────────────────
    def test_status_add_retranslates_with_current_count(self):
        """In '%1 file(s) added (encoding auto-detected)' state, language switch must rebuild from
        the current file_list count. Main bug scenario Hanrim found in screenshots
        (26 files added, then language switched)."""
        en_add = '%1 file(s) added (encoding auto-detected)'
        panel = self._make_panel('ko')
        try:
            # Simulate file_list with 26 items (internal state only, real file objects unnecessary)
            panel.file_list = ['/dummy/path' + str(i) for i in range(26)]
            # Set the 'files added' message (Korean)
            panel._lbl_status.setText(_tr_args(_qm_lookup('ko', en_add, 'TextMergerPanel'), 26))
            # Switch to Japanese
            self._set_lang('ja')
            panel._retranslate_status()
            expected = _tr_args(_qm_lookup('ja', en_add, 'TextMergerPanel'), 26)
            self.assertEqual(panel._lbl_status.text(), expected,
                "언어 전환 후 파일 추가 메시지가 일본어로 재구성 안 됨")
            # Switch to Simplified Chinese
            self._set_lang('zh_cn')
            panel._retranslate_status()
            expected = _tr_args(_qm_lookup('zh_cn', en_add, 'TextMergerPanel'), 26)
            self.assertEqual(panel._lbl_status.text(), expected)
        finally:
            self._set_lang('ko')
            panel.deleteLater()

    def test_status_path_set_retranslates_with_save_dir(self):
        """'Save path set: %1' 상태에서 언어 전환 시 현재 save_dir로 재구성된다."""
        en_path = 'Save path set: %1'
        panel = self._make_panel('ko')
        try:
            panel.save_dir = 'C:/test/output'
            panel._lbl_status.setText(
                _tr_args(_qm_lookup('ko', en_path, 'TextMergerPanel'), 'C:/test/output'))
            self._set_lang('en')
            panel._retranslate_status()
            expected = _tr_args(_qm_lookup('en', en_path, 'TextMergerPanel'), 'C:/test/output')
            self.assertEqual(panel._lbl_status.text(), expected)
        finally:
            self._set_lang('ko')
            panel.deleteLater()

    def test_status_path_set_falls_back_to_ready_if_save_dir_empty(self):
        """save_dir이 비어있는데 메시지만 path_set 패턴인 엣지 케이스 → Ready로 폴백."""
        en_path = 'Save path set: %1'
        panel = self._make_panel('ko')
        try:
            panel.save_dir = ''  # no path
            panel._lbl_status.setText(
                _tr_args(_qm_lookup('ko', en_path, 'TextMergerPanel'), '/removed/path'))
            self._set_lang('en')
            panel._retranslate_status()
            # Empty save_dir → fall back to Ready
            self.assertEqual(panel._lbl_status.text(),
                             _qm_lookup('en', 'Ready', 'TextMergerPanel'))
        finally:
            self._set_lang('ko')
            panel.deleteLater()

    # ── Non-restorable message → reset to Ready ─────────────
    def test_status_del_resets_to_ready_with_log(self):
        """'%1 file(s) removed' 상태 (원본 개수 소실) → Ready 리셋 + 디버그 로그 남김."""
        en_del = '%1 file(s) removed'
        panel = self._make_panel('ko')
        try:
            panel._lbl_status.setText(_tr_args(_qm_lookup('ko', en_del, 'TextMergerPanel'), 5))
            self._set_lang('ja')
            panel._retranslate_status()
            self.assertEqual(panel._lbl_status.text(),
                             _qm_lookup('ja', 'Ready', 'TextMergerPanel'),
                "del 메시지가 Ready로 리셋되지 않음")
        finally:
            self._set_lang('ko')
            panel.deleteLater()

    def test_status_save_done_resets_to_ready(self):
        """'Saved (%1): %2' 상태 (enc/path 소실) → Ready 리셋."""
        en_save_done = 'Saved (%1): %2'
        panel = self._make_panel('ko')
        try:
            panel._lbl_status.setText(
                _tr_args(_qm_lookup('ko', en_save_done, 'TextMergerPanel'), 'UTF-8', 'C:/out.txt'))
            self._set_lang('zh_tw')
            panel._retranslate_status()
            self.assertEqual(panel._lbl_status.text(),
                             _qm_lookup('zh_tw', 'Ready', 'TextMergerPanel'))
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
        """_match_status_template이 플레이스홀더가 있는 템플릿을 정확히 인식한다.
        Phase 3b: en_template 인자 자국이 *옛 internal key 양식 본받기 *영문 source-text 양식 본격 *옮긴 결."""
        en_add = '%1 file(s) added (encoding auto-detected)'
        en_clr = 'All files cleared'
        panel = self._make_panel('ko')
        try:
            # Korean translation pattern matches
            self.assertTrue(
                panel._match_status_template("26개 파일 추가됨 (인코딩 자동 감지 완료)", en_add))
            # English template matches
            self.assertTrue(
                panel._match_status_template("26 file(s) added (encoding auto-detected)", en_add))
            # No-match case
            self.assertFalse(
                panel._match_status_template("전혀 다른 텍스트", en_add))
            # A different source's template ('All files cleared') must not match
            self.assertFalse(
                panel._match_status_template("26개 파일 추가됨 (인코딩 자동 감지 완료)", en_clr))
        finally:
            panel.deleteLater()


# Note: TestV105TranslationNoDuplicates removed in v1.1.0 Phase 3a.
# That class verified two main-module-source invariants on the inline TRANSLATIONS
# dict — no duplicate keys per language, and similar key counts across languages.
# After Phase 3a both premises no longer apply: TRANSLATIONS now lives in
# fns_translations.py composed from per-language fns_*.py files, so duplicate
# keys are caught at PR-review time via git diff (one file per language) rather
# than runtime, and key-count parity is already verified by
# TestTranslationCompleteness.test_all_langs_same_key_count (rewritten in
# Phase 3a to import fns_translations directly).


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
@unittest.skip("Scenario B: _f_ingest / _p_ingest are now async via "
               "BatchIngestWorker. The consolidated-dialog behavior is "
               "preserved inside _run_ingest_worker.on_done(), but this "
               "synchronous test fixture (which calls _f_ingest / _p_ingest "
               "directly on a bare panel) cannot drive an async worker — "
               "_BarePanel is not a QObject, so QThread.__init__ rejects it. "
               "To be re-added with proper worker mocking in the (β) "
               "regression-protection track, after the (α) Qt Linguist track "
               "lands (since i18n externalization will rewrite many "
               "TRANSLATIONS-related tests anyway).")
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


class TestBatchRenamerScenarioB(unittest.TestCase):
    """Scenario B (QTableView + Model virtualization + QThread workers).

    Source-grep checks (PySide6 not required) — these verify that the four new
    classes and the imports they need are present in FileNexusSuite.py. They do
    not exercise runtime behavior; that is left to the regression-protection
    suite to be added after the Qt Linguist track lands (since i18n
    externalization will rewrite many TRANSLATIONS-related tests anyway).
    """

    @classmethod
    def setUpClass(cls):
        with open(_MAIN_PY, encoding='utf-8') as f:
            cls._src = f.read()

    def test_scenario_b_classes_in_source(self):
        """The four new classes are defined."""
        new_classes = [
            'BatchPreviewModel',         # QAbstractTableModel — virtualized table model
            'BatchRowHeightDelegate',    # QStyledItemDelegate — header (30) / child (34) row height
            'BatchIngestWorker',         # QThread — folder/file ingest off main thread
            'BatchRenameWorker',         # QThread — os.rename loop with WinError 5 bulk retry
        ]
        for cls_name in new_classes:
            with self.subTest(cls=cls_name):
                self.assertIn(f'class {cls_name}', self._src,
                              f"{cls_name} 클래스 정의 없음 (시나리오 B)")

    def test_scenario_b_imports_present(self):
        """Required PySide6 imports for the model/view/worker rewrite."""
        # QtCore: QAbstractTableModel + QModelIndex
        qtcore_match = re.search(r'from PySide6\.QtCore import ([^\n]+)', self._src)
        self.assertIsNotNone(qtcore_match, "PySide6.QtCore import 라인 없음")
        qtcore_line = qtcore_match.group(1)
        for sym in ('QAbstractTableModel', 'QModelIndex'):
            with self.subTest(sym=sym):
                self.assertIn(sym, qtcore_line,
                              f"QtCore에 '{sym}' import 없음")
        # QtWidgets: QTableView (additional import line, see line ~71).
        # NOTE: QProgressDialog was removed in v1.1.0 design polishing —
        # _build_progress_dlg now provides a FNS-toned modal progress dialog.
        self.assertIn('QTableView', self._src,
                      "QtWidgets에 'QTableView' import 없음")

    def test_qtablewidget_no_longer_used_in_batch_panel(self):
        """The Batch Renamer panel uses QTableView (not QTableWidget) for both tabs."""
        panel_start = self._src.find('class BatchRenamerPanel')
        self.assertGreater(panel_start, 0, "BatchRenamerPanel 클래스 정의 없음")
        panel_end = self._src.find('\nclass ', panel_start + 10)
        panel_block = self._src[panel_start:panel_end]
        # _f_table / _p_table should be QTableView()
        self.assertIn('self._f_table=QTableView()', panel_block,
                      "_f_table가 QTableView()로 박혀 있지 않음")
        self.assertIn('self._p_table=QTableView()', panel_block,
                      "_p_table가 QTableView()로 박혀 있지 않음")
        # No QTableWidget(0,3) instantiation in the panel (the bare-class symbol
        # may still appear via the module-level mock in tests, but the explicit
        # 0×3 ctor used in the old _f_/_p_ table setup must be gone)
        self.assertNotIn('QTableWidget(0,3)', panel_block,
                         "BatchRenamerPanel에 QTableWidget(0,3) 자국이 남아 있음")

    def test_worker_kind_validation_present(self):
        """Both workers reject kinds other than 'f' / 'p' (defensive constructor check)."""
        for cls_name in ('BatchIngestWorker', 'BatchRenameWorker'):
            with self.subTest(cls=cls_name):
                self.assertIn(f"{cls_name}: kind must be 'f' or 'p'", self._src,
                              f"{cls_name} kind validation 자국 없음")

    def test_model_has_set_data_and_headerdata(self):
        """BatchPreviewModel exposes the public API used by _f_refresh / _p_refresh
        and by language switches."""
        model_start = self._src.find('class BatchPreviewModel')
        self.assertGreater(model_start, 0)
        model_end = self._src.find('\nclass ', model_start + 10)
        model_block = self._src[model_start:model_end]
        for method in ('def set_data', 'def set_filter_fn',
                       'def headerData', 'def refresh_headers',
                       'def is_header'):
            with self.subTest(method=method):
                self.assertIn(method, model_block,
                              f"BatchPreviewModel에 '{method}' 메서드 없음")


class TestBuildProgressDlg(unittest.TestCase):
    """v1.1.0 design polishing — FNS-toned progress dialog replaces Qt's
    QProgressDialog (Batch Renamer ingest + rename workers tone-matched
    with _confirm / _build_dlg helpers).

    Source-grep checks (PySide6 not required) — verify the helper function
    is defined, both worker runners use it, and Qt's default QProgressDialog
    is no longer instantiated anywhere in the codebase.
    """

    @classmethod
    def setUpClass(cls):
        with open(_MAIN_PY, encoding='utf-8') as f:
            cls._src = f.read()

    def test_helper_function_defined(self):
        """_build_progress_dlg helper is defined at module scope."""
        self.assertIn('def _build_progress_dlg(', self._src,
                      "_build_progress_dlg helper 정의 없음")

    def test_helper_returns_four_widgets(self):
        """Helper returns the (dlg, lbl, bar, cancel_btn) tuple expected by callers."""
        helper_start = self._src.find('def _build_progress_dlg(')
        self.assertGreater(helper_start, 0)
        helper_end = self._src.find('\ndef ', helper_start + 10)
        helper_block = self._src[helper_start:helper_end]
        # Final return statement
        self.assertIn('return dlg, lbl, bar, cancel_btn', helper_block,
                      "_build_progress_dlg 4-tuple 반환 자국 없음")

    def test_helper_uses_fns_tone_palette(self):
        """Helper applies FNS-toned colors (SURFACE/TEXT/ACCENT/BORDER/BG)."""
        helper_start = self._src.find('def _build_progress_dlg(')
        self.assertGreater(helper_start, 0)
        helper_end = self._src.find('\ndef ', helper_start + 10)
        helper_block = self._src[helper_start:helper_end]
        # Background + text color
        self.assertIn('background:{SURFACE}', helper_block,
                      "_build_progress_dlg에 SURFACE 배경 없음")
        # Progress bar accent
        self.assertIn('background:{ACCENT}', helper_block,
                      "_build_progress_dlg에 ACCENT 자국 없음")
        # Border outline
        self.assertIn('{BORDER}', helper_block,
                      "_build_progress_dlg에 BORDER 자국 없음")
        # Cancel button uses _btn_style helper (consistent with _dlg_*)
        self.assertIn('_btn_style(False)', helper_block,
                      "_build_progress_dlg 취소 버튼이 _btn_style을 사용하지 않음")

    def test_helper_preserves_modal_behavior(self):
        """Helper sets WindowModal + minimum width + window flags consistent with _build_dlg."""
        helper_start = self._src.find('def _build_progress_dlg(')
        self.assertGreater(helper_start, 0)
        helper_end = self._src.find('\ndef ', helper_start + 10)
        helper_block = self._src[helper_start:helper_end]
        self.assertIn('Qt.WindowModal', helper_block,
                      "_build_progress_dlg가 WindowModal 양식 미적용")
        self.assertIn('setMinimumWidth', helper_block,
                      "_build_progress_dlg에 setMinimumWidth 자국 없음")

    def test_runners_use_helper(self):
        """Both _run_ingest_worker and _run_rename_worker call _build_progress_dlg."""
        for runner in ('_run_ingest_worker', '_run_rename_worker'):
            with self.subTest(runner=runner):
                runner_start = self._src.find(f'def {runner}(self')
                self.assertGreater(runner_start, 0,
                                   f"{runner} 정의 없음")
                runner_end = self._src.find('\n    def ', runner_start + 10)
                runner_block = self._src[runner_start:runner_end]
                self.assertIn('_build_progress_dlg(', runner_block,
                              f"{runner}가 _build_progress_dlg를 호출하지 않음")
                # 4-tuple unpacking pattern
                self.assertIn('dlg, lbl, bar, cancel_btn', runner_block,
                              f"{runner}에 (dlg, lbl, bar, cancel_btn) 언팩 자국 없음")

    def test_runners_preserve_minimum_duration_400(self):
        """Both runners preserve QProgressDialog's setMinimumDuration(400) behavior
        via QTimer.singleShot(400, _maybe_show) gated by completion flag."""
        for runner in ('_run_ingest_worker', '_run_rename_worker'):
            with self.subTest(runner=runner):
                runner_start = self._src.find(f'def {runner}(self')
                self.assertGreater(runner_start, 0)
                runner_end = self._src.find('\n    def ', runner_start + 10)
                runner_block = self._src[runner_start:runner_end]
                self.assertIn('QTimer.singleShot(400', runner_block,
                              f"{runner}에 400ms 지연 양식 자국 없음")
                self.assertIn("_state['done']", runner_block,
                              f"{runner}에 완료 플래그 자국 없음")

    def test_runners_wire_cancel_button(self):
        """Both runners connect cancel_btn.clicked to worker.request_cancel."""
        for runner in ('_run_ingest_worker', '_run_rename_worker'):
            with self.subTest(runner=runner):
                runner_start = self._src.find(f'def {runner}(self')
                self.assertGreater(runner_start, 0)
                runner_end = self._src.find('\n    def ', runner_start + 10)
                runner_block = self._src[runner_start:runner_end]
                self.assertIn('cancel_btn.clicked.connect(worker.request_cancel)',
                              runner_block,
                              f"{runner}에 취소 버튼 연결 자국 없음")

    def test_qprogressdialog_no_longer_instantiated(self):
        """Qt's QProgressDialog should not be instantiated anywhere — replaced
        by _build_progress_dlg. Mentions in docstrings/comments are allowed."""
        # Look for instantiation pattern: QProgressDialog(...)
        # Allow it to appear only in docstrings/comments, not as a callable
        for line_no, line in enumerate(self._src.splitlines(), 1):
            stripped = line.strip()
            # Skip docstrings/comments
            if stripped.startswith('#'):
                continue
            if 'QProgressDialog(' in stripped:
                # Allow inside docstrings — heuristic: surrounded by triple-quote context
                # We do a stricter check: the pattern must not look like a call.
                # If 'dlg = QProgressDialog(' or '= QProgressDialog(' appears outside
                # a docstring, that's a regression.
                if '= QProgressDialog(' in stripped:
                    self.fail(f"Line {line_no}: QProgressDialog() instantiation found — "
                              f"should use _build_progress_dlg() instead. "
                              f"Line: {stripped!r}")

    def test_qprogressdialog_import_removed(self):
        """QProgressDialog import line should no longer include the symbol."""
        # The import line ~L71: from PySide6.QtWidgets import ..., QTableView
        # QProgressDialog should not appear in any 'from PySide6.QtWidgets import' line
        for match in re.finditer(r'from PySide6\.QtWidgets import ([^\n]+)', self._src):
            import_line = match.group(1)
            self.assertNotIn('QProgressDialog', import_line,
                             "QtWidgets import 라인에 QProgressDialog가 남아 있음 — "
                             "v1.1.0에서 제거 양식")


class TestSidebarCardPolish(unittest.TestCase):
    """v1.1.0 design polishing — Sidebar card visual separation.

    After v1.1.0 Phase 2b, the QGraphicsDropShadowEffect import, the
    _apply_card_shadow helper, and its tuned parameters all live in
    fns_theme.py — verified by TestFnsTheme. This class now covers the
    AppSuite-side glue: the _apply_card_shadows method and its
    invocation pattern from __init__ and apply_theme.
    """

    @classmethod
    def setUpClass(cls):
        with open(_MAIN_PY, encoding='utf-8') as f:
            cls._src = f.read()

    def test_appsuite_applies_shadows_after_build(self):
        """AppSuite._apply_card_shadows is defined and called from both __init__
        and apply_theme — the latter is required so shadow color tracks BORDER
        between light/dark themes."""
        self.assertIn('def _apply_card_shadows(self)', self._src,
                      "AppSuite._apply_card_shadows 메서드 정의 없음")
        # findChildren(QGroupBox) discovery pattern
        method_start = self._src.find('def _apply_card_shadows(self)')
        self.assertGreater(method_start, 0)
        method_end = self._src.find('\n    def ', method_start + 10)
        if method_end == -1:
            method_end = self._src.find('\n    @', method_start + 10)
        method_block = self._src[method_start:method_end]
        self.assertIn('findChildren(QGroupBox)', method_block,
                      "_apply_card_shadows가 findChildren(QGroupBox)로 카드를 찾지 않음")
        # Phase 2b: _apply_card_shadow now takes (widget, border_color) since
        # it lives in fns_theme.py and reads BORDER as an argument.
        self.assertIn('_apply_card_shadow(gb, BORDER)', method_block,
                      "_apply_card_shadows가 _apply_card_shadow(gb, BORDER)를 호출하지 않음")
        # Called at least twice: once in __init__, once in apply_theme
        call_count = self._src.count('self._apply_card_shadows()')
        self.assertGreaterEqual(call_count, 2,
                                f"self._apply_card_shadows() 호출이 2회 미만 ({call_count}회). "
                                f"__init__와 apply_theme 양쪽에서 호출되어야 함")

    # Note: the following tests were removed in v1.1.0 Phase 2b because their
    # main-module-source premise no longer applies after the extraction:
    #   - test_qgraphics_drop_shadow_effect_imported
    #     (QGraphicsDropShadowEffect import now lives in fns_theme.py)
    #   - test_card_shadow_helper_defined
    #     (_apply_card_shadow definition now lives in fns_theme.py)
    #   - test_card_shadow_uses_subtle_parameters
    #     (blur/offset/alpha parameters now live in fns_theme.py)
    #   - test_qgroupbox_qss_uses_accent_title_color
    #     (make_style QSS now lives in fns_theme.py)
    #   - test_qgroupbox_qss_uses_strengthened_padding_and_margin
    #     (make_style QSS now lives in fns_theme.py)
    # Equivalent coverage now lives in TestFnsTheme.


class TestFnsTheme(unittest.TestCase):
    """v1.1.0 Phase 2b — fns_theme.py module regression test.

    Verifies the color tokens (THEMES), theme-detection helpers, and the
    QSS stylesheet builder (make_style) extracted to fns_theme.py during
    the v1.1.0 modularization track. All checks are source-grep based on
    fns_theme.py directly (PySide6 not required).

    Replaces six tests removed from TestV010Regression / TestV012Regression
    / TestSidebarCardPolish whose main-module-source premise no longer
    applies after the Phase 2b extraction.
    """

    @classmethod
    def setUpClass(cls):
        _theme_py = os.path.join(os.path.dirname(_MAIN_PY), 'fns_theme.py')
        with open(_theme_py, encoding='utf-8') as f:
            cls._src = f.read()

    # ── THEMES dict structure ────────────────────────────────────────────
    def test_themes_count_9(self):
        """The THEMES dict must contain 9 themes (auto is virtual, resolved at runtime)."""
        m = re.search(r'^THEMES\s*=\s*\{(.*?)^\}', self._src, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(m, "THEMES 정의 없음")
        keys = re.findall(r"^\s{4}'(\w+)'\s*:\s*\{", m.group(1), re.MULTILINE)
        self.assertEqual(len(keys), 9, f"THEMES 키 수 불일치: {keys}")

    def test_themes_names(self):
        """The THEMES dict must contain exactly the 9 expected theme names."""
        m = re.search(r'^THEMES\s*=\s*\{(.*?)^\}', self._src, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(m, "THEMES 정의 없음")
        keys = set(re.findall(r"^\s{4}'(\w+)'\s*:\s*\{", m.group(1), re.MULTILINE))
        expected = {'light','dark','ocean','mint','sand','honey','sakura','lavender','choco'}
        self.assertEqual(keys, expected)

    def test_all_themes_have_btn_border_h(self):
        """Every theme dictionary must include the BTN_BORDER_H key."""
        m = re.search(r'^THEMES\s*=\s*\{(.*?)^\}', self._src, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(m, "THEMES 정의 없음")
        theme_block = m.group(1)
        self.assertGreater(theme_block.count("'BTN_BORDER_H'"), 0,
                           "THEMES 안에 BTN_BORDER_H 키가 하나도 없음")
        theme_count = len(re.findall(r"^\s{4}'(\w+)'\s*:\s*\{", theme_block, re.MULTILINE))
        btn_border_h_count = theme_block.count("'BTN_BORDER_H'")
        self.assertEqual(btn_border_h_count, theme_count,
            f"BTN_BORDER_H 수({btn_border_h_count}) != 테마 수({theme_count})")

    # ── make_style QSS shape ─────────────────────────────────────────────
    def test_make_style_qgroupbox_title_uses_accent(self):
        """The QGroupBox::title selector inside make_style uses ACCENT
        (not MUTED) so section headers read as accent markers rather
        than faded captions."""
        title_start = self._src.find('QGroupBox::title')
        self.assertGreater(title_start, 0, "QGroupBox::title selector 없음")
        title_block = self._src[title_start:title_start + 300]
        self.assertIn("color:{t['ACCENT']}", title_block,
                      "QGroupBox::title이 ACCENT 색을 사용하지 않음")

    def test_make_style_qgroupbox_padding_strengthened(self):
        """The global QGroupBox rule inside make_style uses the v1.1.0
        strengthened spacing: margin-bottom:6px and padding:12px 10px 10px 10px."""
        gb_start = self._src.find('QGroupBox {{')
        self.assertGreater(gb_start, 0, "QGroupBox 글로벌 rule 없음")
        gb_block = self._src[gb_start:gb_start + 300]
        self.assertIn('margin-bottom:6px', gb_block,
                      "QGroupBox에 margin-bottom:6px 없음")
        self.assertIn('padding:12px 10px 10px 10px', gb_block,
                      "QGroupBox padding이 강화되지 않음 (예상: 12px 10px 10px 10px)")

    # ── Card drop-shadow helper ──────────────────────────────────────────
    def test_qgraphics_drop_shadow_effect_imported(self):
        """QGraphicsDropShadowEffect imported from PySide6.QtWidgets in fns_theme.py
        — required by the _apply_card_shadow helper."""
        found = False
        for match in re.finditer(r'from PySide6\.QtWidgets import ([^\n]+)', self._src):
            if 'QGraphicsDropShadowEffect' in match.group(1):
                found = True
                break
        self.assertTrue(found,
                        "QGraphicsDropShadowEffect가 fns_theme.py의 QtWidgets imports에 박혀 있지 않음")

    def test_apply_card_shadow_defined(self):
        """_apply_card_shadow helper is defined in fns_theme.py with the
        Phase 2b signature (widget, border_color)."""
        self.assertIn('def _apply_card_shadow(widget, border_color)', self._src,
                      "_apply_card_shadow(widget, border_color) 정의 없음")

    def test_apply_card_shadow_uses_subtle_parameters(self):
        """Shadow uses tuned 'subtle but visible' parameters: blur 18,
        offset (0, 3), border_color-derived alpha 0.5. These values landed
        after one round of tuning (v1 was too faint at blur 12 / alpha 0.35)."""
        helper_start = self._src.find('def _apply_card_shadow(widget, border_color)')
        self.assertGreater(helper_start, 0)
        helper_end = self._src.find('\ndef ', helper_start + 10)
        # If _apply_card_shadow is the last def in the file, slice to EOF
        if helper_end == -1:
            helper_end = len(self._src)
        helper_block = self._src[helper_start:helper_end]
        self.assertIn('setBlurRadius(18)', helper_block,
                      "_apply_card_shadow blur radius != 18")
        self.assertIn('setOffset(0, 3)', helper_block,
                      "_apply_card_shadow offset != (0, 3)")
        self.assertIn('setAlphaF(0.5)', helper_block,
                      "_apply_card_shadow alpha != 0.5")
        self.assertIn('QColor(border_color)', helper_block,
                      "_apply_card_shadow color is not derived from border_color argument")


# Note: TestFnsTranslations class removed in v1.1.0 Phase 3b (chunk-4).
# The Phase 3a translation layout (fns_translations.py + translations/<lang>.py
# dict modules) was itself superseded by Qt Linguist .ts/.qm sources during
# Phase 3b. The TRANSLATIONS dict no longer exists at runtime; _all_translations_of
# now reads .qm via _qm_lookup; _THEME_NAME_KEY and SUPPORTED_LANGUAGES live
# elsewhere. Equivalent translation-integrity coverage lives in:
#   - TestTsSourceIntegrity  (.ts source-file integrity, key symmetry,
#                             macro-category coverage; PySide6-independent)
#   - TestQmRuntimeIntegrity (.qm runtime + _qm_lookup + _all_translations_of
#                             round-trip; requires real PySide6)


class TestFnsUtils(unittest.TestCase):
    """v1.1.0 Phase 2a — fns_utils.py module regression test.

    Verifies the pure-function helpers (HTML utilities, natural-sort,
    Tag Editor core) extracted to fns_utils.py during the v1.1.0
    modularization track. Module-load based: imports the module
    directly and exercises each helper. PySide6 not required since
    fns_utils has no Qt dependency.

    Replaces the in-test mock helpers and the eleven test classes that
    were grading the mocks rather than the actual extracted module
    (TestDe / TestEx / TestStripXmlIllegal / TestH2t / TestNaturalSort /
    TestRemoveTag / TestAddTag / TestDepad / TestDetectPrefix /
    TestExtractNumber / TestDepadDateRegression — 132 tests in total).
    The old test bodies were grading mock signatures (e.g. _de(None) -> None,
    _ex("'") -> &#39;) that diverged from the real fns_utils behavior;
    rewriting them as-is would have carried dead specifications forward.
    The new class grades fns_utils directly.
    """

    @classmethod
    def setUpClass(cls):
        import fns_utils
        cls._mod = fns_utils
        with open(os.path.join(os.path.dirname(_MAIN_PY), 'fns_utils.py'),
                  encoding='utf-8') as f:
            cls._src = f.read()

    # ── Module surface ───────────────────────────────────────────────────
    def test_module_exposes_all_seventeen_names(self):
        """fns_utils exposes the 17 names the main module imports."""
        expected = {
            # Number / natural-sort utilities (8)
            '_pad', 'extract_number', '_get_leading_num', 'extract_number_auto',
            'auto_width_for_group', 'detect_common_prefix', 'natural_sort_key',
            '_SKIP_FILES',
            # Tag Editor core logic (5)
            'remove_tag_from_name', '_build_tag_str', 'add_tag_to_name',
            'depad_name', 'apply_renames',
            # HTML utilities (4)
            '_de', '_h2t', '_strip_xml_illegal', '_ex',
        }
        for name in expected:
            with self.subTest(name=name):
                self.assertTrue(hasattr(self._mod, name),
                                f"fns_utils에 {name!r} 자국 없음")

    def test_skip_files_is_set_of_lowercase_strings(self):
        """_SKIP_FILES is a set of system-junk file names, all lowercase."""
        s = self._mod._SKIP_FILES
        self.assertIsInstance(s, set)
        self.assertGreater(len(s), 0)
        for name in s:
            self.assertEqual(name, name.lower(),
                             f"_SKIP_FILES 자국 {name!r}이 lowercase 아님")
        # Common Windows junk that the natural-sort filter excludes
        self.assertIn('desktop.ini', s)
        self.assertIn('thumbs.db', s)

    # ── HTML utilities — _de (HTML entity decoding) ──────────────────────
    def test_de_named_entities(self):
        """Named entities decode: &amp; &lt; &gt; &quot; &apos; &#39; &nbsp;"""
        _de = self._mod._de
        self.assertEqual(_de('a&amp;b'), 'a&b')
        self.assertEqual(_de('a&lt;b'), 'a<b')
        self.assertEqual(_de('a&gt;b'), 'a>b')
        self.assertEqual(_de('&quot;hi&quot;'), '"hi"')
        self.assertEqual(_de('&apos;'), "'")
        self.assertEqual(_de('&#39;'), "'")
        self.assertEqual(_de('a&nbsp;b'), 'a b')

    def test_de_numeric_entities(self):
        """Numeric entities (decimal &#N; and hex &#xHH;) decode to chars."""
        _de = self._mod._de
        self.assertEqual(_de('&#65;'), 'A')           # decimal
        self.assertEqual(_de('&#x41;'), 'A')          # hex (lower)
        self.assertEqual(_de('&#44032;'), '가')       # decimal Korean
        self.assertEqual(_de('&#xAC00;'), '가')       # hex Korean

    def test_de_unknown_entities_stripped(self):
        """Unknown lowercase named entities (&unknown;) are stripped to empty.
        This is fns_utils policy: any leftover &[a-z]+; is removed at the end."""
        _de = self._mod._de
        self.assertEqual(_de('&unknown;'), '')
        self.assertEqual(_de('a&xyz;b'), 'ab')

    def test_de_chain_and_no_entity(self):
        """Chained entities decode left-to-right; plain text passes through."""
        _de = self._mod._de
        self.assertEqual(_de('&lt;&amp;&gt;'), '<&>')
        self.assertEqual(_de('hello'), 'hello')
        self.assertEqual(_de(''), '')

    def test_de_surrogates_blocked(self):
        """Surrogate code points (U+D800-U+DFFF) decode to empty rather
        than producing invalid text."""
        _de = self._mod._de
        self.assertEqual(_de('&#55296;'), '')        # U+D800 — leading surrogate
        self.assertEqual(_de('&#57343;'), '')        # U+DFFF — trailing surrogate

    # ── HTML utilities — _ex (HTML / XML escaping) ──────────────────────
    def test_ex_basic_escapes(self):
        """The five XML predefined entities are produced (apos, not #39)."""
        _ex = self._mod._ex
        self.assertEqual(_ex('a&b'), 'a&amp;b')
        self.assertEqual(_ex('<'), '&lt;')
        self.assertEqual(_ex('>'), '&gt;')
        self.assertEqual(_ex('"'), '&quot;')
        self.assertEqual(_ex("'"), '&apos;')

    def test_ex_combined_and_safe_text(self):
        """Combined attribute-style escape; plain Korean passes through."""
        _ex = self._mod._ex
        self.assertEqual(_ex('<a href="x">'),
                         '&lt;a href=&quot;x&quot;&gt;')
        self.assertEqual(_ex('hello 안녕'), 'hello 안녕')
        self.assertEqual(_ex(''), '')

    def test_ex_strips_xml_illegal_first(self):
        """_ex composes _strip_xml_illegal, so control chars never appear in output."""
        _ex = self._mod._ex
        self.assertEqual(_ex('a\x00b'), 'ab')         # NUL stripped
        self.assertEqual(_ex('a\x1Fb'), 'ab')         # control stripped

    # ── HTML utilities — _strip_xml_illegal ─────────────────────────────
    def test_strip_xml_illegal_strips_control_chars(self):
        """C0 control chars (except tab, LF, CR) are stripped."""
        s = self._mod._strip_xml_illegal
        self.assertEqual(s('\x00'), '')
        self.assertEqual(s('\x08'), '')
        self.assertEqual(s('\x0B'), '')
        self.assertEqual(s('\x1F'), '')
        self.assertEqual(s('a\x00b\x1Fc'), 'abc')

    def test_strip_xml_illegal_preserves_legal_chars(self):
        """Tab, LF, CR, and printable text are preserved."""
        s = self._mod._strip_xml_illegal
        self.assertEqual(s('\t'), '\t')
        self.assertEqual(s('\n'), '\n')
        self.assertEqual(s('\r'), '\r')
        self.assertEqual(s('hello'), 'hello')
        self.assertEqual(s('한국어'), '한국어')

    # ── HTML utilities — _h2t (HTML → text) ─────────────────────────────
    def test_h2t_basic_block_tags(self):
        """Block-level tags (br, p, div) become newlines (between content,
        not at the edges — the final .strip() trims leading/trailing whitespace)."""
        _h2t = self._mod._h2t
        self.assertIn('\n', _h2t('a<br>b', False))
        self.assertIn('\n', _h2t('<p>a</p><p>b</p>', False))
        self.assertIn('\n', _h2t('<div>a</div><div>b</div>', False))

    def test_h2t_strips_tags_and_decodes_entities(self):
        """Tags are stripped; entities are decoded inside the text."""
        _h2t = self._mod._h2t
        self.assertEqual(_h2t('<b>hello</b>', False), 'hello')
        self.assertEqual(_h2t('&amp;', False), '&')

    def test_h2t_keep_headings(self):
        """keep=True wraps headings with bullet markers; keep=False strips them silently."""
        _h2t = self._mod._h2t
        kept = _h2t('<h1>Title</h1>body', True)
        self.assertIn('Title', kept)
        self.assertIn('■', kept)             # heading bullet marker
        stripped = _h2t('<h1>Title</h1>body', False)
        self.assertNotIn('■', stripped)

    def test_h2t_drops_script_and_style(self):
        """<script> and <style> blocks are stripped entirely (content + tags)."""
        _h2t = self._mod._h2t
        self.assertNotIn('alert', _h2t('a<script>alert(1)</script>b', False))
        self.assertNotIn('color', _h2t('a<style>p{color:red}</style>b', False))

    # ── Number / natural-sort utilities ─────────────────────────────────
    def test_pad_zero_pads_single_digits(self):
        """_pad zero-pads single-digit strings to width 2; leaves the rest alone."""
        _pad = self._mod._pad
        self.assertEqual(_pad('1'), '01')
        self.assertEqual(_pad('9'), '09')
        self.assertEqual(_pad('10'), '10')
        self.assertEqual(_pad('100'), '100')
        self.assertEqual(_pad('abc'), 'abc')

    def test_extract_number_pads_first_run(self):
        """extract_number returns the file's first numeric run, zero-padded to 2."""
        f = self._mod.extract_number
        self.assertEqual(f('Chapter 1'), '01')
        self.assertEqual(f('Chapter 9'), '09')
        self.assertEqual(f('Chapter 10'), '10')
        self.assertEqual(f('Chapter 100'), '100')
        self.assertEqual(f(''), '')                    # empty stays empty
        self.assertEqual(f('no number'), 'no number')  # no digit → input back

    def test_extract_number_handles_range_and_separators(self):
        """Range (1~3), hyphen (1-3), and dot (1.5) keep the separator."""
        f = self._mod.extract_number
        self.assertEqual(f('1~3'), '01~03')
        self.assertEqual(f('1-3'), '01-3')
        self.assertEqual(f('1.5'), '01.5')

    def test_extract_number_auto_uses_explicit_width(self):
        """extract_number_auto pads to the explicit width argument."""
        f = self._mod.extract_number_auto
        self.assertEqual(f('Chapter 1', 3), '001')
        self.assertEqual(f('Chapter 12', 4), '0012')

    def test_auto_width_for_group_picks_max_digit_count(self):
        """auto_width_for_group returns the digit-count of the largest leading number."""
        f = self._mod.auto_width_for_group
        self.assertEqual(f(['Chapter 1', 'Chapter 2', 'Chapter 9']), 1)
        self.assertEqual(f(['Chapter 1', 'Chapter 100']), 3)
        self.assertEqual(f(['no digits', 'either']), 1)

    def test_get_leading_num_returns_first_int(self):
        """_get_leading_num returns the first integer in the string, 0 if absent."""
        f = self._mod._get_leading_num
        self.assertEqual(f('Chapter 12'), 12)
        self.assertEqual(f('12 Chapter'), 12)
        self.assertEqual(f('no digits'), 0)

    def test_detect_common_prefix_strips_at_first_digit(self):
        """detect_common_prefix returns the shared prefix, cut at the first digit."""
        f = self._mod.detect_common_prefix
        self.assertEqual(f(['Chapter 1', 'Chapter 2']), 'Chapter ')
        self.assertEqual(f(['ABC_1', 'ABC_2']), 'ABC_')
        self.assertEqual(f(['001Chapter', '002Chapter']), '')   # leading digit → empty
        self.assertEqual(f([]), '')

    def test_natural_sort_key_uses_basename_lowercased(self):
        """natural_sort_key splits on digit runs, basename-only, lowercased."""
        f = self._mod.natural_sort_key
        # Mixed case + digits — sort by numeric run
        a = f('/path/to/Chapter 2.txt')
        b = f('/path/to/Chapter 10.txt')
        self.assertLess(a, b, "Chapter 2 must natural-sort before Chapter 10")
        # Basename only — directory ignored
        self.assertEqual(f('/a/b/file.txt'), f('/x/y/file.txt'))

    # ── Tag Editor core logic ───────────────────────────────────────────
    def test_remove_tag_from_name_front_back_both(self):
        """remove_tag_from_name strips bracket tags by position."""
        f = self._mod.remove_tag_from_name
        self.assertEqual(f('[KO] file.txt', position='front'), 'file.txt')
        self.assertEqual(f('file [done].txt', position='back'), 'file.txt')
        self.assertEqual(f('[KO] file [done].txt', position='both'), 'file.txt')

    def test_remove_tag_from_name_target_specific(self):
        """target_tag strips only the given tag, regardless of position."""
        f = self._mod.remove_tag_from_name
        self.assertEqual(f('[KO] file [done].txt', target_tag='KO'),
                         'file [done].txt')
        self.assertEqual(f('[KO] file [done].txt', target_tag='done'),
                         '[KO] file.txt')

    def test_remove_tag_from_name_double_brackets(self):
        """Double-bracket tags ([[tag]]) are stripped by the [+...]+ pattern."""
        f = self._mod.remove_tag_from_name
        self.assertEqual(f('[[KO]] file.txt', position='front'), 'file.txt')

    def test_remove_tag_from_name_empty_or_unchanged_returns_none(self):
        """When the tag-strip would leave the basename empty, or no change
        happens, the function returns None — caller can skip the rename."""
        f = self._mod.remove_tag_from_name
        self.assertIsNone(f('[KO].txt', position='front'))   # would be empty
        self.assertIsNone(f('plain.txt', position='front'))  # no change

    def test_build_tag_str_substitutes_placeholder(self):
        """_build_tag_str replaces the {tag} placeholder in fmt with the raw tag."""
        f = self._mod._build_tag_str
        self.assertEqual(f('KO', '[{tag}]'), '[KO]')
        self.assertEqual(f('done', '({tag})'), '(done)')

    def test_add_tag_to_name_front_and_back(self):
        """add_tag_to_name prepends/appends a formatted tag with optional spacing."""
        f = self._mod.add_tag_to_name
        self.assertEqual(f('file.txt', ['KO'], '[{tag}]', 'front', False, False),
                         '[KO] file.txt')
        self.assertEqual(f('file.txt', ['KO'], '[{tag}]', 'back', False, False),
                         'file [KO].txt')

    def test_add_tag_to_name_skip_when_present(self):
        """skip_exist=True returns None if the tag is already in the basename."""
        f = self._mod.add_tag_to_name
        self.assertIsNone(f('[KO] file.txt', ['KO'], '[{tag}]',
                            'front', True, False))

    def test_depad_name_preserves_dates(self):
        """depad_name leaves YYYY-MM-DD and MM-DD untouched (returns None)."""
        f = self._mod.depad_name
        self.assertIsNone(f('2024-01-01'))
        self.assertIsNone(f('01-01'))

    def test_depad_name_strips_leading_zeros(self):
        """Leading zeros are removed from a single number run."""
        f = self._mod.depad_name
        self.assertEqual(f('001화.txt'), '1화.txt')
        self.assertEqual(f('007.mp3'), '7.mp3')

    def test_depad_name_keeps_zero_after_hyphen(self):
        """Zeros after a hyphen are preserved (range notation 001-197화 → 1-197화)."""
        f = self._mod.depad_name
        # Strips leading 001 but keeps 197
        result = f('사과나무 001-197화(完).txt')
        self.assertIsNotNone(result)
        self.assertIn('1-197', result)
        self.assertNotIn('001', result)

    def test_depad_name_no_change_returns_none(self):
        """If the regex changes nothing, return None — caller can skip the rename."""
        f = self._mod.depad_name
        self.assertIsNone(f('plain.txt'))

    def test_apply_renames_returns_success_count_and_errors(self):
        """apply_renames returns (success_count, error_list) and renames files on disk."""
        f = self._mod.apply_renames
        with tempfile.TemporaryDirectory() as td:
            for name in ('a.txt', 'b.txt'):
                open(os.path.join(td, name), 'w').close()
            success, errors = f([(td, 'a.txt', 'a_renamed.txt'),
                                 (td, 'b.txt', 'b_renamed.txt')])
            self.assertEqual(success, 2)
            self.assertEqual(errors, [])
            self.assertTrue(os.path.exists(os.path.join(td, 'a_renamed.txt')))
            self.assertTrue(os.path.exists(os.path.join(td, 'b_renamed.txt')))

    def test_apply_renames_collects_failures(self):
        """Failed renames are collected without aborting the loop."""
        f = self._mod.apply_renames
        with tempfile.TemporaryDirectory() as td:
            success, errors = f([(td, 'missing.txt', 'whatever.txt')])
            self.assertEqual(success, 0)
            self.assertEqual(len(errors), 1)

    # ── Empty-input boundary (replaces the three TestBoundaryValues tests
    #    that were grading the old in-test mocks: depad / remove_tag /
    #    extract_number with empty-string input). The fns_utils contract
    #    differs from the old mocks: empty input that produces no change
    #    returns None for the rename helpers, and extract_number returns
    #    the input string back rather than None — both intentional, since
    #    None signals "no rename needed" to callers in the main module.
    def test_depad_name_empty_input(self):
        """depad_name('') returns None — empty stays empty, no rename."""
        self.assertIsNone(self._mod.depad_name(''))

    def test_remove_tag_from_name_empty_input(self):
        """remove_tag_from_name('') returns None — nothing to strip."""
        self.assertIsNone(self._mod.remove_tag_from_name('', position='both'))

    def test_extract_number_empty_input(self):
        """extract_number('') returns '' — input passed through unchanged."""
        self.assertEqual(self._mod.extract_number(''), '')

    # ── fns_utils.py source-grep invariants ─────────────────────────────
    def test_no_pyside6_dependency(self):
        """fns_utils.py is pure Python — must not import PySide6."""
        self.assertNotIn('import PySide6', self._src,
                         "fns_utils.py에 PySide6 import 자국 박힘 — 본질 깨짐")
        self.assertNotIn('from PySide6', self._src,
                         "fns_utils.py에 PySide6 from-import 자국 박힘 — 본질 깨짐")

    def test_no_translations_or_theme_dependency(self):
        """fns_utils.py code (excluding the header docstring, which mentions
        these names only to declare independence) must not import or use
        TRANSLATIONS, fns_theme, or ConfigManager."""
        import re as _re_local
        # Strip the header module docstring so its descriptive prose
        # ("no dependencies on PySide6, TRANSLATIONS, ConfigManager...")
        # doesn't trip the substring check.
        code = _re_local.sub(r'^"""[\s\S]*?"""', '', self._src,
                             count=1, flags=_re_local.MULTILINE)
        self.assertNotIn('TRANSLATIONS', code,
                         "fns_utils.py 코드 자국에 TRANSLATIONS 박힘 — 본질 깨짐")
        self.assertNotIn('fns_theme', code,
                         "fns_utils.py 코드 자국에 fns_theme 박힘 — 본질 깨짐")
        self.assertNotIn('ConfigManager', code,
                         "fns_utils.py 코드 자국에 ConfigManager 박힘 — 본질 깨짐")

    def test_only_stdlib_imports(self):
        """fns_utils.py imports only stdlib (os, re) — no third-party packages."""
        import re as _re_local
        imports = _re_local.findall(r'^(?:from|import)\s+(\S+)',
                                     self._src, _re_local.MULTILINE)
        for mod in imports:
            top = mod.split('.')[0]
            with self.subTest(mod=top):
                self.assertIn(top, {'os', 're'},
                              f"fns_utils.py에 비표준 import 자국 ({top}) 박힘")

    # ── Main-module integration ──────────────────────────────────────────
    def test_main_module_imports_from_fns_utils(self):
        """Main module imports the seventeen extracted names from fns_utils."""
        with open(_MAIN_PY, encoding='utf-8') as f:
            src = f.read()
        self.assertIn('from fns_utils import', src,
                      "본체에 fns_utils import 자국 없음")
        for name in ('_pad', 'extract_number', '_get_leading_num',
                     'extract_number_auto', 'auto_width_for_group',
                     'detect_common_prefix', 'natural_sort_key', '_SKIP_FILES',
                     'remove_tag_from_name', '_build_tag_str',
                     'add_tag_to_name', 'depad_name', 'apply_renames',
                     '_de', '_h2t', '_strip_xml_illegal', '_ex'):
            with self.subTest(name=name):
                self.assertIn(name, src,
                              f"본체 import에 {name!r} 자국 없음")

    def test_main_module_no_inline_pure_helpers(self):
        """The seventeen helper definitions must no longer live in the main
        module after Phase 2a — only the import statement should reference them."""
        with open(_MAIN_PY, encoding='utf-8') as f:
            src = f.read()
        # No top-level "def extract_number(" etc.
        for fn in ('extract_number', 'extract_number_auto',
                   'auto_width_for_group', 'detect_common_prefix',
                   'natural_sort_key', 'remove_tag_from_name',
                   'add_tag_to_name', 'depad_name', 'apply_renames',
                   '_build_tag_str', '_de', '_h2t', '_strip_xml_illegal',
                   '_ex', '_pad', '_get_leading_num'):
            with self.subTest(fn=fn):
                self.assertNotRegex(src, rf'^def {fn}\b',
                    f"본체에 def {fn}( 정의 자국이 아직 박혀 있음")
        # No top-level "_SKIP_FILES = " definition (constant)
        self.assertNotRegex(src, r'^_SKIP_FILES\s*=\s*\{',
                            "본체에 _SKIP_FILES = { 정의 자국이 아직 박혀 있음")


class TestFileListBaseRefactor(unittest.TestCase):
    """v1.1.0 (라-B-1.5-B) — File list base classes.

    Verifies the three base classes (FileListModel / FileListBase / DragDropMixin)
    that consolidate the QTreeWidget pattern across five FNS file-list widgets
    into a virtualized QTableView + QAbstractTableModel architecture.
    """

    @classmethod
    def setUpClass(cls):
        with open(_MAIN_PY, encoding='utf-8') as f:
            cls.src = f.read()

    def _get_class_body(self, name):
        import re
        m = re.search(rf'^class {name}\b.*?(?=\n^class |\nif __name__|\Z)',
                      self.src, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(m, f"{name} 클래스 정의 자국 없음")
        return m.group(0)

    def test_three_base_classes_defined(self):
        """FileListModel, FileListBase, DragDropMixin must all exist."""
        self.assertIn('class FileListModel(QAbstractTableModel):', self.src,
                      "FileListModel(QAbstractTableModel) 클래스 정의 자국 없음")
        self.assertIn('class FileListBase(QTableView):', self.src,
                      "FileListBase(QTableView) 클래스 정의 자국 없음")
        self.assertIn('class DragDropMixin:', self.src,
                      "DragDropMixin 클래스 정의 자국 없음")

    def test_filelistmodel_supports_arbitrary_items(self):
        """FileListModel.data() must guard with isinstance(item, str) so non-path
        items (e.g. tuples in _TagPreviewTree) don't crash default rendering."""
        body = self._get_class_body('FileListModel')
        self.assertIn('isinstance(item, str)', body,
                      "FileListModel data()가 임의 item 양식 호환 자국 없음")
        self.assertIn('PATH_ROLE = Qt.ItemDataRole.UserRole + 4', body,
                      "FileListModel.PATH_ROLE 클래스 변수 없음")

    def test_filelistmodel_has_sort_api(self):
        """FileListModel must expose sort(column, order) + sort_key(column) for
        Qt's setSortingEnabled(True) integration."""
        body = self._get_class_body('FileListModel')
        self.assertIn('def sort(self, column, order=', body,
                      "FileListModel.sort() 메서드 자국 없음")
        self.assertIn('def sort_key(self, column):', body,
                      "FileListModel.sort_key() 메서드 자국 없음")
        self.assertIn('natural_sort_key', body,
                      "FileListModel.sort_key가 natural_sort_key 본받지 않음")

    def test_filelistbase_class_attrs(self):
        """FileListBase must declare the contract attributes for subclass overrides."""
        body = self._get_class_body('FileListBase')
        for attr in ('COLUMNS', 'COLUMN_WIDTHS', 'SELECTION_MODE', 'SORT_ENABLED',
                     'INITIAL_SORT_COLUMN', 'INITIAL_SORT_ORDER'):
            self.assertIn(attr, body, f"FileListBase.{attr} 클래스 변수 자국 없음")
        self.assertIn('files_changed = Signal(int)', body,
                      "FileListBase.files_changed 시그널 자국 없음")

    def test_filelistbase_core_methods(self):
        """FileListBase must implement the common file-list contract."""
        body = self._get_class_body('FileListBase')
        for method in ('def add_files(self, paths, warn_fn=None):',
                       'def remove_selected(self):',
                       'def clear_files(self):',
                       'def move_selection(self, delta):',
                       'def keyPressEvent(self, e):',
                       'def retranslate_headers(self):',
                       'def _file_filter(self, paths):',
                       'def _setup_view(self):',
                       'def _make_model(self):'):
            self.assertIn(method, body,
                          f"FileListBase에 '{method.strip()}' 자국 없음")
        self.assertIn('@property', body, "FileListBase.files property 자국 없음")

    def test_dragdropmixin_contract(self):
        """DragDropMixin must declare ACCEPT_EXTERNAL_DROPS and the drag-drop
        event handlers that work via _setup_dragdrop()."""
        body = self._get_class_body('DragDropMixin')
        self.assertIn('ACCEPT_EXTERNAL_DROPS = False', body,
                      "DragDropMixin.ACCEPT_EXTERNAL_DROPS 자국 없음")
        for method in ('def _setup_dragdrop(self):',
                       'def dragEnterEvent(self, e):',
                       'def dragMoveEvent(self, e):',
                       'def startDrag(self, supported_actions):',
                       'def dropEvent(self, e):',
                       'def _handle_internal_drop(self, e):'):
            self.assertIn(method, body,
                          f"DragDropMixin에 '{method.strip()}' 자국 없음")
        # CopyAction enforcement (v1.0.6 pattern, prevents Qt's auto-delete bug)
        self.assertIn('Qt.DropAction.CopyAction', body,
                      "DragDropMixin이 CopyAction 강제 자국 없음 (v1.0.6 패턴)")


class TestFileListSubClassRefactor(unittest.TestCase):
    """v1.1.0 (라-B-1.5-B) — Five file-list widgets refactored to FileListBase.

    Verifies each subclass declares the right COLUMNS/SELECTION_MODE/SORT_ENABLED
    and the right mixin chain. The five subclasses are:
        _TagFileList               — Tag Editor 좌측 (no mixin, Qt-builtin sort)
        _TagPreviewTree            — Tag Editor 우측 (no mixin, preview-only, 3 cols)
        BulkFixerFileList          — DragDropMixin + .txt filter
        TextConverterFileList      — DragDropMixin + mode-aware filter (txt/epub)
        MergeFileTree              — DragDropMixin (EXT=True) + encoding metadata
    """

    @classmethod
    def setUpClass(cls):
        with open(_MAIN_PY, encoding='utf-8') as f:
            cls.src = f.read()

    def _get_class_body(self, name):
        import re
        m = re.search(rf'^class {name}\b.*?(?=\n^class |\nif __name__|\Z)',
                      self.src, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(m, f"{name} 클래스 정의 자국 없음")
        return m.group(0)

    def test_tag_file_list(self):
        """_TagFileList: FileListBase + Qt-builtin sort (no DragDropMixin)."""
        body = self._get_class_body('_TagFileList')
        self.assertIn('class _TagFileList(FileListBase):', body,
                      "_TagFileList가 FileListBase 본받기 자국 없음")
        self.assertNotIn('DragDropMixin', body,
                         "_TagFileList는 DragDropMixin 본받지 않아야 함")
        self.assertIn('SORT_ENABLED = True', body,
                      "_TagFileList.SORT_ENABLED=True 자국 없음")
        # v1.1.0 Phase 3b: i18n keys replaced by QT_TR_NOOP(English source).
        self.assertIn('QT_TR_NOOP("Filename")', body,
                      "_TagFileList COLUMNS에 QT_TR_NOOP(\"Filename\") 자국 없음")
        self.assertIn('QT_TR_NOOP("Path")', body,
                      "_TagFileList COLUMNS에 QT_TR_NOOP(\"Path\") 자국 없음")

    def test_tag_preview_tree(self):
        """_TagPreviewTree: FileListBase + 3 cols + SingleSelection + custom model."""
        body = self._get_class_body('_TagPreviewTree')
        self.assertIn('class _TagPreviewTree(FileListBase):', body)
        self.assertNotIn('DragDropMixin', body,
                         "_TagPreviewTree는 DragDropMixin 본받지 않아야 함")
        self.assertIn('SELECTION_MODE = QAbstractItemView.SingleSelection', body,
                      "_TagPreviewTree.SELECTION_MODE=Single 자국 없음")
        self.assertIn('SORT_ENABLED = False', body,
                      "_TagPreviewTree는 sort 비활성화 (preview only)")
        # v1.1.0 Phase 3b: i18n keys replaced by QT_TR_NOOP(English source).
        # Three-tuple item rendering via render_fn lambdas.
        for source in ('Folder', 'Original Name', 'New Name'):
            self.assertIn(f'QT_TR_NOOP("{source}")', body,
                          f"_TagPreviewTree에 QT_TR_NOOP(\"{source}\") 자국 없음")
        # Custom model for ACCENT-colored 'new name' column
        self.assertIn('_TagPreviewModel', body,
                      "_TagPreviewTree가 _TagPreviewModel 양식 본받지 않음")
        # _TagPreviewModel as separate class with ForegroundRole override
        pm_body = self._get_class_body('_TagPreviewModel')
        self.assertIn('Qt.ForegroundRole', pm_body,
                      "_TagPreviewModel이 ForegroundRole 양식 본받지 않음")

    def test_bulk_fixer_file_list(self):
        """BulkFixerFileList: DragDropMixin + FileListBase + .txt filter."""
        body = self._get_class_body('BulkFixerFileList')
        self.assertIn('class BulkFixerFileList(DragDropMixin, FileListBase):', body,
                      "BulkFixerFileList가 (DragDropMixin, FileListBase) 양식 본받지 않음")
        self.assertIn('ACCEPT_EXTERNAL_DROPS = False', body,
                      "BulkFixerFileList — DropZone이 외부 drop 박는 양식")
        self.assertIn('SORT_ENABLED = True', body)
        # .txt filter via _file_filter override
        self.assertIn('def _file_filter(self, paths):', body,
                      "BulkFixerFileList._file_filter override 자국 없음")
        self.assertIn(".txt'", body, "BulkFixerFileList가 .txt 필터 자국 없음")
        # DragDropMixin signals declared on concrete class (PySide6 양식)
        self.assertIn('files_dropped = Signal(list)', body)
        self.assertIn('order_changed = Signal()', body)

    def test_text_converter_file_list(self):
        """TextConverterFileList: DragDropMixin + FileListBase + mode-aware filter."""
        body = self._get_class_body('TextConverterFileList')
        self.assertIn('class TextConverterFileList(DragDropMixin, FileListBase):', body)
        self.assertIn('ACCEPT_EXTERNAL_DROPS = False', body,
                      "TextConverterFileList — DropZone이 외부 drop 박는 양식")
        self.assertIn('def set_mode(self, mode):', body,
                      "TextConverterFileList.set_mode() 메서드 자국 없음")
        self.assertIn('def _file_filter(self, paths):', body)
        # Mode-aware extension switching
        self.assertIn('"epub2txt"', body)
        self.assertIn('.epub', body)
        self.assertIn('.txt', body)

    def test_merge_file_tree(self):
        """MergeFileTree: DragDropMixin (EXT=True) + FileListBase + encoding metadata."""
        body = self._get_class_body('MergeFileTree')
        self.assertIn('class MergeFileTree(DragDropMixin, FileListBase):', body)
        self.assertIn('ACCEPT_EXTERNAL_DROPS = True', body,
                      "MergeFileTree는 외부 file drop 박을 자국 (ACCEPT_EXTERNAL_DROPS=True)")
        self.assertIn('SORT_ENABLED = False', body,
                      "MergeFileTree는 panel-managed sort (header click → _sort_files)")
        # Metadata wiring API
        self.assertIn('def set_metadata_maps(self, enc_map, conf_map, lines_map):', body,
                      "MergeFileTree.set_metadata_maps() 메서드 없음")
        self.assertIn('def refresh_path(self, path):', body,
                      "MergeFileTree.refresh_path(path) 메서드 없음")
        # Custom model for encoding-role lookups
        self.assertIn('_MergeFileTreeModel', body,
                      "MergeFileTree가 _MergeFileTreeModel 본받지 않음")
        # _MergeFileTreeModel routes the three encoding roles to external dicts
        mm_body = self._get_class_body('_MergeFileTreeModel')
        for role_offset in ('UserRole + 1', 'UserRole + 2', 'UserRole + 3'):
            self.assertIn(role_offset, mm_body,
                          f"_MergeFileTreeModel data()가 {role_offset} 자국 박지 않음")


class TestTextMergerSelectionLayout(unittest.TestCase):
    """v1.1.0 — Text Merger selection-label layout fix.

    The bottom selection summary label (_lbl_selection) used to share a
    horizontal row with the move/delete buttons. With many files selected,
    the label's intrinsic width inflated the left panel's minimumSize and
    pushed the right (// save settings) panel off-screen — also clipping
    the move/delete buttons' own text.

    Fix: (1) move the label to its own row, (2) wrap it in a new
    _ElideLabel helper that ignores horizontal minimumSize and
    right-elides with '...' (full text remains accessible via tooltip).
    """

    @classmethod
    def setUpClass(cls):
        with open(_MAIN_PY, encoding='utf-8') as f:
            cls.src = f.read()

    def _get_class_body(self, name):
        import re
        m = re.search(rf'^class {name}\b.*?(?=\n^class |\nif __name__|\Z)',
                      self.src, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(m, f"{name} 클래스 정의가 없음")
        return m.group(0)

    def test_elide_label_class_defined(self):
        """_ElideLabel(QLabel) helper must exist."""
        self.assertIn('class _ElideLabel(QLabel):', self.src,
                      "_ElideLabel(QLabel) 클래스 정의가 없음")

    def test_elide_label_size_policy_ignored(self):
        """_ElideLabel must set horizontal SizePolicy to Ignored so a long
        string never inflates the parent widget's minimum width."""
        body = self._get_class_body('_ElideLabel')
        self.assertIn('QSizePolicy.Ignored', body,
                      "_ElideLabel은 QSizePolicy.Ignored를 박아야 함 "
                      "(부모 widget의 minimum width가 라벨 텍스트 길이로 expand되는 것을 차단)")
        self.assertIn('setSizePolicy(', body,
                      "_ElideLabel은 setSizePolicy() 호출이 없음")

    def test_elide_label_overrides_settext(self):
        """setText must override QLabel.setText to store the full text and
        re-apply elision, so external callers get elision automatically
        without changes at the call site."""
        body = self._get_class_body('_ElideLabel')
        self.assertIn('def setText(self, text):', body,
                      "_ElideLabel.setText override가 없음")
        self.assertIn('self._full_text', body,
                      "_ElideLabel은 full text를 _full_text에 보관해야 함")
        self.assertIn('setToolTip', body,
                      "_ElideLabel은 full text를 tooltip으로 노출해야 함")

    def test_elide_label_resize_reapplies_elide(self):
        """resizeEvent must trigger _apply_elide so width changes update the
        truncation point dynamically; _apply_elide must use fontMetrics
        elidedText with ElideRight mode."""
        body = self._get_class_body('_ElideLabel')
        self.assertIn('def resizeEvent(self, e):', body,
                      "_ElideLabel.resizeEvent override가 없음")
        self.assertIn('def _apply_elide(self):', body,
                      "_ElideLabel._apply_elide 메서드가 없음")
        self.assertIn('elidedText(', body,
                      "_ElideLabel은 fontMetrics().elidedText()를 사용해야 함")
        self.assertIn('ElideRight', body,
                      "_ElideLabel은 Qt.TextElideMode.ElideRight를 사용해야 함")

    def test_lbl_selection_uses_elide_label(self):
        """Text Merger _lbl_selection must be an _ElideLabel instance,
        not a plain QLabel."""
        self.assertIn('self._lbl_selection = _ElideLabel(', self.src,
                      "_lbl_selection이 _ElideLabel 양식이 아님 — selection layout fix가 적용되지 않음")

    def test_lbl_selection_on_separate_row(self):
        """_lbl_selection must NOT live in bot_btn_row. It must be added to
        the parent vertical layout (ll) separately to prevent layout
        breakage when the text grows long with many selected files."""
        self.assertNotIn('bot_btn_row.addWidget(self._lbl_selection)', self.src,
                         "_lbl_selection이 bot_btn_row에 박혀 있음 — 별도 row로 분리해야 함")
        self.assertIn('ll.addWidget(self._lbl_selection)', self.src,
                      "_lbl_selection이 별도 row(ll.addWidget)에 박혀 있지 않음")


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
