# Copyright © 2026 Hanrim
# Licensed under the MIT License.
# Free to use, modify, redistribute, and sell, provided that the copyright notice is retained.

"""File Nexus Suite — theme palette and stylesheet builder (Phase 2b, v1.1.0 modularization track).

Color tokens, theme detection helpers, the QSS stylesheet builder, and the
card drop-shadow helper extracted from FileNexusSuite.py. These items have
a PySide6 dependency (QApplication, QPalette, QColor, QGraphicsDropShadowEffect)
for system-theme detection and shadow rendering, but no dependency on
TRANSLATIONS, ConfigManager, or any other FNS-specific module.

Contents:
  - Color tokens (THEMES dict — 9 palettes: light, dark, sakura, choco, mint,
    ocean, sand, honey, lavender)
  - System-theme detection (_detect_system_theme, _resolve_theme)
  - Color-format helpers (_hex_rgba, _combo_arrow_url)
  - Stylesheet builder (make_style)
  - Card drop-shadow helper (_apply_card_shadow)

What stays in the main module:
  - _T (current theme dict, module-level global)
  - _unpack (mutates main-module globals: BG, ACCENT, TEXT, ...)
  - _accent_alpha (reads main-module global ACCENT directly; called from 11
    sites across the main module that all use the global form)
  - STYLE (module-level cached stylesheet)

Reason: _unpack and _accent_alpha rely on main-module-level global symbols
that are read directly across the main module. Moving them here would break
the global-binding chain since `from fns_theme import BG` would not refresh
when _unpack rewrites those names later. _apply_card_shadow originally read
the BORDER global the same way, but the shadow color is now passed as an
argument so the helper can live here cleanly.
"""

# ── Standard Library ─────────────────────
import sys
import base64
import subprocess

# ── PySide6 ──────────────────────────────
from PySide6.QtWidgets import QApplication, QGraphicsDropShadowEffect
from PySide6.QtGui import QColor, QPalette


# ═══════════════════════════════════════════════
# Color-format helpers
# ═══════════════════════════════════════════════
def _hex_rgba(hex_color: str, alpha: float) -> str:
    """Convert hex color → rgba() string (for templates inside make_style)."""
    r,g,b = int(hex_color[1:3],16), int(hex_color[3:5],16), int(hex_color[5:7],16)
    return f"rgba({r},{g},{b},{alpha})"


# ═══════════════════════════════════════════════
# Theme palette tokens
# ═══════════════════════════════════════════════
THEMES = {
    'light': {
        'BG':'#F9F8F6','SURFACE':'#FFFFFF','SRF2':'#F3F2EF',
        'BORDER':'#E5E3DD','ACCENT':'#CC785C','ACCENT_HOVER':'#B86A4E','ACCENT2':'#7B6FA3','ACCENT2_HOVER':'#6B5F93',
        'TEXT':'#1A1A1A','MUTED':'#8A8680','GRP_BG':'#F3F2EF',
        'BTN_HOVER':'#F3F2EF','BTN_BORDER_H':'#C9C5BF',
        'BTN_PRESSED':'#ECEAE5','DISABLED':'#C2BDB7',
        'SCROLLBAR_H':'#C2BDB7','GRIDLINE':'#ECEAE5','INPUT_H':'#C9C5BF',
    },
    'dark': {
        'BG':'#1A1A1A','SURFACE':'#242424','SRF2':'#2C2C2C',
        'BORDER':'#3D3D3D','ACCENT':'#CC785C','ACCENT_HOVER':'#B86A4E','ACCENT2':'#7B6FA3','ACCENT2_HOVER':'#6B5F93',
        'TEXT':'#EBEBEB','MUTED':'#8A8A8A','GRP_BG':'#1F1F1F',
        'BTN_HOVER':'#2C2C2C','BTN_BORDER_H':'#555555',
        'BTN_PRESSED':'#383838','DISABLED':'#555555',
        'SCROLLBAR_H':'#555555','GRIDLINE':'#333333','INPUT_H':'#555555',
    },
    'sakura': {
        'BG':'#FEF5F7','SURFACE':'#FFFFFF','SRF2':'#FDF0F3',
        'BORDER':'#F2D5DC','ACCENT':'#D4637A','ACCENT_HOVER':'#C2526A','ACCENT2':'#9B7FA8','ACCENT2_HOVER':'#8A6E97',
        'TEXT':'#2C1F26','MUTED':'#9E8490','GRP_BG':'#FDF0F3',
        'BTN_HOVER':'#FDE8ED','BTN_BORDER_H':'#E8B8C5',
        'BTN_PRESSED':'#FAE0E7','DISABLED':'#CDBABE',
        'SCROLLBAR_H':'#DFBAC3','GRIDLINE':'#F8E5EA','INPUT_H':'#E5C0CB',
    },
    'choco': {
        'BG':'#1E1916','SURFACE':'#26211D','SRF2':'#2D2720',
        'BORDER':'#3D3530','ACCENT':'#B87333','ACCENT_HOVER':'#A56628','ACCENT2':'#8B7355','ACCENT2_HOVER':'#7A6347',
        'TEXT':'#EDE8E2','MUTED':'#8A7D74','GRP_BG':'#231E1A',
        'BTN_HOVER':'#2D2720','BTN_BORDER_H':'#5C4F46',
        'BTN_PRESSED':'#352E28','DISABLED':'#5C4F46',
        'SCROLLBAR_H':'#5C4F46','GRIDLINE':'#332B26','INPUT_H':'#5C4F46',
    },
    'mint': {
        'BG':'#F4F9F1','SURFACE':'#FFFFFF','SRF2':'#EBF5EE',
        'BORDER':'#C5DFC9','ACCENT':'#5C9E70','ACCENT_HOVER':'#4D8A60','ACCENT2':'#E8A0B4','ACCENT2_HOVER':'#D88EA3',
        'TEXT':'#1C2E20','MUTED':'#7A967E','GRP_BG':'#EBF5EE',
        'BTN_HOVER':'#E3F0E6','BTN_BORDER_H':'#A8CEB0',
        'BTN_PRESSED':'#D4EAD8','DISABLED':'#AECAB4',
        'SCROLLBAR_H':'#AECAB4','GRIDLINE':'#D4EAD8','INPUT_H':'#A8CEB0',
    },
    'ocean': {
        'BG':'#EEF6FF','SURFACE':'#FFFFFF','SRF2':'#E0EFFC',
        'BORDER':'#A8CEE8','ACCENT':'#2878B8','ACCENT_HOVER':'#1E68A0','ACCENT2':'#E8A030','ACCENT2_HOVER':'#D48E24',
        'TEXT':'#0A1E30','MUTED':'#5E8AAA','GRP_BG':'#E0EFFC',
        'BTN_HOVER':'#D4E9F8','BTN_BORDER_H':'#82B8D8',
        'BTN_PRESSED':'#C0DCF2','DISABLED':'#8ABDD6',
        'SCROLLBAR_H':'#8ABDD6','GRIDLINE':'#C0DCF2','INPUT_H':'#82B8D8',
    },
    'sand': {
        'BG':'#FBF5EE','SURFACE':'#FFFFFF','SRF2':'#F5EDE0',
        'BORDER':'#E0C4A0','ACCENT':'#B86838','ACCENT_HOVER':'#A45830','ACCENT2':'#8B6914','ACCENT2_HOVER':'#7A5C10',
        'TEXT':'#281808','MUTED':'#9A7A5A','GRP_BG':'#F5EDE0',
        'BTN_HOVER':'#EEE0CC','BTN_BORDER_H':'#C8A07A',
        'BTN_PRESSED':'#E8D0B4','DISABLED':'#C0A080',
        'SCROLLBAR_H':'#C0A080','GRIDLINE':'#EAD8BE','INPUT_H':'#C8A07A',
    },
    'honey': {
        'BG':'#FDFAF0','SURFACE':'#FFFFFF','SRF2':'#FAF5DC',
        'BORDER':'#E8D880','ACCENT':'#C8A030','ACCENT_HOVER':'#B48E28','ACCENT2':'#D4874A','ACCENT2_HOVER':'#BE763C',
        'TEXT':'#2A2200','MUTED':'#8A7A40','GRP_BG':'#FAF5DC',
        'BTN_HOVER':'#F5EEC0','BTN_BORDER_H':'#D8C060',
        'BTN_PRESSED':'#EEE0A0','DISABLED':'#C8B870',
        'SCROLLBAR_H':'#C8B870','GRIDLINE':'#F0E8B0','INPUT_H':'#D8C060',
    },
    'lavender': {
        'BG':'#F7F5FF','SURFACE':'#FFFFFF','SRF2':'#EEE9FF',
        'BORDER':'#D0C4E8','ACCENT':'#6D4FC2','ACCENT_HOVER':'#5C3FAF','ACCENT2':'#A87EE0','ACCENT2_HOVER':'#9366CC',
        'TEXT':'#1E1535','MUTED':'#8876A8','GRP_BG':'#EEE9FF',
        'BTN_HOVER':'#E8E0FF','BTN_BORDER_H':'#B0A0D8',
        'BTN_PRESSED':'#DDD5F8','DISABLED':'#B8A8DC',
        'SCROLLBAR_H':'#B8A8DC','GRIDLINE':'#E5DEFF','INPUT_H':'#B0A0D8',
    },
}


# ═══════════════════════════════════════════════
# System-theme detection
# ═══════════════════════════════════════════════
def _detect_system_theme() -> str:
    """Detect OS dark mode setting and return 'light' or 'dark'."""
    if sys.platform == 'win32':
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return 'light' if val == 1 else 'dark'
        except Exception:
            pass
    elif sys.platform == 'darwin':
        try:
            result = subprocess.run(
                ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                capture_output=True, text=True, timeout=2)
            return 'dark' if 'Dark' in result.stdout else 'light'
        except Exception:
            pass
    # fallback: judge by Qt palette brightness
    bg = QApplication.instance().palette().color(QPalette.Window)
    return 'dark' if bg.lightness() < 128 else 'light'


def _resolve_theme(name: str) -> str:
    """If 'auto', replace with OS-detected result; otherwise return as-is."""
    return _detect_system_theme() if name == 'auto' else name


# ═══════════════════════════════════════════════
# Combo-box arrow SVG → data URL helper
# ═══════════════════════════════════════════════
def _combo_arrow_url(color: str) -> str:
    """Return the dropdown ▼ arrow SVG as a base64 data URL (no image file required)."""
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="10" height="6">'
           f'<path d="M0 0 L10 0 L5 6 Z" fill="{color}"/></svg>')
    b64 = base64.b64encode(svg.encode()).decode()
    return f"url(data:image/svg+xml;base64,{b64})"


# ═══════════════════════════════════════════════
# QSS stylesheet builder
# ═══════════════════════════════════════════════
def make_style(t):
    return f"""
QMainWindow, QWidget {{
    background:{t['BG']}; color:{t['TEXT']};
    font-family:"Pretendard","Segoe UI Variable","Segoe UI","Malgun Gothic","Yu Gothic UI","Microsoft YaHei UI","Microsoft JhengHei UI",sans-serif;
    font-size:13px;
}}
QGroupBox {{
    background:{t['SURFACE']}; border:1px solid {t['BORDER']};
    border-radius:10px; margin-top:22px; margin-bottom:6px; padding:12px 10px 10px 10px;
}}
QGroupBox::title {{
    subcontrol-origin:margin; left:12px; padding:0 4px;
    color:{t['ACCENT']}; font-size:11px; font-weight:700; letter-spacing:1.2px; font-family:"Pretendard","Segoe UI Variable","Segoe UI","Malgun Gothic","Yu Gothic UI","Microsoft YaHei UI","Microsoft JhengHei UI",sans-serif;
}}
QTabWidget#main_tabs::pane {{ border:none; background:{t['BG']}; }}
QTabWidget#main_tabs > QTabBar::tab {{
    background:transparent; border:none;
    border-bottom:2px solid transparent;
    padding:11px 16px 9px 16px; color:{t['MUTED']};
    font-size:14px; font-weight:600; margin-right:2px; min-width:80px; min-height:29px;
    font-family: 'Pretendard','Segoe UI Emoji','Apple Color Emoji','Noto Color Emoji','Segoe UI Variable','Segoe UI','Malgun Gothic','Yu Gothic UI','Microsoft YaHei UI',sans-serif;
}}
QTabWidget#main_tabs > QTabBar::tab:selected {{
    color:{t['ACCENT']}; border-bottom:2px solid {t['ACCENT']}; background:transparent;
}}
QTabWidget#main_tabs > QTabBar::tab:hover:!selected {{
    color:{t['TEXT']}; border-bottom:2px solid {t['BORDER']};
}}
QLabel {{ color:{t['TEXT']}; font-size:13px; }}
QLineEdit {{
    background:{t['SURFACE']}; border:1.5px solid {t['BORDER']};
    border-radius:8px; color:{t['TEXT']};
    padding:6px 12px; font-size:13px; min-height:22px; max-height:36px;
    selection-background-color:{t['ACCENT']};
}}
QLineEdit:focus {{ border:1.5px solid {t['ACCENT']}; }}
QLineEdit:hover {{ border:1.5px solid {t['INPUT_H']}; }}
QRadioButton {{ color:{t['MUTED']}; spacing:7px; }}
QRadioButton::indicator {{
    width:15px; height:15px; border-radius:8px;
    border:1.5px solid {t['INPUT_H']}; background:{t['SURFACE']};
}}
QRadioButton::indicator:hover {{ border-color:{t['ACCENT']}; }}
QRadioButton::indicator:checked {{ border-color:{t['ACCENT']}; background:{t['ACCENT']}; }}
QCheckBox {{ color:{t['MUTED']}; spacing:7px; }}
QCheckBox::indicator {{
    width:15px; height:15px; border-radius:4px;
    border:1.5px solid {t['BORDER']}; background:{t['SURFACE']};
}}
QCheckBox::indicator:hover {{ border-color:{t['ACCENT']}; }}
QCheckBox::indicator:checked {{
    border-color:{t['ACCENT']}; background:{t['ACCENT']};
}}
QPushButton {{
    background:{t['SURFACE']}; border:1.5px solid {t['BTN_BORDER_H']};
    border-radius:8px; color:{t['TEXT']};
    padding:9px 18px; font-size:13px; font-weight:600;
}}
QPushButton:hover {{ background:{t['BTN_HOVER']}; border-color:{t['BTN_BORDER_H']}; }}
QPushButton:pressed {{ background:{t['BTN_PRESSED']}; }}
QPushButton:disabled {{ background:{t['SRF2']}; border-color:{t['BORDER']}; color:{t['DISABLED']}; }}
/* File/folder add buttons — shared by Batch Renamer, Text Merger, Bulk Fixer */
QPushButton#btn_folder_add {{
    background:{t['ACCENT']}; border:none; color:white; padding:7px 16px; font-weight:600; font-size:13px;
}}
QPushButton#btn_folder_add:hover {{ background:{t['ACCENT_HOVER']}; }}
QPushButton#btn_folder_add:disabled {{ background:{_hex_rgba(t['ACCENT'], 0.4)}; color:rgba(255,255,255,0.45); border:none; }}
QPushButton#btn_file_add {{
    background:{t['ACCENT']}; border:none; color:white; padding:7px 16px; font-weight:600; font-size:13px;
}}
QPushButton#btn_file_add:hover {{ background:{t['ACCENT_HOVER']}; }}
QPushButton#btn_file_add:disabled {{ background:{_hex_rgba(t['ACCENT'], 0.4)}; color:rgba(255,255,255,0.45); border:none; }}
QPushButton#btn_preview,QPushButton#btn_fpreview {{
    background:{t['SURFACE']}; border:1.5px solid {t['ACCENT']};
    color:{t['ACCENT']}; font-weight:600; padding:9px 20px; font-size:14px;
}}
QPushButton#btn_rename {{
    background:{t['ACCENT']}; color:white; border:none;
    font-weight:700; padding:9px 20px; font-size:14px;
}}
QPushButton#btn_rename:hover {{ background:{t['ACCENT_HOVER']}; }}
QPushButton#btn_frename {{
    background:{t['ACCENT2']}; color:white; border:none;
    font-weight:700; padding:9px 20px; font-size:14px;
}}
QPushButton#btn_frename:hover {{ background:{t['ACCENT2_HOVER']}; }}
QPushButton#btn_rename:disabled,QPushButton#btn_frename:disabled {{
    background:{_hex_rgba(t['ACCENT'], 0.4)}; border:none; color:rgba(255,255,255,0.45);
}}
QPushButton#btn_preview:disabled,QPushButton#btn_fpreview:disabled {{
    background:{t['SRF2']}; border-color:{t['BORDER']}; color:{t['DISABLED']};
}}
/* Common accent button */
QPushButton#btn_primary {{
    background:{t['ACCENT']}; border:none; color:white;
    font-weight:600; padding:7px 16px; font-size:13px;
}}
QPushButton#btn_primary:hover {{ background:{t['ACCENT_HOVER']}; }}
QPushButton#btn_primary:disabled {{ background:{_hex_rgba(t['ACCENT'], 0.4)}; color:rgba(255,255,255,0.45); border:none; }}
QPushButton#btn_merge {{
    background:{t['ACCENT']}; color:white; border:none;
    font-weight:700; padding:7px 20px; font-size:13px;
}}
QPushButton#btn_merge:hover {{ background:{t['ACCENT_HOVER']}; }}
QPushButton#btn_merge:disabled {{ background:{_hex_rgba(t['ACCENT'], 0.4)}; color:rgba(255,255,255,0.45); border:none; }}
/* Undo button */
QPushButton#btn_undo {{
    background:{t['SURFACE']}; border:1.5px solid {t['BORDER']};
    color:{t['TEXT']}; border-radius:8px; font-weight:600;
}}
QPushButton#btn_undo:hover {{ background:{t['SRF2']}; border-color:{t['ACCENT']}; }}
QPushButton#btn_undo:disabled {{ background:{t['SRF2']}; color:{t['DISABLED']}; }}
/* Table/tree */
QTableWidget {{
    background:{t['SURFACE']}; border:1px solid {t['BORDER']};
    border-radius:10px; gridline-color:{t['GRIDLINE']};
    color:{t['TEXT']}; font-size:13px; outline:none;
}}
QTableWidget::item {{ padding:6px 12px; }}
QTableWidget::item:selected {{ background:{_hex_rgba(t['ACCENT'],0.12)}; color:{t['TEXT']}; }}
QTreeWidget {{
    background:{t['SURFACE']}; border:1px solid {t['BORDER']};
    border-radius:8px; color:{t['TEXT']}; font-size:13px; outline:none;
    alternate-background-color:{t['SRF2']};
}}
QTreeWidget::item {{ padding:6px 8px; }}
QTreeWidget::item:selected {{ background:{_hex_rgba(t['ACCENT'],0.12)}; color:{t['TEXT']}; }}
QHeaderView::section {{
    background:{t['SRF2']}; border:none;
    border-bottom:1px solid {t['BORDER']}; border-right:1px solid {t['BORDER']};
    color:{t['MUTED']}; font-size:12px; font-weight:600;
    letter-spacing:0.3px; padding:8px 12px;
}}
QHeaderView::section:first {{
    border-top-left-radius:7px;
}}
QHeaderView::section:last {{
    border-top-right-radius:7px; border-right:none;
}}
QScrollBar:vertical {{
    background:transparent; width:8px; border-radius:4px; margin:2px;
}}
QScrollBar::handle:vertical {{
    background:{t['BORDER']}; border-radius:4px; min-height:28px;
}}
QScrollBar::handle:vertical:hover {{ background:{t['SCROLLBAR_H']}; }}
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical {{ height:0; }}
QScrollBar::add-page:vertical,QScrollBar::sub-page:vertical {{ background:none; }}
QScrollArea {{ border:none; background:transparent; }}
QScrollArea > QWidget > QWidget {{ background:transparent; }}
QSplitter::handle {{ background:{t['BORDER']}; }}
QProgressBar {{
    background:{t['SRF2']}; border:none; border-radius:4px;
    text-align:center; color:{t['TEXT']};
}}
QProgressBar::chunk {{ background:{t['ACCENT']}; border-radius:3px; }}
QComboBox {{
    background:{t['SURFACE']}; border:1.5px solid {t['BORDER']};
    border-radius:8px; color:{t['TEXT']};
    padding:7px 32px 7px 12px; font-size:13px; min-height:30px;
}}
QComboBox:focus {{ border-color:{t['ACCENT']}; }}
QComboBox:hover {{ border-color:{t['INPUT_H']}; }}
QComboBox::drop-down {{
    subcontrol-origin:padding; subcontrol-position:right center;
    width:32px; border:none; border-left:1px solid {t['BORDER']};
    border-top-right-radius:8px; border-bottom-right-radius:8px;
    background:{t['SRF2']};
}}
QComboBox::down-arrow {{ image:{_combo_arrow_url(t['MUTED'])}; width:10px; height:6px; }}
QComboBox:hover::down-arrow {{ image:{_combo_arrow_url(t['TEXT'])}; }}
QComboBox:focus::down-arrow {{ image:{_combo_arrow_url(t['ACCENT'])}; }}
QComboBox QAbstractItemView {{
    background:{t['SURFACE']}; border:1.5px solid {t['BORDER']};
    border-radius:10px; outline:none; padding:6px;
}}
QComboBox QAbstractItemView::item {{
    padding:5px 14px; min-height:22px;
}}
QMenu {{
    background:{t['SURFACE']}; border:1px solid {t['BORDER']};
    border-radius:8px; color:{t['TEXT']}; font-size:13px; padding:4px;
}}
QMenu::item {{
    padding:8px 16px; border-radius:5px;
}}
QMenu::item:selected {{
    background:{_hex_rgba(t['ACCENT'],0.12)}; color:{t['TEXT']};
}}
QMenu::item:disabled {{
    color:{t['DISABLED']};
}}
QMenu::separator {{
    height:1px; background:{t['BORDER']}; margin:4px 8px;
}}
QStatusBar {{ background:{t['SRF2']}; border-top:1px solid {t['BORDER']}; color:{t['MUTED']}; }}
QTextEdit {{
    background:{t['SURFACE']}; border:1px solid {t['BORDER']};
    border-radius:8px; color:{t['TEXT']}; font-size:13px; padding:7px;
}}
QPlainTextEdit {{
    background:{t['SURFACE']}; border:1px solid {t['BORDER']};
    border-radius:8px; color:{t['TEXT']}; font-size:13px; padding:7px;
}}
QToolTip {{
    background:{t['TEXT']}; color:{t['SURFACE']};
    border:none; border-radius:6px; padding:5px 9px; font-size:12px;
}}
/* named widgets */
QFrame#tab_sep {{
    background:{t['BORDER']}; max-height:1px; border:none;
}}
QLabel#hint_box {{
    background:{t['SRF2']}; border:1px solid {t['BORDER']};
    border-radius:8px; padding:12px; color:{t['MUTED']}; line-height:1.8;
}}
QLabel#ex_box {{
    background:{t['SRF2']}; border:1px solid {t['BORDER']};
    border-radius:6px; padding:10px 14px; font-size:13px;
}}
QLabel#fmt_box {{
    background:{t['SRF2']}; border:1px solid {t['BORDER']};
    border-radius:8px; padding:14px;
}}
QLabel#count_lbl {{ color:{t['MUTED']}; font-size:12px; background:transparent; }}
QLabel#field_lbl {{ color:{t['MUTED']}; font-size:13px; background:transparent; }}
QLabel#grp_title_lbl {{ color:{t['MUTED']}; font-size:11px; font-weight:700; letter-spacing:1.2px; background:transparent; }}
QTextEdit#dbg_edit {{
    background:{t['SURFACE']}; border:1px solid {t['BORDER']};
    color:{t['MUTED']}; font-family:'D2Coding','Malgun Gothic','맑은 고딕','Consolas','Menlo',monospace;
    font-size:12px; padding:7px; border-radius:8px;
}}
QLabel#drop_hint {{
    color:{t['MUTED']}; border:1.5px dashed {t['BORDER']};
    border-radius:8px; padding:14px; background:{t['SURFACE']};
}}
QPushButton#btn_settings {{
    background:transparent; border:1px solid {t['BORDER']};
    border-radius:8px; color:{t['MUTED']}; font-size:16px; padding:0;
    font-family:"Segoe UI Symbol","Segoe UI Emoji","Apple Color Emoji","Noto Color Emoji",sans-serif;
}}
QPushButton#btn_settings:hover {{
    background:{t['SRF2']}; color:{t['TEXT']}; border-color:{t['ACCENT']};
}}
QPushButton#btn_help {{
    background:transparent; border:1px solid {t['BORDER']};
    border-radius:8px; color:{t['MUTED']}; font-size:16px; padding:0;
    font-family:"Segoe UI Symbol","Segoe UI Emoji","Apple Color Emoji","Noto Color Emoji",sans-serif;
}}
QPushButton#btn_help:hover {{
    background:{t['SRF2']}; color:{t['TEXT']}; border-color:{t['ACCENT']};
}}
QPushButton#btn_dbg_clear {{
    background:{t['SRF2']}; border:1px solid {t['BORDER']};
    color:{t['MUTED']}; padding:3px 8px; font-size:12px; border-radius:6px;
}}
QPushButton#btn_dbg_clear:hover {{ background:{t['BORDER']}; }}
"""


# ═══════════════════════════════════════════════
# Card drop-shadow helper
# ═══════════════════════════════════════════════
def _apply_card_shadow(widget, border_color):
    """Apply a subtle drop shadow to a card-like widget (QGroupBox, etc.).

    v1.1.0 (다-1) — Strengthens visual separation between sidebar cards
    without competing with the existing border. Tone-matched with the FNS
    palette: shadow color derived from BORDER with low opacity, so it
    naturally adapts to light/dark themes.

    - Blur radius: 18 px (subtle but visible)
    - Y offset: 3 px (slight elevation, no horizontal displacement)
    - Color: BORDER with alpha 0.5 (matches existing tone, doesn't compete)

    Phase 2b: border_color (the BORDER global at the call site) is passed
    in as an argument rather than read from a module global, so this
    helper can live in fns_theme.py without circular-import gymnastics.

    Idempotent: replaces any existing graphics effect on the widget.
    """
    eff = QGraphicsDropShadowEffect(widget)
    eff.setBlurRadius(18)
    eff.setOffset(0, 3)
    shadow_color = QColor(border_color)
    shadow_color.setAlphaF(0.5)
    eff.setColor(shadow_color)
    widget.setGraphicsEffect(eff)
