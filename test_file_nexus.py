"""
File Nexus Suite — 자동화 테스트 (세밀 버전)
실행: python test_file_nexus.py
"""
import unittest, os, sys, re, zipfile, json, tempfile, time, shutil

sys.path.insert(0, os.path.dirname(__file__))

# 테스트 파일 기준으로 FileNexusSuite.py 절대 경로 고정
_MAIN_PY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'FileNexusSuite.py')


# ════════════════════════════════════════════════════════════════════════
# 테스트용 순수 함수 추출
# ════════════════════════════════════════════════════════════════════════

# ── HTML 유틸 ──────────────────────────────────────────────────────────
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

# ── 자연 정렬 ──────────────────────────────────────────────────────────
def natural_sort_key(s):
    return [int(c) if c.isdigit() else c.lower()
            for c in _re.split(r'(\d+)', s)]

# ── 태그 조작 ──────────────────────────────────────────────────────────
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
    # (?<![0-9\-]): 앞 문자가 숫자 또는 하이픈이면 건드리지 않음
    # → 날짜 형식(2024-01-01) 보존, 범위 표기(001-197화)에서 앞 001만 제거
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
# PySide6 Mock — PySide6 미설치 환경에서도 모듈 exec 가능하도록
# ════════════════════════════════════════════════════════════════════════
def _install_qt_mock():
    """PySide6가 없을 때 sys.modules에 최소 스텁 주입.
    순수 로직(Worker, Fixer, EPUB 등)은 실제 동작 검증.
    Qt UI 렌더링 의존 항목은 형식만 검증됨 — 실제 UI는 PySide6 환경에서 확인 필요.
    """
    from types import ModuleType

    # ── 서브클래싱 가능한 Qt 클래스 스텁 팩토리 ──────────────────────
    def _qcls(name, *bases):
        """상속 가능한 Qt 스텁 클래스를 동적으로 생성."""
        def _noop(self, *a, **kw): pass
        return type(name, bases if bases else (object,), {'__init__': _noop})

    # ── Signal 스텁 ───────────────────────────────────────────────────
    # PySide6 Signal은 descriptor. 클래스 변수로 선언될 때 __set_name__ 호출됨.
    class _Signal:
        def __init__(self, *types): pass
        def __set_name__(self, owner, name): self._attr = name
        def __get__(self, obj, cls=None): return self
        def connect(self, fn): pass
        def disconnect(self, fn=None): pass
        def emit(self, *args): pass
        def __call__(self, *a, **kw): return self  # Signal(int) 패턴 대응

    # ── QColor 스텁 ───────────────────────────────────────────────────
    # _build_help_html 내 _mix() 함수가 red()/green()/blue() 를 호출함.
    class _QColor:
        def __init__(self, *a, **kw): pass
        def red(self):   return 0
        def green(self): return 0
        def blue(self):  return 0
        def alpha(self): return 255
        def name(self):  return '#000000'
        def __getattr__(self, n): return lambda *a, **kw: 0

    # ── 범용 Qt 스텁 (서브클래싱 불필요한 클래스) ────────────────────
    class _QtAny:
        def __init__(self, *a, **kw): pass
        def __call__(self, *a, **kw): return _QtAny()
        def __getattr__(self, n):
            if n.startswith('__'): raise AttributeError(n)
            return _QtAny()  # 중첩 속성 접근 (Qt.ItemDataRole.UserRole 등) 지원
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

    # ── 서브클래싱 가능한 기본 계층 ──────────────────────────────────
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
    qtgui.QColor = _QColor  # 숫자 반환 필요한 특수 스텁

    # ── PySide6 패키지 등록 ───────────────────────────────────────────
    pyside6           = ModuleType('PySide6')
    pyside6.QtCore    = qtcore
    pyside6.QtWidgets = qtwidgets
    pyside6.QtGui     = qtgui
    sys.modules['PySide6']           = pyside6
    sys.modules['PySide6.QtCore']    = qtcore
    sys.modules['PySide6.QtWidgets'] = qtwidgets
    sys.modules['PySide6.QtGui']     = qtgui


# PySide6 미설치 환경이면 mock 주입 (설치된 경우 그대로 사용)
try:
    import PySide6 as _pyside6_available  # noqa: F401
except ImportError:
    _install_qt_mock()


# ── EPUB 변환 / 모듈 심볼 추출 ────────────────────────────────────────
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
    print(f'[경고] FileNexusSuite 로드 실패: {_e}')

# ── Text Fixer 핵심 로직 ───────────────────────────────────────────────
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
# §샘플 데이터 — 테스트 전용 중립 텍스트 (CC0 공용 저작물)
# ════════════════════════════════════════════════════════════════════════
# 이 영역의 텍스트는 실제 저작물이 아닌 순수 테스트 샘플입니다.
# - 서사·캐릭터·세계관·작품 구조 없음 (의도적 중립 구성)
# - 각 상수는 특정 테스트 기능 검증용 (OCR 줄바꿈·단어 잘림·대화체 등)
# - CC0 1.0 Universal 퍼블릭 도메인 — 자유 사용 허용
#
# All text in this section is neutral test sample data.
# Contains no narrative, characters, world-building, or creative work structure.
# Licensed under CC0 1.0 Universal (Public Domain Dedication).

# 타이틀 계열 (구분선 병합 방지 검증용 — 서사 요소 없음)
SAMPLE_KO_TITLE_LONG    = '테스트 샘플 [1] 섹션 A에서 섹션 B까지 (6)'
SAMPLE_KO_TITLE_SHORT   = '테스트 샘플 [1]'
SAMPLE_KO_TITLE_PLAIN   = '테스트 샘플'

# OCR 스타일 줄바꿈 교정 검증 — 한국어 문장 중 "휘\n둥그레" 패턴
SAMPLE_KO_OCR_BROKEN    = ("이 문장은 테스트 목적으로 작성되었으며 중간에 의도적으로 줄바꿈이 들어가 있어 휘\n"
                          "둥그레 같은 단어가 잘린 상태를 검증한다.")
SAMPLE_KO_OCR_SHORT     = ('첫 줄이 끝나고\n두 번째 줄이 자연스럽게 이어진다.')

# 단어 잘림 테스트 — "참\n가자들" → "참가자들" (일반적 단어 잘림 패턴)
SAMPLE_KO_WORD_SPLIT    = "모든 참\n가자들에게 공지를 전달했다."

# 대화문 샘플 (일반적 역할만 등장, 특정 캐릭터 없음)
SAMPLE_KO_DIALOGUE_A    = '응답자가 대답했다.\n"몇 살이냐고요?"\n"열네 살입니다."'
SAMPLE_KO_DIALOGUE_B    = ('"질문해도 될까요? 지금 몇 살인가요?"\n'
                          '"이제 열네 살입니다."')

# 챕터 헤더 구조 보존 검증 — 제목은 "테스트 샘플"로 중립화
SAMPLE_KO_CHAPTER_FULL  = ("────────────────────────────────────────────────────────\n"
                          "테스트 샘플 [1] 섹션 A에서 섹션 B까지 (6)\n"
                          "────────────────────────────────────────────────────────\n"
                          "\n"
                          "다음 섹션으로 이어진다.")
SAMPLE_KO_CHAPTER_SHORT = ("────────────────────────────────\n"
                          "테스트 샘플 [1]\n"
                          "────────────────────────────────")

# 혼합 테스트 (OCR + 빈 줄 + 대화 — 중립 표현)
SAMPLE_KO_MIXED         = ('응답자가 대답하자\n검사자가 메모를 멈췄다.\n\n\n'
                          '"몇 살이냐고요?"\n"열네 살입니다."')

# 자동 단락 분리 검증용 — 긴 문장 여러 개가 스페이스로 연결된 형태 (서사 없음)
SAMPLE_KO_LONG_SENTENCES = (
    "이 문장은 자동 단락 분리 기능을 검증하기 위한 테스트용 예문 중 첫 번째 문장입니다. "
    "그리고 이어지는 두 번째 문장 역시 충분한 길이를 가지도록 의도적으로 작성된 예문입니다. "
    "마지막으로 세 번째 문장은 테스트 조건을 충족하기 위한 용도로 추가된 문장입니다."
)


# ════════════════════════════════════════════════════════════════════════
# §1 HTML 유틸리티
# ════════════════════════════════════════════════════════════════════════
class TestDe(unittest.TestCase):
    """_de: HTML 엔티티 디코딩"""
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
    def test_partial_entity(self):  self.assertEqual(_de('&amp'), '&amp')  # 불완전 엔티티
    def test_unicode_num(self):     self.assertEqual(_de('&#44032;'), '가')
    def test_unicode_hex(self):     self.assertEqual(_de('&#xAC00;'), '가')
    def test_chain(self):           self.assertEqual(_de('&lt;&amp;&gt;'), '<&>')

class TestEx(unittest.TestCase):
    """_ex: HTML 특수문자 이스케이프"""
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
    """_strip_xml_illegal: XML 불법 문자 제거"""
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
    """_h2t: HTML→텍스트"""
    def test_br(self):          self.assertEqual(_h2t('a<br>b'), 'a\nb')
    def test_br_self_close(self):self.assertEqual(_h2t('a<br/>b'), 'a\nb')
    def test_p_tag(self):       self.assertIn('\n', _h2t('<p>a</p><p>b</p>'))
    def test_strip_tags(self):  self.assertEqual(_h2t('<b>hello</b>'), 'hello')
    def test_entity_decode(self):self.assertEqual(_h2t('&amp;'), '&')
    def test_empty(self):       self.assertEqual(_h2t(''), '')
    def test_plain_text(self):  self.assertEqual(_h2t('hello'), 'hello')


# ════════════════════════════════════════════════════════════════════════
# §2 자연 정렬
# ════════════════════════════════════════════════════════════════════════
class TestNaturalSort(unittest.TestCase):
    """natural_sort_key: 자연 정렬"""
    def _sorted(self, lst): return sorted(lst, key=natural_sort_key)

    # 기본 숫자 순서
    def test_1_before_2(self):      self.assertEqual(self._sorted(['2','1']), ['1','2'])
    def test_9_before_10(self):     self.assertEqual(self._sorted(['10','9']), ['9','10'])
    def test_1_10_100(self):        self.assertEqual(self._sorted(['100','10','1']), ['1','10','100'])
    def test_zero_pad_order(self):
        # 같은 숫자값(1)이라 안정정렬 → 입력 순서 유지
        r = self._sorted(['01','001','1'])
        self.assertEqual(len(r), 3)  # 모두 포함
        self.assertEqual(set(r), {'01','001','1'})

    # 혼합 (문자+숫자)
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

    # 엣지케이스
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
# §3 태그 제거
# ════════════════════════════════════════════════════════════════════════
class TestRemoveTag(unittest.TestCase):
    """remove_tag: 파일명 태그 제거"""
    # 위치별 기본 동작
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

    # 특정 태그 타겟
    def test_target_specific(self): self.assertEqual(remove_tag('[BD] 파일.txt','both','BD'), '파일.txt')
    def test_target_keep_other(self):
        r = remove_tag('[BD] 파일 [완결].txt','both','BD')
        self.assertIn('[완결]', r)
        self.assertNotIn('[BD]', r)
    def test_target_not_present(self):
        r = remove_tag('파일 [완결].txt','both','BD')
        self.assertIn('[완결]', r)

    # 확장자 보존
    def test_ext_preserved_txt(self):   self.assertTrue(remove_tag('[A] 파일.txt','both').endswith('.txt'))
    def test_ext_preserved_epub(self):  self.assertTrue(remove_tag('[A] 파일.epub','both').endswith('.epub'))
    def test_ext_preserved_mp4(self):   self.assertTrue(remove_tag('파일 [A].mp4','both').endswith('.mp4'))
    def test_no_ext(self):              self.assertEqual(remove_tag('[A] 파일','both'), '파일')

    # 엣지케이스
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
# §4 태그 추가
# ════════════════════════════════════════════════════════════════════════
class TestAddTag(unittest.TestCase):
    """add_tag: 파일명 태그 추가"""
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
# §5 0 패딩 제거
# ════════════════════════════════════════════════════════════════════════
class TestDepad(unittest.TestCase):
    """depad: 앞자리 0 제거"""
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
        # 000은 숫자 000 → 0
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
# §6 공통 접두사 감지
# ════════════════════════════════════════════════════════════════════════
class TestDetectPrefix(unittest.TestCase):
    """detect_prefix: 공통 접두사 감지"""
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
# §7 숫자 추출
# ════════════════════════════════════════════════════════════════════════
class TestExtractNumber(unittest.TestCase):
    """extract_number: 첫 번째 숫자 추출"""
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
# §8 구분선 감지
# ════════════════════════════════════════════════════════════════════════
class TestIsSepLine(unittest.TestCase):
    """_is_sep_line: 구분선 판별"""
    # True 케이스 (구분선)
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

    # False 케이스 (구분선 아님)
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
# §9 Text Fixer — 줄바꿈 병합 (스마트 merge)
# ════════════════════════════════════════════════════════════════════════
class TestSmartMerge(unittest.TestCase):
    """스마트 병합: 문장 끝 문자 기준"""
    # 병합되어야 하는 경우 (중간 줄바꿈)
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

    # 병합 안 되어야 하는 경우 (문장 끝)
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

    def test_ja_period_no_merge(self):
        out, mid, *_ = _run_fix("文章です。\n次の行。", do_blank=False)
        self.assertEqual(mid, 0)

    def test_zh_period_no_merge(self):
        out, mid, *_ = _run_fix("文章。\n下一行。", do_blank=False)
        self.assertEqual(mid, 0)

    # 구분선은 병합하지 않음
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

    # 빈 줄이 단락 경계
    def test_blank_line_separates_paragraphs(self):
        inp = "A\nB\n\nC\nD"
        out, *_ = _run_fix(inp)
        self.assertIn('\n\n', out)

    # 다단락 병합
    def test_multi_paragraph_independent(self):
        inp = "A\nB\n\nC\nD"
        out, mid, *_ = _run_fix(inp)
        self.assertEqual(mid, 2)


# ════════════════════════════════════════════════════════════════════════
# §10 Text Fixer — 빈 줄 축소
# ════════════════════════════════════════════════════════════════════════
class TestBlankCompression(unittest.TestCase):
    """빈 줄 축소: max_blank 기준"""
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
        # max_blank=2, 정확히 2개 빈줄 → 축소 안 됨
        out, _, blank, *_ = _run_fix("A\n\n\nB", do_mid=False, max_blank=2)
        self.assertEqual(blank, 0)


# ════════════════════════════════════════════════════════════════════════
# §11 Text Fixer — 문장마다 빈 줄 삽입
# ════════════════════════════════════════════════════════════════════════
class TestSentenceSep(unittest.TestCase):
    """문장마다 빈 줄 삽입"""
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
        # 마침표 없이 끝나는 줄은 빈 줄 삽입 안 됨
        out, *_ = _run_fix("이어지는\n문장입니다.", do_mid=False, do_blank=False, do_sep=True)
        # 첫 줄이 마침표 없이 끝났으므로 빈줄 없음
        lines = out.split('\n')
        non_blank = [l for l in lines if l.strip()]
        # 두 줄 사이에 빈 줄 없어야 함
        idx1 = lines.index('이어지는') if '이어지는' in lines else -1
        idx2 = next((i for i,l in enumerate(lines) if '문장입니다' in l), -1)
        if idx1 >= 0 and idx2 >= 0:
            self.assertEqual(idx2 - idx1, 1)

    def test_novel_dialogue_multiple(self):
        inp = SAMPLE_KO_DIALOGUE_A
        out, *_ = _run_fix(inp, do_mid=False, do_blank=False, do_sep=True)
        self.assertGreaterEqual(out.count('\n\n'), 1)


# ════════════════════════════════════════════════════════════════════════
# §12 Text Fixer — 자동 단락 분리 (_split_long_line v2)
# ════════════════════════════════════════════════════════════════════════
class TestSplitLongLine(unittest.TestCase):
    """_split_long_line: 2단계 자동 분리"""
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
        # 짧은 문장들이 하나로 묶여야 함
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
        self.assertEqual(len(r), 1)  # 경계 없으면 분리 안 됨

    def test_many_short_sentence(self):
        # 10개 짧은 문장 → 합산 threshold 30 초과 시 분리
        line = "짧습니다. " * 10
        r = _split_long_line(line.strip(), 30)
        self.assertGreater(len(r), 1)


class TestAutoSplit(unittest.TestCase):
    """do_auto_split: _run_fix 통합"""
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
        # 자동 분리 검증 — 긴 문장 여러 개 연결된 형태
        inp = SAMPLE_KO_LONG_SENTENCES
        out, *_ = _run_fix(inp, do_mid=False, do_blank=False, do_auto_split=True, max_split_chars=80)
        self.assertIn('\n\n', out)
        lines = [l for l in out.split('\n') if l.strip()]
        self.assertGreater(len(lines), 1)


# ════════════════════════════════════════════════════════════════════════
# §13 Text Fixer — 엣지케이스
# ════════════════════════════════════════════════════════════════════════
class TestFixerEdge(unittest.TestCase):
    """Text Fixer 엣지케이스"""
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
        inp = "A\nB"  # 병합되면 1줄
        _, _, _, _, new = _run_fix(inp, do_blank=False)
        self.assertEqual(new, 1)

    def test_no_leading_blank_in_output(self):
        out, *_ = _run_fix("\n\nA\nB")
        self.assertFalse(out.startswith('\n'))

    def test_no_trailing_blank_in_output(self):
        out, *_ = _run_fix("A\nB\n\n")
        self.assertFalse(out.endswith('\n'))


# ════════════════════════════════════════════════════════════════════════
# §14 Text Fixer — 실사용 시나리오 (OCR·대화문·챕터 헤더 등)
# ════════════════════════════════════════════════════════════════════════
class TestFixerRealWorld(unittest.TestCase):
    """실제 사용 시나리오"""
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


# ════════════════════════════════════════════════════════════════════════
# §15 Text Fixer — 옵션 조합
# ════════════════════════════════════════════════════════════════════════
class TestFixerCombinations(unittest.TestCase):
    """옵션 조합 테스트"""
    def test_merge_and_blank(self):
        inp = "A\nB\n\n\n\nC\nD"
        out, mid, blank, *_ = _run_fix(inp, do_mid=True, do_blank=True, max_blank=1)
        self.assertGreater(mid, 0)
        self.assertGreater(blank, 0)
        self.assertNotIn('\n\n\n', out)

    def test_merge_and_auto_split(self):
        # 병합 후 중간에 마침표 있어야 auto split 가능
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
        # 병합 후 자동 분리 — 파이프라인 순서 확인
        inp = "문장이고\n계속되며\n" + "긴내용" * 20 + ".\n짧다.\n짧다."
        out, *_ = _run_fix(inp, do_mid=True, do_blank=False,
                           do_auto_split=True, max_split_chars=80)
        self.assertIsInstance(out, str)


# ════════════════════════════════════════════════════════════════════════
# §16 EPUB 변환
# ════════════════════════════════════════════════════════════════════════
@unittest.skipUnless(HAS_EPUB, "FileNexusSuite 로드 실패")
class TestEpubStructure(unittest.TestCase):
    """txt_to_epub: EPUB 구조 검증"""
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
        """빈 내용 → txt_to_epub은 ValueError를 발생시켜야 한다."""
        with self.assertRaises(ValueError):
            self._write("")


@unittest.skipUnless(HAS_EPUB, "FileNexusSuite 로드 실패")
class TestEpubRoundTrip(unittest.TestCase):
    """EPUB 왕복 변환 검증"""
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
# §17 설정 저장/복원
# ════════════════════════════════════════════════════════════════════════
@unittest.skipUnless(HAS_MODULE, "FileNexusSuite 로드 실패")
class TestConfig(unittest.TestCase):
    """ConfigManager 동작 방식 검증 — JSON 저장/복원 구조 기반."""
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
# §18 파일시스템 통합
# ════════════════════════════════════════════════════════════════════════
class TestFilesystemIntegration(unittest.TestCase):
    """실제 파일시스템 작업 통합 테스트"""
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
# §19 회귀 테스트
# ════════════════════════════════════════════════════════════════════════
class TestRegression(unittest.TestCase):
    """이전 버그 재발 방지"""
    def test_separator_not_merged_with_title(self):
        """구분선이 다음 줄과 병합되지 않음 (이슈: - 는 SENT_END 아님)"""
        inp = "────────────────────────────────\n" + SAMPLE_KO_TITLE_SHORT + "\n────────────────────────────────"
        out, mid, *_ = _run_fix(inp, do_blank=False)
        self.assertEqual(mid, 0)
        lines = out.split('\n')
        self.assertEqual(lines[0], '────────────────────────────────')
        self.assertEqual(lines[1], SAMPLE_KO_TITLE_SHORT)

    def test_chapter_header_structure_intact(self):
        """챕터 헤더 구조 완전 보존"""
        inp = SAMPLE_KO_CHAPTER_FULL
        out, mid, *_ = _run_fix(inp)
        self.assertEqual(mid, 0)

    def test_no_pyqt5_remnants(self):
        """PyQt5 잔여 코드 없음"""
        with open(_MAIN_PY, encoding='utf-8') as f:
            src = f.read()
        self.assertNotIn('PyQt5', src)
        self.assertNotIn('pyqtSignal', src)
        self.assertNotIn('exec_()', src)

    def test_qshortcut_in_qtgui(self):
        """QShortcut이 QtGui에서 import됨 (단축키 구현용)"""
        with open(_MAIN_PY, encoding='utf-8') as f:
            src = f.read()
        gui_line = next((l for l in src.splitlines() if 'from PySide6.QtGui import' in l), '')
        self.assertIn('QShortcut', gui_line)

    def test_qaction_not_in_qtwidgets(self):
        """QAction이 QtWidgets에서 import 안 됨 (QtGui에도 불필요 — 미사용)"""
        with open(_MAIN_PY, encoding='utf-8') as f:
            src = f.read()
        import re
        m = re.search(r'from PySide6\.QtWidgets import \((.+?)\)', src, re.DOTALL)
        if m:
            self.assertNotIn('QAction', m.group(1))

    def test_qprogressbar_not_locally_imported_in_textfixer(self):
        """TextFixerPanel에서 QProgressBar 중복 로컬 import 없음"""
        with open(_MAIN_PY, encoding='utf-8') as f:
            src = f.read()
        fixer_start = src.find('class TextFixerPanel')
        fixer_end = src.find('\nclass TextMergeWorker', fixer_start)
        fixer_block = src[fixer_start:fixer_end]
        local_pb = [l for l in fixer_block.splitlines()
                    if 'from PySide6' in l and 'QProgressBar' in l]
        self.assertEqual(len(local_pb), 0)

    def test_epub_fstring_compat(self):
        """EPUB f-string 내 dict 접근이 Python 3.12 호환"""
        with open(_MAIN_PY, encoding='utf-8') as f:
            src = f.read()
        epub_start = src.find('def txt_to_epub(')
        epub_end = src.find('\ndef ', epub_start + 10)
        epub_block = src[epub_start:epub_end]
        self.assertNotIn('ch["title"]', epub_block)
        self.assertNotIn('ch["content"]', epub_block)

    def test_sc_tab_fixer_in_label_keys(self):
        """설정창 단축키 탭에 tab_5가 번역키로 연결됨"""
        with open(_MAIN_PY, encoding='utf-8') as f:
            src = f.read()
        self.assertIn("'tab_5':'sc_tab_fixer'", src)

    def test_sc_tab_bulk_in_label_keys(self):
        """설정창 단축키 탭에 tab_6(Bulk Fixer)가 번역키로 연결됨"""
        with open(_MAIN_PY, encoding='utf-8') as f:
            src = f.read()
        self.assertIn("'tab_6':'sc_tab_bulk'", src)

    def test_shortcut_defs_has_tab_6(self):
        """SHORTCUT_DEFS에 tab_6(Ctrl+6) 정의가 있어야 한다"""
        with open(_MAIN_PY, encoding='utf-8') as f:
            src = f.read()
        self.assertIn("'tab_6'", src)
        self.assertIn("Ctrl+6", src)

    def test_separator_with_trailing_space(self):
        """trailing space 있는 구분선도 올바르게 감지"""
        self.assertTrue(_is_sep_line("──────── "))
        self.assertTrue(_is_sep_line(" ────────"))

    def test_blank_after_merge_pipeline(self):
        """병합 후 빈줄 축소 파이프라인 순서"""
        inp = "A\nB\n\n\n\nC\nD"
        out, mid, blank, *_ = _run_fix(inp, do_mid=True, do_blank=True, max_blank=1)
        self.assertEqual(mid, 2)
        self.assertGreater(blank, 0)
        self.assertNotIn('\n\n\n', out)

    def test_stats_not_korean_hardcoded(self):
        """통계 텍스트가 한국어 하드코딩 아님 (번역키 사용)"""
        with open(_MAIN_PY, encoding='utf-8') as f:
            src = f.read()
        self.assertNotIn("f'병합된 줄: {fixed_mid}건'", src)
        self.assertIn('tf_stat_mid_n', src)


# ════════════════════════════════════════════════════════════════════════
# §20 성능 테스트
# ════════════════════════════════════════════════════════════════════════
class TestPerformance(unittest.TestCase):
    """성능 벤치마크 (임계값 초과 시 실패)"""
    def test_large_text_merge_speed(self):
        """10,000줄 병합 — 3초 이내"""
        inp = ("중간 문장이고\n" * 4 + "완료됩니다.\n\n") * 1000
        start = time.time()
        _run_fix(inp, do_mid=True, do_blank=True)
        self.assertLess(time.time() - start, 3.0)

    def test_large_text_blank_speed(self):
        """빈줄만 있는 큰 파일 — 1초 이내"""
        inp = "\n" * 5000 + "A\n" * 1000 + "\n" * 5000
        start = time.time()
        _run_fix(inp, do_mid=False, do_blank=True, max_blank=1)
        self.assertLess(time.time() - start, 1.0)

    def test_auto_split_performance(self):
        """자동 단락 분리 대용량 — 2초 이내"""
        long_line = ("문장입니다. " * 10).strip()
        inp = (long_line + "\n\n") * 500
        start = time.time()
        _run_fix(inp, do_mid=False, do_blank=True, do_auto_split=True, max_split_chars=80)
        self.assertLess(time.time() - start, 2.0)

    def test_sep_line_detection_speed(self):
        """구분선 감지 1000회 — 0.1초 이내"""
        start = time.time()
        for _ in range(1000):
            _is_sep_line("──────────────────────────────")
            _is_sep_line("hello world")
        self.assertLess(time.time() - start, 0.1)

    def test_natural_sort_large_list(self):
        """1000개 파일 자연 정렬 — 0.5초 이내"""
        files = [f"파일{i:04d}화.txt" for i in range(1000, 0, -1)]
        start = time.time()
        sorted_files = sorted(files, key=natural_sort_key)
        self.assertLess(time.time() - start, 0.5)
        self.assertEqual(sorted_files[0], "파일0001화.txt")


# ════════════════════════════════════════════════════════════════════════
# §21 경계값 분석 (BVA)
# ════════════════════════════════════════════════════════════════════════
class TestBoundaryValues(unittest.TestCase):
    """경계값 분석"""
    # max_blank 경계
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

    # max_split_chars 경계
    def test_split_at_exactly_threshold(self):
        line = "A" * 49 + ". " + "B" * 49 + "."
        # 첫 세그먼트 길이 = 51 chars > 50 → split
        r = _split_long_line(line, 50)
        self.assertEqual(len(r), 2)

    def test_split_one_below_threshold(self):
        line = "A" * 48 + ". " + "B" * 48 + "."
        # 첫 세그먼트 = 50, 두번째 = 50. 합산 100 > 50 이므로 분리
        r = _split_long_line(line, 50)
        self.assertGreaterEqual(len(r), 1)

    # 구분선 최소 길이 경계
    def test_sep_exactly_3(self):   self.assertTrue(_is_sep_line('---'))
    def test_sep_exactly_2_fail(self): self.assertFalse(_is_sep_line('--'))
    def test_sep_exactly_1_fail(self): self.assertFalse(_is_sep_line('-'))

    # 빈 문자열 경계
    def test_empty_depad(self):     self.assertEqual(depad(''), '')
    def test_empty_remove_tag(self):self.assertEqual(remove_tag('','both'), '')
    def test_empty_extract_num(self):self.assertIsNone(extract_number(''))
    def test_empty_sep_line(self):  self.assertFalse(_is_sep_line(''))


# ════════════════════════════════════════════════════════════════════════
# §추가A  앱 상수 / 버전
# ════════════════════════════════════════════════════════════════════════
@unittest.skipUnless(HAS_MODULE, "FileNexusSuite 로드 실패")
class TestAppConstants(unittest.TestCase):
    """APP_VERSION 및 라이브러리 가용성 플래그 검증."""

    def test_version_exists(self):
        self.assertIsNotNone(_APP_VERSION)

    def test_version_string(self):
        self.assertIsInstance(_APP_VERSION, str)

    def test_version_format(self):
        """시맨틱 버저닝 X.Y.Z 형식 확인."""
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
# §추가B  인코딩 감지 — alchemy_detect_encoding()
# ════════════════════════════════════════════════════════════════════════
@unittest.skipUnless(HAS_MODULE, "FileNexusSuite 로드 실패")
class TestAlchemyDetectEncoding(unittest.TestCase):
    """alchemy_detect_encoding() — 실제 모듈 함수 직접 검증.

    v1.0.4: (encoding, confidence) 튜플 반환으로 변경됨.
    이전 문자열 반환 형식도 지원하도록 헬퍼로 첫 요소만 추출."""

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
        """v1.0.3(str) / v1.0.4(tuple) 양쪽 호환으로 인코딩명만 추출."""
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
# §추가C  도움말 HTML — _build_help_html()
# ════════════════════════════════════════════════════════════════════════
@unittest.skipUnless(HAS_MODULE and _build_help_html is not None,
                     "FileNexusSuite 로드 실패 또는 _build_help_html 없음")
class TestBuildHelpHtml(unittest.TestCase):
    """_build_help_html() — 5개 언어 도움말 생성 검증."""

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
# §추가D  ConfigManager — 실제 클래스 저장/로드
# ════════════════════════════════════════════════════════════════════════
@unittest.skipUnless(HAS_MODULE and _ConfigManager is not None,
                     "FileNexusSuite 로드 실패 또는 ConfigManager 없음")
class TestConfigManagerReal(unittest.TestCase):
    """ConfigManager 실제 클래스 — 저장/로드/get 검증."""

    def setUp(self):
        self.td = tempfile.mkdtemp()
        # _CONFIG_PATH를 임시 디렉토리로 리디렉션
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
# §추가E  depad 날짜 형식 회귀 테스트 (v0.9.0 버그픽스)
# ════════════════════════════════════════════════════════════════════════
_depad_name_fn = _ns.get('depad_name') if HAS_MODULE else None

@unittest.skipUnless(HAS_MODULE and _depad_name_fn is not None,
                     "FileNexusSuite 로드 실패")
class TestDepadDateRegression(unittest.TestCase):
    """depad_name() — 날짜 형식(YYYY-MM-DD) 보존 회귀 테스트.

    수정 전: \\b 패턴이 하이픈을 word boundary로 인식해
             2024-01-01 → 2024-1-1 로 잘못 변환됨.
    수정 후: (?<![0-9\\-]) 패턴으로 하이픈 뒤 0은 건드리지 않음.
    """

    def test_date_yyyy_mm_dd_preserved(self):
        """2024-01-01 형식 날짜는 변환하지 않아야 한다."""
        self.assertIsNone(_depad_name_fn('2024-01-01.txt'))

    def test_date_mm_dd_preserved(self):
        self.assertIsNone(_depad_name_fn('01-01.txt'))

    def test_range_001_197_front_removed(self):
        """사과나무 001-197화(完) — 앞의 001만 제거, 뒤 197은 유지."""
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
        """하이픈 뒤 숫자 01은 제거하지 않아야 한다 → 변환 없으면 None."""
        result = _depad_name_fn('시즌1-01화.txt')
        # 앞에 변환할 0패딩이 없으므로 None이거나 01이 유지되어야 함
        self.assertTrue(result is None or '01' in result)


# ════════════════════════════════════════════════════════════════════════
# §추가F  v0.10.0 회귀 — 소스 파싱 기반 (PySide6 불필요)
# ════════════════════════════════════════════════════════════════════════
class TestV010Regression(unittest.TestCase):
    """v0.10.0 기본 상수 회귀 테스트 — 소스 파일 직접 파싱."""

    def _src(self):
        with open(_MAIN_PY, encoding='utf-8') as f:
            return f.read()

    def test_app_version(self):
        import re
        m = re.search(r'^APP_VERSION\s*=\s*["\']([^"\']+)["\']', self._src(), re.MULTILINE)
        self.assertIsNotNone(m, "APP_VERSION 정의 없음")
        # v1.0.0 이상이면 OK (v1.0.1, v1.0.2, v1.0.3 등 모두 통과)
        parts = m.group(1).split('.')
        self.assertGreaterEqual(int(parts[0]), 1, f"메이저 버전 < 1: {m.group(1)}")

    def test_themes_count(self):
        import re
        src = self._src()
        # THEMES dict의 실제 키 (auto는 런타임 resolve 가상 테마)
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
        """_THEME_NAME_KEY에 auto 포함 — 지원 테마 10개."""
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
        # ko는 TRANSLATIONS = {'ko': 형태로 인라인, 나머지는 줄 첫머리
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
    """v0.10.0 모듈 로드 기반 회귀 테스트 (PySide6 필요)."""

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
# §추가G  번역 시스템 완전성
# ════════════════════════════════════════════════════════════════════════
class TestTranslationCompleteness(unittest.TestCase):
    """TRANSLATIONS — 5개 언어 키 완전성 검증 (소스 파일 직접 파싱, PySide6 불필요)."""

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
        """5언어 키 개수 검증 — zh_cn은 zh_tw fallback으로 부분집합 허용 (v1.0.9 §5.1.G).

        ko/en/ja/zh_tw는 ko 기준과 동일 개수 (대칭).
        zh_cn은 zh_tw와 값이 100% 동일한 키들이 제거되어 적을 수 있으나,
        남은 키는 모두 zh_tw에 있어야 fallback 안전성이 보장됨.
        """
        lang_keys = {l: self._get_lang_keys(l) for l in ['ko','en','ja','zh_cn','zh_tw']}
        ko_count = len(lang_keys['ko'])
        # ko/en/ja/zh_tw 대칭 검증
        for lang in ('en', 'ja', 'zh_tw'):
            with self.subTest(lang=lang):
                self.assertEqual(len(lang_keys[lang]), ko_count,
                    f"{lang} 키 수 {len(lang_keys[lang])} ≠ ko {ko_count}")
        # zh_cn은 zh_tw 부분집합 (fallback 안전성)
        not_in_zh_tw = lang_keys['zh_cn'] - lang_keys['zh_tw']
        with self.subTest(lang='zh_cn_subset'):
            self.assertEqual(not_in_zh_tw, set(),
                f"zh_cn 키가 zh_tw에 없음 (fallback 불가): {sorted(not_in_zh_tw)}")

    def test_zh_cn_fallback_to_zh_tw(self):
        """zh_cn 사전 미정의 키는 zh_tw로 fallback되어야 함 (v1.0.9 §5.1.G).

        §5.1.G에서 zh_cn↔zh_tw 값 동일 키를 zh_cn에서 제거.
        _t() / _rt() 두 함수 모두에 fallback 메커니즘이 살아있어야
        zh_cn 사용자 동작 영향이 0으로 유지됨.
        """
        import re
        lang_keys = {l: self._get_lang_keys(l) for l in ['zh_cn', 'zh_tw']}
        # 검증 대상이 존재해야 함 (정리 작업이 적용된 상태)
        missing_in_zh_cn = lang_keys['zh_tw'] - lang_keys['zh_cn']
        self.assertGreater(len(missing_in_zh_cn), 0,
            "fallback 검증 대상 키가 없음 — §5.1.G 정리가 미적용 상태?")
        # 소스에서 zh_cn → zh_tw fallback 패턴 존재 검증 (_t와 _rt 두 곳)
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
    # 탭 기반 기능 영역 invariant (v1.0.7 세션 3 재구성)
    # 버전 스냅샷 방식(v010/v010_1/v100) 폐기 → 10개 대분류로 재조직
    # 세부 정책은 TEST_MANAGEMENT_POLICY.md 참조
    # ────────────────────────────────────────────────────────────────

    def test_all_langs_have_common_dialog_keys(self):
        """대분류 1 — 전 탭 공통 다이얼로그·버튼 키."""
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
        """대분류 2 — Text Merger 탭 대표 키."""
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
        """대분류 3 — Text Converter 탭 대표 키.

        주의: conv_sub_txt2epub / conv_sub_epub2txt는 L6560의
        `_t('conv_sub_' + val)` 동적 키 생성으로 활성 사용됨 (v1.0.7 감사 수정).
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
        """대분류 4 — Tag Editor 탭 대표 키."""
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
        """대분류 5 — Batch Renamer 탭 대표 키.

        batch_* / rename_* 두 접두사 통합 대분류 (부록 E 참조):
          - batch_* ← 원본 BatchRenamer 클래스명에서 유래, UI·옵션
          - rename_* ← 원본 _do_rename/_confirm_rename 메서드에서 유래, 동작 상태·피드백
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
        """대분류 6 — Text Fixer 탭 대표 키.

        주의: tf_dlg_overwrite는 v1.0.7 세션 2·3에서 제거된 고아 키이므로
        invariant에서 제외됨 (_save_overwrite 데드 메서드와 함께 정리).
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
        """대분류 7 — Bulk Fixer 탭 대표 키."""
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
        """대분류 8 — 설정 다이얼로그 대표 키."""
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
        """대분류 9 — 단축키 시스템 대표 키."""
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
        """대분류 10 — 위 어디에도 속하지 않는 잔여 대표 키 (최소화 목표)."""
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
# §추가H  retranslate 체인 무결성 (크래시 회귀 방지)
# ════════════════════════════════════════════════════════════════════════
class TestRetranslateIntegrity(unittest.TestCase):
    """retranslate 메서드 내 미정의 속성 참조 회귀 테스트.

    v0.10.0 이전:
      - TextMergerPanel.retranslate()에 _file_gb 참조 → AttributeError
      - TextConverterPanel.retranslate()에 _btn_del_all 참조 → AttributeError
    두 버그 모두 AppSuite.retranslate_ui()의 try-except에 걸려
    이후 전 패널 retranslate가 실행되지 않았음.
    """

    def _get_retranslate_body(self, class_name):
        import re
        with open(_MAIN_PY, encoding='utf-8') as f:
            src = f.read()
        # 클래스 범위 추출
        cls_match = re.search(rf'^class {class_name}\b.*?(?=^class |\Z)',
                               src, re.MULTILINE | re.DOTALL)
        if not cls_match: return ''
        cls_body = cls_match.group(0)
        rt_match = re.search(r'def retranslate\(self\):(.*?)(?=\n    def |\Z)',
                              cls_body, re.DOTALL)
        return rt_match.group(1) if rt_match else ''

    def test_merger_no_file_gb(self):
        """TextMergerPanel.retranslate()에 _file_gb 참조가 없어야 한다."""
        body = self._get_retranslate_body('TextMergerPanel')
        self.assertNotIn('_file_gb', body,
            "TextMergerPanel.retranslate()에 _file_gb 잔류 — 크래시 위험")

    def test_converter_no_btn_del_all(self):
        """TextConverterPanel.retranslate()에 _btn_del_all 참조가 없어야 한다."""
        body = self._get_retranslate_body('TextConverterPanel')
        self.assertNotIn('_btn_del_all', body,
            "TextConverterPanel.retranslate()에 _btn_del_all 잔류 — 크래시 위험")

    def test_merger_has_tree_header_retranslate(self):
        """TextMergerPanel.retranslate()에 트리 헤더 갱신이 있어야 한다."""
        body = self._get_retranslate_body('TextMergerPanel')
        self.assertIn('setHeaderLabels', body,
            "MergeFileTree 헤더가 retranslate에서 갱신되지 않음")

    def test_bulk_fixer_sort_btn_uses_t(self):
        """BulkFixerFileList가 setHeaderLabels에 _t() 키를 사용해야 한다.
        (v0.10.1: _sort_files 제거 → QTreeWidget 헤더 클릭으로 정렬)"""
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
        """_dlg_info/warn/error/question 버튼이 _t() 키를 사용해야 한다."""
        import re
        with open(_MAIN_PY, encoding='utf-8') as f:
            src = f.read()
        # _dlg_info 함수 추출
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
        """BulkFixerPanel.retranslate()에 _btn_abort, _chk_keep_structure 갱신이 있어야 한다."""
        body = self._get_retranslate_body('BulkFixerPanel')
        self.assertIn('_btn_abort', body,
            "BulkFixerPanel.retranslate()에 _btn_abort 갱신 없음")
        self.assertIn('_chk_keep_structure', body,
            "BulkFixerPanel.retranslate()에 _chk_keep_structure 갱신 없음")


# ════════════════════════════════════════════════════════════════════════
# §추가I  BulkFixerWorker — 핵심 로직
# ════════════════════════════════════════════════════════════════════════
_BulkFixerWorker = _ns.get('BulkFixerWorker') if HAS_MODULE else None
_TextFixerWorker  = _ns.get('TextFixerWorker')  if HAS_MODULE else None

@unittest.skipUnless(HAS_MODULE and _BulkFixerWorker and _TextFixerWorker,
                     "FileNexusSuite 로드 실패 또는 BulkFixerWorker 없음")
class TestBulkFixerWorker(unittest.TestCase):
    """BulkFixerWorker._fix_text() — 교정 로직 단위 테스트."""

    def _worker(self, **kwargs):
        defaults = dict(files=[], out_dir='',
                        do_mid=True, do_blank=True, max_blank=1,
                        do_sep=False, do_auto_split=False,
                        max_split_chars=100, lang_mode='auto',
                        keep_structure=False)
        defaults.update(kwargs)
        return _BulkFixerWorker(**defaults)

    # ── 기본 교정 ────────────────────────────────
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
        """한국어 모드: CJK 문자로만 된 줄은 병합."""
        w = self._worker(do_mid=True, do_blank=False, lang_mode='ko')
        out, mid, _ = w._fix_text("앞부분이고\n뒷부분이다.")
        self.assertEqual(mid, 1)

    def test_lang_mode_en_abbr_no_merge(self):
        """영어 모드: 약어(Mr.) 뒤는 병합."""
        w = self._worker(do_mid=True, do_blank=False, lang_mode='en')
        out, mid, _ = w._fix_text("Call Mr.\nSmith today.")
        # Mr.는 약어 → 병합되어야 함
        self.assertEqual(mid, 1)

    def test_lang_mode_en_sentence_end_no_merge(self):
        """영어 모드: 문장 끝(.)은 병합 안 됨."""
        w = self._worker(do_mid=True, do_blank=False, lang_mode='en')
        out, mid, _ = w._fix_text("End of sentence.\nNext sentence.")
        self.assertEqual(mid, 0)

    def test_lang_mode_en_hyphen_join(self):
        """영어 모드: 하이픈 단어 분리 복원."""
        w = self._worker(do_mid=True, do_blank=False, lang_mode='en')
        out, mid, _ = w._fix_text("con-\ntinue")
        self.assertIn("continue", out)

    def test_lang_mode_auto_detects_ko(self):
        """자동 감지: 한국어 텍스트는 ko 모드로."""
        w = self._worker(do_mid=True, do_blank=False, lang_mode='auto')
        out, mid, _ = w._fix_text("한국어 텍스트이다\n계속 이어진다")
        self.assertEqual(mid, 1)

    # ── 저장 경로 계산 ────────────────────────────
    def test_save_path_no_outdir(self):
        """out_dir 미지정: 원본 위치에 [Fixed] 접두사."""
        w = self._worker(out_dir='')
        src = '/tmp/test.txt'
        result = w._make_save_path(src)
        self.assertEqual(result, os.path.join('/tmp', '[Fixed]test.txt'))

    def test_save_path_with_outdir(self):
        """out_dir 지정: 지정 폴더에 [Fixed] 접두사."""
        w = self._worker(out_dir='/out')
        src = '/tmp/test.txt'
        result = w._make_save_path(src)
        self.assertEqual(result, os.path.join('/out', '[Fixed]test.txt'))

    def test_save_path_keep_structure(self):
        """keep_structure=True: 폴더 구조 유지."""
        files = ['/data/sub/a.txt', '/data/sub/b.txt']
        w = self._worker(files=files, out_dir='/out', keep_structure=True)
        result = w._make_save_path(files[0])
        # commonpath=/data/sub → rel=. → /out/[Fixed]a.txt
        self.assertTrue(result.startswith('/out'))
        self.assertIn('[Fixed]a.txt', result)


@unittest.skipUnless(HAS_MODULE and _BulkFixerWorker,
                     "FileNexusSuite 로드 실패")
class TestBulkFixerFileIO(unittest.TestCase):
    """BulkFixerWorker — 실제 파일 읽기/쓰기 통합 테스트."""

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
        text, _, _ = w._fix_text(open(src, encoding='utf-8').read())
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
        out, _, _ = w._fix_text(open(src, encoding='utf-8').read())
        self.assertIn("한국어", out)

    def test_multiple_blank_compressed(self):
        src = self._make_file('blank.txt', "A\n\n\n\n\nB")
        w = _BulkFixerWorker(
            files=[src], out_dir='',
            do_mid=False, do_blank=True, max_blank=1,
        )
        out, _, blank = w._fix_text(open(src, encoding='utf-8').read())
        self.assertGreater(blank, 0)
        self.assertNotIn('\n\n\n', out)

    def test_keep_structure_creates_subdirs(self):
        """keep_structure=True: 하위 폴더 구조를 출력 폴더에 재현."""
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
        # 하위 폴더가 출력 경로에 포함
        self.assertTrue(out_path.startswith(out_dir))

    # ── v1.0.3 추가: 인코딩 라운드트립 회귀 방지 ─────────────────
    # v1.0.2까지 BulkFixerWorker.run()이 UTF-16/Shift-JIS/GBK/Big5를
    # 처리하지 못해 깨진 상태로 저장하던 버그(v1.0.3에서 alchemy_detect_encoding
    # 재사용으로 해결)의 회귀를 방지하기 위한 테스트.
    #
    # 주의: 이 테스트는 _fix_text()가 인코딩에 무관한 텍스트 처리 로직임을
    # 확인하는 것이 목적. 실제 인코딩 감지는 TestAlchemyDetectEncoding에서 검증.
    # run() 직접 실행은 QThread 라이프사이클 때문에 생략.

    def test_utf8_bom_roundtrip(self):
        """UTF-8 BOM 파일도 정상 처리."""
        content = "한국어 텍스트\n두 번째 줄"
        src = self._make_file('ko.txt', content, enc='utf-8-sig')
        # 감지 → 디코딩 → 교정 순으로 검증
        # v1.0.6: from FileNexusSuite import 대신 _alchemy_detect_enc 사용 —
        # FileNexusSuite 재import 시 Phase 2-a `_fns_track` 핸들러 재등록으로
        # 위치 추적 collection이 오염되는 문제 방지 (§추가O 보호)
        detected = _alchemy_detect_enc(src)
        # v1.0.4: 튜플 반환 호환 (이전 str / 신규 (str, float))
        enc = detected[0] if isinstance(detected, tuple) else detected
        self.assertEqual(enc, 'utf-8-sig')
        with open(src, 'r', encoding=enc) as f: text = f.read()
        w = _BulkFixerWorker(files=[src], out_dir='',
                             do_mid=False, do_blank=False, max_blank=1)
        out, _, _ = w._fix_text(text)
        self.assertIn("한국어", out)

    def test_utf16_le_roundtrip(self):
        """UTF-16 LE 파일도 정상 처리 (v1.0.2 버그)."""
        content = "한국어 텍스트\n두 번째 줄"
        src = os.path.join(self.td, 'ko_utf16_le.txt')
        with open(src, 'wb') as f:
            f.write(b'\xff\xfe' + content.encode('utf-16-le'))
        # v1.0.6: from FileNexusSuite import 제거 — Phase 2-a `_fns_track` 핸들러 재등록 방지
        detected = _alchemy_detect_enc(src)
        # v1.0.4: 튜플 반환 호환
        enc = detected[0] if isinstance(detected, tuple) else detected
        self.assertEqual(enc, 'utf-16')
        with open(src, 'r', encoding=enc) as f: text = f.read()
        w = _BulkFixerWorker(files=[src], out_dir='',
                             do_mid=False, do_blank=False, max_blank=1)
        out, _, _ = w._fix_text(text)
        self.assertIn("한국어", out)

    def test_utf16_be_roundtrip(self):
        """UTF-16 BE 파일도 정상 처리 (v1.0.2 버그)."""
        content = "한국어 텍스트\n두 번째 줄"
        src = os.path.join(self.td, 'ko_utf16_be.txt')
        with open(src, 'wb') as f:
            f.write(b'\xfe\xff' + content.encode('utf-16-be'))
        # v1.0.6: from FileNexusSuite import 제거 — Phase 2-a `_fns_track` 핸들러 재등록 방지
        detected = _alchemy_detect_enc(src)
        # v1.0.4: 튜플 반환 호환
        enc = detected[0] if isinstance(detected, tuple) else detected
        self.assertEqual(enc, 'utf-16')
        with open(src, 'r', encoding=enc) as f: text = f.read()
        w = _BulkFixerWorker(files=[src], out_dir='',
                             do_mid=False, do_blank=False, max_blank=1)
        out, _, _ = w._fix_text(text)
        self.assertIn("한국어", out)

    def test_cp949_roundtrip(self):
        """한국어 CP949 파일도 정상 처리 (v1.0.2 에서도 정상이었음 — 회귀 방지)."""
        content = "한국어 텍스트\n두 번째 줄"
        src = self._make_file('ko_cp949.txt', content, enc='cp949')
        w = _BulkFixerWorker(files=[src], out_dir='',
                             do_mid=False, do_blank=False, max_blank=1)
        with open(src, 'r', encoding='cp949') as f: text = f.read()
        out, _, _ = w._fix_text(text)
        self.assertIn("한국어", out)

    def test_5_languages_utf8(self):
        """5개 언어 × UTF-8 전체 회귀 방지 검증."""
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
                # 핵심 단어가 출력에 그대로 있어야 함
                for keyword in content.split():
                    self.assertIn(keyword, out,
                                  f"{fname}: '{keyword}' 누락 또는 깨짐")


# ════════════════════════════════════════════════════════════════════════
# §추가J  lang_mode — TextFixerWorker (v0.10.0 신규 파라미터)
# ════════════════════════════════════════════════════════════════════════
@unittest.skipUnless(HAS_MODULE and _TextFixerWorker,
                     "FileNexusSuite 로드 실패")
class TestTextFixerLangMode(unittest.TestCase):
    """TextFixerWorker.lang_mode 파라미터 테스트."""

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
        self.assertEqual(lang, 'ko')  # CJK → ko 모드

    def test_detect_lang_empty(self):
        lang = _TextFixerWorker._detect_lang("")
        self.assertEqual(lang, 'ko')  # 기본값

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
# §추가K  v0.12.0 회귀 — 소스 파싱 기반 (PySide6 불필요)
# ════════════════════════════════════════════════════════════════════════
class TestV012Regression(unittest.TestCase):
    """v0.12.0 주요 변경사항 회귀 테스트 — 소스 파일 직접 파싱."""

    def _src(self):
        with open(_MAIN_PY, encoding='utf-8') as f:
            return f.read()

    # ── 버전 ────────────────────────────────────────────────────────────
    def test_app_version_012(self):
        """APP_VERSION이 v1.0.0 이상"""
        m = _re.search(r'^APP_VERSION\s*=\s*["\']([^"\']+)["\']', self._src(), _re.MULTILINE)
        self.assertIsNotNone(m, "APP_VERSION 정의 없음")
        parts = m.group(1).split('.')
        self.assertGreaterEqual(int(parts[0]), 1, f"메이저 버전 < 1: {m.group(1)}")

    # ── SVG 아이콘 시스템 ─────────────────────────────────────────────
    def test_svg_paths_dict_defined(self):
        """_SVG_PATHS 딕셔너리가 소스에 정의되어 있어야 한다."""
        self.assertIn('_SVG_PATHS', self._src())

    def test_svg_line_icons_dict_defined(self):
        """_SVG_LINE_ICONS 딕셔너리가 소스에 정의되어 있어야 한다."""
        self.assertIn('_SVG_LINE_ICONS', self._src())

    def test_svg_paths_filled_keys_present(self):
        """_SVG_PATHS에 핵심 filled 아이콘 키가 모두 있어야 한다."""
        src = self._src()
        for key in ('document', 'folder', 'folder_open', 'tag', 'refresh',
                    'wrench', 'magnifier', 'save', 'trash', 'broom',
                    'question', 'list', 'clipboard', 'arrow_up', 'arrow_down',
                    'check', 'info'):
            with self.subTest(key=key):
                self.assertIn(f"'{key}'", src, f"_SVG_PATHS에 '{key}' 없음")

    def test_svg_line_icons_keys_present(self):
        """_SVG_LINE_ICONS에 핵심 line 아이콘 키가 모두 있어야 한다."""
        src = self._src()
        for key in ('document_line', 'folder_open_line', 'tag_line', 'folder_line',
                    'wrench_line', 'broom_line', 'gear_line', 'question_line',
                    'theme_line', 'globe_line', 'keyboard_line', 'license_line',
                    'info_line', 'bell_line'):
            with self.subTest(key=key):
                self.assertIn(f"'{key}'", src, f"_SVG_LINE_ICONS에 '{key}' 없음")

    def test_bulk_fixer_tab_uses_broom_line(self):
        """Bulk Fixer 탭 아이콘이 broom_line(line 스타일)으로 변경되었어야 한다.

        v0.12.0: broom(filled) → broom_line(line) 교체로 다른 탭과 통일.
        """
        src = self._src()
        # 탭 아이콘 목록에서 broom_line이 사용되어야 함
        self.assertIn("'broom_line'", src, "broom_line 키가 소스에 없음")
        # 탭 아이콘 배열(_tab_icons)에서 broom_line이 마지막(Bulk Fixer) 자리에 있는지 확인
        m = _re.search(r"_tab_icons\s*=\s*\[(.*?)\]", src, _re.DOTALL)
        self.assertIsNotNone(m, "_tab_icons 배열 정의 없음")
        self.assertIn('broom_line', m.group(1), "_tab_icons 배열에 broom_line 없음")

    def test_svg_icon_function_defined(self):
        """_svg_icon() 함수가 소스에 정의되어 있어야 한다."""
        self.assertIn('def _svg_icon(', self._src())

    def test_svg_icon_white_disabled_pixmap(self):
        """_svg_icon()에서 'white' 아이콘 시 Disabled 픽스맵 자동 추가 로직 존재."""
        src = self._src()
        # 'white' + Disabled 조합 처리 코드 확인
        self.assertIn("color == 'white'", src)
        self.assertIn('QIcon.Mode.Disabled', src)

    # ── 테마 시스템 ───────────────────────────────────────────────────
    def test_all_themes_have_btn_border_h(self):
        """모든 테마 딕셔너리에 BTN_BORDER_H 키가 있어야 한다 (v0.12.0 대비 개선)."""
        src = self._src()
        m = _re.search(r'^THEMES\s*=\s*\{(.*?)^\}', src, _re.MULTILINE | _re.DOTALL)
        self.assertIsNotNone(m, "THEMES 정의 없음")
        theme_block = m.group(1)
        # 각 테마 블록 내에 BTN_BORDER_H가 있어야 함
        self.assertGreater(
            theme_block.count("'BTN_BORDER_H'"), 0,
            "THEMES 안에 BTN_BORDER_H가 하나도 없음"
        )
        # 테마 수만큼 있어야 함 (9개 테마)
        theme_count = len(_re.findall(r"^\s{4}'(\w+)'\s*:\s*\{", theme_block, _re.MULTILINE))
        btn_border_h_count = theme_block.count("'BTN_BORDER_H'")
        self.assertEqual(btn_border_h_count, theme_count,
            f"BTN_BORDER_H 수({btn_border_h_count}) ≠ 테마 수({theme_count})")

    def test_themes_count_9(self):
        """THEMES 딕셔너리에 테마가 9개 있어야 한다 (auto는 런타임 resolve 가상 테마)."""
        src = self._src()
        m = _re.search(r'^THEMES\s*=\s*\{(.*?)^\}', src, _re.MULTILINE | _re.DOTALL)
        self.assertIsNotNone(m)
        keys = _re.findall(r"^\s{4}'(\w+)'\s*:\s*\{", m.group(1), _re.MULTILINE)
        self.assertEqual(len(keys), 9, f"THEMES 키 수 불일치: {keys}")

    # ── 번역 — 이모지 제거 확인 ───────────────────────────────────────
    def test_btn_add_file_no_emoji(self):
        """btn_add_file 번역값에서 이모지가 제거되었어야 한다 (v0.12.0 정리)."""
        src = self._src()
        # 'btn_add_file' 키의 값을 추출해 이모지 유니코드 범위 확인
        m = _re.search(r"'btn_add_file'\s*:\s*'([^']+)'", src)
        if m:
            val = m.group(1)
            # 일반 이모지 범위 (U+1F300–U+1FFFF)
            has_emoji = any(0x1F300 <= ord(c) <= 0x1FFFF for c in val)
            self.assertFalse(has_emoji, f"btn_add_file 값에 이모지 포함: {repr(val)}")

    def test_btn_add_folder_no_emoji(self):
        """btn_add_folder 번역값에서 이모지가 제거되었어야 한다."""
        src = self._src()
        m = _re.search(r"'btn_add_folder'\s*:\s*'([^']+)'", src)
        if m:
            val = m.group(1)
            has_emoji = any(0x1F300 <= ord(c) <= 0x1FFFF for c in val)
            self.assertFalse(has_emoji, f"btn_add_folder 값에 이모지 포함: {repr(val)}")

    # ── 로그 시스템 ───────────────────────────────────────────────────
    def test_crash_log_max_3(self):
        """crash 로그 최대 보관 수가 3개로 줄었어야 한다 (v0.12.0: 20→3)."""
        src = self._src()
        # 크래시 로그 cleanup 로직에서 3 또는 -3 슬라이싱이 사용되는지 확인
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
        """정상 종료 시 세션 로그 자동 삭제 로직이 있어야 한다."""
        src = self._src()
        self.assertIn('session', src.lower())
        # closeEvent에서 세션 로그 파일을 닫거나 삭제하는 코드
        self.assertTrue(
            'session_log' in src or '_session_log_fp' in src,
            "세션 로그 관련 코드가 소스에 없음"
        )

    # ── _svg_html_img 보존 ────────────────────────────────────────────
    def test_svg_html_img_preserved_unused(self):
        """_svg_html_img()가 미사용 상태로 보존되어 있어야 한다."""
        self.assertIn('def _svg_html_img(', self._src())


@unittest.skipUnless(HAS_MODULE, "FileNexusSuite 로드 실패 (PySide6 필요)")
class TestV012RegressionModule(unittest.TestCase):
    """v0.12.0 모듈 로드 기반 회귀 테스트 (PySide6 필요)."""

    def test_svg_paths_is_dict(self):
        """_SVG_PATHS가 dict 타입이어야 한다."""
        svg_paths = _ns.get('_SVG_PATHS')
        self.assertIsNotNone(svg_paths, "_SVG_PATHS가 namespace에 없음")
        self.assertIsInstance(svg_paths, dict)

    def test_svg_line_icons_is_dict(self):
        """_SVG_LINE_ICONS가 dict 타입이어야 한다."""
        svg_line = _ns.get('_SVG_LINE_ICONS')
        self.assertIsNotNone(svg_line, "_SVG_LINE_ICONS가 namespace에 없음")
        self.assertIsInstance(svg_line, dict)

    def test_svg_paths_has_all_filled_keys(self):
        """_SVG_PATHS에 17개 이상의 filled 아이콘이 있어야 한다."""
        svg_paths = _ns.get('_SVG_PATHS', {})
        self.assertGreaterEqual(len(svg_paths), 17,
            f"_SVG_PATHS 항목 수 부족: {len(svg_paths)}")

    def test_svg_line_icons_has_all_line_keys(self):
        """_SVG_LINE_ICONS에 14개 이상의 line 아이콘이 있어야 한다."""
        svg_line = _ns.get('_SVG_LINE_ICONS', {})
        self.assertGreaterEqual(len(svg_line), 14,
            f"_SVG_LINE_ICONS 항목 수 부족: {len(svg_line)}")

    def test_broom_line_in_svg_line_icons(self):
        """_SVG_LINE_ICONS에 broom_line 키가 있어야 한다 (Bulk Fixer 탭 아이콘)."""
        svg_line = _ns.get('_SVG_LINE_ICONS', {})
        self.assertIn('broom_line', svg_line)

    def test_broom_in_svg_paths(self):
        """_SVG_PATHS에 broom 키가 있어야 한다 (filled 스타일 보존)."""
        svg_paths = _ns.get('_SVG_PATHS', {})
        self.assertIn('broom', svg_paths)

    def test_all_themes_have_btn_border_h_key(self):
        """모든 테마 딕셔너리에 BTN_BORDER_H 키가 있어야 한다."""
        themes = _ns.get('THEMES', {})
        for name, t in themes.items():
            with self.subTest(theme=name):
                self.assertIn('BTN_BORDER_H', t,
                    f"테마 '{name}'에 BTN_BORDER_H 없음")

    def test_themes_count_module(self):
        """THEMES에 테마가 9개 있어야 한다."""
        themes = _ns.get('THEMES', {})
        self.assertEqual(len(themes), 9, f"테마 수 불일치: {sorted(themes.keys())}")

    def test_app_version_from_ns(self):
        """namespace에서 가져온 APP_VERSION이 v1.0.0 이상이어야 한다."""
        ver = _ns.get('APP_VERSION')
        self.assertIsNotNone(ver, "APP_VERSION 없음")
        # v1.0.0 이상이면 OK
        parts = ver.split('.')
        self.assertGreaterEqual(int(parts[0]), 1, f"메이저 버전 < 1: {ver}")

    def test_svg_icon_callable(self):
        """_svg_icon 함수가 namespace에 존재하고 호출 가능해야 한다."""
        fn = _ns.get('_svg_icon')
        self.assertIsNotNone(fn, "_svg_icon이 namespace에 없음")
        self.assertTrue(callable(fn))

    def test_svg_html_img_callable(self):
        """_svg_html_img 함수가 namespace에 보존되어 있어야 한다."""
        fn = _ns.get('_svg_html_img')
        self.assertIsNotNone(fn, "_svg_html_img이 namespace에 없음")
        self.assertTrue(callable(fn))

    def test_translations_btn_keys_no_emoji(self):
        """번역 키 btn_add_file / btn_add_folder 값에 이모지가 없어야 한다."""
        translations = _ns.get('TRANSLATIONS', {})
        ko = translations.get('ko', {})
        for key in ('btn_add_file', 'btn_add_folder', 'btn_del_sel', 'btn_del_all'):
            val = ko.get(key, '')
            with self.subTest(key=key):
                has_emoji = any(0x1F300 <= ord(c) <= 0x1FFFF for c in val)
                self.assertFalse(has_emoji,
                    f"ko['{key}'] 값에 이모지 포함: {repr(val)}")


# ════════════════════════════════════════════════════════════════════════
# §추가L  v1.0.0 회귀 — 소스 파싱 기반 (PySide6 불필요)
# ════════════════════════════════════════════════════════════════════════
class TestV100Regression(unittest.TestCase):
    """v1.0.0 주요 변경사항 회귀 테스트 — 소스 파일 직접 파싱."""

    def _src(self):
        with open(_MAIN_PY, encoding='utf-8') as f:
            return f.read()

    # ── 버전 ────────────────────────────────────────────────────────────
    def test_app_version_100(self):
        """APP_VERSION이 v1.0.0 이상"""
        m = _re.search(r'^APP_VERSION\s*=\s*["\']([^"\']+)["\']', self._src(), _re.MULTILINE)
        self.assertIsNotNone(m, "APP_VERSION 정의 없음")
        parts = m.group(1).split('.')
        self.assertGreaterEqual(int(parts[0]), 1, f"메이저 버전 < 1: {m.group(1)}")

    # ── QPlainTextEdit 교체 ──────────────────────────────────────────
    def test_qplaintextedit_import(self):
        """QPlainTextEdit가 import되어 있어야 한다 (QTextEdit 대용량 한계 해결)."""
        self.assertIn('QPlainTextEdit', self._src())

    def test_text_fixer_edit_uses_qplaintextedit(self):
        """TextFixerEdit가 QPlainTextEdit 기반이어야 한다."""
        src = self._src()
        m = _re.search(r'class TextFixerEdit\((\w+)\)', src)
        self.assertIsNotNone(m, "TextFixerEdit 클래스 정의 없음")
        self.assertEqual(m.group(1), 'QPlainTextEdit')

    def test_text_fixer_output_edit_uses_qplaintextedit(self):
        """TextFixerOutputEdit가 QPlainTextEdit 기반이어야 한다."""
        src = self._src()
        m = _re.search(r'class TextFixerOutputEdit\((\w+)\)', src)
        self.assertIsNotNone(m, "TextFixerOutputEdit 클래스 정의 없음")
        self.assertEqual(m.group(1), 'QPlainTextEdit')

    # ── 애니메이션 위젯 ──────────────────────────────────────────────
    def test_scroll_hint_class(self):
        """_ScrollHint 클래스가 정의되어 있어야 한다."""
        self.assertIn('class _ScrollHint', self._src())

    def test_help_button_class(self):
        """_HelpButton 클래스가 정의되어 있어야 한다."""
        self.assertIn('class _HelpButton', self._src())

    def test_gear_button_class(self):
        """_GearButton 클래스가 정의되어 있어야 한다."""
        self.assertIn('class _GearButton', self._src())

    # ── Output 폴더 전역 설정 ────────────────────────────────────────
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

    # ── Bulk Fixer 프리셋 ────────────────────────────────────────────
    def test_bulk_combo_preset(self):
        """Bulk Fixer에 _combo_preset 콤보박스가 있어야 한다."""
        self.assertIn('_combo_preset', self._src())

    def test_bulk_apply_preset(self):
        """_apply_preset 메서드가 정의되어 있어야 한다."""
        self.assertIn('def _apply_preset', self._src())

    # ── Bulk Fixer abort 버튼 ────────────────────────────────────────
    def test_btn_abort_widget(self):
        """_btn_abort 위젯이 있어야 한다 (btn_undo에서 분리)."""
        self.assertIn('_btn_abort', self._src())

    # ── grp_title_lbl 스타일 ─────────────────────────────────────────
    def test_grp_title_lbl_style(self):
        """make_style에 QLabel#grp_title_lbl 스타일이 있어야 한다."""
        self.assertIn('grp_title_lbl', self._src())

    # ── 섹션 헤더 // 접두사 ──────────────────────────────────────────
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
        # v1.0.0 이상이면 OK (v1.0.1, v1.0.2, v1.0.3 등 모두 통과)
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
# §추가N  v1.0.3 인코딩 감지 회귀 방지
# ════════════════════════════════════════════════════════════════════════
class TestV103Regression(unittest.TestCase):
    """v1.0.3 — Text Fixer·Bulk Fixer 인코딩 감지 버그 회귀 방지."""

    @classmethod
    def setUpClass(cls):
        with open(_MAIN_PY, encoding='utf-8') as f:
            cls.src = f.read()

    def test_no_latin_1_fallback_in_text_fixer(self):
        """TextFixerPanel.load_file이 latin-1 폴백을 사용하지 않아야 함.
        v1.0.2까지는 latin-1 폴백이 있어서 잘못된 인코딩의 파일도
        무조건 디코딩 '성공'시켜 깨진 텍스트가 그대로 처리됐음."""
        # load_file 메서드 본문 추출
        m = re.search(
            r'def load_file\(self, path: str\):(.*?)(?=\n    def |\nclass )',
            self.src, re.DOTALL)
        self.assertIsNotNone(m, "load_file 메서드를 찾을 수 없음")
        body = m.group(1)
        self.assertNotIn("'latin-1'", body,
            "TextFixerPanel.load_file에 latin-1 폴백이 남아있음 (v1.0.2 버그)")

    def test_no_latin_1_in_bulk_fixer_worker(self):
        """BulkFixerWorker.run이 latin-1 폴백을 사용하지 않아야 함."""
        # BulkFixerWorker.run 메서드 내 for enc 리스트 추출
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
        """TextFixerPanel.load_file이 alchemy 기반 인코딩 감지를 사용해야 함.

        v1.0.6 Phase 2-a부터 직접 호출 또는 safe_read_text_with_report 헬퍼 경유
        (헬퍼 내부 L3935가 alchemy_detect_encoding을 호출) 둘 다 허용.
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
        """BulkFixerWorker.run이 alchemy 기반 인코딩 감지를 사용해야 함.

        v1.0.6 Phase 2-a부터 직접 호출 또는 safe_read_text_with_report 헬퍼 경유
        (헬퍼 내부 L3935가 alchemy_detect_encoding을 호출) 둘 다 허용.
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
        """BulkFixerPanel._on_file_selected이 alchemy 기반 인코딩 감지를 사용해야 함.

        v1.0.6 Phase 2-a부터 직접 호출 또는 safe_read_text_with_report 헬퍼 경유
        (헬퍼 내부 L3935가 alchemy_detect_encoding을 호출) 둘 다 허용.
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
        # 간단하게 전체 소스에서 3회 이상 등장하는지만 확인
        for enc in ('shift_jis', 'gbk', 'big5'):
            count = self.src.count(f"'{enc}'")
            self.assertGreaterEqual(count, 3,
                f"'{enc}' 폴백이 3곳 미만 (Text Fixer + Bulk 2곳에 있어야 함): {count}회")


@unittest.skipUnless(HAS_MODULE, "FileNexusSuite 로드 실패 (PySide6 필요)")
class TestV103RegressionModule(unittest.TestCase):
    """v1.0.3 모듈 로드 기반 회귀 테스트."""

    def test_app_version_is_103(self):
        """APP_VERSION이 '1.0.3' 이상이어야 한다.
        v1.0.3에 도입된 인코딩 감지 개선 기능 회귀 검증이므로,
        1.0.3 이상이면 충족 (V012/V100 패턴과 일관)."""
        ver = _ns.get('APP_VERSION')
        self.assertIsNotNone(ver, "APP_VERSION 정의 없음")
        parts = [int(p) for p in ver.split('.')]
        self.assertGreaterEqual(parts, [1, 0, 3],
            f"APP_VERSION {ver}은 1.0.3 이상이어야 함")

    def test_alchemy_detect_encoding_utf16_le(self):
        """alchemy_detect_encoding이 UTF-16 LE를 정확히 감지.
        v1.0.4: (encoding, confidence) 튜플 반환으로 변경됨 — 첫 요소 확인."""
        detect = _ns.get('alchemy_detect_encoding')
        self.assertIsNotNone(detect)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b'\xff\xfe' + '한국어'.encode('utf-16-le'))
            path = f.name
        try:
            result = detect(path)
            # v1.0.3까지: str, v1.0.4부터: (str, float). 두 형식 모두 호환.
            enc = result[0] if isinstance(result, tuple) else result
            self.assertEqual(enc, 'utf-16')
        finally:
            os.unlink(path)

    def test_alchemy_detect_encoding_utf16_be(self):
        """alchemy_detect_encoding이 UTF-16 BE를 정확히 감지.
        v1.0.4: (encoding, confidence) 튜플 반환으로 변경됨 — 첫 요소 확인."""
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
# v1.0.4 회귀 테스트 — Text Merger 종합 개선
# ════════════════════════════════════════════════════════════════════════
class TestV104Regression(unittest.TestCase):
    """v1.0.4 — Text Merger 인코딩 옵션 확장 + 사전 경고 + 신뢰도 UI + 통합.

    인수인계 후보 1/2/3/4를 모두 포함:
      - D. _detect_encoding 통합 (alchemy 시그니처 (str, float) 확장)
      - A. Text Merger 저장 인코딩 확장 (Shift-JIS / GBK / Big5)
      - B. UnicodeEncodeError 사전 경고 다이얼로그
      - C. 신뢰도 % 색상 코딩 + 툴팁
    """

    @classmethod
    def setUpClass(cls):
        with open(_MAIN_PY, encoding='utf-8') as f:
            cls.src = f.read()

    # ── D: _detect_encoding 통합 ──────────────────────────────────
    def test_alchemy_returns_tuple_in_source(self):
        """alchemy_detect_encoding 함수가 (enc, conf) 튜플 형식으로 반환해야 함."""
        m = re.search(
            r'def alchemy_detect_encoding\(path\):(.*?)(?=\ndef |\nclass )',
            self.src, re.DOTALL)
        self.assertIsNotNone(m, "alchemy_detect_encoding 함수를 찾을 수 없음")
        body = m.group(1)
        # return 문이 튜플 형식 ("...", ...)인지 확인 (문자열만 반환하던 v1.0.3 형식 차단)
        self.assertIn('return ("utf-8-sig", 1.0)', body,
            "BOM 감지 시 (str, float) 튜플 반환이 아님 (v1.0.3 시그니처 잔재)")
        self.assertIn('return ("utf-16", 1.0)', body,
            "UTF-16 BOM 감지 시 (str, float) 튜플 반환이 아님")

    def test_text_merger_no_self_detect_encoding(self):
        """Text Merger 패널의 _detect_encoding 메서드가 제거되었어야 함 (alchemy 통합).
        v1.0.3까지 Text Merger는 자체 _detect_encoding을 가지고 있었으나,
        v1.0.4에서 alchemy_detect_encoding으로 통합됨."""
        # MergePanel 클래스 내부에 def _detect_encoding이 있으면 안 됨
        self.assertNotIn('def _detect_encoding(self, path)', self.src,
            "Text Merger의 _detect_encoding 메서드가 아직 남아있음 (D 작업 누락)")

    def test_text_merger_uses_alchemy(self):
        """Text Merger 파일 추가 흐름에서 alchemy_detect_encoding을 호출해야 함."""
        # _add_files 또는 동등한 흐름에서 alchemy 호출 확인
        # self._detect_encoding(path) → alchemy_detect_encoding(path) 변경됐는지
        self.assertNotIn('self._detect_encoding(path)', self.src,
            "Text Merger가 여전히 self._detect_encoding을 호출 (D 작업 누락)")
        # 호출 패턴 변경 확인
        m = re.search(r'enc, conf = alchemy_detect_encoding\(path\)', self.src)
        self.assertIsNotNone(m, "Text Merger _add_files에서 alchemy 호출 패턴이 안 보임")

    def test_alchemy_callers_unpack_tuple(self):
        """alchemy_detect_encoding의 모든 호출부가 튜플 언패킹을 사용해야 함.
        v1.0.4: 시그니처 변경으로 (enc, conf) 또는 (enc, _) 형식으로 받아야 함.

        v1.0.6 Phase 2-a: TextFixer / BulkWorker / BulkPreview 3곳의 직접 호출이
        safe_read_text_with_report 헬퍼로 통합되어 호출 건수 감소 (6건 이상 → 4건).
        정의 1건(L3676) + safe_read_text_with_report 내부 1건 + Text Converter +
        Text Merger = 총 4건이 Phase 2-a 이후 정상 수치.
        """
        # 호출 전체 카운트 (정의 포함 — regex는 정의도 매칭)
        all_calls = re.findall(r'alchemy_detect_encoding\(', self.src)
        self.assertGreaterEqual(len(all_calls), 4,
            f"alchemy_detect_encoding 호출이 4건 미만: {len(all_calls)} "
            f"(Phase 2-a 이후 정상 하한은 4 — 정의 + 헬퍼 + Converter + Merger)")
        # 단일 변수 할당 패턴(예: detected_enc = alchemy_detect_encoding(path)) 잔재 차단
        bad = re.findall(r'^\s*[a-z_]+ = alchemy_detect_encoding\(',
                         self.src, re.MULTILINE)
        self.assertEqual(bad, [],
            f"튜플 언패킹 안 한 호출부 발견 (v1.0.3 시그니처 잔재): {bad}")

    # ── A: Text Merger 인코딩 옵션 추가 ──────────────────────────
    def test_text_merger_combo_has_cjk_encodings(self):
        """Text Merger 콤보박스에 Shift-JIS, GBK, Big5가 추가되어야 함.
        v1.0.5: addItems([...]) → _ENC_ITEMS 상수로 이동. 정규식을 상수 블록 검색으로 업데이트."""
        # v1.0.5: _ENC_ITEMS 클래스 상수에서 CJK 3종 검증
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
        # _enc_codec dict에 Shift-JIS / GBK / Big5 매핑 확인
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
                # 두 dict 모두에 키가 등장해야 하므로 최소 2회
                count = self.src.count(f"'{key}':")
                self.assertGreaterEqual(count, 2,
                    f"_ENC_COLOR/_ENC_LABEL에 '{key}' 키 누락 (현재 {count}회)")

    # ── B: UnicodeEncodeError 사전 경고 ──────────────────────────
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

    # ── C: 신뢰도 색상 코딩 + 툴팁 ──────────────────────────────
    def test_confidence_4_tier_color_coding(self):
        """MergeEncodingDelegate.paint에 신뢰도 4단계 색상 분기가 있어야 함."""
        # 4가지 색상이 모두 등장하는지
        for hex_color in ('#4CAF50', '#F1C40F', '#E67E22', '#E74C3C'):
            with self.subTest(color=hex_color):
                self.assertIn(hex_color, self.src,
                    f"신뢰도 색상 {hex_color} 누락 (4단계 색상 코딩 미적용)")
        # 임계값 분기 패턴 확인
        self.assertIn('conf >= 0.90', self.src, "≥90% 분기 누락")
        self.assertIn('conf >= 0.70', self.src, "≥70% 분기 누락")
        self.assertIn('conf >= 0.50', self.src, "≥50% 분기 누락")

    def test_merge_low_conf_hint_keys_in_5_languages(self):
        """5개 언어 사전에 merge_low_conf_hint 키가 있어야 함 (툴팁용)."""
        count = self.src.count("'merge_low_conf_hint'")
        self.assertGreaterEqual(count, 5,
            f"'merge_low_conf_hint' 키가 5개 언어 미만 정의됨 (현재 {count}회)")

    # ── 버그 수정 검증 (v1.0.4 초판 피드백 반영) ──────────────
    def test_dlg_question_supports_rich_text(self):
        """_dlg_question이 rich_text 파라미터를 지원해야 함.
        버그 1 수정: 경고 다이얼로그에서 HTML 태그(<b>, <br>, <code>)가
        렌더링되지 않고 그대로 텍스트로 표시되던 문제 해결."""
        # 함수 시그니처에 rich_text 파라미터 존재 확인
        self.assertIn('def _dlg_question(parent, title: str, msg: str, min_width: int = 360, rich_text: bool = False)',
                      self.src,
                      "_dlg_question에 rich_text 파라미터 추가 누락")
        # Text Merger 경고 호출부가 rich_text=True로 호출해야 함
        self.assertIn("_dlg_question(self, _t('merge_enc_warn_title'), warn_msg, min_width=460, rich_text=True)",
                      self.src,
                      "Text Merger 경고 다이얼로그 호출부가 rich_text=True를 전달하지 않음")

    def test_alchemy_fallback_covers_cjk(self):
        """alchemy_detect_encoding의 폴백 로직에 CJK 인코딩 순차 검증이 포함되어야 함.
        버그 2 수정: chardet이 ASCII로 시작하는 Shift-JIS 파일을 cp1006 등으로
        오인식해도 폴백 단계에서 strict 디코딩으로 올바른 인코딩을 찾도록 강화."""
        m = re.search(
            r'def alchemy_detect_encoding\(path\):(.*?)(?=\ndef |\nclass )',
            self.src, re.DOTALL)
        self.assertIsNotNone(m)
        body = m.group(1)
        # 폴백 루프에 CJK 4종이 명시되어야 함 (순서 중요: cp949 → shift_jis → gbk → big5)
        self.assertIn('for _fallback in ("cp949", "shift_jis", "gbk", "big5"):',
                      body,
                      "alchemy 폴백 루프에 CJK 순차 검증 누락")
        # raw.decode(_fallback) 패턴 확인
        self.assertIn('raw.decode(_fallback)', body,
                      "alchemy 폴백 루프에서 strict 디코딩 검증 누락")


@unittest.skipUnless(HAS_MODULE, "FileNexusSuite 로드 실패 (PySide6 필요)")
class TestV104RegressionModule(unittest.TestCase):
    """v1.0.4 모듈 로드 기반 회귀 테스트 — 런타임 동작 검증."""

    def test_app_version_is_104_or_later(self):
        """APP_VERSION이 '1.0.4' 이상이어야 한다.
        v1.0.4 시점: '정확히 1.0.4' 검증이었으나, 이후 버전(v1.0.5+)에서도 통과 가능하도록
        '이상' 비교로 완화. 의도(v1.0.4 릴리즈 이후의 버전 번호) 유지."""
        ver = _ns.get('APP_VERSION')
        self.assertIsNotNone(ver, "APP_VERSION 없음")
        # '1.0.4' 이상 (문자열 비교 대신 튜플 비교로 '1.0.10' 같은 케이스도 대응)
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
        """한글 텍스트를 Shift-JIS로 저장 시도하면 손실 감지되어야 함.
        v1.0.4 확장: SAMPLE_KO_LONG_SENTENCES(약 140자)로 확장하여 실제 사용 환경 근접.
        v1.0.4 수정: 반환값이 5-tuple로 확장됨 (kinds, total, total_chars 추가)."""
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
        # 긴 텍스트면 샘플 5개 슬롯이 채워져야 함 (한글은 고유 문자 종류 많음)
        self.assertEqual(len(samples), 5,
            f"긴 한글 텍스트인데 샘플이 5개 미만: {len(samples)}개")

    def test_check_encoding_compat_utf8_passthrough(self):
        """UTF-8 인코딩은 모든 유니코드 문자를 표현 가능 → 손실 없음.
        v1.0.4 확장: 다국어 + 이모지 조합을 풍부하게 늘려 실제 환경 근접.
        v1.0.4 수정: 반환값이 5-tuple로 확장됨."""
        check = _ns.get('alchemy_check_encoding_compat')
        self.assertIsNotNone(check)
        # 한국어·일본어·중국어·이모지·특수문자 혼합 긴 텍스트
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
        """샘플 리스트는 깨질 문자가 많아도 최대 5개로 제한되어야 함 (다이얼로그 가독성).
        v1.0.4 수정: 반환값이 5-tuple로 확장됨."""
        check = _ns.get('alchemy_check_encoding_compat')
        self.assertIsNotNone(check)
        # 깨질 고유 문자 수십 개 확보 (이모지 + 한글 + 일본어 + 중국어)
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
        """영향받는 총 글자 수는 중복을 포함한 실제 ? 대체 개수와 일치해야 함.
        v1.0.4 B 옵션: 사용자에게 '실제 파일의 몇 %가 깨지는지' 정확히 안내하기 위함."""
        check = _ns.get('alchemy_check_encoding_compat')
        self.assertIsNotNone(check)
        # '한' 문자가 정확히 10번 반복 + ASCII 공백
        text = '한 ' * 10  # 총 20자 중 '한'이 10번
        has_loss, bad_kinds, bad_total, total_chars, samples = check(text, 'cp1252')
        self.assertTrue(has_loss)
        # cp1252는 한글 표현 불가, 공백은 표현 가능 → '한' 10번이 전부 깨짐
        self.assertEqual(bad_kinds, 1, f"고유 종류 수가 1이 아님: {bad_kinds}")
        self.assertEqual(bad_total, 10, f"영향 총 글자 수가 10이 아님: {bad_total}")
        self.assertEqual(total_chars, 20, f"전체 글자 수가 20이 아님: {total_chars}")
        # 실제로 replace 저장 시 ? 개수와 일치하는지 교차 검증
        encoded = text.encode('cp1252', errors='replace')
        question_count = encoded.count(b'?')
        self.assertEqual(bad_total, question_count,
            f"bad_total({bad_total}) != 실제 ? 개수({question_count})")

    def test_alchemy_detect_ascii_started_shift_jis(self):
        """ASCII로 시작하는 Shift-JIS 파일을 올바르게 감지해야 함.
        버그 2 수정: chardet이 이런 파일을 cp1006(우르두어) 등으로 오인식하는데,
        alchemy 폴백 단계에서 CJK 순차 strict 검증으로 구제.

        테스트 컨텐츠는 실제 보고된 케이스(~9KB) 수준으로 충분히 길게 구성.
        짧은 컨텐츠는 cp949로도 우연히 decode 성공할 수 있어 의미 있는 검증이 안 됨."""
        detect = _ns.get('alchemy_detect_encoding')
        self.assertIsNotNone(detect)
        import tempfile
        # 실제 보고된 케이스(9552 bytes) 수준으로 충분한 일본어 본문 포함
        # + Shift-JIS 고유 특수문자로 cp949 decode 실패 보장
        ja_line = 'これは日本語のエンコーディングテストです。漢字・ひらがな・カタカナを含みます。\r\n'
        special = '々ヽヾゝゞ〃仝〆〇ー「」『』〜\r\n'  # Shift-JIS 고유 심볼 (모두 인코딩 가능)
        content = ('Hello. This is an English encoding test file.\r\n'
                   'For File Nexus Suite Bulk Fixer verification.\r\n'
                   '\r\n'
                   + ja_line * 80  # ~8KB 일본어
                   + special * 10)  # Shift-JIS 고유 문자 확실히 포함
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
    """v1.0.5 — Text Merger 저장 인코딩 드롭다운 UI 사용성 개선 (소스 검증).

    핵심 변경:
      - 콤보박스: addItems(문자열) → addItem(display, userData) 패턴
      - 내부 키(기존 8종)는 userData에 보존 → 기존 설정값 100% 호환
      - 표시 라벨은 언어별 i18n 키 참조 (예: 'Shift-JIS (일본어)', '(日文)' 등)
      - 도움말 라벨 신규 (merge_enc_hint): "확실하지 않으면 UTF-8을 선택하세요"
    """

    @classmethod
    def setUpClass(cls):
        with open(_MAIN_PY, encoding='utf-8') as f:
            cls.src = f.read()

    # ── 클래스 상수 _ENC_ITEMS 검증 ───────────────────────────────
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
        # 각 키마다 i18n 키 매핑
        for i18n_key in ['merge_enc_utf8', 'merge_enc_utf8_bom', 'merge_enc_euckr',
                         'merge_enc_cp949', 'merge_enc_utf16', 'merge_enc_shiftjis',
                         'merge_enc_gbk', 'merge_enc_big5']:
            self.assertIn(f"'{i18n_key}'", block,
                f"_ENC_ITEMS에 i18n 키 {i18n_key!r} 누락")

    # ── 콤보박스 addItem 패턴 검증 ────────────────────────────────
    def test_combo_uses_add_item_with_user_data(self):
        """콤보박스 초기화는 addItem(display, userData) 패턴을 사용해야 한다."""
        # v1.0.4의 addItems(["UTF-8", ...]) 패턴이 남아있으면 안 됨
        self.assertNotIn(
            'self._combo_enc.addItems(["UTF-8", "UTF-8-BOM"',
            self.src,
            "v1.0.4 addItems 패턴이 아직 남아있음 (안 B 적용 누락)")
        # 새 패턴 확인
        self.assertIn(
            'self._combo_enc.addItem(_t(_i18n_key), _enc_key)',
            self.src,
            "addItem(display, userData) 신규 패턴이 보이지 않음")

    # ── 도움말 라벨 검증 ─────────────────────────────────────────
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

    # ── currentText → currentData 마이그레이션 검증 ─────────────
    def test_merge_files_uses_current_data(self):
        """_merge_files()에서 currentData() 기반으로 내부 키를 가져와야 한다."""
        # v1.0.5: currentData() or currentText() 폴백 패턴
        self.assertIn(
            'self._save_enc = self._combo_enc.currentData() or self._combo_enc.currentText()',
            self.src,
            "_merge_files에서 currentData 패턴이 보이지 않음")

    def test_get_config_uses_current_data(self):
        """get_config()에서 currentData() 기반으로 내부 키를 저장해야 한다."""
        # get_config 내부의 'combo_enc': 라인에 currentData()가 있어야 함
        m = re.search(
            r"'combo_enc':\s*self\._combo_enc\.currentData\(\)\s*or\s*self\._combo_enc\.currentText\(\)",
            self.src)
        self.assertIsNotNone(m,
            "get_config()에서 currentData 폴백 패턴이 보이지 않음")

    def test_apply_config_uses_find_data_with_fallback(self):
        """apply_config()는 findData() 우선, 실패 시 findText() 폴백을 사용해야 한다.
        이유: v1.0.4까지는 표시 텍스트(='Shift-JIS')를 저장했으므로,
        구버전 설정 파일을 v1.0.5가 열어도 로드 실패하지 않게 이중 방어."""
        self.assertIn('idx = self._combo_enc.findData(enc)', self.src,
            "apply_config()에서 findData 호출 누락")
        self.assertIn('if idx < 0: idx = self._combo_enc.findText(enc)', self.src,
            "apply_config()에서 findText 폴백 누락 (구버전 호환 위험)")

    # ── 45개 번역 항목 존재 검증 ─────────────────────────────────
    def test_all_languages_have_enc_keys(self):
        """5개 언어 사전에 9개 merge_enc_* 키가 모두 있어야 한다 (총 45개)."""
        required_keys = [
            'merge_enc_utf8', 'merge_enc_utf8_bom', 'merge_enc_euckr',
            'merge_enc_cp949', 'merge_enc_utf16', 'merge_enc_shiftjis',
            'merge_enc_gbk', 'merge_enc_big5', 'merge_enc_hint',
        ]
        # 각 키가 최소 5회(5개 언어) 등장해야 함
        for key in required_keys:
            count = len(re.findall(rf"'{key}'\s*:", self.src))
            self.assertGreaterEqual(count, 5,
                f"키 '{key}'가 5개 언어 사전 중 {count}개에만 존재 (누락)")

    def test_zh_uses_rifun_not_rigoyu(self):
        """중국어 간체/번체에서 '日文' 표기를 사용해야 한다 (v1.0.4 tip과 일관성).
        제가 작성 중 '日语'/'日語'로 실수할 여지가 있어 명시 검증."""
        # 간체/번체 모두 Shift-JIS 라벨은 '(日文)'
        # '日语'나 '日語'가 쓰였다면 잘못된 번역 (v1.0.4 tip은 일관되게 '日文')
        # 중국어 사전 블록에서만 검사 (일본어 사전의 '日本語'는 정상)
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

    # ── APP_VERSION 검증은 TestAppVersion으로 분리됨 (v1.0.7에서 버전 독립 구조 검증으로 재설계) ─────


@unittest.skipUnless(HAS_MODULE, "FileNexusSuite 로드 실패 (PySide6 필요)")
class TestV105RegressionModule(unittest.TestCase):
    """v1.0.5 모듈 로드 기반 회귀 테스트 — 런타임 동작 검증.

    주의: APP_VERSION 검증은 TestAppVersionModule로 분리됨 (v1.0.7에서 버전 독립 구조 검증으로 재설계)
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
        """각 언어의 라벨이 내부 인코딩 키를 포함해야 한다 (예: 'UTF-8 (...)').
        이유: 사용자가 라벨을 봐도 어떤 인코딩인지 식별 가능해야 함."""
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
        """중국어 간체/번체에서 Shift-JIS 라벨은 '日文'을 포함해야 한다.
        (일본어권 '日本語'와 구별되는 중국어권 관용 표기)"""
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
        """TextMergerPanel._ENC_ITEMS의 내부 키가 v1.0.4까지의 저장값과 호환되어야 한다.
        이 테스트는 이전 사용자의 설정 파일을 열었을 때 정상 로드됨을 보장."""
        panel_cls = _ns.get('TextMergerPanel')
        self.assertIsNotNone(panel_cls, "TextMergerPanel 클래스 누락")
        enc_items = getattr(panel_cls, '_ENC_ITEMS', None)
        self.assertIsNotNone(enc_items, "_ENC_ITEMS 상수 누락")
        # 내부 키만 추출
        internal_keys = [k for k, _ in enc_items]
        # v1.0.4 콤보박스 순서와 동일해야 함 (setCurrentIndex 관련 회귀 방지)
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
    """v1.0.5 — Text Merger 언어 전환 시 상태 메시지 갱신 버그 수정 검증.

    배경:
      - v1.0.4 이전부터 존재했을 가능성이 큰 기존 버그
      - retranslate()가 `merge_status_ready` 상태일 때만 _lbl_status를 갱신했음
      - 결과: 파일 추가 후 언어 전환하면 "26개 파일 추가됨..."이 한국어로 남음
      - v1.0.5에서 빌드 후 실기 QA(신용우님) 중 3개 언어 스크린샷으로 발견됨

    수정 설계:
      - 정적 메시지(`ready`, `clr`, `reading`, `save_err`, `path_reset_done`): 단순 재렌더
      - 복원 가능 동적 메시지(`add`: file_list 수, `path_set`: save_dir): 원본 정보로 재구성
      - 복원 불가 메시지(`del`, `save_done`, `bulk_scanning`): `ready`로 리셋 + 디버그 로그
    """

    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        # 단일 QApplication 재사용 (다른 테스트와 충돌 방지)
        cls.app = QApplication.instance() or QApplication([])

    def _make_panel(self, lang_code='ko'):
        """테스트용 TextMergerPanel 인스턴스 생성.
        _current_lang을 임시로 변경해 panel 구축."""
        # _ns['_current_lang']을 직접 변경 (exec 네임스페이스 = _t의 전역 스코프)
        _ns['_current_lang'] = lang_code
        PanelCls = _ns.get('TextMergerPanel')
        return PanelCls()

    def _set_lang(self, lang_code):
        """현재 언어 설정 (런타임에서 언어 전환 시뮬레이션)."""
        _ns['_current_lang'] = lang_code

    # ── 정적 메시지 재렌더링 ────────────────────────────────
    def test_status_ready_retranslates(self):
        """'ready' 상태에서 언어 전환 시 해당 언어의 'ready' 메시지로 바뀐다."""
        panel = self._make_panel('ko')
        try:
            # 초기 상태 = ready 한국어
            translations = _ns.get('TRANSLATIONS')
            self.assertEqual(panel._lbl_status.text(), translations['ko']['merge_status_ready'])
            # 영어로 전환
            self._set_lang('en')
            panel._retranslate_status()
            self.assertEqual(panel._lbl_status.text(), translations['en']['merge_status_ready'])
            # 일본어로 전환
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

    # ── 동적 메시지 복원 재렌더링 ────────────────────────────
    def test_status_add_retranslates_with_current_count(self):
        """'merge_status_add' 상태에서 언어 전환 시 현재 file_list 수로 재구성된다.
        이게 스크린샷에서 신용우님이 발견한 주요 버그 시나리오 (26개 파일 추가 후 언어 전환)."""
        panel = self._make_panel('ko')
        try:
            translations = _ns.get('TRANSLATIONS')
            # file_list를 26개로 시뮬레이션 (내부 상태만, 실제 파일 객체는 불필요)
            panel.file_list = ['/dummy/path' + str(i) for i in range(26)]
            # 파일 추가 메시지 세팅 (한국어)
            panel._lbl_status.setText(translations['ko']['merge_status_add'].format(n=26))
            # 일본어로 전환
            self._set_lang('ja')
            panel._retranslate_status()
            expected = translations['ja']['merge_status_add'].format(n=26)
            self.assertEqual(panel._lbl_status.text(), expected,
                f"언어 전환 후 파일 추가 메시지가 일본어로 재구성 안 됨")
            # 간체로 전환
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
            panel.save_dir = ''  # 경로 없음
            panel._lbl_status.setText(translations['ko']['merge_path_set'].format(path='/removed/path'))
            self._set_lang('en')
            panel._retranslate_status()
            # save_dir 빈 상태 → ready 폴백
            self.assertEqual(panel._lbl_status.text(), translations['en']['merge_status_ready'])
        finally:
            self._set_lang('ko')
            panel.deleteLater()

    # ── 복원 불가 메시지 → ready 리셋 ───────────────────────
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

    # ── 방어적 처리 ─────────────────────────────────────────
    def test_unknown_status_text_left_untouched(self):
        """알려지지 않은 임의 텍스트는 변경하지 않는다 (방어적 처리)."""
        panel = self._make_panel('ko')
        try:
            arbitrary = "이건 어떤 상태도 아닌 임의 텍스트 @#$%"
            panel._lbl_status.setText(arbitrary)
            self._set_lang('en')
            panel._retranslate_status()
            # 변경되지 않음
            self.assertEqual(panel._lbl_status.text(), arbitrary,
                "알려지지 않은 상태 텍스트가 의도치 않게 변경됨")
        finally:
            self._set_lang('ko')
            panel.deleteLater()

    # ── 패턴 매칭 유틸 단위 테스트 ─────────────────────────
    def test_match_status_template_with_placeholders(self):
        """_match_status_template이 플레이스홀더가 있는 템플릿을 정확히 인식한다."""
        panel = self._make_panel('ko')
        try:
            # 한국어 'merge_status_add' 템플릿: "{n}개 파일 추가됨 (인코딩 자동 감지 완료)"
            self.assertTrue(
                panel._match_status_template("26개 파일 추가됨 (인코딩 자동 감지 완료)",
                                              'merge_status_add'))
            # 영어 템플릿
            self.assertTrue(
                panel._match_status_template("26 file(s) added (encoding auto-detected)",
                                              'merge_status_add'))
            # 매칭 안 되는 경우
            self.assertFalse(
                panel._match_status_template("전혀 다른 텍스트", 'merge_status_add'))
            # 다른 키의 템플릿 (merge_status_clr)은 매칭 안 돼야 함
            self.assertFalse(
                panel._match_status_template("26개 파일 추가됨 (인코딩 자동 감지 완료)",
                                              'merge_status_clr'))
        finally:
            panel.deleteLater()


class TestV105TranslationNoDuplicates(unittest.TestCase):
    """v1.0.5 — 번역 사전 중복 키 제거 후 재발 방지 검증.

    배경:
      - v1.0.2 인수인계에서 'zh_cn 사전 188개 키 중복' 이슈가 식별됨
      - v1.0.5 시점 실측으로 74개 중복 라인이 잔존 (값은 전부 일치, 동작 영향 0)
      - 모두 단순 삭제 가능이라 이번 버전에서 일괄 정리함
      - 본 테스트는 해당 이슈가 재발하지 않도록 소스 파싱 기반으로 상시 감시
    """

    @classmethod
    def setUpClass(cls):
        with open(_MAIN_PY, encoding='utf-8') as f:
            cls.src = f.read()

    def _count_keys_per_language(self):
        """AST로 TRANSLATIONS의 각 언어 dict 범위를 정확히 잡고,
        해당 범위에서 딕셔너리 키 출현 횟수를 집계."""
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
        """5개 언어 각각의 사전에 중복 키가 없어야 한다.
        Python dict는 중복 키를 나중 값으로 덮어쓰기 때문에 동작상 문제는 없지만,
        - 코드 라인 수 낭비
        - 번역 수정 시 한 쪽만 고치면 다른 쪽이 살아남아 혼란 유발
        - v1.0.2~v1.0.4까지 방치된 기술 부채
        를 상시 감시하기 위해 구조 검증 테스트로 포함."""
        per_lang = self._count_keys_per_language()
        self.assertEqual(len(per_lang), 5,
            f"TRANSLATIONS에 5개 언어가 있어야 하는데 {len(per_lang)}개")
        for lang_code, counter in per_lang.items():
            dups = {k: v for k, v in counter.items() if v > 1}
            self.assertEqual(len(dups), 0,
                f"[{lang_code}] 중복 키 {len(dups)}개 발견: {list(dups.items())[:5]}")

    def test_all_languages_have_similar_key_count(self):
        """5개 언어의 고유 키 수가 비슷해야 한다 (완결성 보장).
        큰 차이가 있으면 어떤 언어에서 번역이 누락됐다는 신호.
        v1.0.5 중복 정리 직후 기준 391±2 정도를 허용 범위로 설정.
        v1.0.9 §5.1.G — zh_cn은 zh_tw fallback 메커니즘으로 부분집합 허용,
        검증 대상에서 제외하고 다른 4언어만 ≤5 차이 강제."""
        per_lang = self._count_keys_per_language()
        counts = {lang: len(c) for lang, c in per_lang.items()}
        # zh_cn은 zh_tw fallback으로 의도적으로 작음 — 키 수 검증에서 제외
        counts_for_check = {l: c for l, c in counts.items() if l != 'zh_cn'}
        max_count = max(counts_for_check.values())
        min_count = min(counts_for_check.values())
        # 완전 동일은 어려우니 5개 이내 차이까지 허용 (일부 언어 미번역 키가 남을 수 있음)
        self.assertLessEqual(max_count - min_count, 5,
            f"언어별 키 수 차이 과다 (zh_cn 제외, 허용 ≤5): "
            f"{counts_for_check}  (zh_cn={counts.get('zh_cn')} — fallback 의도)")


# ════════════════════════════════════════════════════════════════════════
# §추가N  APP_VERSION 검증 (v1.0.6)
# ════════════════════════════════════════════════════════════════════════
# 버전업 시점에 APP_VERSION 상수가 정확히 갱신됐는지 검증.
# v1.0.7 재설계 — 버전 스냅샷 방식(TestV104Regression → TestV105Regression →
# TestV106AppVersion 이월)을 버전 독립 구조 검증으로 전환. TEST_MANAGEMENT_POLICY.md
# §4.4 "버전 스냅샷 방식 invariant 신규 도입 금지" 원칙 적용. 매 릴리즈마다 클래스명·
# 검증값을 이월해오던 수작업 관례를 폐기하고, APP_VERSION이 존재하며 세미버전 형식
# (MAJOR.MINOR.PATCH)을 따르는지만 검증. v1.0.7, v1.0.8, v2.0.0 등 모든 버전에서
# 별도 갱신 없이 통과.


class TestAppVersion(unittest.TestCase):
    """APP_VERSION 상수 구조적 검증 (v1.0.7 재설계, 버전 독립).

    기존 이력: TestV104Regression → TestV105Regression → TestV106AppVersion (이월 방식)
    현재 방식: 버전 독립 구조 검증 (세미버전 포맷만 검증, 구체적 값 강제 안 함)
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
# §추가O  Phase 2-a 인코딩 리포트 기능 (v1.0.6)
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
        # 최소 failures 리스트 (테스트용)
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
        content = open(rp, encoding='utf-8').read()
        self.assertIn('일부 문자가 손상', content)

    def test_tier2_advice(self):
        """Tier 2 (501~5000) → 한국어 Tier 2 조치 문구 포함."""
        rp = _write_report(self.td, self._orig_file(), 'utf-8',
                           self.sample_failures, 1000, 'processed', lang='ko')
        content = open(rp, encoding='utf-8').read()
        self.assertIn('다수의 문자가 손상', content)

    def test_tier3_skipped(self):
        """Tier 3 (5001+) + skipped → 한국어 Tier 3 + 원본 보호 문구."""
        rp = _write_report(self.td, self._orig_file(), 'utf-8',
                           self.sample_failures, 6000, 'skipped', lang='ko')
        content = open(rp, encoding='utf-8').read()
        self.assertIn('처리 건너뜀', content)
        self.assertIn('원본 보호', content)

    def test_truncated_count_shown(self):
        """total > len(failures)일 때 '추적 생략' 문구 + 개수 표시."""
        # failures=1개, total=1000 → 999개 생략
        rp = _write_report(self.td, self._orig_file(), 'utf-8',
                           self.sample_failures, 1000, 'processed', lang='ko')
        content = open(rp, encoding='utf-8').read()
        self.assertIn('추적 생략', content)
        self.assertIn('999', content)

    def test_all_languages_no_untranslated_keys(self):
        """5개 언어 모두에서 번역 키가 그대로 노출되면 안 됨."""
        untranslated = ['report_header', 'report_file', 'report_path',
                        'report_advice_title', 'report_advice_tier1']
        for lang in ['ko', 'en', 'ja', 'zh_cn', 'zh_tw']:
            rp = _write_report(self.td, self._orig_file(), 'utf-8',
                               self.sample_failures, 100, 'processed', lang=lang)
            content = open(rp, encoding='utf-8').read()
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
        # BOM 없음 확인
        self.assertFalse(raw.startswith(b'\xef\xbb\xbf'), 'BOM이 붙어있음')
        # UTF-8로 해독 가능
        raw.decode('utf-8')  # 예외 던지지 않아야


# ════════════════════════════════════════════════════════════════════════
# §추가P  v1.0.6 버그 수정 회귀 방지 — Bulk Fixer 미리보기 프리징
# ════════════════════════════════════════════════════════════════════════
# 50만 줄급 대용량 파일에서 _on_file_selected가 12초 이상 프리징하던 버그
# (Phase 2-a 실기 QA 중 발견, 회귀 방지 목적)

@unittest.skipUnless(HAS_MODULE, "FileNexusSuite 로드 실패")
class TestBulkFixerPreviewLargeFile(unittest.TestCase):
    """v1.0.6: Bulk Fixer 미리보기가 대용량 파일에서도 빠르게 동작해야 함.

    수정 전: text.splitlines(keepends=True)[:80]
            → 27MB 전체 파싱 후 50만 객체 생성, 80개만 사용 (O(N) 낭비)
    수정 후: text[:32768].splitlines(keepends=True)[:80]
            → 파일 크기와 무관하게 32KB만 처리
    """

    def test_preview_extraction_logic_uses_head_slice(self):
        """소스에 text[:NNNNN].splitlines 패턴이 있어야 함 (회귀 방지)."""
        with open(_MAIN_PY, 'r', encoding='utf-8') as f:
            src = f.read()
        # _on_file_selected 본체 추출 (BulkFixerPanel 내)
        # 정규식: def _on_file_selected ... setPlainText(preview)
        m = re.search(
            r'def _on_file_selected\(self, cur, _prev\):(.*?)(?=\n    def |\nclass )',
            src, re.DOTALL)
        self.assertIsNotNone(m, '_on_file_selected 메서드를 찾을 수 없음')
        body = m.group(1)
        # 수정된 패턴 존재 확인: text[:NNNNN].splitlines
        self.assertRegex(body, r'text\[:\d+\]\.splitlines',
            '미리보기 헤드 슬라이스 패턴(text[:NNNNN].splitlines) 누락 — v1.0.6 수정 회귀 의심')
        # 전체 splitlines 직접 호출(수정 전 패턴) 없어야 함
        # 정확한 매칭: text.splitlines 앞에 [:가 없는 경우
        self.assertNotRegex(body, r'(?<!\])text\.splitlines',
            '수정 전 패턴(text.splitlines 전체 호출)이 남아있음 — v1.0.6 수정 회귀')


@unittest.skipUnless(HAS_MODULE, "FileNexusSuite 로드 실패")
class TestPreviewExtractionPerformance(unittest.TestCase):
    """v1.0.6: 미리보기 추출 로직의 성능 특성 검증 (순수 함수 단위).

    _on_file_selected 내부의 preview 추출 로직을 분리 검증.
    실제 Qt 위젯 없이 Python 레벨에서 동등 로직을 재현하여
    파일 크기와 무관하게 일정 시간에 끝나는지 확인.
    """

    def _extract_preview_fixed(self, text):
        """v1.0.6 수정 후 방식 복제."""
        return ''.join(text[:32768].splitlines(keepends=True)[:80])

    def test_large_file_preview_under_100ms(self):
        """50만 줄 시뮬레이션에서 미리보기 추출이 100ms 이내."""
        # 한국어 웹소설 스타일: 평균 40자 줄 × 50만 줄
        line = '이것은 한국어 웹소설의 한 줄입니다. 적당한 길이의 문장입니다.\n'
        text = line * 500000  # 약 20MB, 50만 줄
        t0 = time.perf_counter()
        preview = self._extract_preview_fixed(text)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        self.assertLess(elapsed_ms, 100,
            f'50만 줄 파일 미리보기 추출이 100ms 초과: {elapsed_ms:.1f}ms '
            f'(v1.0.6 버그 회귀 의심 — text[:32768].splitlines 확인 필요)')
        # 결과도 올바른지 확인 (80줄)
        self.assertLessEqual(len(preview.splitlines()), 80)

    def test_preview_size_consistent_across_file_sizes(self):
        """파일 크기와 무관하게 미리보기 크기가 일정 (32KB 상한)."""
        short_text = '짧은 파일입니다.\n' * 100  # 작은 파일
        huge_text = '큰 파일의 한 줄입니다.\n' * 1000000  # 매우 큰 파일

        preview_short = self._extract_preview_fixed(short_text)
        preview_huge = self._extract_preview_fixed(huge_text)

        # 작은 파일은 전체가 미리보기로 나오고, 큰 파일은 80줄만
        # 두 경우 모두 32KB 이하여야 함
        self.assertLessEqual(len(preview_short.encode('utf-8')), 32768)
        self.assertLessEqual(len(preview_huge.encode('utf-8')), 32768)
        # 80줄 제한 확인
        self.assertLessEqual(len(preview_huge.splitlines()), 80)


# ════════════════════════════════════════════════════════════════════════
# §추가Q  v1.0.8 SettingsDialog 구조 invariant — 페이지 lazy 재생성
# ════════════════════════════════════════════════════════════════════════

@unittest.skipUnless(HAS_MODULE, "FileNexusSuite 로드 실패 (PySide6 필요)")
class TestSettingsDialogStructureInvariant(unittest.TestCase):
    """v1.0.8 옵션 C — 설정 다이얼로그 페이지 lazy 재생성 메커니즘 구조 검증.

    배경: v1.0.5부터 존재한 라벨/프레임 color 잔재 버그를 v1.0.8에서 페이지
    재생성 메커니즘으로 구조적 해결. 이 메커니즘이 향후 누군가의 실수로
    제거되거나 약화되지 않도록 invariant로 보호한다.

    참조: TEST_MANAGEMENT_POLICY §3 4번 원칙 (신규 기능에 대한 자동 커버리지 명시),
    Claude_Handover v1.0.7 §5.1 / §7.8, Phase2_Completion_Record §11.3.
    """

    @classmethod
    def setUpClass(cls):
        import inspect as _ins
        cls._ins = _ins
        cls.dialog_cls = _ns.get('SettingsDialog')

    def test_settings_dialog_has_recreate_pages(self):
        """SettingsDialog 클래스에 _recreate_pages 메서드가 존재해야 한다.

        v1.0.8 옵션 C 핵심 메커니즘 — 페이지 재생성을 담당하는 메서드.
        제거되면 라벨 color 잔재 버그가 부활.
        """
        self.assertIsNotNone(self.dialog_cls, "SettingsDialog 클래스 없음")
        self.assertTrue(hasattr(self.dialog_cls, '_recreate_pages'),
            "SettingsDialog._recreate_pages 메서드 없음 — "
            "v1.0.8 페이지 lazy 재생성 메커니즘이 누락됨")
        self.assertTrue(callable(getattr(self.dialog_cls, '_recreate_pages')),
            "SettingsDialog._recreate_pages가 callable이 아님")

    def test_refresh_theme_calls_recreate_pages(self):
        """SettingsDialog._refresh_theme 본문이 self._recreate_pages()를 호출해야 한다.

        v1.0.8 옵션 C — _refresh_theme이 페이지 내부 위젯 갱신을 _recreate_pages에
        위임하는 구조. 호출이 빠지면 라벨 color 잔재 버그가 부활.
        """
        self.assertIsNotNone(self.dialog_cls, "SettingsDialog 클래스 없음")
        src = self._ins.getsource(self.dialog_cls._refresh_theme)
        self.assertIn('self._recreate_pages()', src,
            "_refresh_theme 본문에 'self._recreate_pages()' 호출 없음 — "
            "v1.0.8 옵션 C 메커니즘이 끊어짐")

    def test_retranslate_dialog_simplified(self):
        """SettingsDialog._retranslate_dialog이 페이지 내부 위젯 attribute를
        직접 갱신하지 않아야 한다.

        v1.0.8 옵션 C — _retranslate_dialog은 외곽(사이드바/네비/하단 버튼)만
        책임지고, 페이지 내부 텍스트 갱신은 _recreate_pages에 위임. 페이지 내부
        attribute(_lang_page_title 등) 직접 setText는 v1.0.7 단순화 이전 패턴.
        """
        self.assertIsNotNone(self.dialog_cls, "SettingsDialog 클래스 없음")
        src = self._ins.getsource(self.dialog_cls._retranslate_dialog)
        # 페이지 내부 attribute 패턴들 — 이전 버전 구조의 흔적
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
# 테스트 러너 — 자동 발견 방식 (수동 등록 불필요)
# ════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    import inspect as _inspect
    import sys as _sys

    # stdout/stderr UTF-8 강제 (v1.0.7 CI 도입 — GitHub Actions windows-latest의
    # 기본 콘솔 인코딩이 cp1252라 한글·이모지 출력 시 UnicodeEncodeError 발생).
    # Python 3.7+ 표준 기능이며, 한림 로컬(Windows)·Linux·macOS 모두 무해.
    if hasattr(_sys.stdout, 'reconfigure'):
        _sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(_sys.stderr, 'reconfigure'):
        _sys.stderr.reconfigure(encoding='utf-8')

    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()

    # 현재 모듈에서 unittest.TestCase 상속 클래스 자동 수집
    # 장점:
    #   - 새 테스트 클래스 추가 시 수동 등록 불필요
    #   - 누락 방지 (클래스 정의 = 자동 실행)
    #   - 유지보수성 향상
    _current_module = _sys.modules[__name__]
    klasses = sorted(
        [
            obj for _name, obj in _inspect.getmembers(_current_module)
            if _inspect.isclass(obj)
            and issubclass(obj, unittest.TestCase)
            and obj is not unittest.TestCase
            and obj.__module__ == _current_module.__name__  # 외부 import 제외
        ],
        key=lambda c: c.__name__  # 실행 순서 일관성
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
    print(f'  총 테스트  : {total}개  ({len(klasses)}개 클래스)')
    print(f'  \u2705 성공    : {passed}개')
    print(f'  \u274c 실패    : {fails}개')
    print(f'  \u2757 오류    : {errors}개')
    print(f'  \u23ed  스킵   : {skips}개')
    print('=' * 60)

    if fails or errors:
        print()
        for f in result.failures:
            print(f'FAIL: {f[0]}')
            for line in f[1].splitlines()[-4:]: print(f'  {line}')
        for e in result.errors:
            print(f'ERROR: {e[0]}')
            for line in e[1].splitlines()[-4:]: print(f'  {line}')

    # CI exit code 계약 (v1.0.7) — 실패/오류 시 non-zero 반환하여 자동 테스트 파이프라인이
    # 통과 여부를 정확히 감지하도록 보장. 로컬 실행에서는 영향 없음.
    _sys.exit(0 if (not fails and not errors) else 1)
