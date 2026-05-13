"""
File Nexus Suite — UI 미리보기 도구 (v1.0.0 최신화)
각 팝업, 다이얼로그, 진행바, 애니메이션 위젯을 버튼 클릭으로 바로 확인합니다.
실행: python preview_ui.py  (FileNexusSuite.py와 같은 폴더에 위치)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── 1. QApplication 먼저 생성 ─────────────────────────────────────────
from PySide6.QtWidgets import QApplication
app = QApplication(sys.argv)

# ── 2. 모듈 로드 및 언어/테마 초기화 ─────────────────────────────────
import FileNexusSuite as fns
fns._CFG.load()
fns._current_lang = fns._CFG.get('language', fns._detect_os_lang())
_resolved = fns._resolve_theme(fns._CFG.get('theme', 'auto'))
_t_colors  = fns.THEMES.get(_resolved, fns.THEMES['light'])
fns._unpack(_t_colors)
app.setStyleSheet(fns.make_style(_t_colors))

# ── 3. 초기화 후 임포트 ───────────────────────────────────────────────
from FileNexusSuite import (
    _tr_args, THEMES, make_style, _resolve_theme, _CFG,
    _show_first_run_notice,
    _dlg_info, _dlg_warn, _dlg_error, _dlg_question,
    _btn_style, _make_app_icon, _dlg_icon_pix,
    _svg_icon, _SVG_PATHS, _SVG_LINE_ICONS,
    _GearButton, _ScrollHint,
    SettingsDialog,
)
from fns_help import HelpDialog, _HelpButton, LicenseDialog
from PySide6.QtCore import QT_TR_NOOP
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QProgressBar, QFrame, QScrollArea,
    QGroupBox, QDialog, QComboBox,
)
from PySide6.QtCore import Qt, QTimer, QSize


class PreviewWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Nexus Suite — UI Preview")
        try: self.setWindowIcon(_make_app_icon())
        except Exception: pass
        self.setMinimumWidth(540)
        self.resize(540, 780)

        # 모든 섹션 버튼·GroupBox 참조 — _restyle()에서 일괄 갱신
        self._all_btns: list = []
        self._all_grps: list = []

        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        self.setCentralWidget(scroll)
        container = QWidget(); scroll.setWidget(container)
        root = QVBoxLayout(container)
        root.setContentsMargins(20, 20, 20, 20); root.setSpacing(14)

        # ── 테마 / 언어 선택 ─────────────────────────────────────────
        top_row = QHBoxLayout()
        # 테마
        theme_lbl = QLabel("Theme:")
        theme_lbl.setStyleSheet(f"font-size:13px;color:{fns.TEXT};font-weight:600;")
        self._theme_combo = QComboBox()
        self._theme_combo.addItems(['auto'] + list(THEMES.keys()))
        idx = self._theme_combo.findText(_CFG.get('theme', 'auto'))
        if idx >= 0: self._theme_combo.setCurrentIndex(idx)
        self._theme_combo.currentTextChanged.connect(self._apply_theme)
        # 언어
        lang_lbl = QLabel("Lang:")
        lang_lbl.setStyleSheet(f"font-size:13px;color:{fns.TEXT};font-weight:600;")
        self._lang_combo = QComboBox()
        self._lang_combo.addItems(['ko', 'en', 'ja', 'zh_cn', 'zh_tw'])
        lang_idx = self._lang_combo.findText(fns._current_lang)
        if lang_idx >= 0: self._lang_combo.setCurrentIndex(lang_idx)
        self._lang_combo.currentTextChanged.connect(self._apply_lang)

        top_row.addWidget(theme_lbl); top_row.addWidget(self._theme_combo)
        top_row.addSpacing(16)
        top_row.addWidget(lang_lbl); top_row.addWidget(self._lang_combo)
        top_row.addStretch()
        root.addLayout(top_row)
        self._add_sep(root)

        # ── 팝업 / 다이얼로그 (버튼 레이블 retranslate 대상) ──────────
        self._popup_grp, self._popup_btns = self._section_tracked(
            "📋 Popups / Dialogs",
            [
                (QT_TR_NOOP('Welcome to File Nexus Suite!'),  self._show_first_run),
                (QT_TR_NOOP('Task in Progress'),              self._show_close_busy),
                (QT_TR_NOOP('Help'),                          self._show_help),
                (QT_TR_NOOP('License'),                       self._show_license),
            ]
        )
        root.addWidget(self._popup_grp)

        # ── 일반 다이얼로그 (버튼 레이블 + 다이얼로그 내용 모두 self.tr()) ──
        self._dlg_grp, self._dlg_btns = self._section_tracked(
            "💬 Message Dialogs",
            [
                (QT_TR_NOOP('Done'),
                 lambda: _dlg_info(self, self.tr('Done'),
                                   _tr_args(self.tr('%1 file(s) added (encoding auto-detected)'), 3))),
                (QT_TR_NOOP('Warning'),
                 lambda: _dlg_warn(self, self.tr('Warning'),
                                   self.tr('Please add files first.'))),
                (QT_TR_NOOP('Error'),
                 lambda: _dlg_error(self, self.tr('Error'),
                                    self.tr('File not found'))),
                (QT_TR_NOOP('Confirm'),
                 lambda: _dlg_question(self, self.tr('Confirm'),
                                       self.tr('Remove all files from the list?'))),
            ]
        )
        root.addWidget(self._dlg_grp)

        # ── 진행 바 ──────────────────────────────────────────────────
        root.addWidget(self._section("⏳ Progress Bars", [
            ("Overall progress (5s)",          self._run_progress),
            ("Per-file progress (3 steps)",    self._run_file_progress),
            ("Folder scan bar",                self._run_scan_bar),
        ]))

        # 전체 진행 바 (8px)
        self._pb = QProgressBar()
        self._pb.setRange(0, 100); self._pb.setValue(0)
        self._pb.setFixedHeight(8); self._pb.setTextVisible(False)
        self._pb.setVisible(False)
        root.addWidget(self._pb)
        self._pb_lbl = QLabel("")
        self._pb_lbl.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._pb_lbl.setFixedHeight(16)
        self._pb_lbl.setStyleSheet(
            f"font-size:11px;color:{fns.MUTED};"
            f"font-family:'Consolas','Courier New','Menlo',monospace;")
        self._pb_lbl.setVisible(False)
        root.addWidget(self._pb_lbl)

        # 현재 파일 진행 바 (5px)
        self._file_pb = QProgressBar()
        self._file_pb.setRange(0, 100); self._file_pb.setValue(0)
        self._file_pb.setFixedHeight(5); self._file_pb.setTextVisible(False)
        self._file_pb.setVisible(False)
        root.addWidget(self._file_pb)
        self._file_pb_lbl = QLabel("")
        self._file_pb_lbl.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._file_pb_lbl.setFixedHeight(16)
        self._file_pb_lbl.setStyleSheet(
            f"font-size:11px;color:{fns.MUTED};"
            f"font-family:'Consolas','Courier New','Menlo',monospace;")
        self._file_pb_lbl.setVisible(False)
        root.addWidget(self._file_pb_lbl)

        # 스캔 바 (5px)
        self._scan_pb = QProgressBar()
        self._scan_pb.setRange(0, 100); self._scan_pb.setValue(0)
        self._scan_pb.setFixedHeight(5); self._scan_pb.setTextVisible(False)
        self._scan_pb.setVisible(False)
        root.addWidget(self._scan_pb)
        self._scan_lbl = QLabel("")
        self._scan_lbl.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._scan_lbl.setFixedHeight(16)
        self._scan_lbl.setStyleSheet(
            f"font-size:11px;color:{fns.MUTED};"
            f"font-family:'Consolas','Courier New','Menlo',monospace;")
        self._scan_lbl.setVisible(False)
        root.addWidget(self._scan_lbl)

        # 상단 테마·언어 레이블 참조 보관 (_restyle용)
        self._theme_lbl = theme_lbl
        self._lang_lbl  = lang_lbl

        self._add_sep(root)

        # ── 다이얼로그 아이콘 ─────────────────────────────────────────
        root.addWidget(self._section("🎨 Dialog Icons", [
            ("info",     lambda: self._show_icon('info')),
            ("warn",     lambda: self._show_icon('warn')),
            ("error",    lambda: self._show_icon('error')),
            ("question", lambda: self._show_icon('question')),
        ]))

        self._add_sep(root)

        # ── SVG 아이콘 미리보기 (v1.0.0) ──────────────────────
        root.addWidget(self._section("🖼️ SVG Icons — Filled", [
            (f"{k}",  (lambda k=k: self._show_svg_icon(k, filled=True)))
            for k in _SVG_PATHS
        ]))
        root.addWidget(self._section("🖼️ SVG Icons — Line", [
            (f"{k}", (lambda k=k: self._show_svg_icon(k, filled=False)))
            for k in _SVG_LINE_ICONS
        ]))

        self._add_sep(root)

        # ── 애니메이션 위젯 (v1.0.0 신규) ────────────────────────────
        root.addWidget(self._section("✨ Animated Widgets", [
            ("_HelpButton — hover sine",       self._show_help_button),
            ("_GearButton — hover rotate",     self._show_gear_button),
            ("_ScrollHint — scroll overlay",   self._show_scroll_hint),
        ]))

        self._add_sep(root)

        # ── 다이얼로그 (v1.0.0 신규) ─────────────────────────────────
        root.addWidget(self._section("⚙️ Dialogs / Panels", [
            ("SettingsDialog",                 self._show_settings),
        ]))

        self._add_sep(root)

        # ── Bulk Fixer 프로그레스 바 (v1.0.0 스타일) ──────────────────
        root.addWidget(self._section("📊 Bulk Fixer Progress (v1.0.0)", [
            ("2-tier progress (overall + file)", self._run_bulk_progress),
        ]))

        # 전체 바 (8px)
        self._bulk_pb = QProgressBar()
        self._bulk_pb.setRange(0, 100); self._bulk_pb.setValue(0)
        self._bulk_pb.setFixedHeight(8); self._bulk_pb.setTextVisible(False)
        self._bulk_pb.setVisible(False)
        root.addWidget(self._bulk_pb)
        # 전체 바 아래 우측 정렬 레이블
        self._bulk_total_lbl = QLabel("")
        self._bulk_total_lbl.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._bulk_total_lbl.setFixedHeight(16)
        self._bulk_total_lbl.setStyleSheet(
            f"font-size:11px;color:{fns.MUTED};"
            f"font-family:'Consolas','Courier New','Menlo',monospace;")
        self._bulk_total_lbl.setVisible(False)
        root.addWidget(self._bulk_total_lbl)

        # 파일 바 (5px, 불투명도 낮춤)
        self._bulk_file_pb = QProgressBar()
        self._bulk_file_pb.setRange(0, 100); self._bulk_file_pb.setValue(0)
        self._bulk_file_pb.setFixedHeight(5); self._bulk_file_pb.setTextVisible(False)
        self._bulk_file_pb.setVisible(False)
        root.addWidget(self._bulk_file_pb)
        # 파일 바 아래 우측 정렬 레이블
        self._bulk_file_lbl = QLabel("")
        self._bulk_file_lbl.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._bulk_file_lbl.setFixedHeight(16)
        self._bulk_file_lbl.setStyleSheet(
            f"font-size:11px;color:{fns.MUTED};"
            f"font-family:'Consolas','Courier New','Menlo',monospace;")
        self._bulk_file_lbl.setVisible(False)
        root.addWidget(self._bulk_file_lbl)

        root.addStretch()
        self._pb_timer = self._file_pb_timer = self._scan_timer = None
        self._bulk_timer = None
        self._pb_val = self._file_pb_val = self._scan_val = 0
        self._bulk_total_val = self._bulk_file_val = 0
        self._bulk_file_idx = 1
        self._scan_found = 0
        self._file_idx = 1

    # ── 헬퍼 ─────────────────────────────────────────────────────────
    def _add_sep(self, layout):
        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background:{fns.BORDER};max-height:1px;border:none;")
        layout.addWidget(sep)

    def _btn_ss(self):
        """섹션 버튼 공통 stylesheet — fns 전역에서 현재 색상을 읽음."""
        return (
            f"QPushButton{{background:{fns.SRF2};border:1px solid {fns.BORDER};"
            f"border-radius:7px;color:{fns.TEXT};font-size:13px;"
            f"padding:0 14px;text-align:left;}}"
            f"QPushButton:hover{{background:{fns.ACCENT};color:white;border-color:{fns.ACCENT};}}"
        )

    def _grp_ss(self):
        """섹션 GroupBox 공통 stylesheet — fns 전역에서 현재 색상을 읽음."""
        return (
            f"QGroupBox{{font-size:13px;font-weight:700;color:{fns.TEXT};"
            f"border:1px solid {fns.BORDER};border-radius:8px;"
            f"margin-top:8px;padding-top:8px;}}"
            f"QGroupBox::title{{subcontrol-origin:margin;left:10px;padding:0 4px;}}"
        )

    def _section(self, title, buttons):
        gb = QGroupBox(title)
        gb.setStyleSheet(self._grp_ss())
        lay = QVBoxLayout(gb); lay.setSpacing(6); lay.setContentsMargins(12, 8, 12, 10)
        for label, cb in buttons:
            btn = QPushButton(label); btn.setFixedHeight(34)
            btn.setStyleSheet(self._btn_ss())
            btn.clicked.connect(cb)
            lay.addWidget(btn)
            self._all_btns.append(btn)
        self._all_grps.append(gb)
        return gb

    def _section_tracked(self, title, items):
        """self.tr() 기반 버튼으로 섹션 생성 — retranslate 지원.

        items: list of (t_key, callback)
        returns: (QGroupBox, dict[t_key → QPushButton])
        """
        gb = QGroupBox(title)
        gb.setStyleSheet(self._grp_ss())
        lay = QVBoxLayout(gb); lay.setSpacing(6); lay.setContentsMargins(12, 8, 12, 10)
        btns = {}
        for t_key, cb in items:
            btn = QPushButton(self.tr(t_key)); btn.setFixedHeight(34)
            btn.setStyleSheet(self._btn_ss())
            btn.clicked.connect(cb)
            lay.addWidget(btn)
            btns[t_key] = btn
            self._all_btns.append(btn)
        self._all_grps.append(gb)
        return gb, btns

    def _apply_theme(self, theme_name):
        resolved = _resolve_theme(theme_name)
        t = THEMES.get(resolved, THEMES['light'])
        fns._unpack(t)
        QApplication.instance().setStyleSheet(make_style(t))
        self._restyle()

    def _restyle(self):
        """테마 변경 후 inline stylesheet를 가진 위젯을 일괄 갱신."""
        ss_btn = self._btn_ss()
        ss_grp = self._grp_ss()
        for btn in self._all_btns:
            btn.setStyleSheet(ss_btn)
        for grp in self._all_grps:
            grp.setStyleSheet(ss_grp)
        # 상단 레이블
        lbl_ss = f"font-size:13px;color:{fns.TEXT};font-weight:600;"
        self._theme_lbl.setStyleSheet(lbl_ss)
        self._lang_lbl.setStyleSheet(lbl_ss)
        # 진행 바
        pb_ss8  = (f"QProgressBar{{border:none;background:{fns.BORDER};border-radius:4px;}}"
                   f"QProgressBar::chunk{{background:{fns.ACCENT};border-radius:4px;}}")
        pb_ss5  = (f"QProgressBar{{border:none;background:{fns.BORDER};border-radius:2px;}}"
                   f"QProgressBar::chunk{{background:{fns.ACCENT};border-radius:2px;opacity:0.7;}}")
        mono_ss = (f"font-size:11px;color:{fns.MUTED};"
                   f"font-family:'Consolas','Courier New','Menlo',monospace;")
        self._pb.setStyleSheet(pb_ss8)
        self._file_pb.setStyleSheet(pb_ss5)
        self._scan_pb.setStyleSheet(pb_ss5)
        # 진행 바 레이블
        self._pb_lbl.setStyleSheet(mono_ss)
        self._file_pb_lbl.setStyleSheet(mono_ss)
        self._scan_lbl.setStyleSheet(mono_ss)
        # Bulk Fixer 2단 진행 바
        self._bulk_pb.setStyleSheet(pb_ss8)
        self._bulk_file_pb.setStyleSheet(pb_ss5)
        self._bulk_total_lbl.setStyleSheet(mono_ss)
        self._bulk_file_lbl.setStyleSheet(mono_ss)

    def _apply_lang(self, lang):
        fns._current_lang = lang
        self._retranslate()

    def _retranslate(self):
        """언어 변경 시 번역 가능한 모든 위젯 텍스트를 갱신."""
        # 팝업 / 일반 다이얼로그 섹션 버튼
        for key, btn in {**self._popup_btns, **self._dlg_btns}.items():
            btn.setText(self.tr(key))
        # 닫기 버튼이 있는 고정 다이얼로그 레이블은 재생성 시점(클릭)에 self.tr() 호출하므로 자동 반영

    # ── 팝업 핸들러 ───────────────────────────────────────────────────
    def _show_first_run(self):
        _show_first_run_notice(self)

    def _show_close_busy(self):
        dlg = QDialog(self)
        dlg.setWindowTitle(self.tr('Task in Progress'))
        try: dlg.setWindowIcon(_make_app_icon())
        except Exception: pass
        dlg.setMinimumWidth(380)
        dlg.setWindowFlags(dlg.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        dlg.setStyleSheet(
            f"QDialog{{background:{fns.SURFACE};}} "
            f"QLabel{{background:transparent;color:{fns.TEXT};}}")
        root = QVBoxLayout(dlg)
        root.setContentsMargins(24, 20, 24, 16); root.setSpacing(12)

        row = QHBoxLayout(); row.setSpacing(14)
        row.setAlignment(Qt.AlignmentFlag.AlignTop)
        ico = QLabel(); ico.setPixmap(_dlg_icon_pix('warn', 40))
        ico.setFixedSize(40, 40); ico.setStyleSheet("background:transparent;")
        busy_text = self.tr('A task is currently running. Quitting now may result in data loss.\n\nAre you sure you want to quit?')
        msg = QLabel(f"▸ Bulk Fixer\n\n{busy_text}")
        msg.setWordWrap(True)
        msg.setStyleSheet(f"font-size:13px;color:{fns.TEXT};")
        row.addWidget(ico); row.addWidget(msg, 1)
        root.addLayout(row)

        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background:{fns.BORDER};max-height:1px;border:none;")
        root.addWidget(sep)

        br = QHBoxLayout(); br.setSpacing(8); br.addStretch()
        btn_cancel = QPushButton(self.tr('Cancel'))
        btn_cancel.setStyleSheet(_btn_style(False))
        btn_cancel.clicked.connect(dlg.reject)
        btn_exit = QPushButton(self.tr('Quit'))
        btn_exit.setStyleSheet(
            "QPushButton{background:#C04030;border:none;color:white;"
            "border-radius:8px;padding:9px 28px;font-size:12px;font-weight:600;"
            "min-width:80px;}"
            "QPushButton:hover{background:#A03020;}")
        btn_exit.clicked.connect(dlg.accept)
        btn_cancel.setDefault(True)
        br.addWidget(btn_cancel); br.addWidget(btn_exit)
        root.addLayout(br)
        dlg.show()
        btn_w = max(btn_cancel.sizeHint().width(), btn_exit.sizeHint().width())
        btn_cancel.setFixedWidth(btn_w); btn_exit.setFixedWidth(btn_w)
        dlg.exec()

    def _show_help(self):
        dlg = HelpDialog(self); dlg.exec()

    def _show_license(self):
        dlg = LicenseDialog(self); dlg.exec()

    # ── 진행 바 ───────────────────────────────────────────────────────
    def _run_progress(self):
        if self._pb_timer and self._pb_timer.isActive(): return
        self._pb.setVisible(True); self._pb_lbl.setVisible(True)
        self._pb.setValue(0); self._pb_lbl.setText("  0%")
        self._pb_val = 0
        self._pb_timer = QTimer(self)
        self._pb_timer.timeout.connect(self._tick_pb)
        self._pb_timer.start(50)

    def _tick_pb(self):
        self._pb_val = min(self._pb_val + 2, 100)
        self._pb.setValue(self._pb_val)
        self._pb_lbl.setText(f"{self._pb_val:>3d}%")
        if self._pb_val >= 100:
            self._pb_timer.stop()
            QTimer.singleShot(1200, lambda: (
                self._pb.setVisible(False), self._pb_lbl.setVisible(False)))

    def _run_file_progress(self):
        """Per-file 2-tier progress bar"""
        if self._file_pb_timer and self._file_pb_timer.isActive(): return
        self._file_pb.setVisible(True); self._file_pb_lbl.setVisible(True)
        self._file_pb.setValue(0)
        self._file_pb_lbl.setText("document_01.txt    0%")
        self._file_pb_val = 0
        self._file_idx = 1
        self._file_pb_timer = QTimer(self)
        self._file_pb_timer.timeout.connect(self._tick_file_pb)
        self._file_pb_timer.start(60)

    def _tick_file_pb(self):
        self._file_pb_val = min(self._file_pb_val + 2, 100)
        self._file_pb.setValue(self._file_pb_val)
        fname = f"document_{self._file_idx:02d}.txt"
        self._file_pb_lbl.setText(
            f"{fname}  {self._file_pb_val:>3d}%")
        if self._file_pb_val >= 100:
            self._file_idx += 1
            if self._file_idx > 5:
                self._file_pb_timer.stop()
                self._file_pb_lbl.setText(_tr_args(self.tr('✔  Done — %1 file(s) processed'), 5))
                QTimer.singleShot(1500, lambda: (
                    self._file_pb.setVisible(False),
                    self._file_pb_lbl.setVisible(False)))
            else:
                self._file_pb_val = 0

    def _run_scan_bar(self):
        if self._scan_timer and self._scan_timer.isActive(): return
        self._scan_pb.setVisible(True); self._scan_lbl.setVisible(True)
        self._scan_pb.setValue(0); self._scan_found = 0; self._scan_val = 0
        self._scan_timer = QTimer(self)
        self._scan_timer.timeout.connect(self._tick_scan)
        self._scan_timer.start(40)

    def _tick_scan(self):
        self._scan_val = min(self._scan_val + 1, 100)
        self._scan_found += 3
        self._scan_pb.setValue(self._scan_val)
        _tr = self.tr('Scanning... %1 found')
        self._scan_lbl.setText(f"{_tr_args(_tr, self._scan_found)}  {self._scan_val:>3d}%")
        if self._scan_val >= 100:
            self._scan_timer.stop()
            self._scan_lbl.setText(_tr_args(self.tr('✔  Done — %1 file(s) processed'), self._scan_found))
            QTimer.singleShot(1500, lambda: (
                self._scan_pb.setVisible(False),
                self._scan_lbl.setVisible(False)))

    def _show_icon(self, kind):
        dlg = QDialog(self); dlg.setWindowTitle(f"Icon — {kind}")
        dlg.setStyleSheet(
            f"QDialog{{background:{fns.SURFACE};}} QLabel{{background:transparent;}}")
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(30, 24, 30, 20); lay.setSpacing(16)
        for size in [24, 32, 44, 56]:
            row = QHBoxLayout()
            lbl = QLabel(f"{size}px")
            lbl.setStyleSheet(f"color:{fns.MUTED};font-size:12px;"); lbl.setFixedWidth(40)
            ico = QLabel(); ico.setPixmap(_dlg_icon_pix(kind, size))
            ico.setFixedSize(size, size)
            row.addWidget(lbl); row.addWidget(ico); row.addStretch()
            lay.addLayout(row)
        btn = QPushButton(self.tr('Close')); btn.setStyleSheet(_btn_style(True))
        btn.clicked.connect(dlg.accept); lay.addWidget(btn)
        dlg.exec()

    def _show_svg_icon(self, key: str, filled: bool):
        """SVG 아이콘 팝업 — Filled / Line 스타일 모두 지원."""
        style = "Filled" if filled else "Line"
        dlg = QDialog(self)
        dlg.setWindowTitle(f"SVG Icon — {key}  [{style}]")
        dlg.setStyleSheet(
            f"QDialog{{background:{fns.SURFACE};}} QLabel{{background:transparent;}}")
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(30, 24, 30, 20); lay.setSpacing(20)

        # 크기별 × 색상별 (ACCENT / TEXT / MUTED / white on ACCENT bg)
        sizes = [16, 18, 24, 32, 48]
        colors = [
            ("ACCENT", fns.ACCENT),
            ("TEXT",   fns.TEXT),
            ("MUTED",  fns.MUTED),
            ("white",  "white"),
        ]

        # 헤더
        hdr = QLabel(f"<b>{key}</b>  <span style='color:{fns.MUTED};font-size:12px;'>[{style}]</span>")
        hdr.setStyleSheet(f"font-size:14px;color:{fns.ACCENT};")
        lay.addWidget(hdr)

        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background:{fns.BORDER};max-height:1px;border:none;")
        lay.addWidget(sep)

        for size in sizes:
            row = QHBoxLayout(); row.setSpacing(20)
            size_lbl = QLabel(f"{size}px")
            size_lbl.setFixedWidth(36)
            size_lbl.setStyleSheet(f"font-size:11px;color:{fns.MUTED};")
            row.addWidget(size_lbl)

            for color_name, color_val in colors:
                col_container = QVBoxLayout(); col_container.setSpacing(2)
                ico_lbl = QLabel()

                # 'white' 아이콘은 ACCENT 배경에 표시
                if color_name == "white":
                    ico_lbl.setFixedSize(size + 8, size + 8)
                    ico_lbl.setStyleSheet(
                        f"background:{fns.ACCENT};border-radius:4px;")
                    ico_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    icon = _svg_icon(key, "white", size)
                    ico_lbl.setPixmap(icon.pixmap(QSize(size, size)))
                else:
                    ico_lbl.setFixedSize(size, size)
                    ico_lbl.setStyleSheet("background:transparent;")
                    icon = _svg_icon(key, color_val, size)
                    ico_lbl.setPixmap(icon.pixmap(QSize(size, size)))

                cap_lbl = QLabel(color_name)
                cap_lbl.setStyleSheet(f"font-size:10px;color:{fns.MUTED};")
                cap_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                col_container.addWidget(ico_lbl, alignment=Qt.AlignmentFlag.AlignHCenter)
                col_container.addWidget(cap_lbl, alignment=Qt.AlignmentFlag.AlignHCenter)
                row.addLayout(col_container)

            row.addStretch()
            lay.addLayout(row)

        sep2 = QFrame(); sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet(f"background:{fns.BORDER};max-height:1px;border:none;")
        lay.addWidget(sep2)

        btn = QPushButton(self.tr('Close')); btn.setStyleSheet(_btn_style(True))
        btn.clicked.connect(dlg.accept); lay.addWidget(btn)
        dlg.exec()

    # ── 애니메이션 위젯 핸들러 (v1.0.0) ──────────────────────────────
    def _show_help_button(self):
        """_HelpButton 호버 사인파 애니메이션 미리보기."""
        dlg = QDialog(self); dlg.setWindowTitle("_HelpButton Preview")
        dlg.setStyleSheet(f"QDialog{{background:{fns.SURFACE};}}")
        try: dlg.setWindowIcon(_make_app_icon())
        except Exception: pass
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(30, 24, 30, 20); lay.setSpacing(16)

        desc = QLabel("Hover to see the icon bounce up with a sine wave.")
        desc.setStyleSheet(f"font-size:13px;color:{fns.MUTED};")
        desc.setWordWrap(True)
        lay.addWidget(desc)

        row = QHBoxLayout(); row.setSpacing(16)
        for key in ('question', 'info'):
            hb = _HelpButton()
            hb.setIcon(_svg_icon(key, fns.ACCENT, 22))
            hb.setIconSize(QSize(22, 22))
            hb.setFixedSize(44, 44)
            hb.setStyleSheet(
                f"QPushButton{{background:{fns.SRF2};border:1px solid {fns.BORDER};"
                f"border-radius:10px;}}"
                f"QPushButton:hover{{border-color:{fns.ACCENT};}}")
            lbl = QLabel(key)
            lbl.setStyleSheet(f"font-size:11px;color:{fns.MUTED};")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            col = QVBoxLayout(); col.setSpacing(4)
            col.addWidget(hb, alignment=Qt.AlignmentFlag.AlignCenter)
            col.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)
            row.addLayout(col)
        row.addStretch()
        lay.addLayout(row)

        close = QPushButton(self.tr('Close')); close.setStyleSheet(_btn_style(True))
        close.clicked.connect(dlg.accept); lay.addWidget(close)
        dlg.exec()

    def _show_gear_button(self):
        """_GearButton 호버 회전 애니메이션 미리보기."""
        dlg = QDialog(self); dlg.setWindowTitle("_GearButton Preview")
        dlg.setStyleSheet(f"QDialog{{background:{fns.SURFACE};}}")
        try: dlg.setWindowIcon(_make_app_icon())
        except Exception: pass
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(30, 24, 30, 20); lay.setSpacing(16)

        desc = QLabel("Hover to see the gear icon rotate clockwise.")
        desc.setStyleSheet(f"font-size:13px;color:{fns.MUTED};")
        desc.setWordWrap(True)
        lay.addWidget(desc)

        gb = _GearButton()
        gb.setIcon(_svg_icon('gear_line', fns.MUTED, 22))
        gb.setIconSize(QSize(22, 22))
        gb.setFixedSize(44, 44)
        gb.setStyleSheet(
            f"QPushButton{{background:{fns.SRF2};border:1px solid {fns.BORDER};"
            f"border-radius:10px;}}"
            f"QPushButton:hover{{border-color:{fns.ACCENT};}}")
        lay.addWidget(gb, alignment=Qt.AlignmentFlag.AlignCenter)

        close = QPushButton(self.tr('Close')); close.setStyleSheet(_btn_style(True))
        close.clicked.connect(dlg.accept); lay.addWidget(close)
        dlg.exec()

    def _show_scroll_hint(self):
        """_ScrollHint 사인파 + 페이드 애니메이션 미리보기."""
        dlg = QDialog(self); dlg.setWindowTitle("_ScrollHint Preview")
        dlg.setStyleSheet(f"QDialog{{background:{fns.SURFACE};}}")
        try: dlg.setWindowIcon(_make_app_icon())
        except Exception: pass
        dlg.resize(400, 280)
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(20, 16, 20, 16); lay.setSpacing(8)

        desc = QLabel("3 triangles + gradient overlay, sine wave ±3px + fade")
        desc.setStyleSheet(f"font-size:13px;color:{fns.MUTED};")
        desc.setWordWrap(True)
        lay.addWidget(desc)

        lbl_up = QLabel("▲ UP"); lbl_up.setStyleSheet(f"font-size:11px;color:{fns.MUTED};")
        lbl_up.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint_up = _ScrollHint('up')
        hint_up.setFixedHeight(36)

        lbl_dn = QLabel("▼ DOWN"); lbl_dn.setStyleSheet(f"font-size:11px;color:{fns.MUTED};")
        lbl_dn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint_dn = _ScrollHint('down')
        hint_dn.setFixedHeight(36)

        lay.addWidget(lbl_up); lay.addWidget(hint_up)
        lay.addSpacing(12)
        lay.addWidget(lbl_dn); lay.addWidget(hint_dn)
        lay.addStretch()

        close = QPushButton(self.tr('Close')); close.setStyleSheet(_btn_style(True))
        close.clicked.connect(dlg.accept); lay.addWidget(close)
        dlg.exec()

    # ── SettingsDialog ────────────────────────────────────────────────
    def _show_settings(self):
        dlg = SettingsDialog(self); dlg.exec()

    # ── Bulk Fixer 2단 프로그레스 바 (v1.0.0) ────────────────────────
    def _run_bulk_progress(self):
        """전체(8px) + 파일(5px) 2단 진행 바, 바 아래 우측 정렬 모노스페이스."""
        if self._bulk_timer and self._bulk_timer.isActive(): return
        self._bulk_pb.setVisible(True); self._bulk_total_lbl.setVisible(True)
        self._bulk_file_pb.setVisible(True); self._bulk_file_lbl.setVisible(True)
        self._bulk_pb.setValue(0); self._bulk_file_pb.setValue(0)
        self._bulk_total_val = 0; self._bulk_file_val = 0
        self._bulk_file_idx = 1
        self._bulk_total_lbl.setText("0/10    0%")
        self._bulk_file_lbl.setText("document_01.txt  0%")
        self._bulk_timer = QTimer(self)
        self._bulk_timer.timeout.connect(self._tick_bulk)
        self._bulk_timer.start(50)

    def _tick_bulk(self):
        TOTAL_FILES = 10
        self._bulk_file_val = min(self._bulk_file_val + 4, 100)
        self._bulk_file_pb.setValue(self._bulk_file_val)
        fname = f"document_{self._bulk_file_idx:02d}.txt"
        self._bulk_file_lbl.setText(f"{fname}  {self._bulk_file_val:>3d}%")

        if self._bulk_file_val >= 100:
            pct = int(self._bulk_file_idx / TOTAL_FILES * 100)
            self._bulk_pb.setValue(pct)
            self._bulk_total_lbl.setText(
                f"{self._bulk_file_idx}/{TOTAL_FILES}   {pct:>3d}%")
            self._bulk_file_idx += 1
            if self._bulk_file_idx > TOTAL_FILES:
                self._bulk_timer.stop()
                self._bulk_pb.setValue(100)
                self._bulk_total_lbl.setText(
                    f"{TOTAL_FILES}/{TOTAL_FILES}   100%")
                self._bulk_file_lbl.setText(_tr_args(self.tr('✔  Done — %1 file(s) processed'), TOTAL_FILES))
                QTimer.singleShot(2000, lambda: (
                    self._bulk_pb.setVisible(False),
                    self._bulk_total_lbl.setVisible(False),
                    self._bulk_file_pb.setVisible(False),
                    self._bulk_file_lbl.setVisible(False)))
            else:
                self._bulk_file_val = 0


win = PreviewWindow()
win.show()
sys.exit(app.exec())
