# Copyright © 2026 Hanrim
# Licensed under the MIT License.
# Free to use, modify, redistribute, and sell, provided that the copyright notice is retained.
#
# Icons: SVG icon set (line/filled styles) created by Microsoft Copilot.
# No external icon libraries used. No additional attribution required.

"""
File Nexus Suite  —  Integrated File Management Tool
Tab 1: Text Merger     (Merge text/Word/PDF/Excel files)
Tab 2: Text Converter  (EPUB ↔ TXT conversion)
Tab 3: Tag Editor      (Bulk edit filename [tags])
Tab 4: Batch Renamer   (Bulk rename folders & files)
Tab 5: Text Fixer      (Fix text line breaks)
Tab 6: Bulk Fixer      (Bulk fix line breaks in text files)

Theme: File Nexus Suite  Palette
Languages: 한국어 / English / 日本語 / 中文(简体/繁體)
"""

# ── Standard Library ────────────────────────────
import sys, os, re, zipfile, uuid, json, base64, subprocess, atexit, html
from pathlib import Path
from datetime import datetime

# ── Optional Libraries ─────────────────────────

try:
    import chardet as _chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False

try:
    import docx as _docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import openpyxl
    XLSX_AVAILABLE = True
except ImportError:
    XLSX_AVAILABLE = False

try:
    import hwpx as _hwpx
    HWPX_AVAILABLE = True
except ImportError:
    HWPX_AVAILABLE = False

# ── PySide6 ────────────────────────────────────
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QCheckBox, QRadioButton,
    QButtonGroup, QTextEdit, QPlainTextEdit, QScrollArea, QFrame, QFileDialog,
    QDialog, QProgressBar, QSplitter, QTabWidget,
    QAbstractItemView, QStackedWidget,
    QComboBox, QTreeWidget, QTreeWidgetItem, QHeaderView,
    QTableWidget, QTableWidgetItem, QGroupBox, QGridLayout,
    QSpinBox, QToolButton, QMenu,
)
from PySide6.QtCore import Qt, Signal, QThread, QSize, QRect, QRectF, QPointF, QTimer, QBuffer, QByteArray, QIODevice
from PySide6.QtGui import QColor, QPalette, QCursor, QPainter, QPen, QBrush, QFont, QKeySequence, QLinearGradient, QPolygonF, QIcon, QPixmap, QPainterPath, QImageReader, QShortcut, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QStyledItemDelegate, QStyle, QProxyStyle

# ═══════════════════════════════════════════════
# App Version
# ═══════════════════════════════════════════════
APP_VERSION = "1.0.10"

# ═══════════════════════════════════════════════
# Sleep Prevention Utility (Windows only, no-op on other OSes)
# ═══════════════════════════════════════════════
def _prevent_sleep() -> None:
    """Prevent sleep/display-off during operation — ES_SYSTEM_REQUIRED | ES_CONTINUOUS."""
    try:
        import ctypes
        ctypes.windll.kernel32.SetThreadExecutionState(
            0x80000000 | 0x00000001  # ES_CONTINUOUS | ES_SYSTEM_REQUIRED
        )
    except Exception:
        pass  # ignore on non-Windows environments

def _allow_sleep() -> None:
    """Release sleep prevention after operation — passing ES_CONTINUOUS alone restores default."""
    try:
        import ctypes
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)  # ES_CONTINUOUS
    except Exception:
        pass

# ═══════════════════════════════════════════════
# Theme System
# ═══════════════════════════════════════════════
# Cross-platform color emoji font priority
_EMOJI_FONT_FAMILY = (
    "'Segoe UI Emoji','Apple Color Emoji','Noto Color Emoji',"
    "'Noto Emoji','EmojiOne Color','Twemoji Mozilla',sans-serif"
)


def _emoji_pix(char: str, pt: int = 16, size: int = 24) -> QPixmap:
    """Render emoji as QPixmap — for tab QIcon (cross-OS consistency)."""
    pix = QPixmap(size, size); pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix); p.setRenderHint(QPainter.TextAntialiasing)
    f = QFont(); f.setPointSize(pt)
    try: f.setFamilies(["Segoe UI Emoji","Apple Color Emoji","Noto Color Emoji","Noto Emoji"])
    except AttributeError: f.setFamily("Segoe UI Emoji")   # Qt < 5.13 fallback
    p.setFont(f)
    p.drawText(QRect(0, 0, size, size), Qt.AlignmentFlag.AlignCenter, char)
    p.end(); return pix


# ── SVG Icon System ────────────────────────────────────────────────────────
try:
    from PySide6.QtSvg import QSvgRenderer as _QSvgRenderer
    _HAS_SVG = True
except ImportError:
    _HAS_SVG = False

# Filled SVG path data for buttons (B) (based on 24×24 viewBox)
# primary button: 'white' icon / secondary button: ACCENT icon
_SVG_PATHS: dict[str, str] = {
    'document':    'M6 2h9l5 5v15H6V2zm8 0v5h5',
    'folder':      'M10 4l2 2h8a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1h6z',
    'folder_open': 'M3 6h7l2 2h9v12H3V6z',
    'tag':         'M3 12l9-9h9v9l-9 9-9-9zM15 6a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3z',
    'refresh':     'M12 4V1L8 5l4 4V6c3.3 0 6 2.7 6 6 0 1.1-.3 2.1-.8 3l1.5 1.5C19.5 15 20 13.6 20 12c0-4.4-3.6-8-8-8zm-6.7.7L3.8 6.2C2.5 7.9 2 9.4 2 12c0 4.4 3.6 8 8 8v3l4-4-4-4v3c-3.3 0-6-2.7-6-6 0-1.1.3-2.1.8-3l-1.5-1.3z',
    'wrench':      'M14 2a6 6 0 0 0-6 6c0 1 .2 2 .6 2.9L2 18l4 4 6.1-6.6c.9.4 1.9.6 2.9.6a6 6 0 0 0 0-12z',
    'magnifier':   'M10 2a8 8 0 0 1 6.3 12.9l5.4 5.4-1.4 1.4-5.4-5.4A8 8 0 1 1 10 2zm0 2a6 6 0 1 0 0 12 6 6 0 0 0 0-12z',
    'save':        'M17 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14V7l-2-4zM12 19a2 2 0 1 1 0-4 2 2 0 0 1 0 4zm1-10H7V5h6v4z',
    'trash':       'M3 6h18v2H3V6zm2 3h14l-1.5 12h-11L5 9zm5 2v8h2v-8h-2zm4 0v8h2v-8h-2z',
    'broom':       'M2 20h20v2H2v-2zm10-18l6 6-8 8-6-6 8-8z',
    'question':    'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 15h-1v-2h2v2h-1zm1-4h-2c0-2 3-2 3-4a2 2 0 0 0-4 0H8a4 4 0 0 1 8 0c0 2-3 2-3 4z',
    'list':        'M4 6h2v2H4V6zm0 5h2v2H4v-2zm0 5h2v2H4v-2zM8 7h12v2H8V7zm0 5h12v2H8v-2zm0 5h12v2H8v-2z',
    'clipboard':   'M16 2H8a2 2 0 0 0-2 2v2H4v16h16V6h-2V4a2 2 0 0 0-2-2zm0 4H8V4h8v2z',
    'arrow_up':    'M12 4l-8 8h5v8h6v-8h5l-8-8z',
    'arrow_down':  'M12 20l8-8h-5V4h-6v8H4l8 8z',
    'check':       'M20 6L9 17l-5-5 1.5-1.5L9 14l9.5-9.5z',
    'info':        'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z',
}

# Line (outline) style SVG — for tabs (stage A) / headers (stage C) / settings navigation
# stroke-based or filled composite structure, with {color} placeholder for color substitution
_SVG_LINE_ICONS: dict[str, str] = {
    'document_line': (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        ' stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M6 2h9l5 5v15H6z"/><path d="M14 2v5h5"/></svg>'
    ),
    'folder_open_line': (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        ' stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M3 6h7l2 2h9v12H3z"/></svg>'
    ),
    'tag_line': (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        ' stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M3 12l9-9h9v9l-9 9z"/>'
        '<circle cx="15" cy="9" r="1.5" fill="{color}" stroke="none"/></svg>'
    ),
    'folder_line': (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        ' stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M3 6h7l2 2h9v10H3z"/></svg>'
    ),
    'wrench_line': (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        ' stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M14 2a6 6 0 0 0-6 6c0 1 .2 2 .6 2.9L2 18l4 4 6.1-6.6c.9.4 1.9.6 2.9.6a6 6 0 0 0 0-12z"/></svg>'
    ),
    'question_line': (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        ' stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 14a4 4 0 1 0-4-4"/>'
        '<circle cx="12" cy="18.5" r="0.8" fill="{color}" stroke="none"/></svg>'
    ),
    'gear_line': (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        ' stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="12" cy="12" r="3"/>'
        '<path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06'
        'a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09'
        'a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06'
        'a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09'
        'a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06'
        'a1.65 1.65 0 0 0 1.82.33h.09a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09'
        'a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06'
        'a1.65 1.65 0 0 0-.33 1.82v.09a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09'
        'a1.65 1.65 0 0 0-1.51 1z"/></svg>'
    ),
    'bell_line': (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        ' stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/>'
        '<path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>'
    ),
    'info_line': (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        ' stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="12" cy="12" r="10"/>'
        '<line x1="12" y1="16" x2="12" y2="12"/>'
        '<circle cx="12" cy="8" r="0.8" fill="{color}" stroke="none"/></svg>'
    ),
    'broom_line': (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        ' stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M19 5L5 19"/>'
        '<path d="M5 19h6m-6 0v-6"/>'
        '</svg>'
    ),
    'theme_line': (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}">'
        '<path d="M12 2a10 10 0 0 0 0 20h1a3 3 0 0 0 0-6h-1a4 4 0 0 1 0-8h1a3 3 0 0 0 0-6h-1z"/>'
        '<circle cx="6.5" cy="11.5" r="1.5"/>'
        '<circle cx="9.5" cy="7.5" r="1.5"/>'
        '<circle cx="14.5" cy="7.5" r="1.5"/>'
        '<circle cx="17.5" cy="11.5" r="1.5"/>'
        '</svg>'
    ),
    'globe_line': (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        ' stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="12" cy="12" r="10"/>'
        '<path d="M2 12h20M12 2a15.3 15.3 0 0 0 0 20M12 2a15.3 15.3 0 0 1 0 20"/>'
        '</svg>'
    ),
    'keyboard_line': (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        ' stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="2" y="6" width="20" height="12" rx="2"/>'
        '<path d="M6 10h.01M10 10h.01M14 10h.01M18 10h.01M6 14h12"/>'
        '</svg>'
    ),
    'license_line': (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        ' stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M6 2h9l5 5v15H6z"/>'
        '<path d="M14 2v5h5"/>'
        '<line x1="8" y1="13" x2="16" y2="13"/>'
        '<line x1="8" y1="17" x2="16" y2="17"/>'
        '</svg>'
    ),
}


def _svg_icon(key: str, color: str, size: int = 18) -> 'QIcon':
    """Create QIcon from SVG — supports both filled (button) and line (tab/header) styles.
    Rendered at 2x resolution for sharpness.
    'white' icons automatically add a MUTED-color pixmap for disabled state.
    Returns empty QIcon when PySide6.QtSvg is not installed (graceful fallback).
    """
    if not _HAS_SVG:
        return QIcon()
    try:
        def _render(col: str) -> 'QPixmap':
            if key in _SVG_LINE_ICONS:
                svg_bytes = _SVG_LINE_ICONS[key].replace('{color}', col).encode('utf-8')
            else:
                path_d = _SVG_PATHS.get(key, '')
                if not path_d:
                    return QPixmap()
                svg_bytes = (
                    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
                    f'<path fill="{col}" d="{path_d}"/>'
                    f'</svg>'
                ).encode('utf-8')
            renderer = _QSvgRenderer(svg_bytes)
            scale = 2
            pix = QPixmap(size * scale, size * scale)
            pix.fill(Qt.GlobalColor.transparent)
            p = QPainter(pix)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            renderer.render(p)
            p.end()
            pix.setDevicePixelRatio(scale)
            return pix

        icon = QIcon()
        pix = _render(color)
        if pix.isNull():
            return QIcon()
        icon.addPixmap(pix, QIcon.Mode.Normal)
        # 'white' icons get an additional MUTED-color pixmap for disabled state
        # → keeps icons visible on disabled buttons with light backgrounds
        if color == 'white':
            dis_pix = _render(MUTED)
            if not dis_pix.isNull():
                icon.addPixmap(dis_pix, QIcon.Mode.Disabled)
        return icon
    except Exception:
        return QIcon()


def _svg_icon_dual(key: str, normal_color: str, active_color: str, size: int = 18) -> 'QIcon':
    """Dual-mode SVG QIcon with two colors: Normal / Active (hover).
    For buttons like btn_preview where normal and hover background colors differ.
    """
    icon = _svg_icon(key, normal_color, size)
    if not _HAS_SVG or icon.isNull():
        return icon
    try:
        def _render(col: str) -> 'QPixmap':
            if key in _SVG_LINE_ICONS:
                svg_bytes = _SVG_LINE_ICONS[key].replace('{color}', col).encode('utf-8')
            else:
                path_d = _SVG_PATHS.get(key, '')
                if not path_d:
                    return QPixmap()
                svg_bytes = (
                    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
                    f'<path fill="{col}" d="{path_d}"/>'
                    f'</svg>'
                ).encode('utf-8')
            renderer = _QSvgRenderer(svg_bytes)
            scale = 2
            pix = QPixmap(size * scale, size * scale)
            pix.fill(Qt.GlobalColor.transparent)
            p = QPainter(pix)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            renderer.render(p)
            p.end()
            pix.setDevicePixelRatio(scale)
            return pix
        active_pix = _render(active_color)
        if not active_pix.isNull():
            icon.addPixmap(active_pix, QIcon.Mode.Active)
        return icon
    except Exception:
        return icon


def _svg_html_img(key: str, color: str, size: int = 32) -> str:
    """Convert SVG icon to base64 PNG and return as an HTML <img> tag — for Qt HTML renderer."""
    try:
        icon = _svg_icon(key, color, size)
        pix = icon.pixmap(QSize(size * 2, size * 2))
        ba = QByteArray()
        buf = QBuffer(ba)
        buf.open(QIODevice.WriteOnly)
        pix.save(buf, 'PNG')
        b64 = ba.toBase64().data().decode('ascii')
        return (f"<img src='data:image/png;base64,{b64}' "
                f"width='{size}' height='{size}' style='vertical-align:middle;'/>")
    except Exception:
        return ""


def _hex_rgba(hex_color: str, alpha: float) -> str:
    """Convert hex color → rgba() string (for templates inside make_style)."""
    r,g,b = int(hex_color[1:3],16), int(hex_color[3:5],16), int(hex_color[5:7],16)
    return f"rgba({r},{g},{b},{alpha})"


def _accent_alpha(alpha: float = 0.12) -> str:
    """rgba string of the current theme's ACCENT color — for inline setStyleSheet calls."""
    c = QColor(ACCENT)
    return f"rgba({c.red()},{c.green()},{c.blue()},{alpha})"


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
_T = THEMES['light']


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


def _unpack(t=None):
    global BG,SURFACE,SRF2,BORDER,ACCENT,ACCENT_HOVER,ACCENT2,ACCENT2_HOVER
    global TEXT,MUTED,GRP_BG,BTN_HOVER,BTN_BORDER_H,BTN_PRESSED,DISABLED,INPUT_H
    d = t or _T
    BG=d['BG']; SURFACE=d['SURFACE']; SRF2=d['SRF2']; BORDER=d['BORDER']
    ACCENT=d['ACCENT']; ACCENT_HOVER=d['ACCENT_HOVER']
    ACCENT2=d['ACCENT2']; ACCENT2_HOVER=d['ACCENT2_HOVER']
    TEXT=d['TEXT']; MUTED=d['MUTED']; GRP_BG=d['GRP_BG']
    BTN_HOVER=d['BTN_HOVER']; BTN_BORDER_H=d['BTN_BORDER_H']
    BTN_PRESSED=d['BTN_PRESSED']; DISABLED=d['DISABLED']; INPUT_H=d['INPUT_H']

_unpack()

def _combo_arrow_url(color: str) -> str:
    """Return the dropdown ▼ arrow SVG as a base64 data URL (no image file required)."""
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="10" height="6">'
           f'<path d="M0 0 L10 0 L5 6 Z" fill="{color}"/></svg>')
    b64 = base64.b64encode(svg.encode()).decode()
    return f"url(data:image/svg+xml;base64,{b64})"

def make_style(t):
    return f"""
QMainWindow, QWidget {{
    background:{t['BG']}; color:{t['TEXT']};
    font-family:"Pretendard","Segoe UI Variable","Segoe UI","Malgun Gothic","Yu Gothic UI","Microsoft YaHei UI","Microsoft JhengHei UI",sans-serif;
    font-size:13px;
}}
QGroupBox {{
    background:{t['SURFACE']}; border:1px solid {t['BORDER']};
    border-radius:10px; margin-top:22px; padding:10px 8px 8px 8px;
}}
QGroupBox::title {{
    subcontrol-origin:margin; left:12px; padding:0 4px;
    color:{t['MUTED']}; font-size:11px; font-weight:700; letter-spacing:1.2px; font-family:"Pretendard","Segoe UI Variable","Segoe UI","Malgun Gothic","Yu Gothic UI","Microsoft YaHei UI","Microsoft JhengHei UI",sans-serif;
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

STYLE = make_style(_T)


# ═══════════════════════════════════════════════
# Settings save/restore (config.json)
# ═══════════════════════════════════════════════
def _app_dir() -> Path:
    """Return the path of the executable (.exe) or script — also covers PyInstaller builds."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent   # built exe location
    return Path(__file__).parent             # dev-mode script location

_CONFIG_PATH = _app_dir() / "FileNexusSuite.json"
_OUTPUT_DIR  = _app_dir() / "Output"   # default output folder — shared by Text Converter, Bulk Fixer
try:
    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    pass  # ignore in environments without write permission

class ConfigManager:
    """Save/restore app settings to/from a JSON file."""
    def __init__(self):
        self._data: dict = {}

    def load(self) -> dict:
        try:
            if _CONFIG_PATH.exists():
                self._data = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            self._data = {}
        return self._data

    def save(self, data: dict):
        try:
            _CONFIG_PATH.write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        except Exception as e:
            _glog(f"[ConfigManager] save error: {e}")

    def get(self, key, default=None):
        return self._data.get(key, default)

    def update(self, key, value):
        self._data[key] = value

_CFG = ConfigManager()

# ── Global debug log (set by AppSuite, called directly from panels) ──
_g_log_fn = None
_session_log_fp = None  # session log file handle


def _t(key: str, **kwargs) -> str:
    """Return the translated string for the current language. zh_cn falls back to zh_tw first, then to Korean."""
    lang = _current_lang
    s = (TRANSLATIONS.get(lang, TRANSLATIONS['ko']).get(key)
         or (TRANSLATIONS['zh_tw'].get(key) if lang == 'zh_cn' else None)
         or TRANSLATIONS['ko'].get(key, key))
    return s.format(**kwargs) if kwargs else s


def _all_translations_of(key: str) -> set:
    """Return the set of all-language values for a translation key.
    Used for status label comparison inside retranslate() — auto-reflects when translations are added or changed."""
    return {v.get(key, '') for v in TRANSLATIONS.values()
            if isinstance(v, dict) and v.get(key)}


_THEME_NAME_KEY = {
    'light':'theme_light','auto':'theme_auto','dark':'theme_dark',
    'choco':'theme_choco','ocean':'theme_ocean','mint':'theme_mint',
    'sand':'theme_sand','honey':'theme_honey',
    'sakura':'theme_sakura','lavender':'theme_lavender',
}

def _theme_label(theme_name: str) -> str:
    """Return the name in the current language for a theme key. Uses _t() to guarantee language timing."""
    key = _THEME_NAME_KEY.get(theme_name, '')
    return _t(key) if key else theme_name

def _glog(msg: str):
    """Print log to the AppSuite debug window from any panel, and also write it to the file."""
    if _g_log_fn:
        _g_log_fn(msg)
    # also write to the session log file
    if _session_log_fp:
        try:
            ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            _session_log_fp.write(f"[{ts}] {msg}\n")
            _session_log_fp.flush()
        except Exception:
            pass

# ── Shortcut definitions (id → label, default) ──
SHORTCUT_DEFS = {
    'tab_1': {'default': 'Ctrl+1'},
    'tab_2': {'default': 'Ctrl+2'},
    'tab_3': {'default': 'Ctrl+3'},
    'tab_4': {'default': 'Ctrl+4'},
    'tab_5': {'default': 'Ctrl+5'},
    'tab_6': {'default': 'Ctrl+6'},
}


# ── Supported languages definition ─────────────────
TRANSLATIONS = {'ko': {'app_subtitle': '통합 파일 작업 도구',
        'debug_log': 'Debug Log',
        'btn_clear': '지우기',
        'btn_add_file': '파일 추가',
        'btn_add_folder': '폴더 추가',
        'btn_del_sel': '선택 삭제',
        'btn_del_all': '전체 삭제',
        'btn_up': '위로',
        'btn_down': '아래로',
        'btn_close': '닫기',
        'btn_apply': '적용',
        'btn_reset': '기본값',
        'btn_reset_all': '모든 단축키 기본값 복원',
        'merge_save_settings': '// 저장 설정',
        'merge_save_enc': '저장 인코딩:',
        'merge_save_path': '저장 경로:',
        'merge_path_none': '저장 경로가 지정되지 않았습니다',
        'merge_path_pick': '경로 지정',
        'merge_path_reset': '초기화',
        'merge_sep': '파일 구분선 삽입',
        'merge_btn': '병합 및 저장',
        'merge_status_ready': '준비',
        'btn_undo': '실행 취소',
        'btn_abort': '중단',
        'merge_sel_none': '선택된 파일: 없음',
        'merge_open_explorer': '탐색기에서 열기',
        'conv_sub_txt2epub': 'TXT → EPUB',
        'conv_sub_epub2txt': 'EPUB → TXT',
        'conv_out_folder': '// 출력 폴더',
        'conv_out_ph': '비워두면 입력 파일 위치에 저장',
        'conv_btn_pick': '폴더 지정',
        'conv_btn_start': '변환 시작',
        'conv_btn_converting': '⏳ 변환 중…',
        'conv_opt_epub2txt': '⚙  변환 옵션  (EPUB → TXT)',
        'conv_chk_sep': '챕터 구분선 추가',
        'conv_chk_title': '챕터 제목 포함',
        'conv_chk_trim': '연속 빈 줄 정리',
        'conv_save_enc': '저장 인코딩:',
        'tc_title_placeholder': '제목 없음',
        'tc_author_placeholder': '작자 미상',
        'conv_meta': '📖  책 정보  (TXT → EPUB)',
        'conv_book_title': '책 제목',
        'conv_author': '저자',
        'conv_lang': '책 언어:',
        'conv_chapter_mode': '챕터 구분 방식:',
        'conv_ch0': '구분선 기준 (===, ---, ★★★ 등)',
        'conv_ch1': '빈 줄 3개 이상 기준',
        'conv_ch2': '전체를 한 챕터로',
        'conv_status_start': '파일을 추가하고 변환을 시작하세요.',
        'conv_file_list': '// 파일 목록',
        'tag_sub_remove': '태그 제거',
        'tag_sub_add': '태그 추가',
        'tag_sub_depad': '앞자리 0 제거',
        'tag_col_filename': '파일명',
        'tag_col_path': '경로',
        'tag_filter': '// 필터 설정',
        'tag_ext_label': '대상 확장자',
        'tag_ext_hint': '쉼표로 구분',
        'tag_cb_recursive': '하위 폴더 포함',
        'tag_cb_allext': '모든 확장자 대상',
        'tag_rm_pos': '제거 위치',
        'tag_rm_tag': '제거 태그',
        'tag_rm_tag_ph': '비워두면 모든 [태그] 제거',
        'tag_rm_front': '앞쪽만',
        'tag_rm_back': '뒤쪽만',
        'tag_rm_both': '앞/뒤 모두',
        'tag_add_fmt': '태그 형식',
        'tag_add_fmt_hint': '예:  [태그]  @태그  #태그',
        'tag_add_val': '추가할 태그',
        'tag_add_val_ph': '쉼표로 여러 개 입력',
        'tag_add_pos': '태그 위치',
        'tag_add_front': '파일명 앞',
        'tag_add_back': '파일명 뒤',
        'tag_add_skip': '이미 태그 있으면 건너뜀',
        'tag_add_replace': '기존 태그를 새 태그로 교체',
        'tag_add_space_after': '태그 뒤 공백',
        'tag_add_space_before': '태그 앞 공백',
        'tag_col_folder': '폴더',
        'tag_col_orig': '원본 파일명',
        'tag_col_new': '변경 후 파일명',
        'tag_btn_apply_rm': '태그 제거 적용',
        'tag_btn_apply_add': '태그 추가 적용',
        'tag_btn_apply_depad': '앞자리 0 제거 적용',
        'tag_status_start': '파일 추가 후 미리보기를 클릭하세요.',
        'tag_count_total':  '총 {n}개',
        'tag_status_found': '{n}개 파일의 태그를 제거할 수 있습니다.',
        'tag_status_found_add': '{n}개 파일에 태그를 추가할 수 있습니다.',
        'tag_status_found_depad': '{n}개 파일의 앞자리 0을 제거할 수 있습니다.',
        'tag_no_change':    '변경할 파일이 없습니다.',
        'tag_skip_count':   '{n}개 건너뜀',
        'tag_apply_confirm': '총 {n}개 파일 이름을 변경합니다.\n계속하시겠습니까?',
        'tag_apply_done':   '{n}개 파일 {label} 완료.',
        'batch_sub_folder': '📁  폴더 이름 변경',
        'batch_sub_file': '📄  파일 이름 변경',
        'batch_btn_folder_pick': '폴더 선택',
        'batch_btn_file_pick': '폴더 선택',
        'batch_col_folder': '폴더 이름',
        'batch_col_arrow': '▶',
        'batch_col_new': '바뀔 이름',
        'batch_col_file': '원래 파일명',
        'batch_col_file_new': '바뀔 파일명',
        'batch_opt_smart': '스마트 추출',
        'batch_opt_seq': '순차 번호',
        'batch_smart_pfx': '// 접두사 / 접미사',
        'batch_smart_prefix': '접두사',
        'batch_smart_suffix': '접미사',
        'batch_smart_common': '// 공통 접두어 처리',
        'batch_smart_auto': '자동 감지',
        'batch_smart_manual': '직접 지정',
        'batch_smart_none': '제거 안 함',
        'batch_smart_manual_ph': '제거할 접두어',
        'batch_seq_reset': '// 번호 리셋',
        'batch_seq_global': '전체 연속',
        'batch_seq_pergroup': '그룹마다 리셋',
        'batch_seq_start': '// 시작 번호',
        'batch_seq_from0': '00부터',
        'batch_seq_from1': '01부터',
        'batch_seq_digits': '// 자릿수',
        'batch_seq_auto': '자동 (권장)',
        'batch_seq_2d': '2자리 고정',
        'batch_seq_3d': '3자리 고정',
        'batch_seq_4d': '4자리 고정',
        'batch_seq_pfx_lbl': '// 접두사 / 접미사',
        'batch_seq_name': '// 이름 보존',
        'batch_seq_numonly': '숫자만',
        'batch_seq_keep': '숫자 + 원래이름',
        'batch_seq_sep': '구분자',
        'batch_file_pfx': '// 접두사',
        'batch_file_pfx_folder': '폴더 이름 사용 (권장)',
        'batch_file_pfx_custom': '직접 입력',
        'batch_file_pfx_ph': '모든 폴더에 동일하게 적용',
        'batch_file_sep_start': '// 구분자 / 시작 번호',
        'batch_file_sep': '구분자',
        'batch_file_from0': '0부터',
        'batch_file_from1': '1부터',
        'batch_file_digits': '// 번호 자릿수',
        'batch_file_auto': '자동 (권장)',
        'batch_file_nopad': '없음 (1,2…)',
        'batch_file_2d': '최소 2자리',
        'batch_file_3d': '최소 3자리',
        'batch_file_filter': '// 파일 필터',
        'batch_file_all': '모든 파일',
        'batch_file_ext': '특정 확장자만',
        'batch_usage_title': '사용법',
        'batch_hint_folder': '<b>사용법</b><br>① 상위 폴더를 드래그하거나 버튼으로 선택<br>② 변환 방식 탭 선택<br>③ <b>미리보기</b>로 결과 확인<br>④ <b>이름 '
                             '변경 실행</b><br><br>📌 상위 폴더는 <b>변경 안 됨</b><br>📌 하위 폴더 이름만 변경됩니다',
        'batch_hint_file': '📌 <b>폴더 이름</b>이 접두사로 사용됨<br>📌 파일은 이름 순 정렬 후 번호 부여<br>📌 원본 확장자는 유지됩니다<br>📌 숨김 파일(.*)은 자동 '
                           '제외됩니다',
        'settings_title': '설정',
        'settings_nav_theme': '테마',
        'settings_nav_shortcuts': '단축키',
        'settings_nav_language': '일반 설정',
        'settings_theme_title': '색상 모드',
        'settings_theme_hint': '더블클릭하면 바로 적용됩니다.',
        'settings_output_dir': '출력 폴더',
        'settings_sc_title': '단축키 설정',
        'settings_sc_desc': '단축키 버튼을 클릭한 뒤 원하는 키를 누르세요.  ESC 로 취소합니다.',
        'settings_sc_action': '동작',
        'settings_sc_key': '단축키',
        'settings_sc_note': '💡  단축키는 적용 버튼을 누르면 즉시 반영됩니다.',
        'settings_lang_title': '언어 설정',
        'settings_lang_desc': '앱 UI 언어를 선택합니다. 적용 버튼을 누르면 반영됩니다.',
        'settings_applied': '✅  설정이 적용되었습니다.',
        'dlg_ok': '확인',
        'dlg_yes': '예',
        'dlg_no': '아니오',
        'rename_do': '변경하기',
        'rename_cancel': '취소',
        'rename_no_preview': '먼저 미리보기를 실행하세요.',
        'rename_collision': '충돌 감지',
        'dlg_warning':   '경고',
        'dlg_done':      '완료',
        'dlg_done_err':  '완료 (일부 오류)',
        'dlg_undo':      '실행 취소',
        'dlg_undo_fail': '실행 취소 실패',
        'dlg_save_err':  '저장 오류',
        'dlg_confirm_title': '확인',
        'conv_unsupported': '지원되지 않는 파일 형식',
        'conv_no_outdir':   '폴더를 먼저 지정하세요.',
        'conv_no_files_msg':'파일을 먼저 추가하세요.',
        'conv_outdir_miss': '출력 폴더가 존재하지 않습니다.',
        'tag_no_files_msg': '추가된 파일이 없습니다.',
        'tag_no_tag_msg':   '추가할 태그를 입력해주세요.',
        'merge_clr_confirm':'목록의 모든 파일을 삭제할까요?',
        'merge_undo_done':  '병합 파일을 삭제했습니다.',
        'merge_undo_miss':  '파일을 찾을 수 없습니다.',
        'first_run_title':  '처음 실행하셨군요!',
        'first_run_desc':   'File Nexus Suite는 아래의 파일과 폴더를 프로그램 위치에 자동으로 생성합니다.',
        'first_run_item_json':   '환경설정(테마·언어·단축키 등)을 저장하는 구성 파일',
        'first_run_item_output': 'Text Converter · Bulk Fixer 기본 출력 폴더',
        'first_run_item_log':    'crash_*.log  오류 발생 시 자동 생성되는 크래시 로그 (최근 3개 보관)',
        'first_run_tip':    '필요 시 삭제 가능하며, 프로그램 실행 시 자동으로 재생성됩니다.',
        'first_run_item_internal': '_internal/ 폴더는 프로그램 필수 파일입니다. 삭제하면 실행이 불가능합니다.',
        'close_busy_title':  '작업 진행 중',
        'close_busy_msg':    '작업이 진행 중입니다. 지금 종료하면 데이터가 손실될 수 있습니다.\n\n종료하시겠습니까?',
        'close_busy_exit':   '종료',
        'close_busy_cancel': '취소',
        'first_run_ui_title':  'File Nexus Suite UI 안내',
        'first_run_ui_help':   '우측 상단의 💡 버튼을 클릭하면 각 탭의 상세 사용법을 확인할 수 있습니다.',
        'first_run_ui_batch':  'Batch Renamer 오른쪽 패널 상단의 // 사용법 ▼을 클릭하면 관련 안내가 펼쳐집니다.',
        'first_run_tabs_title': '탭 기능 안내',
        'first_run_tab_merger': '여러 파일을 하나의 텍스트로 병합합니다',
        'first_run_tab_converter': 'TXT ↔ EPUB 파일을 상호 변환합니다',
        'first_run_tab_tag': '파일명의 [태그]를 일괄 추가·제거합니다',
        'first_run_tab_batch': '폴더·파일 이름을 규칙에 따라 일괄 변경합니다',
        'first_run_tab_fixer': '단일 TXT 파일의 줄바꿈을 교정합니다',
        'first_run_tab_bulk': '여러 TXT 파일의 줄바꿈을 일괄 교정합니다',
        'dlg_error_title': '오류',
        'rename_no_pairs':   '변경할 이름이 없습니다.',
        'rename_explorer_warn': '⚠  탐색기에서 대상 폴더가 열려있으면 액세스 오류가 발생할 수 있습니다.\n이름 변경 전 탐색기 창을 닫거나 다른 위치로 이동해 주세요.',
        'rename_no_subfolders': '하위 폴더가 없습니다.',
        'rename_no_files':   '파일이 없습니다.',
        'merge_no_support':  '폴더에서 지원 파일을 찾을 수 없습니다.\n지원: txt · md · csv · docx · pdf · xlsx · hwpx 등',
        'merge_hwp_legacy_title': 'HWP(구형) 파일은 지원되지 않습니다',
        'merge_hwp_legacy_msg':   '구형 HWP 파일({n}개)이 감지되어 추가되지 않았습니다.\n\n한컴 한글에서 <b>다른 이름으로 저장 → HWPX</b>로 변환 후 다시 시도해주세요.\n\nText Merger는 HWPX(KS X 6101 OWPML 표준) 형식만 지원합니다.',
        'merge_no_files':   '병합할 파일이 없습니다.',
        'sc_tab_merger': 'Text Merger 탭 전환',
        'sc_tab_converter': 'Text Converter 탭 전환',
        'sc_tab_tag': 'Tag Editor 탭 전환',
        'sc_tab_batch': 'Batch Renamer 탭 전환',
        'sc_tab_fixer': 'Text Fixer 탭 전환',
        'sc_tab_bulk':  'Bulk Fixer 탭 전환',
        'batch_btn_rename': '이름 변경 실행',
        'btn_preview': '미리보기',
        'sq_suffix_ph2': '예: _final',
        'sq_prefix_ph2': '예: chapter_',
        'settings_tooltip': '설정',
        'settings_nav_license': '라이선스',
        'license_summary': 'MIT 라이선스로 배포 · 사용·수정·재배포·판매 모두 허용 · 저작권 고지 유지 필요',
        'tf_open':         '파일 열기',
        'tf_run':          '수정 실행',
        'tf_copy':         '복사',
        'tf_save':         '저장',
        'tf_save_fixed':   '원본 위치에 [Fixed] 태그로 저장',
        'tf_save_as':      '다른 이름으로 저장…',
        'tf_clear':        '초기화',
        'tf_opt_mid':      '단락 내 줄바꿈 병합  (빈 줄 기준)',
        'tf_opt_sep':      '문장마다 빈 줄 삽입',
        'tf_opt_auto':     '자동 단락 분리 — 최대',
        'tf_opt_chars':    '자',
        'tf_opt_blank':    '과도한 빈 줄 축소 — 최대',
        'tf_opt_line':     '줄',
        'tf_lang_mode':    '병합 모드',
        'tf_preset_label':  '프리셋',
        'tf_preset_doc':    '일반 문서',
        'tf_preset_novel':  '책·소설',
        'tf_lang_auto':    '자동',
        'tf_lang_ko':      '한국어·기타',
        'tf_lang_en':      'English',
        'tf_grp_input':    '// 원본 텍스트',
        'tf_grp_output':   '// 수정된 텍스트',
        'tf_ph_input_edit': '여기에 텍스트를 직접 붙여넣으세요...',
        'tf_ph_output':    '수정 결과가 여기에 표시됩니다...',
        'tf_stat_mid':     '병합된 줄: -',
        'tf_stat_mid_n':   '병합된 줄: {n}건',
        'tf_stat_blank':   '빈 줄 축소: -',
        'tf_stat_blank_n': '빈 줄 축소: {n}건',
        'tf_stat_orig':    '원본 줄 수: -',
        'tf_stat_orig_n':  '원본 줄 수: {n}',
        'tf_stat_new':     '수정 후 줄 수: -',
        'tf_stat_new_n':   '수정 후 줄 수: {n}',
        'tf_search_ph':    '검색어 입력  (Enter: 다음,  Shift+Enter: 이전)',
        'tf_search_none':  '없음',
        'tf_search_prev':  '◀ 이전',
        'tf_search_next':  '다음 ▶',
        'tf_diff_prev':    '◀ 이전',
        'tf_diff_next':    '다음 ▶',
        'tf_status_ready': 'Text Fixer에 오신 것을 환영합니다',
        'tf_done':         '🌿  완료 — 줄 병합 {mid}건, 빈 줄 {blank}건 수정됨',
        'tf_copied':       '📋  클립보드에 복사됐습니다',
        'tf_saved':        '💾  저장 완료: {name}',
        'tf_cleared':      '초기화됐습니다',
        'bulk_file_list':  '// 파일 목록',
        'bulk_drop_txt':   '파일 또는 폴더를 드래그하세요',
        'bulk_drop_fmt':   'TXT (*.txt) 형식 지원',
        'bulk_options':    '// 교정 옵션',
        'bulk_preview':    '// 미리보기',
        'bulk_preview_ph': '파일을 선택하면 미리보기가 표시됩니다',
        'bulk_save_mode':  '// 저장 설정',
        'bulk_save_desc':   '[Fixed] 태그를 앞에 붙여 저장합니다. 출력 폴더를 지정하지 않으면 원본 파일과 같은 위치에 저장됩니다.',
        'bulk_keep_structure': '폴더 구조 유지 (출력 폴더 지정 시)',
        'bulk_out_ph':     '비워두면 원본 파일 위치에 저장',
        'bulk_run':        '일괄 교정 시작',
        'bulk_running':    '⏳ 처리 중…',
        'bulk_status_ready': '파일을 추가하고 일괄 교정을 시작하세요.',
        'bulk_status_done':  '✔  완료 — {n}개 파일 처리됨',
        'bulk_status_err':   '⚠  오류 발생: {msg}',
        'conv_status_done':  '✅ 완료!',
        'conv_status_fail':  '❌ 변환 실패',
        'tf_undo_done':      '실행 취소 — 원본 텍스트로 복원됐습니다',
        'merge_status_add':  '{n}개 파일 추가됨 (인코딩 자동 감지 완료)',
        'merge_status_del':  '{n}개 파일 삭제됨',
        'merge_status_clr':  '전체 삭제 완료',
        'merge_path_set':    '저장 경로 지정: {path}',
        'merge_path_reset_done': '저장 경로가 초기화되었습니다',
        'merge_reading':     '📂  파일 읽는 중...',
        'merge_save_done':   '저장 완료 ({enc}): {path}',
        'merge_save_err':    '❌ 오류 발생',
        'merge_enc_warn_title': '⚠ 인코딩 호환성 경고',
        'merge_enc_warn_msg':   '선택하신 저장 인코딩 <b>{enc}</b>(으)로는 일부 문자가 표현되지 않습니다.<br><br>• 깨질 문자 종류: 약 <b>{kinds}종</b><br>• 영향받는 글자 수: 약 <b>{total}자</b> (전체의 <b>{pct}%</b>)<br>• 샘플: <code>{samples}</code><br><br>계속 진행하면 해당 문자는 <code>?</code>로 대체되어 저장됩니다.<br><br>그래도 저장하시겠습니까?',
        # v1.0.5: Text Merger 저장 인코딩 드롭다운 용도 설명 라벨 + 한 줄 도움말
        'merge_enc_utf8':      'UTF-8',
        'merge_enc_utf8_bom':  'UTF-8-BOM (Excel 호환)',
        'merge_enc_euckr':     'EUC-KR (한국어)',
        'merge_enc_cp949':     'CP949 (한국어 Windows)',
        'merge_enc_utf16':     'UTF-16',
        'merge_enc_shiftjis':  'Shift-JIS (일본어)',
        'merge_enc_gbk':       'GBK (중국어 간체)',
        'merge_enc_big5':      'Big5 (중국어 번체)',
        'merge_enc_hint':      '확실하지 않으면 UTF-8을 선택하세요',
        'merge_enc_recommend': '💡 추천: {enc}',
        'merge_enc_recommend_apply': '적용',
        'merge_low_conf_hint':  'ℹ chardet 원본 신뢰도가 낮게 표시되어도 인코딩 결과는 정확할 수 있습니다 (특히 CJK 인코딩).',
        'tag_file_count':    '파일 {n}개',
        'sc_none':           '없음',
        'sc_press':          '입력하세요…',
        'bulk_file_count': '파일 {n}개',
        'bulk_err_nofiles': '처리할 파일이 없습니다.',
        'bulk_no_txt':      '폴더에서 TXT 파일을 찾을 수 없습니다.',
        'bulk_scanning':    '폴더 탐색 중... {n}개 발견',
        'tf_running':      '✨  수정 중...',
        'tf_err_nofile':   '파일을 찾을 수 없습니다',
        'tf_err_perm':     '파일을 읽을 권한이 없습니다',
        'tf_err_enc':      '지원하는 인코딩으로 파일을 읽을 수 없습니다',
        'tf_warn_partial_enc': '⚠ 일부 문자의 인코딩이 손상되어 있습니다.\n\n파일: {fname}\n사용 인코딩: {enc}\n대체된 문자 수: {n}개\n\n파일은 로드되었으나 손상된 위치에 대체 문자(�)가 표시됩니다.\n원본 파일이 손상되지 않았는지 확인해주세요.',
        # v1.0.6 Phase 2-a: Bulk Fixer 완료 다이얼로그 (4-카테고리 브레이크다운)
        'bulk_done_title':   '교정 완료',
        'bulk_done_ok':      '정상 처리: {n}개',
        'bulk_done_warn':    '주의 처리: {n}개 (인코딩 리포트 생성됨)',
        'bulk_done_skip':    '스킵됨: {n}개 (Text Fixer에서 검토 권장)',
        'bulk_done_fail':    '실패: {n}개 (디버그 로그 확인)',
        'bulk_status_skip':  '스킵',
        # v1.0.6 Phase 2-a: 인코딩 리포트 템플릿 (파일로 저장되는 텍스트)
        'report_header':          'File Nexus Suite — 인코딩 변환 리포트',
        'report_file':            '파일',
        'report_path':            '경로',
        'report_size':            '파일 크기',
        'report_enc':             '감지 인코딩',
        'report_fail_count':      '인코딩 실패 수',
        'report_action':          '처리 결과',
        'report_action_processed':'교정 완료',
        'report_action_skipped':  '처리 건너뜀 (원본 보호)',
        'report_time':            '리포트 생성 시각',
        'report_line_col':        'Line {line}, Column {col}',
        'report_bytes':           '원본 바이트',
        'report_context':         '주변 텍스트',
        'report_summary_title':   '요약 통계',
        'report_total_failures':  '총 실패 문자 수',
        'report_truncated':       '추적 생략 (상세 기록은 최대 5,000개까지)',
        'report_advice_title':    '권장 조치',
        'report_advice_tier1':    ('파일은 정상적으로 교정되었으나 일부 문자가 손상되어 있습니다.\n'
                                  '해당 라인을 메모장 또는 전용 텍스트 에디터로 확인하시고,\n'
                                  '필요 시 원본 출처에서 재다운로드를 권장합니다.'),
        'report_advice_tier2':    ('파일은 교정되었으나 다수의 문자가 손상되어 있습니다.\n'
                                  '교정된 결과물의 품질이 저하되었을 수 있으므로 반드시 검토하세요.\n'
                                  '원본 파일의 상태를 우선적으로 확인하시기 바랍니다.'),
        'report_advice_tier3':    ('이 파일은 위에 표시된 "감지 인코딩"으로 5,000개 이상의\n'
                                  '디코딩 실패가 발생했습니다.\n'
                                  '이는 파일의 실제 인코딩이 감지된 것과 다를 가능성이 매우 높다는\n'
                                  '뜻입니다. 잘못된 인코딩으로 강제 처리 시 결과물이 원본보다\n'
                                  '손상될 수 있어, 원본 보호를 위해 자동 제외되었습니다.\n\n'
                                  '권장 조치:\n'
                                  '- Text Fixer에서 이 파일을 개별 검토하세요.\n'
                                  '- 원본 파일이 다른 인코딩(UTF-8, Shift-JIS 등)일 가능성을 확인하세요.'),
        'tf_err_fix':      '오류가 발생했습니다',
        'tf_err_save':     '저장할 수 없습니다',
        'tf_dlg_nofile':   '파일 없음',
        'tf_dlg_noperm':   '접근 오류',
        'tf_dlg_ioerr':    '파일 오류',
        'tf_dlg_encerr':   '인코딩 오류',
        'tf_highlight':    '🟡 노란 줄 = 병합됨  🟠 주황 줄 = 빈 줄 제거',
        'tf_drop1': 'TXT 파일을 드래그하거나  파일 추가 버튼을 사용하세요',
        'tf_drop2': 'TXT (*.txt) 형식 지원',
        'tf_drop_hover': '놓으면 파일을 불러옵니다!',
        'open_folder_tooltip': '폴더 열기',
        'theme_lavender': '라벤더',
        'theme_sakura': '벚꽃',
        'theme_honey': '허니',
        'theme_sand': '샌드',
        'theme_ocean': '오션',
        'theme_mint': '민트',
        'theme_choco': '앤틱 브론즈',
        'theme_dark': '다크',
        'theme_auto': '자동 (기본)',
        'theme_light': '화이트',
        'merge_ext_supported': '지원',
        'batch_file_ext_ph': '예: jpg, png, gif',
        'batch_file_fmt_pattern': '{폴더명}{구분자}{번호}.{확장자}',
        'batch_file_fmt_label': '출력 형식',
        'conv_drop_epub_fmt': 'EPUB (*.epub) 형식 지원',
        'conv_drop_txt_fmt': 'TXT (*.txt) 형식 지원',
        'batch_del_all': '전체 삭제',
        'batch_click_preview': '← 미리보기를 누르세요',
        'batch_parent_folder': '  (상위 폴더 — 이름 변경 안 됨)',
        'batch_folder_label': '  (폴더)',
        'batch_confirm_items': '개 항목의 이름을 변경합니다',
        'batch_done_items': '개 이름 변경 완료',
        'dlg_rename_partial_note': '실패 항목은 변경되지 않았으며, 실행 취소 대상에서도 제외됩니다.',
        'sq_suffix_ph': '예: 화',
        'sq_prefix_ph': '예: ch_',
        'sm_suffix_ph': '예: 화',
        'sm_prefix_ph': '예: ch_',
        'batch_count_file': '그룹 {g}개 / 파일 {f}개',
        'batch_count_folder': '그룹 {g}개 / 폴더 {f}개',
        'batch_drop2_p': '여러 폴더 동시 드래그 가능',
        'batch_drop1_p': '폴더를 드래그 → 파일 이름 변경',
        'batch_drop2_f': '여러 폴더 동시 드래그 가능',
        'batch_drop1_f': '상위 폴더를 드래그 → 하위 폴더 이름 변경',
        'tag_drop2': '클릭하면 폴더 선택 창이 열립니다',
        'tag_drop1': '파일 또는 폴더를 드래그하세요',
        'conv_file_count': '파일 {n}개',
        'conv_drop_epub': 'EPUB 파일을 드래그하거나  파일 추가 버튼을 사용하세요',
        'conv_drop_txt': 'TXT 파일을 드래그하거나  파일 추가 버튼을 사용하세요',
        'merge_sel_multi': '선택된 파일 {n}개: {names}{more}',
        'merge_sel_one': '선택된 파일: {name}',
        'merge_stats': '파일 {n}개 | 총 {lines}줄',
        'merge_drop': '파일 또는 폴더를 드래그하세요',
        'dlg_rename_confirm': '이름 변경 확인',
        'dlg_rename_done': '완료',
        'dlg_rename_partial': '일부 실패',
        'crash_title': '예상치 못한 오류 발생',
        'crash_main': '오류가 발생하여 프로그램이 종료됩니다.',
        'crash_log_at': '로그 저장 위치:',
        'crash_open_log': '로그 폴더 열기',
        'already_running_title': '이미 실행 중',
        'already_running_main': 'File Nexus Suite가 이미 실행 중입니다.',
        'already_running_sub': '실행 중인 창을 확인해 주세요.',
        'rename_skip_dup_in_batch': '배치 내 동일 목적지 중복',
        'rename_skip_dest_exists': '목적지 파일 이미 존재',
        'lib_required_msg': '{lib} 라이브러리가 필요합니다.\npip install {lib}',
        'dlg_info': '알림',
        'help_window_title': '💡  도움말 — File Nexus Suite v{ver}',
        'help_sidebar_title': '💡  도움말',
        'help_section_intro': '소개'},
 'en': {'app_subtitle': 'Integrated File Tool',
        'debug_log': 'Debug Log',
        'btn_clear': 'Clear',
        'btn_add_file': 'Add Files',
        'btn_add_folder': 'Add Folder',
        'btn_del_sel': 'Delete Selected',
        'btn_del_all': 'Delete All',
        'btn_up': 'Up',
        'btn_down': 'Down',
        'btn_close': 'Close',
        'btn_apply': 'Apply',
        'btn_reset': 'Default',
        'btn_reset_all': 'Reset All Shortcuts',
        'merge_save_settings': '// Save Settings',
        'merge_save_enc': 'Encoding:',
        'merge_save_path': 'Save Path:',
        'merge_path_none': 'No save path specified',
        'merge_path_pick': 'Select Path',
        'merge_path_reset': 'Reset',
        'merge_sep': 'Insert File Separator',
        'merge_btn': 'Merge && Save',
        'merge_status_ready': 'Ready',
        'btn_undo': 'Undo',
        'btn_abort': 'Stop',
        'merge_sel_none': 'Selected: None',
        'merge_open_explorer': 'Open in Explorer',
        'conv_sub_txt2epub': 'TXT → EPUB',
        'conv_sub_epub2txt': 'EPUB → TXT',
        'conv_out_folder': '// Output Folder',
        'conv_out_ph': 'Blank = save next to source file',
        'conv_btn_pick': 'Select Folder',
        'conv_btn_start': 'Start Conversion',
        'conv_btn_converting': '⏳ Converting…',
        'conv_opt_epub2txt': '⚙  Options  (EPUB → TXT)',
        'conv_chk_sep': 'Add Chapter Separator',
        'conv_chk_title': 'Include Chapter Titles',
        'conv_chk_trim': 'Trim Consecutive Blank Lines',
        'conv_save_enc': 'Save Encoding:',
        'tc_title_placeholder': 'Untitled',
        'tc_author_placeholder': 'Unknown',
        'conv_meta': '📖  Book Info  (TXT → EPUB)',
        'conv_book_title': 'Title',
        'conv_author': 'Author',
        'conv_lang': 'Language:',
        'conv_chapter_mode': 'Chapter Split:',
        'conv_ch0': 'By separator (===, ---, ★★★…)',
        'conv_ch1': 'By 3+ blank lines',
        'conv_ch2': 'Entire file as one chapter',
        'conv_status_start': 'Add files and start conversion.',
        'conv_file_list': '// File List',
        'tag_sub_remove': 'Remove Tag',
        'tag_sub_add': 'Add Tag',
        'tag_sub_depad': 'Remove Leading Zeros',
        'tag_col_filename': 'Filename',
        'tag_col_path': 'Path',
        'tag_filter': '// Filter Settings',
        'tag_ext_label': 'Extensions',
        'tag_ext_hint': 'comma-separated',
        'tag_cb_recursive': 'Include Subfolders',
        'tag_cb_allext': 'All Extensions',
        'tag_rm_pos': 'Remove From',
        'tag_rm_tag': 'Target Tag',
        'tag_rm_tag_ph': 'Empty = remove all [tags]',
        'tag_rm_front': 'Front',
        'tag_rm_back': 'Back',
        'tag_rm_both': 'Both',
        'tag_add_fmt': 'Tag Format',
        'tag_add_fmt_hint': 'e.g.  [tag]  @tag  #tag',
        'tag_add_val': 'Tag Value',
        'tag_add_val_ph': 'Comma-separated tags',
        'tag_add_pos': 'Position',
        'tag_add_front': 'Before Name',
        'tag_add_back': 'After Name',
        'tag_add_skip': 'Skip if tag exists',
        'tag_add_replace': 'Replace existing tag',
        'tag_add_space_after': 'Space after tag',
        'tag_add_space_before': 'Space before tag',
        'tag_col_folder': 'Folder',
        'tag_col_orig': 'Original Name',
        'tag_col_new': 'New Name',
        'tag_btn_apply_rm': 'Apply Remove',
        'tag_btn_apply_add': 'Apply Add',
        'tag_btn_apply_depad': 'Apply',
        'tag_status_start': 'Add files then click Preview.',
        'tag_count_total':  'Total: {n}',
        'tag_status_found': 'Tag removable in {n} file(s).',
        'tag_status_found_add': 'Tag addable to {n} file(s).',
        'tag_status_found_depad': 'Leading zeros removable in {n} file(s).',
        'tag_no_change':    'No files to change.',
        'tag_skip_count':   '{n} skipped',
        'tag_apply_confirm': 'Rename {n} file(s).\nContinue?',
        'tag_apply_done':   '{n} file(s) {label} complete.',
        'batch_sub_folder': '📁  Rename Folders',
        'batch_sub_file': '📄  Rename Files',
        'batch_btn_folder_pick': 'Select Folder',
        'batch_btn_file_pick': 'Select Folder',
        'batch_col_folder': 'Folder Name',
        'batch_col_arrow': '▶',
        'batch_col_new': 'New Name',
        'batch_col_file': 'Original Name',
        'batch_col_file_new': 'New Name',
        'batch_opt_smart': 'Smart Extract',
        'batch_opt_seq': 'Sequential',
        'batch_smart_pfx': '// Prefix / Suffix',
        'batch_smart_prefix': 'Prefix',
        'batch_smart_suffix': 'Suffix',
        'batch_smart_common': '// Common Prefix',
        'batch_smart_auto': 'Auto Detect',
        'batch_smart_manual': 'Manual',
        'batch_smart_none': 'Keep As-Is',
        'batch_smart_manual_ph': 'Prefix to remove',
        'batch_seq_reset': '// Number Reset',
        'batch_seq_global': 'Continuous',
        'batch_seq_pergroup': 'Reset per Group',
        'batch_seq_start': '// Start Number',
        'batch_seq_from0': 'From 00',
        'batch_seq_from1': 'From 01',
        'batch_seq_digits': '// Digits',
        'batch_seq_auto': 'Auto (Recommended)',
        'batch_seq_2d': '2 Fixed',
        'batch_seq_3d': '3 Fixed',
        'batch_seq_4d': '4 Fixed',
        'batch_seq_pfx_lbl': '// Prefix / Suffix',
        'batch_seq_name': '// Name Mode',
        'batch_seq_numonly': 'Number Only',
        'batch_seq_keep': 'Number + Name',
        'batch_seq_sep': 'Separator',
        'batch_file_pfx': '// Prefix',
        'batch_file_pfx_folder': 'Use Folder Name (Recommended)',
        'batch_file_pfx_custom': 'Custom Input',
        'batch_file_pfx_ph': 'Apply to all folders',
        'batch_file_sep_start': '// Separator / Start',
        'batch_file_sep': 'Separator',
        'batch_file_from0': 'From 0',
        'batch_file_from1': 'From 1',
        'batch_file_digits': '// Digits',
        'batch_file_auto': 'Auto (Recommended)',
        'batch_file_nopad': 'None (1,2…)',
        'batch_file_2d': 'Min 2 digits',
        'batch_file_3d': 'Min 3 digits',
        'batch_file_filter': '// File Filter',
        'batch_file_all': 'All Files',
        'batch_file_ext': 'Specific Extensions',
        'batch_usage_title': 'How to Use',
        'batch_hint_folder': '<b>How to Use</b><br>① Drag parent folder or use button<br>② Select renaming method<br>③ '
                             'Check <b>Preview</b><br>④ <b>Execute Rename</b><br><br>📌 Parent folder is <b>NOT '
                             'renamed</b><br>📌 Only subfolders are renamed',
        'batch_hint_file': '📌 <b>Folder name</b> used as prefix<br>📌 Files sorted by name then numbered<br>📌 Original '
                           'extension preserved<br>📌 Hidden files (.*) excluded',
        'settings_title': 'Settings',
        'settings_nav_theme': 'Theme',
        'settings_nav_shortcuts': 'Shortcuts',
        'settings_nav_language': 'General',
        'settings_theme_title': 'Color Mode',
        'settings_theme_hint': 'Double-click to apply immediately.',
        'settings_output_dir': 'Output Folder',
        'settings_sc_title': 'Keyboard Shortcuts',
        'settings_sc_desc': 'Click a button then press the desired key. Press ESC to cancel.',
        'settings_sc_action': 'Action',
        'settings_sc_key': 'Shortcut',
        'settings_sc_note': '💡  Shortcuts are applied when you click Apply.',
        'settings_lang_title': 'Language',
        'settings_lang_desc': 'Select UI language. Click Apply to confirm.',
        'settings_applied': '✅  Settings applied.',
        'dlg_ok': 'OK',
        'dlg_yes': 'Yes',
        'dlg_no': 'No',
        'rename_do': 'Rename',
        'rename_cancel': 'Cancel',
        'rename_no_preview': 'Please run preview first.',
        'rename_collision': 'Name Conflict',
        'dlg_warning':   'Warning',
        'dlg_done':      'Done',
        'dlg_done_err':  'Done (with errors)',
        'dlg_undo':      'Undo',
        'dlg_undo_fail': 'Undo Failed',
        'dlg_save_err':  'Save Error',
        'dlg_confirm_title': 'Confirm',
        'conv_unsupported': 'Unsupported file format',
        'conv_no_outdir':   'Please specify an output folder first.',
        'conv_no_files_msg':'Please add files first.',
        'conv_outdir_miss': 'Output folder does not exist.',
        'tag_no_files_msg': 'No files added.',
        'tag_no_tag_msg':   'Please enter a tag to add.',
        'merge_clr_confirm':'Remove all files from the list?',
        'merge_undo_done':  'Merged file deleted.',
        'merge_undo_miss':  'File not found.',
        'first_run_title':  'Welcome to File Nexus Suite!',
        'first_run_desc':   'File Nexus Suite automatically creates the following files and folders in the program directory.',
        'first_run_item_json':   'Configuration file that stores settings (theme, language, shortcuts, etc.)',
        'first_run_item_output': 'Default output folder for Text Converter and Bulk Fixer',
        'first_run_item_log':    'crash_*.log  Crash logs generated automatically on error (last 3 kept)',
        'first_run_tip':    'Can be deleted if needed — they will be recreated automatically on the next launch.',
        'first_run_item_internal': 'The _internal/ folder contains essential program files. Deleting it will prevent the program from running.',
        'close_busy_title':  'Task in Progress',
        'close_busy_msg':    'A task is currently running. Quitting now may result in data loss.\n\nAre you sure you want to quit?',
        'close_busy_exit':   'Quit',
        'close_busy_cancel': 'Cancel',
        'first_run_ui_title':  'File Nexus Suite UI Guide',
        'first_run_ui_help':   'Click the 💡 button in the upper-right corner to view detailed usage for each tab.',
        'first_run_ui_batch':  'In Batch Renamer, click // How to Use ▼ at the top of the right panel to expand the guide.',
        'first_run_tabs_title': 'Tab Features',
        'first_run_tab_merger': 'Merge multiple files into a single text',
        'first_run_tab_converter': 'Convert between TXT and EPUB formats',
        'first_run_tab_tag': 'Batch add or remove [tags] from filenames',
        'first_run_tab_batch': 'Rename folders and files in bulk with rules',
        'first_run_tab_fixer': 'Fix line breaks in a single TXT file',
        'first_run_tab_bulk': 'Fix line breaks across multiple TXT files',
        'dlg_error_title': 'Error',
        'rename_no_pairs':   'No names to change.',
        'rename_explorer_warn': '⚠  If the target folder is open in Explorer, an access error may occur.\nPlease close Explorer or navigate away before renaming.',
        'rename_no_subfolders': 'No subfolders found.',
        'rename_no_files':   'No files found.',
        'merge_no_support':  'No supported files found in folder.\nSupported: txt · md · csv · docx · pdf · xlsx · hwpx, etc.',
        'merge_hwp_legacy_title': 'HWP (legacy) files are not supported',
        'merge_hwp_legacy_msg':   '{n} legacy HWP file(s) detected and skipped.\n\nPlease open the file in Hancom Office and use <b>Save As → HWPX</b>, then try again.\n\nText Merger only supports the HWPX format (KS X 6101 OWPML standard).',
        'merge_no_files':   'No files to merge.',
        'sc_tab_merger': 'Switch to Text Merger',
        'sc_tab_converter': 'Switch to Text Converter',
        'sc_tab_tag': 'Switch to Tag Editor',
        'sc_tab_batch': 'Switch to Batch Renamer',
        'sc_tab_fixer': 'Switch to Text Fixer',
        'sc_tab_bulk':  'Switch to Bulk Fixer',
        'batch_btn_rename': 'Rename',
        'btn_preview': 'Preview',
        'sq_suffix_ph2': 'e.g. _final',
        'sq_prefix_ph2': 'e.g. chapter_',
        'settings_tooltip': 'Settings',
        'settings_nav_license': 'License',
        'license_summary': 'Licensed under the MIT License · Free to use, modify, distribute, and sell · Copyright notice must be retained.',
        'tf_open':         'Open File',
        'tf_run':          'Fix',
        'tf_copy':         'Copy',
        'tf_save':         'Save',
        'tf_save_fixed':   'Save as [Fixed] beside original',
        'tf_save_as':      'Save As…',
        'tf_clear':        'Clear',
        'tf_opt_mid':      'Merge lines',
        'tf_opt_sep':      'Insert blanks',
        'tf_opt_auto':     'Auto-split — max',
        'tf_opt_chars':    'chars',
        'tf_opt_blank':    'Reduce blanks — max',
        'tf_opt_line':     'lines',
        'tf_lang_mode':    'Merge Mode',
        'tf_preset_label':  'Preset',
        'tf_preset_doc':    'General',
        'tf_preset_novel':  'Book/Novel',
        'tf_lang_auto':    'Auto',
        'tf_lang_ko':      'Korean·Other',
        'tf_lang_en':      'English',
        'tf_grp_input':    '// Original Text',
        'tf_grp_output':   '// Fixed Text',
        'tf_ph_input_edit': 'Paste your text here directly...',
        'tf_ph_output':    'Fixed result will appear here...',
        'tf_stat_mid':     'Merged lines: -',
        'tf_stat_mid_n':   'Merged: {n} lines',
        'tf_stat_blank':   'Blanks reduced: -',
        'tf_stat_blank_n': 'Blanks reduced: {n}',
        'tf_stat_orig':    'Original lines: -',
        'tf_stat_orig_n':  'Original: {n} lines',
        'tf_stat_new':     'Fixed lines: -',
        'tf_stat_new_n':   'Fixed: {n} lines',
        'tf_search_ph':    'Enter keyword  (Enter: next,  Shift+Enter: prev)',
        'tf_search_none':  'None',
        'tf_search_prev':  '◀ Prev',
        'tf_search_next':  'Next ▶',
        'tf_diff_prev':    '◀ Prev',
        'tf_diff_next':    'Next ▶',
        'tf_status_ready': 'Welcome to Text Fixer',
        'tf_done':         '🌿  Done — {mid} merges, {blank} blanks fixed',
        'tf_copied':       '📋  Copied to clipboard',
        'tf_saved':        '💾  Saved: {name}',
        'tf_cleared':      'Cleared',
        'bulk_file_list':  '// File List',
        'bulk_drop_txt':   'Drag files or folders here',
        'bulk_drop_fmt':   'TXT (*.txt) supported',
        'bulk_options':    '// Fix Options',
        'bulk_preview':    '// Preview',
        'bulk_preview_ph': 'Select a file to preview',
        'bulk_save_mode':  '// Save Settings',
        'bulk_save_desc':   'Saves with [Fixed] prefix. If no output folder is specified, saves alongside the original file.',
        'bulk_keep_structure': 'Preserve folder structure (when output folder is set)',
        'bulk_out_ph':     'Empty = save beside source file',
        'bulk_run':        'Start Bulk Fix',
        'bulk_running':    '⏳ Processing…',
        'bulk_status_ready': 'Add files and start bulk fix.',
        'bulk_status_done':  '✔  Done — {n} file(s) processed',
        'bulk_status_err':   '⚠  Error: {msg}',
        'conv_status_done':  '✅ Done!',
        'conv_status_fail':  '❌ Conversion failed',
        'tf_undo_done':      'Undone — original text restored',
        'merge_status_add':  '{n} file(s) added (encoding auto-detected)',
        'merge_status_del':  '{n} file(s) removed',
        'merge_status_clr':  'All files cleared',
        'merge_path_set':    'Save path set: {path}',
        'merge_path_reset_done': 'Save path reset',
        'merge_reading':     '📂  Reading files...',
        'merge_save_done':   'Saved ({enc}): {path}',
        'merge_save_err':    '❌ Error occurred',
        'merge_enc_warn_title': '⚠ Encoding compatibility warning',
        'merge_enc_warn_msg':   'The selected save encoding <b>{enc}</b> cannot represent some characters.<br><br>• Distinct incompatible characters: about <b>{kinds}</b><br>• Total affected characters: about <b>{total}</b> (<b>{pct}%</b> of file)<br>• Sample: <code>{samples}</code><br><br>If you continue, those characters will be replaced with <code>?</code>.<br><br>Proceed with save?',
        # v1.0.5: Text Merger save-encoding dropdown labels + one-line hint
        'merge_enc_utf8':      'UTF-8',
        'merge_enc_utf8_bom':  'UTF-8-BOM (Excel compatible)',
        'merge_enc_euckr':     'EUC-KR (Korean)',
        'merge_enc_cp949':     'CP949 (Korean Windows)',
        'merge_enc_utf16':     'UTF-16',
        'merge_enc_shiftjis':  'Shift-JIS (Japanese)',
        'merge_enc_gbk':       'GBK (Simplified Chinese)',
        'merge_enc_big5':      'Big5 (Traditional Chinese)',
        'merge_enc_hint':      'If unsure, select UTF-8',
        'merge_enc_recommend': '💡 Recommended: {enc}',
        'merge_enc_recommend_apply': 'Apply',
        'merge_low_conf_hint':  'ℹ Even if the chardet raw confidence is low, the detected encoding may still be accurate (especially for CJK encodings).',
        'tag_file_count':    '{n} file(s)',
        'sc_none':           'None',
        'sc_press':          'Press a key…',
        'bulk_file_count': '{n} file(s)',
        'bulk_err_nofiles': 'No files to process.',
        'bulk_no_txt':      'No TXT files found in the folder.',
        'bulk_scanning':    'Scanning... {n} found',
        'tf_running':      '✨  Fixing...',
        'tf_err_nofile':   'File not found',
        'tf_err_perm':     'No read permission',
        'tf_err_enc':      'Cannot read file with supported encodings',
        'tf_warn_partial_enc': '⚠ Some characters have corrupted encoding.\n\nFile: {fname}\nUsed encoding: {enc}\nReplaced characters: {n}\n\nThe file was loaded, but replacement characters (�) will appear at corrupted positions.\nPlease check if the original file is intact.',
        # v1.0.6 Phase 2-a: Bulk Fixer completion dialog (4-category breakdown)
        'bulk_done_title':   'Correction Complete',
        'bulk_done_ok':      'Normally processed: {n}',
        'bulk_done_warn':    'Processed with warnings: {n} (encoding report generated)',
        'bulk_done_skip':    'Skipped: {n} (review in Text Fixer recommended)',
        'bulk_done_fail':    'Failed: {n} (check debug log)',
        'bulk_status_skip':  'Skipped',
        # v1.0.6 Phase 2-a: Encoding report template (saved as text file)
        'report_header':          'File Nexus Suite — Encoding Conversion Report',
        'report_file':            'File',
        'report_path':            'Path',
        'report_size':            'File size',
        'report_enc':             'Detected encoding',
        'report_fail_count':      'Encoding failure count',
        'report_action':          'Action taken',
        'report_action_processed':'Corrected',
        'report_action_skipped':  'Skipped (original preserved)',
        'report_time':            'Report generated at',
        'report_line_col':        'Line {line}, Column {col}',
        'report_bytes':           'Original bytes',
        'report_context':         'Surrounding text',
        'report_summary_title':   'Summary',
        'report_total_failures':  'Total failures',
        'report_truncated':       'Omitted from tracking (details limited to 5,000 entries)',
        'report_advice_title':    'Recommended action',
        'report_advice_tier1':    ('The file was corrected successfully, but some characters are damaged.\n'
                                  'Please review the affected lines in Notepad or a dedicated text editor,\n'
                                  'and consider re-downloading from the original source if needed.'),
        'report_advice_tier2':    ('The file was corrected, but many characters are damaged.\n'
                                  'The corrected output quality may be degraded — please review it carefully.\n'
                                  'Prioritize verifying the integrity of the original file.'),
        'report_advice_tier3':    ('This file had more than 5,000 decoding failures with the encoding shown\n'
                                  'above ("Detected encoding"). This strongly suggests that the file\'s\n'
                                  'actual encoding differs from what was detected. Forcing an incorrect\n'
                                  'encoding could damage the output more than the original file, so it has\n'
                                  'been automatically excluded to protect the original.\n\n'
                                  'Recommended action:\n'
                                  '- Review this file individually in Text Fixer.\n'
                                  '- Check if the file might be in a different encoding (UTF-8, Shift-JIS, etc.).'),
        'tf_err_fix':      'An error occurred',
        'tf_err_save':     'Cannot save',
        'tf_dlg_nofile':   'File Not Found',
        'tf_dlg_noperm':   'Access Error',
        'tf_dlg_ioerr':    'File Error',
        'tf_dlg_encerr':   'Encoding Error',
        'tf_highlight':    '🟡 Yellow = merged  🟠 Orange = blank removed',
        'tf_drop1': 'Drag a TXT file here or use the Open File button',
        'tf_drop2': 'TXT (*.txt) supported',
        'tf_drop_hover': 'Drop to load the file!',
        'open_folder_tooltip': 'Open Folder',
        'theme_lavender': 'Lavender',
        'theme_sakura': 'Sakura',
        'theme_honey': 'Honey',
        'theme_sand': 'Sand',
        'theme_ocean': 'Ocean',
        'theme_mint': 'Mint',
        'theme_choco': 'Antique Bronze',
        'theme_dark': 'Dark',
        'theme_auto': 'Auto (Default)',
        'theme_light': 'White',
        'merge_ext_supported': 'supported',
        'batch_file_ext_ph': 'e.g. jpg, png, gif',
        'batch_file_fmt_pattern': '{folder}{sep}{number}.{ext}',
        'batch_file_fmt_label': 'Output Format',
        'conv_drop_epub_fmt': 'EPUB (*.epub) format supported',
        'conv_drop_txt_fmt': 'TXT (*.txt) format supported',
        'batch_del_all': 'Delete All',
        'batch_click_preview': '← Click Preview',
        'batch_parent_folder': '  (parent folder — not renamed)',
        'batch_folder_label': '  (folder)',
        'batch_confirm_items': 'items will be renamed',
        'batch_done_items': 'items renamed',
        'dlg_rename_partial_note': 'Failed items were not changed and are excluded from undo.',
        'sq_suffix_ph': 'e.g. ep',
        'sq_prefix_ph': 'e.g. ch_',
        'sm_suffix_ph': 'e.g. ep',
        'sm_prefix_ph': 'e.g. ch_',
        'batch_count_file': '{g} groups / {f} files',
        'batch_count_folder': '{g} groups / {f} folders',
        'batch_drop2_p': 'Multiple folders supported',
        'batch_drop1_p': 'Drag folder → rename files',
        'batch_drop2_f': 'Multiple folders supported',
        'batch_drop1_f': 'Drag parent folder → rename subfolders',
        'tag_drop2': 'Click to open folder selection',
        'tag_drop1': 'Drag files or folders here',
        'conv_file_count': '{n} files',
        'conv_drop_epub': 'Drag EPUB files here or use the Add Files button',
        'conv_drop_txt': 'Drag TXT files here or use the Add Files button',
        'merge_sel_multi': '{n} files selected: {names}{more}',
        'merge_sel_one': 'Selected: {name}',
        'merge_stats': '{n} files | {lines} lines total',
        'merge_drop': 'Drag files or folders here',
        'dlg_rename_confirm': 'Rename Confirmation',
        'dlg_rename_done': 'Done',
        'dlg_rename_partial': 'Partial Failure',
        'crash_title': 'Unexpected Error',
        'crash_main': 'An error occurred and the program will exit.',
        'crash_log_at': 'Log saved at:',
        'crash_open_log': 'Open Log Folder',
        'already_running_title': 'Already Running',
        'already_running_main': 'File Nexus Suite is already running.',
        'already_running_sub': 'Please check the existing window.',
        'rename_skip_dup_in_batch': 'Duplicate destination within batch',
        'rename_skip_dest_exists': 'Destination file already exists',
        'lib_required_msg': 'The {lib} library is required.\npip install {lib}',
        'dlg_info': 'Info',
        'help_window_title': '💡  Help — File Nexus Suite v{ver}',
        'help_sidebar_title': '💡  Help',
        'help_section_intro': 'About'},
 'ja': {'app_subtitle': '統合ファイルツール',
        'debug_log': 'デバッグログ',
        'btn_clear': 'クリア',
        'btn_add_file': 'ファイル追加',
        'btn_add_folder': 'フォルダ追加',
        'btn_del_sel': '選択削除',
        'btn_del_all': '全削除',
        'btn_up': '上へ',
        'btn_down': '下へ',
        'btn_close': '閉じる',
        'btn_apply': '適用',
        'btn_reset': '初期値',
        'btn_reset_all': '全ショートカットをリセット',
        'merge_save_settings': '// 保存設定',
        'merge_save_enc': '保存エンコード:',
        'merge_save_path': '保存先:',
        'merge_path_none': '保存先が指定されていません',
        'merge_path_pick': 'パスを指定',
        'merge_path_reset': 'リセット',
        'merge_sep': 'ファイル区切りを挿入',
        'merge_btn': '結合して保存',
        'merge_status_ready': '準備完了',
        'btn_undo': '元に戻す',
        'btn_abort': '中断',
        'merge_sel_none': '選択中: なし',
        'merge_open_explorer': 'エクスプローラーで開く',
        'conv_sub_txt2epub': 'TXT → EPUB',
        'conv_sub_epub2txt': 'EPUB → TXT',
        'conv_out_folder': '// 出力フォルダ',
        'conv_out_ph': '空欄 = 入力ファイルと同じ場所に保存',
        'conv_btn_pick': 'フォルダ指定',
        'conv_btn_start': '変換開始',
        'conv_btn_converting': '⏳ 変換中…',
        'conv_opt_epub2txt': '⚙  変換オプション  (EPUB → TXT)',
        'conv_chk_sep': '章区切りを追加',
        'conv_chk_title': '章タイトルを含める',
        'conv_chk_trim': '連続空行を整理',
        'conv_save_enc': '保存エンコード:',
        'tc_title_placeholder': '無題',
        'tc_author_placeholder': '不明',
        'conv_meta': '📖  書籍情報  (TXT → EPUB)',
        'conv_book_title': 'タイトル',
        'conv_author': '著者',
        'conv_lang': '言語:',
        'conv_chapter_mode': '章分割方法:',
        'conv_ch0': '区切り線基準 (===, ---, ★★★ など)',
        'conv_ch1': '3行以上の空行基準',
        'conv_ch2': '全体を1章として',
        'conv_status_start': 'ファイルを追加して変換を開始してください。',
        'conv_file_list': '// ファイルリスト',
        'tag_sub_remove': 'タグ削除',
        'tag_sub_add': 'タグ追加',
        'tag_sub_depad': '先頭0を削除',
        'tag_col_filename': 'ファイル名',
        'tag_col_path': 'パス',
        'tag_filter': '// フィルター設定',
        'tag_ext_label': '対象拡張子',
        'tag_ext_hint': 'カンマ区切り',
        'tag_cb_recursive': 'サブフォルダを含む',
        'tag_cb_allext': '全拡張子対象',
        'tag_rm_pos': '削除位置',
        'tag_rm_tag': '対象タグ',
        'tag_rm_tag_ph': '空欄 = すべての[タグ]を削除',
        'tag_rm_front': '前のみ',
        'tag_rm_back': '後のみ',
        'tag_rm_both': '前後両方',
        'tag_add_fmt': 'タグ形式',
        'tag_add_fmt_hint': '例:  [タグ]  @タグ  #タグ',
        'tag_add_val': '追加するタグ',
        'tag_add_val_ph': 'カンマで複数入力',
        'tag_add_pos': 'タグ位置',
        'tag_add_front': 'ファイル名の前',
        'tag_add_back': 'ファイル名の後',
        'tag_add_skip': 'タグ既存時はスキップ',
        'tag_add_replace': '既存タグを新タグに置換',
        'tag_add_space_after': 'タグの後にスペース',
        'tag_add_space_before': 'タグの前にスペース',
        'tag_col_folder': 'フォルダ',
        'tag_col_orig': '元ファイル名',
        'tag_col_new': '変更後ファイル名',
        'tag_btn_apply_rm': 'タグ削除を適用',
        'tag_btn_apply_add': 'タグ追加を適用',
        'tag_btn_apply_depad': '先頭0削除 適用',
        'tag_status_start': 'ファイルを追加してプレビューをクリックしてください。',
        'tag_count_total':  '合計 {n}個',
        'tag_status_found': '{n}個のファイルのタグを削除できます。',
        'tag_status_found_add': '{n}個のファイルにタグを追加できます。',
        'tag_status_found_depad': '{n}個のファイルの先頭ゼロを削除できます。',
        'tag_no_change':    '変更するファイルがありません。',
        'tag_skip_count':   '{n}個スキップ',
        'tag_apply_confirm': '合計{n}個のファイル名を変更します。\n続けますか？',
        'tag_apply_done':   '{n}個のファイルの{label}が完了しました。',
        'batch_sub_folder': '📁  フォルダ名変更',
        'batch_sub_file': '📄  ファイル名変更',
        'batch_btn_folder_pick': 'フォルダ選択',
        'batch_btn_file_pick': 'フォルダ選択',
        'batch_col_folder': 'フォルダ名',
        'batch_col_arrow': '▶',
        'batch_col_new': '変更後の名前',
        'batch_col_file': '元のファイル名',
        'batch_col_file_new': '変更後ファイル名',
        'batch_opt_smart': 'スマート抽出',
        'batch_opt_seq': '連番',
        'batch_smart_pfx': '// 接頭辞 / 接尾辞',
        'batch_smart_prefix': '接頭辞',
        'batch_smart_suffix': '接尾辞',
        'batch_smart_common': '// 共通接頭辞の処理',
        'batch_smart_auto': '自動検出',
        'batch_smart_manual': '手動指定',
        'batch_smart_none': '削除しない',
        'batch_smart_manual_ph': '削除する接頭辞',
        'batch_seq_reset': '// 番号リセット',
        'batch_seq_global': '全体連続',
        'batch_seq_pergroup': 'グループごとにリセット',
        'batch_seq_start': '// 開始番号',
        'batch_seq_from0': '00から',
        'batch_seq_from1': '01から',
        'batch_seq_digits': '// 桁数',
        'batch_seq_auto': '自動 (推奨)',
        'batch_seq_2d': '2桁固定',
        'batch_seq_3d': '3桁固定',
        'batch_seq_4d': '4桁固定',
        'batch_seq_pfx_lbl': '// 接頭辞 / 接尾辞',
        'batch_seq_name': '// 名前の保持',
        'batch_seq_numonly': '番号のみ',
        'batch_seq_keep': '番号 + 元の名前',
        'batch_seq_sep': '区切り文字',
        'batch_file_pfx': '// 接頭辞',
        'batch_file_pfx_folder': 'フォルダ名を使用 (推奨)',
        'batch_file_pfx_custom': '直接入力',
        'batch_file_pfx_ph': '全フォルダに同じ値を適用',
        'batch_file_sep_start': '// 区切り / 開始番号',
        'batch_file_sep': '区切り文字',
        'batch_file_from0': '0から',
        'batch_file_from1': '1から',
        'batch_file_digits': '// 番号の桁数',
        'batch_file_auto': '自動 (推奨)',
        'batch_file_nopad': 'なし (1,2…)',
        'batch_file_2d': '最小2桁',
        'batch_file_3d': '最小3桁',
        'batch_file_filter': '// ファイルフィルター',
        'batch_file_all': '全ファイル',
        'batch_file_ext': '特定の拡張子のみ',
        'batch_usage_title': '使い方',
        'batch_hint_folder': '<b>使い方</b><br>① 親フォルダをドラッグまたはボタンで選択<br>② 変換方式タブを選択<br>③ <b>プレビュー</b>で結果確認<br>④ '
                             '<b>名前変更実行</b><br><br>📌 親フォルダは<b>変更されません</b><br>📌 サブフォルダのみ変更されます',
        'batch_hint_file': '📌 <b>フォルダ名</b>が接頭辞として使用されます<br>📌 ファイルは名前順で並べ替えて番号付け<br>📌 元の拡張子は保持されます<br>📌 '
                           '隠しファイル(.*)は除外されます',
        'settings_title': '設定',
        'settings_nav_theme': 'テーマ',
        'settings_nav_shortcuts': 'ショートカット',
        'settings_nav_language': '一般設定',
        'settings_theme_title': 'カラーモード',
        'settings_theme_hint': 'ダブルクリックで即時適用。',
        'settings_output_dir': '出力フォルダ',
        'settings_sc_title': 'キーボードショートカット',
        'settings_sc_desc': 'ボタンをクリックしてからキーを押してください。ESCでキャンセル。',
        'settings_sc_action': '操作',
        'settings_sc_key': 'ショートカット',
        'settings_sc_note': '💡  ショートカットは適用ボタンを押すと反映されます。',
        'settings_lang_title': '言語設定',
        'settings_lang_desc': 'UI言語を選択してください。適用ボタンで反映されます。',
        'settings_applied': '✅  設定を適用しました。',
        'dlg_ok': '確認',
        'dlg_yes': 'はい',
        'dlg_no': 'いいえ',
        'rename_do': '変更する',
        'rename_cancel': 'キャンセル',
        'rename_no_preview': '先にプレビューを実行してください。',
        'rename_collision': '名前の競合',
        'dlg_warning':   '警告',
        'dlg_done':      '完了',
        'dlg_done_err':  '完了（一部エラー）',
        'dlg_undo':      '元に戻す',
        'dlg_undo_fail': '元に戻す失敗',
        'dlg_save_err':  '保存エラー',
        'dlg_confirm_title': '確認',
        'conv_unsupported': 'サポートされていないファイル形式',
        'conv_no_outdir':   '先に出力フォルダを指定してください。',
        'conv_no_files_msg':'先にファイルを追加してください。',
        'conv_outdir_miss': '出力フォルダが存在しません。',
        'tag_no_files_msg': 'ファイルが追加されていません。',
        'tag_no_tag_msg':   '追加するタグを入力してください。',
        'merge_clr_confirm':'リストのすべてのファイルを削除しますか？',
        'merge_undo_done':  '統合ファイルを削除しました。',
        'merge_undo_miss':  'ファイルが見つかりません。',
        'first_run_title':  'ようこそ File Nexus Suite へ！',
        'first_run_desc':   'File Nexus Suiteはプログラムのフォルダに以下のファイルとフォルダを自動生成します。',
        'first_run_item_json':   '設定（テーマ・言語・ショートカット等）を保存する構成ファイル',
        'first_run_item_output': 'Text Converter・Bulk Fixerのデフォルト出力フォルダ',
        'first_run_item_log':    'crash_*.log  エラー時に自動生成されるクラッシュログ（最新3件保持）',
        'first_run_tip':    '必要に応じて削除可能です。次回起動時に自動で再生成されます。',
        'first_run_item_internal': '_internal/ フォルダはプログラムの必須ファイルです。削除すると起動できなくなります。',
        'close_busy_title':  '処理中',
        'close_busy_msg':    '処理が進行中です。今終了するとデータが失われる可能性があります。\n\n終了しますか？',
        'close_busy_exit':   '終了',
        'close_busy_cancel': 'キャンセル',
        'first_run_ui_title':  'File Nexus Suite UI ガイド',
        'first_run_ui_help':   '右上の 💡 ボタンをクリックすると、各タブの詳しい使い方を確認できます。',
        'first_run_ui_batch':  'Batch Renamer の右パネル上部にある // 使い方 ▼ をクリックするとガイドが展開されます。',
        'first_run_tabs_title': 'タブ機能のご案内',
        'first_run_tab_merger': '複数のファイルを一つのテキストに結合',
        'first_run_tab_converter': 'TXT ↔ EPUBファイルを相互変換',
        'first_run_tab_tag': 'ファイル名の[タグ]を一括追加・削除',
        'first_run_tab_batch': 'フォルダ・ファイル名をルールに従って一括変更',
        'first_run_tab_fixer': '単一TXTファイルの改行を修正',
        'first_run_tab_bulk': '複数TXTファイルの改行を一括修正',
        'dlg_error_title': 'エラー',
        'rename_no_pairs':   '変更する名前がありません。',
        'rename_explorer_warn': '⚠  対象フォルダがエクスプローラーで開かれている場合、アクセスエラーが発生することがあります。\n名前変更前にエクスプローラーを閉じるか、別の場所に移動してください。',
        'rename_no_subfolders': 'サブフォルダが見つかりません。',
        'rename_no_files':   'ファイルが見つかりません。',
        'merge_no_support':  'フォルダにサポートファイルが見つかりません。\nサポート: txt · md · csv · docx · pdf · xlsx · hwpx 等',
        'merge_hwp_legacy_title': 'HWP (旧) ファイルはサポートされていません',
        'merge_hwp_legacy_msg':   '{n} 個の旧 HWP ファイルが検出されたため追加されませんでした。\n\nハンコムオフィスで <b>名前を付けて保存 → HWPX</b> に変換してから再度お試しください。\n\nText Merger は HWPX (KS X 6101 OWPML 標準) 形式のみをサポートしています。',
        'merge_no_files':   '統合するファイルがありません。',
        'sc_tab_merger': 'Text Mergerに切替',
        'sc_tab_converter': 'Text Converterに切替',
        'sc_tab_tag': 'Tag Editorに切替',
        'sc_tab_batch': 'Batch Renamerに切替',
        'sc_tab_fixer': 'Text Fixerに切替',
        'sc_tab_bulk':  'Bulk Fixerに切替',
        'batch_btn_rename': '名前変更実行',
        'btn_preview': 'プレビュー',
        'sq_suffix_ph2': '例: _final',
        'sq_prefix_ph2': '例: chapter_',
        'settings_tooltip': '設定',
        'settings_nav_license': 'ライセンス',
        'license_summary': 'MITライセンスで配布 · 使用・改変・再配布・販売はすべて自由 · 著作権表示の保持が必要',
        'tf_open':         'ファイルを開く',
        'tf_run':          '修正実行',
        'tf_copy':         'コピー',
        'tf_save':         '保存',
        'tf_save_fixed':   '元の場所に[Fixed]タグ付きで保存',
        'tf_save_as':      '名前を付けて保存…',
        'tf_clear':        'クリア',
        'tf_opt_mid':      '段落内の改行を結合（空行基準）',
        'tf_opt_sep':      '文ごとに空行を挿入',
        'tf_opt_auto':     '自動段落分割 — 最大',
        'tf_opt_chars':    '文字',
        'tf_opt_blank':    '過剰な空行を削減 — 最大',
        'tf_opt_line':     '行',
        'tf_lang_mode':    '結合モード',
        'tf_preset_label':  'プリセット',
        'tf_preset_doc':    '一般文書',
        'tf_preset_novel':  '本・小説',
        'tf_lang_auto':    '自動',
        'tf_lang_ko':      '韓国語·その他',
        'tf_lang_en':      'English',
        'tf_grp_input':    '// 元のテキスト',
        'tf_grp_output':   '// 修正済みテキスト',
        'tf_ph_input_edit': 'ここに直接テキストを貼り付けてください...',
        'tf_ph_output':    '修正結果がここに表示されます...',
        'tf_stat_mid':     '結合行: -',
        'tf_stat_mid_n':   '結合行: {n}件',
        'tf_stat_blank':   '空行削減: -',
        'tf_stat_blank_n': '空行削減: {n}件',
        'tf_stat_orig':    '元の行数: -',
        'tf_stat_orig_n':  '元の行数: {n}',
        'tf_stat_new':     '修正後の行数: -',
        'tf_stat_new_n':   '修正後: {n}行',
        'tf_search_ph':    'キーワード入力  (Enter: 次へ,  Shift+Enter: 前へ)',
        'tf_search_none':  'なし',
        'tf_search_prev':  '◀ 前へ',
        'tf_search_next':  '次へ ▶',
        'tf_diff_prev':    '◀ 前へ',
        'tf_diff_next':    '次へ ▶',
        'tf_status_ready': 'Text Fixerへようこそ',
        'tf_done':         '🌿  完了 — {mid}件結合, {blank}件空行修正',
        'tf_copied':       '📋  クリップボードにコピーしました',
        'tf_saved':        '💾  保存完了: {name}',
        'tf_cleared':      'クリアしました',
        'bulk_file_list':  '// ファイルリスト',
        'bulk_drop_txt':   'ファイルまたはフォルダをドラッグしてください',
        'bulk_drop_fmt':   'TXT (*.txt) 形式対応',
        'bulk_options':    '// 修正オプション',
        'bulk_preview':    '// プレビュー',
        'bulk_preview_ph': 'ファイルを選択するとプレビューが表示されます',
        'bulk_save_mode':  '// 保存設定',
        'bulk_save_desc':   '[Fixed]タグを先頭に付けて保存します。出力フォルダを指定しない場合、元ファイルと同じ場所に保存されます。',
        'bulk_keep_structure': 'フォルダ構造を維持（出力フォルダ指定時）',
        'bulk_out_ph':     '空欄 = 元ファイルと同じ場所に保存',
        'bulk_run':        '一括修正開始',
        'bulk_running':    '⏳ 処理中…',
        'bulk_status_ready': 'ファイルを追加して一括修正を開始してください。',
        'bulk_status_done':  '✔  完了 — {n}個のファイルを処理しました',
        'bulk_status_err':   '⚠  エラー: {msg}',
        'conv_status_done':  '✅ 完了!',
        'conv_status_fail':  '❌ 変換失敗',
        'tf_undo_done':      '元に戻しました — 元のテキストを復元しました',
        'merge_status_add':  '{n}個のファイルを追加しました (エンコード自動検出)',
        'merge_status_del':  '{n}個のファイルを削除しました',
        'merge_status_clr':  'すべて削除しました',
        'merge_path_set':    '保存先を設定しました: {path}',
        'merge_path_reset_done': '保存先をリセットしました',
        'merge_reading':     '📂  ファイルを読み込み中...',
        'merge_save_done':   '保存完了 ({enc}): {path}',
        'merge_save_err':    '❌ エラーが発生しました',
        'merge_enc_warn_title': '⚠ エンコード互換性の警告',
        'merge_enc_warn_msg':   '選択された保存エンコード <b>{enc}</b> では一部の文字を表現できません。<br><br>• 失われる文字の種類: 約 <b>{kinds}種</b><br>• 影響を受ける文字数: 約 <b>{total}文字</b> (全体の <b>{pct}%</b>)<br>• サンプル: <code>{samples}</code><br><br>続行すると該当文字は <code>?</code> に置き換えられて保存されます。<br><br>それでも保存しますか？',
        # v1.0.5: Text Merger 保存エンコード ドロップダウン 用途ラベル + 1行ヒント
        'merge_enc_utf8':      'UTF-8',
        'merge_enc_utf8_bom':  'UTF-8-BOM (Excel 互換)',
        'merge_enc_euckr':     'EUC-KR (韓国語)',
        'merge_enc_cp949':     'CP949 (韓国語 Windows)',
        'merge_enc_utf16':     'UTF-16',
        'merge_enc_shiftjis':  'Shift-JIS (日本語)',
        'merge_enc_gbk':       'GBK (簡体字中国語)',
        'merge_enc_big5':      'Big5 (繁体字中国語)',
        'merge_enc_hint':      'わからない場合は UTF-8 を選択してください',
        'merge_enc_recommend': '💡 推奨: {enc}',
        'merge_enc_recommend_apply': '適用',
        'merge_low_conf_hint':  'ℹ chardet の元の信頼度が低く表示されても、検出されたエンコードは正確な場合があります（特にCJKエンコード）。',
        'tag_file_count':    '{n}個のファイル',
        'sc_none':           'なし',
        'sc_press':          'キーを入力…',
        'bulk_file_count': '{n}個のファイル',
        'bulk_err_nofiles': '処理するファイルがありません。',
        'bulk_no_txt':      'フォルダにTXTファイルが見つかりません。',
        'bulk_scanning':    'スキャン中... {n}件見つかりました',
        'tf_running':      '✨  修正中...',
        'tf_err_nofile':   'ファイルが見つかりません',
        'tf_err_perm':     '読み取り権限がありません',
        'tf_err_enc':      'サポートされているエンコーディングでファイルを読めません',
        'tf_warn_partial_enc': '⚠ 一部文字のエンコーディングが破損しています。\n\nファイル: {fname}\n使用エンコーディング: {enc}\n置換された文字数: {n} 文字\n\nファイルは読み込まれましたが、破損箇所には置換文字 (�) が表示されます。\n元のファイルが破損していないか確認してください。',
        # v1.0.6 Phase 2-a: Bulk Fixer 完了ダイアログ (4分類)
        'bulk_done_title':   '修正完了',
        'bulk_done_ok':      '正常処理: {n}件',
        'bulk_done_warn':    '注意処理: {n}件 (エンコーディングレポート生成済み)',
        'bulk_done_skip':    'スキップ: {n}件 (Text Fixer での個別確認を推奨)',
        'bulk_done_fail':    '失敗: {n}件 (デバッグログを確認)',
        'bulk_status_skip':  'スキップ',
        # v1.0.6 Phase 2-a: エンコーディングレポートテンプレート (テキストファイルとして保存)
        'report_header':          'File Nexus Suite — エンコーディング変換レポート',
        'report_file':            'ファイル',
        'report_path':            'パス',
        'report_size':            'ファイルサイズ',
        'report_enc':             '検出エンコーディング',
        'report_fail_count':      'エンコーディング失敗数',
        'report_action':          '処理結果',
        'report_action_processed':'修正完了',
        'report_action_skipped':  '処理をスキップ (原本保護)',
        'report_time':            'レポート生成時刻',
        'report_line_col':        'Line {line}, Column {col}',
        'report_bytes':           '元バイト',
        'report_context':         '周囲のテキスト',
        'report_summary_title':   '要約統計',
        'report_total_failures':  '総失敗文字数',
        'report_truncated':       '追跡省略 (詳細記録は最大5,000件まで)',
        'report_advice_title':    '推奨対応',
        'report_advice_tier1':    ('ファイルは正常に修正されましたが、一部の文字が破損しています。\n'
                                  '該当行をメモ帳または専用テキストエディタで確認し、\n'
                                  '必要に応じて元の出典から再ダウンロードすることをお勧めします。'),
        'report_advice_tier2':    ('ファイルは修正されましたが、多数の文字が破損しています。\n'
                                  '修正結果の品質が低下している可能性があるため、必ず確認してください。\n'
                                  'まず元ファイルの状態を優先的に確認してください。'),
        'report_advice_tier3':    ('このファイルは、上記「検出エンコーディング」で 5,000 件以上の\n'
                                  'デコード失敗が発生しました。\n'
                                  'これはファイルの実際のエンコーディングが検出されたものと異なる\n'
                                  '可能性が非常に高いことを意味します。誤ったエンコーディングでの\n'
                                  '強制処理は原本より悪い結果を生む可能性があるため、原本保護のため\n'
                                  '自動的に除外されました。\n\n'
                                  '推奨対応:\n'
                                  '- Text Fixer でこのファイルを個別に確認してください。\n'
                                  '- 元ファイルが他のエンコーディング (UTF-8、Shift-JIS など) である可能性を確認してください。'),
        'tf_err_fix':      'エラーが発生しました',
        'tf_err_save':     '保存できません',
        'tf_dlg_nofile':   'ファイルなし',
        'tf_dlg_noperm':   'アクセスエラー',
        'tf_dlg_ioerr':    'ファイルエラー',
        'tf_dlg_encerr':   'エンコードエラー',
        'tf_highlight':    '🟡 黄色 = 結合済み  🟠 オレンジ = 空行削除',
        'tf_drop1': 'TXTファイルをドラッグするかファイルを開くボタンを使ってください',
        'tf_drop2': 'TXT (*.txt) 形式対応',
        'tf_drop_hover': 'ドロップしてファイルを読み込む！',
        'open_folder_tooltip': 'フォルダを開く',
        'theme_lavender': 'ラベンダー',
        'theme_sakura': '桜',
        'theme_honey': 'ハニー',
        'theme_sand': 'サンド',
        'theme_ocean': 'オーシャン',
        'theme_mint': 'ミント',
        'theme_choco': 'アンティークブロンズ',
        'theme_dark': 'ダーク',
        'theme_auto': '自動（標準）',
        'theme_light': 'ホワイト',
        'merge_ext_supported': '形式対応',
        'batch_file_ext_ph': '例: jpg, png, gif',
        'batch_file_fmt_pattern': '{フォルダ名}{区切}{番号}.{拡張子}',
        'batch_file_fmt_label': '出力形式',
        'conv_drop_epub_fmt': 'EPUB (*.epub) 形式対応',
        'conv_drop_txt_fmt': 'TXT (*.txt) 形式対応',
        'batch_del_all': '全削除',
        'batch_click_preview': '← プレビューをクリック',
        'batch_parent_folder': '  (親フォルダ — 名前変更なし)',
        'batch_folder_label': '  (フォルダ)',
        'batch_confirm_items': '件の名前を変更します',
        'batch_done_items': '件の名前変更が完了',
        'dlg_rename_partial_note': '失敗した項目は変更されず、元に戻す対象からも除外されます。',
        'sq_suffix_ph': '例: 話',
        'sq_prefix_ph': '例: ch_',
        'sm_suffix_ph': '例: 話',
        'sm_prefix_ph': '例: ch_',
        'batch_count_file': 'グループ {g}個 / ファイル {f}個',
        'batch_count_folder': 'グループ {g}個 / フォルダ {f}個',
        'batch_drop2_p': '複数フォルダ同時ドラッグ対応',
        'batch_drop1_p': 'フォルダをドラッグ → ファイル名変更',
        'batch_drop2_f': '複数フォルダ同時ドラッグ対応',
        'batch_drop1_f': '親フォルダをドラッグ → サブフォルダ名変更',
        'tag_drop2': 'クリックでフォルダ選択ウィンドウを開きます',
        'tag_drop1': 'ファイルまたはフォルダをドラッグしてください',
        'conv_file_count': 'ファイル {n}個',
        'conv_drop_epub': 'EPUBファイルをドラッグするか、ファイル追加ボタンを使用してください',
        'conv_drop_txt': 'TXTファイルをドラッグするか、ファイル追加ボタンを使用してください',
        'merge_sel_multi': '{n}個選択中: {names}{more}',
        'merge_sel_one': '選択中: {name}',
        'merge_stats': 'ファイル {n}個 | 合計 {lines}行',
        'merge_drop': 'ファイルまたはフォルダをドラッグしてください',
        'dlg_rename_confirm': '名前変更の確認',
        'dlg_rename_done': '完了',
        'dlg_rename_partial': '一部失敗',
        'crash_title': '予期しないエラー',
        'crash_main': 'エラーが発生しました。プログラムを終了します。',
        'crash_log_at': 'ログ保存先:',
        'crash_open_log': 'ログフォルダを開く',
        'already_running_title': '起動中',
        'already_running_main': 'File Nexus Suite はすでに起動しています。',
        'already_running_sub': '既存のウィンドウをご確認ください。',
        'rename_skip_dup_in_batch': 'バッチ内で宛先が重複',
        'rename_skip_dest_exists': '宛先ファイルが既に存在',
        'lib_required_msg': '{lib} ライブラリが必要です。\npip install {lib}',
        'dlg_info': 'お知らせ',
        'help_window_title': '💡  ヘルプ — File Nexus Suite v{ver}',
        'help_sidebar_title': '💡  ヘルプ',
        'help_section_intro': '概要'},
 'zh_cn': {'app_subtitle': '综合文件工具',
           'debug_log': '调试日志',
           'btn_clear': '清空',
           'btn_add_file': '添加文件',
           'btn_add_folder': '添加文件夹',
           'btn_del_sel': '删除选中',
           'btn_del_all': '全部删除',
           'btn_close': '关闭',
           'btn_apply': '应用',
           'btn_reset': '默认',
           'btn_reset_all': '重置所有快捷键',
           'merge_save_settings': '// 保存设置',
           'merge_save_enc': '保存编码:',
           'merge_save_path': '保存路径:',
           'merge_path_none': '未指定保存路径',
           'merge_path_pick': '选择路径',
           'merge_path_reset': '重置',
           'merge_sep': '插入文件分隔符',
           'merge_btn': '合并并保存',
           'merge_status_ready': '就绪',
           'btn_undo': '撤销',
           'btn_abort': '中断',
           'merge_sel_none': '已选: 无',
           'merge_open_explorer': '在资源管理器中打开',
           'conv_sub_txt2epub': 'TXT → EPUB',
           'conv_sub_epub2txt': 'EPUB → TXT',
           'conv_out_folder': '// 输出文件夹',
           'conv_out_ph': '留空则保存到源文件位置',
           'conv_btn_pick': '选择文件夹',
           'conv_btn_start': '开始转换',
           'conv_btn_converting': '⏳ 转换中…',
           'conv_opt_epub2txt': '⚙  转换选项  (EPUB → TXT)',
           'conv_chk_sep': '添加章节分隔符',
           'conv_chk_title': '包含章节标题',
           'conv_chk_trim': '整理连续空行',
           'conv_save_enc': '保存编码:',
           'tc_title_placeholder': '无题',
           'conv_meta': '📖  书籍信息  (TXT → EPUB)',
           'conv_book_title': '书名',
           'conv_lang': '语言:',
           'conv_chapter_mode': '章节分割方式:',
           'conv_ch0': '分隔线 (===, ---, ★★★ 等)',
           'conv_ch2': '整体作为单章',
           'conv_status_start': '添加文件后开始转换。',
           'conv_file_list': '// 文件列表',
           'tag_sub_remove': '删除标签',
           'tag_sub_add': '添加标签',
           'tag_sub_depad': '删除前导零',
           'tag_col_filename': '文件名',
           'tag_col_path': '路径',
           'tag_filter': '// 过滤设置',
           'tag_ext_label': '目标扩展名',
           'tag_ext_hint': '逗号分隔',
           'tag_cb_recursive': '包含子文件夹',
           'tag_cb_allext': '所有扩展名',
           'tag_rm_pos': '删除位置',
           'tag_rm_tag': '目标标签',
           'tag_rm_tag_ph': '留空 = 删除所有[标签]',
           'tag_rm_front': '仅前面',
           'tag_rm_back': '仅后面',
           'tag_rm_both': '前后都删',
           'tag_add_fmt': '标签格式',
           'tag_add_fmt_hint': '例:  [标签]  @标签  #标签',
           'tag_add_val': '添加标签',
           'tag_add_val_ph': '逗号分隔多个标签',
           'tag_add_pos': '标签位置',
           'tag_add_front': '文件名前',
           'tag_add_back': '文件名后',
           'tag_add_skip': '已有标签则跳过',
           'tag_add_replace': '替换现有标签',
           'tag_add_space_after': '标签后加空格',
           'tag_add_space_before': '标签前加空格',
           'tag_col_folder': '文件夹',
           'tag_col_orig': '原文件名',
           'tag_col_new': '更改后文件名',
           'tag_btn_apply_rm': '应用删除',
           'tag_btn_apply_add': '应用添加',
           'tag_btn_apply_depad': '应用',
           'tag_status_start': '添加文件后点击预览。',
           'tag_count_total':  '共 {n} 个',
           'tag_status_found': '可以删除 {n} 个文件的标签。',
           'tag_status_found_add': '可以向 {n} 个文件添加标签。',
           'tag_status_found_depad': '可以删除 {n} 个文件的前导零。',
           'tag_no_change':    '没有需要更改的文件。',
           'tag_skip_count':   '已跳过 {n} 个',
           'tag_apply_confirm': '将重命名共 {n} 个文件。\n是否继续？',
           'tag_apply_done':   '{n} 个文件{label}完成。',
           'batch_sub_folder': '📁  重命名文件夹',
           'batch_sub_file': '📄  重命名文件',
           'batch_btn_folder_pick': '选择文件夹',
           'batch_btn_file_pick': '选择文件夹',
           'batch_col_folder': '文件夹名',
           'batch_col_new': '新名称',
           'batch_col_file': '原文件名',
           'batch_col_file_new': '新文件名',
           'batch_opt_smart': '智能提取',
           'batch_opt_seq': '顺序编号',
           'batch_smart_pfx': '// 前缀 / 后缀',
           'batch_smart_prefix': '前缀',
           'batch_smart_suffix': '后缀',
           'batch_smart_common': '// 公共前缀处理',
           'batch_smart_auto': '自动检测',
           'batch_smart_manual': '手动指定',
           'batch_smart_none': '不删除',
           'batch_smart_manual_ph': '要删除的前缀',
           'batch_seq_reset': '// 编号重置',
           'batch_seq_global': '连续编号',
           'batch_seq_pergroup': '每组重置',
           'batch_seq_start': '// 起始编号',
           'batch_seq_from0': '从00开始',
           'batch_seq_from1': '从01开始',
           'batch_seq_digits': '// 位数',
           'batch_seq_auto': '自动 (推荐)',
           'batch_seq_pfx_lbl': '// 前缀 / 后缀',
           'batch_seq_name': '// 名称保留',
           'batch_seq_numonly': '仅编号',
           'batch_seq_keep': '编号+原名',
           'batch_file_pfx': '// 前缀',
           'batch_file_pfx_folder': '使用文件夹名 (推荐)',
           'batch_file_pfx_custom': '手动输入',
           'batch_file_pfx_ph': '应用到所有文件夹',
           'batch_file_sep_start': '// 分隔符 / 起始编号',
           'batch_file_from0': '从0开始',
           'batch_file_from1': '从1开始',
           'batch_file_digits': '// 编号位数',
           'batch_file_auto': '自动 (推荐)',
           'batch_file_nopad': '无 (1,2…)',
           'batch_file_filter': '// 文件过滤',
           'batch_file_all': '所有文件',
           'batch_file_ext': '特定扩展名',
           'batch_usage_title': '使用方法',
           'batch_hint_folder': '<b>使用方法</b><br>① 拖拽父文件夹或点击按钮选择<br>② 选择重命名方式<br>③ 点击<b>预览</b>查看结果<br>④ '
                                '<b>执行重命名</b><br><br>📌 父文件夹<b>不会被重命名</b><br>📌 仅重命名子文件夹',
           'batch_hint_file': '📌 <b>文件夹名</b>作为前缀使用<br>📌 文件按名称排序后编号<br>📌 保留原始扩展名<br>📌 隐藏文件（.*）自动排除',
           'settings_title': '设置',
           'settings_nav_theme': '主题',
           'settings_nav_shortcuts': '快捷键',
           'settings_nav_language': '常规设置',
           'settings_theme_title': '颜色模式',
           'settings_theme_hint': '双击即时应用。',
           'settings_output_dir': '输出文件夹',
           'settings_sc_title': '键盘快捷键',
           'settings_sc_desc': '点击按钮后按下所需按键。按ESC取消。',
           'settings_sc_key': '快捷键',
           'settings_sc_note': '💡  点击应用按钮后快捷键即刻生效。',
           'settings_lang_title': '语言设置',
           'settings_lang_desc': '选择界面语言，点击应用确认。',
           'settings_applied': '✅  设置已应用。',
           'dlg_ok': '确认',
           'dlg_yes': '是',
           'dlg_no': '否',
           'rename_do': '重命名',
           'rename_cancel': '取消',
           'rename_no_preview': '请先执行预览。',
           'rename_collision': '名称冲突',
           'dlg_warning':   '警告',
           'dlg_error_title': '错误',
           'dlg_done_err':  '完成（部分错误）',
           'dlg_undo':      '撤销',
           'dlg_undo_fail': '撤销失败',
           'dlg_save_err':  '保存错误',
           'dlg_confirm_title': '确认',
           'conv_unsupported': '不支持的文件格式',
           'conv_no_outdir':   '请先指定输出文件夹。',
           'conv_no_files_msg':'请先添加文件。',
           'conv_outdir_miss': '输出文件夹不存在。',
           'tag_no_files_msg': '没有添加文件。',
           'tag_no_tag_msg':   '请输入要添加的标签。',
           'merge_clr_confirm':'删除列表中的所有文件？',
           'merge_undo_done':  '已删除合并文件。',
           'merge_undo_miss':  '找不到文件。',
           'first_run_title':  '欢迎使用 File Nexus Suite！',
           'first_run_desc':   'File Nexus Suite会在程序所在目录自动创建以下文件和文件夹。',
           'first_run_item_json':   '保存设置（主题、语言、快捷键等）的配置文件',
           'first_run_item_output': 'Text Converter和Bulk Fixer的默认输出文件夹',
           'first_run_item_log':    'crash_*.log  发生错误时自动生成的崩溃日志（保留最近3个）',
           'first_run_tip':    '如有需要可安全删除，下次启动时将自动重新创建。',
           'close_busy_title':  '任务进行中',
           'close_busy_msg':    '当前有任务正在运行。现在退出可能导致数据丢失。\n\n确定要退出吗？',
           'first_run_item_internal': '_internal/ 文件夹包含程序必要文件，删除后将无法运行。',
           'first_run_ui_help':   '点击右上角的 💡 按钮，可查看各标签页的详细使用说明。',
           'first_run_ui_batch':  '在 Batch Renamer 中，点击右侧面板顶部的 // 使用方法 ▼ 可展开使用指南。',
           'first_run_tabs_title': '功能标签介绍',
           'first_run_tab_merger': '将多个文件合并为一个文本',
           'first_run_tab_converter': 'TXT ↔ EPUB 文件格式互转',
           'first_run_tab_tag': '批量添加或删除文件名中的[标签]',
           'first_run_tab_batch': '按规则批量重命名文件夹和文件',
           'first_run_tab_fixer': '修复单个TXT文件的换行格式',
           'first_run_tab_bulk': '批量修复多个TXT文件的换行格式',
           'rename_no_pairs':   '没有要更改的名称。',
           'rename_explorer_warn': '⚠  若目标文件夹在资源管理器中处于打开状态，可能会出现访问错误。\n重命名前请关闭资源管理器或切换到其他位置。',
           'rename_no_subfolders': '没有找到子文件夹。',
           'rename_no_files':   '没有找到文件。',
           'merge_no_support':  '文件夹中未找到支持的文件。\n支持: txt · md · csv · docx · pdf · xlsx · hwpx 等',
           'merge_hwp_legacy_title': 'HWP (旧版) 文件不受支持',
           'merge_hwp_legacy_msg':   '检测到 {n} 个旧版 HWP 文件，已跳过。\n\n请在韩文 Office 中使用 <b>另存为 → HWPX</b> 转换后再试。\n\nText Merger 仅支持 HWPX (KS X 6101 OWPML 标准) 格式。',
           'merge_no_files':   '没有要合并的文件。',
           'sc_tab_merger': '切换到 Text Merger',
           'sc_tab_converter': '切换到 Text Converter',
           'sc_tab_tag': '切换到 Tag Editor',
           'sc_tab_batch': '切换到 Batch Renamer',
           'sc_tab_fixer': '切换到 Text Fixer',
           'sc_tab_bulk':  '切换到 Bulk Fixer',
           'batch_btn_rename': '执行重命名',
           'btn_preview': '预览',
           'settings_tooltip': '设置',
           'settings_nav_license': '许可证',
           'license_summary': '采用 MIT 许可证 · 可自由使用、修改、再发布、销售 · 须保留版权声明',
           'tf_open':         '打开文件',
           'tf_run':          '执行修复',
           'tf_copy':         '复制',
           'tf_save':         '保存',
           'tf_save_fixed':   '在原位置另存为_fixed.txt',
           'tf_save_as':      '另存为…',
           'tf_opt_mid':      '合并段落内换行（以空行为基准）',
           'tf_opt_sep':      '在句子之间插入空行',
           'tf_opt_auto':     '自动段落分割 — 最多',
           'tf_opt_blank':    '减少过多空行 — 最多',
           'tf_lang_mode':    '合并模式',
           'tf_preset_label':  '预设',
           'tf_preset_doc':    '普通文档',
           'tf_preset_novel':  '书籍/小说',
           'tf_lang_auto':    '自动',
           'tf_lang_ko':      '韩语·其他',
           'tf_grp_input':    '// 原始文本',
           'tf_grp_output':   '// 修复后的文本',
        'tf_ph_input_edit': '在此直接粘贴文本...',
           'tf_ph_output':    '修复结果将显示在此处...',
           'tf_stat_mid':     '合并行数: -',
           'tf_stat_mid_n':   '合并行数: {n}',
           'tf_stat_blank':   '空行缩减: -',
           'tf_stat_blank_n': '空行缩减: {n}',
           'tf_stat_orig':    '原始行数: -',
           'tf_stat_orig_n':  '原始行数: {n}',
           'tf_stat_new':     '修复后行数: -',
           'tf_stat_new_n':   '修复后: {n}行',
           'tf_search_ph':    '输入关键词  (Enter: 下一个,  Shift+Enter: 上一个)',
           'tf_search_none':  '无',
           'tf_search_prev':  '◀ 上一个',
           'tf_search_next':  '下一个 ▶',
           'tf_diff_prev':    '◀ 上一个',
           'tf_diff_next':    '下一个 ▶',
           'tf_status_ready': '欢迎使用 Text Fixer',
           'tf_done':         '🌿  完成 — 合并 {mid} 行，修复空行 {blank} 处',
           'tf_copied':       '📋  已复制到剪贴板',
           'tf_saved':        '💾  保存完成: {name}',
           'bulk_file_list':  '// 文件列表',
           'bulk_drop_txt':   '将文件或文件夹拖到此处',
           'bulk_drop_fmt':   '支持TXT (*.txt) 格式',
           'bulk_options':    '// 修复选项',
           'bulk_preview':    '// 预览',
           'bulk_preview_ph': '选择文件后显示预览',
           'bulk_save_mode':  '// 保存方式',
           'bulk_out_ph':     '留空 = 保存在原文件旁边',
           'bulk_keep_structure': '保留文件夹结构（指定输出文件夹时）',
           'bulk_run':        '开始批量修复',
           'bulk_running':    '⏳ 处理中…',
           'bulk_status_ready': '添加文件后开始批量修复。',
           'bulk_status_done':  '✔  完成 — 已处理{n}个文件',
           'bulk_status_err':   '⚠  错误: {msg}',
           'bulk_file_count': '{n}个文件',
           'bulk_err_nofiles': '没有可处理的文件。',
           'bulk_no_txt':      '在文件夹中找不到TXT文件。',
           'bulk_scanning':    '扫描中... 已找到{n}个',
           'tf_running':      '✨  修复中...',
           'tf_err_nofile':   '找不到文件',
           'tf_err_perm':     '没有读取权限',
           'tf_err_enc':      '无法使用支持的编码读取文件',
           'tf_warn_partial_enc': '⚠ 部分字符的编码已损坏。\n\n文件: {fname}\n使用编码: {enc}\n已替换字符数: {n} 个\n\n文件已加载，但损坏位置将显示替换字符 (�)。\n请确认原始文件未损坏。',
           # v1.0.6 Phase 2-a: Bulk Fixer 完成对话框 (4分类)
           'bulk_done_ok':      '正常处理: {n}个',
           'bulk_done_warn':    '注意处理: {n}个 (已生成编码报告)',
           'bulk_done_skip':    '已跳过: {n}个 (建议在 Text Fixer 中单独审核)',
           'bulk_done_fail':    '失败: {n}个 (请查看调试日志)',
           'bulk_status_skip':  '已跳过',
           # v1.0.6 Phase 2-a: 编码报告模板 (保存为文本文件)
           'report_header':          'File Nexus Suite — 编码转换报告',
           'report_file':            '文件',
           'report_path':            '路径',
           'report_size':            '文件大小',
           'report_enc':             '检测编码',
           'report_fail_count':      '编码失败数',
           'report_action':          '处理结果',
           'report_action_skipped':  '跳过处理 (原文件已保护)',
           'report_time':            '报告生成时间',
           'report_bytes':           '原始字节',
           'report_context':         '周围文本',
           'report_summary_title':   '统计摘要',
           'report_total_failures':  '失败字符总数',
           'report_truncated':       '省略追踪 (详细记录上限 5,000 个)',
           'report_advice_title':    '建议操作',
           'report_advice_tier1':    ('文件已正常校正，但部分字符已损坏。\n'
                                     '请在记事本或专用文本编辑器中确认相关行，\n'
                                     '如有必要，建议从原始来源重新下载。'),
           'report_advice_tier2':    ('文件已校正，但大量字符已损坏。\n'
                                     '校正结果的质量可能已降低，请务必审查。\n'
                                     '请优先确认原始文件的完整性。'),
           'report_advice_tier3':    ('此文件在上述"检测编码"下发生了 5,000 个以上的\n'
                                     '解码失败。\n'
                                     '这强烈表明文件的实际编码与检测到的编码不同。\n'
                                     '强制使用错误编码处理可能导致结果比原文件更损坏，\n'
                                     '因此为保护原始文件，已自动跳过此文件。\n\n'
                                     '建议操作:\n'
                                     '- 在 Text Fixer 中单独审核此文件。\n'
                                     '- 检查此文件是否可能使用其他编码 (UTF-8、Shift-JIS 等)。'),
           'tf_err_fix':      '发生错误',
           'tf_err_save':     '无法保存',
           'tf_dlg_nofile':   '文件不存在',
           'tf_dlg_noperm':   '访问错误',
           'tf_dlg_ioerr':    '文件错误',
           'tf_dlg_encerr':   '编码错误',
           'tf_highlight':    '🟡 黄色 = 已合并  🟠 橙色 = 空行已删除',
           'tf_drop1': '将TXT文件拖到此处或使用打开文件按钮',
           'tf_drop2': '支持 TXT (*.txt) 格式',
           'tf_drop_hover': '放开以加载文件！',
           'open_folder_tooltip': '打开文件夹',
           'theme_sakura': '樱花',
           'theme_sand': '沙漠',
           'theme_ocean': '海洋',
           'theme_mint': '薄荷',
           'theme_choco': '古铜色',
           'theme_auto': '自动（默认）',
           'merge_ext_supported': '支持',
           'batch_file_fmt_pattern': '{文件夹名}{分隔符}{编号}.{扩展名}',
           'batch_file_fmt_label': '输出格式',
           'conv_drop_epub_fmt': '支持 EPUB (*.epub) 格式',
           'conv_drop_txt_fmt': '支持 TXT (*.txt) 格式',
           'batch_del_all': '全部删除',
           'batch_click_preview': '← 点击预览',
           'batch_parent_folder': '  (上级文件夹 — 不重命名)',
           'batch_folder_label': '  (文件夹)',
           'batch_confirm_items': '个项目将被重命名',
           'batch_done_items': '个项目重命名完成',
           'dlg_rename_partial_note': '失败的项目未被更改，且不包含在撤销操作中。',
           'sq_suffix_ph': '例: 话',
           'sm_suffix_ph': '例: 话',
           'batch_count_file': '组 {g}个 / 文件 {f}个',
           'batch_count_folder': '组 {g}个 / 文件夹 {f}个',
           'batch_drop2_p': '支持同时拖动多个文件夹',
           'batch_drop1_p': '拖动文件夹 → 重命名文件',
           'batch_drop2_f': '支持同时拖动多个文件夹',
           'batch_drop1_f': '拖动父文件夹 → 重命名子文件夹',
           'tag_drop2': '点击打开文件夹选择窗口',
           'tag_drop1': '将文件或文件夹拖到此处',
           'conv_file_count': '文件 {n}个',
           'conv_drop_epub': '将EPUB文件拖到此处，或使用添加文件按钮',
           'conv_drop_txt': '将TXT文件拖到此处，或使用添加文件按钮',
           'merge_sel_multi': '已选 {n}个: {names}{more}',
           'merge_sel_one': '已选: {name}',
           'merge_stats': '文件 {n}个 | 共 {lines}行',
           'merge_drop': '将文件或文件夹拖到此处',
           'dlg_rename_confirm': '重命名确认',
           'dlg_rename_partial': '部分失败',
           'bulk_save_desc':  '在文件名前加 [Fixed] 标签保存。如未指定输出文件夹，将保存在原文件相同位置。',
           'conv_status_done':  '✅ 完成!',
           'conv_status_fail':  '❌ 转换失败',
           'tf_undo_done':      '已撤销 — 已恢复原始文本',
           'merge_status_add':  '已添加{n}个文件（自动检测编码）',
           'merge_status_del':  '已删除{n}个文件',
           'merge_status_clr':  '已清空所有文件',
           'merge_path_set':    '已设置保存路径: {path}',
           'merge_path_reset_done': '已重置保存路径',
           'merge_reading':     '📂  正在读取文件...',
           'merge_save_done':   '保存完成 ({enc}): {path}',
           'merge_save_err':    '❌ 发生错误',
           'merge_enc_warn_title': '⚠ 编码兼容性警告',
           'merge_enc_warn_msg':   '所选保存编码 <b>{enc}</b> 无法表示部分字符。<br><br>• 受影响字符种类: 约 <b>{kinds} 种</b><br>• 实际受影响字数: 约 <b>{total} 个</b> (占全文 <b>{pct}%</b>)<br>• 示例: <code>{samples}</code><br><br>如果继续，这些字符将被替换为 <code>?</code>。<br><br>仍要保存吗？',
           # v1.0.5: Text Merger 保存编码下拉框用途说明标签 + 一行提示
           'merge_enc_utf8':      'UTF-8',
           'merge_enc_utf8_bom':  'UTF-8-BOM (Excel 兼容)',
           'merge_enc_euckr':     'EUC-KR (韩语)',
           'merge_enc_cp949':     'CP949 (韩语 Windows)',
           'merge_enc_utf16':     'UTF-16',
           'merge_enc_shiftjis':  'Shift-JIS (日文)',
           'merge_enc_gbk':       'GBK (简体中文)',
           'merge_enc_big5':      'Big5 (繁体中文)',
           'merge_enc_hint':      '不确定时请选择 UTF-8',
           'merge_enc_recommend': '💡 推荐: {enc}',
           'merge_enc_recommend_apply': '应用',
           'merge_low_conf_hint':  'ℹ chardet 原始置信度较低时，检测到的编码仍可能准确（尤其是 CJK 编码）。',
           'tag_file_count':    '{n}个文件',
           'sc_none':           '无',
           'sc_press':          '请按键…',
           'crash_title':       '发生意外错误',
           'crash_main':        '程序发生错误，即将退出。',
           'crash_log_at':      '日志保存位置:',
           'crash_open_log':    '打开日志文件夹',
           'already_running_title': '已在运行',
           'already_running_main':  'File Nexus Suite 已在运行中。',
           'already_running_sub':   '请检查已打开的窗口。',
           'rename_skip_dup_in_batch': '批次内目标重复',
           'rename_skip_dest_exists':  '目标文件已存在',
           'lib_required_msg':  '需要 {lib} 库。\npip install {lib}',
           'dlg_info':          '提示',
           'help_window_title': '💡  帮助 — File Nexus Suite v{ver}',
           'help_sidebar_title':'💡  帮助',
           'help_section_intro':'简介'},
 'zh_tw': {'app_subtitle': '綜合檔案工具',
           'debug_log': '除錯日誌',
           'btn_clear': '清除',
           'btn_add_file': '新增檔案',
           'btn_add_folder': '新增資料夾',
           'btn_del_sel': '刪除選取',
           'btn_del_all': '全部刪除',
           'btn_up': '上移',
           'btn_down': '下移',
           'btn_close': '關閉',
           'btn_apply': '套用',
           'btn_reset': '預設',
           'btn_reset_all': '重設所有快捷鍵',
           'merge_save_settings': '// 儲存設定',
           'merge_save_enc': '儲存編碼:',
           'merge_save_path': '儲存路徑:',
           'merge_path_none': '未指定儲存路徑',
           'merge_path_pick': '選擇路徑',
           'merge_path_reset': '重設',
           'merge_sep': '插入檔案分隔符',
           'merge_btn': '合併並儲存',
           'merge_status_ready': '就緒',
           'btn_undo': '復原',
           'btn_abort': '中斷',
           'merge_sel_none': '已選取: 無',
           'merge_open_explorer': '在檔案總管中開啟',
           'conv_sub_txt2epub': 'TXT → EPUB',
           'conv_sub_epub2txt': 'EPUB → TXT',
           'conv_out_folder': '// 輸出資料夾',
           'conv_out_ph': '留空則儲存到來源檔案位置',
           'conv_btn_pick': '選擇資料夾',
           'conv_btn_start': '開始轉換',
           'conv_btn_converting': '⏳ 轉換中…',
           'conv_opt_epub2txt': '⚙  轉換選項  (EPUB → TXT)',
           'conv_chk_sep': '新增章節分隔符',
           'conv_chk_title': '包含章節標題',
           'conv_chk_trim': '整理連續空行',
           'conv_save_enc': '儲存編碼:',
           'tc_title_placeholder': '無題',
           'tc_author_placeholder': '佚名',
           'conv_meta': '📖  書籍資訊  (TXT → EPUB)',
           'conv_book_title': '書名',
           'conv_author': '作者',
           'conv_lang': '語言:',
           'conv_chapter_mode': '章節分割方式:',
           'conv_ch0': '分隔線 (===, ---, ★★★ 等)',
           'conv_ch1': '3行以上空行',
           'conv_ch2': '整體作為單章',
           'conv_status_start': '新增檔案後開始轉換。',
           'conv_file_list': '// 檔案列表',
           'tag_sub_remove': '移除標籤',
           'tag_sub_add': '新增標籤',
           'tag_sub_depad': '移除前導零',
           'tag_col_filename': '檔案名稱',
           'tag_col_path': '路徑',
           'tag_filter': '// 篩選設定',
           'tag_ext_label': '目標副檔名',
           'tag_ext_hint': '逗號分隔',
           'tag_cb_recursive': '包含子資料夾',
           'tag_cb_allext': '所有副檔名',
           'tag_rm_pos': '移除位置',
           'tag_rm_tag': '目標標籤',
           'tag_rm_tag_ph': '留空 = 移除所有[標籤]',
           'tag_rm_front': '僅前面',
           'tag_rm_back': '僅後面',
           'tag_rm_both': '前後都移除',
           'tag_add_fmt': '標籤格式',
           'tag_add_fmt_hint': '例:  [標籤]  @標籤  #標籤',
           'tag_add_val': '新增標籤',
           'tag_add_val_ph': '逗號分隔多個標籤',
           'tag_add_pos': '標籤位置',
           'tag_add_front': '檔案名稱前',
           'tag_add_back': '檔案名稱後',
           'tag_add_skip': '已有標籤則跳過',
           'tag_add_replace': '替換現有標籤',
           'tag_add_space_after': '標籤後加空格',
           'tag_add_space_before': '標籤前加空格',
           'tag_col_folder': '資料夾',
           'tag_col_orig': '原檔案名稱',
           'tag_col_new': '變更後檔案名稱',
           'tag_btn_apply_rm': '套用移除',
           'tag_btn_apply_add': '套用新增',
           'tag_btn_apply_depad': '套用',
           'tag_status_start': '新增檔案後點擊預覽。',
           'tag_count_total':  '共 {n} 個',
           'tag_status_found': '可移除 {n} 個檔案的標籤。',
           'tag_status_found_add': '可向 {n} 個檔案新增標籤。',
           'tag_status_found_depad': '可移除 {n} 個檔案的前導零。',
           'tag_no_change':    '沒有需要變更的檔案。',
           'tag_skip_count':   '已跳過 {n} 個',
           'tag_apply_confirm': '將重新命名共 {n} 個檔案。\n是否繼續？',
           'tag_apply_done':   '{n} 個檔案{label}完成。',
           'batch_sub_folder': '📁  重新命名資料夾',
           'batch_sub_file': '📄  重新命名檔案',
           'batch_btn_folder_pick': '選擇資料夾',
           'batch_btn_file_pick': '選擇資料夾',
           'batch_col_folder': '資料夾名稱',
           'batch_col_arrow': '▶',
           'batch_col_new': '新名稱',
           'batch_col_file': '原檔案名稱',
           'batch_col_file_new': '新檔案名稱',
           'batch_opt_smart': '智慧提取',
           'batch_opt_seq': '循序編號',
           'batch_smart_pfx': '// 前綴 / 後綴',
           'batch_smart_prefix': '前綴',
           'batch_smart_suffix': '後綴',
           'batch_smart_common': '// 公共前綴處理',
           'batch_smart_auto': '自動偵測',
           'batch_smart_manual': '手動指定',
           'batch_smart_none': '不刪除',
           'batch_smart_manual_ph': '要刪除的前綴',
           'batch_seq_reset': '// 編號重置',
           'batch_seq_global': '連續編號',
           'batch_seq_pergroup': '每組重置',
           'batch_seq_start': '// 起始編號',
           'batch_seq_from0': '從00開始',
           'batch_seq_from1': '從01開始',
           'batch_seq_digits': '// 位數',
           'batch_seq_auto': '自動 (推薦)',
           'batch_seq_2d': '固定2位',
           'batch_seq_3d': '固定3位',
           'batch_seq_4d': '固定4位',
           'batch_seq_pfx_lbl': '// 前綴 / 後綴',
           'batch_seq_name': '// 名稱保留',
           'batch_seq_numonly': '僅編號',
           'batch_seq_keep': '編號+原名',
           'batch_seq_sep': '分隔符',
           'batch_file_pfx': '// 前綴',
           'batch_file_pfx_folder': '使用資料夾名稱 (推薦)',
           'batch_file_pfx_custom': '手動輸入',
           'batch_file_pfx_ph': '套用到所有資料夾',
           'batch_file_sep_start': '// 分隔符 / 起始編號',
           'batch_file_sep': '分隔符',
           'batch_file_from0': '從0開始',
           'batch_file_from1': '從1開始',
           'batch_file_digits': '// 編號位數',
           'batch_file_auto': '自動 (推薦)',
           'batch_file_nopad': '無 (1,2…)',
           'batch_file_2d': '最少2位',
           'batch_file_3d': '最少3位',
           'batch_file_filter': '// 檔案篩選',
           'batch_file_all': '所有檔案',
           'batch_file_ext': '特定副檔名',
           'batch_usage_title': '使用方式',
           'batch_hint_folder': '<b>使用方式</b><br>① 拖曳上層資料夾或點擊按鈕選擇<br>② 選擇重新命名方式<br>③ 點擊<b>預覽</b>查看結果<br>④ '
                                '<b>執行重新命名</b><br><br>📌 上層資料夾<b>不會被重新命名</b><br>📌 僅重新命名子資料夾',
           'batch_hint_file': '📌 <b>資料夾名稱</b>作為前綴使用<br>📌 檔案依名稱排序後編號<br>📌 保留原始副檔名<br>📌 隱藏檔案（.*）自動排除',
           'settings_title': '設定',
           'settings_nav_theme': '主題',
           'settings_nav_shortcuts': '快捷鍵',
           'settings_nav_language': '一般設定',
           'settings_theme_title': '色彩模式',
           'settings_theme_hint': '雙擊即時套用。',
           'settings_output_dir': '輸出資料夾',
           'settings_sc_title': '鍵盤快捷鍵',
           'settings_sc_desc': '點擊按鈕後按下所需按鍵。按ESC取消。',
           'settings_sc_action': '操作',
           'settings_sc_key': '快捷鍵',
           'settings_sc_note': '💡  點擊套用按鈕後快捷鍵即刻生效。',
           'settings_lang_title': '語言設定',
           'settings_lang_desc': '選擇介面語言，點擊套用確認。',
           'settings_applied': '✅  設定已套用。',
           'dlg_ok': '確認',
           'dlg_yes': '是',
           'dlg_no': '否',
           'rename_do': '重新命名',
           'rename_cancel': '取消',
           'rename_no_preview': '請先執行預覽。',
           'rename_collision': '名稱衝突',
           'dlg_warning':   '警告',
           'dlg_error_title': '錯誤',
           'dlg_done':      '完成',
           'dlg_done_err':  '完成（部分錯誤）',
           'dlg_undo':      '復原',
           'dlg_undo_fail': '復原失敗',
           'dlg_save_err':  '儲存錯誤',
           'dlg_confirm_title': '確認',
           'conv_unsupported': '不支援的檔案格式',
           'conv_no_outdir':   '請先指定輸出資料夾。',
           'conv_no_files_msg':'請先新增檔案。',
           'conv_outdir_miss': '輸出資料夾不存在。',
           'tag_no_files_msg': '沒有新增檔案。',
           'tag_no_tag_msg':   '請輸入要新增的標籤。',
           'merge_clr_confirm':'刪除清單中的所有檔案？',
           'merge_undo_done':  '已刪除合併檔案。',
           'merge_undo_miss':  '找不到檔案。',
           'first_run_title':  '歡迎使用 File Nexus Suite！',
           'first_run_desc':   'File Nexus Suite會在程式所在目錄自動建立以下檔案和資料夾。',
           'first_run_item_json':   '儲存設定（主題、語言、快捷鍵等）的設定檔',
           'first_run_item_output': 'Text Converter和Bulk Fixer的預設輸出資料夾',
           'first_run_item_log':    'crash_*.log  發生錯誤時自動生成的當機日誌（保留最近3個）',
           'first_run_tip':    '如有需要可安全刪除，下次啟動時將自動重新建立。',
           'close_busy_title':  '任務進行中',
           'close_busy_msg':    '目前有任務正在執行。現在退出可能導致資料遺失。\n\n確定要退出嗎？',
           'close_busy_exit':   '退出',
           'close_busy_cancel': '取消',
           'first_run_item_internal': '_internal/ 資料夾包含程式必要檔案，刪除後將無法執行。',
           'first_run_ui_title':  'File Nexus Suite UI 指南',
           'first_run_ui_help':   '點擊右上角的 💡 按鈕，可查看各分頁的詳細使用說明。',
           'first_run_ui_batch':  '在 Batch Renamer 中，點擊右側面板頂部的 // 使用方式 ▼ 可展開使用指南。',
           'first_run_tabs_title': '功能標籤介紹',
           'first_run_tab_merger': '將多個檔案合併為一個文字檔',
           'first_run_tab_converter': 'TXT ↔ EPUB 檔案格式互轉',
           'first_run_tab_tag': '批次新增或移除檔名中的[標籤]',
           'first_run_tab_batch': '依規則批次重新命名資料夾和檔案',
           'first_run_tab_fixer': '修正單一TXT檔案的換行格式',
           'first_run_tab_bulk': '批次修正多個TXT檔案的換行格式',
           'rename_no_pairs':   '沒有要更改的名稱。',
           'rename_explorer_warn': '⚠  若目標資料夾在檔案總管中處於開啟狀態，可能會發生存取錯誤。\n重新命名前請關閉檔案總管或切換至其他位置。',
           'rename_no_subfolders': '沒有找到子資料夾。',
           'rename_no_files':   '沒有找到檔案。',
           'merge_no_support':  '資料夾中未找到支援的檔案。\n支援: txt · md · csv · docx · pdf · xlsx · hwpx 等',
           'merge_hwp_legacy_title': 'HWP (舊版) 檔案不受支援',
           'merge_hwp_legacy_msg':   '偵測到 {n} 個舊版 HWP 檔案，已略過。\n\n請在韓文 Office 中使用 <b>另存新檔 → HWPX</b> 轉換後再試。\n\nText Merger 僅支援 HWPX (KS X 6101 OWPML 標準) 格式。',
           'merge_no_files':   '沒有要合併的檔案。',
           'sc_tab_merger': '切換到 Text Merger',
           'sc_tab_converter': '切換到 Text Converter',
           'sc_tab_tag': '切換到 Tag Editor',
           'sc_tab_batch': '切換到 Batch Renamer',
           'sc_tab_fixer': '切換到 Text Fixer',
           'sc_tab_bulk':  '切換到 Bulk Fixer',
           'batch_btn_rename': '執行重新命名',
           'btn_preview': '預覽',
           'sq_suffix_ph2': '例: _final',
           'sq_prefix_ph2': '例: chapter_',
           'settings_tooltip': '設定',
           'settings_nav_license': '授權',
           'license_summary': '採用 MIT 授權 · 可自由使用、修改、再發佈、銷售 · 須保留版權聲明',
           'tf_open':         '開啟檔案',
           'tf_run':          '執行修復',
           'tf_copy':         '複製',
           'tf_save':         '儲存',
           'tf_save_fixed':   '在原位置以[Fixed]標籤儲存',
           'tf_save_as':      '另存新檔…',
           'tf_clear':        '清空',
           'tf_opt_mid':      '合併段落內換行（以空行為基準）',
           'tf_opt_sep':      '在句子之間插入空行',
           'tf_opt_auto':     '自動段落分割 — 最多',
           'tf_opt_chars':    '字',
           'tf_opt_blank':    '減少過多空行 — 最多',
           'tf_opt_line':     '行',
           'tf_lang_mode':    '合併模式',
           'tf_preset_label':  '預設',
           'tf_preset_doc':    '一般文件',
           'tf_preset_novel':  '書籍/小說',
           'tf_lang_auto':    '自動',
           'tf_lang_ko':      '韓語·其他',
           'tf_lang_en':      'English',
           'tf_grp_input':    '// 原始文字',
           'tf_grp_output':   '// 修復後文字',
        'tf_ph_input_edit': '在此直接貼上文字...',
           'tf_ph_output':    '修復結果將顯示於此...',
           'tf_stat_mid':     '合併行數: -',
           'tf_stat_mid_n':   '合併行數: {n}',
           'tf_stat_blank':   '空行縮減: -',
           'tf_stat_blank_n': '空行縮減: {n}',
           'tf_stat_orig':    '原始行數: -',
           'tf_stat_orig_n':  '原始行數: {n}',
           'tf_stat_new':     '修復後行數: -',
           'tf_stat_new_n':   '修復後: {n}行',
           'tf_search_ph':    '輸入關鍵字  (Enter: 下一個,  Shift+Enter: 上一個)',
           'tf_search_none':  '無',
           'tf_search_prev':  '◀ 上一個',
           'tf_search_next':  '下一個 ▶',
           'tf_diff_prev':    '◀ 上一個',
           'tf_diff_next':    '下一個 ▶',
           'tf_status_ready': '歡迎使用 Text Fixer',
           'tf_done':         '🌿  完成 — 合併 {mid} 行，修復空行 {blank} 處',
           'tf_copied':       '📋  已複製到剪貼簿',
           'tf_saved':        '💾  儲存完成: {name}',
           'tf_cleared':      '已清空',
           'bulk_file_list':  '// 檔案列表',
           'bulk_drop_txt':   '將檔案或資料夾拖曳到此處',
           'bulk_drop_fmt':   '支援TXT (*.txt) 格式',
           'bulk_options':    '// 修復選項',
           'bulk_preview':    '// 預覽',
           'bulk_preview_ph': '選擇檔案後顯示預覽',
           'bulk_save_mode':  '// 儲存方式',
           'bulk_save_desc':  '在檔案名前加 [Fixed] 標籤儲存。如未指定輸出資料夾，將儲存在原檔案相同位置。',
           'bulk_out_ph':     '留空 = 儲存在原檔案旁邊',
           'bulk_keep_structure': '保留資料夾結構（指定輸出資料夾時）',
           'bulk_run':        '開始批量修復',
           'bulk_running':    '⏳ 處理中…',
           'bulk_status_ready': '新增檔案後開始批量修復。',
           'bulk_status_done':  '✔  完成 — 已處理{n}個檔案',
           'bulk_status_err':   '⚠  錯誤: {msg}',
           'bulk_file_count': '{n}個檔案',
           'bulk_err_nofiles': '沒有可處理的檔案。',
           'bulk_no_txt':      '在資料夾中找不到TXT檔案。',
           'bulk_scanning':    '掃描中... 已找到{n}個',
           'tf_running':      '✨  修復中...',
           'tf_err_nofile':   '找不到檔案',
           'tf_err_perm':     '沒有讀取權限',
           'tf_err_enc':      '無法使用支援的編碼讀取檔案',
           'tf_warn_partial_enc': '⚠ 部分字元的編碼已損壞。\n\n檔案: {fname}\n使用編碼: {enc}\n已替換字元數: {n} 個\n\n檔案已載入，但損壞位置將顯示替換字元 (�)。\n請確認原始檔案未損壞。',
           # v1.0.6 Phase 2-a: Bulk Fixer 完成對話框 (4分類)
           'bulk_done_title':   '校正完成',
           'bulk_done_ok':      '正常處理: {n}個',
           'bulk_done_warn':    '注意處理: {n}個 (已產生編碼報告)',
           'bulk_done_skip':    '已略過: {n}個 (建議在 Text Fixer 中個別審核)',
           'bulk_done_fail':    '失敗: {n}個 (請檢查除錯記錄)',
           'bulk_status_skip':  '已略過',
           # v1.0.6 Phase 2-a: 編碼報告範本 (儲存為文字檔案)
           'report_header':          'File Nexus Suite — 編碼轉換報告',
           'report_file':            '檔案',
           'report_path':            '路徑',
           'report_size':            '檔案大小',
           'report_enc':             '偵測編碼',
           'report_fail_count':      '編碼失敗數',
           'report_action':          '處理結果',
           'report_action_processed':'校正完成',
           'report_action_skipped':  '略過處理 (原始檔案已保護)',
           'report_time':            '報告產生時間',
           'report_line_col':        'Line {line}, Column {col}',
           'report_bytes':           '原始位元組',
           'report_context':         '周圍文字',
           'report_summary_title':   '統計摘要',
           'report_total_failures':  '失敗字元總數',
           'report_truncated':       '省略追蹤 (詳細記錄上限 5,000 個)',
           'report_advice_title':    '建議操作',
           'report_advice_tier1':    ('檔案已正常校正，但部分字元已損毀。\n'
                                     '請在記事本或專用文字編輯器中確認相關行，\n'
                                     '如有必要，建議從原始來源重新下載。'),
           'report_advice_tier2':    ('檔案已校正，但大量字元已損毀。\n'
                                     '校正結果的品質可能已降低，請務必審核。\n'
                                     '請優先確認原始檔案的完整性。'),
           'report_advice_tier3':    ('此檔案在上述「偵測編碼」下發生了 5,000 個以上的\n'
                                     '解碼失敗。\n'
                                     '這強烈顯示檔案的實際編碼與偵測到的編碼不同。\n'
                                     '強制使用錯誤編碼處理可能導致結果比原始檔案更損毀，\n'
                                     '因此為保護原始檔案，已自動略過此檔案。\n\n'
                                     '建議操作:\n'
                                     '- 在 Text Fixer 中個別審核此檔案。\n'
                                     '- 檢查此檔案是否可能使用其他編碼 (UTF-8、Shift-JIS 等)。'),
           'tf_err_fix':      '發生錯誤',
           'tf_err_save':     '無法儲存',
           'tf_dlg_nofile':   '檔案不存在',
           'tf_dlg_noperm':   '存取錯誤',
           'tf_dlg_ioerr':    '檔案錯誤',
           'tf_dlg_encerr':   '編碼錯誤',
           'tf_highlight':    '🟡 黃色 = 已合併  🟠 橙色 = 空行已刪除',
           'tf_drop1': '將TXT檔案拖曳至此或使用開啟檔案按鈕',
           'tf_drop2': '支援 TXT (*.txt) 格式',
           'tf_drop_hover': '放開以載入檔案！',
           'conv_status_done':  '✅ 完成!',
           'conv_status_fail':  '❌ 轉換失敗',
           'tf_undo_done':      '已復原 — 已還原原始文字',
           'merge_status_add':  '已新增{n}個檔案（自動偵測編碼）',
           'merge_status_del':  '已刪除{n}個檔案',
           'merge_status_clr':  '已清除所有檔案',
           'merge_path_set':    '已設定儲存路徑: {path}',
           'merge_path_reset_done': '已重設儲存路徑',
           'merge_reading':     '📂  正在讀取檔案...',
           'merge_save_done':   '儲存完成 ({enc}): {path}',
           'merge_save_err':    '❌ 發生錯誤',
           'merge_enc_warn_title': '⚠ 編碼相容性警告',
           'merge_enc_warn_msg':   '所選儲存編碼 <b>{enc}</b> 無法表示部分字元。<br><br>• 受影響字元種類: 約 <b>{kinds} 種</b><br>• 實際受影響字數: 約 <b>{total} 個</b> (佔全文 <b>{pct}%</b>)<br>• 範例: <code>{samples}</code><br><br>如果繼續，這些字元將被替換為 <code>?</code>。<br><br>仍要儲存嗎？',
           # v1.0.5: Text Merger 儲存編碼下拉選單用途說明標籤 + 一行提示
           'merge_enc_utf8':      'UTF-8',
           'merge_enc_utf8_bom':  'UTF-8-BOM (Excel 相容)',
           'merge_enc_euckr':     'EUC-KR (韓語)',
           'merge_enc_cp949':     'CP949 (韓語 Windows)',
           'merge_enc_utf16':     'UTF-16',
           'merge_enc_shiftjis':  'Shift-JIS (日文)',
           'merge_enc_gbk':       'GBK (簡體中文)',
           'merge_enc_big5':      'Big5 (繁體中文)',
           'merge_enc_hint':      '不確定時請選擇 UTF-8',
           'merge_enc_recommend': '💡 推薦: {enc}',
           'merge_enc_recommend_apply': '套用',
           'merge_low_conf_hint':  'ℹ chardet 原始信賴度較低時，偵測到的編碼仍可能準確（尤其是 CJK 編碼）。',
           'tag_file_count':    '{n}個檔案',
           'sc_none':           '無',
           'sc_press':          '請按鍵…',
           'open_folder_tooltip': '開啟資料夾',
           'theme_lavender': '薰衣草',
           'theme_sakura': '櫻花',
           'theme_honey': '蜂蜜',
           'theme_sand': '秋',
           'theme_ocean': '夏',
           'theme_mint': '春',
           'theme_choco': '古銅色',
           'theme_dark': '深色',
           'theme_auto': '自動（預設）',
           'theme_light': '白色',
           'merge_ext_supported': '支援',
           'batch_file_ext_ph': '例: jpg, png, gif',
           'batch_file_fmt_pattern': '{資料夾名}{分隔符}{編號}.{副檔名}',
           'batch_file_fmt_label': '輸出格式',
           'conv_drop_epub_fmt': '支援 EPUB (*.epub) 格式',
           'conv_drop_txt_fmt': '支援 TXT (*.txt) 格式',
           'batch_del_all': '全部刪除',
           'batch_click_preview': '← 點擊預覽',
           'batch_parent_folder': '  (上層資料夾 — 不重新命名)',
           'batch_folder_label': '  (資料夾)',
           'batch_confirm_items': '個項目將被重新命名',
           'batch_done_items': '個項目重新命名完成',
           'dlg_rename_partial_note': '失敗的項目未被更改，且不包含在復原操作中。',
           'sq_suffix_ph': '例: 話',
           'sq_prefix_ph': '例: ch_',
           'sm_suffix_ph': '例: 話',
           'sm_prefix_ph': '例: ch_',
           'batch_count_file': '群組 {g}個 / 檔案 {f}個',
           'batch_count_folder': '群組 {g}個 / 資料夾 {f}個',
           'batch_drop2_p': '支援同時拖曳多個資料夾',
           'batch_drop1_p': '拖曳資料夾 → 重新命名檔案',
           'batch_drop2_f': '支援同時拖曳多個資料夾',
           'batch_drop1_f': '拖曳上層資料夾 → 重新命名子資料夾',
           'tag_drop2': '點擊以開啟資料夾選擇視窗',
           'tag_drop1': '將檔案或資料夾拖曳到此處',
           'conv_file_count': '檔案 {n}個',
           'conv_drop_epub': '將EPUB檔案拖曳到此處或使用新增檔案按鈕',
           'conv_drop_txt': '將TXT檔案拖曳到此處或使用新增檔案按鈕',
           'merge_sel_multi': '已選取 {n}個: {names}{more}',
           'merge_sel_one': '已選取: {name}',
           'merge_stats': '檔案 {n}個 | 共 {lines}行',
           'merge_drop': '將檔案或資料夾拖曳到此處',
           'dlg_rename_confirm': '重新命名確認',
           'dlg_rename_done': '完成',
           'dlg_rename_partial': '部分失敗',
           'crash_title':       '發生意外錯誤',
           'crash_main':        '程式發生錯誤，即將結束。',
           'crash_log_at':      '日誌儲存位置:',
           'crash_open_log':    '開啟日誌資料夾',
           'already_running_title': '已在執行',
           'already_running_main':  'File Nexus Suite 已在執行中。',
           'already_running_sub':   '請確認已開啟的視窗。',
           'rename_skip_dup_in_batch': '批次內目標重複',
           'rename_skip_dest_exists':  '目標檔案已存在',
           'lib_required_msg':  '需要 {lib} 函式庫。\npip install {lib}',
           'dlg_info':          '提示',
           'help_window_title': '💡  說明 — File Nexus Suite v{ver}',
           'help_sidebar_title':'💡  說明',
           'help_section_intro':'簡介'}}
SUPPORTED_LANGUAGES = [
    ('ko', '한국어'),
    ('en', 'English'),
    ('ja', '日本語'),
    ('zh_cn', '中文 (简体)'),
    ('zh_tw', '中文 (繁體)'),
]




def _setup_crash_logger():
    """
    Auto-save error log on app crash.
    - Captures exceptions from main thread + QThread
    - Saves to [program folder]/logs/
    - Keeps the latest 3, auto-deletes older ones
    - Shows crash dialog (with log path)
    """
    import traceback, platform, threading

    # ── Log folder setup ──────────────────────────────────────────────────────
    # Use a logs directory in the same folder as the program file
    _log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")

    try:
        os.makedirs(_log_dir, exist_ok=True)
    except OSError:
        # fallback to temp folder if not writable
        import tempfile
        _log_dir = os.path.join(tempfile.gettempdir(), "FileNexusSuite", "logs")
        os.makedirs(_log_dir, exist_ok=True)

    def _write_crash_log(exc_type, exc_value, exc_tb, thread_name="MainThread"):
        """Save crash log file and return its path."""
        _session_crashed[0] = True  # not a normal exit — keep the session log
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_path = os.path.join(_log_dir, f"crash_{ts}.log")
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write("=" * 70 + "\n")
                f.write("  File Nexus Suite — Crash Report\n")
                f.write("=" * 70 + "\n")
                f.write(f"Time      : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Thread    : {thread_name}\n")
                f.write(f"OS        : {platform.platform()}\n")
                f.write(f"Python    : {sys.version.split()[0]}\n")
                f.write(f"Language  : {_current_lang}\n")
                f.write("=" * 70 + "\n\n")
                f.write("[ Traceback ]\n")
                f.write("".join(traceback.format_exception(exc_type, exc_value, exc_tb)))
            # cleanup old logs (keep only the latest 3)
            logs = sorted(
                [os.path.join(_log_dir, f) for f in os.listdir(_log_dir) if f.startswith("crash_")],
                key=os.path.getmtime
            )
            for old in logs[:-3]:
                try: os.remove(old)
                except OSError: pass
        except Exception:
            pass
        return log_path

    def _show_crash_dialog(log_path, exc_type, exc_value):
        """Theme-aware crash notification dialog."""
        try:
            from PySide6.QtWidgets import (QApplication, QDialog, QVBoxLayout,
                                          QHBoxLayout, QLabel, QPushButton,
                                          QFrame, QTextEdit)
            from PySide6.QtCore import Qt

            QApplication.instance() or QApplication(sys.argv)

            # determine theme colors
            try:
                _resolved = _resolve_theme(_CFG.get("theme", "auto"))
                _tc = THEMES.get(_resolved, THEMES["light"])
            except Exception:
                _tc = THEMES.get("light", {
                    "BG":"#F5F4F0","SURFACE":"#FFFFFF","BORDER":"#D8D5CE",
                    "ACCENT":"#CC4444","ACCENT_HOVER":"#BB3333","TEXT":"#1A1A1A",
                    "MUTED":"#8A8078","SRF2":"#EBEBEB"
                })

            bg=_tc["BG"]; surface=_tc["SURFACE"]; border=_tc["BORDER"]
            accent="#CC4444"; text=_tc["TEXT"]; muted=_tc["MUTED"]

            _title    = _t('crash_title')
            _main     = _t('crash_main')
            _path_lbl = _t('crash_log_at')
            _open_lbl = _t('crash_open_log')
            _ok_lbl   = _t('dlg_ok')
            _err_summary = f"{exc_type.__name__}: {exc_value}"

            dlg = QDialog()
            dlg.setWindowTitle("File Nexus Suite")
            dlg.setFixedSize(520, 340)
            dlg.setWindowFlags(dlg.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
            dlg.setStyleSheet(f"QDialog{{background:{bg};}} QLabel{{background:transparent;color:{text};}}")

            root = QVBoxLayout(dlg); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

            # top red bar
            bar = QFrame(); bar.setFixedHeight(4)
            bar.setStyleSheet(f"background:{accent};border:none;")
            root.addWidget(bar)

            body = QVBoxLayout(); body.setContentsMargins(28,24,28,20); body.setSpacing(10)

            # icon + title
            hrow = QHBoxLayout(); hrow.setSpacing(12)
            icon_lbl = QLabel("💥"); icon_lbl.setStyleSheet("font-size:26px;")
            icon_lbl.setFixedWidth(36)
            title_lbl = QLabel(_title)
            title_lbl.setStyleSheet(f"font-size:15px;font-weight:700;color:{accent};")
            hrow.addWidget(icon_lbl); hrow.addWidget(title_lbl,1)
            body.addLayout(hrow)

            sep = QFrame(); sep.setFrameShape(QFrame.HLine)
            sep.setStyleSheet(f"background:{border};max-height:1px;border:none;")
            body.addWidget(sep)

            main_lbl = QLabel(_main)
            main_lbl.setStyleSheet(f"font-size:13px;color:{text};")
            body.addWidget(main_lbl)

            # error summary
            err_box = QTextEdit()
            err_box.setReadOnly(True)
            err_box.setPlainText(_err_summary)
            err_box.setFixedHeight(50)
            err_box.setStyleSheet(
                f"background:{surface};border:1px solid {border};border-radius:6px;"
                f"color:{muted};font-size:11px;padding:4px;")
            body.addWidget(err_box)

            # log path
            path_row = QVBoxLayout(); path_row.setSpacing(3)
            path_lbl = QLabel(_path_lbl)
            path_lbl.setStyleSheet(f"font-size:11px;color:{muted};font-weight:600;")
            path_val = QLabel(log_path)
            path_val.setStyleSheet(f"font-size:11px;color:{text};")
            path_val.setWordWrap(True)
            path_row.addWidget(path_lbl); path_row.addWidget(path_val)
            body.addLayout(path_row)
            body.addStretch()

            # button row
            btn_row = QHBoxLayout(); btn_row.setSpacing(10)
            open_btn = QPushButton(_open_lbl)
            open_btn.setFixedHeight(34)
            open_btn.setStyleSheet(
                f"QPushButton{{background:{surface};border:1.5px solid {border};"
                f"color:{text};border-radius:7px;font-size:12px;padding:0 14px;}}"
                f"QPushButton:hover{{background:{_tc.get('SRF2',surface)};border-color:{accent};}}")
            open_btn.clicked.connect(lambda: subprocess.Popen(
                f'explorer "{_log_dir}"' if sys.platform == "win32"
                else ["xdg-open", _log_dir] if sys.platform == "linux"
                else ["open", _log_dir]))

            ok_btn = QPushButton(_ok_lbl)
            ok_btn.setFixedHeight(34)
            ok_btn.setDefault(True)
            ok_btn.setStyleSheet(
                f"QPushButton{{background:{accent};color:white;border:none;"
                f"border-radius:7px;font-size:12px;font-weight:600;padding:0 20px;}}"
                f"QPushButton:hover{{background:#BB3333;}}")
            ok_btn.clicked.connect(dlg.accept)

            btn_row.addStretch(); btn_row.addWidget(open_btn); btn_row.addWidget(ok_btn)
            body.addLayout(btn_row)
            root.addLayout(body)
            dlg.exec()
        except Exception:
            pass  # silently exit if the dialog itself fails

    # re-entry guard — blocks infinite popup loop if the same exception fires during dlg.exec()
    _excepthook_lock = [False]
    # whether a crash occurred — decides if the session log gets deleted at atexit
    _session_crashed = [False]

    def _excepthook(exc_type, exc_value, exc_tb):
        """Main thread unhandled exception handler."""
        if issubclass(exc_type, (KeyboardInterrupt, SystemExit)):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        if _excepthook_lock[0]:
            # crash dialog is already showing — write to stderr only, no extra popup
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        _excepthook_lock[0] = True
        try:
            log_path = _write_crash_log(exc_type, exc_value, exc_tb)
            _show_crash_dialog(log_path, exc_type, exc_value)
        finally:
            _excepthook_lock[0] = False
        sys.__excepthook__(exc_type, exc_value, exc_tb)

    def _thread_excepthook(args):
        """QThread / generic thread unhandled exception handler (Python 3.8+)."""
        if issubclass(args.exc_type, (KeyboardInterrupt, SystemExit)):
            return
        thread_name = getattr(args.thread, "name", "WorkerThread")
        _write_crash_log(args.exc_type, args.exc_value, args.exc_traceback, thread_name)
        # thread crashes only write to log, no dialog

    sys.excepthook = _excepthook
    try:
        threading.excepthook = _thread_excepthook  # Python 3.8+
    except AttributeError:
        pass

    # ── Begin session log file ──────────────────────────────────────────
    global _session_log_fp
    try:
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        session_log_path = os.path.join(_log_dir, f"session_{ts}.log")
        _session_log_fp = open(session_log_path, "w", encoding="utf-8")
        _session_log_fp.write("=" * 70 + "\n")
        _session_log_fp.write("  File Nexus Suite — Session Log\n")
        _session_log_fp.write("=" * 70 + "\n")
        _session_log_fp.write(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        _session_log_fp.write(f"OS        : {platform.platform()}\n")
        _session_log_fp.write(f"Python    : {sys.version.split()[0]}\n")
        _session_log_fp.write("=" * 70 + "\n\n")
        # v1.0.6: force-flush header — preserves "app did boot" evidence even on hard kill / deadlock
        _session_log_fp.flush()
        # cleanup old session logs (only crash logs persist, so keep the latest 5)
        s_logs = sorted(
            [os.path.join(_log_dir, f) for f in os.listdir(_log_dir)
             if f.startswith("session_")],
            key=os.path.getmtime
        )
        for old in s_logs[:-5]:
            try: os.remove(old)
            except OSError: pass
    except Exception:
        _session_log_fp = None

    # ── Auto-delete session log on normal exit ──────────────────────────
    def _cleanup_session_log():
        """Delete session log on normal exit (no crash)."""
        global _session_log_fp
        if _session_log_fp is None:
            return
        session_path = _session_log_fp.name
        try:
            _session_log_fp.close()
        except Exception:
            pass
        _session_log_fp = None
        if not _session_crashed[0]:
            try:
                os.remove(session_path)
            except OSError:
                pass

    atexit.register(_cleanup_session_log)

    return _log_dir

def _show_already_running_popup():
    """Theme-aware already-running notification dialog."""
    from PySide6.QtWidgets import (QApplication, QDialog, QVBoxLayout,
                                  QHBoxLayout, QLabel, QPushButton, QFrame)
    from PySide6.QtCore import Qt

    QApplication.instance() or QApplication(sys.argv)

    # read saved theme
    try:
        with open(_CONFIG_PATH, "r", encoding="utf-8") as _f:
            _cfg = json.load(_f)
        _theme_name = _cfg.get("theme", "auto")
        _lang = _cfg.get("language", "ko")
    except Exception:
        _theme_name = "auto"
        _lang = "ko"

    # determine theme colors
    _resolved = _resolve_theme(_theme_name)
    _t_colors = THEMES.get(_resolved, THEMES["light"])
    bg      = _t_colors["BG"]
    border  = _t_colors["BORDER"]
    accent  = _t_colors["ACCENT"]
    text    = _t_colors["TEXT"]
    muted   = _t_colors["MUTED"]

    _title    = _t('already_running_title')
    _main     = _t('already_running_main')
    _sub      = _t('already_running_sub')
    _ok_lbl   = _t('dlg_ok')

    # build custom dialog
    dlg = QDialog()
    dlg.setWindowTitle("File Nexus Suite")
    try:
        dlg.setWindowIcon(_make_app_icon())
    except Exception:
        pass
    dlg.setFixedSize(400, 220)
    dlg.setWindowFlags(dlg.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
    dlg.setStyleSheet(f"""
        QDialog {{ background: {bg}; }}
        QLabel  {{ background: transparent; color: {text}; }}
    """)

    root = QVBoxLayout(dlg)
    root.setContentsMargins(0, 0, 0, 0)
    root.setSpacing(0)

    # top color bar
    bar = QFrame(); bar.setFixedHeight(4)
    bar.setStyleSheet(f"background: {accent}; border: none;")
    root.addWidget(bar)

    # content area
    body = QVBoxLayout()
    body.setContentsMargins(32, 28, 32, 24)
    body.setSpacing(10)

    # icon + title row
    hrow = QHBoxLayout(); hrow.setSpacing(14)
    icon_lbl = QLabel("🔔")
    icon_lbl.setStyleSheet("font-size: 28px; background: transparent;")
    icon_lbl.setFixedWidth(36)
    title_lbl = QLabel(_title)
    title_lbl.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {accent};")
    hrow.addWidget(icon_lbl)
    hrow.addWidget(title_lbl, 1)
    body.addLayout(hrow)

    # separator
    sep = QFrame(); sep.setFrameShape(QFrame.HLine)
    sep.setStyleSheet(f"background: {border}; max-height: 1px; border: none;")
    body.addWidget(sep)
    body.addSpacing(4)

    # main message
    main_lbl = QLabel(_main)
    main_lbl.setStyleSheet(f"font-size: 13px; color: {text};")
    main_lbl.setWordWrap(True)
    body.addWidget(main_lbl)

    # sub message
    sub_lbl = QLabel(_sub)
    sub_lbl.setStyleSheet(f"font-size: 12px; color: {muted};")
    sub_lbl.setWordWrap(True)
    body.addWidget(sub_lbl)

    body.addStretch()

    # OK button
    btn_row = QHBoxLayout()
    btn_row.addStretch()
    ok_btn = QPushButton(_ok_lbl)
    ok_btn.setFixedWidth(100)
    ok_btn.setFixedHeight(36)
    ok_btn.setDefault(True)
    ok_btn.setStyleSheet(f"""
        QPushButton {{
            background: {accent}; color: white; border: none;
            border-radius: 8px; font-size: 13px; font-weight: 600;
        }}
        QPushButton:hover {{ background: {_t_colors["ACCENT_HOVER"]}; }}
    """)
    ok_btn.clicked.connect(dlg.accept)
    btn_row.addWidget(ok_btn)
    body.addLayout(btn_row)

    root.addLayout(body)
    dlg.exec()

def _check_single_instance():
    """
    Ensure single instance.
    - If already running, show one theme-aware popup and exit.
    - If a popup is already up, additional launches exit silently without duplicating it.
    - Store the returned mutex/lock in a variable so GC does not release it.
    """
    APP_MUTEX_NAME   = "FileNexusSuite_SingleInstance_v1"
    POPUP_MUTEX_NAME = "FileNexusSuite_PopupActive_v1"

    if sys.platform == "win32":
        import ctypes
        ERROR_ALREADY_EXISTS = 183

        app_mutex = ctypes.windll.kernel32.CreateMutexW(None, False, APP_MUTEX_NAME)
        if ctypes.windll.kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
            popup_mutex = ctypes.windll.kernel32.CreateMutexW(None, True, POPUP_MUTEX_NAME)
            already_popup = (ctypes.windll.kernel32.GetLastError() == ERROR_ALREADY_EXISTS)

            if not already_popup:
                _show_already_running_popup()
                ctypes.windll.kernel32.ReleaseMutex(popup_mutex)
                ctypes.windll.kernel32.CloseHandle(popup_mutex)

            ctypes.windll.kernel32.CloseHandle(app_mutex)
            sys.exit(0)

        return app_mutex

    else:
        import tempfile
        lock_path = os.path.join(tempfile.gettempdir(), "FileNexusSuite.lock")
        try:
            import fcntl
            _lock_fp = open(lock_path, "w")
            fcntl.lockf(_lock_fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return _lock_fp
        except (IOError, OSError, ImportError):
            _show_already_running_popup()
            sys.exit(0)

def _detect_os_lang() -> str:
    """Convert the OS default language to a supported language code.

    Priority:
    1. Windows: registry Control Panel\\International → LocaleName
       - In PyInstaller builds, the locale module returns Windows-internal forms
         like 'Korean_Korea', breaking 'ko' matching — this fixes that
    2. locale.getlocale() — POSIX form (e.g., 'ko_KR')
    3. locale.getdefaultlocale() — deprecated, but a fallback for some environments
    4. Returns 'en' if all of the above fail
    """
    code = ''

    # ── 1. Windows registry (most reliable) ──────────────────────────
    if sys.platform == 'win32':
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r'Control Panel\International')
            val, _ = winreg.QueryValueEx(key, 'LocaleName')
            winreg.CloseKey(key)
            code = val.replace('-', '_')   # 'ko-KR' → 'ko_KR'
        except Exception:
            pass

    # ── 2. locale.getlocale() ─────────────────────────────────────────
    if not code:
        try:
            import locale
            code = locale.getlocale()[0] or ''
        except Exception:
            code = ''

    # ── 3. locale.getdefaultlocale() fallback ────────────────────────
    if not code:
        try:
            import locale
            code = locale.getdefaultlocale()[0] or ''
        except Exception:
            code = ''

    if code.startswith('ko'): return 'ko'
    if code.startswith('ja'): return 'ja'
    if code.startswith('zh_TW') or code.startswith('zh_HK'): return 'zh_tw'
    if code.startswith('zh'): return 'zh_cn'
    return 'en'

_current_lang = _detect_os_lang()   # runtime current language — initialized from OS default


# ═══════════════════════════════════════════════
# Batch Renamer helpers
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
# Text Converter core logic
# ═══════════════════════════════════════════════
def alchemy_detect_encoding(path):
    """File encoding detection — direct BOM check + chardet + fallback.

    v1.0.3: CJK encodings (GBK/Big5/Shift-JIS) use a lowered threshold of 0.5.
    chardet often returns 0.5–0.7 confidence for these encodings, so
    applying the strict 0.7 cutoff leads to wrong utf-8/cp949 fallbacks.

    v1.0.4: unified to return an (encoding, confidence) tuple — absorbs the separate
    _detect_encoding() previously used by Text Merger. Confidence is chardet's raw value (0–1),
    1.0 on BOM detection, 0.0 on fallback. Read size raised from 8192 → 32768.

    Returns:
        tuple[str, float]: (normalized encoding name, 0–1 confidence)
    """
    try:
        with open(path, "rb") as f: raw = f.read(32768)
        if raw[:3] == bytes([0xef,0xbb,0xbf]): return ("utf-8-sig", 1.0)
        if raw[:2] in (bytes([0xff,0xfe]), bytes([0xfe,0xff])): return ("utf-16", 1.0)
        if HAS_CHARDET:
            result = _chardet.detect(raw); enc = (result.get("encoding") or "utf-8").lower()
            conf = float(result.get("confidence", 0) or 0.0)
            # chardet often returns 0.5–0.7 for CJK encodings → relaxed threshold
            # cp932/windows-31j are Windows Shift-JIS extensions → normalize to shift_jis
            _CJK_ENCS = ("gb18030","gbk","gb2312","big5",
                         "shift_jis","shift-jis","cp932","windows-31j","euc-jp")
            if conf >= 0.7 or (conf >= 0.5 and enc in _CJK_ENCS):
                if enc in ("utf-8","utf-8-sig","ascii"): return ("utf-8", conf)
                if enc in ("euc-kr","euc_kr","cp949","ms949"): return ("cp949", conf)
                if enc in ("utf-16","utf-16-le","utf-16-be"): return ("utf-16", conf)
                # GBK/GB2312/GB18030 → normalize to gbk (gbk is a superset)
                if enc in ("gb18030","gbk","gb2312"): return ("gbk", conf)
                # Shift-JIS variants → normalize to shift_jis (cp932/windows-31j are Windows extensions)
                if enc in ("shift_jis","shift-jis","cp932","windows-31j"): return ("shift_jis", conf)
                return (enc, conf)
        # v1.0.6: assign 0.7 on utf-8 strict pass (was 0.0). Same logic as cp949/shift_jis fallback.
        # strict pass guarantees lossless decode → meets 0.7 recommend cutoff. Badge honestly shows "70% UTF-8".
        try: raw.decode("utf-8"); return ("utf-8", 0.7)
        except UnicodeDecodeError: pass
        # v1.0.4: rescue path even when chardet mis-detects CJK files (e.g., Shift-JIS that starts with ASCII → cp1006)
        # by sequentially strict-validating CJK encodings: cp949 → shift_jis → gbk → big5.
        # (Shift-JIS files fail cp949 strict decode, so the order is independent.)
        # v1.0.6: assign 0.7 on strict-pass (was 0.0 → previously ignored by the auto-recommend algorithm).
        # strict-pass mathematically guarantees "decodable losslessly with this encoding", so
        # it meets the 0.7 recommend cutoff. But without chardet validation, 0.9 (green) overstates it — 0.7 (yellow) is appropriate.
        for _fallback in ("cp949", "shift_jis", "gbk", "big5"):
            try:
                raw.decode(_fallback)
                return (_fallback, 0.7)
            except UnicodeDecodeError: continue
        return ("cp949", 0.0)  # last-resort fallback (preserves v1.0.3 behavior)
    except Exception: return ("utf-8", 0.0)


def alchemy_check_encoding_compat(text, codec):
    """Pre-validate whether text can be saved with the given codec losslessly (new in v1.0.4).

    Catches incompatible combinations (e.g., saving Korean text as Shift-JIS) and warns
    before a UnicodeEncodeError actually occurs.

    Unicode encodings (UTF-8 / UTF-16 family) can represent every Unicode character →
    skip validation and immediately return (False, 0, 0, total, []).

    Args:
        text: text to be saved
        codec: Python codec name (e.g., "shift_jis", "gbk", "big5", "cp949")

    Returns:
        tuple[bool, int, int, int, list[str]]:
            - lossy flag (True = some characters will break)
            - count of distinct broken character kinds (e.g., 1 even if "한" appears 50 times)
            - total affected character count (with duplicates, e.g., 50 if "한" appears 50 times)
            - total character count (for ratio calculation)
            - up to 5 sample broken characters (for dialog display)
    """
    total_chars = len(text)
    if codec in ("utf-8", "utf-8-sig", "utf-16", "utf-16-le", "utf-16-be"):
        return (False, 0, 0, total_chars, [])
    try:
        text.encode(codec)  # validate in one shot via strict mode (most cases)
        return (False, 0, 0, total_chars, [])
    except UnicodeEncodeError:
        pass
    # lossy → identify the set of distinct broken characters (dedupe via set, validate once)
    bad_chars = set()
    samples = []
    for ch in set(text):
        try: ch.encode(codec)
        except UnicodeEncodeError:
            bad_chars.add(ch)
            if len(samples) < 5: samples.append(ch)
    # count total affected characters (full scan, duplicates included)
    bad_total_count = sum(1 for ch in text if ch in bad_chars)
    return (True, len(bad_chars), bad_total_count, total_chars, samples)


# v1.0.6 Phase 2-a: cap on tracked failure positions (beyond this, count only)
MAX_TRACK_FAILURES = 5000

# v1.0.6 field-QA re-optimization: thread-local storage for tracking + a global error handler
# (replaces the prior O(N×K) slicing approach with a single O(N) pass via codecs.register_error)
import codecs as _codecs_mod
import bisect as _bisect_mod
import threading as _threading_mod

_decode_tracking_state = _threading_mod.local()


def _fns_track_error_handler(e):
    """FileNexusSuite-dedicated error handler — collects failure info into thread-local state.

    Registered once via codecs.register_error('_fns_track', ...).
    Called from inside _decode_with_failure_tracking after setting up the captured list in thread-local.

    Args:
        e: UnicodeDecodeError — accesses e.start / e.end / e.object

    Returns:
        tuple[str, int]: (replacement string, next decoding position)
    """
    captured = getattr(_decode_tracking_state, 'captured', None)
    if captured is not None and len(captured) < MAX_TRACK_FAILURES:
        captured.append({
            'byte_pos': e.start,
            'bad_bytes': bytes(e.object[e.start:e.end]),
        })
    return ('\ufffd', e.end)


# register only once at module load (avoids handler accumulation)
_codecs_mod.register_error('_fns_track', _fns_track_error_handler)


def _decode_with_failure_tracking(raw: bytes, enc: str) -> tuple:
    """Decode a byte sequence while tracking each UnicodeDecodeError position (v1.0.6 Phase 2-a).

    v1.0.6 re-optimization (O(N×K) freeze discovered during field QA):
        before: `while pos < len: raw[pos:].decode('strict')` — slice copy per iteration →
              UI froze on a 27MB file with thousands of errors
        after: a custom error handler via codecs.register_error + a single raw.decode() call →
              one O(N) pass at the C level

    Algorithm:
        1. set up the captured list in thread-local
        2. raw.decode(enc, errors='_fns_track') — handler appends to captured on each error
        3. find \\ufffd positions in the decoded text (str.find, C-level O(N))
        4. build a \\n position index (str.find loop, C-level O(N))
        5. resolve line/column in O(log N) via bisect

    Performance: 27MB + thousands of errors — minutes → under a few hundred ms (hundreds~thousands× faster)

    Args:
        raw: raw byte sequence
        enc: encoding name to attempt

    Returns:
        tuple[str | None, list, int]:
            - text: decoded text (None on catastrophic failure)
            - failures: list of failure-position dicts (up to MAX_TRACK_FAILURES)
                       each dict: {byte_pos, bad_bytes_hex, line, col, context}
            - total_failures: actual total failure count (includes overflow beyond MAX)
    """
    # prepare thread-local captured list
    captured = []
    _decode_tracking_state.captured = captured

    try:
        try:
            text = raw.decode(enc, errors='_fns_track')
        except (LookupError, TypeError):
            # nonexistent encoding, etc. — catastrophic failure
            return (None, [], 0)
        except Exception:
            # unexpected failure → fallback to errors='replace' (loses position info)
            try:
                text = raw.decode(enc, errors='replace')
                return (text, [], text.count('\ufffd'))
            except Exception:
                return (None, [], 0)
    finally:
        _decode_tracking_state.captured = None

    # total failure count: number of \ufffd in the decoded text (fast C-level count)
    total_failures = text.count('\ufffd')

    if total_failures == 0 or not captured:
        return (text, [], total_failures)

    # for each error in captured, find char_pos (= position of \ufffd in text)
    # captured holds up to MAX_TRACK_FAILURES; text.find is C-level and fast
    ufffd_positions = []
    start = 0
    for _ in range(len(captured)):
        pos = text.find('\ufffd', start)
        if pos < 0:
            break
        ufffd_positions.append(pos)
        start = pos + 1

    # build a \n position index for line lookups (built once, O(N))
    nl_positions = []
    start = 0
    while True:
        pos = text.find('\n', start)
        if pos < 0:
            break
        nl_positions.append(pos)
        start = pos + 1

    # assemble the failures list (each entry O(log N))
    failures = []
    for cap, cp in zip(captured, ufffd_positions):
        # line/column — fast lookup via bisect
        line_idx = _bisect_mod.bisect_left(nl_positions, cp)
        line_num = line_idx + 1
        if line_idx > 0:
            col = cp - nl_positions[line_idx - 1]
        else:
            col = cp + 1

        # surrounding text: 20 chars before + � + 20 chars after (control chars normalized to spaces)
        ctx_start = max(0, cp - 20)
        ctx_end = min(len(text), cp + 21)  # +1 for \ufffd itself, +20 for after
        ctx = text[ctx_start:ctx_end]
        ctx = ctx.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')

        failures.append({
            'byte_pos': cap['byte_pos'],
            'bad_bytes_hex': ' '.join(f'0x{b:02X}' for b in cap['bad_bytes']),
            'line': line_num,
            'col': col,
            'context': ctx,
        })

    return (text, failures, total_failures)


def safe_read_text_with_report(path: str) -> tuple:
    """Read a file safely — if all 8 strict fallbacks fail, retry one last time with errors='replace' (new in v1.0.6).

    Like Notepad, makes "partially-broken files" readable so preview/fix does not fail outright.
    Broken bytes are replaced with U+FFFD (Replacement Character, '�') (Python errors='replace' default).

    v1.0.6 Phase 2-a: failure-position tracking added — in replace mode, collects byte/line/column info for each error.

    Args:
        path: file path

    Returns:
        tuple[str | None, str, str, int, list, int]:
            - text: text read in (None if the file itself was inaccessible)
            - used_enc: encoding name actually used
            - read_mode: 'strict' (normal strict decode succeeded) or 'replace' (errors='replace' fallback)
            - replace_count: in replace mode, count of U+FFFD substitutions (0 on strict success)
            - failures: in replace mode, list of failure positions (up to MAX_TRACK_FAILURES);
                       each entry is a dict(byte_pos, bad_bytes_hex, line, col, context). Empty list on strict success.
            - total_failures: in replace mode, the actual total failure count (includes overflow beyond MAX_TRACK_FAILURES).
                             0 on strict success.
    """
    try:
        detected_enc, _conf = alchemy_detect_encoding(path)
    except Exception:
        detected_enc = "utf-8"
    # Step 1: try the 8-way strict-decode fallback (preserves existing logic)
    candidates = (detected_enc, 'utf-8-sig', 'utf-8', 'cp949', 'euc-kr',
                  'shift_jis', 'gbk', 'big5')
    for enc in candidates:
        try:
            with open(path, 'r', encoding=enc) as f:
                return (f.read(), enc, 'strict', 0, [], 0)
        except (UnicodeDecodeError, LookupError):
            continue
        except OSError:
            # file inaccessible (permissions / missing / etc.) — no point in trying further
            return (None, detected_enc, 'strict', 0, [], 0)
    # Step 2: all strict attempts failed → final retry with errors='replace' + position tracking
    # detected encoding first; otherwise cp949 (default for Korean environments)
    replace_enc = detected_enc if detected_enc else 'cp949'
    try:
        with open(path, 'rb') as f:
            raw = f.read()
    except Exception:
        return (None, replace_enc, 'replace', 0, [], 0)

    text, failures, total_failures = _decode_with_failure_tracking(raw, replace_enc)
    if text is None:
        return (None, replace_enc, 'replace', 0, [], 0)

    replace_count = text.count('\ufffd')
    return (text, replace_enc, 'replace', replace_count, failures, total_failures)


def write_encoding_report(
    output_dir,
    original_path: str,
    used_enc: str,
    failures: list,
    total_failures: int,
    action_taken: str,
    lang: str = None,
):
    """Generate an encoding report file (v1.0.6 Phase 2-a).

    Provides post-hoc transparency for files Bulk Fixer processed in replace mode.
    Not generated when total_failures == 0 (normally processed file).

    Tier-based recommended-action branches:
    - Tier 1 (1~500): 'processed' + report_advice_tier1 (some damage, review recommended)
    - Tier 2 (501~5000): 'processed' + report_advice_tier2 (many damaged, check original)
    - Tier 3 (5001+): 'skipped' + report_advice_tier3 (skipped to protect original, Text Fixer recommended)

    Args:
        output_dir: folder to save the report. If None or invalid, uses the original file's folder.
        original_path: original file path (for report metadata)
        used_enc: encoding name used for decoding
        failures: list of failure-position dicts (up to MAX_TRACK_FAILURES)
        total_failures: actual total failure count
        action_taken: 'processed' (Tier 1/2) or 'skipped' (Tier 3)
        lang: report language code (None uses the current UI language)

    Returns:
        path of the generated report file. None on failure or when total_failures == 0.
    """
    if total_failures <= 0:
        return None

    # determine save path: output_dir if given, otherwise the original file's folder
    original_dir = os.path.dirname(original_path)
    if output_dir and os.path.isdir(output_dir):
        save_dir = output_dir
    else:
        save_dir = original_dir
    fname = os.path.basename(original_path)
    report_name = f"{fname}.encoding_report.txt"
    report_path = os.path.join(save_dir, report_name)

    # current language (frozen at report-generation time)
    if lang is None:
        lang = _current_lang

    def _rt(key, **kwargs):
        """Report-only translator — driven by the lang parameter (stays fixed even if _current_lang changes in a worker thread).
        zh_cn falls back to zh_tw first, then to Korean."""
        s = (TRANSLATIONS.get(lang, TRANSLATIONS['ko']).get(key)
             or (TRANSLATIONS['zh_tw'].get(key) if lang == 'zh_cn' else None)
             or TRANSLATIONS['ko'].get(key, key))
        return s.format(**kwargs) if kwargs else s

    try:
        try:
            file_size = os.path.getsize(original_path)
        except OSError:
            file_size = 0

        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # tier branching
        if action_taken == 'skipped':
            tier_key = 'report_advice_tier3'
        elif total_failures > 500:
            tier_key = 'report_advice_tier2'
        else:
            tier_key = 'report_advice_tier1'

        action_text = (_rt('report_action_skipped') if action_taken == 'skipped'
                       else _rt('report_action_processed'))

        sep = '=' * 68
        lines = []
        # header
        lines.append(sep)
        lines.append(f'  {_rt("report_header")}')
        lines.append(sep)
        lines.append(f'{_rt("report_file")}: {fname}')
        lines.append(f'{_rt("report_path")}: {original_path}')
        lines.append(f'{_rt("report_size")}: {file_size:,} bytes')
        lines.append(f'{_rt("report_enc")}: {used_enc.upper()}')
        lines.append(f'{_rt("report_fail_count")}: {total_failures:,}')
        lines.append(f'{_rt("report_action")}: {action_text}')
        lines.append(f'{_rt("report_time")}: {now_str}')
        lines.append('')

        # failure-position list (up to MAX_TRACK_FAILURES)
        for i, f in enumerate(failures, 1):
            lines.append(f'[{i}] {_rt("report_line_col", line=f["line"], col=f["col"])}')
            lines.append(f'    {_rt("report_bytes")}: {f["bad_bytes_hex"]}')
            lines.append(f'    {_rt("report_context")}: "{f["context"]}"')
            lines.append('')

        # summary statistics
        lines.append(sep)
        lines.append(f'  {_rt("report_summary_title")}')
        lines.append(sep)
        lines.append(f'{_rt("report_total_failures")}: {total_failures:,}')
        truncated = total_failures - len(failures)
        if truncated > 0:
            lines.append(f'{_rt("report_truncated")}: {truncated:,}')
        lines.append('')

        # recommended actions
        lines.append(sep)
        lines.append(f'  {_rt("report_advice_title")}')
        lines.append(sep)
        lines.append(_rt(tier_key))
        lines.append('')

        content = '\n'.join(lines)

        # save without UTF-8 BOM (compatible with other text editors)
        with open(report_path, 'w', encoding='utf-8') as rf:
            rf.write(content)

        return report_path
    except Exception as e:
        _glog(f"[Bulk Fixer] failed to generate report: {fname}: {e}")
        return None


def merger_recommend_save_encoding(enc_map: dict, conf_map: dict) -> tuple:
    """Analyze the file encodings detected by Text Merger and recommend a safe save encoding (new in v1.0.6).

    A1'' policy (confidence-threshold applied):
    - if every text file is detected as the same non-Unicode encoding,
      and every file's confidence is ≥ 0.7 → recommend that encoding
    - otherwise → recommend UTF-8 (safe)
    - binary markers like docx/pdf/xlsx are ignored (extracted text is plain)

    Misdetected cases (confidence < 0.7) safely fall back to UTF-8.
    Principle #1 (honesty): "do not recommend what you are not confident about"

    Args:
        enc_map:  {file_path: encoding_name}  — TextMergerPanel.enc_map
        conf_map: {file_path: confidence(0~1)} — TextMergerPanel.enc_confidence

    Returns:
        tuple[str, str]: (dropdown userData key, user-facing display name)
            e.g., ("CP949", "CP949"), ("UTF-8", "UTF-8"), ("Shift-JIS", "Shift-JIS")
    """
    # filter to text files only (exclude binary markers)
    _BINARY_MARKERS = {"DOCX", "PDF", "XLSX"}
    text_files = {
        path: enc for path, enc in enc_map.items()
        if enc.upper() not in _BINARY_MARKERS
    }
    # 0 text files → UTF-8 (default-safe)
    if not text_files:
        return ("UTF-8", "UTF-8")

    # map non-Unicode names normalized by alchemy_detect_encoding → dropdown userData keys
    _RECOMMENDABLE = {
        "cp949":     "CP949",
        "euc-kr":    "EUC-KR",
        "shift_jis": "Shift-JIS",
        "gbk":       "GBK",
        "big5":      "Big5",
    }
    # are all text files the same encoding?
    enc_set = set(e.lower() for e in text_files.values())
    if len(enc_set) != 1:
        return ("UTF-8", "UTF-8")
    only_enc = enc_set.pop()
    if only_enc not in _RECOMMENDABLE:
        return ("UTF-8", "UTF-8")  # UTF-8 / UTF-16 / etc. stay as UTF-8

    # A1'' core: every file's confidence ≥ 0.7
    _MIN_CONF = 0.7
    confs = [conf_map.get(p, 0.0) for p in text_files.keys()]
    if any(c < _MIN_CONF for c in confs):
        return ("UTF-8", "UTF-8")  # not confident enough → safe UTF-8

    rec_key = _RECOMMENDABLE[only_enc]
    return (rec_key, rec_key)


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

def epub_to_text(path, opts):
    """EPUB → TXT conversion (custom implementation using zipfile + regex)."""
    with zipfile.ZipFile(path,"r") as zf:
        cont = zf.read("META-INF/container.xml").decode("utf-8","replace")
        m = re.search(r'full-path\s*=\s*[^\s>]+',cont)
        if not m: raise ValueError("OPF not found")
        raw=m.group(0); op=re.sub(r'full-path\s*=\s*["\']',"",raw).rstrip('"\'  ')
        base=op.rsplit("/",1)[0]+"/" if "/" in op else ""
        opf=zf.read(op).decode("utf-8","replace")
        tm=re.search(r"<dc:title[^>]*>(.*?)</dc:title>",opf,re.S)
        am=re.search(r"<dc:creator[^>]*>(.*?)</dc:creator>",opf,re.S)
        t=_de(tm.group(1).strip()) if tm else ""; a=_de(am.group(1).strip()) if am else ""
        mf={}
        for it in re.finditer(r"<item\s+([^>]+?)/?>",opf,re.S):
            attrs=it.group(1)
            id_m=re.search(r'\bid\s*=\s*["\'](.*?)["\']',attrs)
            hr_m=re.search(r'href\s*=\s*["\'](.*?)["\']',attrs)
            if id_m and hr_m: mf[id_m.group(1)]=base+hr_m.group(1).split("#")[0]
        spine=[]
        sm=re.search(r"<spine[^>]*>(.*?)</spine>",opf,re.S)
        if sm:
            for r in re.finditer(r'idref\s*=\s*["\'](.*?)["\']',sm.group(1)): spine.append(r.group(1))
        out,ch=[],0
        if t:
            out.append(f"■ {t}")
            if a: out.append(f"저자: {a}")
            out.append("")
        names=zf.namelist()
        for iid in spine:
            href=mf.get(iid)
            if not href: continue
            matched=next((n for n in names if n.lower()==href.lower() or n==href),None)
            if not matched: continue
            html=zf.read(matched).decode("utf-8","replace")
            text=_h2t(html,opts.get("titles",True))
            if not text.strip(): continue
            if opts.get("separator") and ch>0: out.append("\n"+"─"*40+"\n")
            out.append(text); ch+=1
    res="\n".join(out)
    if opts.get("trim_blank"): res=re.sub(r"\n{3,}","\n\n",res)
    return res,ch

def _strip_xml_illegal(s):
    return re.sub(r'[^\x09\x0A\x0D\x20-\uD7FF\uE000-\uFFFD\U00010000-\U0010FFFF]','',s)

def _ex(s):
    s=_strip_xml_illegal(s)
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;") \
             .replace('"',"&quot;").replace("'","&apos;")

def txt_to_epub(path, out_path, meta):
    enc_read=meta.get("encoding","utf-8")
    with open(path,"r",encoding=enc_read,errors="replace") as f: text=f.read()
    text=_strip_xml_illegal(text)
    mode=meta.get("chapter_mode","separator")
    if mode=="separator": parts=re.split(r"\n[ \t]*(?:={3,}|-{3,}|\*{3,}|~{3,}|_{3,}|─{3,})[ \t]*\n",text)
    elif mode=="emptylines": parts=re.split(r"\n{3,}",text)
    else: parts=[text]
    chapters=[]
    for i,p in enumerate(parts):
        p=p.strip()
        if not p: continue
        lines=p.split("\n"); title=f"Chapter {i+1}"
        if len(lines)>1 and len(lines[0])<60 and not lines[0].endswith("."):
            extracted = lines[0].strip()
            if extracted:
                title = extracted
                # first line was used as the title, so strip it from the body (avoids h1 + p duplication)
                p = "\n".join(lines[1:]).lstrip("\n")
        chapters.append({"title":title,"content":p})
    if not chapters: raise ValueError("No chapters found")
    uid=str(uuid.uuid4()); bt=_ex(meta.get("title","Untitled")); ba=_ex(meta.get("author","Unknown"))
    lang=meta.get("lang","ko")
    with zipfile.ZipFile(out_path,"w",zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(zipfile.ZipInfo("mimetype"),"application/epub+zip",compress_type=zipfile.ZIP_STORED)
        zf.writestr("META-INF/container.xml",
            '<?xml version="1.0" encoding="UTF-8"?><container version="1.0" '
            'xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles>'
            '<rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>'
            '</rootfiles></container>')
        zf.writestr("OEBPS/style.css",
            "body{font-family:serif;line-height:1.9;margin:1.5em;}h1{font-size:1.4em;margin:1.2em 0 .6em;}p{margin:.4em 0;text-indent:1em;}")
        mi,si,nav=[],[],[]
        for i,ch in enumerate(chapters):
            fn=f"chapter{i+1:03d}.xhtml"; ct=_ex(ch['title'])
            body="\n".join(f"  <p>{_ex(l.strip())}</p>" for l in ch['content'].split("\n") if l.strip())
            zf.writestr(f"OEBPS/{fn}",
                f'<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">'
                f'<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{lang}"><head><title>{ct}</title><link rel="stylesheet" type="text/css" href="style.css"/></head>'
                f'<body><h1>{ct}</h1>\n{body}\n</body></html>')
            mi.append(f'<item id="ch{i+1}" href="{fn}" media-type="application/xhtml+xml"/>')
            si.append(f'<itemref idref="ch{i+1}"/>')
            nav.append(f'<navPoint id="np{i+1}" playOrder="{i+1}"><navLabel><text>{ct}</text></navLabel><content src="{fn}"/></navPoint>')
        zf.writestr("OEBPS/toc.ncx",
            f'<?xml version="1.0" encoding="UTF-8"?><ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">'
            f'<head><meta name="dtb:uid" content="urn:uuid:{uid}"/></head>'
            f'<docTitle><text>{bt}</text></docTitle><navMap>{"".join(nav)}</navMap></ncx>')
        zf.writestr("OEBPS/content.opf",
            f'<?xml version="1.0" encoding="UTF-8"?><package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="BookId">'
            f'<metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">'
            f'<dc:title>{bt}</dc:title><dc:creator opf:role="aut">{ba}</dc:creator>'
            f'<dc:language>{lang}</dc:language><dc:identifier id="BookId">urn:uuid:{uid}</dc:identifier></metadata>'
            f'<manifest><item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>'
            f'<item id="css" href="style.css" media-type="text/css"/>{"".join(mi)}</manifest>'
            f'<spine toc="ncx">{"".join(si)}</spine></package>')
    return len(chapters)


# ═══════════════════════════════════════════════
# Widget classes
# ═══════════════════════════════════════════════

# ── Help button (sine-wave up/down animation on hover) ──



class _HelpButton(QPushButton):
    """Button with a sine-wave animation: the icon lifts slightly upward and returns on hover."""

    def __init__(self, parent=None):
        super().__init__("", parent)
        self._phase = 0.0
        self._hovered = False
        self._timer = QTimer(self)
        self._timer.setInterval(30)
        self._timer.timeout.connect(self._tick)
        self._offset = 0.0

    def _tick(self):
        import math as _math
        self._phase += 0.12
        self._offset = -abs(_math.sin(self._phase)) * 4  # upward only, ±4px
        if not self._hovered and abs(self._offset) < 0.1:
            self._timer.stop()
            self._phase = 0.0
            self._offset = 0.0
        self.update()

    def enterEvent(self, e):
        self._hovered = True
        self._phase = 0.0
        self._timer.start()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._hovered = False
        super().leaveEvent(e)

    def paintEvent(self, e):
        # paint only the button background/border (excluding the icon)
        from PySide6.QtWidgets import QStylePainter, QStyleOptionButton, QStyle
        from PySide6.QtGui import QIcon
        painter = QStylePainter(self)
        opt = QStyleOptionButton()
        self.initStyleOption(opt)
        opt.icon = QIcon()  # remove icon → render background/border only
        painter.drawControl(QStyle.ControlElement.CE_PushButton, opt)
        painter.end()
        # draw the icon directly with the offset applied
        icon = self.icon()
        if icon.isNull(): return
        p2 = QPainter(self)
        r = self.rect()
        sz = self.iconSize()
        ix = (r.width() - sz.width()) // 2
        iy = (r.height() - sz.height()) // 2 + int(self._offset)
        icon.paint(p2, ix, iy, sz.width(), sz.height())
        p2.end()


class _GearButton(QPushButton):
    """Button with an animation that rotates the icon slightly clockwise on hover."""

    def __init__(self, parent=None):
        super().__init__("", parent)
        self._angle = 0.0
        self._target = 0.0
        self._hovered = False
        self._timer = QTimer(self)
        self._timer.setInterval(30)
        self._timer.timeout.connect(self._tick)

    def _tick(self):
        if self._hovered:
            self._target += 2.5
        diff = self._target - self._angle
        self._angle += diff * 0.15
        if not self._hovered and abs(diff) < 0.3:
            self._angle = 0.0
            self._target = 0.0
            self._timer.stop()
        self.update()

    def enterEvent(self, e):
        self._hovered = True
        self._timer.start()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._hovered = False
        self._target = round(self._angle / 360) * 360
        super().leaveEvent(e)

    def paintEvent(self, e):
        from PySide6.QtWidgets import QStylePainter, QStyleOptionButton, QStyle
        from PySide6.QtGui import QIcon
        painter = QStylePainter(self)
        opt = QStyleOptionButton()
        self.initStyleOption(opt)
        opt.icon = QIcon()
        painter.drawControl(QStyle.ControlElement.CE_PushButton, opt)
        painter.end()
        icon = self.icon()
        if icon.isNull(): return
        p2 = QPainter(self)
        p2.setRenderHint(QPainter.Antialiasing)
        r = self.rect()
        sz = self.iconSize()
        p2.translate(r.width() / 2, r.height() / 2)
        p2.rotate(self._angle)
        p2.translate(-sz.width() / 2, -sz.height() / 2)
        icon.paint(p2, 0, 0, sz.width(), sz.height())
        p2.end()


# ── Scroll-direction hint overlay ───────────────
class _ScrollHint(QLabel):
    """Overlay widget that signals scroll direction with three triangles + a gradient.
    Conveys scrollability via sine-wave motion (±3px) + fade (alpha 32~255) animation.
    paintEvent reads the global ACCENT directly, so calling update() on theme change is enough."""
    def __init__(self, direction='up', parent=None):
        super().__init__(parent)
        self._direction = direction
        self.setFixedHeight(36)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self._phase = 0.0
        self._timer = QTimer(self)
        self._timer.setInterval(30)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def _tick(self):
        import math as _math
        self._phase += 0.08
        if self._phase > _math.pi * 2:
            self._phase -= _math.pi * 2
        self.update()

    def paintEvent(self, e):
        import math as _math
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        ac = QColor(ACCENT)
        is_up = (self._direction == 'up')

        s    = _math.sin(self._phase)
        offset = s * 3.0
        fade   = (s + 1) / 2

        dy = -offset if is_up else offset

        # ── Gradient background ──────────────────────
        grad = QLinearGradient(0, 0, 0, h)
        base_alpha = int(32 + fade * 24)
        c_solid = QColor(ac); c_solid.setAlpha(base_alpha)
        c_clear = QColor(ac); c_clear.setAlpha(0)
        if is_up:
            grad.setColorAt(0.0, c_solid); grad.setColorAt(1.0, c_clear)
        else:
            grad.setColorAt(0.0, c_clear); grad.setColorAt(1.0, c_solid)
        painter.fillRect(self.rect(), QBrush(grad))

        # ── Three triangles (horizontally centered, more opaque toward the right) ──
        tw, th = 9, 5
        gap    = 8
        n      = 3
        total_w = n * tw + (n - 1) * gap
        sx = (w - total_w) / 2
        cy = h / 2 + dy

        base_alphas = [90, 170, 255]
        anim_alphas = [int(a * (0.35 + fade * 0.65)) for a in base_alphas]

        for i in range(n):
            x = sx + i * (tw + gap)
            col = QColor(ac); col.setAlpha(anim_alphas[i])
            painter.setBrush(QBrush(col))
            painter.setPen(Qt.PenStyle.NoPen)

            if is_up:
                pts = [QPointF(x,        cy + th / 2),
                       QPointF(x + tw,   cy + th / 2),
                       QPointF(x + tw/2, cy - th / 2)]
            else:
                pts = [QPointF(x,        cy - th / 2),
                       QPointF(x + tw,   cy - th / 2),
                       QPointF(x + tw/2, cy + th / 2)]

            painter.drawPolygon(QPolygonF(pts))

        painter.end()


class ScrollHintArea(QScrollArea):
    """QScrollArea that shows a _ScrollHint overlay based on scroll position."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._hint_top = _ScrollHint('up',   self)
        self._hint_bot = _ScrollHint('down', self)
        for h in (self._hint_top, self._hint_bot):
            h.hide()
        self.verticalScrollBar().valueChanged.connect(self._sync)

    def refresh_style(self):
        """Called on theme change — since paintEvent reads ACCENT directly, just trigger a repaint."""
        self._hint_top.update()
        self._hint_bot.update()

    def _sync(self):
        sb = self.verticalScrollBar()
        self._hint_top.setVisible(sb.value() > sb.minimum())
        self._hint_bot.setVisible(sb.value() < sb.maximum())
        self._reposition()

    def _reposition(self):
        vg = self.viewport().geometry()
        w  = vg.width(); h = 36
        self._hint_top.setGeometry(vg.x(), vg.y(), w, h)
        self._hint_bot.setGeometry(vg.x(), vg.bottom() - h, w, h)
        self._hint_top.raise_()
        self._hint_bot.raise_()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._sync()

    def showEvent(self, e):
        super().showEvent(e)
        self._sync()


# ── Batch Renamer DropZone ─────────────────────
class BatchDropZone(QLabel):
    folder_dropped = Signal(list)
    def __init__(self, key1, key2="", obj_name="dropZone"):
        super().__init__()
        self._key1=key1; self._key2=key2; self._obj=obj_name
        self.setObjectName(obj_name); self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAcceptDrops(True); self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumHeight(120); self.setTextFormat(Qt.TextFormat.RichText)
        self.set_idle()
    def set_idle(self):
        t=_T
        self.setStyleSheet(f"QLabel#{self._obj}{{border:1.5px dashed {t['BORDER']};border-radius:10px;background:{t['SURFACE']};padding:14px;}}")
        line1=_t(self._key1) if self._key1 else ""
        line2=_t(self._key2) if self._key2 else ""
        sub=(f"<div style='color:{t['DISABLED']};font-size:13px;margin-top:4px;'>{line2}</div>") if line2 else ""
        self.setText(f"<div style='text-align:center;'><div style='font-size:28px;'>📂</div><div style='color:{t['MUTED']};font-size:13px;margin-top:6px;'>{line1}</div>{sub}</div>")
    def set_hover(self):
        t=_T
        self.setStyleSheet(f"QLabel#{self._obj}{{border:2px dashed {t['ACCENT']};border-radius:10px;background:{_accent_alpha(0.07)};padding:14px;}}")
        self.setText(f"<div style='text-align:center;'><div style='font-size:28px;'>📂</div><div style='color:{t['ACCENT']};font-size:13px;margin-top:6px;'>{_t('tf_drop_hover')}</div></div>")
    def dragEnterEvent(self,e):
        if e.mimeData().hasUrls(): e.acceptProposedAction(); self.set_hover()
        else: e.ignore()
    def dragMoveEvent(self,e):
        if e.mimeData().hasUrls(): e.acceptProposedAction()
        else: e.ignore()
    def dragLeaveEvent(self,e): self.set_idle()
    def dropEvent(self,e):
        self.set_idle()
        dirs=[u.toLocalFile() for u in e.mimeData().urls() if os.path.isdir(u.toLocalFile())]
        if dirs: self.folder_dropped.emit(dirs)
        else: e.ignore()

# ── Tag Editor DropZone ────────────────────────
class TagDropZone(QLabel):
    folder_dropped = Signal(str)
    files_dropped  = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tagDropZone")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAcceptDrops(True)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumHeight(120)
        self.setTextFormat(Qt.TextFormat.RichText)
        self.set_idle()

    def set_idle(self):
        t = _T
        self.setStyleSheet(
            f"QLabel#tagDropZone{{border:1.5px dashed {t['BORDER']};"
            f"border-radius:10px;background:{t['SURFACE']};padding:14px;}}")
        self.setText(
            f"<div style='text-align:center;'>"
            f"<div style='font-size:28px;font-family:{_EMOJI_FONT_FAMILY};'>🏷️</div>"
            f"<div style='color:{t['MUTED']};font-size:13px;margin-top:6px;'>"
            f"{_t('tag_drop1')}</div>"
            f"<div style='color:{t['DISABLED']};font-size:13px;margin-top:4px;'>"
            f"{_t('tag_drop2')}</div>"
            f"</div>")

    def set_hover(self):
        t = _T
        self.setStyleSheet(
            f"QLabel#tagDropZone{{border:2px dashed {t['ACCENT']};"
            f"border-radius:10px;background:{_accent_alpha(0.07)};padding:14px;}}")
        self.setText(
            f"<div style='text-align:center;'>"
            f"<div style='font-size:28px;font-family:{_EMOJI_FONT_FAMILY};'>🏷️</div>"
            f"<div style='color:{t['ACCENT']};font-size:13px;margin-top:6px;'>"
            f"{_t('tf_drop_hover')}</div></div>")

    def mousePressEvent(self, e):
        if e.button() != Qt.MouseButton.LeftButton: return
        folder = QFileDialog.getExistingDirectory(self, _t('btn_add_folder'))
        if folder: self.folder_dropped.emit(folder)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls(): e.acceptProposedAction(); self.set_hover()
        else: e.ignore()

    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls(): e.acceptProposedAction()
        else: e.ignore()

    def dragLeaveEvent(self, e): self.set_idle()

    def dropEvent(self, e):
        self.set_idle()
        if not e.mimeData().hasUrls(): e.ignore(); return
        files = []
        for url in e.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isdir(path): self.folder_dropped.emit(path)
            elif os.path.isfile(path): files.append(path)
        if files: self.files_dropped.emit(files)
        e.acceptProposedAction()

# ── Text Merger DropZone ───────────────────────
class MergeDropZone(QLabel):
    files_dropped = Signal(list)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
    def dragEnterEvent(self,e):
        if e.mimeData().hasUrls(): e.acceptProposedAction()
        else: e.ignore()
    def dragMoveEvent(self,e):
        if e.mimeData().hasUrls(): e.acceptProposedAction()
        else: e.ignore()
    def dropEvent(self,e):
        if e.mimeData().hasUrls():
            paths=[u.toLocalFile() for u in e.mimeData().urls() if u.isLocalFile()]
            self.files_dropped.emit(paths); e.acceptProposedAction()
        else: e.ignore()

class MergeFileTree(QTreeWidget):
    """Text Merger's dedicated QTreeWidget — supports external file drops + internal reorder drags."""
    files_dropped = Signal(list)
    order_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(2)
        self.setHeaderLabels([_t("tag_col_filename"), _t("tag_col_path")])
        self.setRootIsDecorated(False)
        self.setUniformRowHeights(True)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # Use DragDrop instead of InternalMove — when combining InternalMove + e.ignore(),
        # avoids the bug where Qt deletes the source item
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragEnabled(True)
        hdr = self.header()
        hdr.setSectionResizeMode(0, QHeaderView.Stretch)
        hdr.setSectionResizeMode(1, QHeaderView.Interactive)
        self.setColumnWidth(1, 180)
        self.setSortingEnabled(False)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls(): e.acceptProposedAction()
        else: super().dragEnterEvent(e)

    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls(): e.acceptProposedAction()
        else: super().dragMoveEvent(e)

    def startDrag(self, supported_actions):
        """Force CopyAction — blocks Qt's MoveAction auto-deletion of the source.
        The actual move is handled manually in dropEvent."""
        super().startDrag(Qt.DropAction.CopyAction)

    def dropEvent(self, e):
        if e.mimeData().hasUrls():
            paths = [u.toLocalFile() for u in e.mimeData().urls() if u.isLocalFile()]
            self.files_dropped.emit(paths); e.acceptProposedAction()
        elif e.source() is self:
            # internal drag — handled manually in DragDrop mode
            dragged = self.selectedItems()
            if not dragged:
                e.accept(); return
            target = self.itemAt(e.pos())
            if target is None:
                # drop in empty area → move to the very end
                src_rows = sorted([self.indexOfTopLevelItem(i) for i in dragged], reverse=True)
                saved = []
                for row in src_rows:
                    saved.insert(0, self.takeTopLevelItem(row))
                for item in saved:
                    self.addTopLevelItem(item)
                self.selectionModel().clearSelection()
                for item in saved: item.setSelected(True)
                e.acceptProposedAction()
                self.order_changed.emit()
                return
            if target in dragged:
                e.accept(); return  # dropped on itself — do nothing
            target_row = self.indexOfTopLevelItem(target)
            drop_above = e.pos().y() < self.visualItemRect(target).center().y()
            src_rows = sorted([self.indexOfTopLevelItem(i) for i in dragged], reverse=True)
            saved = []
            for row in src_rows:
                saved.insert(0, self.takeTopLevelItem(row))
                if row < target_row:
                    target_row -= 1
            insert_row = target_row if drop_above else target_row + 1
            for i, item in enumerate(saved):
                self.insertTopLevelItem(insert_row + i, item)
            self.selectionModel().clearSelection()
            for i in range(len(saved)):
                t = self.topLevelItem(insert_row + i)
                if t: t.setSelected(True)
            e.acceptProposedAction()
            self.order_changed.emit()
        else:
            e.ignore()

# ── Text Converter DropZone (new in v1.0.6 §5.2 #7) ───
class TextConverterDropZone(QLabel):
    """Drag-and-drop zone dedicated to Text Converter (new in v1.0.6 #7).

    Mirrors the BulkFixerDropZone pattern but with Text Converter-specific requirements:
    - dynamically allows .txt (txt2epub) / .epub (epub2txt) based on mode
    - folder drops not supported (Text Converter keeps the existing no-_btn_add_folder policy)
    - text/icon refreshes immediately on mode switch
    """
    files_dropped = Signal(list)   # list of files with extensions matching the mode

    def __init__(self, parent=None):
        super().__init__(parent)
        self._mode = "txt2epub"
        self.setObjectName("tcDropZone")
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumHeight(110)
        self.setTextFormat(Qt.TextFormat.RichText)
        self.set_idle()

    def set_mode(self, mode: str):
        """Mode switch — refresh dropzone text/icon immediately."""
        self._mode = mode
        self.set_idle()

    def _current_icon(self):
        return "📚" if self._mode == "epub2txt" else "📄"

    def _current_main_key(self):
        return 'conv_drop_epub' if self._mode == "epub2txt" else 'conv_drop_txt'

    def _current_fmt_key(self):
        return 'conv_drop_epub_fmt' if self._mode == "epub2txt" else 'conv_drop_txt_fmt'

    def set_idle(self):
        t = _T
        self.setStyleSheet(
            f"QLabel#tcDropZone{{border:1.5px dashed {t['BORDER']};"
            f"border-radius:10px;background:{t['SURFACE']};padding:14px;"
            f"color:{t['TEXT']};}}")
        self.setText(
            f"<div style='text-align:center;'>"
            f"<div style='font-size:28px;line-height:1;font-family:{_EMOJI_FONT_FAMILY};'>"
            f"{self._current_icon()}</div>"
            f"<div style='color:{t['MUTED']};font-size:13px;margin-top:8px;'>"
            f"{_t(self._current_main_key())}</div>"
            f"<div style='color:{t['DISABLED']};font-size:13px;margin-top:4px;'>"
            f"{_t(self._current_fmt_key())}</div>"
            f"</div>")

    def set_hover(self):
        t = _T
        self.setStyleSheet(
            f"QLabel#tcDropZone{{border:2px dashed {t['ACCENT']};"
            f"border-radius:10px;background:{_accent_alpha(0.07)};padding:14px;}}")
        self.setText(
            f"<div style='text-align:center;'>"
            f"<div style='font-size:28px;line-height:1;font-family:{_EMOJI_FONT_FAMILY};'>"
            f"{self._current_icon()}</div>"
            f"<div style='color:{t['ACCENT']};font-size:13px;margin-top:8px;'>"
            f"{_t('tf_drop_hover')}</div>"
            f"</div>")

    def refresh_style(self):
        self.set_idle()

    def _has_valid(self, mime):
        """Check whether at least one file with a mode-matching extension is present. All folders are rejected."""
        if not mime.hasUrls(): return False
        ext = ".epub" if self._mode == "epub2txt" else ".txt"
        for u in mime.urls():
            if not u.isLocalFile(): continue
            p = u.toLocalFile()
            if os.path.isdir(p): continue  # folders not allowed
            if p.lower().endswith(ext): return True
        return False

    def dragEnterEvent(self, e):
        if self._has_valid(e.mimeData()):
            self.set_hover(); e.acceptProposedAction()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if self._has_valid(e.mimeData()): e.acceptProposedAction()
        else: e.ignore()

    def dragLeaveEvent(self, e):
        self.set_idle()

    def dropEvent(self, e):
        self.set_idle()
        ext = ".epub" if self._mode == "epub2txt" else ".txt"
        valid_files = []
        for url in e.mimeData().urls():
            if not url.isLocalFile(): continue
            p = url.toLocalFile()
            if os.path.isdir(p): continue  # ignore folders (not supported)
            if p.lower().endswith(ext):
                valid_files.append(p)
        if valid_files:
            self.files_dropped.emit(valid_files)
            e.acceptProposedAction()
        else:
            e.ignore()


# ── Text Converter FileList ─────────────────────
class TextConverterFileList(QTreeWidget):
    """Text Converter-dedicated file list — 2 columns (filename|path), header-click sort.

    v1.0.6 #7: switched from InternalMove → DragDrop. External drops are handled by TextConverterDropZone.
    This widget is for internal reordering only. Mirrors the BulkFixerFileList pattern.
    """
    files_changed = Signal(int)
    order_changed = Signal()  # v1.0.6 #7: signal fired when drag-reorder completes

    def __init__(self, parent=None):
        super().__init__(parent)
        self._files = []; self._mode = "txt2epub"
        self._sort_asc = False  # ascending on first click
        self.setColumnCount(2)
        self.setHeaderLabels([_t('tag_col_filename'), _t('tag_col_path')])
        self.setRootIsDecorated(False)
        self.setUniformRowHeights(True)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # v1.0.6 #7: DragDrop mode (avoids the Qt auto-delete bug from combining InternalMove + e.ignore())
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragEnabled(True)
        self.setSortingEnabled(False)
        hdr = self.header()
        hdr.setSectionResizeMode(0, QHeaderView.Stretch)
        hdr.setSectionResizeMode(1, QHeaderView.Interactive)
        self.setColumnWidth(1, 180)
        hdr.setSortIndicatorShown(True)
        # v1.0.6 #7: workaround for Qt disabling header clicks when setSortingEnabled(False)
        # — mirrors the pattern validated in BulkFixerFileList
        hdr.setSectionsClickable(True)
        hdr.sectionClicked.connect(self._on_header_clicked)

    def _on_header_clicked(self, col):
        if col == 0:
            self._sort_asc = not self._sort_asc
            order = Qt.SortOrder.AscendingOrder if self._sort_asc else Qt.SortOrder.DescendingOrder
            self.header().setSortIndicator(0, order)
            self.sort_files(self._sort_asc)

    def sort_files(self, ascending=True):
        self._files.sort(key=natural_sort_key, reverse=not ascending)
        self._rebuild()

    # v1.0.6: UserRole for storing the pure file path (avoids toolTip pollution — same policy as MergeEncodingDelegate)
    _PATH_ROLE = Qt.ItemDataRole.UserRole + 4

    def _make_item(self, path):
        item = QTreeWidgetItem([os.path.basename(path), os.path.dirname(path)])
        item.setToolTip(0, path); item.setToolTip(1, path)
        item.setData(0, self._PATH_ROLE, path)  # v1.0.6: pure path
        return item

    def _rebuild(self):
        self.clear()
        for p in self._files:
            self.addTopLevelItem(self._make_item(p))

    def set_mode(self, mode):
        self._mode = mode; self.clear_files(); self.viewport().update()

    def add_files(self, paths, warn_fn=None):
        added = []; wrong = []
        ext = ".epub" if self._mode == "epub2txt" else ".txt"
        for p in paths:
            if not p: continue
            if not p.lower().endswith(ext): wrong.append(os.path.basename(p)); continue
            if p not in self._files: self._files.append(p); added.append(p)
        if wrong and warn_fn: warn_fn(wrong)
        for p in added:
            self.addTopLevelItem(self._make_item(p))
        if added: self.files_changed.emit(len(self._files))

    def remove_selected(self):
        rows = sorted({self.indexOfTopLevelItem(i) for i in self.selectedItems()}, reverse=True)
        for r in rows:
            self.takeTopLevelItem(r); del self._files[r]
        self.files_changed.emit(len(self._files))

    def clear_files(self):
        self._files.clear(); self.clear(); self.files_changed.emit(0)

    def move_selection(self, delta):
        rows = sorted({self.indexOfTopLevelItem(i) for i in self.selectedItems()})
        if not rows: return
        if delta < 0 and rows[0] == 0: return
        if delta > 0 and rows[-1] == len(self._files) - 1: return
        new_rows = []
        for r in (reversed(rows) if delta > 0 else rows):
            nr = r + delta
            self._files[r], self._files[nr] = self._files[nr], self._files[r]
            item = self.takeTopLevelItem(r); self.insertTopLevelItem(nr, item)
            new_rows.append(nr)
        self.selectionModel().clearSelection()
        for r in new_rows: self.topLevelItem(r).setSelected(True)

    @property
    def files(self): return list(self._files)

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace): self.remove_selected()
        else: super().keyPressEvent(e)

    def _sync(self):
        # v1.0.6: prefer _PATH_ROLE; fall back for backwards compatibility
        def _p(it):
            v = it.data(0, self._PATH_ROLE)
            return v if v else it.toolTip(0)
        self._files = [_p(self.topLevelItem(i))
                       for i in range(self.topLevelItemCount())]

    def startDrag(self, supported_actions):
        """v1.0.6 #7: force CopyAction — blocks Qt's MoveAction auto-deletion of the source.
        The actual move is handled manually in dropEvent. (Mirrors the BulkFixerFileList pattern.)"""
        super().startDrag(Qt.DropAction.CopyAction)

    def dragEnterEvent(self, e):
        # v1.0.6 #7: internal reorder only (external drops are handled by TextConverterDropZone)
        if e.source() is self: e.acceptProposedAction()
        else: e.ignore()

    def dragMoveEvent(self, e):
        if e.source() is self: e.acceptProposedAction()
        else: e.ignore()

    def dropEvent(self, e):
        """v1.0.6 #7: manual internal reorder (mirrors the BulkFixerFileList pattern)."""
        if e.source() is not self:
            e.ignore(); return
        dragged = self.selectedItems()
        if not dragged:
            e.accept(); return
        target = self.itemAt(e.pos())
        if target is None:
            # drop in empty area → move to the very end
            src_rows = sorted([self.indexOfTopLevelItem(i) for i in dragged], reverse=True)
            saved = []
            for row in src_rows:
                saved.insert(0, self.takeTopLevelItem(row))
            for item in saved:
                self.addTopLevelItem(item)
            self.selectionModel().clearSelection()
            for item in saved: item.setSelected(True)
            e.acceptProposedAction()
            self._sync()
            self.order_changed.emit()
            return
        if target in dragged:
            e.accept(); return  # dropped on itself — ignore
        target_row = self.indexOfTopLevelItem(target)
        drop_above = e.pos().y() < self.visualItemRect(target).center().y()
        src_rows = sorted([self.indexOfTopLevelItem(i) for i in dragged], reverse=True)
        saved = []
        for row in src_rows:
            saved.insert(0, self.takeTopLevelItem(row))
            if row < target_row:
                target_row -= 1
        insert_row = target_row if drop_above else target_row + 1
        for i, item in enumerate(saved):
            self.insertTopLevelItem(insert_row + i, item)
        self.selectionModel().clearSelection()
        for i in range(len(saved)):
            t = self.topLevelItem(insert_row + i)
            if t: t.setSelected(True)
        e.acceptProposedAction()
        self._sync()
        self.order_changed.emit()

# ── Text Converter Worker ───────────────────────
class ConvertWorker(QThread):
    sig_progress      = Signal(int)
    sig_file_progress = Signal(int, str)      # current file progress (0–100, filename)
    sig_log           = Signal(str, str)
    sig_done          = Signal(bool, int, int, str)
    sig_files         = Signal(list)  # list of converted files (for undo)
    def __init__(self,files,mode,opts,odir):
        super().__init__(); self.files=files; self.mode=mode; self.opts=opts; self.odir=odir
    def run(self):
        _prevent_sleep()
        try:
            ok=fail=0; out_dir=self.odir or ""; n=len(self.files); created_files=[]
            for i,path in enumerate(self.files):
                self.sig_progress.emit(int((i/n)*95))
                fname = os.path.basename(path)
                self.sig_file_progress.emit(0, fname)
                self.sig_log.emit(f"({i+1}/{n}) {fname}","")
                try:
                    base=os.path.splitext(fname)[0]
                    d=self.odir if self.odir else str(Path(path).parent.resolve())
                    self.sig_file_progress.emit(20, fname)
                    if self.mode=="epub2txt":
                        out_path=os.path.join(d,base+".txt")
                        res,ch=epub_to_text(path,self.opts)
                        self.sig_file_progress.emit(70, fname)
                        enc=self.opts.get("encoding","utf-8")
                        with open(out_path,"w",encoding=enc,errors="replace") as f: f.write(res)
                        self.sig_log.emit(f"  → {os.path.basename(out_path)}  ({ch} ch)","ok")
                    else:
                        out_path=os.path.join(d,base+".epub")
                        file_opts=dict(self.opts); file_opts["encoding"], _ = alchemy_detect_encoding(path)
                        self.sig_file_progress.emit(30, fname)
                        ch=txt_to_epub(path,out_path,file_opts)
                        self.sig_log.emit(f"  → {os.path.basename(out_path)}  ({ch} ch)","ok")
                    self.sig_file_progress.emit(100, fname)
                    created_files.append(out_path); out_dir=d; ok+=1
                except Exception as e:
                    self.sig_log.emit(f"  ✗ {e}","err"); fail+=1
                    self.sig_file_progress.emit(0, fname)
            self.sig_progress.emit(100)
            if created_files: self.sig_files.emit(created_files)
            self.sig_done.emit(ok>0,ok,fail,out_dir)
        finally:
            _allow_sleep()


# ═══════════════════════════════════════════════
# Tab 1: Batch Renamer panel
# ═══════════════════════════════════════════════
class BatchRenamerPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._f_groups=[]; self._f_preview=[]
        self._p_groups=[]; self._p_preview=[]; self._undo_data=None
        self._build()

    def _build(self):
        outer=QVBoxLayout(self); outer.setContentsMargins(0,0,0,0); outer.setSpacing(0)

        # ── Tab bar (unified Tag Editor style) ──
        tab_bar=QWidget(); tab_bar.setFixedHeight(50)
        tbl=QHBoxLayout(tab_bar); tbl.setContentsMargins(8,0,0,0); tbl.setSpacing(0)
        self._main_tab_btns={}
        for key,label in [("folder",_t("batch_sub_folder")),("file",_t("batch_sub_file"))]:
            btn=QPushButton(label); btn.setCheckable(False)
            btn.clicked.connect(lambda _,k=key: self._switch_main_tab(k))
            tbl.addWidget(btn); self._main_tab_btns[key]=btn
        tbl.addStretch(); outer.addWidget(tab_bar)

        sep=QFrame(); sep.setFrameShape(QFrame.HLine); sep.setObjectName("tab_sep")
        outer.addWidget(sep)

        # ── Tab content stack ────────────────────
        self._main_stack=QStackedWidget()
        self._main_stack.addWidget(self._build_folder_tab())   # index 0
        self._main_stack.addWidget(self._build_file_tab())     # index 1
        outer.addWidget(self._main_stack,1)

        self._cur_main_tab="folder"
        self._update_main_tab_style()

    def _undo(self):
        """Undo the last rename operation once."""
        if not self._undo_data: return
        kind, undo_map = self._undo_data
        errors=[]; done=0
        # before undo — close any Explorer window holding the changed path (cur)
        undo_folders = [cur for cur, _ in undo_map]
        closed_folders = self._close_explorer_for_paths(undo_folders)
        _glog(f"↩ [Batch Renamer] undo — {len(undo_map)} item(s)")
        # reversed: undo_map is stored from deepest → shallowest
        # undo must go shallow (parent) → deep (child) so paths stay valid
        pending_undo = []
        for cur, orig in reversed(undo_map):
            try:
                if os.path.exists(cur):
                    os.rename(cur, orig); done+=1
                    _glog(f"  ✅ {os.path.basename(cur)}  →  {os.path.basename(orig)}")
                else:
                    errors.append(f"{os.path.basename(cur)}: file not found")
                    _glog(f"  ⚠ {os.path.basename(cur)}: file not found")
            except OSError as e:
                if getattr(e, 'winerror', None) == 5:
                    pending_undo.append((cur, orig))
                    _glog(f"  ⏳ {os.path.basename(cur)}: locked — retry queued")
                else:
                    errors.append(f"{os.path.basename(cur)}: {e}")
                    _glog(f"  ❌ {os.path.basename(cur)}: {e}")
        # WinError 5 failures — retry after a 2-second wait
        if pending_undo:
            import time
            _glog(f"  ⏳ [retry] {len(pending_undo)} item(s) — waiting 2 seconds")
            time.sleep(2.0)
            for attempt in range(5):
                still = []
                for cur, orig in pending_undo:
                    try:
                        if os.path.exists(cur):
                            os.rename(cur, orig); done += 1
                            _glog(f"  ✅ {os.path.basename(cur)}  →  {os.path.basename(orig)} (retry {attempt+1})")
                        else:
                            errors.append(f"{os.path.basename(cur)}: file not found")
                    except OSError as e:
                        if getattr(e, 'winerror', None) == 5:
                            still.append((cur, orig))
                        else:
                            errors.append(f"{os.path.basename(cur)}: {e}")
                pending_undo = still
                if not pending_undo: break
                time.sleep(1.0)
            for cur, orig in pending_undo:
                errors.append(f"{os.path.basename(cur)}: access denied — close Explorer and try again")
                _glog(f"  ❌ {os.path.basename(cur)}: final failure")
        self._undo_data = None
        for attr in ('_f_btn_undo', '_p_btn_undo'):
            if hasattr(self, attr): getattr(self, attr).setEnabled(False)
        # after undo, reset group data, table, and buttons
        # — prevents the issue where the dropzone refuses new drags if _f_groups remain
        if hasattr(self, '_f_clear'): self._f_clear()
        if hasattr(self, '_p_clear'): self._p_clear()
        msg = _t('tag_apply_done', n=done, label=_t('dlg_undo'))
        if errors: msg += f'  {_t("dlg_done_err")} ×{len(errors)}'
        _glog(f"  done: {msg}")
        if errors: _dlg_warn(self, _t('dlg_undo'), msg + "\n\n" + "\n".join(errors[:10]))
        else: _dlg_info(self, _t('dlg_undo'), msg)
        # after undo, reopen any Explorer windows that were closed
        self._reopen_explorer(closed_folders)

    def refresh_btn_styles(self):
        """On theme change, directly refresh buttons that the QSS cascade does not reach."""
        folder_ss = (f"QPushButton{{background:{ACCENT};border:none;color:white;"
                     f"padding:9px 16px;font-weight:600;border-radius:8px;}}"
                     f"QPushButton:hover{{background:{ACCENT_HOVER};}}"
                     f"QPushButton:disabled{{background:{DISABLED};color:rgba(255,255,255,0.5);}}")
        file_ss   = (f"QPushButton{{background:{ACCENT};border:none;color:white;"
                     f"padding:9px 16px;font-weight:600;border-radius:8px;}}"
                     f"QPushButton:hover{{background:{ACCENT_HOVER};}}"
                     f"QPushButton:disabled{{background:{DISABLED};color:rgba(255,255,255,0.5);}}")
        secondary_ss = (f"QPushButton{{background:{SURFACE};border:1.5px solid {BTN_BORDER_H};"
                        f"color:{TEXT};border-radius:8px;padding:5px 12px;}}"
                        f"QPushButton:hover{{background:{SRF2};border-color:{ACCENT};}}"
                        f"QPushButton:pressed{{background:{BTN_PRESSED};}}"
                        f"QPushButton:disabled{{background:{SRF2};color:{DISABLED};}}")
        if hasattr(self, '_f_btn_add'):   self._f_btn_add.setStyleSheet(folder_ss)
        if hasattr(self, '_p_btn_fadd'):  self._p_btn_fadd.setStyleSheet(file_ss)
        if hasattr(self, '_f_btn_clear'): self._f_btn_clear.setStyleSheet(secondary_ss)
        if hasattr(self, '_p_btn_clear'): self._p_btn_clear.setStyleSheet(secondary_ss)
        if hasattr(self, '_f_btn_undo'): self._f_btn_undo.setStyleSheet(secondary_ss)
        if hasattr(self, '_p_btn_undo'): self._p_btn_undo.setStyleSheet(secondary_ss)
        # refresh SVG icon colors (secondary buttons only — primary stays white)
        _isz = QSize(20,20)
        for attr in ('_f_btn_preview', '_p_btn_preview'):
            if hasattr(self, attr): getattr(self, attr).setIcon(_svg_icon_dual('magnifier', ACCENT, 'white')); getattr(self, attr).setIconSize(_isz)

    def _update_main_tab_style(self):
        for key,btn in self._main_tab_btns.items():
            active=(key==self._cur_main_tab)
            btn.setStyleSheet(
                f"QPushButton{{background:{_accent_alpha(0.12) if active else 'transparent'};"
                f"border:none;border-bottom:2px solid {ACCENT if active else 'transparent'};"
                f"border-radius:0;padding:8px 16px;"
                f"color:{ACCENT if active else MUTED};"
                f"font-size:13px;font-weight:{'600' if active else '500'};min-width:110px;}}"
            )

    def _switch_main_tab(self, key):
        self._cur_main_tab=key
        self._main_stack.setCurrentIndex(0 if key=="folder" else 1)
        self._update_main_tab_style()

    # ── Folder tab ────────────────────────────
    def _build_folder_tab(self):
        w=QWidget(); lay=QHBoxLayout(w); lay.setContentsMargins(0,8,0,0); lay.setSpacing(0)
        sp=QSplitter(Qt.Orientation.Horizontal); sp.setHandleWidth(1)
        left=QWidget(); ll=QVBoxLayout(left); ll.setContentsMargins(8,0,10,8); ll.setSpacing(8)
        self._f_drop=BatchDropZone("batch_drop1_f","batch_drop2_f","dropZoneFolder")
        self._f_drop.folder_dropped.connect(self._f_on_dropped)
        ll.addWidget(self._f_drop)
        br=QHBoxLayout(); br.setSpacing(8)
        btn_add=QPushButton(_t("batch_btn_folder_pick")); btn_add.setObjectName("btn_folder_add")
        btn_add.setIcon(_svg_icon('folder_open', 'white')); btn_add.setIconSize(QSize(20,20))
        btn_add.clicked.connect(self._f_pick)
        self._f_btn_add = btn_add  # keep reference for theme refresh
        self._f_lbl_count=QLabel(_t("batch_count_folder", g=0, f=0)); self._f_lbl_count.setObjectName("count_lbl")
        btn_clear=QPushButton(_t('btn_del_all')); self._f_btn_clear=btn_clear; btn_clear.setMinimumWidth(80); btn_clear.setFixedHeight(36); btn_clear.clicked.connect(self._f_clear)
        br.addWidget(btn_add); br.addStretch(); br.addWidget(self._f_lbl_count); br.addWidget(btn_clear)
        ll.addLayout(br)
        self._f_table=QTableWidget(0,3)
        self._f_table.setHorizontalHeaderLabels([_t("batch_col_folder"),_t("batch_col_arrow"),_t("batch_col_new")])
        self._f_table.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        self._f_table.horizontalHeader().setSectionResizeMode(1,QHeaderView.Fixed)
        self._f_table.horizontalHeader().setSectionResizeMode(2,QHeaderView.Stretch)
        self._f_table.setColumnWidth(1,36); self._f_table.verticalHeader().setVisible(False)
        self._f_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._f_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        ll.addWidget(self._f_table)
        ar=QHBoxLayout(); ar.setSpacing(8)
        self._f_btn_preview=QPushButton(_t("btn_preview")); self._f_btn_preview.setObjectName("btn_preview")
        self._f_btn_preview.setIcon(_svg_icon_dual('magnifier', ACCENT, 'white')); self._f_btn_preview.setIconSize(QSize(20,20))
        self._f_btn_preview.setFixedHeight(48); self._f_btn_preview.setEnabled(False); self._f_btn_preview.clicked.connect(self._f_do_preview)
        self._f_btn_rename=QPushButton(_t("batch_btn_rename")); self._f_btn_rename.setObjectName("btn_rename")
        self._f_btn_rename.setIcon(_svg_icon('check', 'white')); self._f_btn_rename.setIconSize(QSize(18,18))
        self._f_btn_rename.setFixedHeight(48); self._f_btn_rename.setEnabled(False); self._f_btn_rename.clicked.connect(self._f_do_rename)
        self._f_btn_undo=QPushButton(_t('btn_undo')); self._f_btn_undo.setObjectName("btn_undo")
        self._f_btn_undo.setFixedHeight(48); self._f_btn_undo.setEnabled(False)
        self._f_btn_undo.clicked.connect(self._undo)
        ar.addWidget(self._f_btn_preview, 1); ar.addWidget(self._f_btn_rename, 1); ar.addWidget(self._f_btn_undo, 1)
        ll.addLayout(ar); sp.addWidget(left)
        # right-side settings
        rs=ScrollHintArea(); self._sa_folder=rs
        rs.setWidgetResizable(True); rs.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff); rs.setFixedWidth(330)
        rw=QWidget(); rl=QVBoxLayout(rw); rl.setContentsMargins(12,6,8,40); rl.setSpacing(8)

        # option tab bar (Tag Editor style)
        # ── Collapsible usage hint (default: collapsed) ─────────────────
        self._f_hint_open = False
        self._f_hint_btn = QPushButton(f"  {_t('batch_usage_title')}  ▼")
        self._f_hint_btn.setFixedHeight(28)
        self._f_hint_btn.setObjectName("hint_toggle_btn")
        self._f_hint_btn.setStyleSheet(
            f"QPushButton{{background:transparent;border:none;border-bottom:1px solid {BORDER};"
            f"border-radius:0;text-align:left;padding:0 6px;font-size:12px;"
            f"color:{MUTED};font-weight:600;}}"
            f"QPushButton:hover{{color:{ACCENT};}}")
        self._hint_folder = QLabel(_t('batch_hint_folder'))
        self._hint_folder.setObjectName("hint_box")
        self._hint_folder.setTextFormat(Qt.TextFormat.RichText)
        self._hint_folder.setWordWrap(True)
        self._hint_folder.setVisible(False)
        def _f_toggle_hint():
            self._f_hint_open = not self._f_hint_open
            self._hint_folder.setVisible(self._f_hint_open)
            arrow = "▲" if self._f_hint_open else "▼"
            self._f_hint_btn.setText(f"  {_t('batch_usage_title')}  {arrow}")
        self._f_hint_btn.clicked.connect(_f_toggle_hint)
        rl.addWidget(self._f_hint_btn)
        rl.addWidget(self._hint_folder)

        opt_bar=QWidget(); opt_bar.setFixedHeight(46)
        obl=QHBoxLayout(opt_bar); obl.setContentsMargins(0,0,0,0); obl.setSpacing(0)
        self._opt_tab_btns={}
        _opt_icons={"smart":"magnifier","seq":"list"}
        for key,label in [("smart",_t('batch_opt_smart')),("seq",_t('batch_opt_seq'))]:
            btn=QPushButton(label); btn.clicked.connect(lambda _,k=key: self._switch_opt_tab(k))
            icon_key=_opt_icons.get(key,'')
            if icon_key: btn.setIcon(_svg_icon(icon_key, MUTED)); btn.setIconSize(QSize(16,16))
            obl.addWidget(btn); self._opt_tab_btns[key]=btn
        obl.addStretch(); rl.addWidget(opt_bar)

        opt_sep=QFrame(); opt_sep.setFrameShape(QFrame.HLine); opt_sep.setObjectName("tab_sep")
        rl.addWidget(opt_sep)

        self._opt_stack=QStackedWidget()
        self._opt_stack.addWidget(self._build_smart_tab())  # index 0
        self._opt_stack.addWidget(self._build_seq_tab())    # index 1
        rl.addWidget(self._opt_stack,stretch=1)

        self._cur_opt_tab="smart"
        self._update_opt_tab_style()

        rs.setWidget(rw); sp.addWidget(rs); sp.setSizes([700,300])
        lay.addWidget(sp); return w

    def _update_opt_tab_style(self):
        _opt_icons={"smart":"magnifier","seq":"list"}
        for key,btn in self._opt_tab_btns.items():
            active=(key==self._cur_opt_tab)
            btn.setStyleSheet(
                f"QPushButton{{background:{_accent_alpha(0.12) if active else 'transparent'};"
                f"border:none;border-bottom:2px solid {ACCENT if active else 'transparent'};"
                f"border-radius:0;padding:7px 14px;"
                f"color:{ACCENT if active else MUTED};"
                f"font-size:13px;font-weight:{'600' if active else '500'};min-width:90px;}}"
            )
            icon_key=_opt_icons.get(key,'')
            if icon_key:
                btn.setIcon(_svg_icon(icon_key, ACCENT if active else MUTED))
                btn.setIconSize(QSize(16,16))

    def _switch_opt_tab(self, key):
        self._cur_opt_tab=key
        self._opt_stack.setCurrentIndex(0 if key=="smart" else 1)
        self._update_opt_tab_style()


    def _build_smart_tab(self):
        w=QWidget(); lay=QVBoxLayout(w); lay.setSpacing(10); lay.setContentsMargins(4,4,4,4)
        ex=QLabel(f"Report 1.0  →  <span style='color:{ACCENT}'>01.0</span><br>Project 2-2  →  <span style='color:{ACCENT}'>02-2</span><br>Volume3-1ch  →  <span style='color:{ACCENT}'>03-1ch</span><br>Part03End  →  <span style='color:{ACCENT}'>03</span>")
        ex.setObjectName("ex_box"); ex.setTextFormat(Qt.TextFormat.RichText); lay.addWidget(ex)
        g1=QGroupBox(_t("batch_smart_pfx")); self._g_smart_pfx=g1; v1=QVBoxLayout(g1); v1.setSpacing(5)
        self._lbl_smart_pfx=QLabel(_t("batch_smart_prefix")); self._lbl_smart_pfx.setObjectName("field_lbl"); v1.addWidget(self._lbl_smart_pfx)
        self._sm_prefix=QLineEdit(); self._sm_prefix.setPlaceholderText(_t("sm_prefix_ph")); v1.addWidget(self._sm_prefix)
        self._lbl_smart_sfx=QLabel(_t("batch_smart_suffix")); self._lbl_smart_sfx.setObjectName("field_lbl"); v1.addWidget(self._lbl_smart_sfx)
        self._sm_suffix=QLineEdit(); self._sm_suffix.setPlaceholderText(_t("sm_suffix_ph")); v1.addWidget(self._sm_suffix)
        lay.addWidget(g1)
        g2=QGroupBox(_t("batch_smart_common")); self._g_smart_common=g2; v2=QVBoxLayout(g2)
        self._rb_auto=QRadioButton(_t("batch_smart_auto")); self._rb_manual=QRadioButton(_t("batch_smart_manual")); self._rb_none=QRadioButton(_t("batch_smart_none"))
        self._rb_auto.setChecked(True)
        bg=QButtonGroup(self)
        for rb in (self._rb_auto,self._rb_manual,self._rb_none): bg.addButton(rb); v2.addWidget(rb)
        self._sm_manual_pfx=QLineEdit(); self._sm_manual_pfx.setPlaceholderText(_t("batch_smart_manual_ph")); self._sm_manual_pfx.setEnabled(False)
        self._rb_manual.toggled.connect(self._sm_manual_pfx.setEnabled); v2.addWidget(self._sm_manual_pfx)
        lay.addWidget(g2); lay.addStretch(); return w

    def _build_seq_tab(self):
        w=QWidget(); lay=QVBoxLayout(w); lay.setSpacing(10); lay.setContentsMargins(4,4,4,4)
        g0=QGroupBox(_t("batch_seq_reset")); self._g_seq_reset=g0; v0=QVBoxLayout(g0)
        self._rb_seq_global=QRadioButton(_t("batch_seq_global")); self._rb_seq_reset=QRadioButton(_t("batch_seq_pergroup"))
        self._rb_seq_global.setChecked(True)
        bg0=QButtonGroup(self); bg0.addButton(self._rb_seq_global); bg0.addButton(self._rb_seq_reset)
        v0.addWidget(self._rb_seq_global); v0.addWidget(self._rb_seq_reset); lay.addWidget(g0)
        g1=QGroupBox(_t("batch_seq_start")); self._g_seq_start=g1; h1=QHBoxLayout(g1)
        self._rb_s0=QRadioButton(_t("batch_seq_from0")); self._rb_s1=QRadioButton(_t("batch_seq_from1")); self._rb_s0.setChecked(True)
        bg1=QButtonGroup(self); bg1.addButton(self._rb_s0); bg1.addButton(self._rb_s1)
        h1.addWidget(self._rb_s0); h1.addWidget(self._rb_s1); lay.addWidget(g1)
        g2=QGroupBox(_t("batch_seq_digits")); self._g_seq_digits=g2; v2=QVBoxLayout(g2)
        self._rb_d_auto=QRadioButton(_t("batch_seq_auto")); self._rb_d2=QRadioButton(_t("batch_seq_2d")); self._rb_d3=QRadioButton(_t("batch_seq_3d")); self._rb_d4=QRadioButton(_t("batch_seq_4d"))
        self._rb_d_auto.setChecked(True)
        bg2=QButtonGroup(self)
        for rb in (self._rb_d_auto,self._rb_d2,self._rb_d3,self._rb_d4): bg2.addButton(rb); v2.addWidget(rb)
        lay.addWidget(g2)
        g3=QGroupBox(_t("batch_seq_pfx_lbl")); self._g_seq_pfx=g3; v3=QVBoxLayout(g3); v3.setSpacing(5)
        self._lbl_sq_pfx=QLabel(_t("batch_smart_prefix")); self._lbl_sq_pfx.setObjectName("field_lbl"); v3.addWidget(self._lbl_sq_pfx); self._sq_prefix=QLineEdit(); self._sq_prefix.setPlaceholderText(_t("sq_prefix_ph2")); v3.addWidget(self._sq_prefix)
        self._lbl_sq_sfx=QLabel(_t("batch_smart_suffix")); self._lbl_sq_sfx.setObjectName("field_lbl"); v3.addWidget(self._lbl_sq_sfx); self._sq_suffix=QLineEdit(); self._sq_suffix.setPlaceholderText(_t("sq_suffix_ph2")); v3.addWidget(self._sq_suffix)
        lay.addWidget(g3)
        g4=QGroupBox(_t("batch_seq_name")); self._g_seq_name=g4; v4=QVBoxLayout(g4)
        self._rb_numonly=QRadioButton(_t("batch_seq_numonly")); self._rb_keep=QRadioButton(_t("batch_seq_keep")); self._rb_numonly.setChecked(True)
        bg3=QButtonGroup(self); bg3.addButton(self._rb_numonly); bg3.addButton(self._rb_keep)
        self._lbl_sq_sep=QLabel(_t("batch_seq_sep")); self._lbl_sq_sep.setObjectName("field_lbl"); sr=QHBoxLayout(); sr.addWidget(self._lbl_sq_sep); self._sq_sep=QLineEdit("_"); self._sq_sep.setMaximumWidth(50); sr.addWidget(self._sq_sep); sr.addStretch()
        self._sep_w=QWidget(); self._sep_w.setLayout(sr); self._sep_w.setVisible(False)
        self._rb_keep.toggled.connect(self._sep_w.setVisible)
        v4.addWidget(self._rb_numonly); v4.addWidget(self._rb_keep); v4.addWidget(self._sep_w)
        lay.addWidget(g4); lay.addStretch(); return w

    # ── File tab ──────────────────────────────
    def _build_file_tab(self):
        w=QWidget(); lay=QHBoxLayout(w); lay.setContentsMargins(0,8,0,0); lay.setSpacing(0)
        sp=QSplitter(Qt.Orientation.Horizontal); sp.setHandleWidth(1)
        left=QWidget(); ll=QVBoxLayout(left); ll.setContentsMargins(8,0,10,8); ll.setSpacing(8)
        self._p_drop=BatchDropZone("batch_drop1_p","batch_drop2_p","dropZoneFile")
        self._p_drop.folder_dropped.connect(self._p_on_dropped); ll.addWidget(self._p_drop)
        br2=QHBoxLayout(); br2.setSpacing(8)
        btn_fadd=QPushButton(_t("batch_btn_file_pick")); btn_fadd.setObjectName("btn_file_add"); btn_fadd.clicked.connect(self._p_pick)
        btn_fadd.setIcon(_svg_icon('folder_open', 'white')); btn_fadd.setIconSize(QSize(20,20))
        self._p_btn_fadd = btn_fadd  # keep reference for theme refresh
        self._p_lbl_count=QLabel(_t("batch_count_file", g=0, f=0)); self._p_lbl_count.setObjectName("count_lbl")
        btn_fclear=QPushButton(_t('btn_del_all')); self._p_btn_clear=btn_fclear; btn_fclear.setMinimumWidth(80); btn_fclear.setFixedHeight(36); btn_fclear.clicked.connect(self._p_clear)
        br2.addWidget(btn_fadd); br2.addStretch(); br2.addWidget(self._p_lbl_count); br2.addWidget(btn_fclear)
        ll.addLayout(br2)
        self._p_table=QTableWidget(0,3)
        self._p_table.setHorizontalHeaderLabels([_t("batch_col_file"),_t("batch_col_arrow"),_t("batch_col_file_new")])
        self._p_table.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        self._p_table.horizontalHeader().setSectionResizeMode(1,QHeaderView.Fixed)
        self._p_table.horizontalHeader().setSectionResizeMode(2,QHeaderView.Stretch)
        self._p_table.setColumnWidth(1,44); self._p_table.verticalHeader().setVisible(False)
        self._p_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._p_table.setSelectionBehavior(QAbstractItemView.SelectRows); ll.addWidget(self._p_table)
        ar2=QHBoxLayout(); ar2.setSpacing(8)
        self._p_btn_preview=QPushButton(_t("btn_preview")); self._p_btn_preview.setObjectName("btn_fpreview")
        self._p_btn_preview.setIcon(_svg_icon_dual('magnifier', ACCENT, 'white')); self._p_btn_preview.setIconSize(QSize(20,20))
        self._p_btn_preview.setFixedHeight(48); self._p_btn_preview.setEnabled(False); self._p_btn_preview.clicked.connect(self._p_do_preview)
        self._p_btn_rename=QPushButton(_t("batch_btn_rename")); self._p_btn_rename.setObjectName("btn_frename")
        self._p_btn_rename.setIcon(_svg_icon('check', 'white')); self._p_btn_rename.setIconSize(QSize(18,18))
        self._p_btn_rename.setFixedHeight(48); self._p_btn_rename.setEnabled(False); self._p_btn_rename.clicked.connect(self._p_do_rename)
        self._p_btn_undo=QPushButton(_t('btn_undo')); self._p_btn_undo.setObjectName("btn_undo")
        self._p_btn_undo.setFixedHeight(48); self._p_btn_undo.setEnabled(False)
        self._p_btn_undo.clicked.connect(self._undo)
        ar2.addWidget(self._p_btn_preview, 1); ar2.addWidget(self._p_btn_rename, 1); ar2.addWidget(self._p_btn_undo, 1)
        ll.addLayout(ar2); sp.addWidget(left)
        # right-side settings
        fs=ScrollHintArea(); self._sa_file=fs
        fs.setWidgetResizable(True); fs.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff); fs.setFixedWidth(330)
        fw=QWidget(); frl=QVBoxLayout(fw); frl.setContentsMargins(12,4,8,40); frl.setSpacing(6)
        # ── Collapsible usage hint (default: collapsed) ─────────────────
        self._p_hint_open = False
        self._p_hint_btn = QPushButton(f"  {_t('batch_usage_title')}  ▼")
        self._p_hint_btn.setFixedHeight(28)
        self._p_hint_btn.setObjectName("hint_toggle_btn")
        self._p_hint_btn.setStyleSheet(
            f"QPushButton{{background:transparent;border:none;border-bottom:1px solid {BORDER};"
            f"border-radius:0;text-align:left;padding:0 6px;font-size:12px;"
            f"color:{MUTED};font-weight:600;}}"
            f"QPushButton:hover{{color:{ACCENT};}}")
        self._hint_file = QLabel(_t('batch_hint_file'))
        self._hint_file.setObjectName("hint_box")
        self._hint_file.setTextFormat(Qt.TextFormat.RichText)
        self._hint_file.setWordWrap(True)
        self._hint_file.setVisible(False)
        def _p_toggle_hint():
            self._p_hint_open = not self._p_hint_open
            self._hint_file.setVisible(self._p_hint_open)
            arrow = "▲" if self._p_hint_open else "▼"
            self._p_hint_btn.setText(f"  {_t('batch_usage_title')}  {arrow}")
        self._p_hint_btn.clicked.connect(_p_toggle_hint)
        frl.addWidget(self._p_hint_btn)
        frl.addWidget(self._hint_file)

        fmt=QLabel(f"<b>{_t('batch_file_fmt_label')}</b><br><span style='color:{ACCENT};font-size:13px;'>{_t('batch_file_fmt_pattern')}</span>"); self._fmt_lbl=fmt
        fmt.setObjectName("fmt_box"); fmt.setTextFormat(Qt.TextFormat.RichText); fmt.setWordWrap(True); frl.addWidget(fmt)
        # prefix
        gp=QGroupBox(_t("batch_file_pfx")); self._gp=gp; vp=QVBoxLayout(gp); vp.setContentsMargins(10,6,10,8); vp.setSpacing(4)
        self._p_rb_folder=QRadioButton(_t("batch_file_pfx_folder")); self._p_rb_custom=QRadioButton(_t("batch_file_pfx_custom")); self._p_rb_folder.setChecked(True)
        bgf=QButtonGroup(self); bgf.addButton(self._p_rb_folder); bgf.addButton(self._p_rb_custom)
        self._p_custom_pfx=QLineEdit(); self._p_custom_pfx.setPlaceholderText(_t("batch_file_pfx_ph")); self._p_custom_pfx.setEnabled(False)
        self._p_rb_custom.toggled.connect(self._p_custom_pfx.setEnabled)
        vp.addWidget(self._p_rb_folder); vp.addWidget(self._p_rb_custom); vp.addWidget(self._p_custom_pfx); frl.addWidget(gp)
        # separator + start number (single row)
        gs_row=QGroupBox(_t("batch_file_sep_start")); self._gs_row=gs_row; hs=QHBoxLayout(gs_row); hs.setContentsMargins(10,6,10,8); hs.setSpacing(10)
        self._lbl_p_sep=QLabel(_t("batch_file_sep")); self._lbl_p_sep.setObjectName("field_lbl"); hs.addWidget(self._lbl_p_sep)
        self._p_sep=QLineEdit("-"); self._p_sep.setMaximumWidth(50); hs.addWidget(self._p_sep)
        div=QFrame(); div.setFrameShape(QFrame.VLine); div.setStyleSheet(f"color:{BORDER};"); hs.addWidget(div)
        self._p_rb_s0=QRadioButton(_t("batch_file_from0")); self._p_rb_s1=QRadioButton(_t("batch_file_from1")); self._p_rb_s1.setChecked(True)
        bgs=QButtonGroup(self); bgs.addButton(self._p_rb_s0); bgs.addButton(self._p_rb_s1)
        hs.addWidget(self._p_rb_s0); hs.addWidget(self._p_rb_s1); hs.addStretch(); frl.addWidget(gs_row)
        # number digits (2×2)
        gpd=QGroupBox(_t("batch_file_digits")); self._gpd=gpd; gd=QVBoxLayout(gpd); gd.setContentsMargins(10,6,10,8); gd.setSpacing(3)
        self._p_rb_auto=QRadioButton(_t("batch_file_auto")); self._p_rb_nopad=QRadioButton(_t("batch_file_nopad"))
        self._p_rb_pad2=QRadioButton(_t("batch_file_2d"));  self._p_rb_pad3=QRadioButton(_t("batch_file_3d"))
        self._p_rb_auto.setChecked(True); bgp=QButtonGroup(self)
        for rb in (self._p_rb_auto,self._p_rb_nopad,self._p_rb_pad2,self._p_rb_pad3): bgp.addButton(rb)
        dr1=QHBoxLayout(); dr1.addWidget(self._p_rb_auto);  dr1.addWidget(self._p_rb_nopad); dr1.addStretch()
        dr2=QHBoxLayout(); dr2.addWidget(self._p_rb_pad2); dr2.addWidget(self._p_rb_pad3);  dr2.addStretch()
        gd.addLayout(dr1); gd.addLayout(dr2); frl.addWidget(gpd)
        # file filter
        gfl=QGroupBox(_t("batch_file_filter")); self._gfl=gfl; vfl=QVBoxLayout(gfl); vfl.setContentsMargins(10,6,10,8); vfl.setSpacing(4)
        self._p_rb_all=QRadioButton(_t("batch_file_all")); self._p_rb_ext=QRadioButton(_t("batch_file_ext")); self._p_rb_all.setChecked(True)
        bge=QButtonGroup(self); bge.addButton(self._p_rb_all); bge.addButton(self._p_rb_ext)
        self._p_ext_input=QLineEdit(); self._p_ext_input.setPlaceholderText(_t("batch_file_ext_ph")); self._p_ext_input.setEnabled(False)
        self._p_rb_ext.toggled.connect(self._p_ext_input.setEnabled)
        vfl.addWidget(self._p_rb_all); vfl.addWidget(self._p_rb_ext); vfl.addWidget(self._p_ext_input); frl.addWidget(gfl)
        frl.addStretch()
        fs.setWidget(fw); sp.addWidget(fs); sp.setSizes([700,300]); lay.addWidget(sp); return w

    # ── Folder tab logic ──────────────────────
    def _f_on_dropped(self,dirs): self._f_ingest(dirs)
    def _f_pick(self):
        path=QFileDialog.getExistingDirectory(self,_t("batch_btn_folder_pick"),"",QFileDialog.ShowDirsOnly)
        if path: self._f_ingest([path])
    def _f_ingest(self,parent_paths):
        added=0
        skipped=[]   # parents that contributed no group (consolidated for one final dialog)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            # O(1) duplicate check via set (was O(N²) any() linear scan)
            existing=set(g["parent"] for g in self._f_groups)

            def _ingest_one(parent):
                nonlocal added
                parent=os.path.normpath(parent)
                if parent in existing: return
                try: entries=os.listdir(parent)
                except OSError as exc: _dlg_warn(self, _t('dlg_ok'), str(exc)); _glog(f"❌ failed to read folder: {parent} — {exc}"); return
                children=sorted([os.path.join(parent,d) for d in entries
                                 if os.path.isdir(os.path.join(parent,d)) and not d.startswith('.')],
                                key=natural_sort_key)
                if not children: return
                existing.add(parent)
                self._f_groups.append({"parent":parent,"children":children}); added+=1
                _glog(f"📁 [Batch/Folder] add group: {parent}  ({len(children)} subfolder(s))")
                # recursively descend into subfolders that contain further subfolders
                for child in children:
                    _ingest_one(child)

            for parent in parent_paths:
                parent=os.path.normpath(parent)
                before=len(self._f_groups)
                _ingest_one(parent)
                if len(self._f_groups)==before:
                    skipped.append(parent)
        finally:
            QApplication.restoreOverrideCursor()
        # consolidated "no subfolders found" dialog (was per-folder popup spam)
        if skipped:
            if len(skipped) <= 10:
                msg = f"{_t('rename_no_subfolders')}\n\n" + "\n".join(skipped)
            else:
                msg = f"{_t('rename_no_subfolders')} ({len(skipped)})\n\n" + "\n".join(skipped[:10]) + f"\n... (+{len(skipped)-10})"
            _dlg_info(self, _t('dlg_ok'), msg)
        if added: self._f_refresh(False); self._f_btn_preview.setEnabled(True); self._f_btn_rename.setEnabled(False)
    def _f_clear(self):
        self._f_groups.clear(); self._f_preview.clear(); self._f_refresh(False)
        self._f_btn_preview.setEnabled(False); self._f_btn_rename.setEnabled(False)
    def _f_calc_preview(self):
        mode=self._opt_stack.currentIndex(); result=[]
        if mode==0:
            pfx=self._sm_prefix.text(); sfx=self._sm_suffix.text()
            for grp in self._f_groups:
                names=[os.path.basename(c) for c in grp["children"]]
                strip="" if self._rb_none.isChecked() else (self._sm_manual_pfx.text() if self._rb_manual.isChecked() else detect_common_prefix(names))
                trimmed_list=[]
                for path,name in zip(grp["children"],names):
                    t=name[len(strip):] if strip and name.startswith(strip) else name
                    if not t: t=name
                    trimmed_list.append((path,t))
                width=auto_width_for_group([t for _,t in trimmed_list])
                for path,trimmed in trimmed_list: result.append((path,f"{pfx}{extract_number_auto(trimmed,width)}{sfx}"))
        else:
            start=1 if self._rb_s1.isChecked() else 0
            pfx=self._sq_prefix.text(); sfx=self._sq_suffix.text(); reset=self._rb_seq_reset.isChecked()
            if self._rb_d_auto.isChecked():
                total=sum(len(g["children"]) for g in self._f_groups)
                digits=len(str(start+total-1)) if total else 1
            else: digits=3 if self._rb_d3.isChecked() else (4 if self._rb_d4.isChecked() else 2)
            gi=0
            for grp in self._f_groups:
                for li,path in enumerate(grp["children"]):
                    idx=li if reset else gi; num=str(start+idx).zfill(digits)
                    name=os.path.basename(path)
                    new=f"{pfx}{num}{self._sq_sep.text()}{name}{sfx}" if self._rb_keep.isChecked() else f"{pfx}{num}{sfx}"
                    result.append((path,new)); gi+=1
        return result
    def _f_do_preview(self):
        self._f_preview=self._f_calc_preview(); self._f_refresh(True); self._f_btn_rename.setEnabled(bool(self._f_preview))
        total=sum(len(g["children"]) for g in self._f_groups)
        _glog(f"🔍 [Batch/Folder] preview — {len(self._f_groups)} group(s), {total} folder(s) → {len(self._f_preview)} change(s)")
    def _f_refresh(self,preview):
        pm=dict(self._f_preview) if preview else {}
        total=sum(len(g["children"]) for g in self._f_groups)
        self._f_lbl_count.setText(_t("batch_count_folder", g=len(self._f_groups), f=total))
        tbl=self._f_table; tbl.setUpdatesEnabled(False); tbl.blockSignals(True)
        try:
            tbl.setRowCount(0); tbl.setRowCount(len(self._f_groups)+total); row=0
            for grp in self._f_groups:
                hi=QTableWidgetItem(f"  📂  {grp['parent']}")
                hi.setForeground(QColor(ACCENT)); hi.setBackground(QColor(GRP_BG)); hi.setToolTip(grp['parent'])
                f=hi.font(); f.setBold(True); f.setPointSize(10); hi.setFont(f)
                ai=QTableWidgetItem(""); ai.setBackground(QColor(GRP_BG))
                ni=QTableWidgetItem(_t("batch_parent_folder")); ni.setForeground(QColor(MUTED)); ni.setBackground(QColor(GRP_BG))
                for col,it in enumerate([hi,ai,ni]): it.setFlags(Qt.ItemFlag.ItemIsEnabled); tbl.setItem(row,col,it)
                tbl.setRowHeight(row,30); row+=1
                for cp in grp["children"]:
                    oi=QTableWidgetItem(f"    └  {os.path.basename(cp)}"); oi.setForeground(QColor(MUTED)); oi.setToolTip(cp)
                    ari=QTableWidgetItem("→"); ari.setTextAlignment(Qt.AlignmentFlag.AlignCenter); ari.setForeground(QColor(BORDER))
                    nwi=QTableWidgetItem(pm[cp]) if cp in pm else QTableWidgetItem(_t("batch_click_preview"))
                    if cp in pm: nwi.setToolTip(pm[cp])
                    nwi.setForeground(QColor(ACCENT) if cp in pm else QColor(BORDER))
                    tbl.setItem(row,0,oi); tbl.setItem(row,1,ari); tbl.setItem(row,2,nwi); tbl.setRowHeight(row,34); row+=1
        finally: tbl.blockSignals(False); tbl.setUpdatesEnabled(True)
    def _close_explorer_for_groups(self):
        """Detect Explorer windows holding the target folder path via PowerShell COM and close them.
        Windows-only — no-op on other platforms.
        Returns: list of folder paths from closed windows (for re-opening after completion)."""
        if sys.platform != 'win32': return []
        target_paths = set()
        for g in self._f_groups:
            target_paths.add(os.path.normpath(g["parent"]))
            for c in g["children"]:
                target_paths.add(os.path.normpath(c))
        if not target_paths: return []
        try:
            ps_list = (
                "$shell = New-Object -ComObject Shell.Application;"
                "$shell.Windows() | ForEach-Object { $_.LocationURL }"
            )
            r = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_list],
                capture_output=True, text=True, timeout=5
            )
            urls = [u.strip() for u in r.stdout.splitlines() if u.strip().startswith("file:///")]
            if not urls: return []
            from urllib.parse import unquote
            overlap_urls = []; overlap_folders = []
            for url in urls:
                folder = os.path.normpath(unquote(url[8:].replace("/", os.sep)))
                for t in target_paths:
                    if folder.lower().startswith(t.lower()) or t.lower().startswith(folder.lower()):
                        overlap_urls.append(url); overlap_folders.append(folder); break
            if not overlap_urls: return []
            msg = (f"{_t('rename_explorer_warn')}\n"
                   f"{len(overlap_urls)} window(s) will be closed and reopened after renaming.")
            if not _dlg_question(self, _t("dlg_confirm_title"), msg, min_width=480): return []
            cond = " -or ".join(f'$_.LocationURL -eq "{u}"' for u in overlap_urls)
            ps_close = (
                f"$shell = New-Object -ComObject Shell.Application;"
                f"$shell.Windows() | Where-Object {{ {cond} }} | ForEach-Object {{ $_.Quit() }}"
            )
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_close],
                           capture_output=True, timeout=5)
            import time; time.sleep(0.5)
            _glog(f"  🗙 closed {len(overlap_urls)} Explorer window(s)")
            return overlap_folders
        except Exception as e:
            _glog(f"  ⚠ failed to close Explorer windows: {e}"); return []

    @staticmethod
    def _reopen_explorer(folders):
        """Re-open previously closed Explorer windows at the same path (or parent)."""
        if sys.platform != 'win32' or not folders: return
        try:
            import time; time.sleep(0.5)
            norm = sorted({os.path.normpath(f) for f in folders},
                          key=lambda p: p.count(os.sep))
            opened = set()
            for folder in norm:
                # fall back to the parent folder if the path disappeared due to renaming
                target = folder
                while target and not os.path.exists(target):
                    target = os.path.dirname(target)
                if not target or not os.path.exists(target): continue
                skip = any(target.lower().startswith(o.lower() + os.sep) for o in opened)
                if not skip:
                    subprocess.Popen(['explorer', target])
                    opened.add(target)
                    time.sleep(0.2)
                    _glog(f"  📂 Explorer reopened: {target}")
            _glog(f"  📂 reopened {len(opened)} Explorer window(s) total")
        except Exception as e:
            _glog(f"  ⚠ failed to reopen Explorer: {e}")

    def _close_explorer_for_paths(self, paths):
        """Detect and close Explorer windows based on a path list (for undo).
        Returns: list of folder paths from closed windows."""
        if sys.platform != 'win32' or not paths: return []
        target_paths = {os.path.normpath(p) for p in paths}
        try:
            ps_list = (
                "$shell = New-Object -ComObject Shell.Application;"
                "$shell.Windows() | ForEach-Object { $_.LocationURL }"
            )
            r = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_list],
                capture_output=True, text=True, timeout=5
            )
            urls = [u.strip() for u in r.stdout.splitlines() if u.strip().startswith("file:///")]
            if not urls: return []
            from urllib.parse import unquote
            overlap_urls = []; overlap_folders = []
            for url in urls:
                folder = os.path.normpath(unquote(url[8:].replace("/", os.sep)))
                for t in target_paths:
                    if folder.lower().startswith(t.lower()) or t.lower().startswith(folder.lower()):
                        overlap_urls.append(url); overlap_folders.append(folder); break
            if not overlap_urls: return []
            msg = (f"{_t('rename_explorer_warn')}\n"
                   f"{len(overlap_urls)} window(s) will be closed and reopened after undo.")
            if not _dlg_question(self, _t("dlg_confirm_title"), msg, min_width=480): return []
            cond = " -or ".join(f'$_.LocationURL -eq "{u}"' for u in overlap_urls)
            ps_close = (
                f"$shell = New-Object -ComObject Shell.Application;"
                f"$shell.Windows() | Where-Object {{ {cond} }} | ForEach-Object {{ $_.Quit() }}"
            )
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_close],
                           capture_output=True, timeout=5)
            import time; time.sleep(0.5)
            _glog(f"  🗙 closed {len(overlap_urls)} Explorer window(s)")
            return overlap_folders
        except Exception as e:
            _glog(f"  ⚠ failed to close Explorer windows: {e}"); return []

    def _f_do_rename(self):
        if not self._f_preview: _dlg_warn(self, _t('dlg_ok'), _t('rename_no_preview')); return
        pairs=[(o,n) for o,n in self._f_preview if os.path.basename(o)!=n]
        if not pairs: _dlg_info(self, _t('dlg_ok'), _t('rename_no_pairs')); return
        col=self._check_cols(pairs)
        if col: _dlg_error(self, _t('rename_collision'), "\n".join(col[:10])); return
        if not self._confirm(len(pairs),pairs): return
        # ── Auto-close Explorer windows holding the target folder ─────
        closed_folders = self._close_explorer_for_groups()
        _glog(f"▶ [Batch/Folder] running rename — {len(pairs)} item(s)")
        errors,done=[],0; rm=dict(self._f_preview); undo_map=[]
        pending=[]  # WinError 5 failures — bulk-retried after full completion
        # process deepest (children) first — renaming parents first would invalidate child paths
        for grp in reversed(self._f_groups):
            nc=[]
            for cp in grp["children"]:
                nn=rm.get(cp,os.path.basename(cp))
                if os.path.basename(cp)==nn: nc.append(cp); continue
                np2=os.path.join(os.path.dirname(cp),nn)
                try:
                    os.rename(cp,np2); nc.append(np2); done+=1
                    undo_map.append((np2,cp))
                    _glog(f"  ✅ {os.path.basename(cp)}  →  {nn}")
                except OSError as e:
                    if getattr(e,'winerror',None)==5:
                        # ACCESS_DENIED — bulk-retry later
                        pending.append((cp,np2,nn)); nc.append(cp)
                        _glog(f"  ⏳ {os.path.basename(cp)}: locked — retry queued")
                    else:
                        errors.append(f"{os.path.basename(cp)}: {e}"); nc.append(cp)
                        _glog(f"  ❌ {os.path.basename(cp)}: {e}")
            grp["children"]=nc

        # ── Bulk retry (up to 5 rounds, up to 1 second wait per round) ──
        if pending:
            import time
            _glog(f"  ⏳ [retry] {len(pending)} item(s) — wait 2s then retry")
            time.sleep(2.0)
            for attempt in range(5):
                still=[]
                for cp,np2,nn in pending:
                    try:
                        os.rename(cp,np2); done+=1
                        undo_map.append((np2,cp))
                        _glog(f"  ✅ {os.path.basename(cp)}  →  {nn} (retry {attempt+1})")
                        # refresh grp["children"]
                        for g in self._f_groups:
                            if cp in g["children"]:
                                g["children"][g["children"].index(cp)]=np2; break
                    except OSError as e:
                        if getattr(e,'winerror',None)==5:
                            still.append((cp,np2,nn))
                        else:
                            errors.append(f"{os.path.basename(cp)}: {e}")
                            _glog(f"  ❌ {os.path.basename(cp)}: {e}")
                pending=still
                if not pending: break
                time.sleep(1.0)
            for cp,np2,nn in pending:
                errors.append(f"{os.path.basename(cp)}: access denied — close Explorer and try again")
                _glog(f"  ❌ {os.path.basename(cp)}: final failure")
        _glog(f"  done: {done} succeeded / {len(errors)} failed")
        if done > 0:
            self._undo_data = ('rename', undo_map)
            self._f_btn_undo.setEnabled(True)
            if hasattr(self, '_p_btn_undo'): self._p_btn_undo.setEnabled(False)
        self._f_preview=[]; self._f_refresh(False); self._f_btn_rename.setEnabled(False)
        self._show_result(done,errors,_t("batch_sub_folder"))
        # after rename, reopen any Explorer windows that were closed
        self._reopen_explorer(closed_folders)

    # ── File tab logic ────────────────────────
    def _p_on_dropped(self,dirs): self._p_ingest(dirs)
    def _p_pick(self):
        path=QFileDialog.getExistingDirectory(self,_t("batch_btn_file_pick"),"",QFileDialog.ShowDirsOnly)
        if path: self._p_ingest([path])
    def _p_ingest(self,folder_paths):
        added=0
        skipped=[]   # folders that contributed no group (consolidated for one final dialog)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            # O(1) duplicate check via set (was O(N²) any() linear scan)
            existing=set(g["folder"] for g in self._p_groups)
            for folder in folder_paths:
                folder=os.path.normpath(folder)
                # ── Step 1: check for direct files ────────────────────────
                try: entries=os.listdir(folder)
                except OSError as exc: _dlg_warn(self, _t('dlg_ok'), str(exc)); _glog(f"❌ failed to read folder: {folder} — {exc}"); continue
                files=sorted([os.path.join(folder,f) for f in entries
                              if os.path.isfile(os.path.join(folder,f))
                              and not f.startswith('.') and f.lower() not in _SKIP_FILES],
                             key=natural_sort_key)
                if files:
                    # direct files exist → add a single group using the existing approach
                    if folder not in existing:
                        existing.add(folder)
                        self._p_groups.append({"folder":folder,"files":files}); added+=1
                        _glog(f"📁 [Batch/File] add group: {folder}  ({len(files)} file(s))")
                else:
                    # ── Step 2: no direct files → recursively descend into subfolders ──
                    sub_added=0
                    for root, dirs, filenames in os.walk(folder):
                        dirs.sort(key=lambda d: natural_sort_key(os.path.join(root, d)))
                        if root == folder: continue  # already confirmed top-level has no files
                        sub_files=sorted([os.path.join(root,f) for f in filenames
                                         if not f.startswith('.') and f.lower() not in _SKIP_FILES],
                                        key=natural_sort_key)
                        if sub_files and root not in existing:
                            existing.add(root)
                            self._p_groups.append({"folder":root,"files":sub_files}); sub_added+=1
                            _glog(f"📁 [Batch/File] add sub-group: {root}  ({len(sub_files)} file(s))")
                    if sub_added==0:
                        skipped.append(folder)
                    else:
                        added+=sub_added
        finally:
            QApplication.restoreOverrideCursor()
        # consolidated "no files found" dialog (was per-folder popup spam)
        if skipped:
            if len(skipped) <= 10:
                msg = f"{_t('rename_no_files')}\n\n" + "\n".join(skipped)
            else:
                msg = f"{_t('rename_no_files')} ({len(skipped)})\n\n" + "\n".join(skipped[:10]) + f"\n... (+{len(skipped)-10})"
            _dlg_info(self, _t('dlg_ok'), msg)
        if added: self._p_refresh(False); self._p_btn_preview.setEnabled(True); self._p_btn_rename.setEnabled(False)
    def _p_clear(self):
        self._p_groups.clear(); self._p_preview.clear(); self._p_refresh(False)
        self._p_btn_preview.setEnabled(False); self._p_btn_rename.setEnabled(False)
    def _p_filtered(self,files):
        if self._p_rb_all.isChecked(): return files
        raw=self._p_ext_input.text()
        exts={("."+e.strip().lstrip(".")).lower() for e in raw.split(",") if e.strip()}
        return files if not exts else [f for f in files if os.path.splitext(f)[1].lower() in exts]
    def _p_calc_preview(self):
        start=0 if self._p_rb_s0.isChecked() else 1; sep=self._p_sep.text() or "-"; result=[]
        for grp in self._p_groups:
            files=self._p_filtered(grp["files"])
            # ── digit width per group (each group sized by its own file count) ──
            grp_max_num=start+len(files)-1
            if self._p_rb_nopad.isChecked(): auto_d=1
            else:
                auto_d=len(str(grp_max_num)) if grp_max_num>0 else 1
                if self._p_rb_pad2.isChecked(): auto_d=max(2,auto_d)
                if self._p_rb_pad3.isChecked(): auto_d=max(3,auto_d)
            fn=os.path.basename(grp["folder"])
            prefix=self._p_custom_pfx.text() or fn if self._p_rb_custom.isChecked() else fn
            for idx,fpath in enumerate(files):
                _,ext=os.path.splitext(fpath)
                ns=str(start+idx) if self._p_rb_nopad.isChecked() else str(start+idx).zfill(auto_d)
                result.append((fpath,f"{prefix}{sep}{ns}{ext}"))
        return result
    def _p_do_preview(self):
        self._p_preview=self._p_calc_preview(); self._p_refresh(True); self._p_btn_rename.setEnabled(bool(self._p_preview))
        total=sum(len(self._p_filtered(g["files"])) for g in self._p_groups)
        _glog(f"🔍 [Batch/File] preview — {len(self._p_groups)} group(s), {total} file(s) → {len(self._p_preview)} change(s)")
    def _p_refresh(self,preview):
        pm=dict(self._p_preview) if preview else {}
        total=sum(len(self._p_filtered(g["files"])) for g in self._p_groups)
        self._p_lbl_count.setText(_t("batch_count_file", g=len(self._p_groups), f=total))
        tbl=self._p_table; tbl.setUpdatesEnabled(False); tbl.blockSignals(True)
        try:
            tbl.setRowCount(0); tbl.setRowCount(len(self._p_groups)+total); row=0
            for grp in self._p_groups:
                hi=QTableWidgetItem(f"  📂  {grp['folder']}"); hi.setForeground(QColor(ACCENT2)); hi.setBackground(QColor(GRP_BG)); hi.setToolTip(grp['folder'])
                f=hi.font(); f.setBold(True); f.setPointSize(10); hi.setFont(f)
                ai=QTableWidgetItem(""); ai.setBackground(QColor(GRP_BG))
                ni=QTableWidgetItem(_t("batch_folder_label")); ni.setForeground(QColor(MUTED)); ni.setBackground(QColor(GRP_BG))
                for col,it in enumerate([hi,ai,ni]): it.setFlags(Qt.ItemFlag.ItemIsEnabled); tbl.setItem(row,col,it)
                tbl.setRowHeight(row,30); row+=1
                for fp in self._p_filtered(grp["files"]):
                    oi=QTableWidgetItem(f"    └  {os.path.basename(fp)}"); oi.setForeground(QColor(MUTED)); oi.setToolTip(fp)
                    ari=QTableWidgetItem("→"); ari.setTextAlignment(Qt.AlignmentFlag.AlignCenter); ari.setForeground(QColor(BORDER))
                    nwi=QTableWidgetItem(pm[fp]) if fp in pm else QTableWidgetItem(_t("batch_click_preview"))
                    if fp in pm: nwi.setToolTip(pm[fp])
                    nwi.setForeground(QColor(ACCENT2) if fp in pm else QColor(BORDER))
                    tbl.setItem(row,0,oi); tbl.setItem(row,1,ari); tbl.setItem(row,2,nwi); tbl.setRowHeight(row,34); row+=1
        finally: tbl.blockSignals(False); tbl.setUpdatesEnabled(True)
    def _p_do_rename(self):
        if not self._p_preview: _dlg_warn(self, _t('dlg_ok'), _t('rename_no_preview')); return
        pairs=[(o,n) for o,n in self._p_preview if os.path.basename(o)!=n]
        if not pairs: _dlg_info(self, _t('dlg_ok'), _t('rename_no_pairs')); return
        col=self._check_cols(pairs)
        if col: _dlg_error(self, _t('rename_collision'), "\n".join(col[:10])); return
        if not self._confirm(len(pairs),pairs): return
        _glog(f"▶ [Batch/File] running rename — {len(pairs)} item(s)")
        errors,done=[],0; rm=dict(self._p_preview); undo_map=[]
        for grp in self._p_groups:
            nf=[]
            for fp in grp["files"]:
                nn=rm.get(fp,os.path.basename(fp))
                if os.path.basename(fp)==nn: nf.append(fp); continue
                np2=os.path.join(os.path.dirname(fp),nn)
                try: os.rename(fp,np2); nf.append(np2); done+=1; undo_map.append((np2,fp)); _glog(f"  ✅ {os.path.basename(fp)}  →  {nn}")
                except OSError as e: errors.append(f"{os.path.basename(fp)}: {e}"); nf.append(fp); _glog(f"  ❌ {os.path.basename(fp)}: {e}")
            grp["files"]=nf
        _glog(f"  done: {done} succeeded / {len(errors)} failed")
        if done > 0:
            self._undo_data = ('rename', undo_map)
            self._p_btn_undo.setEnabled(True)
            if hasattr(self, '_f_btn_undo'): self._f_btn_undo.setEnabled(False)
        self._p_preview=[]; self._p_refresh(False); self._p_btn_rename.setEnabled(False)
        self._show_result(done,errors,_t("batch_sub_file"))

    # ── Common utilities ──────────────────────
    def _check_cols(self,pairs):
        errs=[]; bp={}
        for o,n in pairs: bp.setdefault(os.path.dirname(o),[]).append((o,n))
        for pdir,ents in bp.items():
            seen=set()
            for _,n in ents:
                if n in seen: errs.append(f"'{n}'  ← duplicate in batch")
                seen.add(n)
            try: existing=set(os.listdir(pdir))
            except OSError: existing=set()
            ob={os.path.basename(o) for o,_ in ents}
            for _,n in ents:
                if n in existing and n not in ob: errs.append(f"'{n}'  ← conflicts with existing")
        return errs
    def _confirm(self,count,pairs):
        lines="\n".join(f"  {os.path.basename(o)}  →  {n}" for o,n in pairs[:14])
        if len(pairs)>14: lines+=f"\n  ... +{len(pairs)-14} more"
        dlg=QDialog(self); dlg.setWindowTitle(_t("dlg_rename_confirm")); dlg.setMinimumWidth(480)
        try:
            dlg.setWindowIcon(_make_app_icon())
        except Exception:
            pass
        dlg.setStyleSheet(f"QDialog{{background:{SURFACE};}} QLabel{{background:transparent;color:{TEXT};}}")
        root=QVBoxLayout(dlg); root.setContentsMargins(28,24,28,24); root.setSpacing(16)
        hdr=QLabel(f"<b style='font-size:15px;color:{TEXT};'>{count}</b><span style='font-size:13px;color:{MUTED};'> {_t('batch_confirm_items')}</span>")
        hdr.setTextFormat(Qt.TextFormat.RichText); root.addWidget(hdr)
        sep=QFrame(); sep.setFrameShape(QFrame.HLine); sep.setStyleSheet(f"background:{BORDER};max-height:1px;border:none;"); root.addWidget(sep)
        scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff); scroll.setMaximumHeight(320)
        lw=QWidget(); lw.setStyleSheet(f"background:{BG};"); ll=QVBoxLayout(lw); ll.setContentsMargins(10,8,10,8); ll.setSpacing(0)
        for i,(old,new) in enumerate(pairs[:20]):
            rw=QWidget(); rw.setStyleSheet(f"background:{SURFACE if i%2==0 else BG};border-radius:4px;")
            rl=QHBoxLayout(rw); rl.setContentsMargins(8,5,8,5); rl.setSpacing(8)
            ol=QLabel(os.path.basename(old)); ol.setStyleSheet(f"color:{MUTED};font-size:12px;background:transparent;"); ol.setFixedWidth(180)
            al=QLabel("→"); al.setStyleSheet(f"color:{BORDER};font-size:12px;background:transparent;"); al.setFixedWidth(20); al.setAlignment(Qt.AlignmentFlag.AlignCenter)
            nl=QLabel(new); nl.setStyleSheet(f"color:{ACCENT};font-size:12px;font-weight:600;background:transparent;")
            rl.addWidget(ol); rl.addWidget(al); rl.addWidget(nl,stretch=1); ll.addWidget(rw)
        if len(pairs)>20: ml=QLabel(f"  … +{len(pairs)-20} more"); ml.setStyleSheet(f"color:{MUTED};font-size:12px;padding:6px 8px;background:transparent;"); ll.addWidget(ml)
        ll.addStretch(); scroll.setWidget(lw); root.addWidget(scroll)
        # warning that Explorer is open
        warn_lbl = QLabel(_t('rename_explorer_warn'))
        warn_lbl.setWordWrap(True)
        warn_lbl.setStyleSheet(
            f"color:{MUTED};font-size:11px;background:{SRF2};"
            f"border:1px solid {BORDER};border-radius:6px;padding:8px 10px;")
        root.addWidget(warn_lbl)
        br=QHBoxLayout(); br.setSpacing(10); br.addStretch()
        bc=QPushButton(_t('rename_cancel')); bc.setStyleSheet(f"QPushButton{{background:{SURFACE};border:1.5px solid {BORDER};color:{TEXT};border-radius:8px;padding:9px 28px;font-size:13px;font-weight:600;}}QPushButton:hover{{background:{SRF2};}}")
        bc.clicked.connect(dlg.reject)
        bo=QPushButton(_t('rename_do')); bo.setStyleSheet(f"QPushButton{{background:{ACCENT};border:none;color:white;border-radius:8px;padding:9px 28px;font-size:13px;font-weight:600;}}QPushButton:hover{{background:{ACCENT_HOVER};}}")
        bo.setDefault(True); bo.clicked.connect(dlg.accept)
        br.addWidget(bc); br.addWidget(bo); root.addLayout(br)
        return dlg.exec()==QDialog.Accepted
    def _show_result(self,done,errors,kind):
        total = done + len(errors)
        dlg=QDialog(self); dlg.setWindowTitle(_t("dlg_rename_done") if not errors else _t("dlg_rename_partial")); dlg.setMinimumWidth(360)
        try:
            dlg.setWindowIcon(_make_app_icon())
        except Exception:
            pass
        dlg.setStyleSheet(f"QDialog{{background:{SURFACE};}} QLabel{{background:transparent;color:{TEXT};}}")
        root=QVBoxLayout(dlg); root.setContentsMargins(32,28,32,24); root.setSpacing(14)
        if not errors:
            il=QLabel("✅"); il.setAlignment(Qt.AlignmentFlag.AlignCenter); il.setStyleSheet("font-size:40px;background:transparent;"); root.addWidget(il)
            ml=QLabel(f"<b style='font-size:15px;color:{TEXT};'>{done}</b><span style='font-size:13px;color:{MUTED};'> {_t('batch_done_items')}</span>"); ml.setTextFormat(Qt.TextFormat.RichText); ml.setAlignment(Qt.AlignmentFlag.AlignCenter); root.addWidget(ml)
            btn=QPushButton(_t('dlg_ok')); btn.setStyleSheet(f"QPushButton{{background:{ACCENT};border:none;color:white;border-radius:8px;padding:9px 32px;font-size:13px;font-weight:600;}}QPushButton:hover{{background:{ACCENT_HOVER};}}")
            btn.clicked.connect(dlg.accept)
        else:
            il=QLabel("⚠️"); il.setAlignment(Qt.AlignmentFlag.AlignCenter); il.setStyleSheet("font-size:36px;background:transparent;"); root.addWidget(il)
            # show total attempt count
            sl=QLabel(
                f"<span style='font-size:13px;color:{MUTED};'>{total} total  </span>"
                f"<b style='font-size:14px;color:{TEXT};'>{done} ok</b>"
                f"<span style='font-size:13px;color:#C0392B;'>  /  {len(errors)} failed</span>"
            )
            sl.setTextFormat(Qt.TextFormat.RichText); sl.setAlignment(Qt.AlignmentFlag.AlignCenter); root.addWidget(sl)
            # failure description
            note=QLabel(_t("dlg_rename_partial_note"))
            note.setStyleSheet(f"font-size:11px;color:{MUTED};")
            note.setAlignment(Qt.AlignmentFlag.AlignCenter)
            note.setWordWrap(True)
            root.addWidget(note)
            eb=QTextEdit(); eb.setReadOnly(True); eb.setMaximumHeight(120); eb.setPlainText("\n".join(errors))
            eb.setStyleSheet(f"QTextEdit{{background:{BG};border:1px solid {BORDER};border-radius:8px;color:#C0392B;font-size:11px;padding:8px;}}"); root.addWidget(eb)
            btn=QPushButton(_t('dlg_ok')); btn.setStyleSheet(f"QPushButton{{background:{SURFACE};border:1.5px solid {BORDER};color:{TEXT};border-radius:8px;padding:9px 32px;font-size:13px;font-weight:600;}}QPushButton:hover{{background:{SRF2};}}")
            btn.clicked.connect(dlg.accept)
        br=QHBoxLayout(); br.addStretch(); br.addWidget(btn); br.addStretch(); root.addLayout(br)
        dlg.exec()


    def retranslate(self):
        # main tab
        for key, text in [("folder", _t('batch_sub_folder')), ("file", _t('batch_sub_file'))]:
            if key in self._main_tab_btns: self._main_tab_btns[key].setText(text)
        # option tab
        for key, text in [("smart", _t('batch_opt_smart')), ("seq", _t('batch_opt_seq'))]:
            if key in self._opt_tab_btns: self._opt_tab_btns[key].setText(text)
        # folder tab
        self._f_btn_add.setText(_t('batch_btn_folder_pick'))
        if hasattr(self,"_f_btn_clear"): self._f_btn_clear.setText(_t("batch_del_all"))
        self._f_table.setHorizontalHeaderLabels([_t('batch_col_folder'), _t('batch_col_arrow'), _t('batch_col_new')])
        self._f_btn_preview.setText(_t('btn_preview'))
        self._f_btn_rename.setText(_t('batch_btn_rename'))
        # file tab
        self._p_btn_fadd.setText(_t('batch_btn_file_pick'))
        if hasattr(self,"_p_btn_clear"): self._p_btn_clear.setText(_t("batch_del_all"))
        self._p_table.setHorizontalHeaderLabels([_t('batch_col_file'), _t('batch_col_arrow'), _t('batch_col_file_new')])
        self._p_btn_preview.setText(_t('btn_preview'))
        self._p_btn_rename.setText(_t('batch_btn_rename'))
        # Smart tab GroupBox
        self._g_smart_pfx.setTitle(_t('batch_smart_pfx'))
        self._lbl_smart_pfx.setText(_t('batch_smart_prefix'))
        self._lbl_smart_sfx.setText(_t('batch_smart_suffix'))
        self._g_smart_common.setTitle(_t('batch_smart_common'))
        self._rb_auto.setText(_t('batch_smart_auto'))
        self._rb_manual.setText(_t('batch_smart_manual'))
        self._rb_none.setText(_t('batch_smart_none'))
        self._sm_manual_pfx.setPlaceholderText(_t("batch_smart_manual_ph"))
        self._sq_prefix.setPlaceholderText(_t("sq_prefix_ph2"))
        self._sq_suffix.setPlaceholderText(_t("sq_suffix_ph2"))
        self._sm_prefix.setPlaceholderText(_t("sm_prefix_ph"))
        self._sm_suffix.setPlaceholderText(_t("sm_suffix_ph"))
        self._sq_prefix.setPlaceholderText(_t("sq_prefix_ph"))
        self._sq_suffix.setPlaceholderText(_t("sq_suffix_ph"))
        if hasattr(self,"_p_custom_pfx"): self._p_custom_pfx.setPlaceholderText(_t("batch_file_pfx_ph"))
        if hasattr(self,"_p_ext_input"): self._p_ext_input.setPlaceholderText(_t("batch_file_ext_ph"))
        # Sequential tab GroupBox
        self._g_seq_reset.setTitle(_t('batch_seq_reset'))
        self._rb_seq_global.setText(_t('batch_seq_global'))
        self._rb_seq_reset.setText(_t('batch_seq_pergroup'))
        self._g_seq_start.setTitle(_t('batch_seq_start'))
        self._rb_s0.setText(_t('batch_seq_from0'))
        self._rb_s1.setText(_t('batch_seq_from1'))
        self._g_seq_digits.setTitle(_t('batch_seq_digits'))
        self._rb_d_auto.setText(_t('batch_seq_auto'))
        self._rb_d2.setText(_t('batch_seq_2d'))
        self._rb_d3.setText(_t('batch_seq_3d'))
        self._rb_d4.setText(_t('batch_seq_4d'))
        self._g_seq_pfx.setTitle(_t('batch_seq_pfx_lbl'))
        self._lbl_sq_pfx.setText(_t('batch_smart_prefix'))
        self._lbl_sq_sfx.setText(_t('batch_smart_suffix'))
        self._g_seq_name.setTitle(_t('batch_seq_name'))
        self._rb_numonly.setText(_t('batch_seq_numonly'))
        self._rb_keep.setText(_t('batch_seq_keep'))
        self._lbl_sq_sep.setText(_t('batch_seq_sep'))
        # File tab right-side panel
        self._gp.setTitle(_t('batch_file_pfx'))
        self._p_rb_folder.setText(_t('batch_file_pfx_folder'))
        self._p_rb_custom.setText(_t('batch_file_pfx_custom'))
        self._p_custom_pfx.setPlaceholderText(_t('batch_file_pfx_ph'))
        self._gs_row.setTitle(_t('batch_file_sep_start'))
        self._lbl_p_sep.setText(_t('batch_file_sep'))
        self._p_rb_s0.setText(_t('batch_file_from0'))
        self._p_rb_s1.setText(_t('batch_file_from1'))
        self._gpd.setTitle(_t('batch_file_digits'))
        self._p_rb_auto.setText(_t('batch_file_auto'))
        self._p_rb_nopad.setText(_t('batch_file_nopad'))
        self._p_rb_pad2.setText(_t('batch_file_2d'))
        self._p_rb_pad3.setText(_t('batch_file_3d'))
        self._gfl.setTitle(_t('batch_file_filter'))
        self._p_rb_all.setText(_t('batch_file_all'))
        self._p_rb_ext.setText(_t('batch_file_ext'))
        # count label
        _f_total = sum(len(g["children"]) for g in self._f_groups)
        _p_total = sum(len(self._p_filtered(g["files"])) for g in self._p_groups)
        self._f_lbl_count.setText(_t("batch_count_folder", g=len(self._f_groups), f=_f_total))
        self._p_lbl_count.setText(_t("batch_count_file", g=len(self._p_groups), f=_p_total))
        # output format label
        if hasattr(self,"_fmt_lbl"): self._fmt_lbl.setText(f"<b>{_t('batch_file_fmt_label')}</b><br><span style='color:{ACCENT};font-size:13px;'>{_t('batch_file_fmt_pattern')}</span>")
        # hint box
        self._hint_folder.setText(_t("batch_hint_folder"))
        self._hint_file.setText(_t("batch_hint_file"))
        # refresh collapsible button text
        f_arrow = "▲" if self._f_hint_open else "▼"
        self._f_hint_btn.setText(f"  {_t('batch_usage_title')}  {f_arrow}")
        p_arrow = "▲" if self._p_hint_open else "▼"
        self._p_hint_btn.setText(f"  {_t('batch_usage_title')}  {p_arrow}")
        # refresh dropzone wording
        if hasattr(self,"_f_drop"): self._f_drop.set_idle()
        if hasattr(self,"_p_drop"): self._p_drop.set_idle()
        if hasattr(self,"_f_btn_undo"): self._f_btn_undo.setText(_t('btn_undo'))
        if hasattr(self,"_p_btn_undo"): self._p_btn_undo.setText(_t('btn_undo'))

    # ── Settings save/restore ─────────────────
    def get_config(self) -> dict:
        return {
            'main_tab': self._cur_main_tab,
            'opt_tab':  self._cur_opt_tab,
            # smart tab
            'sm_prefix':    self._sm_prefix.text(),
            'sm_suffix':    self._sm_suffix.text(),
            'sm_pfx_mode':  'auto' if self._rb_auto.isChecked() else 'manual' if self._rb_manual.isChecked() else 'none',
            'sm_manual_pfx': self._sm_manual_pfx.text(),
            # seq tab
            'sq_seq_mode':  'reset' if self._rb_seq_reset.isChecked() else 'global',
            'sq_start':     '1' if self._rb_s1.isChecked() else '0',
            'sq_digits':    '2' if self._rb_d2.isChecked() else '3' if self._rb_d3.isChecked() else '4' if self._rb_d4.isChecked() else 'auto',
            'sq_prefix':    self._sq_prefix.text(),
            'sq_suffix':    self._sq_suffix.text(),
            'sq_name_mode': 'keep' if self._rb_keep.isChecked() else 'numonly',
            'sq_sep':       self._sq_sep.text(),
            # file tab
            'p_pfx_mode':   'custom' if self._p_rb_custom.isChecked() else 'folder',
            'p_custom_pfx': self._p_custom_pfx.text(),
            'p_sep':        self._p_sep.text(),
            'p_start':      '0' if self._p_rb_s0.isChecked() else '1',
            'p_pad':        'none' if self._p_rb_nopad.isChecked() else '2' if self._p_rb_pad2.isChecked() else '3' if self._p_rb_pad3.isChecked() else 'auto',
            'p_filter':     'ext' if self._p_rb_ext.isChecked() else 'all',
            'p_ext':        self._p_ext_input.text(),
        }

    def apply_config(self, d: dict):
        if not d: return
        # smart tab
        self._sm_prefix.setText(d.get('sm_prefix', ''))
        self._sm_suffix.setText(d.get('sm_suffix', ''))
        m = d.get('sm_pfx_mode', 'auto')
        if m == 'manual': self._rb_manual.setChecked(True)
        elif m == 'none': self._rb_none.setChecked(True)
        else: self._rb_auto.setChecked(True)
        self._sm_manual_pfx.setText(d.get('sm_manual_pfx', ''))
        # seq tab
        if d.get('sq_seq_mode') == 'reset': self._rb_seq_reset.setChecked(True)
        else: self._rb_seq_global.setChecked(True)
        if d.get('sq_start') == '1': self._rb_s1.setChecked(True)
        else: self._rb_s0.setChecked(True)
        digs = d.get('sq_digits', 'auto')
        {'2': self._rb_d2, '3': self._rb_d3, '4': self._rb_d4}.get(digs, self._rb_d_auto).setChecked(True)
        self._sq_prefix.setText(d.get('sq_prefix', ''))
        self._sq_suffix.setText(d.get('sq_suffix', ''))
        if d.get('sq_name_mode') == 'keep': self._rb_keep.setChecked(True)
        else: self._rb_numonly.setChecked(True)
        self._sq_sep.setText(d.get('sq_sep', '_') or '_')
        # file tab
        if d.get('p_pfx_mode') == 'custom': self._p_rb_custom.setChecked(True)
        else: self._p_rb_folder.setChecked(True)
        self._p_custom_pfx.setText(d.get('p_custom_pfx', ''))
        self._p_sep.setText(d.get('p_sep', '-') or '-')
        if d.get('p_start') == '0': self._p_rb_s0.setChecked(True)
        else: self._p_rb_s1.setChecked(True)
        pad = d.get('p_pad', 'auto')
        {'none': self._p_rb_nopad, '2': self._p_rb_pad2, '3': self._p_rb_pad3}.get(pad, self._p_rb_auto).setChecked(True)
        if d.get('p_filter') == 'ext': self._p_rb_ext.setChecked(True)
        else: self._p_rb_all.setChecked(True)
        self._p_ext_input.setText(d.get('p_ext', ''))
        # tabs
        if d.get('main_tab') == 'file': self._switch_main_tab('file')
        if d.get('opt_tab') == 'seq': self._switch_opt_tab('seq')


# ═══════════════════════════════════════════════
# Tab 2: Text Converter panel
# ═══════════════════════════════════════════════
class TextConverterPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._mode="txt2epub"
        self._worker=None; self._undo_data=None
        self._output_dir=""
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Mode tab bar (unified Tag Editor style) ──
        self._tab_bar = QWidget(); self._tab_bar.setFixedHeight(58)
        tbl = QHBoxLayout(self._tab_bar)
        tbl.setContentsMargins(8, 0, 0, 0)
        tbl.setSpacing(0)
        self._tab_btns = {}
        for val, label in [("txt2epub", "TXT → EPUB"), ("epub2txt", "EPUB → TXT")]:
            btn = QPushButton(label)
            btn.setCheckable(False)
            btn.clicked.connect(lambda _, v=val: self._switch(v))
            tbl.addWidget(btn)
            self._tab_btns[val] = btn
        tbl.addStretch()
        root.addWidget(self._tab_bar)

        sep = QFrame(); sep.setFrameShape(QFrame.HLine); sep.setObjectName("tab_sep")
        root.addWidget(sep)

        # ── Two-pane body ─────────────────────
        body = QWidget()
        body_lay = QHBoxLayout(body)
        body_lay.setContentsMargins(16, 14, 16, 14)
        body_lay.setSpacing(16)

        # ── Left: dropzone + file list + control buttons (v1.0.6 #7) ──
        left = QWidget()
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(0, 0, 0, 0)
        left_lay.setSpacing(10)

        # v1.0.6 #7: dropzone (top) — external file drops only, dynamic mode-based switching
        self._drop_zone = TextConverterDropZone()
        self._drop_zone.files_dropped.connect(self._on_files_dropped)
        left_lay.addWidget(self._drop_zone)

        # file-list title (BulkFixer pattern)
        self._lbl_file_list = QLabel(_t('conv_file_list'))
        self._lbl_file_list.setObjectName("grp_title_lbl")
        left_lay.addWidget(self._lbl_file_list)

        # create _flist first — top/bottom button connect() calls reference it
        self._flist = TextConverterFileList()
        self._flist.setMinimumHeight(200)
        self._lbl_cnt = QLabel(""); self._lbl_cnt.setObjectName("count_lbl")
        self._flist.files_changed.connect(lambda n: self._lbl_cnt.setText(_t("conv_file_count", n=n)))

        # top button row: add file / delete all (BulkFixer pattern)
        top_row = QHBoxLayout(); top_row.setSpacing(6)
        self._btn_add = QPushButton(_t('btn_add_file'))
        self._btn_add.setObjectName("btn_primary")
        self._btn_add.setIcon(_svg_icon('document', 'white')); self._btn_add.setIconSize(QSize(20,20))
        self._btn_add.clicked.connect(self._add_files)
        self._btn_clr = QPushButton(_t('btn_del_all'))
        self._btn_clr.setIcon(_svg_icon('trash', ACCENT)); self._btn_clr.setIconSize(QSize(20,20))
        self._btn_clr.clicked.connect(self._flist.clear_files)
        for btn in [self._btn_add, self._btn_clr]:
            btn.setFixedHeight(36)
        top_row.addWidget(self._btn_add)
        top_row.addStretch()
        top_row.addWidget(self._btn_clr)
        left_lay.addLayout(top_row)

        # file list — added to the layout (sorts via QTreeWidget header clicks)
        left_lay.addWidget(self._flist, 1)

        # bottom button row: delete-selected / up / down / count (BulkFixer pattern)
        bot_row = QHBoxLayout(); bot_row.setSpacing(6)
        self._btn_del = QPushButton(_t('btn_del_sel'))
        self._btn_del.setIcon(_svg_icon('trash', ACCENT)); self._btn_del.setIconSize(QSize(20,20))
        self._btn_del.clicked.connect(self._flist.remove_selected)
        self._btn_up = QPushButton(_t('btn_up'))
        self._btn_up.setIcon(_svg_icon('arrow_up', ACCENT)); self._btn_up.setIconSize(QSize(16,16))
        self._btn_up.clicked.connect(lambda: self._flist.move_selection(-1))
        self._btn_dn = QPushButton(_t('btn_down'))
        self._btn_dn.setIcon(_svg_icon('arrow_down', ACCENT)); self._btn_dn.setIconSize(QSize(16,16))
        self._btn_dn.clicked.connect(lambda: self._flist.move_selection(1))
        for btn in [self._btn_del, self._btn_up, self._btn_dn]:
            btn.setFixedHeight(36)
        bot_row.addWidget(self._btn_del)
        bot_row.addWidget(self._btn_up)
        bot_row.addWidget(self._btn_dn)
        bot_row.addStretch()
        bot_row.addWidget(self._lbl_cnt)
        left_lay.addLayout(bot_row)

        body_lay.addWidget(left, stretch=5)

        # ── Right: per-mode options ─────────────
        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(10)

        # EPUB→TXT options
        self._c_epub_opts = QGroupBox(_t("conv_opt_epub2txt"))
        epub_lay = QVBoxLayout(self._c_epub_opts)
        epub_lay.setContentsMargins(10, 6, 10, 8)
        epub_lay.setSpacing(8)
        self._chk_sep  = QCheckBox(_t("conv_chk_sep")); self._chk_sep.setChecked(True)
        self._chk_ttl  = QCheckBox(_t("conv_chk_title"));  self._chk_ttl.setChecked(True)
        self._chk_trim = QCheckBox(_t("conv_chk_trim"));  self._chk_trim.setChecked(True)
        epub_lay.addWidget(self._chk_sep)
        epub_lay.addWidget(self._chk_ttl)
        epub_lay.addWidget(self._chk_trim)
        enc_row = QHBoxLayout(); enc_row.setSpacing(8)
        self._lbl_enc=QLabel(_t("conv_save_enc")); self._lbl_enc.setObjectName("field_lbl"); enc_row.addWidget(self._lbl_enc)
        self._combo_enc = _ThemedCombo()
        self._combo_enc.addItems(["utf-8", "utf-8-sig", "cp949", "euc-kr"])
        self._combo_enc.setFixedWidth(150)
        enc_row.addWidget(self._combo_enc)
        self._combo_enc.setFixedHeight(30)
        self._combo_enc.setStyleSheet(
            f"QComboBox{{background:{SURFACE};border:1.5px solid {BORDER};"
            f"border-radius:8px;color:{TEXT};"
            f"padding:3px 28px 3px 10px;font-size:13px;min-height:18px;}}"
            f"QComboBox:focus{{border-color:{ACCENT};}}"
            f"QComboBox:hover{{border-color:{INPUT_H};}}"
            f"QComboBox::drop-down{{subcontrol-origin:padding;"
            f"subcontrol-position:right center;width:26px;border:none;"
            f"border-left:1px solid {BORDER};"
            f"border-top-right-radius:8px;border-bottom-right-radius:8px;"
            f"background:{SRF2};}}"
            f"QComboBox::down-arrow{{image:{_combo_arrow_url(MUTED)};width:10px;height:6px;}}"
            f"QComboBox:hover::down-arrow{{image:{_combo_arrow_url(TEXT)};}}"
            f"QComboBox:focus::down-arrow{{image:{_combo_arrow_url(ACCENT)};}}"); enc_row.addStretch()
        epub_lay.addLayout(enc_row)
        right_lay.addWidget(self._c_epub_opts)

        # TXT→EPUB meta options
        self._c_txt_meta = QGroupBox(_t("conv_meta"))
        meta_lay = QVBoxLayout(self._c_txt_meta)
        meta_lay.setContentsMargins(10, 6, 10, 8)
        meta_lay.setSpacing(8)
        self._lbl_book_title=QLabel(_t("conv_book_title")); self._lbl_book_title.setObjectName("field_lbl"); meta_lay.addWidget(self._lbl_book_title)
        self._edit_title = QLineEdit(); self._edit_title.setPlaceholderText(_t('tc_title_placeholder'))
        meta_lay.addWidget(self._edit_title)
        self._lbl_author=QLabel(_t("conv_author")); self._lbl_author.setObjectName("field_lbl"); meta_lay.addWidget(self._lbl_author)
        self._edit_author = QLineEdit(); self._edit_author.setPlaceholderText(_t('tc_author_placeholder'))
        meta_lay.addWidget(self._edit_author)
        self._lbl_lang=QLabel(_t("conv_lang")); self._lbl_lang.setObjectName("field_lbl"); meta_lay.addWidget(self._lbl_lang)
        self._combo_lang = _ThemedCombo()
        self._combo_lang.addItems(["한국어 (ko)", "English (en)", "日本語 (ja)", "中文 简体 (zh-CN)", "中文 繁體 (zh-TW)"])
        self._combo_lang_codes = ["ko", "en", "ja", "zh-CN", "zh-TW"]
        meta_lay.addWidget(self._combo_lang)
        self._combo_lang.setFixedHeight(30)
        self._combo_lang.setStyleSheet(
            f"QComboBox{{background:{SURFACE};border:1.5px solid {BORDER};"
            f"border-radius:8px;color:{TEXT};"
            f"padding:3px 28px 3px 10px;font-size:13px;min-height:18px;}}"
            f"QComboBox:focus{{border-color:{ACCENT};}}"
            f"QComboBox:hover{{border-color:{INPUT_H};}}"
            f"QComboBox::drop-down{{subcontrol-origin:padding;"
            f"subcontrol-position:right center;width:26px;border:none;"
            f"border-left:1px solid {BORDER};"
            f"border-top-right-radius:8px;border-bottom-right-radius:8px;"
            f"background:{SRF2};}}"
            f"QComboBox::down-arrow{{image:{_combo_arrow_url(MUTED)};width:10px;height:6px;}}"
            f"QComboBox:hover::down-arrow{{image:{_combo_arrow_url(TEXT)};}}"
            f"QComboBox:focus::down-arrow{{image:{_combo_arrow_url(ACCENT)};}}")
        self._lbl_ch_mode=QLabel(_t("conv_chapter_mode")); self._lbl_ch_mode.setObjectName("field_lbl"); meta_lay.addWidget(self._lbl_ch_mode)
        self._combo_ch = _ThemedCombo()
        self._combo_ch.addItems([_t('conv_ch0'), _t('conv_ch1'), _t('conv_ch2')])
        meta_lay.addWidget(self._combo_ch)
        self._combo_ch.setFixedHeight(30)
        self._combo_ch.setStyleSheet(
            f"QComboBox{{background:{SURFACE};border:1.5px solid {BORDER};"
            f"border-radius:8px;color:{TEXT};"
            f"padding:3px 28px 3px 10px;font-size:13px;min-height:18px;}}"
            f"QComboBox:focus{{border-color:{ACCENT};}}"
            f"QComboBox:hover{{border-color:{INPUT_H};}}"
            f"QComboBox::drop-down{{subcontrol-origin:padding;"
            f"subcontrol-position:right center;width:26px;border:none;"
            f"border-left:1px solid {BORDER};"
            f"border-top-right-radius:8px;border-bottom-right-radius:8px;"
            f"background:{SRF2};}}"
            f"QComboBox::down-arrow{{image:{_combo_arrow_url(MUTED)};width:10px;height:6px;}}"
            f"QComboBox:hover::down-arrow{{image:{_combo_arrow_url(TEXT)};}}"
            f"QComboBox:focus::down-arrow{{image:{_combo_arrow_url(ACCENT)};}}")
        right_lay.addWidget(self._c_txt_meta)

        # output folder (v1.0.6 #7: moved left → right)
        out_gb = QGroupBox(_t("conv_out_folder")); self._out_gb=out_gb
        out_inner = QVBoxLayout(out_gb)
        out_inner.setContentsMargins(10, 6, 10, 8)
        out_inner.setSpacing(6)
        orow = QHBoxLayout(); orow.setSpacing(6)
        self._edit_odir = QLineEdit()
        self._edit_odir.setPlaceholderText(_t("conv_out_ph"))
        self._edit_odir.setFixedHeight(36)
        self._btn_brw = QPushButton(_t("conv_btn_pick")); self._btn_brw.setObjectName("btn_primary"); self._btn_brw.setFixedHeight(36); self._btn_brw.clicked.connect(self._browse_out)
        self._btn_brw.setIcon(_svg_icon('folder', 'white')); self._btn_brw.setIconSize(QSize(20,20))
        self._btn_opn = QPushButton(""); self._btn_opn.setFixedSize(36, 36); self._btn_opn.setToolTip(_t("open_folder_tooltip")); self._btn_opn.clicked.connect(self._open_out_dir)
        self._btn_opn.setIcon(_svg_icon('folder_open', ACCENT)); self._btn_opn.setIconSize(QSize(20,20))
        orow.addWidget(self._edit_odir, 1); orow.addWidget(self._btn_brw); orow.addWidget(self._btn_opn)
        out_inner.addLayout(orow)
        right_lay.addWidget(out_gb)

        # convert / undo buttons (v1.0.6 #7: moved left → right, kept 2-line vertical layout)
        self._btn_convert = QPushButton(_t("conv_btn_start")); self._btn_convert.setObjectName("btn_merge")
        self._btn_convert.setIcon(_svg_icon('refresh', 'white')); self._btn_convert.setIconSize(QSize(22,22))
        self._btn_convert.setFixedHeight(44)
        self._btn_convert.clicked.connect(self._start)
        right_lay.addWidget(self._btn_convert)

        self._btn_undo = QPushButton(_t('btn_undo')); self._btn_undo.setObjectName("btn_undo")
        self._btn_undo.setFixedHeight(44); self._btn_undo.setEnabled(False)
        self._btn_undo.clicked.connect(self._undo)
        right_lay.addWidget(self._btn_undo)

        # progress bar (v1.0.6 #7: moved left → right)
        self._progress = QProgressBar()
        self._progress.setRange(0, 100); self._progress.setValue(0)
        self._progress.setFixedHeight(8); self._progress.setTextVisible(False)
        self._progress.setVisible(False)
        right_lay.addWidget(self._progress)

        # current-file progress bar
        self._file_progress = QProgressBar()
        self._file_progress.setRange(0, 100); self._file_progress.setValue(0)
        self._file_progress.setFixedHeight(5); self._file_progress.setTextVisible(False)
        self._file_progress.setVisible(False)
        self._file_progress.setStyleSheet(
            f"QProgressBar{{border:none;background:{BORDER};border-radius:2px;}}"
            f"QProgressBar::chunk{{background:{ACCENT};border-radius:2px;opacity:0.7;}}")
        right_lay.addWidget(self._file_progress)

        self._lbl_file_progress = QLabel("")
        self._lbl_file_progress.setStyleSheet(
            f"font-size:11px;color:{MUTED};"
            f"font-family:'Consolas','Courier New','Menlo',monospace;")
        self._lbl_file_progress.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._lbl_file_progress.setFixedHeight(16)
        self._lbl_file_progress.setVisible(False)
        right_lay.addWidget(self._lbl_file_progress)

        # status label (v1.0.6 #7: moved left → right)
        self._lbl_status = QLabel(_t("conv_status_start"))
        self._lbl_status.setStyleSheet("font-size:13px;")
        self._lbl_status.setWordWrap(True)
        right_lay.addWidget(self._lbl_status)

        right_lay.addStretch()

        body_lay.addWidget(right, stretch=4)
        root.addWidget(body, stretch=1)
        self._switch("txt2epub")



    def _switch(self,mode):
        self._mode=mode
        for val,btn in self._tab_btns.items():
            active=(val==mode)
            btn.setStyleSheet(
                f"QPushButton{{background:{_accent_alpha(0.12) if active else 'transparent'};"
                f"border:none;border-bottom:2px solid {ACCENT if active else 'transparent'};"
                f"border-radius:0;padding:8px 16px;"
                f"color:{ACCENT if active else MUTED};"
                f"font-size:13px;font-weight:{'600' if active else '500'};min-width:90px;}}"
            )
        self._c_epub_opts.setVisible(mode=="epub2txt")
        self._c_txt_meta.setVisible(mode=="txt2epub")
        self._flist.set_mode(mode)
        # v1.0.6 #7: refresh dropzone text/icon immediately on mode switch
        if hasattr(self, '_drop_zone'):
            self._drop_zone.set_mode(mode)

    def _add_files(self):
        ext="EPUB (*.epub)" if self._mode=="epub2txt" else "TXT (*.txt)"
        paths,_=QFileDialog.getOpenFileNames(self,_t('btn_add_file'),self._edit_odir.text() or str(Path.home()),ext)
        def warn(names): _dlg_warn(self, _t('dlg_warning'), f"{_t('conv_unsupported')}:\n"+"\n".join(names))
        self._flist.add_files(paths,warn_fn=warn)

    def _on_files_dropped(self, paths: list):
        """v1.0.6 #7: called when a file is dropped on TextConverterDropZone.

        The dropzone applies first-pass filtering by mode (rejects wrong extensions),
        but defensively reuses the warn logic in _add_files for safe handling.
        """
        if not paths: return
        def warn(names): _dlg_warn(self, _t('dlg_warning'), f"{_t('conv_unsupported')}:\n"+"\n".join(names))
        self._flist.add_files(paths, warn_fn=warn)

    def _browse_out(self):
        start = self._edit_odir.text() or _CFG.get('output_dir', str(_OUTPUT_DIR))
        d=QFileDialog.getExistingDirectory(self,_t('conv_btn_pick'), start)
        if d: self._edit_odir.setText(d)

    def _open_out_dir(self):
        d = self._edit_odir.text().strip()
        if not d or not os.path.isdir(d):
            # fall back to the original file's location if no output folder is set
            if self._flist.files:
                d = os.path.dirname(self._flist.files[0])
            if not d or not os.path.isdir(d):
                _dlg_warn(self, _t('dlg_warning'), _t('conv_no_outdir')); return
        if sys.platform == "win32": os.startfile(d)
        elif sys.platform == "darwin": subprocess.Popen(["open", d])
        else: subprocess.Popen(["xdg-open", d])

    def _wlog(self,msg,tag=""):
        if msg.strip(): _glog(f"  [convert] {msg.strip()}")

    def _start(self):
        files=self._flist.files
        if not files: _dlg_warn(self, _t('dlg_warning'), _t('conv_no_files_msg')); return
        if self._worker and self._worker.isRunning(): return  # prevent duplicate runs
        self._progress.setValue(0)
        self._btn_convert.setEnabled(False); self._btn_convert.setText(_t("conv_btn_converting")); self._lbl_status.setText(_t("conv_btn_converting").replace("⏳ ",""))
        odir=self._edit_odir.text().strip()
        if odir and not Path(odir).is_dir():
            self._btn_convert.setEnabled(True); self._btn_convert.setText(_t("conv_btn_start"))
            _dlg_warn(self, _t('dlg_warning'), _t('conv_outdir_miss')); return
        if self._mode=="epub2txt":
            opts={"separator":self._chk_sep.isChecked(),"titles":self._chk_ttl.isChecked(),"trim_blank":self._chk_trim.isChecked(),"encoding":self._combo_enc.currentText()}
        else:
            lcode = self._combo_lang_codes[self._combo_lang.currentIndex()] if hasattr(self, '_combo_lang') else "ko"
            ci=self._combo_ch.currentIndex()
            cm=["separator","emptylines","single"][ci] if ci>=0 else "separator"
            opts={"title":self._edit_title.text().strip(),"author":self._edit_author.text().strip() or _t('tc_author_placeholder'),"lang":lcode,"chapter_mode":cm}
        snap=self._mode
        label="EPUB→TXT" if self._mode=="epub2txt" else "TXT→EPUB"
        _glog(f"▶ [Text Converter] {label} conversion started — {len(files)} file(s)")
        # safely release the previous worker
        if self._worker is not None:
            try:
                self._worker.sig_progress.disconnect()
                self._worker.sig_log.disconnect()
                self._worker.sig_files.disconnect()
                self._worker.sig_file_progress.disconnect()
                self._worker.sig_done.disconnect()
            except Exception:
                pass
            self._worker = None
        self._worker=ConvertWorker(files,self._mode,opts,odir)
        self._progress.setValue(0); self._progress.setVisible(True)
        self._file_progress.setValue(0); self._file_progress.setVisible(True)
        self._lbl_file_progress.setText(""); self._lbl_file_progress.setVisible(True)
        self._worker.sig_progress.connect(self._progress.setValue)
        self._worker.sig_file_progress.connect(self._on_file_progress)
        self._worker.sig_log.connect(self._wlog)
        self._worker.sig_files.connect(self._on_files)
        self._worker.sig_done.connect(lambda s,ok,fail,d: self._on_done(s,ok,fail,d,snap))
        self._worker.start()

    def _on_file_progress(self, pct: int, fname: str):
        self._file_progress.setValue(pct)
        self._lbl_file_progress.setText(f"{fname}  {pct:>3d}%")

    def _on_files(self, file_list):
        """Receive the list of converted files — stored for undo."""
        self._undo_data = ('files', file_list)
        if hasattr(self, '_btn_undo'): self._btn_undo.setEnabled(True)

    def _on_done(self,success,ok,fail,out_dir,mode):
        self._btn_convert.setEnabled(True); self._btn_convert.setText(_t("conv_btn_start"))
        # hide progress bar and file-progress label
        self._progress.setValue(0); self._progress.setVisible(False)
        self._file_progress.setValue(0); self._file_progress.setVisible(False)
        self._lbl_file_progress.setText(""); self._lbl_file_progress.setVisible(False)
        label="EPUB→TXT" if mode=="epub2txt" else "TXT→EPUB"
        if success:
            self._lbl_status.setText(_t('conv_status_done'))
            _glog(f"  [Text Converter] {label} done — {ok} succeeded" + (f", {fail} failed" if fail else ""))
            if out_dir: _glog(f"  saved to: {out_dir}")
            msg = f"{label}\n\n{_t('bulk_status_done', n=ok)}"
            if fail: msg += f"\n{_t('dlg_done_err')} ×{fail}"
            if out_dir: msg += f"\n\n{_t('merge_save_path')}\n{out_dir}"
            _dlg_info(self, _t('dlg_done'), msg)
            # auto-open output folder after saving completes
            if out_dir and os.path.isdir(out_dir):
                try: os.startfile(out_dir)
                except Exception: pass
        else:
            self._lbl_status.setText(_t('conv_status_fail'))
            _glog(f"  [Text Converter] {label} conversion failed")


    def is_busy(self) -> bool:
        """True while the conversion worker is running."""
        return bool(self._worker and self._worker.isRunning())

    def _stop_worker(self):
        if self._worker and self._worker.isRunning():
            try:
                self._worker.sig_progress.disconnect()
                self._worker.sig_log.disconnect()
                self._worker.sig_files.disconnect()
                self._worker.sig_file_progress.disconnect()
                self._worker.sig_done.disconnect()
            except Exception:
                pass
            self._worker.quit()
            if not self._worker.wait(2000):
                self._worker.terminate(); self._worker.wait(500)

    def _undo(self):
        """Undo the last conversion by deleting the produced files."""
        if not self._undo_data: return
        kind, file_list = self._undo_data
        _glog(f"↩ [Text Converter] undo — {len(file_list)} file(s)")
        deleted=[]; errors=[]
        for path in file_list:
            try:
                if os.path.exists(path):
                    os.remove(path); deleted.append(path)
                    _glog(f"  ✅ deleted: {os.path.basename(path)}")
                else:
                    errors.append(f"{os.path.basename(path)}: file not found")
            except OSError as e:
                errors.append(f"{os.path.basename(path)}: {e}")
        self._undo_data = None
        if hasattr(self, '_btn_undo'): self._btn_undo.setEnabled(False)
        msg = _t('tag_apply_done', n=len(deleted), label=_t('dlg_undo'))
        if errors: msg += f'  {_t("dlg_done_err")} ×{len(errors)}'
        _glog(f"  done: {msg}")
        if errors: _dlg_warn(self, _t('dlg_undo'), msg + "\n\n" + "\n".join(errors[:10]))
        else: _dlg_info(self, _t('dlg_undo'), msg)

    def refresh_btn_styles(self):
        """On theme change, directly refresh buttons that the QSS cascade does not reach."""
        secondary_ss = (f"QPushButton{{background:{SURFACE};border:1.5px solid {BTN_BORDER_H};"
                        f"color:{TEXT};border-radius:8px;padding:5px 12px;}}"
                        f"QPushButton:hover{{background:{SRF2};border-color:{ACCENT};}}"
                        f"QPushButton:pressed{{background:{BTN_PRESSED};}}"
                        f"QPushButton:disabled{{background:{SRF2};color:{DISABLED};}}")
        for attr in ('_btn_del', '_btn_clr', '_btn_up', '_btn_dn'):
            if hasattr(self, attr): getattr(self, attr).setStyleSheet(secondary_ss)
        if hasattr(self, '_btn_undo'): self._btn_undo.setStyleSheet(secondary_ss)
        if hasattr(self, '_btn_opn'):
            icon_btn_ss = (f"QPushButton{{background:{SURFACE};border:1.5px solid {BORDER};"
                           f"color:{TEXT};border-radius:8px;padding:0;font-size:16px;}}"
                           f"QPushButton:hover{{background:{SRF2};border-color:{ACCENT};}}"
                           f"QPushButton:pressed{{background:{BTN_PRESSED};}}"
                           f"QPushButton:disabled{{background:{SRF2};color:{DISABLED};}}")
            self._btn_opn.setStyleSheet(icon_btn_ss)
        # refresh SVG icon colors (when ACCENT changes)
        _isz = QSize(20,20)
        for attr, key in [('_btn_del','trash'),('_btn_clr','trash'),
                          ('_btn_up','arrow_up'),('_btn_dn','arrow_down'),
                          ('_btn_opn','folder_open')]:
            if hasattr(self, attr): getattr(self, attr).setIcon(_svg_icon(key, ACCENT)); getattr(self, attr).setIconSize(_isz)
        # refresh combobox inline style
        _css = _themed_combo_ss()
        for attr in ('_combo_enc', '_combo_lang', '_combo_ch'):
            if hasattr(self, attr): getattr(self, attr).setStyleSheet(_css)
        # refresh file-list tree style
        if hasattr(self, '_flist'):
            self._flist.setStyleSheet(
                f"QTreeWidget{{background:{SURFACE};border:1px solid {BORDER};"
                f"border-radius:8px;color:{TEXT};font-size:13px;outline:none;"
                f"alternate-background-color:{SRF2};}}"
                f"QTreeWidget::item{{padding:4px 6px;}}"
                f"QTreeWidget::item:selected{{background:{_accent_alpha(0.12)};color:{TEXT};}}"
                f"QHeaderView::section{{background:{SRF2};border:none;"
                f"border-bottom:1px solid {BORDER};border-right:1px solid {BORDER};"
                f"color:{MUTED};font-size:11px;font-weight:600;padding:6px 10px;}}"
                f"QHeaderView::section:first{{border-top-left-radius:7px;}}"
                f"QHeaderView::section:last{{border-top-right-radius:7px;border-right:none;}}"
            )
        # refresh progress-bar style
        if hasattr(self, '_file_progress'):
            self._file_progress.setStyleSheet(
                f"QProgressBar{{border:none;background:{BORDER};border-radius:2px;}}"
                f"QProgressBar::chunk{{background:{ACCENT};border-radius:2px;opacity:0.7;}}")
        if hasattr(self, '_lbl_file_progress'):
            self._lbl_file_progress.setStyleSheet(
                f"font-size:11px;color:{MUTED};"
                f"font-family:'Consolas','Courier New','Menlo',monospace;")
        # v1.0.6 #7: dropzone responds to theme switch
        if hasattr(self, '_drop_zone'):
            self._drop_zone.refresh_style()

    def retranslate(self):
        self._flist.setHeaderLabels([_t('tag_col_filename'), _t('tag_col_path')])
        # v1.0.6 #7: viewport().update() unnecessary now that paintEvent is removed (dropzone owns the text)
        self._lbl_file_list.setText(_t('conv_file_list'))
        for val, btn in self._tab_btns.items():
            btn.setText(_t('conv_sub_' + val))
        self._out_gb.setTitle(_t('conv_out_folder'))
        self._edit_odir.setPlaceholderText(_t('conv_out_ph'))
        self._btn_brw.setText(_t('conv_btn_pick'))
        self._btn_add.setText(_t('btn_add_file'))
        self._btn_del.setText(_t('btn_del_sel'))
        self._btn_clr.setText(_t('btn_del_all'))
        self._btn_up.setText(_t('btn_up'))
        self._btn_dn.setText(_t('btn_down'))
        if self._btn_convert.isEnabled():
            self._btn_convert.setText(_t('conv_btn_start'))
        if hasattr(self, '_btn_undo'): self._btn_undo.setText(_t('btn_undo'))
        self._c_epub_opts.setTitle(_t('conv_opt_epub2txt'))
        self._chk_sep.setText(_t('conv_chk_sep'))
        self._chk_ttl.setText(_t('conv_chk_title'))
        self._chk_trim.setText(_t('conv_chk_trim'))
        self._lbl_enc.setText(_t('conv_save_enc'))
        if hasattr(self,"_btn_opn"): self._btn_opn.setToolTip(_t("open_folder_tooltip"))
        self._c_txt_meta.setTitle(_t('conv_meta'))
        self._lbl_book_title.setText(_t('conv_book_title'))
        self._lbl_author.setText(_t('conv_author'))
        self._edit_title.setPlaceholderText(_t('tc_title_placeholder'))
        self._edit_author.setPlaceholderText(_t('tc_author_placeholder'))
        self._lbl_lang.setText(_t('conv_lang'))
        self._lbl_ch_mode.setText(_t('conv_chapter_mode'))
        ci = self._combo_ch.currentIndex()
        self._combo_ch.clear()
        self._combo_ch.addItems([_t('conv_ch0'), _t('conv_ch1'), _t('conv_ch2')])
        self._combo_ch.setCurrentIndex(ci)
        # v1.0.6 #7: re-render dropzone text/icon in the current language (conv_help reference removed along with _help_box)
        if hasattr(self, '_drop_zone'):
            self._drop_zone.set_mode(self._mode)
        if self._lbl_status.text() in _all_translations_of('conv_status_start'):
            self._lbl_status.setText(_t('conv_status_start'))

    # ── Settings save/restore ─────────────────
    def get_config(self) -> dict:
        lcode = self._combo_lang_codes[self._combo_lang.currentIndex()] if hasattr(self, '_combo_lang') else "ko"
        return {
            'mode':         self._mode,
            'output_dir':   self._edit_odir.text(),
            'chk_sep':      self._chk_sep.isChecked(),
            'chk_ttl':      self._chk_ttl.isChecked(),
            'chk_trim':     self._chk_trim.isChecked(),
            'combo_enc':    self._combo_enc.currentText(),
            'title':        self._edit_title.text(),
            'author':       self._edit_author.text(),
            'lang':         lcode,
            'combo_ch':     self._combo_ch.currentIndex(),
        }

    def apply_config(self, d: dict):
        if not d: return
        self._edit_odir.setText(d.get('output_dir', _CFG.get('output_dir', str(_OUTPUT_DIR))))
        self._chk_sep.setChecked(d.get('chk_sep', True))
        self._chk_ttl.setChecked(d.get('chk_ttl', True))
        self._chk_trim.setChecked(d.get('chk_trim', True))
        enc = d.get('combo_enc', 'utf-8')
        idx = self._combo_enc.findText(enc)
        if idx >= 0: self._combo_enc.setCurrentIndex(idx)
        self._edit_title.setText(d.get('title', ''))
        self._edit_author.setText(d.get('author', ''))
        lang = d.get('lang', 'ko')
        if hasattr(self, '_combo_lang_codes') and lang in self._combo_lang_codes:
            self._combo_lang.setCurrentIndex(self._combo_lang_codes.index(lang))
        ci = d.get('combo_ch', 0)
        if isinstance(ci, int) and 0 <= ci < self._combo_ch.count():
            self._combo_ch.setCurrentIndex(ci)
        mode = d.get('mode', 'txt2epub')
        if mode in ('txt2epub', 'epub2txt'): self._switch(mode)


# ═══════════════════════════════════════════════
# Tab 3: Tag Editor panel
# ═══════════════════════════════════════════════
class TagEditorPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._mode="remove"
        self._targets=[]; self._undo_data=None
        self._file_paths=[]; self._file_paths_set=set()
        self._allext_saved=None
        self._build()
        self._update_tab_style()
        self._apply_mode_ui()
        self._refresh_tree_styles()

    def _build(self):
        root=QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        # ── Tab bar ──────────────────────────────
        tab_bar=QWidget(); tab_bar.setFixedHeight(50)
        tl=QHBoxLayout(tab_bar); tl.setContentsMargins(8,0,0,0); tl.setSpacing(0)
        self._tab_btns={}
        for mk,key in [("remove","tag_sub_remove"),("add","tag_sub_add"),("depad","tag_sub_depad")]:
            btn=QPushButton(_t(key)); btn.setCheckable(False)
            btn.clicked.connect(lambda _,m=mk: self._switch_mode(m))
            tl.addWidget(btn); self._tab_btns[mk]=btn
        tl.addStretch(); root.addWidget(tab_bar)
        sep=QFrame(); sep.setFrameShape(QFrame.HLine); sep.setObjectName("tab_sep")
        root.addWidget(sep)

        # ── Two-pane body ────────────────────────
        body=QWidget()
        body_lay=QHBoxLayout(body)
        body_lay.setContentsMargins(14,12,14,12)
        body_lay.setSpacing(14)

        # ── Left: file input area ────────────────
        left=QWidget()
        ll=QVBoxLayout(left); ll.setContentsMargins(0,0,0,0); ll.setSpacing(8)

        # dropzone
        self._drop_zone=TagDropZone()
        self._drop_zone.folder_dropped.connect(self._on_folder_dropped)
        self._drop_zone.files_dropped.connect(self._on_files_dropped)
        ll.addWidget(self._drop_zone)

        # file add/delete button row
        btn_row=QHBoxLayout(); btn_row.setSpacing(8)
        self._btn_add_files=QPushButton(_t('btn_add_file')); self._btn_add_files.setObjectName("btn_primary"); self._btn_add_files.clicked.connect(self._add_files_dialog)
        self._btn_add_files.setIcon(_svg_icon('document', 'white')); self._btn_add_files.setIconSize(QSize(20,20))
        self._btn_add_folder=QPushButton(_t('btn_add_folder')); self._btn_add_folder.setObjectName("btn_folder_add"); self._btn_add_folder.clicked.connect(self._add_folder_dialog)
        self._btn_add_folder.setIcon(_svg_icon('folder_open', 'white')); self._btn_add_folder.setIconSize(QSize(20,20))
        self._file_count_lbl=QLabel(""); self._file_count_lbl.setObjectName("count_lbl")
        self._btn_del_all=QPushButton(_t('btn_del_all')); self._btn_del_all.setMinimumWidth(90); self._btn_del_all.setFixedHeight(36); self._btn_del_all.clicked.connect(self._del_all_files)
        self._btn_del_all.setIcon(_svg_icon('trash', ACCENT)); self._btn_del_all.setIconSize(QSize(20,20))
        btn_row.addWidget(self._btn_add_files); btn_row.addWidget(self._btn_add_folder)
        btn_row.addStretch(); btn_row.addWidget(self._file_count_lbl); btn_row.addWidget(self._btn_del_all)
        ll.addLayout(btn_row)

        # file list (GroupBox removed — table placed directly)
        self._file_list=QTreeWidget(); self._file_list.setColumnCount(2)
        self._file_list.setAlternatingRowColors(True)
        self._file_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._file_list.setRootIsDecorated(False); self._file_list.setUniformRowHeights(True)
        hfl=self._file_list.header()
        hfl.setSectionResizeMode(0,QHeaderView.Stretch)
        hfl.setSectionResizeMode(1,QHeaderView.Interactive)
        self._file_list.setColumnWidth(1, 160)
        self._file_list.setHeaderLabels([_t("tag_col_filename"),_t("tag_col_path")])
        self._file_list.setSortingEnabled(True)
        self._file_list.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        hfl.setSortIndicatorShown(True)
        self._btn_del_sel=QPushButton(_t('btn_del_sel')); self._btn_del_sel.setMinimumWidth(90); self._btn_del_sel.setFixedHeight(36); self._btn_del_sel.clicked.connect(self._del_selected_files)
        self._btn_del_sel.setIcon(_svg_icon('trash', ACCENT)); self._btn_del_sel.setIconSize(QSize(20,20))
        del_row=QHBoxLayout(); del_row.addStretch(); del_row.addWidget(self._btn_del_sel)
        ll.addWidget(self._file_list, 1)
        # folder-scan progress bar (hidden by default)
        self._scan_bar = QProgressBar()
        self._scan_bar.setRange(0, 100); self._scan_bar.setValue(0)
        self._scan_bar.setFixedHeight(5); self._scan_bar.setTextVisible(False)
        self._scan_bar.setStyleSheet(
            f"QProgressBar{{border:none;background:{BORDER};border-radius:2px;}}"
            f"QProgressBar::chunk{{background:{ACCENT};border-radius:2px;opacity:0.7;}}")
        self._scan_bar.setVisible(False)
        ll.addWidget(self._scan_bar)
        self._scan_lbl = QLabel("")
        self._scan_lbl.setStyleSheet(
            f"font-size:11px;color:{MUTED};"
            f"font-family:'Consolas','Courier New','Menlo',monospace;")
        self._scan_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._scan_lbl.setFixedHeight(16)
        self._scan_lbl.setVisible(False)
        ll.addWidget(self._scan_lbl)
        self._scan_worker = None
        ll.addLayout(del_row)

        # target extensions
        ext_gb=QGroupBox(_t("tag_filter")); self._ext_gb=ext_gb
        ext_gl=QVBoxLayout(ext_gb); ext_gl.setContentsMargins(8,4,8,6); ext_gl.setSpacing(6)
        ext_row=QHBoxLayout(); ext_row.setSpacing(8)
        self._lbl_ext=QLabel(_t("tag_ext_label")); self._lbl_ext.setObjectName("field_lbl"); ext_row.addWidget(self._lbl_ext)
        self._ext_edit=QLineEdit("mp4, mkv, avi, srt, txt")
        self._lbl_ext_hint=QLabel(_t("tag_ext_hint")); self._lbl_ext_hint.setObjectName("field_lbl"); ext_row.addWidget(self._ext_edit,1); ext_row.addWidget(self._lbl_ext_hint)
        ext_gl.addLayout(ext_row)
        opt_row=QHBoxLayout(); opt_row.setSpacing(16)
        self._cb_recursive=QCheckBox(_t("tag_cb_recursive")); self._cb_recursive.setChecked(True)
        self._cb_allext=QCheckBox(_t("tag_cb_allext")); self._cb_allext.setChecked(False)
        opt_row.addWidget(self._cb_recursive); opt_row.addWidget(self._cb_allext); opt_row.addStretch()
        ext_gl.addLayout(opt_row)
        ll.addWidget(ext_gb)

        body_lay.addWidget(left, stretch=3)

        # ── Right: options + preview ────────────
        right=QWidget()
        rl=QVBoxLayout(right); rl.setContentsMargins(0,0,0,0); rl.setSpacing(8)

        # per-mode options panel
        self._remove_panel=self._make_remove_panel()
        self._add_panel=self._make_add_panel()
        rl.addWidget(self._remove_panel)
        rl.addWidget(self._add_panel)
        # initial state: remove mode, so hide add_panel immediately (avoids dead space)
        self._add_panel.setMaximumHeight(0)
        self._add_panel.hide()

        # change preview (GroupBox removed — table placed directly)
        count_row=QHBoxLayout()
        count_row.addStretch()
        self._count_lbl=QLabel(""); self._count_lbl.setObjectName("count_lbl")
        count_row.addWidget(self._count_lbl)
        rl.addLayout(count_row)
        self._tree=QTreeWidget(); self._tree.setColumnCount(3)
        self._tree.setAlternatingRowColors(True)
        self._tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self._tree.setRootIsDecorated(False); self._tree.setUniformRowHeights(True)
        self._tree.setHeaderLabels([_t("tag_col_folder"),_t("tag_col_orig"),_t("tag_col_new")])
        hv=self._tree.header()
        hv.setSectionResizeMode(0,QHeaderView.Interactive)
        hv.setSectionResizeMode(1,QHeaderView.Stretch)
        hv.setSectionResizeMode(2,QHeaderView.Stretch)
        self._tree.setColumnWidth(0,140)
        rl.addWidget(self._tree,1)

        # preview / apply buttons
        br=QHBoxLayout(); br.setSpacing(10)
        self._btn_preview=QPushButton(_t("btn_preview")); self._btn_preview.setObjectName("btn_preview")
        self._btn_preview.setObjectName("btn_preview")
        self._btn_preview.setIcon(_svg_icon_dual('magnifier', ACCENT, 'white')); self._btn_preview.setIconSize(QSize(20,20))
        self._btn_preview.setFixedHeight(48)
        self._btn_preview.clicked.connect(self._preview)
        self._btn_apply=QPushButton(_t("tag_btn_apply_rm")); self._btn_apply.setObjectName("btn_rename")
        self._btn_apply.setObjectName("btn_rename")
        self._btn_apply.setIcon(_svg_icon('wrench', 'white')); self._btn_apply.setIconSize(QSize(20,20))
        self._btn_apply.setFixedHeight(48)
        self._btn_apply.setEnabled(False)
        self._btn_apply.clicked.connect(self._apply)
        self._btn_undo=QPushButton(_t('btn_undo')); self._btn_undo.setObjectName("btn_undo")
        self._btn_undo.setFixedHeight(48); self._btn_undo.setEnabled(False)
        self._btn_undo.clicked.connect(self._undo)
        br.addWidget(self._btn_preview, 1); br.addWidget(self._btn_apply, 1); br.addWidget(self._btn_undo, 1)
        rl.addLayout(br)

        self._status_lbl=QLabel(_t("tag_status_start"))
        self._status_lbl.setStyleSheet("font-size:13px;")
        self._status_lbl.setWordWrap(True)
        rl.addWidget(self._status_lbl)

        body_lay.addWidget(right, stretch=3)
        root.addWidget(body,1)


    def _make_remove_panel(self):
        frame=QFrame(); frame.setObjectName("tag_opt_frame")
        frame.setStyleSheet(f"QFrame#tag_opt_frame{{background:{SRF2};border:1px solid {BORDER};border-radius:8px;}}")
        fl=QVBoxLayout(frame); fl.setContentsMargins(12,10,12,10); fl.setSpacing(8)
        # tag input field
        r0=QHBoxLayout(); r0.setSpacing(8)
        self._lbl_rm_tag=QLabel(_t('tag_rm_tag')); self._lbl_rm_tag.setObjectName("count_lbl"); self._lbl_rm_tag.setFixedWidth(80)
        self._rm_tag_edit=QLineEdit(); self._rm_tag_edit.setPlaceholderText(_t('tag_rm_tag_ph'))
        r0.addWidget(self._lbl_rm_tag); r0.addWidget(self._rm_tag_edit,1); fl.addLayout(r0)
        # separator
        div=QFrame(); div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"background:{BORDER};max-height:1px;border:none;"); fl.addWidget(div)
        # removal position
        r1=QHBoxLayout(); r1.setSpacing(12)
        self._lbl_rm_pos=QLabel(_t("tag_rm_pos")); self._lbl_rm_pos.setStyleSheet(f"font-size:13px;color:{MUTED};"); r1.addWidget(self._lbl_rm_pos)
        self._rm_group=QButtonGroup(self); self._rb_rm={}
        for val,key in [("front","tag_rm_front"),("back","tag_rm_back"),("both","tag_rm_both")]:
            rb=QRadioButton(_t(key)); rb.setChecked(val=="front"); self._rm_group.addButton(rb); self._rb_rm[val]=rb; r1.addWidget(rb)
        r1.addStretch(); fl.addLayout(r1)
        return frame

    def _make_add_panel(self):
        frame=QFrame(); frame.setObjectName("tag_opt_frame")
        frame.setStyleSheet(f"QFrame#tag_opt_frame{{background:{SRF2};border:1px solid {BORDER};border-radius:8px;}}")
        fl=QVBoxLayout(frame); fl.setContentsMargins(12,10,12,10); fl.setSpacing(6)
        # tag format
        r1=QHBoxLayout(); r1.setSpacing(8)
        self._lbl_fmt=QLabel(_t("tag_add_fmt")); self._lbl_fmt.setObjectName("count_lbl"); self._lbl_fmt.setFixedWidth(80)
        self._fmt_edit=QLineEdit("[{tag}]")
        r1.addWidget(self._lbl_fmt); r1.addWidget(self._fmt_edit,1); fl.addLayout(r1)
        fmt_hint=QLabel(_t("tag_add_fmt_hint")); self._fmt_hint=fmt_hint
        fmt_hint.setStyleSheet(f"color:{MUTED};font-size:12px;padding-left:88px;background:transparent;border:none;")
        fl.addWidget(fmt_hint)
        # tag to add
        r2=QHBoxLayout(); r2.setSpacing(8)
        self._lbl_tagval=QLabel(_t("tag_add_val")); self._lbl_tagval.setObjectName("count_lbl"); self._lbl_tagval.setFixedWidth(80)
        self._tagval_edit=QLineEdit(); self._tagval_edit.setPlaceholderText(_t("tag_add_val_ph")); r2.addWidget(self._lbl_tagval); r2.addWidget(self._tagval_edit,1); fl.addLayout(r2)
        # tag position
        r3=QHBoxLayout(); r3.setSpacing(10)
        self._lbl_pos=QLabel(_t("tag_add_pos")); self._lbl_pos.setObjectName("count_lbl"); self._lbl_pos.setFixedWidth(80)
        self._add_pos_group=QButtonGroup(self)
        self._rb_front=QRadioButton(_t("tag_add_front")); self._rb_front.setChecked(True)
        self._rb_back=QRadioButton(_t("tag_add_back"))
        self._add_pos_group.addButton(self._rb_front); self._add_pos_group.addButton(self._rb_back)
        r3.addWidget(self._lbl_pos); r3.addWidget(self._rb_front); r3.addWidget(self._rb_back); r3.addStretch(); fl.addLayout(r3)
        # separator — visually splits the tag-position (radio) group from the options (checkbox) group
        div_line=QFrame(); div_line.setFrameShape(QFrame.HLine)
        div_line.setStyleSheet(f"background:{BORDER};max-height:1px;border:none;margin-left:0px;margin-right:0px;")
        fl.addWidget(div_line)
        # checkbox row 1 — position options
        r3b=QHBoxLayout(); r3b.setSpacing(10)
        self._cb_skip=QCheckBox(_t("tag_add_skip")); self._cb_replace=QCheckBox(_t("tag_add_replace"))
        r3b.addSpacing(88); r3b.addWidget(self._cb_skip); r3b.addWidget(self._cb_replace); r3b.addStretch(); fl.addLayout(r3b)
        # checkbox row 2 — whitespace options
        r4=QHBoxLayout(); r4.setSpacing(10)
        self._cb_space_after=QCheckBox(_t("tag_add_space_after")); self._cb_space_after.setChecked(True)
        self._cb_space_before=QCheckBox(_t("tag_add_space_before")); self._cb_space_before.setChecked(True)
        r4.addSpacing(88); r4.addWidget(self._cb_space_after); r4.addWidget(self._cb_space_before); r4.addStretch(); fl.addLayout(r4)
        return frame

    def _update_tab_style(self):
        for mode,btn in self._tab_btns.items():
            active=(mode==self._mode)
            btn.setStyleSheet(f"QPushButton{{background:{_accent_alpha(0.12) if active else 'transparent'};border:none;border-bottom:2px solid {ACCENT if active else 'transparent'};border-radius:0;padding:8px 16px;color:{ACCENT if active else MUTED};font-size:13px;font-weight:{'600' if active else '500'};min-width:90px;}}")  

    def _switch_mode(self,mode):
        if mode==self._mode: return
        self._mode=mode; self._update_tab_style(); self._apply_mode_ui()

    def _apply_mode_ui(self):
        # show/hide + setMaximumHeight fully removes layout space too
        if self._mode == "remove":
            self._remove_panel.setMaximumHeight(16777215)
            self._remove_panel.show()
            self._add_panel.setMaximumHeight(0)
            self._add_panel.hide()
            self._btn_apply.setText(_t("tag_btn_apply_rm"))
            if self._allext_saved is not None:
                self._cb_allext.setChecked(self._allext_saved); self._allext_saved = None
        elif self._mode == "add":
            self._remove_panel.setMaximumHeight(0)
            self._remove_panel.hide()
            self._add_panel.setMaximumHeight(16777215)
            self._add_panel.show()
            self._btn_apply.setText(_t("tag_btn_apply_add"))
            if self._allext_saved is not None:
                self._cb_allext.setChecked(self._allext_saved); self._allext_saved = None
        else:  # depad
            self._remove_panel.setMaximumHeight(0)
            self._remove_panel.hide()
            self._add_panel.setMaximumHeight(0)
            self._add_panel.hide()
            self._btn_apply.setText(_t('tag_btn_apply_depad'))
            if self._allext_saved is None:
                self._allext_saved = self._cb_allext.isChecked()
            self._cb_allext.setChecked(True)
        self._targets = []; self._file_paths = []; self._file_paths_set = set()
        self._file_list.clear(); self._file_count_lbl.setText("")
        self._tree.clear(); self._count_lbl.setText("")
        self._btn_apply.setEnabled(False)
        self._status_lbl.setText(_t('tag_status_start'))

    def _on_folder_dropped(self,folder): self._add_files_from_folder(folder)
    def _on_files_dropped(self,file_paths):
        exts=self._get_extensions(); exts_lower={e.lower() for e in exts}
        for path in file_paths:
            ext=Path(path).suffix.lstrip(".").lower()
            if exts_lower and ext not in exts_lower: continue
            dp=str(Path(path).parent); fn=Path(path).name; key=(dp,fn)
            if key not in self._file_paths_set: self._file_paths.append(key); self._file_paths_set.add(key)
        self._refresh_file_list()

    def _add_files_from_folder(self, folder):
        exts = self._get_extensions()
        recursive = self._cb_recursive.isChecked()
        if self._scan_worker and self._scan_worker.isRunning():
            try:
                self._scan_worker.sig_progress.disconnect()
                self._scan_worker.sig_found.disconnect()
                self._scan_worker.sig_done.disconnect()
                self._scan_worker.sig_error.disconnect()
            except Exception: pass
            self._scan_worker.abort(); self._scan_worker.wait(1000)
        self._set_scan_ui(True)
        self._scan_worker = FolderScanWorker(
            folder,
            exts=set(f'.{e}' for e in exts) if exts else None,
            recursive=recursive)
        self._scan_worker.sig_progress.connect(self._scan_bar.setValue)
        self._scan_worker.sig_found.connect(
            lambda n: self._scan_lbl.setText(_t('bulk_scanning', n=n)))
        self._scan_worker.sig_done.connect(self._on_scan_done)
        self._scan_worker.sig_error.connect(self._on_scan_error)
        self._scan_worker.start()

    def _set_scan_ui(self, scanning: bool):
        self._scan_bar.setVisible(scanning)
        self._scan_bar.setValue(0)
        self._scan_lbl.setVisible(scanning)
        if not scanning: self._scan_lbl.setText("")
        for btn in (self._btn_add_files, self._btn_add_folder,
                    self._btn_del_all, self._btn_del_sel,
                    self._btn_preview, self._btn_apply):
            btn.setEnabled(not scanning)
        if scanning:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        else:
            QApplication.restoreOverrideCursor()

    def _on_scan_done(self, paths: list):
        self._set_scan_ui(False)
        if not paths:
            _dlg_warn(self, _t('dlg_ok'), _t('merge_no_support')); return
        for path in paths:
            dp = str(Path(path).parent); fn = Path(path).name
            key = (dp, fn)
            if key not in self._file_paths_set:
                self._file_paths.append(key); self._file_paths_set.add(key)
        self._refresh_file_list()

    def _on_scan_error(self, msg: str):
        self._set_scan_ui(False)
        _dlg_error(self, _t('dlg_error_title'), msg)

    def is_busy(self) -> bool:
        """Whether the folder-scan worker is running — used for shutdown confirmation."""
        return bool(self._scan_worker and self._scan_worker.isRunning())

    def _stop_worker(self):
        """Clean up the scan worker on app exit."""
        if self._scan_worker and self._scan_worker.isRunning():
            self._scan_worker.abort(); self._scan_worker.wait(1000)
            self._set_scan_ui(False)

    def _add_files_dialog(self):
        paths,_=QFileDialog.getOpenFileNames(self,_t('btn_add_file'),"","All Files (*.*)")
        if paths: self._on_files_dropped(paths)
    def _add_folder_dialog(self):
        folder=QFileDialog.getExistingDirectory(self,_t('btn_add_folder'))
        if folder: self._add_files_from_folder(folder)
    def _del_selected_files(self):
        for item in reversed(self._file_list.selectedItems()):
            idx=self._file_list.indexOfTopLevelItem(item)
            if 0<=idx<len(self._file_paths):
                key=self._file_paths.pop(idx); self._file_paths_set.discard(key); self._file_list.takeTopLevelItem(idx)
        self._update_file_count(); self._targets=[]; self._tree.clear(); self._count_lbl.setText(""); self._btn_apply.setEnabled(False)
    def _del_all_files(self):
        self._file_paths.clear(); self._file_paths_set.clear(); self._file_list.clear()
        self._update_file_count(); self._tree.clear(); self._count_lbl.setText(""); self._btn_apply.setEnabled(False)
        self._status_lbl.setText(_t('tag_status_start'))
    def _refresh_file_list(self):
        self._file_list.setUpdatesEnabled(False)
        self._file_list.clear()
        for dp, fn in self._file_paths:
            item = QTreeWidgetItem([fn, dp])
            self._file_list.addTopLevelItem(item)
        self._file_list.setUpdatesEnabled(True)
        self._update_file_count()
    def _update_file_count(self):
        n=len(self._file_paths); self._file_count_lbl.setText(_t('tag_file_count', n=n) if n else "")
    def _get_extensions(self):
        if self._cb_allext.isChecked(): return []
        return [e.strip() for e in self._ext_edit.text().split(",") if e.strip()]

    def _preview(self):
        if not self._file_paths: _dlg_warn(self, _t('dlg_warning'), _t('tag_no_files_msg')); return
        self._targets=[]; skip_info=[]  # skip_info: [(source_filename, destination_filename, reason)]

        source_full = {os.path.join(dp, fn) for dp, fn in self._file_paths}

        if self._mode=="remove":
            pos=next((v for v,rb in self._rb_rm.items() if rb.isChecked()),"front")
            target_tag=self._rm_tag_edit.text().strip()
            _glog(f"🔍 tag-remove preview — tag: {'['+target_tag+']' if target_tag else 'all'}, position: {pos}, targets: {len(self._file_paths)}")
            seen=set()
            for dp,fn in self._file_paths:
                nn=remove_tag_from_name(fn,pos,target_tag if target_tag else None)
                if nn and nn!=fn:
                    dk=(dp,nn); pp=os.path.join(dp,nn)
                    if dk in seen:
                        skip_info.append((fn, nn, _t('rename_skip_dup_in_batch')))
                        _glog(f"  ⚠ skipped: {fn} → {nn}  (duplicate within batch)")
                        continue
                    if os.path.exists(pp) and pp not in source_full:
                        skip_info.append((fn, nn, _t('rename_skip_dest_exists')))
                        _glog(f"  ⚠ skipped: {fn} → {nn}  (destination '{nn}' already exists)")
                        continue
                    seen.add(dk); self._targets.append((dp,fn,nn))
                    _glog(f"  ✅ {fn}  →  {nn}")
            sk="status_found"
        elif self._mode=="add":
            raw=self._tagval_edit.text().strip()
            if not raw: _dlg_warn(self, _t('dlg_warning'), _t('tag_no_tag_msg')); return
            tags=[v.strip() for v in raw.split(",") if v.strip()]; pos="front" if self._rb_front.isChecked() else "back"
            _glog(f"🔍 tag-add preview — tags: {tags}, position: {pos}, targets: {len(self._file_paths)}")
            seen=set()
            for dp,fn in self._file_paths:
                nn=add_tag_to_name(fn,tags,self._fmt_edit.text() or "[{tag}]",pos,self._cb_skip.isChecked(),self._cb_replace.isChecked(),space_after=self._cb_space_after.isChecked(),space_before=self._cb_space_before.isChecked())
                if nn:
                    dk=(dp,nn); pp=os.path.join(dp,nn)
                    if dk in seen:
                        skip_info.append((fn, nn, _t('rename_skip_dup_in_batch')))
                        _glog(f"  ⚠ skipped: {fn} → {nn}  (duplicate within batch)")
                        continue
                    if os.path.exists(pp) and pp not in source_full:
                        skip_info.append((fn, nn, _t('rename_skip_dest_exists')))
                        _glog(f"  ⚠ skipped: {fn} → {nn}  (destination '{nn}' already exists)")
                        continue
                    seen.add(dk); self._targets.append((dp,fn,nn))
                    _glog(f"  ✅ {fn}  →  {nn}")
            sk="status_found_add"
        else:
            _glog(f"🔍 zero-padding-strip preview — targets: {len(self._file_paths)}")
            seen=set()
            for dp,fn in self._file_paths:
                nn=depad_name(fn)
                if nn:
                    dk=(dp,nn); pp=os.path.join(dp,nn)
                    if dk in seen:
                        skip_info.append((fn, nn, _t('rename_skip_dup_in_batch')))
                        _glog(f"  ⚠ skipped: {fn} → {nn}  (duplicate within batch)")
                        continue
                    if os.path.exists(pp) and pp not in source_full:
                        skip_info.append((fn, nn, _t('rename_skip_dest_exists')))
                        _glog(f"  ⚠ skipped: {fn} → {nn}  (destination '{nn}' already exists)")
                        continue
                    seen.add(dk); self._targets.append((dp,fn,nn))
                    _glog(f"  ✅ {fn}  →  {nn}")
            sk="status_found_depad"

        self._tree.clear()
        for dp,on,nn in self._targets:
            item=QTreeWidgetItem([dp,on,nn]); item.setForeground(2,QColor(ACCENT)); self._tree.addTopLevelItem(item)
        cnt=len(self._targets); skip=len(skip_info)
        self._count_lbl.setText(_t('tag_count_total', n=cnt) if cnt else "")
        self._btn_apply.setEnabled(cnt>0)
        labels={
            "status_found":       _t('tag_status_found', n=cnt),
            "status_found_add":   _t('tag_status_found_add', n=cnt),
            "status_found_depad": _t('tag_status_found_depad', n=cnt),
        }
        msg=labels.get(sk, str(cnt)) if cnt else _t('tag_no_change')
        if skip > 0:
            # show only the first case per reason as a sample
            parts = []
            for fn, nn, reason in skip_info[:3]:
                parts.append(f"'{nn}' — {reason}")
            if skip > 3: parts.append(f"+{skip-3} more")
            msg += f"  ({_t('tag_skip_count', n=skip)}: {' / '.join(parts)})"
        _glog(f"  → processed {cnt}, skipped {skip}")
        self._status_lbl.setText(msg)

    def _apply(self):
        if not self._targets: return
        labels={"add":_t('tag_sub_add'),"depad":_t('tag_sub_depad')}
        label=labels.get(self._mode, _t('tag_sub_remove'))
        if not _dlg_question(self, _t('dlg_confirm_title'), _t('tag_apply_confirm', n=len(self._targets))): return
        _glog(f"▶ running {label} — {len(self._targets)} item(s)")
        undo_map=[(os.path.join(dp,new), os.path.join(dp,old)) for dp,old,new in self._targets]
        success,errors=apply_renames(self._targets)
        msg=_t('tag_apply_done', n=success, label=label)
        for dp,old,new in self._targets:
            _glog(f"  ✅ {old}  →  {new}")
        if errors:
            for e in errors: _glog(f"  ❌ {e}")
            _dlg_warn(self, _t('dlg_done_err'), msg+"\n\n"+"\n".join(errors[:10]))
        else: _dlg_info(self, _t('dlg_done'), msg)
        _glog(f"  Done: {success} succeeded, {len(errors)} failed")
        if success > 0:
            self._undo_data = undo_map[:success]
            self._btn_undo.setEnabled(True)
        self._status_lbl.setText(msg); self._targets=[]
        self._file_paths=[]; self._file_paths_set=set(); self._file_list.clear(); self._file_count_lbl.setText("")
        self._tree.clear(); self._count_lbl.setText(""); self._btn_apply.setEnabled(False)

    def _refresh_tree_styles(self):
        """Inject TreeWidget header colors directly on theme switch."""
        ss = (
            f"QTreeWidget{{"
            f"background:{_T['SURFACE']};border:1px solid {_T['BORDER']};border-radius:8px;"
            f"color:{_T['TEXT']};font-size:13px;outline:none;"
            f"alternate-background-color:{_T['SRF2']};}}"
            f"QTreeWidget::item{{padding:4px 6px;}}"
            f"QTreeWidget::item:selected{{background:{_accent_alpha(0.12)};color:{_T['TEXT']};}}"
            f"QHeaderView::section{{"
            f"background:{_T['SRF2']};border:none;"
            f"border-bottom:1px solid {_T['BORDER']};border-right:1px solid {_T['BORDER']};"
            f"color:{_T['MUTED']};font-size:11px;font-weight:600;"
            f"letter-spacing:0.5px;padding:7px 10px;}}"
            f"QHeaderView::section:first{{border-top-left-radius:7px;}}"
            f"QHeaderView::section:last{{border-top-right-radius:7px;border-right:none;}}"
        )
        self._file_list.setStyleSheet(ss)
        self._tree.setStyleSheet(ss)


    def _undo(self):
        """Restore the last Tag Editor operation once."""
        if not self._undo_data: return
        errors=[]; done=0
        _glog(f"↩ [Tag Editor] Undo — {len(self._undo_data)} items")
        for cur, orig in self._undo_data:
            try:
                if os.path.exists(cur):
                    os.rename(cur, orig); done+=1
                    _glog(f"  ✅ {os.path.basename(cur)}  →  {os.path.basename(orig)}")
                else:
                    errors.append(f"{os.path.basename(cur)}: file not found")
            except OSError as e:
                errors.append(f"{os.path.basename(cur)}: {e}")
        self._undo_data = None
        if hasattr(self, '_btn_undo'): self._btn_undo.setEnabled(False)
        msg = _t('tag_apply_done', n=done, label=_t('dlg_undo'))
        if errors: msg += f'  {_t("dlg_done_err")} ×{len(errors)}'
        _glog(f"  Done: {msg}")
        if errors: _dlg_warn(self, _t('dlg_undo'), msg + "\n\n" + "\n".join(errors[:10]))
        else: _dlg_info(self, _t('dlg_undo'), msg)

    def refresh_btn_styles(self):
        """Refresh buttons that the QSS cascade does not reach on theme switch."""
        secondary_ss = (f"QPushButton{{background:{SURFACE};border:1.5px solid {BTN_BORDER_H};"
                        f"color:{TEXT};border-radius:8px;padding:5px 12px;}}"
                        f"QPushButton:hover{{background:{SRF2};border-color:{ACCENT};}}"
                        f"QPushButton:pressed{{background:{BTN_PRESSED};}}"
                        f"QPushButton:disabled{{background:{SRF2};color:{DISABLED};}}")
        primary_ss = (f"QPushButton{{background:{ACCENT};border:none;color:white;"
                      f"padding:9px 16px;font-weight:600;border-radius:8px;}}"
                      f"QPushButton:hover{{background:{ACCENT_HOVER};}}"
                      f"QPushButton:disabled{{background:{DISABLED};color:rgba(255,255,255,0.5);}}")
        for attr in ('_btn_add_files', '_btn_add_folder'):
            if hasattr(self, attr): getattr(self, attr).setStyleSheet(primary_ss)
        for attr in ('_btn_del_all', '_btn_del_sel'):
            if hasattr(self, attr): getattr(self, attr).setStyleSheet(secondary_ss)
        if hasattr(self, '_btn_undo'): self._btn_undo.setStyleSheet(secondary_ss)
        # Refresh SVG icon colors
        _isz = QSize(20,20)
        for attr, key in [('_btn_del_all','trash'),('_btn_del_sel','trash')]:
            if hasattr(self, attr): getattr(self, attr).setIcon(_svg_icon(key, ACCENT)); getattr(self, attr).setIconSize(_isz)
        if hasattr(self, '_btn_preview'):
            self._btn_preview.setIcon(_svg_icon_dual('magnifier', ACCENT, 'white')); self._btn_preview.setIconSize(_isz)

    def retranslate(self):
        for mk, lbl in [("remove", _t('tag_sub_remove')),
                        ("add",    _t('tag_sub_add')),
                        ("depad",  _t('tag_sub_depad'))]:
            if mk in self._tab_btns: self._tab_btns[mk].setText(lbl)
        self._btn_add_files.setText(_t('btn_add_file'))
        self._btn_add_folder.setText(_t('btn_add_folder'))
        self._btn_del_all.setText(_t('btn_del_all'))
        self._btn_del_sel.setText(_t('btn_del_sel'))
        self._file_list.setHeaderLabels([_t('tag_col_filename'), _t('tag_col_path')])
        self._ext_gb.setTitle(_t('tag_filter'))
        self._lbl_ext.setText(_t('tag_ext_label'))
        self._lbl_ext_hint.setText(_t('tag_ext_hint'))
        self._cb_recursive.setText(_t('tag_cb_recursive'))
        self._cb_allext.setText(_t('tag_cb_allext'))
        self._lbl_rm_pos.setText(_t('tag_rm_pos'))
        if hasattr(self, '_lbl_rm_tag'): self._lbl_rm_tag.setText(_t('tag_rm_tag'))
        if hasattr(self, '_rm_tag_edit'): self._rm_tag_edit.setPlaceholderText(_t('tag_rm_tag_ph'))
        for val, key in [('front','tag_rm_front'),('back','tag_rm_back'),('both','tag_rm_both')]:
            if val in self._rb_rm: self._rb_rm[val].setText(_t(key))
        self._lbl_fmt.setText(_t('tag_add_fmt'))
        self._fmt_hint.setText(_t('tag_add_fmt_hint'))
        self._lbl_tagval.setText(_t('tag_add_val'))
        self._tagval_edit.setPlaceholderText(_t('tag_add_val_ph'))
        self._lbl_pos.setText(_t('tag_add_pos'))
        self._rb_front.setText(_t('tag_add_front'))
        self._rb_back.setText(_t('tag_add_back'))
        self._cb_skip.setText(_t('tag_add_skip'))
        self._cb_replace.setText(_t('tag_add_replace'))
        self._cb_space_after.setText(_t('tag_add_space_after'))
        self._cb_space_before.setText(_t('tag_add_space_before'))
        self._prev_gb_removed = True  # GroupBox removed
        self._tree.setHeaderLabels([_t('tag_col_folder'), _t('tag_col_orig'), _t('tag_col_new')])
        self._btn_preview.setText(_t('btn_preview'))
        mode_map = {'remove': _t('tag_btn_apply_rm'),
                    'add':    _t('tag_btn_apply_add'),
                    'depad':  _t('tag_btn_apply_depad')}
        self._btn_apply.setText(mode_map.get(self._mode, _t('tag_btn_apply_rm')))
        if hasattr(self,"_drop_zone"): self._drop_zone.set_idle()
        if self._status_lbl.text() in _all_translations_of('tag_status_start'):
            self._status_lbl.setText(_t('tag_status_start'))
        if hasattr(self, '_btn_undo'): self._btn_undo.setText(_t('btn_undo'))
        self._update_file_count()

    # ── Settings save / restore ─────────────────
    def get_config(self) -> dict:
        pos = next((v for v,rb in self._rb_rm.items() if rb.isChecked()), 'front')
        return {
            'mode':         self._mode,
            'rm_pos':       pos,
            'fmt':          self._fmt_edit.text(),
            'tagval':       self._tagval_edit.text(),
            'add_pos':      'front' if self._rb_front.isChecked() else 'back',
            'cb_skip':      self._cb_skip.isChecked(),
            'cb_replace':   self._cb_replace.isChecked(),
            'cb_space_after':  self._cb_space_after.isChecked(),
            'cb_space_before': self._cb_space_before.isChecked(),
            'cb_recursive': self._cb_recursive.isChecked(),
            'cb_allext':    self._cb_allext.isChecked(),
            'ext':          self._ext_edit.text(),
        }

    def apply_config(self, d: dict):
        if not d: return
        pos = d.get('rm_pos', 'front')
        if pos in self._rb_rm: self._rb_rm[pos].setChecked(True)
        self._fmt_edit.setText(d.get('fmt', '[{tag}]') or '[{tag}]')
        self._tagval_edit.setText(d.get('tagval', ''))
        if d.get('add_pos') == 'back': self._rb_back.setChecked(True)
        else: self._rb_front.setChecked(True)
        self._cb_skip.setChecked(d.get('cb_skip', False))
        self._cb_replace.setChecked(d.get('cb_replace', False))
        self._cb_space_after.setChecked(d.get('cb_space_after', True))
        self._cb_space_before.setChecked(d.get('cb_space_before', True))
        self._cb_recursive.setChecked(d.get('cb_recursive', True))
        self._cb_allext.setChecked(d.get('cb_allext', True))
        self._ext_edit.setText(d.get('ext', ''))
        mode = d.get('mode', 'remove')
        if mode in ('remove', 'add', 'depad'): self._switch_mode(mode)


# ═══════════════════════════════════════════════
# Encoding badge delegate (for Text Merger)
# ═══════════════════════════════════════════════
class MergeEncodingDelegate(QStyledItemDelegate):
    """Delegate that draws encoding color badge + confidence% on file list items."""
    _ENC_COLOR = {
        'utf-8': '#4CAF50', 'utf-8-sig': '#009688', 'ascii': '#78909C',
        'euc-kr': '#E67E22', 'cp949': '#E67E22', 'euc_kr': '#E67E22',
        'utf-16': '#3498DB', 'utf-16-le': '#3498DB', 'utf-16-be': '#3498DB',
        # v1.0.4: Added CJK encodings (matches alchemy_detect_encoding normalization)
        'shift_jis': '#E91E63', 'shift-jis': '#E91E63',
        'gbk': '#F1C40F', 'gb18030': '#F1C40F', 'gb2312': '#F1C40F',
        'big5': '#00BCD4',
        'docx': '#2980B9', 'pdf': '#E74C3C', 'xlsx': '#27AE60',
        # v1.0.6: Added HWPX (Hancom Office KS X 6101 OWPML)
        'hwpx': '#9B59B6',
    }
    _ENC_LABEL = {
        'utf-8': 'UTF-8', 'utf-8-sig': 'UTF-8 BOM', 'ascii': 'ASCII',
        'euc-kr': 'EUC-KR', 'cp949': 'CP949', 'euc_kr': 'EUC-KR',
        'utf-16': 'UTF-16', 'utf-16-le': 'UTF-16', 'utf-16-be': 'UTF-16',
        # v1.0.4: Added CJK encodings
        'shift_jis': 'Shift-JIS', 'shift-jis': 'Shift-JIS',
        'gbk': 'GBK', 'gb18030': 'GBK', 'gb2312': 'GBK',
        'big5': 'Big5',
        'docx': 'DOCX', 'pdf': 'PDF', 'xlsx': 'XLSX',
        # v1.0.6: Added HWPX
        'hwpx': 'HWPX',
    }
    _BADGE_ROLE  = Qt.ItemDataRole.UserRole + 1   # enc string
    _CONF_ROLE   = Qt.ItemDataRole.UserRole + 2   # confidence float 0-1
    _LINES_ROLE  = Qt.ItemDataRole.UserRole + 3   # line count int
    # v1.0.6: Store pure file path (avoid tooltip pollution). v1.0.4 tooltips were
    # being decorated with notes, breaking code that read toolTip(0) as the file path.
    _PATH_ROLE   = Qt.ItemDataRole.UserRole + 4   # full file path (unmodified)

    def paint(self, painter: QPainter, option, index):
        painter.save()
        # ── Background ────────────────────────────
        if option.state & QStyle.State_Selected:
            c = QColor(ACCENT); c.setAlpha(40)
            painter.fillRect(option.rect, c)
        elif option.state & QStyle.State_MouseOver:
            painter.fillRect(option.rect, QColor(_T['BTN_HOVER']))

        enc_raw = index.data(self._BADGE_ROLE) or 'utf-8'
        conf    = index.data(self._CONF_ROLE)  or 0.0
        fname   = index.data(Qt.ItemDataRole.DisplayRole)   or ''

        enc_key = enc_raw.lower()
        color   = self._ENC_COLOR.get(enc_key, '#9B59B6')
        label   = self._ENC_LABEL.get(enc_key, enc_raw.upper()[:9])
        is_bin  = enc_key in ('docx', 'pdf', 'xlsx', 'hwpx')

        r      = option.rect
        pad    = 10
        badge_w = 72
        badge_h = 20

        # ── Badge first (right-anchored) ──────────
        badge_rect = QRect(r.right() - badge_w - pad,
                           r.top() + (r.height() - badge_h) // 2,
                           badge_w, badge_h)
        painter.setRenderHint(QPainter.Antialiasing)
        fill = QColor(color); fill.setAlpha(55)          # ← 28→55 (more saturated)
        painter.setBrush(QBrush(fill))
        painter.setPen(QPen(QColor(color), 1.5))         # ← 1.5px border
        painter.drawRoundedRect(badge_rect, 10, 10)

        bl_font = QFont(painter.font())
        bl_font.setPointSize(8); bl_font.setBold(True)
        painter.setFont(bl_font)
        painter.setPen(QColor(color))
        painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, label)

        # ── Confidence % ──────────────────────────
        conf_w = 38
        if conf > 0.0 and not is_bin:
            conf_rect = QRect(r.right() - badge_w - conf_w - pad - 4,
                              r.top(), conf_w, r.height())
            cf_font = QFont(painter.font())
            cf_font.setPointSize(8); cf_font.setBold(False)
            painter.setFont(cf_font)
            # v1.0.4: 4-tier confidence color coding (chardet raw value basis)
            if   conf >= 0.90: conf_color = '#4CAF50'   # green — safe
            elif conf >= 0.70: conf_color = '#F1C40F'   # yellow — caution
            elif conf >= 0.50: conf_color = '#E67E22'   # orange — warning (CJK threshold = alchemy 0.5)
            else:              conf_color = '#E74C3C'   # red — danger
            painter.setPen(QColor(conf_color))
            painter.drawText(conf_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                             f"{conf * 100:.0f}%")

        # ── File name (2 lines: name + extension) ─
        right_edge = r.right() - badge_w - conf_w - pad * 3 - 4
        fn_rect = QRect(r.left() + pad, r.top(), right_edge - r.left() - pad, r.height())

        base  = os.path.splitext(fname)[0]
        ext   = os.path.splitext(fname)[1]   # e.g. ".txt"

        # Name (bold)
        name_font = QFont(painter.font())
        name_font.setPointSize(9); name_font.setBold(False)
        painter.setFont(name_font)
        painter.setPen(QColor(_T['TEXT']))
        fm = painter.fontMetrics()
        elided = fm.elidedText(base, Qt.TextElideMode.ElideMiddle, fn_rect.width() - (fm.horizontalAdvance(ext) + 4))
        full_text = elided + ext

        painter.drawText(fn_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, full_text)

        painter.restore()

    def sizeHint(self, option, index):
        return QSize(option.rect.width(), 36)          # ← 30→36


# ═══════════════════════════════════════════════
# Tab 4: Text Merger panel
# ═══════════════════════════════════════════════

# ═══════════════════════════════════════════════
# Tab 5: Text Fixer panel
# ═══════════════════════════════════════════════


class TextFixerEdit(QPlainTextEdit):
    """Direct text input editor. QPlainTextEdit-based — no large-document rendering limits.
    File drag-and-drop is blocked to prevent file names from being inserted as text."""

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.ignore()   # Ignore file drop → handled only by the dropzone above
        else:
            super().dragEnterEvent(e)

    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls():
            e.ignore()
        else:
            super().dragMoveEvent(e)

    def dropEvent(self, e):
        if e.mimeData().hasUrls():
            e.ignore()   # Ignore file drop
        else:
            super().dropEvent(e)


class TextFixerOutputEdit(QPlainTextEdit):
    """Output editor for the corrected text. QPlainTextEdit-based — no large-document rendering limits."""

    def __init__(self, parent=None):
        super().__init__(parent)

    def lock_scroll(self): pass
    def unlock_scroll(self): pass

class TextFixerDropZone(QLabel):
    """Drag-and-drop zone for TXT files only — BatchDropZone style."""
    file_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tfDropZone")
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumHeight(110)
        self.setTextFormat(Qt.TextFormat.RichText)
        self.set_idle()

    def set_idle(self):
        t = _T
        self.setStyleSheet(
            f"QLabel#tfDropZone{{border:1.5px dashed {t['BORDER']};"
            f"border-radius:10px;background:{t['SURFACE']};padding:14px;"
            f"color:{t['TEXT']};}}")
        self.setText(
            f"<div style='text-align:center;'>"
            f"<div style='font-size:28px;line-height:1;font-family:{_EMOJI_FONT_FAMILY};'>📄</div>"
            f"<div style='color:{t['MUTED']};font-size:13px;margin-top:8px;'>"
            f"{_t('tf_drop1')}</div>"
            f"<div style='color:{t['DISABLED']};font-size:13px;margin-top:4px;'>"
            f"{_t('tf_drop2')}</div>"
            f"</div>")

    def set_hover(self):
        t = _T
        self.setStyleSheet(
            f"QLabel#tfDropZone{{border:2px dashed {t['ACCENT']};"
            f"border-radius:10px;background:{_accent_alpha(0.07)};padding:14px;}}")
        self.setText(
            f"<div style='text-align:center;'>"
            f"<div style='font-size:28px;line-height:1;font-family:{_EMOJI_FONT_FAMILY};'>📄</div>"
            f"<div style='color:{t['ACCENT']};font-size:13px;margin-top:8px;'>"
            f"{_t('tf_drop_hover')}</div>"
            f"</div>")

    def refresh_style(self):
        self.set_idle()

    def _has_valid_txt(self, mime):
        return mime.hasUrls() and any(
            u.isLocalFile() and u.toLocalFile().lower().endswith('.txt')
            for u in mime.urls()
        )

    def mousePressEvent(self, e):
        """Open file dialog on click."""
        if e.button() != Qt.MouseButton.LeftButton: return
        path, _ = QFileDialog.getOpenFileName(
            None, _t('tf_open'), '', 'Text Files (*.txt);;All Files (*)')
        if path: self.file_dropped.emit(path)

    def dragEnterEvent(self, e):
        if self._has_valid_txt(e.mimeData()):
            self.set_hover(); e.acceptProposedAction()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if self._has_valid_txt(e.mimeData()): e.acceptProposedAction()
        else: e.ignore()

    def dragLeaveEvent(self, e):
        self.set_idle()

    def dropEvent(self, e):
        self.set_idle()
        for url in e.mimeData().urls():
            if url.isLocalFile():
                path = url.toLocalFile()
                if path.lower().endswith('.txt'):
                    self.file_dropped.emit(path)
                    e.acceptProposedAction()
                    return
        e.ignore()


class TextFixerWorker(QThread):
    """Background worker for line-break correction — same logic as FixWorker."""
    done     = Signal(str, int, int, int, int)
    error    = Signal(str)
    progress = Signal(int)   # 0–100

    def __init__(self, text, do_mid, do_blank, max_blank, do_sep=False,
                 do_auto_split=False, max_split_chars=100, lang_mode='auto'):
        super().__init__()
        self.text = text; self.do_mid = do_mid
        self.do_blank = do_blank; self.max_blank = max_blank
        self.do_sep = do_sep
        self.do_auto_split = do_auto_split
        self.max_split_chars = max_split_chars
        self.lang_mode = lang_mode  # 'auto' | 'ko' | 'en'

    # Sentence-end characters — lines ending with these are not merged with the next line
    _SENT_END = frozenset('.!?…。！？‥\u201c\u201d\u2018\u2019」』）)}>]"\'')
    # Sentence boundary pattern — for automatic paragraph splitting
    _BOUNDARY_PAT = re.compile(r'[\.!?…]["\u201d\u2019\u300d\u300f]?(?=\s|$)')
    # Divider characters — lines made entirely of these are not merged
    _SEP_CHARS = frozenset('-=*_~─━═·•▶★☆…▪▸►◆■□▲△')

    # English abbreviations — a trailing "." after these is not treated as a sentence end
    _EN_ABBR = frozenset([
        'mr','mrs','ms','dr','prof','sr','jr','vs','etc','i.e','e.g',
        'no','vol','ch','st','ave','blvd','dept','approx','corp','inc',
        'ltd','fig','pp','ed','eds','jan','feb','mar','apr','jun','jul',
        'aug','sep','oct','nov','dec','govt','univ','assoc','est',
    ])
    # English-mode auto-detection — switch to English mode when CJK char ratio is low
    _CJK_RANGE = re.compile(r'[\u1100-\u11FF\uAC00-\uD7A3\u3040-\u30FF\u4E00-\u9FFF]')

    @staticmethod
    def _detect_lang(text: str) -> str:
        """Auto-detect language mode from CJK character ratio in text."""
        sample = text[:3000]
        total = len(sample.replace(' ', '').replace('\n', ''))
        if total == 0: return 'ko'
        cjk = len(TextFixerWorker._CJK_RANGE.findall(sample))
        return 'ko' if cjk / total > 0.1 else 'en'

    @staticmethod
    def _is_en_abbr(line: str) -> bool:
        """Check whether the line's last word is an English abbreviation."""
        word = re.sub(r'[^a-zA-Z.]', '', line.rstrip().split()[-1]).lower() if line.strip() else ''
        return word.rstrip('.') in TextFixerWorker._EN_ABBR or (len(word) == 2 and word[1] == '.')

    @staticmethod
    def _merge_en(prev: str, nxt: str) -> str:
        """English-mode merge — restore words split by hyphens."""
        p = prev.rstrip()
        n = nxt.lstrip()
        if p.endswith('-') and n and n[0].islower():
            return p[:-1] + n   # Remove hyphen, then directly concatenate
        return p + ' ' + n

    @staticmethod
    def _split_long_line(line, max_chars):
        """Split long lines on sentence boundaries.
        Step 1: split at every sentence boundary
        Step 2: re-merge short consecutive sentences within max_chars
        """
        if len(line) <= max_chars:
            return [line]
        # Step 1 — split at every boundary
        all_segs = []; start = 0
        for m in TextFixerWorker._BOUNDARY_PAT.finditer(line):
            end = m.end()
            seg = line[start:end].strip()
            if seg: all_segs.append(seg)
            skip = end
            while skip < len(line) and line[skip] == ' ': skip += 1
            start = skip
        if start < len(line):
            rem = line[start:].strip()
            if rem: all_segs.append(rem)
        if not all_segs:
            return [line]
        # Step 2 — group by accumulated length
        groups = []; cur = []; cur_len = 0
        for seg in all_segs:
            if cur and cur_len + len(seg) > max_chars:
                groups.append(' '.join(cur))
                cur = [seg]; cur_len = len(seg)
            else:
                cur.append(seg); cur_len += len(seg)
        if cur: groups.append(' '.join(cur))
        return groups if groups else [line]

    @staticmethod
    def _is_sep_line(line: str) -> bool:
        """Return whether the line is a divider (made of repeated symbols only)."""
        s = line.strip()
        return (len(s) >= 3
                and all(c in TextFixerWorker._SEP_CHARS or c == ' ' for c in s)
                and any(c in TextFixerWorker._SEP_CHARS for c in s))

    def run(self):
        _prevent_sleep()
        try:
            lines = self.text.split('\n')
            orig_lines = len(lines)
            fixed_mid = 0; fixed_blank = 0

            # Determine language mode
            use_lang = self.lang_mode
            if use_lang == 'auto':
                use_lang = self._detect_lang(self.text)

            # Split paragraphs by blank lines
            paragraphs = []; current = []
            total_lines = max(len(lines), 1)
            for li, line in enumerate(lines):
                if li % max(1, total_lines // 20) == 0:
                    self.progress.emit(int(li / total_lines * 35))
                if line.strip() == '':
                    paragraphs.append(current); paragraphs.append(None); current = []
                else:
                    current.append(line)
            paragraphs.append(current)
            self.progress.emit(40)

            result = []
            for para in paragraphs:
                if para is None: result.append(''); continue
                if not para: continue
                if self.do_mid and len(para) > 1:
                    out_lines = [para[0]]
                    for nxt in para[1:]:
                        prev = out_lines[-1]
                        prev_end = prev.rstrip()
                        last_ch = prev_end[-1] if prev_end else ''
                        is_sep = self._is_sep_line(prev) or self._is_sep_line(nxt)
                        if is_sep:
                            out_lines.append(nxt); continue
                        if use_lang == 'en':
                            # English mode — abbreviation exception + hyphen restore
                            is_abbr = (last_ch == '.' and self._is_en_abbr(prev_end))
                            is_sent_end = (last_ch in self._SENT_END and not is_abbr
                                           and not prev_end.rstrip('.').endswith('..'))
                            if is_sent_end:
                                out_lines.append(nxt)
                            else:
                                out_lines[-1] = self._merge_en(prev, nxt)
                                fixed_mid += 1
                        else:
                            # Korean / other mode — original logic
                            if (last_ch
                                    and last_ch not in self._SENT_END):
                                out_lines[-1] = prev + nxt.lstrip()
                                fixed_mid += 1
                            else:
                                out_lines.append(nxt)
                    result.extend(out_lines)
                else:
                    result.extend(para)

            self.progress.emit(60)
            # Reduce excessive blank lines
            if self.do_blank:
                collapsed = []; blank_run = 0
                for line in result:
                    if line.strip() == '':
                        blank_run += 1
                        if blank_run <= self.max_blank: collapsed.append('')
                        else: fixed_blank += 1
                    else:
                        blank_run = 0; collapsed.append(line)
                result = collapsed

            # Trim leading / trailing blank lines
            while result and result[0].strip() == '': result.pop(0)
            while result and result[-1].strip() == '': result.pop()

            # Insert blank line after each sentence
            if self.do_sep:
                sep_result = []; prev_blank = False
                for i, line in enumerate(result):
                    sep_result.append(line)
                    is_blank = not line.strip()
                    if not is_blank and not prev_blank and i < len(result) - 1:
                        nxt = result[i + 1]
                        if nxt.strip():  # Only when the next line is non-empty
                            last_ch = line.rstrip()[-1] if line.rstrip() else ''
                            nxt_first = nxt.lstrip()[0] if nxt.lstrip() else ''
                            if (last_ch in self._SENT_END
                                    or nxt_first in '"\u201c\u201d\u2018\u2019\u300c\u300e'):
                                sep_result.append('')
                    prev_blank = is_blank
                result = sep_result
                # Re-tidy leading / trailing blank lines
                while result and result[0].strip() == '': result.pop(0)
                while result and result[-1].strip() == '': result.pop()

            self.progress.emit(80)
            # Auto paragraph split (split long lines on sentence boundaries)
            if self.do_auto_split:
                expanded = []
                for line in result:
                    if not line.strip() or len(line) <= self.max_split_chars:
                        expanded.append(line)
                    else:
                        parts = self._split_long_line(line, self.max_split_chars)
                        for j, part in enumerate(parts):
                            if part: expanded.append(part)
                            if j < len(parts) - 1: expanded.append('')
                result = expanded
                while result and result[0].strip() == '': result.pop(0)
                while result and result[-1].strip() == '': result.pop()

            self.progress.emit(100)
            self.done.emit('\n'.join(result), fixed_mid, fixed_blank, orig_lines, len(result))
        except Exception as e:
            self.error.emit(str(e))
        finally:
            _allow_sleep()


class TextFixerPanel(QWidget):
    """Tab 5 — text line-break correction panel."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self._undo_data = None
        self._last_original = ''
        self._loaded_path = None   # Original path saved when loaded from a file
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)

        sep = QFrame(); sep.setFrameShape(QFrame.HLine); sep.setObjectName("tab_sep")
        root.addWidget(sep)

        body = QWidget(); bl = QVBoxLayout(body)
        bl.setContentsMargins(16, 10, 16, 10); bl.setSpacing(10)

        # ── Drop zone ─────────────────────────────────────────────────
        self._drop_zone = TextFixerDropZone()
        self._drop_zone.file_dropped.connect(self.load_file)
        bl.addWidget(self._drop_zone)

        # ── Button toolbar ────────────────────────────────────────────
        tb = QHBoxLayout(); tb.setSpacing(8)
        self._btn_open  = QPushButton(_t('tf_open'));  self._btn_open.clicked.connect(self._open_file)
        self._btn_open.setIcon(_svg_icon('folder_open', ACCENT)); self._btn_open.setIconSize(QSize(20,20))
        self._btn_run   = QPushButton(_t('tf_run'));   self._btn_run.setObjectName("btn_merge"); self._btn_run.clicked.connect(self.run_fix)
        self._btn_run.setIcon(_svg_icon('wrench', 'white')); self._btn_run.setIconSize(QSize(20,20))
        self._btn_copy  = QPushButton(_t('tf_copy'));  self._btn_copy.clicked.connect(self.copy_output); self._btn_copy.setEnabled(False)
        self._btn_copy.setIcon(_svg_icon('clipboard', ACCENT)); self._btn_copy.setIconSize(QSize(20,20))
        self._btn_save = QToolButton(); self._btn_save.setText(_t('tf_save'))
        self._btn_save.setIcon(_svg_icon('save', ACCENT)); self._btn_save.setIconSize(QSize(20,20))
        self._btn_save.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._btn_save.setEnabled(False)
        self._btn_save.setFixedHeight(36)
        self._btn_save.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        self._btn_save.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._save_menu = QMenu(self._btn_save)
        self._act_fixed   = self._save_menu.addAction(_t('tf_save_fixed'))
        self._save_menu.addSeparator()
        self._act_saveas  = self._save_menu.addAction(_t('tf_save_as'))
        self._act_fixed.triggered.connect(self._save_fixed)
        self._act_saveas.triggered.connect(self._save_as)
        self._btn_save.setMenu(self._save_menu)
        self._btn_save.clicked.connect(self._save_default)
        self._btn_clear = QPushButton(_t('tf_clear')); self._btn_clear.clicked.connect(self.clear_all)
        self._btn_clear.setIcon(_svg_icon('trash', ACCENT)); self._btn_clear.setIconSize(QSize(20,20))
        self._btn_undo  = QPushButton(_t('btn_undo')); self._btn_undo.setObjectName("btn_undo"); self._btn_undo.clicked.connect(self._undo); self._btn_undo.setEnabled(False)
        for btn in [self._btn_open, self._btn_run, self._btn_undo, self._btn_copy]:
            btn.setFixedHeight(36)
            tb.addWidget(btn)
        tb.addWidget(self._btn_save)  # QToolButton (separate)
        for btn in [self._btn_clear]:
            btn.setFixedHeight(36)
            tb.addWidget(btn)
        tb.addStretch()
        bl.addLayout(tb)

        # ── Option group ──────────────────────────────────────────────
        # ── Option bar (inline, no GroupBox) ──────────────────────────
        opt_bar = QWidget()
        opt_bar.setObjectName("tf_opt_bar")
        self._opt_bar = opt_bar
        opt_bar.setStyleSheet(
            f"QWidget#tf_opt_bar{{background:{SRF2};border:1px solid {BORDER};"
            f"border-radius:8px;}}"
            f"QWidget#tf_opt_bar QComboBox{{background:{SRF2};border-color:{BORDER};}}"
            f"QWidget#tf_opt_bar QComboBox::drop-down{{background:{BORDER};}}")
        ol = QVBoxLayout(opt_bar); ol.setContentsMargins(14, 10, 14, 10); ol.setSpacing(8)

        self._lbl_lang_mode = QLabel(_t('tf_lang_mode'))
        self._combo_lang_mode = _ThemedCombo()
        self._combo_lang_mode.addItems([_t('tf_lang_auto'), _t('tf_lang_ko'), _t('tf_lang_en')])
        self._combo_lang_mode.setFixedHeight(24)
        self._combo_lang_mode.setFixedWidth(160)
        self._combo_lang_mode.setStyleSheet(
            f"QComboBox{{background:{SRF2};border:1.5px solid {BORDER};"
            f"border-radius:8px;color:{TEXT};"
            f"padding:2px 28px 2px 8px;font-size:13px;min-height:18px;}}"
            f"QComboBox:focus{{border-color:{ACCENT};}}"
            f"QComboBox:hover{{border-color:{INPUT_H};}}"
            f"QComboBox::drop-down{{subcontrol-origin:padding;"
            f"subcontrol-position:right center;width:24px;border:none;"
            f"border-left:1.5px solid {BORDER};"
            f"border-top-right-radius:8px;border-bottom-right-radius:8px;"
            f"background:{BORDER};}}"
            f"QComboBox::down-arrow{{image:{_combo_arrow_url(MUTED)};width:10px;height:6px;}}"
            f"QComboBox:hover::down-arrow{{image:{_combo_arrow_url(TEXT)};}}"
            f"QComboBox:focus::down-arrow{{image:{_combo_arrow_url(ACCENT)};}}")

        # Row 1: merge mode + preset
        row1 = QHBoxLayout(); row1.setSpacing(8)
        row1.addWidget(self._lbl_lang_mode); row1.addWidget(self._combo_lang_mode)
        # Preset dropdown
        vsep_p = QFrame(); vsep_p.setFrameShape(QFrame.VLine)
        vsep_p.setStyleSheet(f"background:{BORDER};max-width:1px;"); vsep_p.setFixedHeight(18)
        self._lbl_preset = QLabel(_t('tf_preset_label'))
        self._lbl_preset.setStyleSheet(f"color:{MUTED};font-size:12px;")
        self._combo_preset = _ThemedCombo()
        self._combo_preset.addItems([_t('tf_preset_doc'), _t('tf_preset_novel')])
        self._combo_preset.setFixedHeight(24); self._combo_preset.setFixedWidth(140)
        self._combo_preset.setStyleSheet(self._combo_lang_mode.styleSheet())
        self._combo_preset.currentIndexChanged.connect(self._apply_preset)
        row1.addWidget(vsep_p)
        row1.addWidget(self._lbl_preset); row1.addWidget(self._combo_preset)
        row1.addStretch()

        # Rows 2~3: column-aligned grid (same structure as Bulk Fixer)
        self._chk_mid  = QCheckBox(_t('tf_opt_mid'));  self._chk_mid.setChecked(True)
        self._chk_sep  = QCheckBox(_t('tf_opt_sep'));  self._chk_sep.setChecked(False)
        self._chk_auto = QCheckBox(_t('tf_opt_auto')); self._chk_auto.setChecked(False)
        self._chk_auto.stateChanged.connect(lambda s: self._spin_auto.setEnabled(bool(s)))
        self._spin_auto = QSpinBox(); self._spin_auto.setRange(30, 300); self._spin_auto.setValue(100); self._spin_auto.setEnabled(False)
        self._spin_auto.setFixedHeight(24)
        self._lbl_chars = QLabel(_t('tf_opt_chars'))
        self._chk_blank = QCheckBox(_t('tf_opt_blank')); self._chk_blank.setChecked(True)
        self._chk_blank.stateChanged.connect(lambda s: self._spin_blank.setEnabled(bool(s)))
        self._spin_blank = QSpinBox(); self._spin_blank.setRange(1, 10); self._spin_blank.setValue(1)
        self._spin_blank.setFixedHeight(24)
        self._lbl_line = QLabel(_t('tf_opt_line'))

        from PySide6.QtWidgets import QGridLayout, QSizePolicy
        grid = QGridLayout(); grid.setSpacing(8); grid.setContentsMargins(0,0,0,0)
        for chk in (self._chk_mid, self._chk_sep):
            chk.setMaximumWidth(260)
            chk.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        vsep0 = QFrame(); vsep0.setFrameShape(QFrame.VLine)
        vsep0.setStyleSheet(f"background:{BORDER};max-width:1px;")
        vsep1 = QFrame(); vsep1.setFrameShape(QFrame.VLine)
        vsep1.setStyleSheet(f"background:{BORDER};max-width:1px;")
        grid.addWidget(self._chk_mid,   0, 0)
        grid.addWidget(vsep0,           0, 1)
        grid.addWidget(self._chk_auto,  0, 2)
        grid.addWidget(self._spin_auto, 0, 3)
        grid.addWidget(self._lbl_chars, 0, 4)
        grid.addWidget(self._chk_sep,   1, 0)
        grid.addWidget(vsep1,           1, 1)
        grid.addWidget(self._chk_blank, 1, 2)
        grid.addWidget(self._spin_blank,1, 3)
        grid.addWidget(self._lbl_line,  1, 4)
        grid.setColumnStretch(5, 1)

        ol.addLayout(row1); ol.addLayout(grid)
        bl.addWidget(opt_bar)

        # ── Progress bar (hidden by default) ──────────────────────────
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setFixedHeight(5)
        self._progress_bar.setVisible(False)
        self._progress_bar.setStyleSheet(self._progress_ss())
        bl.addWidget(self._progress_bar)

        # ── Text editors (splitter) ───────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal); splitter.setHandleWidth(6)

        # Left: original text
        _w_in = QWidget(); _vl_in = QVBoxLayout(_w_in)
        _vl_in.setContentsMargins(0,0,0,0); _vl_in.setSpacing(4)
        self._grp_in = QLabel(_t('tf_grp_input'))
        self._grp_in.setObjectName("grp_title_lbl")
        self._input_edit = TextFixerEdit()
        self._input_edit.setPlaceholderText(_t('tf_ph_input_edit'))
        self._input_edit.textChanged.connect(self._on_input_changed)
        _vl_in.addWidget(self._grp_in)
        _vl_in.addWidget(self._input_edit, stretch=1)

        # Right: corrected text
        _w_out = QWidget(); _vl_out = QVBoxLayout(_w_out)
        _vl_out.setContentsMargins(0,0,0,0); _vl_out.setSpacing(4)
        self._grp_out = QLabel(_t('tf_grp_output'))
        self._grp_out.setObjectName("grp_title_lbl")
        self._output_edit = TextFixerOutputEdit(); self._output_edit.setReadOnly(True)
        self._output_edit.setPlaceholderText(_t('tf_ph_output'))
        _vl_out.addWidget(self._grp_out)
        _vl_out.addWidget(self._output_edit, stretch=1)

        splitter.addWidget(_w_in); splitter.addWidget(_w_out)
        splitter.setSizes([520, 520])
        bl.addWidget(splitter, stretch=1)

        # ── Search bar (Ctrl+F, hidden by default) ────────────────────
        self._search_bar = QWidget()
        sb = QHBoxLayout(self._search_bar); sb.setContentsMargins(6,4,12,4); sb.setSpacing(6)
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText(_t('tf_search_ph'))
        self._search_edit.setFixedHeight(28)
        self._search_edit.setStyleSheet(
            f"QLineEdit{{background:{SURFACE};border:1px solid {BORDER};"
            f"border-radius:6px;padding:2px 8px;color:{TEXT};font-size:13px;}}"
            f"QLineEdit:focus{{border-color:{ACCENT};}}")
        self._lbl_search_count = QLabel("")
        self._lbl_search_count.setStyleSheet(f"color:{MUTED};font-size:12px;min-width:60px;")
        btn_ss = (f"QPushButton{{background:{SURFACE};border:1px solid {BORDER};"
                  f"color:{TEXT};border-radius:6px;padding:3px 10px;font-size:12px;}}"
                  f"QPushButton:hover{{border-color:{ACCENT};color:{ACCENT};}}"
                  f"QPushButton:disabled{{color:{DISABLED};}}")
        self._btn_search_prev = QPushButton(_t('tf_search_prev')); self._btn_search_prev.setFixedHeight(26)
        self._btn_search_next = QPushButton(_t('tf_search_next')); self._btn_search_next.setFixedHeight(26)
        btn_close_s = QPushButton("✕"); btn_close_s.setFixedSize(26, 26)
        for b in (self._btn_search_prev, self._btn_search_next, btn_close_s):
            b.setStyleSheet(btn_ss)
        self._btn_search_prev.clicked.connect(lambda: self._search_step(-1))
        self._btn_search_next.clicked.connect(lambda: self._search_step(1))
        btn_close_s.clicked.connect(self._close_search)
        self._search_edit.returnPressed.connect(lambda: self._search_step(1))
        self._search_edit.textChanged.connect(self._search_run)
        sb.addWidget(QLabel("🔍")); sb.addWidget(self._search_edit, 1)
        sb.addWidget(self._lbl_search_count)
        sb.addWidget(self._btn_search_prev); sb.addWidget(self._btn_search_next)
        sb.addWidget(btn_close_s)
        self._search_bar.setVisible(False)
        self._search_matches = []   # List of (edit, cursor) pairs
        self._search_cur = -1
        bl.addWidget(self._search_bar)

        # Ctrl+F shortcut
        sc_find = QShortcut(QKeySequence("Ctrl+F"), self)
        sc_find.activated.connect(self._open_search)
        sc_esc = QShortcut(QKeySequence("Escape"), self)
        sc_esc.activated.connect(self._close_search)

        # ── Scrolling: panels are independent — no sync (avoids drift caused by line-count differences) ──
        # Use ◀ Prev / Next ▶ buttons to navigate change regions

        # ── Diff navigation bar (jump between change regions, only shown when results exist) ──
        self._diff_nav_bar = QWidget()
        dnb = QHBoxLayout(self._diff_nav_bar)
        dnb.setContentsMargins(0, 2, 0, 2); dnb.setSpacing(6)
        self._diff_positions = []
        self._diff_cur = -1
        nav_ss = (f"QPushButton{{background:{SURFACE};border:1px solid {BORDER};"
                  f"color:{TEXT};border-radius:6px;padding:3px 10px;font-size:12px;}}"
                  f"QPushButton:hover{{border-color:{ACCENT};color:{ACCENT};}}"
                  f"QPushButton:disabled{{color:{DISABLED};}}")
        self._btn_prev_diff = QPushButton(_t('tf_diff_prev'))
        self._btn_next_diff = QPushButton(_t('tf_diff_next'))
        self._lbl_diff_pos  = QLabel("")
        self._lbl_diff_pos.setStyleSheet(f"color:{MUTED};font-size:12px;min-width:60px;")
        self._lbl_diff_pos.setAlignment(Qt.AlignmentFlag.AlignCenter)
        for btn in (self._btn_prev_diff, self._btn_next_diff):
            btn.setStyleSheet(nav_ss); btn.setFixedHeight(24); btn.setEnabled(False)
        self._btn_prev_diff.clicked.connect(lambda: self._nav_diff(-1))
        self._btn_next_diff.clicked.connect(lambda: self._nav_diff(1))
        dnb.addStretch()
        dnb.addWidget(self._btn_prev_diff)
        dnb.addWidget(self._lbl_diff_pos)
        dnb.addWidget(self._btn_next_diff)
        dnb.addStretch()
        self._diff_nav_bar.setVisible(False)
        bl.addWidget(self._diff_nav_bar)

        # ── Statistics bar ────────────────────────────────────────────
        stat = QHBoxLayout(); stat.setSpacing(8)
        self._lbl_mid_fix   = self._mk_stat(_t('tf_stat_mid'))
        self._lbl_blank_fix = self._mk_stat(_t('tf_stat_blank'))
        self._lbl_orig      = self._mk_stat(_t('tf_stat_orig'))
        self._lbl_new       = self._mk_stat(_t('tf_stat_new'))
        self._lbl_status    = QLabel(_t('tf_status_ready'))
        self._lbl_status.setStyleSheet(f"color:{MUTED};font-size:12px;")
        for w in [self._lbl_mid_fix, self._lbl_blank_fix, self._lbl_orig, self._lbl_new]:
            stat.addWidget(w)
        stat.addStretch()
        stat.addWidget(self._lbl_status)
        bl.addLayout(stat)

        root.addWidget(body, stretch=1)

    def _progress_ss(self):
        """Theme-aware progress bar style."""
        return (f"QProgressBar{{border:none;background:{BORDER};border-radius:2px;}}"
                f"QProgressBar::chunk{{background:{ACCENT};border-radius:2px;}}")

    def _mk_stat(self, text):
        lbl = QLabel(text); lbl.setObjectName("count_lbl"); return lbl

    def _apply_preset(self, index):
        """Auto-set options when a preset is chosen."""
        if index == 0:   # General document
            self._chk_mid.setChecked(True)
            self._chk_sep.setChecked(False)
            self._chk_auto.setChecked(False)
            self._chk_blank.setChecked(True)
        elif index == 1: # Book / novel
            self._chk_mid.setChecked(True)
            self._chk_sep.setChecked(True)
            self._chk_auto.setChecked(True)
            self._chk_blank.setChecked(True)

    # ── File open ─────────────────────────────────────────────────────
    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, _t('tf_open'), '', 'Text Files (*.txt);;All Files (*)')
        if path: self.load_file(path)

    def load_file(self, path: str):
        if not os.path.isfile(path):
            _dlg_warn(self, _t('tf_dlg_nofile'), f"{_t('tf_err_nofile')}:\n{path}"); return
        if not os.access(path, os.R_OK):
            _dlg_warn(self, _t('tf_dlg_noperm'), f"{_t('tf_err_perm')}:\n{path}"); return
        # v1.0.3: alchemy_detect_encoding detects BOM / UTF-16 / CJK encodings
        # v1.0.4: alchemy returns (enc, conf) tuple — confidence is unused here
        # v1.0.6: use safe_read_text_with_report helper —
        # if all 8 strict fallbacks fail, retry with errors='replace' as last resort (file load always succeeds)
        # v1.0.6 Phase 2-a: helper now returns 6-tuple — Text Fixer only uses dialogs, so
        # failures / total_failures are ignored (single-file B-mode: based on user consent)
        try:
            text, used_enc, read_mode, replace_count, _failures, _total_failures = \
                safe_read_text_with_report(path)
        except OSError as e:
            _dlg_error(self, _t('tf_dlg_ioerr'), str(e)); return
        if text is None:
            _dlg_error(self, _t('tf_dlg_encerr'), f"{_t('tf_err_enc')}:\n{path}"); return
        self._input_edit.setPlainText(text)
        self._input_edit.verticalScrollBar().setValue(0)
        self._start_keep_top()  # Prevent async layout scroll-jump on large files
        self._loaded_path = path   # Reference for original-path saving
        fname = os.path.basename(path)
        if read_mode == 'replace':
            # v1.0.6: Partial encoding failure — warn user + show in status bar
            self._lbl_status.setText(
                f'⚠  {fname}  ({used_enc.upper()}, {replace_count} chars replaced)')
            _glog(f"⚠ [Text Fixer] Partial encoding failure: {fname} "
                  f"({used_enc}, {replace_count} chars replaced)")
            _dlg_warn(self, _t('tf_dlg_encerr'),
                      _t('tf_warn_partial_enc', fname=fname, enc=used_enc.upper(),
                         n=replace_count))
        else:
            self._lbl_status.setText(f'📂  {fname}  ({used_enc.upper()})')
            _glog(f"[Text Fixer] File loaded: {fname} ({used_enc})")

    def _start_keep_top(self, edits=None):
        """Prevent scroll drift during async layout of large documents.
        If rangeChanged is silent for 2 seconds, layout is considered complete and we exit."""
        if edits is None:
            edits = [self._input_edit, self._output_edit]
        _user_scrolled = [False]
        _layout_done = [False]
        for edit in edits:
            try: edit.verticalScrollBar().sliderPressed.disconnect()
            except (RuntimeError, TypeError): pass
            edit.verticalScrollBar().sliderPressed.connect(
                lambda: _user_scrolled.__setitem__(0, True))

        # If rangeChanged is silent for 2 seconds, treat layout as complete
        _debounce = [None]
        def _on_layout_stable():
            _layout_done[0] = True
            for edit in edits:
                try: edit.verticalScrollBar().rangeChanged.disconnect(_on_range)
                except (RuntimeError, TypeError): pass
        def _on_range(lo, hi):
            if _debounce[0]: _debounce[0].stop()
            t = QTimer(); t.setSingleShot(True); t.setInterval(2000)
            t.timeout.connect(_on_layout_stable)
            t.start()
            _debounce[0] = t
        for edit in edits:
            edit.verticalScrollBar().rangeChanged.connect(_on_range)
        # Safety net: force exit after 60 seconds
        QTimer.singleShot(60000, _on_layout_stable)

        def _keep():
            if _user_scrolled[0] or _layout_done[0]:
                return
            for edit in edits:
                sb = edit.verticalScrollBar()
                if sb.value() != 0:
                    sb.setValue(0)
            QTimer.singleShot(100, _keep)
        QTimer.singleShot(200, _keep)
        QTimer.singleShot(200, _keep)

    # ── Run correction ────────────────────────────────────────────────
    def run_fix(self):
        text = self._input_edit.toPlainText()
        if not text.strip(): return
        self._last_original = text
        self._btn_run.setEnabled(False)
        self._lbl_status.setText(_t('tf_running'))
        # Initialize and show progress bar
        self._progress_bar.setValue(0)
        self._progress_bar.setVisible(True)
        if self._worker and self._worker.isRunning():
            try:
                self._worker.done.disconnect()
                self._worker.error.disconnect()
                self._worker.progress.disconnect()
            except Exception:
                pass
            self._worker.quit()
            if not self._worker.wait(2000): self._worker.terminate(); self._worker.wait(500)
        _lang_codes = ['auto', 'ko', 'en']
        lang_mode = _lang_codes[self._combo_lang_mode.currentIndex()]
        self._worker = TextFixerWorker(
            text, self._chk_mid.isChecked(),
            self._chk_blank.isChecked(), self._spin_blank.value(),
            self._chk_sep.isChecked(),
            self._chk_auto.isChecked(), self._spin_auto.value(),
            lang_mode=lang_mode
        )
        self._worker.done.connect(self._on_fix_done)
        self._worker.error.connect(self._on_fix_error)
        self._worker.progress.connect(self._progress_bar.setValue)
        self._worker.start()

    def _on_fix_done(self, result, fixed_mid, fixed_blank, orig, new):
        self._output_edit.unlock_scroll()  # Unlock any prior scroll lock
        self._output_edit.setPlainText(result)
        for edit in (self._input_edit, self._output_edit):
            cur = edit.textCursor()
            cur.movePosition(cur.MoveOperation.Start)
            edit.setTextCursor(cur)
            edit.verticalScrollBar().setValue(0)
        _orig = self._last_original
        def _do_highlight():
            self._highlight_diff(_orig, result)
        QTimer.singleShot(100, _do_highlight)
        self._start_keep_top()  # Prevent async layout scroll-jump in both panels
        self._lbl_mid_fix.setText(_t('tf_stat_mid_n', n=fixed_mid))
        self._lbl_blank_fix.setText(_t('tf_stat_blank_n', n=fixed_blank))
        self._lbl_orig.setText(_t('tf_stat_orig_n', n=orig))
        self._lbl_new.setText(_t('tf_stat_new_n', n=new))
        self._btn_run.setEnabled(True)
        self._btn_copy.setEnabled(True); self._btn_save.setEnabled(True)
        # Enable overwrite only when loaded from a file
        if hasattr(self, '_act_overwrite'):
            self._act_overwrite.setEnabled(bool(self._loaded_path))
        # Hide progress bar after completion
        self._progress_bar.setValue(100)
        QTimer.singleShot(600, lambda: self._progress_bar.setVisible(False))
        # Save undo state
        self._undo_data = ('text', self._last_original, self._input_edit.toPlainText())
        self._btn_undo.setEnabled(True)
        self._lbl_status.setText(
            _t('tf_done', mid=fixed_mid, blank=fixed_blank) + '  │  ' + _t('tf_highlight')
        )
        _glog(f"[Text Fixer] Done — {fixed_mid} merges, {fixed_blank} blank lines")

    def _highlight_diff(self, original, result):
        if not original or not result: return
        if len(result.split('\n')) > 3000: return
        import difflib
        orig_lines   = original.split('\n')
        result_lines = result.split('\n')

        # ── Collect change positions ──────────────────────────────────
        orig_changed  = set()   # Line numbers changed in original
        out_changed   = set()   # Line numbers changed in corrected text
        diff_anchors  = []      # For navigation — output line numbers (first line of each group)

        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
                None, orig_lines, result_lines, autojunk=False).get_opcodes():
            if tag in ('replace', 'delete', 'insert'):
                orig_changed.update(range(i1, i2))
                out_changed.update(range(j1, j2))
                anchor = j1 if j1 < len(result_lines) else max(0, j1 - 1)
                diff_anchors.append(anchor)

        # Update navigation state
        self._diff_positions = sorted(diff_anchors)
        self._diff_cur = -1
        has = bool(self._diff_positions)
        self._btn_prev_diff.setEnabled(has)
        self._btn_next_diff.setEnabled(has)
        self._lbl_diff_pos.setText(f"0/{len(self._diff_positions)}" if has else "")
        self._diff_nav_bar.setVisible(has)

        # ── Original highlight (red) ──────────────────────────────────
        fmt_orig = QTextCharFormat()
        fmt_orig.setBackground(QColor(220, 80, 80, 70))
        doc_in = self._input_edit.document()
        cur_in = QTextCursor(doc_in)

        # Block Qt from scrolling the viewport to a change position during highlighting
        for edit in (self._input_edit, self._output_edit):
            edit.setUpdatesEnabled(False)

        cur_in.beginEditBlock()
        for li in sorted(orig_changed):
            blk = doc_in.findBlockByNumber(li)
            if blk.isValid():
                cur_in.setPosition(blk.position())
                cur_in.movePosition(cur_in.MoveOperation.EndOfBlock, cur_in.MoveMode.KeepAnchor)
                cur_in.mergeCharFormat(fmt_orig)
        cur_in.endEditBlock()

        # ── Corrected-text highlight (green) ──────────────────────────
        fmt_out = QTextCharFormat()
        fmt_out.setBackground(QColor(60, 180, 100, 70))
        doc_out = self._output_edit.document()
        cur_out = QTextCursor(doc_out)
        cur_out.beginEditBlock()
        for li in sorted(out_changed):
            blk = doc_out.findBlockByNumber(li)
            if blk.isValid():
                cur_out.setPosition(blk.position())
                cur_out.movePosition(cur_out.MoveOperation.EndOfBlock, cur_out.MoveMode.KeepAnchor)
                cur_out.mergeCharFormat(fmt_out)
        cur_out.endEditBlock()

        # Pin cursor to top, then resume updates → Qt renders first frame from the top
        for edit in (self._input_edit, self._output_edit):
            c = edit.textCursor()
            c.movePosition(c.MoveOperation.Start)
            edit.setTextCursor(c)
            edit.verticalScrollBar().setValue(0)
            edit.setUpdatesEnabled(True)

    def _open_search(self):
        self._search_bar.setVisible(True)
        self._search_edit.setFocus()
        self._search_edit.selectAll()

    def _close_search(self):
        self._search_bar.setVisible(False)
        self._search_matches = []; self._search_cur = -1
        self._lbl_search_count.setText("")
        # Clear search highlights
        for edit in (self._input_edit, self._output_edit):
            cur = edit.textCursor()
            cur.select(cur.SelectionType.Document)
            fmt = QTextCharFormat(); fmt.setBackground(QColor(0, 0, 0, 0))
            cur.mergeCharFormat(fmt)
            cur.clearSelection(); edit.setTextCursor(cur)
        # Reapply diff highlights
        orig = self._last_original
        result = self._output_edit.toPlainText()
        if orig and result:
            self._highlight_diff(orig, result)

    def _search_run(self):
        keyword = self._search_edit.text()
        self._search_matches = []; self._search_cur = -1
        # Reset existing search highlights, then reapply diff
        self._close_search_highlights()
        if not keyword:
            self._lbl_search_count.setText(""); return
        fmt_match = QTextCharFormat(); fmt_match.setBackground(QColor(255, 220, 0, 160))
        matches = []
        for edit in (self._input_edit, self._output_edit):
            doc = edit.document()
            cur = QTextCursor(doc)
            while True:
                cur = doc.find(keyword, cur)
                if cur.isNull(): break
                highlight = QTextCursor(cur)
                highlight.mergeCharFormat(fmt_match)
                matches.append((edit, QTextCursor(cur)))
        self._search_matches = matches
        total = len(matches)
        self._lbl_search_count.setText(f"0/{total}" if total else _t('tf_search_none'))
        self._lbl_search_count.setStyleSheet(
            f"color:{'#C0392B' if not total else MUTED};font-size:12px;min-width:60px;")
        if total: self._search_step(1)

    def _close_search_highlights(self):
        """Clear only search highlights (keep diff highlights)."""
        # Simple approach: reapply diff to overwrite
        pass

    def _search_step(self, direction):
        if not self._search_matches: return
        n = len(self._search_matches)
        self._search_cur = (self._search_cur + direction) % n
        self._lbl_search_count.setText(f"{self._search_cur + 1}/{n}")
        edit, cur = self._search_matches[self._search_cur]
        # Move the editor cursor to the target position
        edit.setTextCursor(cur)
        edit.ensureCursorVisible()
        # Sync-scroll the opposite panel to the same line
        line_no = cur.blockNumber()
        other = self._output_edit if edit is self._input_edit else self._input_edit
        blk = other.document().findBlockByNumber(line_no)
        if blk.isValid():
            oc = other.textCursor(); oc.setPosition(blk.position())
            other.setTextCursor(oc); other.ensureCursorVisible()
        """Jump to previous / next change region."""
        if not self._diff_positions: return
        n = len(self._diff_positions)
        self._diff_cur = max(0, min(n - 1, self._diff_cur + direction))
        line_no = self._diff_positions[self._diff_cur]
        self._lbl_diff_pos.setText(f"{self._diff_cur + 1}/{n}")
        self._btn_prev_diff.setEnabled(self._diff_cur > 0)
        self._btn_next_diff.setEnabled(self._diff_cur < n - 1)

        # Scroll both panels to the target line
        for edit in (self._input_edit, self._output_edit):
            blk = edit.document().findBlockByNumber(line_no)
            if blk.isValid():
                cur = edit.textCursor()
                cur.setPosition(blk.position())
                edit.setTextCursor(cur)
                edit.ensureCursorVisible()

    def _on_fix_error(self, msg):
        self._btn_run.setEnabled(True)
        self._progress_bar.setVisible(False)
        _dlg_error(self, _t('tf_err_fix'), msg)
        self._lbl_status.setText(_t('tf_err_fix'))

    # ── Copy / save ───────────────────────────────────────────────────
    def copy_output(self):
        text = self._output_edit.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self._lbl_status.setText(_t('tf_copied'))

    # ── Save methods ──────────────────────────────────────────────
    def _save_default(self):
        """Default action on button click: save as _fixed if a file was loaded, otherwise Save As."""
        if self._loaded_path:
            self._save_fixed()
        else:
            self._save_as()

    def _save_fixed(self):
        """Save with [Fixed] tag prepended at the original location."""
        text = self._output_edit.toPlainText()
        if not text: return
        if self._loaded_path:
            fname = os.path.basename(self._loaded_path)
            save_path = os.path.join(os.path.dirname(self._loaded_path), f'[Fixed]{fname}')
        else:
            save_path, _ = QFileDialog.getSaveFileName(
                self, _t('tf_save_fixed'), os.path.join(_CFG.get('output_dir', str(_OUTPUT_DIR)), '[Fixed]text.txt'), 'Text Files (*.txt);;All Files (*)')
            if not save_path: return
        try:
            with open(save_path, 'w', encoding='utf-8') as f: f.write(text)
            self._lbl_status.setText(_t('tf_saved', name=os.path.basename(save_path)))
            _glog(f'[Text Fixer] [Fixed] saved: {save_path}')
            try: os.startfile(os.path.dirname(save_path))
            except Exception: pass
        except OSError as e:
            _dlg_error(self, _t('tf_err_save'), str(e))

    def _save_as(self):
        """Save As (always opens dialog)."""
        text = self._output_edit.toPlainText()
        if not text: return
        # Default location: global output folder, file name in [Fixed] format
        global_odir = _CFG.get('output_dir', str(_OUTPUT_DIR))
        if self._loaded_path:
            fname = os.path.basename(self._loaded_path)
            default = os.path.join(global_odir, f'[Fixed]{fname}')
        else:
            default = os.path.join(global_odir, '[Fixed]text.txt')
        path, _ = QFileDialog.getSaveFileName(
            self, _t('tf_save_as'), default,
            'Text Files (*.txt);;All Files (*)')
        if not path: return
        try:
            with open(path, 'w', encoding='utf-8') as f: f.write(text)
            self._lbl_status.setText(_t('tf_saved', name=os.path.basename(path)))
            _glog(f'[Text Fixer] Saved: {path}')
            try: os.startfile(os.path.dirname(path))
            except Exception: pass
        except OSError as e:
            _dlg_error(self, _t('tf_err_save'), str(e))

    def save_file(self):
        """Backward-compatibility shim — delegates to _save_default."""
        self._save_default()

    # ── Reset ─────────────────────────────────────────────────────────
    def clear_all(self):
        self._input_edit.clear(); self._output_edit.clear()
        self._last_original = ''; self._undo_data = None; self._loaded_path = None
        self._btn_copy.setEnabled(False); self._btn_save.setEnabled(False)
        self._btn_undo.setEnabled(False)
        self._lbl_mid_fix.setText(_t('tf_stat_mid'))
        self._lbl_blank_fix.setText(_t('tf_stat_blank'))
        self._lbl_orig.setText(_t('tf_stat_orig'))
        self._lbl_new.setText(_t('tf_stat_new'))
        self._lbl_status.setText(_t('tf_cleared'))

    # ── Undo ──────────────────────────────────────────────────────────
    def _undo(self):
        if not self._undo_data: return
        _, orig_text, _ = self._undo_data
        self._output_edit.clear()
        self._input_edit.setPlainText(orig_text)
        self._undo_data = None; self._btn_undo.setEnabled(False)
        self._btn_copy.setEnabled(False); self._btn_save.setEnabled(False)
        self._lbl_status.setText(_t('tf_undo_done'))

    # ── Worker shutdown ───────────────────────────────────────────────
    def is_busy(self) -> bool:
        """True if the correction worker is running."""
        return bool(self._worker and self._worker.isRunning())

    def _stop_worker(self):
        if self._worker and self._worker.isRunning():
            self._worker.quit()
            if not self._worker.wait(2000): self._worker.terminate(); self._worker.wait(500)

    # ── DnD (whole panel) ─────────────────────────────────────────────
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls() and any(
            u.isLocalFile() and u.toLocalFile().lower().endswith('.txt')
            for u in e.mimeData().urls()
        ): e.acceptProposedAction()
        else: e.ignore()

    def dropEvent(self, e):
        for url in e.mimeData().urls():
            if url.isLocalFile():
                path = url.toLocalFile()
                if path.lower().endswith('.txt'):
                    self.load_file(path); e.acceptProposedAction(); return
        e.ignore()

    # ── On-input change ───────────────────────────────────────────────
    def _on_input_changed(self):
        self._btn_run.setEnabled(bool(self._input_edit.toPlainText().strip()))

    # ── Theme / translation / settings ────────────────────────────────
    def refresh_btn_styles(self):
        secondary_ss = (f"QPushButton{{background:{SURFACE};border:1.5px solid {BTN_BORDER_H};"
                        f"color:{TEXT};border-radius:8px;padding:5px 12px;}}"
                        f"QPushButton:hover{{background:{SRF2};border-color:{ACCENT};}}"
                        f"QPushButton:pressed{{background:{BTN_PRESSED};}}"
                        f"QPushButton:disabled{{background:{SRF2};color:{DISABLED};}}")
        for attr in ('_btn_open', '_btn_copy', '_btn_clear', '_btn_undo'):
            if hasattr(self, attr): getattr(self, attr).setStyleSheet(secondary_ss)
        # QToolButton (save button) — separate style
        if hasattr(self, '_btn_save'):
            self._btn_save.setStyleSheet(
                f'QToolButton{{background:{SURFACE};border:1.5px solid {BORDER};'
                f'color:{TEXT};border-radius:8px;padding:5px 10px;}}'
                f'QToolButton:hover{{background:{SRF2};border-color:{ACCENT};}}'
                f'QToolButton:pressed{{background:{BTN_PRESSED};}}'
                f'QToolButton:disabled{{background:{SRF2};color:{DISABLED};}}'
                f'QToolButton::menu-button{{border-left:1px solid {BORDER};'
                f'border-radius:0 8px 8px 0;width:16px;}}'
            )
            self._btn_save.setIcon(_svg_icon('save', ACCENT))
            self._btn_save.setIconSize(QSize(20,20))
        if hasattr(self, '_drop_zone'): self._drop_zone.set_idle()
        # Refresh option-bar theme
        if hasattr(self, '_opt_bar'):
            self._opt_bar.setStyleSheet(
                f"QWidget#tf_opt_bar{{background:{SRF2};border:1px solid {BORDER};"
                f"border-radius:8px;}}"
                f"QWidget#tf_opt_bar QComboBox{{background:{SRF2};border-color:{BORDER};}}"
                f"QWidget#tf_opt_bar QComboBox::drop-down{{background:{BORDER};}}")
        if hasattr(self, '_combo_lang_mode'):
            self._combo_lang_mode.setStyleSheet(
                f"QComboBox{{background:{SRF2};border:1.5px solid {BORDER};"
                f"border-radius:8px;color:{TEXT};"
                f"padding:2px 28px 2px 8px;font-size:13px;min-height:18px;}}"
                f"QComboBox:focus{{border-color:{ACCENT};}}"
                f"QComboBox:hover{{border-color:{INPUT_H};}}"
                f"QComboBox::drop-down{{subcontrol-origin:padding;"
                f"subcontrol-position:right center;width:24px;border:none;"
                f"border-left:1.5px solid {BORDER};"
                f"border-top-right-radius:8px;border-bottom-right-radius:8px;"
                f"background:{BORDER};}}"
                f"QComboBox::down-arrow{{image:{_combo_arrow_url(MUTED)};width:10px;height:6px;}}"
                f"QComboBox:hover::down-arrow{{image:{_combo_arrow_url(TEXT)};}}"
                f"QComboBox:focus::down-arrow{{image:{_combo_arrow_url(ACCENT)};}}")
        if hasattr(self, '_progress_bar'):
            self._progress_bar.setStyleSheet(self._progress_ss())
        # Refresh preset combobox style
        if hasattr(self, '_combo_preset'):
            self._combo_preset.setStyleSheet(
                f"QComboBox{{background:{SRF2};border:1.5px solid {BORDER};"
                f"border-radius:8px;color:{TEXT};"
                f"padding:2px 28px 2px 8px;font-size:13px;min-height:18px;}}"
                f"QComboBox:focus{{border-color:{ACCENT};}}"
                f"QComboBox:hover{{border-color:{INPUT_H};}}"
                f"QComboBox::drop-down{{subcontrol-origin:padding;"
                f"subcontrol-position:right center;width:24px;border:none;"
                f"border-left:1.5px solid {BORDER};"
                f"border-top-right-radius:8px;border-bottom-right-radius:8px;"
                f"background:{BORDER};}}"
                f"QComboBox::down-arrow{{image:{_combo_arrow_url(MUTED)};width:10px;height:6px;}}"
                f"QComboBox:hover::down-arrow{{image:{_combo_arrow_url(TEXT)};}}"
                f"QComboBox:focus::down-arrow{{image:{_combo_arrow_url(ACCENT)};}}")
        # Refresh SVG icon colors
        _isz = QSize(20,20)
        for attr, key in [('_btn_open','folder_open'),
                          ('_btn_copy','clipboard'),('_btn_clear','trash')]:
            if hasattr(self, attr): getattr(self, attr).setIcon(_svg_icon(key, ACCENT)); getattr(self, attr).setIconSize(_isz)

    def retranslate(self):
        self._btn_open.setText(_t('tf_open'))
        self._btn_run.setText(_t('tf_run'))
        self._btn_copy.setText(_t('tf_copy'))
        self._btn_save.setText(_t('tf_save'))
        if hasattr(self, '_act_fixed'):
            self._act_fixed.setText(_t('tf_save_fixed'))
            self._act_saveas.setText(_t('tf_save_as'))
        self._btn_clear.setText(_t('tf_clear'))
        self._btn_undo.setText(_t('btn_undo'))
        self._chk_mid.setText(_t('tf_opt_mid'))
        if hasattr(self, '_chk_sep'): self._chk_sep.setText(_t('tf_opt_sep'))
        if hasattr(self, '_chk_auto'): self._chk_auto.setText(_t('tf_opt_auto'))
        if hasattr(self, '_lbl_chars'): self._lbl_chars.setText(_t('tf_opt_chars'))
        self._chk_blank.setText(_t('tf_opt_blank'))
        self._lbl_line.setText(_t('tf_opt_line'))
        if hasattr(self, '_lbl_lang_mode'):
            self._lbl_lang_mode.setText(_t('tf_lang_mode'))
        if hasattr(self, '_combo_lang_mode'):
            ci = self._combo_lang_mode.currentIndex()
            self._combo_lang_mode.clear()
            self._combo_lang_mode.addItems([_t('tf_lang_auto'), _t('tf_lang_ko'), _t('tf_lang_en')])
            self._combo_lang_mode.setCurrentIndex(ci)
        self._grp_in.setText(_t('tf_grp_input'))
        self._grp_out.setText(_t('tf_grp_output'))
        self._input_edit.setPlaceholderText(_t('tf_ph_input_edit'))
        self._output_edit.setPlaceholderText(_t('tf_ph_output'))
        self._lbl_mid_fix.setText(_t('tf_stat_mid'))
        self._lbl_blank_fix.setText(_t('tf_stat_blank'))
        self._lbl_orig.setText(_t('tf_stat_orig'))
        self._lbl_new.setText(_t('tf_stat_new'))
        if hasattr(self._drop_zone, 'set_idle'): self._drop_zone.set_idle()
        # Refresh search bar / diff navigation
        if hasattr(self, '_search_edit'):
            self._search_edit.setPlaceholderText(_t('tf_search_ph'))
        if hasattr(self, '_lbl_preset'): self._lbl_preset.setText(_t('tf_preset_label'))
        if hasattr(self, '_combo_preset'):
            ci = self._combo_preset.currentIndex()
            self._combo_preset.blockSignals(True)
            self._combo_preset.clear()
            self._combo_preset.addItems([_t('tf_preset_doc'), _t('tf_preset_novel')])
            self._combo_preset.setCurrentIndex(ci)
            self._combo_preset.blockSignals(False)
        if hasattr(self, '_btn_search_prev'):
            self._btn_search_prev.setText(_t('tf_search_prev'))
            self._btn_search_next.setText(_t('tf_search_next'))
        if hasattr(self, '_btn_prev_diff'):
            self._btn_prev_diff.setText(_t('tf_diff_prev'))
            self._btn_next_diff.setText(_t('tf_diff_next'))
        # Status text — only refresh while in ready state
        if hasattr(self, '_lbl_status'):
            ready_msgs = set(_all_translations_of('tf_status_ready'))
            if self._lbl_status.text() in ready_msgs or not self._lbl_status.text():
                self._lbl_status.setText(_t('tf_status_ready'))

    def get_config(self): return {
        'do_mid': self._chk_mid.isChecked(),
        'do_sep': self._chk_sep.isChecked(),
        'do_auto_split': self._chk_auto.isChecked(),
        'max_split_chars': self._spin_auto.value(),
        'do_blank': self._chk_blank.isChecked(),
        'max_blank': self._spin_blank.value(),
        'lang_mode_idx': self._combo_lang_mode.currentIndex() if hasattr(self, '_combo_lang_mode') else 0,
        'preset_idx': self._combo_preset.currentIndex() if hasattr(self, '_combo_preset') else 0,
    }

    def apply_config(self, cfg):
        # Restore preset first (before options — individual options will overwrite)
        if hasattr(self, '_combo_preset'):
            self._combo_preset.blockSignals(True)
            self._combo_preset.setCurrentIndex(cfg.get('preset_idx', 0))
            self._combo_preset.blockSignals(False)
        self._chk_mid.setChecked(cfg.get('do_mid', True))
        self._chk_sep.setChecked(cfg.get('do_sep', False))
        self._chk_auto.setChecked(cfg.get('do_auto_split', False))
        self._spin_auto.setValue(cfg.get('max_split_chars', 100))
        self._spin_auto.setEnabled(cfg.get('do_auto_split', False))
        self._chk_blank.setChecked(cfg.get('do_blank', True))
        self._spin_blank.setValue(cfg.get('max_blank', 1))
        if hasattr(self, '_combo_lang_mode'):
            self._combo_lang_mode.setCurrentIndex(cfg.get('lang_mode_idx', 0))


# ═══════════════════════════════════════════════
# Tab 6: Bulk Fixer — file list widget
# ═══════════════════════════════════════════════
class BulkFixerDropZone(QLabel):
    """Drop zone dedicated to Bulk Fixer (new in v1.0.6).

    File / folder drop area only — structurally separated from the file list to avoid
    Qt behavior conflicts that occurred when InternalMove mode coexisted with external drops.
    Fuses MergeDropZone (Text Merger) + TextFixerDropZone (Text Fixer) patterns.
    """
    files_dropped  = Signal(list)   # List of .txt files
    folder_dropped = Signal(str)    # Single folder path

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("bulkDropZone")
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumHeight(110)
        self.setTextFormat(Qt.TextFormat.RichText)
        self.set_idle()

    def set_idle(self):
        t = _T
        self.setStyleSheet(
            f"QLabel#bulkDropZone{{border:1.5px dashed {t['BORDER']};"
            f"border-radius:10px;background:{t['SURFACE']};padding:14px;"
            f"color:{t['TEXT']};}}")
        self.setText(
            f"<div style='text-align:center;'>"
            f"<div style='font-size:28px;line-height:1;font-family:{_EMOJI_FONT_FAMILY};'>📄</div>"
            f"<div style='color:{t['MUTED']};font-size:13px;margin-top:8px;'>"
            f"{_t('bulk_drop_txt')}</div>"
            f"<div style='color:{t['DISABLED']};font-size:13px;margin-top:4px;'>"
            f"{_t('bulk_drop_fmt')}</div>"
            f"</div>")

    def set_hover(self):
        t = _T
        self.setStyleSheet(
            f"QLabel#bulkDropZone{{border:2px dashed {t['ACCENT']};"
            f"border-radius:10px;background:{_accent_alpha(0.07)};padding:14px;}}")
        self.setText(
            f"<div style='text-align:center;'>"
            f"<div style='font-size:28px;line-height:1;font-family:{_EMOJI_FONT_FAMILY};'>📄</div>"
            f"<div style='color:{t['ACCENT']};font-size:13px;margin-top:8px;'>"
            f"{_t('tf_drop_hover')}</div>"
            f"</div>")

    def refresh_style(self):
        self.set_idle()

    def _has_valid(self, mime):
        """Check whether .txt files (or folders that may contain .txt) are present."""
        if not mime.hasUrls(): return False
        for u in mime.urls():
            if not u.isLocalFile(): continue
            p = u.toLocalFile()
            if os.path.isdir(p): return True
            if p.lower().endswith('.txt'): return True
        return False

    def dragEnterEvent(self, e):
        if self._has_valid(e.mimeData()):
            self.set_hover(); e.acceptProposedAction()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if self._has_valid(e.mimeData()): e.acceptProposedAction()
        else: e.ignore()

    def dragLeaveEvent(self, e):
        self.set_idle()

    def dropEvent(self, e):
        _glog(f"🔵 [Trace] BulkFixerDropZone.dropEvent enter (urls={len(e.mimeData().urls())})")
        self.set_idle()
        txt_files = []
        folders = []
        for url in e.mimeData().urls():
            if not url.isLocalFile(): continue
            p = url.toLocalFile()
            if os.path.isdir(p):
                folders.append(p)
            elif p.lower().endswith('.txt'):
                txt_files.append(p)
        # If folders exist, send the first folder via the folder signal (panel does recursive scan)
        # .txt files go through a separate signal
        if folders:
            self.folder_dropped.emit(folders[0])
        if txt_files:
            self.files_dropped.emit(txt_files)
        if folders or txt_files:
            e.acceptProposedAction()
        else:
            e.ignore()
        _glog(f"🔵 [Trace] BulkFixerDropZone.dropEvent exit (txt={len(txt_files)}, folders={len(folders)})")


class BulkFixerFileList(QTreeWidget):
    """Multi-file list widget for TXT only — 2 columns (file name | path).

    v1.0.6: switched from InternalMove to DragDrop mode. External drops are handled by BulkFixerDropZone.
    This widget is internal-reorder only. Replicates the MergeFileTree (Text Merger) pattern.
    """
    files_changed = Signal(int)
    order_changed = Signal()  # v1.0.6: signal emitted after drag reorder completes

    def __init__(self, parent=None):
        super().__init__(parent)
        self._files = []
        self._sort_asc = True
        self.setColumnCount(2)
        self.setHeaderLabels([_t('tag_col_filename'), _t('tag_col_path')])
        self.setRootIsDecorated(False)
        self.setUniformRowHeights(True)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # v1.0.6: DragDrop mode (avoids Qt's auto-delete bug from InternalMove + e.ignore() combo)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragEnabled(True)
        self.setSortingEnabled(False)
        hdr = self.header()
        hdr.setSectionResizeMode(0, QHeaderView.Stretch)
        hdr.setSectionResizeMode(1, QHeaderView.Interactive)
        self.setColumnWidth(1, 180)
        hdr.setSortIndicatorShown(True)
        hdr.setSortIndicator(0, Qt.SortOrder.AscendingOrder)
        # v1.0.6: Workaround for Qt disabling header click when setSortingEnabled(False)
        # — replicates the pattern applied to MergeFileTree in v1.0.4
        hdr.setSectionsClickable(True)
        hdr.sectionClicked.connect(self._on_header_clicked)

    def _on_header_clicked(self, col):
        if col == 0:
            self._sort_asc = not self._sort_asc
            order = Qt.SortOrder.AscendingOrder if self._sort_asc else Qt.SortOrder.DescendingOrder
            self.header().setSortIndicator(0, order)
            self.sort_files(self._sort_asc)

    # v1.0.6: UserRole for storing pure file path (avoids toolTip pollution)
    _PATH_ROLE = Qt.ItemDataRole.UserRole + 4

    def _make_item(self, path):
        item = QTreeWidgetItem([os.path.basename(path), os.path.dirname(path)])
        item.setToolTip(0, path)
        item.setToolTip(1, path)
        item.setData(0, self._PATH_ROLE, path)  # v1.0.6: pure path
        return item

    def add_files(self, paths):
        added = []
        for p in paths:
            if not p: continue
            if not p.lower().endswith('.txt'): continue
            if p not in self._files:
                self._files.append(p); added.append(p)
        for p in added:
            self.addTopLevelItem(self._make_item(p))
        if added: self.files_changed.emit(len(self._files))

    def remove_selected(self):
        items = self.selectedItems()
        if not items: return
        rows = sorted({self.indexOfTopLevelItem(i) for i in items}, reverse=True)
        for r in rows:
            self.takeTopLevelItem(r)
            del self._files[r]
        self.files_changed.emit(len(self._files))

    def clear_files(self):
        self._files.clear(); self.clear(); self.files_changed.emit(0)

    def move_selection(self, delta):
        items = self.selectedItems()
        if not items: return
        rows = sorted({self.indexOfTopLevelItem(i) for i in items})
        if delta < 0 and rows[0] == 0: return
        if delta > 0 and rows[-1] == len(self._files) - 1: return
        new_rows = []
        for r in (reversed(rows) if delta > 0 else rows):
            nr = r + delta
            self._files[r], self._files[nr] = self._files[nr], self._files[r]
            item = self.takeTopLevelItem(r)
            self.insertTopLevelItem(nr, item)
            new_rows.append(nr)
        self.clearSelection()
        for r in new_rows:
            self.topLevelItem(r).setSelected(True)

    @property
    def files(self): return list(self._files)

    def sort_files(self, ascending=True):
        if not self._files: return
        self._files.sort(key=lambda p: os.path.basename(p).lower(), reverse=not ascending)
        self.clear()
        for p in self._files:
            self.addTopLevelItem(self._make_item(p))

    def _sync(self):
        # v1.0.6: prefer _PATH_ROLE, fall back to legacy lookup for compatibility
        def _p(it):
            v = it.data(0, self._PATH_ROLE)
            return v if v else it.toolTip(0)
        self._files = [_p(self.topLevelItem(i))
                       for i in range(self.topLevelItemCount())]

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace): self.remove_selected()
        else: super().keyPressEvent(e)

    def startDrag(self, supported_actions):
        """v1.0.6: Force CopyAction — block Qt's automatic source deletion on MoveAction.
        Actual reorder is handled manually in dropEvent. (MergeFileTree pattern)"""
        super().startDrag(Qt.DropAction.CopyAction)

    def dragEnterEvent(self, e):
        # Allow internal reorder only (external drops handled by BulkFixerDropZone)
        if e.source() is self: e.acceptProposedAction()
        else: e.ignore()

    def dragMoveEvent(self, e):
        if e.source() is self: e.acceptProposedAction()
        else: e.ignore()

    def dropEvent(self, e):
        """v1.0.6: Manual internal reorder (replicates MergeFileTree pattern)."""
        _glog(f"🔵 [Trace] BulkFixerFileList.dropEvent enter (source_is_self={e.source() is self})")
        if e.source() is not self:
            e.ignore(); return
        dragged = self.selectedItems()
        if not dragged:
            e.accept(); return
        target = self.itemAt(e.pos())
        if target is None:
            # Drop into empty area → move to the end
            src_rows = sorted([self.indexOfTopLevelItem(i) for i in dragged], reverse=True)
            saved = []
            for row in src_rows:
                saved.insert(0, self.takeTopLevelItem(row))
            for item in saved:
                self.addTopLevelItem(item)
            self.selectionModel().clearSelection()
            for item in saved: item.setSelected(True)
            e.acceptProposedAction()
            self._sync()
            self.order_changed.emit()
            return
        if target in dragged:
            e.accept(); return  # Drop onto self — ignore
        target_row = self.indexOfTopLevelItem(target)
        drop_above = e.pos().y() < self.visualItemRect(target).center().y()
        src_rows = sorted([self.indexOfTopLevelItem(i) for i in dragged], reverse=True)
        saved = []
        for row in src_rows:
            saved.insert(0, self.takeTopLevelItem(row))
            if row < target_row:
                target_row -= 1
        insert_row = target_row if drop_above else target_row + 1
        for i, item in enumerate(saved):
            self.insertTopLevelItem(insert_row + i, item)
        self.selectionModel().clearSelection()
        for i in range(len(saved)):
            t = self.topLevelItem(insert_row + i)
            if t: t.setSelected(True)
        e.acceptProposedAction()
        self._sync()
        self.order_changed.emit()
        _glog(f"🔵 [Trace] BulkFixerFileList.dropEvent exit (moved={len(saved)})")


# ═══════════════════════════════════════════════
# Tab 6: Bulk Fixer — background worker
# ═══════════════════════════════════════════════
class FolderScanWorker(QThread):
    """Recursively scan a folder in the background — collect file list.
    exts: set of allowed extensions (e.g. {'.txt', '.md'}); None means all
    recursive: True scans subfolders, False scans only the top level
    """
    sig_progress = Signal(int)        # 0–100
    sig_found    = Signal(int)        # Number of files found so far
    sig_done     = Signal(list)       # Final list of file paths
    sig_error    = Signal(str)

    def __init__(self, folder: str, exts=None, recursive: bool = True, parent=None):
        super().__init__(parent)
        self.folder    = folder
        self.exts      = {e.lower() for e in exts} if exts else None
        self.recursive = recursive
        self._abort    = False

    def abort(self): self._abort = True

    def run(self):
        try:
            if self.recursive:
                # Step 1: collect folder list (for progress calculation)
                all_dirs = []
                for root, dirs, _ in os.walk(self.folder):
                    if self._abort: self.sig_done.emit([]); return
                    all_dirs.append(root)
                    dirs.sort()
                total = max(len(all_dirs), 1)
                # Step 2: scan files
                paths = []
                for i, dirpath in enumerate(all_dirs):
                    if self._abort: self.sig_done.emit([]); return
                    try:
                        for fname in sorted(os.listdir(dirpath)):
                            if self.exts is None or \
                               os.path.splitext(fname)[1].lower() in self.exts:
                                full = os.path.join(dirpath, fname)
                                if os.path.isfile(full):
                                    paths.append(full)
                    except OSError:
                        pass
                    self.sig_progress.emit(int((i + 1) / total * 100))
                    self.sig_found.emit(len(paths))
            else:
                # Non-recursive: top-level files only
                paths = []
                try:
                    entries = sorted(os.listdir(self.folder))
                    total = max(len(entries), 1)
                    for i, fname in enumerate(entries):
                        if self._abort: self.sig_done.emit([]); return
                        if self.exts is None or \
                           os.path.splitext(fname)[1].lower() in self.exts:
                            full = os.path.join(self.folder, fname)
                            if os.path.isfile(full):
                                paths.append(full)
                        self.sig_progress.emit(int((i + 1) / total * 100))
                        self.sig_found.emit(len(paths))
                except OSError as e:
                    self.sig_error.emit(str(e)); return
            self.sig_done.emit(paths)
        except Exception as e:
            self.sig_error.emit(str(e))


class BulkFixerWorker(QThread):
    """Bulk correction worker for multiple TXT files."""
    # v1.0.6 Phase 2-a: encoding-tier processing thresholds
    TIER1_THRESHOLD = 500    # 1~500 failures: Tier 1 (process + report)
    TIER2_THRESHOLD = 5000   # 501~5000 failures: Tier 2 (process + report, warning level)
                             # 5001+ failures: Tier 3 (skip + report)

    sig_progress      = Signal(int)
    sig_file_progress = Signal(int, str)
    # v1.0.6 Phase 2-a: sig_file_done bool → str category ('ok' / 'warn' / 'skip' / 'fail')
    sig_file_done     = Signal(str, str)
    # v1.0.6 Phase 2-a: sig_done (ok, fail) → (ok, warn, skip, fail) 4-param
    sig_done          = Signal(int, int, int, int)
    sig_error         = Signal(str)

    def __init__(self, files, out_dir,
                 do_mid, do_blank, max_blank,
                 do_sep=False, do_auto_split=False, max_split_chars=100,
                 lang_mode='auto', keep_structure=False):
        super().__init__()
        self.files = files
        self.out_dir = out_dir
        self.keep_structure = keep_structure  # Preserve original folder structure when output dir is set
        self.do_mid = do_mid
        self.do_blank = do_blank
        self.max_blank = max_blank
        self.do_sep = do_sep
        self.do_auto_split = do_auto_split
        self.max_split_chars = max_split_chars
        self.lang_mode = lang_mode
        self._abort = False

    def abort(self): self._abort = True

    def _fix_text(self, text, progress_cb=None, cb_chunk=500):
        """Reuses TextFixerWorker logic — single-text correction.
        progress_cb: optional callback fn(done_lines) — for large-file progress updates
        """
        # Determine language mode
        use_lang = self.lang_mode
        if use_lang == 'auto':
            use_lang = TextFixerWorker._detect_lang(text)

        lines = text.split('\n')
        fixed_mid = 0; fixed_blank = 0
        paragraphs = []; current = []
        for i, line in enumerate(lines):
            if line.strip() == '':
                paragraphs.append(current); paragraphs.append(None); current = []
            else:
                current.append(line)
        paragraphs.append(current)
        result = []
        n_para = max(len(paragraphs), 1)
        for pi, para in enumerate(paragraphs):
            # Callback: emit progress every cb_chunk paragraphs
            if progress_cb and pi % cb_chunk == 0:
                progress_cb(pi * len(lines) // n_para)
            if para is None: result.append(''); continue
            if not para: continue
            if self.do_mid and len(para) > 1:
                out_lines = [para[0]]
                for nxt in para[1:]:
                    prev = out_lines[-1]
                    prev_end = prev.rstrip()
                    last_ch = prev_end[-1] if prev_end else ''
                    is_sep = TextFixerWorker._is_sep_line(prev) or TextFixerWorker._is_sep_line(nxt)
                    if is_sep:
                        out_lines.append(nxt); continue
                    if use_lang == 'en':
                        is_abbr = (last_ch == '.' and TextFixerWorker._is_en_abbr(prev_end))
                        is_sent_end = (last_ch in TextFixerWorker._SENT_END and not is_abbr
                                       and not prev_end.rstrip('.').endswith('..'))
                        if is_sent_end:
                            out_lines.append(nxt)
                        else:
                            out_lines[-1] = TextFixerWorker._merge_en(prev, nxt)
                            fixed_mid += 1
                    else:
                        if (last_ch and last_ch not in TextFixerWorker._SENT_END):
                            out_lines[-1] = prev.rstrip() + ' ' + nxt.lstrip()
                            fixed_mid += 1
                        else:
                            out_lines.append(nxt)
                result.extend(out_lines)
            else:
                result.extend(para)
            result.append('')
        while result and result[-1].strip() == '': result.pop()
        if self.do_blank:
            cleaned = []; blank_count = 0
            for line in result:
                if line.strip() == '':
                    blank_count += 1
                    if blank_count <= self.max_blank: cleaned.append(line)
                    else: fixed_blank += 1
                else:
                    blank_count = 0; cleaned.append(line)
            result = cleaned
        if self.do_sep:
            sep_result = []; prev_blank = True
            for i, line in enumerate(result):
                sep_result.append(line)
                is_blank = not line.strip()
                if not is_blank and not prev_blank and i < len(result) - 1:
                    nxt = result[i + 1]
                    if nxt.strip():
                        last_ch = line.rstrip()[-1] if line.rstrip() else ''
                        nxt_first = nxt.lstrip()[0] if nxt.lstrip() else ''
                        if (last_ch in TextFixerWorker._SENT_END or
                                nxt_first in '"\u201c\u201d\u2018\u2019\u300c\u300e'):
                            sep_result.append('')
                prev_blank = is_blank
            result = sep_result
        if self.do_auto_split:
            expanded = []
            for line in result:
                if not line.strip() or len(line) <= self.max_split_chars:
                    expanded.append(line)
                else:
                    parts = TextFixerWorker._split_long_line(line, self.max_split_chars)
                    for j, part in enumerate(parts):
                        if part: expanded.append(part)
                        if j < len(parts) - 1: expanded.append('')
            result = expanded
        while result and result[0].strip() == '': result.pop(0)
        while result and result[-1].strip() == '': result.pop()
        return '\n'.join(result), fixed_mid, fixed_blank

    def _make_save_path(self, src):
        """Compute save path — prepend [Fixed] tag to file name.
        If keep_structure=True and out_dir is set, reproduces the original folder structure."""
        fname = os.path.basename(src)
        fixed_name = f"[Fixed]{fname}"
        if self.out_dir:
            if self.keep_structure:
                src_dir = os.path.dirname(src)
                if not hasattr(self, '_common_base'):
                    dirs = [os.path.dirname(f) for f in self.files]
                    self._common_base = os.path.commonpath(dirs) if dirs else src_dir
                try:
                    rel = os.path.relpath(src_dir, self._common_base)
                    save_dir = os.path.join(self.out_dir, rel)
                except ValueError:
                    save_dir = self.out_dir
                os.makedirs(save_dir, exist_ok=True)  # Only needed when reproducing structure
            else:
                save_dir = self.out_dir
        else:
            save_dir = os.path.dirname(src)  # Original location — folder already exists
        return os.path.join(save_dir, fixed_name)

    def run(self):
        _prevent_sleep()
        total = len(self.files)
        # v1.0.6 Phase 2-a: 4 counters (ok: strict success / warn: encoding Tier 1/2 processed
        # / skip: encoding Tier 3 (original protected, skipped) / fail: I/O or other exception)
        ok = 0; warn = 0; skip = 0; fail = 0
        try:
            for idx, path in enumerate(self.files):
                if self._abort: break
                fname = os.path.basename(path)
                self.sig_progress.emit(int(idx / total * 100))
                self.sig_file_progress.emit(0, fname)
                try:
                    # v1.0.3: alchemy_detect_encoding detects BOM / UTF-16 / CJK encodings
                    # v1.0.4: alchemy returns (enc, conf) tuple — confidence is unused here
                    # v1.0.6: use safe_read_text_with_report helper —
                    # if all strict fallbacks fail, retry with errors='replace' as last resort
                    # v1.0.6 Phase 2-a: 6-tuple return — track failure positions + tier branching
                    text, used_enc, read_mode, replace_count, failures, total_failures = \
                        safe_read_text_with_report(path)
                    if text is None: raise OSError(_t('tf_err_enc'))

                    # Pre-compute save path (report file lives in the same folder as the corrected output)
                    save_path = self._make_save_path(path)
                    save_dir = os.path.dirname(save_path)

                    # v1.0.6 Phase 2-a: tier branching only in replace mode
                    # Tier 1 (1~500): process + report
                    # Tier 2 (501~5000): process + report (warning level)
                    # Tier 3 (5001+): skip + report (protect original)
                    if read_mode == 'replace':
                        if total_failures > self.TIER2_THRESHOLD:
                            # Tier 3: skip — do not correct, only generate report (original untouched)
                            report_path = write_encoding_report(
                                output_dir=save_dir,
                                original_path=path,
                                used_enc=used_enc,
                                failures=failures,
                                total_failures=total_failures,
                                action_taken='skipped',
                            )
                            report_info = (f", report: {os.path.basename(report_path)}"
                                           if report_path else "")
                            _glog(f"❌ [Bulk Fixer] Tier 3 skipped (suspected encoding misdetect): "
                                  f"{fname} ({used_enc}, {total_failures:,} chars failed{report_info})")
                            self.sig_file_progress.emit(100, fname)
                            skip += 1
                            self.sig_file_done.emit(path, 'skip')
                            continue  # Next file — original protected
                        else:
                            # Tier 1 or 2: proceed with correction + generate report
                            report_path = write_encoding_report(
                                output_dir=save_dir,
                                original_path=path,
                                used_enc=used_enc,
                                failures=failures,
                                total_failures=total_failures,
                                action_taken='processed',
                            )
                            report_info = (f", report: {os.path.basename(report_path)}"
                                           if report_path else "")
                            tier_label = ("Tier 2" if total_failures > self.TIER1_THRESHOLD
                                          else "Tier 1")
                            _glog(f"⚠ [Bulk Fixer] {tier_label} partial encoding failure: {fname} "
                                  f"({used_enc}, {total_failures:,} chars failed{report_info})")
                            # warn count is incremented after successful save (shares the normal correction flow)

                    self.sig_file_progress.emit(20, fname)
                    # Correction — emit intermediate progress between 33%~80% based on line count
                    lines = text.split('\n')
                    n_lines = max(len(lines), 1)
                    chunk = max(n_lines // 20, 500)  # 5% increments or every 500 lines, whichever is larger

                    def _progress_cb(done_lines):
                        pct = 20 + int(done_lines / n_lines * 60)  # 20~80%
                        self.sig_file_progress.emit(min(pct, 80), fname)

                    fixed, _, _ = self._fix_text(text, _progress_cb, chunk)
                    self.sig_file_progress.emit(85, fname)
                    # Save
                    with open(save_path, 'w', encoding='utf-8') as f: f.write(fixed)
                    self.sig_file_progress.emit(100, fname)

                    # v1.0.6 Phase 2-a: classify count by read_mode
                    # (replace-mode Tier 3 was already continued above)
                    if read_mode == 'replace':
                        warn += 1
                        self.sig_file_done.emit(path, 'warn')
                    else:
                        ok += 1
                        self.sig_file_done.emit(path, 'ok')
                except Exception as e:
                    self.sig_file_progress.emit(0, fname)
                    fail += 1
                    self.sig_file_done.emit(path, 'fail')
                    _glog(f'[Bulk Fixer] Error {fname}: {e}')
            self.sig_progress.emit(100)
            self.sig_done.emit(ok, warn, skip, fail)
        except Exception as e:
            self.sig_error.emit(str(e))
        finally:
            _allow_sleep()


# ═══════════════════════════════════════════════
# Tab 6: Bulk Fixer panel
# ═══════════════════════════════════════════════
class BulkFixerPanel(QWidget):
    """Tab 6 — TXT bulk line-break correction panel."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)

        sep = QFrame(); sep.setFrameShape(QFrame.HLine); sep.setObjectName("tab_sep")
        root.addWidget(sep)

        body = QWidget()
        body_lay = QHBoxLayout(body)
        body_lay.setContentsMargins(16, 14, 16, 14); body_lay.setSpacing(16)

        # ══════════════════════════════════════
        # Left: file list
        # ══════════════════════════════════════
        left = QWidget()
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(0, 0, 0, 0); left_lay.setSpacing(10)

        # v1.0.6: Drop zone (top) — external file/folder drop only, always visible
        self._drop_zone = BulkFixerDropZone()
        self._drop_zone.files_dropped.connect(self._on_files_dropped)
        self._drop_zone.folder_dropped.connect(self._on_folder_dropped)
        left_lay.addWidget(self._drop_zone)

        # File list title
        self._lbl_file_list = QLabel(_t('bulk_file_list'))
        self._lbl_file_list.setObjectName("grp_title_lbl")
        left_lay.addWidget(self._lbl_file_list)

        # Create _flist first — top-button connect() references it
        self._flist = BulkFixerFileList()
        self._flist.setMinimumHeight(200)
        self._flist.currentItemChanged.connect(self._on_file_selected)
        self._lbl_cnt = QLabel("")
        self._lbl_cnt.setObjectName("count_lbl")
        self._flist.files_changed.connect(
            lambda n: self._lbl_cnt.setText(_t('bulk_file_count', n=n)))

        # ── Top button row: add file / add folder / clear all (same structure as Text Merger)
        top_row = QHBoxLayout(); top_row.setSpacing(6)
        self._btn_add = QPushButton(_t('btn_add_file'))
        self._btn_add.setObjectName("btn_primary")
        self._btn_add.setIcon(_svg_icon('document', 'white')); self._btn_add.setIconSize(QSize(20,20))
        self._btn_add.clicked.connect(self._add_files)
        self._btn_add_folder = QPushButton(_t('btn_add_folder'))
        self._btn_add_folder.setObjectName("btn_folder_add")
        self._btn_add_folder.setIcon(_svg_icon('folder_open', 'white')); self._btn_add_folder.setIconSize(QSize(20,20))
        self._btn_add_folder.clicked.connect(self._add_folder)
        self._btn_clr = QPushButton(_t('btn_del_all'))
        self._btn_clr.setIcon(_svg_icon('trash', ACCENT)); self._btn_clr.setIconSize(QSize(20,20))
        self._btn_clr.clicked.connect(self._flist.clear_files)
        for btn in [self._btn_add, self._btn_add_folder, self._btn_clr]:
            btn.setFixedHeight(36)
        top_row.addWidget(self._btn_add)
        top_row.addWidget(self._btn_add_folder)
        top_row.addStretch()
        top_row.addWidget(self._btn_clr)
        left_lay.addLayout(top_row)

        # File list — added to layout (sortable via QTreeWidget header click)
        left_lay.addWidget(self._flist, 1)

        # Folder-scan progress bar (hidden in normal state)
        self._scan_bar = QProgressBar()
        self._scan_bar.setRange(0, 100); self._scan_bar.setValue(0)
        self._scan_bar.setFixedHeight(5); self._scan_bar.setTextVisible(False)
        self._scan_bar.setStyleSheet(
            f"QProgressBar{{border:none;background:{BORDER};border-radius:2px;}}"
            f"QProgressBar::chunk{{background:{ACCENT};border-radius:2px;opacity:0.7;}}")
        self._scan_bar.setVisible(False)
        left_lay.addWidget(self._scan_bar)
        self._scan_lbl = QLabel("")
        self._scan_lbl.setStyleSheet(
            f"font-size:11px;color:{MUTED};"
            f"font-family:'Consolas','Courier New','Menlo',monospace;")
        self._scan_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._scan_lbl.setFixedHeight(16)
        self._scan_lbl.setVisible(False)
        left_lay.addWidget(self._scan_lbl)
        self._scan_worker = None

        # ── Bottom button row: delete selected / move up / move down (same structure as Text Merger)
        bot_row = QHBoxLayout(); bot_row.setSpacing(6)
        self._btn_del = QPushButton(_t('btn_del_sel'))
        self._btn_del.setIcon(_svg_icon('trash', ACCENT)); self._btn_del.setIconSize(QSize(20,20))
        self._btn_del.clicked.connect(self._flist.remove_selected)
        self._btn_up = QPushButton(_t('btn_up'))
        self._btn_up.setIcon(_svg_icon('arrow_up', ACCENT)); self._btn_up.setIconSize(QSize(16,16))
        self._btn_up.clicked.connect(lambda: self._flist.move_selection(-1))
        self._btn_dn = QPushButton(_t('btn_down'))
        self._btn_dn.setIcon(_svg_icon('arrow_down', ACCENT)); self._btn_dn.setIconSize(QSize(16,16))
        self._btn_dn.clicked.connect(lambda: self._flist.move_selection(1))
        for btn in [self._btn_del, self._btn_up, self._btn_dn]:
            btn.setFixedHeight(36)
        bot_row.addWidget(self._btn_del)
        bot_row.addWidget(self._btn_up)
        bot_row.addWidget(self._btn_dn)
        bot_row.addStretch()
        bot_row.addWidget(self._lbl_cnt)
        left_lay.addLayout(bot_row)

        body_lay.addWidget(left, 4)

        # ══════════════════════════════════════
        # Right: options + preview + save + run
        # ══════════════════════════════════════
        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(0, 0, 0, 0); right_lay.setSpacing(10)

        # ── Correction options ──────────────────
        self._lbl_opts = QLabel(_t('bulk_options'))
        self._lbl_opts.setObjectName("grp_title_lbl")
        right_lay.addWidget(self._lbl_opts)

        opt_bar = QWidget(); opt_bar.setObjectName("tf_opt_bar")
        self._opt_bar = opt_bar
        opt_bar.setStyleSheet(
            f"QWidget#tf_opt_bar{{background:{SRF2};border:1px solid {BORDER};"
            f"border-radius:8px;}}"
            f"QWidget#tf_opt_bar QComboBox{{background:{SRF2};border-color:{BORDER};}}"
            f"QWidget#tf_opt_bar QComboBox::drop-down{{background:{BORDER};}}")
        ol = QVBoxLayout(opt_bar)
        ol.setContentsMargins(14, 10, 14, 10); ol.setSpacing(8)

        self._lbl_lang_mode = QLabel(_t('tf_lang_mode'))
        self._combo_lang_mode = _ThemedCombo()
        self._combo_lang_mode.addItems([_t('tf_lang_auto'), _t('tf_lang_ko'), _t('tf_lang_en')])
        self._combo_lang_mode.setFixedHeight(24)
        self._combo_lang_mode.setFixedWidth(160)
        self._combo_lang_mode.setStyleSheet(
            f"QComboBox{{background:{SRF2};border:1.5px solid {BORDER};"
            f"border-radius:8px;color:{TEXT};"
            f"padding:2px 28px 2px 8px;font-size:13px;min-height:18px;}}"
            f"QComboBox:focus{{border-color:{ACCENT};}}"
            f"QComboBox:hover{{border-color:{INPUT_H};}}"
            f"QComboBox::drop-down{{subcontrol-origin:padding;"
            f"subcontrol-position:right center;width:24px;border:none;"
            f"border-left:1.5px solid {BORDER};"
            f"border-top-right-radius:8px;border-bottom-right-radius:8px;"
            f"background:{BORDER};}}"
            f"QComboBox::down-arrow{{image:{_combo_arrow_url(MUTED)};width:10px;height:6px;}}"
            f"QComboBox:hover::down-arrow{{image:{_combo_arrow_url(TEXT)};}}"
            f"QComboBox:focus::down-arrow{{image:{_combo_arrow_url(ACCENT)};}}")

        # Row 1: merge mode + preset
        row1 = QHBoxLayout(); row1.setSpacing(8)
        row1.addWidget(self._lbl_lang_mode); row1.addWidget(self._combo_lang_mode)
        sep1 = QFrame(); sep1.setFrameShape(QFrame.VLine)
        sep1.setStyleSheet(f"background:{BORDER};max-width:1px;"); sep1.setFixedHeight(18)
        row1.addWidget(sep1)
        self._lbl_preset_bulk = QLabel(_t('tf_preset_label'))
        self._combo_preset = _ThemedCombo()
        self._combo_preset.addItems([_t('tf_preset_doc'), _t('tf_preset_novel')])
        self._combo_preset.setFixedHeight(24); self._combo_preset.setFixedWidth(140)
        self._combo_preset.setStyleSheet(self._combo_lang_mode.styleSheet())
        self._combo_preset.currentIndexChanged.connect(self._apply_preset)
        row1.addWidget(self._lbl_preset_bulk); row1.addWidget(self._combo_preset)
        row1.addStretch()

        # Rows 2~3: column-aligned grid
        self._chk_mid  = QCheckBox(_t('tf_opt_mid'));  self._chk_mid.setChecked(True)
        self._chk_sep  = QCheckBox(_t('tf_opt_sep'));  self._chk_sep.setChecked(False)
        self._chk_auto = QCheckBox(_t('tf_opt_auto')); self._chk_auto.setChecked(False)
        self._chk_auto.stateChanged.connect(lambda s: self._spin_auto.setEnabled(bool(s)))
        self._spin_auto = QSpinBox()
        self._spin_auto.setRange(30, 300); self._spin_auto.setValue(100)
        self._spin_auto.setEnabled(False); self._spin_auto.setFixedHeight(24)
        self._lbl_chars = QLabel(_t('tf_opt_chars'))
        self._chk_blank = QCheckBox(_t('tf_opt_blank')); self._chk_blank.setChecked(True)
        self._chk_blank.stateChanged.connect(lambda s: self._spin_blank.setEnabled(bool(s)))
        self._spin_blank = QSpinBox()
        self._spin_blank.setRange(1, 10); self._spin_blank.setValue(1)
        self._spin_blank.setFixedHeight(24)
        self._lbl_line = QLabel(_t('tf_opt_line'))

        from PySide6.QtWidgets import QGridLayout, QSizePolicy
        grid = QGridLayout(); grid.setSpacing(8); grid.setContentsMargins(0,0,0,0)
        vsep0 = QFrame(); vsep0.setFrameShape(QFrame.VLine)
        vsep0.setStyleSheet(f"background:{BORDER};max-width:1px;")
        vsep1 = QFrame(); vsep1.setFrameShape(QFrame.VLine)
        vsep1.setStyleSheet(f"background:{BORDER};max-width:1px;")
        # Column 0 checkbox: max-width set to prevent CJK long-text overflow
        for chk in (self._chk_mid, self._chk_sep):
            chk.setMaximumWidth(260)
            chk.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # Columns: 0=check1  1=divider  2=check2  3=spin  4=unit  5=stretch
        grid.addWidget(self._chk_mid,   0, 0)
        grid.addWidget(vsep0,           0, 1)
        grid.addWidget(self._chk_auto,  0, 2)
        grid.addWidget(self._spin_auto, 0, 3)
        grid.addWidget(self._lbl_chars, 0, 4)
        grid.addWidget(self._chk_sep,   1, 0)
        grid.addWidget(vsep1,           1, 1)
        grid.addWidget(self._chk_blank, 1, 2)
        grid.addWidget(self._spin_blank,1, 3)
        grid.addWidget(self._lbl_line,  1, 4)
        grid.setColumnStretch(5, 1)

        ol.addLayout(row1); ol.addLayout(grid)
        right_lay.addWidget(opt_bar)

        # ── Preview ──────────────────────────────
        self._lbl_preview = QLabel(_t('bulk_preview'))
        self._lbl_preview.setObjectName("grp_title_lbl")
        right_lay.addWidget(self._lbl_preview)

        self._preview_edit = QTextEdit()
        self._preview_edit.setReadOnly(True)
        self._preview_edit.setPlaceholderText(_t('bulk_preview_ph'))
        self._preview_edit.setMinimumHeight(120)
        right_lay.addWidget(self._preview_edit, stretch=1)

        # ── Save mode ────────────────────────────
        self._lbl_save_mode = QLabel(_t('bulk_save_mode'))
        self._lbl_save_mode.setObjectName("grp_title_lbl")
        right_lay.addWidget(self._lbl_save_mode)

        save_bar = QWidget()
        save_bar.setObjectName("bulk_save_bar")
        save_bar.setStyleSheet(
            f"QWidget#bulk_save_bar{{background:{SRF2};border:1px solid {BORDER};border-radius:8px;}}")
        self._save_bar = save_bar
        sl = QVBoxLayout(save_bar)
        sl.setContentsMargins(10, 10, 10, 12); sl.setSpacing(6)

        # Save-mode description
        self._lbl_save_desc = QLabel(_t('bulk_save_desc'))
        self._lbl_save_desc.setStyleSheet(f"color:{MUTED};font-size:11px;background:transparent;")
        self._lbl_save_desc.setWordWrap(True)
        sl.addWidget(self._lbl_save_desc)

        # Output folder row
        orow = QHBoxLayout(); orow.setSpacing(6)
        self._edit_odir = QLineEdit()
        self._edit_odir.setPlaceholderText(_t('bulk_out_ph'))
        self._edit_odir.setFixedHeight(32)
        self._btn_brw = QPushButton(_t('conv_btn_pick'))
        self._btn_brw.setObjectName("btn_primary")
        self._btn_brw.setIcon(_svg_icon('folder', 'white')); self._btn_brw.setIconSize(QSize(18,18))
        self._btn_brw.setFixedHeight(32)
        self._btn_brw.clicked.connect(self._browse_out)
        orow.addWidget(self._edit_odir, 1); orow.addWidget(self._btn_brw)
        sl.addLayout(orow)

        # Preserve folder structure checkbox
        self._chk_keep_structure = QCheckBox(_t('bulk_keep_structure'))
        self._chk_keep_structure.setChecked(False)
        self._chk_keep_structure.setStyleSheet(f"color:{MUTED};font-size:12px;background:transparent;")
        sl.addWidget(self._chk_keep_structure)
        right_lay.addWidget(save_bar)

        # ── Progress bars (overall + current file) ─
        # Overall progress bar
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100); self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setFixedHeight(8); self._progress_bar.setVisible(False)
        self._progress_bar.setStyleSheet(self._progress_ss())
        right_lay.addWidget(self._progress_bar)

        # Text under overall bar: right-aligned, % monospace-width
        self._lbl_total_progress = QLabel("")
        self._lbl_total_progress.setStyleSheet(
            f"font-size:11px;color:{MUTED};"
            f"font-family:'Consolas','Courier New','Menlo',monospace;")
        self._lbl_total_progress.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._lbl_total_progress.setFixedHeight(16)
        self._lbl_total_progress.setVisible(False)
        right_lay.addWidget(self._lbl_total_progress)

        # Current-file bar
        self._file_progress_bar = QProgressBar()
        self._file_progress_bar.setRange(0, 100); self._file_progress_bar.setValue(0)
        self._file_progress_bar.setTextVisible(False)
        self._file_progress_bar.setFixedHeight(5); self._file_progress_bar.setVisible(False)
        self._file_progress_bar.setStyleSheet(
            f"QProgressBar{{border:none;background:{BORDER};border-radius:2px;}}"
            f"QProgressBar::chunk{{background:{ACCENT};border-radius:2px;opacity:0.7;}}")
        right_lay.addWidget(self._file_progress_bar)

        # Text under file bar: right-aligned, % monospace-width
        self._lbl_file_progress = QLabel("")
        self._lbl_file_progress.setStyleSheet(
            f"font-size:11px;color:{MUTED};"
            f"font-family:'Consolas','Courier New','Menlo',monospace;")
        self._lbl_file_progress.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._lbl_file_progress.setFixedHeight(16)
        self._lbl_file_progress.setVisible(False)
        right_lay.addWidget(self._lbl_file_progress)

        # ── Run button + status ──────────────────
        run_row = QHBoxLayout(); run_row.setSpacing(10)
        self._btn_run = QPushButton(_t('bulk_run'))
        self._btn_run.setObjectName("btn_merge")
        self._btn_run.setIcon(_svg_icon('broom', 'white')); self._btn_run.setIconSize(QSize(22,22))
        self._btn_run.setFixedHeight(44)
        self._btn_run.clicked.connect(self._start)
        self._btn_abort = QPushButton(_t('btn_abort'))
        self._btn_abort.setFixedHeight(44); self._btn_abort.setEnabled(False)
        self._btn_abort.clicked.connect(self._abort)
        run_row.addWidget(self._btn_run, 1); run_row.addWidget(self._btn_abort)
        right_lay.addLayout(run_row)

        self._lbl_status = QLabel(_t('bulk_status_ready'))
        self._lbl_status.setStyleSheet(f"color:{MUTED};font-size:12px;")
        self._lbl_status.setWordWrap(True)
        right_lay.addWidget(self._lbl_status)

        right_lay.addStretch()
        body_lay.addWidget(right, 5)
        root.addWidget(body, 1)

    # ── Internal helpers ───────────────────────
    def _progress_ss(self):
        return (f"QProgressBar{{border:none;background:{BORDER};border-radius:2px;}}"
                f"QProgressBar::chunk{{background:{ACCENT};border-radius:2px;}}")

    def _set_save_mode(self, mode):
        pass  # Save mode is fixed ([Fixed] tag) — kept as legacy-compat dummy

    # v1.0.6: Handle files/folders received from the drop zone ──
    def _on_files_dropped(self, paths: list):
        """Called when BulkFixerDropZone drops .txt files."""
        _glog(f"🔵 [Trace] _on_files_dropped enter (n={len(paths) if paths else 0})")
        if paths: self._flist.add_files(paths)
        _glog("🔵 [Trace] _on_files_dropped exit")

    def _on_folder_dropped(self, folder: str):
        """Called when BulkFixerDropZone drops a folder — reuses existing _add_folder scan logic."""
        _glog(f"🔵 [Trace] _on_folder_dropped enter (folder={folder!r})")
        if not folder or not os.path.isdir(folder): return
        if self._scan_worker and self._scan_worker.isRunning():
            try:
                self._scan_worker.sig_progress.disconnect()
                self._scan_worker.sig_found.disconnect()
                self._scan_worker.sig_done.disconnect()
                self._scan_worker.sig_error.disconnect()
            except Exception: pass
            self._scan_worker.abort(); self._scan_worker.wait(1000)
        self._set_scan_ui(True)
        self._scan_worker = FolderScanWorker(folder, exts={'.txt'}, recursive=True)
        self._scan_worker.sig_progress.connect(self._scan_bar.setValue)
        self._scan_worker.sig_found.connect(
            lambda n: self._scan_lbl.setText(_t('bulk_scanning', n=n)))
        self._scan_worker.sig_done.connect(self._on_scan_done)
        self._scan_worker.sig_error.connect(self._on_scan_error)
        self._scan_worker.start()
        _glog("🔵 [Trace] _on_folder_dropped exit (scan worker started)")

    def _add_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, _t('btn_add_file'), '', 'Text Files (*.txt);;All Files (*)')
        if paths: self._flist.add_files(paths)

    def _add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, _t('btn_add_folder'))
        if not folder: return
        # Abort if already scanning
        if self._scan_worker and self._scan_worker.isRunning():
            try:
                self._scan_worker.sig_progress.disconnect()
                self._scan_worker.sig_found.disconnect()
                self._scan_worker.sig_done.disconnect()
                self._scan_worker.sig_error.disconnect()
            except Exception: pass
            self._scan_worker.abort(); self._scan_worker.wait(1000)
        # Lock UI + show scan bar
        self._set_scan_ui(True)
        self._scan_worker = FolderScanWorker(folder, exts={'.txt'}, recursive=True)
        self._scan_worker.sig_progress.connect(self._scan_bar.setValue)
        self._scan_worker.sig_found.connect(
            lambda n: self._scan_lbl.setText(_t('bulk_scanning', n=n)))
        self._scan_worker.sig_done.connect(self._on_scan_done)
        self._scan_worker.sig_error.connect(self._on_scan_error)
        self._scan_worker.start()

    def _set_scan_ui(self, scanning: bool):
        """Lock / unlock UI during scan."""
        self._scan_bar.setVisible(scanning)
        self._scan_bar.setValue(0)
        self._scan_lbl.setVisible(scanning)
        if not scanning: self._scan_lbl.setText("")
        for btn in (self._btn_add, self._btn_add_folder, self._btn_clr,
                    self._btn_del, self._btn_up, self._btn_dn):
            btn.setEnabled(not scanning)
        # v1.0.6: Disable drop zone during scan (prevents extra drops)
        if hasattr(self, '_drop_zone'):
            self._drop_zone.setEnabled(not scanning)
        if scanning:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        else:
            QApplication.restoreOverrideCursor()

    def _on_scan_done(self, paths: list):
        self._set_scan_ui(False)
        if paths:
            self._flist.add_files(paths)
        else:
            _dlg_warn(self, _t('dlg_ok'), _t('bulk_no_txt'))

    def _on_scan_error(self, msg: str):
        self._set_scan_ui(False)
        _dlg_error(self, _t('dlg_error_title'), msg)

    def _apply_preset(self, index):
        """Auto-set options when a preset is chosen — same presets as Text Fixer."""
        if index == 0:   # General document
            self._chk_mid.setChecked(True)
            self._chk_sep.setChecked(False)
            self._chk_auto.setChecked(False)
            self._chk_blank.setChecked(True)
        elif index == 1: # Book / novel
            self._chk_mid.setChecked(True)
            self._chk_sep.setChecked(True)
            self._chk_auto.setChecked(True)
            self._chk_blank.setChecked(True)

    def _browse_out(self):
        start = self._edit_odir.text() or _CFG.get('output_dir', str(_OUTPUT_DIR))
        d = QFileDialog.getExistingDirectory(self, _t('conv_btn_pick'), start)
        if d: self._edit_odir.setText(d)

    def _on_file_selected(self, cur, _prev):
        import time
        _t0 = time.perf_counter()
        if not cur:
            self._preview_edit.clear()
            _glog(f"🔵 [Trace] _on_file_selected exit (no-cur, {(time.perf_counter()-_t0)*1000:.1f}ms)")
            return
        # v1.0.6: prefer _PATH_ROLE, fall back to legacy lookup for compatibility
        path = cur.data(0, BulkFixerFileList._PATH_ROLE) or cur.toolTip(0)
        fname = os.path.basename(path) if path else '?'
        _glog(f"🔵 [Trace] _on_file_selected enter ({fname})")
        if not path or not os.path.exists(path):
            self._preview_edit.setPlainText('')
            _glog(f"🔵 [Trace] _on_file_selected exit (no path, {(time.perf_counter()-_t0)*1000:.1f}ms)")
            return
        # v1.0.6: use safe_read_text_with_report helper
        # — if all 8 strict fallbacks fail, retry with errors='replace' as last resort (preview always shown)
        # v1.0.6 Phase 2-a: helper now returns 6-tuple — preview does not need a report, so ignored
        # v1.0.6 diagnostics: 3-stage trace — measure safe_read / preview extraction / setPlainText separately
        _t_s0 = time.perf_counter()
        text, used_enc, mode, replace_count, _failures, _total_failures = \
            safe_read_text_with_report(path)
        _t_s1 = time.perf_counter()
        _glog(f"🔵 [Trace]   → safe_read done ({(_t_s1-_t_s0)*1000:.1f}ms, "
              f"mode={mode}, text_len={len(text) if text else 0:,})")
        if text is None:
            self._preview_edit.setPlainText('')
            _glog(f"🔵 [Trace] _on_file_selected exit (text=None, {(time.perf_counter()-_t0)*1000:.1f}ms)")
            return
        # Preview shows only the first 80 lines (performance)
        # v1.0.6 Phase 2-a: handle freezing on huge files (~500K lines) —
        # splitlines on a 27MB string allocates 500K objects but uses only 80 → severely wasteful
        # Slice the leading 32KB first, then splitlines → 80 lines is plenty, ~800x reduction in work
        # (Bulk Fixer preview is for "is this the right file + is the encoding correct" — fine review is Text Fixer's job)
        _t_p0 = time.perf_counter()
        preview = ''.join(text[:32768].splitlines(keepends=True)[:80])
        _t_p1 = time.perf_counter()
        _glog(f"🔵 [Trace]   → preview extraction done ({(_t_p1-_t_p0)*1000:.1f}ms, "
              f"preview_len={len(preview):,})")
        _t_r0 = time.perf_counter()
        self._preview_edit.setPlainText(preview)
        _t_r1 = time.perf_counter()
        _glog(f"🔵 [Trace]   → setPlainText done ({(_t_r1-_t_r0)*1000:.1f}ms)")
        if mode == 'replace':
            _glog(f"⚠ [Bulk Fixer] Preview: partial encoding failure — "
                  f"{os.path.basename(path)} ({used_enc}, {replace_count} chars replaced)")
        _glog(f"🔵 [Trace] _on_file_selected exit ({fname}, mode={mode}, "
              f"{(time.perf_counter()-_t0)*1000:.1f}ms)")

    # ── Run / abort ────────────────────────────
    def _start(self):
        files = self._flist.files
        if not files:
            _dlg_warn(self, '', _t('bulk_err_nofiles')); return
        out_dir = self._edit_odir.text().strip()
        # If a target folder is set, verify it exists
        if out_dir and not os.path.isdir(out_dir):
            _dlg_warn(self, '', _t('conv_out_ph')); return

        self._btn_run.setEnabled(False)
        self._btn_abort.setEnabled(True)
        self._progress_bar.setValue(0); self._progress_bar.setVisible(True)
        self._lbl_total_progress.setText(""); self._lbl_total_progress.setVisible(True)
        self._file_progress_bar.setValue(0); self._file_progress_bar.setVisible(True)
        self._lbl_file_progress.setText(""); self._lbl_file_progress.setVisible(True)
        self._lbl_status.setText(_t('bulk_running'))
        _lang_codes = ['auto', 'ko', 'en']
        lang_mode = _lang_codes[self._combo_lang_mode.currentIndex()]

        if self._worker is not None:
            try:
                self._worker.sig_progress.disconnect()
                self._worker.sig_file_progress.disconnect()
                self._worker.sig_done.disconnect()
                self._worker.sig_error.disconnect()
            except Exception:
                pass
        self._worker = BulkFixerWorker(
            files, out_dir,
            do_mid=self._chk_mid.isChecked(),
            do_blank=self._chk_blank.isChecked(),
            max_blank=self._spin_blank.value(),
            do_sep=self._chk_sep.isChecked(),
            do_auto_split=self._chk_auto.isChecked(),
            max_split_chars=self._spin_auto.value(),
            lang_mode=lang_mode,
            keep_structure=self._chk_keep_structure.isChecked() if hasattr(self, '_chk_keep_structure') else False
        )
        self._worker.sig_progress.connect(self._progress_bar.setValue)
        self._worker.sig_file_progress.connect(self._on_file_progress)
        self._worker.sig_done.connect(self._on_done)
        self._worker.sig_error.connect(self._on_error)
        self._worker.start()

    def _on_file_progress(self, pct: int, fname: str):
        self._file_progress_bar.setValue(pct)
        total = len(self._flist.files)
        done  = self._progress_bar.value() * total // 100
        overall_pct = int(self._progress_bar.value())
        # Below the overall bar: N/M  X%  (% width fixed to 4 chars)
        self._lbl_total_progress.setText(f"{done + 1}/{total}  {overall_pct:3d}%")
        # File-name ellipsis + % width fixed to 4 chars
        max_len = 18
        if len(fname) > max_len:
            base, ext = fname.rsplit('.', 1) if '.' in fname else (fname, '')
            keep = max(max_len - len(ext) - 4, 4)
            fname_short = f"{base[:keep]}...{base[-2:]}.{ext}" if ext else f"{fname[:max_len-3]}..."
        else:
            fname_short = fname
        self._lbl_file_progress.setText(f"{fname_short}  {pct:3d}%")

    def _abort(self):
        if self._worker: self._worker.abort()
        self._btn_abort.setEnabled(False)

    def _on_done(self, ok, warn, skip, fail):
        """v1.0.6 Phase 2-a: receives 4-category counts.
        - ok: strict success
        - warn: encoding Tier 1/2 processed + report generated
        - skip: encoding Tier 3 (original protected) + report generated
        - fail: I/O or other exception
        """
        self._progress_bar.setVisible(False)
        self._lbl_total_progress.setVisible(False)
        self._file_progress_bar.setVisible(False)
        self._lbl_file_progress.setVisible(False)
        self._btn_run.setEnabled(True); self._btn_abort.setEnabled(False)

        # Status label: number of saved files (ok+warn) and abnormal counts
        processed = ok + warn
        msg = _t('bulk_status_done', n=processed)
        if skip: msg += f'  {_t("bulk_status_skip")} ×{skip}'
        if fail: msg += f'  {_t("dlg_done_err")} ×{fail}'
        self._lbl_status.setText(msg)
        _glog(f'[Bulk Fixer] Done — ok {ok}, warn {warn}, skip {skip}, fail {fail}')

        # v1.0.6 Phase 2-a: if any abnormal count (warn/skip/fail) is non-zero,
        # show the tier-breakdown dialog. If all ok, skip the dialog (preserve previous UX).
        if warn > 0 or skip > 0 or fail > 0:
            msg_lines = [_t('bulk_done_ok', n=ok)]
            if warn > 0: msg_lines.append(_t('bulk_done_warn', n=warn))
            if skip > 0: msg_lines.append(_t('bulk_done_skip', n=skip))
            if fail > 0: msg_lines.append(_t('bulk_done_fail', n=fail))
            _dlg_info(self, _t('bulk_done_title'), '\n'.join(msg_lines))

        # Auto-open output folder after save completion
        out_dir = self._edit_odir.text().strip() or None
        if not out_dir:
            # If output folder is unset, use the first file's source folder
            item = self._flist.topLevelItem(0)
            if item:
                p = item.text(1)
                out_dir = os.path.dirname(p) if os.path.isfile(p) else p
        if out_dir and os.path.isdir(out_dir):
            try: os.startfile(out_dir)
            except Exception: pass

    def _on_error(self, msg):
        self._progress_bar.setVisible(False)
        self._lbl_total_progress.setVisible(False)
        self._file_progress_bar.setVisible(False)
        self._lbl_file_progress.setVisible(False)
        self._btn_run.setEnabled(True); self._btn_abort.setEnabled(False)
        self._lbl_status.setText(_t('bulk_status_err', msg=msg))

    def is_busy(self) -> bool:
        """True if the bulk-correction worker is running."""
        return bool(self._worker and self._worker.isRunning())

    def _stop_worker(self):
        if self._worker and self._worker.isRunning():
            self._worker.abort(); self._worker.wait(2000)
        if self._scan_worker and self._scan_worker.isRunning():
            self._scan_worker.abort(); self._scan_worker.wait(1000)
            self._set_scan_ui(False)
    def retranslate(self):
        self._lbl_file_list.setText(_t('bulk_file_list'))
        # v1.0.6: re-translate drop-zone text
        if hasattr(self, '_drop_zone'): self._drop_zone.refresh_style()
        self._btn_add.setText(_t('btn_add_file'))
        if hasattr(self, '_btn_add_folder'): self._btn_add_folder.setText(_t('btn_add_folder'))
        self._btn_del.setText(_t('btn_del_sel'))
        self._btn_clr.setText(_t('btn_del_all'))
        self._btn_up.setText(_t('btn_up'))
        self._btn_dn.setText(_t('btn_down'))
        self._lbl_opts.setText(_t('bulk_options'))
        self._chk_mid.setText(_t('tf_opt_mid'))
        self._chk_sep.setText(_t('tf_opt_sep'))
        self._chk_auto.setText(_t('tf_opt_auto'))
        self._lbl_chars.setText(_t('tf_opt_chars'))
        self._chk_blank.setText(_t('tf_opt_blank'))
        self._lbl_line.setText(_t('tf_opt_line'))
        if hasattr(self, '_lbl_lang_mode'):
            self._lbl_lang_mode.setText(_t('tf_lang_mode'))
        if hasattr(self, '_combo_lang_mode'):
            ci = self._combo_lang_mode.currentIndex()
            self._combo_lang_mode.clear()
            self._combo_lang_mode.addItems([_t('tf_lang_auto'), _t('tf_lang_ko'), _t('tf_lang_en')])
            self._combo_lang_mode.setCurrentIndex(ci)
        self._lbl_preview.setText(_t('bulk_preview'))
        self._preview_edit.setPlaceholderText(_t('bulk_preview_ph'))
        self._lbl_save_mode.setText(_t('bulk_save_mode'))
        if hasattr(self, '_lbl_save_desc'): self._lbl_save_desc.setText(_t('bulk_save_desc'))
        self._edit_odir.setPlaceholderText(_t('bulk_out_ph'))
        self._btn_brw.setText(_t('conv_btn_pick'))
        self._btn_run.setText(_t('bulk_run'))
        if hasattr(self, '_btn_abort'): self._btn_abort.setText(_t('btn_abort'))
        if hasattr(self, '_chk_keep_structure'): self._chk_keep_structure.setText(_t('bulk_keep_structure'))
        if hasattr(self, '_lbl_preset_bulk'): self._lbl_preset_bulk.setText(_t('tf_preset_label'))
        if hasattr(self, '_combo_preset'):
            ci = self._combo_preset.currentIndex()
            self._combo_preset.blockSignals(True)
            self._combo_preset.clear()
            self._combo_preset.addItems([_t('tf_preset_doc'), _t('tf_preset_novel')])
            self._combo_preset.setCurrentIndex(ci)
            self._combo_preset.blockSignals(False)
        # Status text — only refresh while in ready state (avoid overwriting in-progress messages)
        if hasattr(self, '_lbl_status'):
            ready_msgs = set(_all_translations_of('bulk_status_ready'))
            if self._lbl_status.text() in ready_msgs or not self._lbl_status.text():
                self._lbl_status.setText(_t('bulk_status_ready'))
        n = self._flist.topLevelItemCount()
        if n: self._lbl_cnt.setText(_t('bulk_file_count', n=n))
        self._flist.setHeaderLabels([_t('tag_col_filename'), _t('tag_col_path')])
        self._flist.update()

    # ── Settings save / restore ─────────────────
    def get_config(self) -> dict:
        return {
            'out_dir':        self._edit_odir.text(),
            'keep_structure': self._chk_keep_structure.isChecked() if hasattr(self, '_chk_keep_structure') else False,
            'preset_idx':     self._combo_preset.currentIndex() if hasattr(self, '_combo_preset') else 0,
            'do_mid':         self._chk_mid.isChecked(),
            'do_sep':         self._chk_sep.isChecked(),
            'do_auto':        self._chk_auto.isChecked(),
            'max_auto':       self._spin_auto.value(),
            'do_blank':       self._chk_blank.isChecked(),
            'max_blank':      self._spin_blank.value(),
            'lang_mode_idx':  self._combo_lang_mode.currentIndex() if hasattr(self, '_combo_lang_mode') else 0,
        }

    def apply_config(self, d: dict):
        if not d: return
        self._edit_odir.setText(d.get('out_dir', _CFG.get('output_dir', str(_OUTPUT_DIR))))
        if hasattr(self, '_chk_keep_structure'):
            self._chk_keep_structure.setChecked(d.get('keep_structure', False))
        if hasattr(self, '_combo_preset'):
            self._combo_preset.blockSignals(True)
            self._combo_preset.setCurrentIndex(d.get('preset_idx', 0))
            self._combo_preset.blockSignals(False)
        self._chk_mid.setChecked(d.get('do_mid', True))
        self._chk_sep.setChecked(d.get('do_sep', False))
        self._chk_auto.setChecked(d.get('do_auto', False))
        self._spin_auto.setValue(d.get('max_auto', 100))
        self._chk_blank.setChecked(d.get('do_blank', True))
        self._spin_blank.setValue(d.get('max_blank', 1))
        if hasattr(self, '_combo_lang_mode'):
            self._combo_lang_mode.setCurrentIndex(d.get('lang_mode_idx', 0))

    def refresh_btn_styles(self):
        # v1.0.6: re-apply drop-zone style on theme change
        if hasattr(self, '_drop_zone'): self._drop_zone.refresh_style()
        secondary_ss = (f"QPushButton{{background:{SURFACE};border:1.5px solid {BTN_BORDER_H};"
                        f"color:{TEXT};border-radius:8px;padding:5px 12px;}}"
                        f"QPushButton:hover{{background:{SRF2};border-color:{ACCENT};}}"
                        f"QPushButton:pressed{{background:{BTN_PRESSED};}}"
                        f"QPushButton:disabled{{background:{SRF2};color:{DISABLED};}}")
        for attr in ('_btn_del', '_btn_clr', '_btn_up', '_btn_dn', '_btn_abort'):
            if hasattr(self, attr): getattr(self, attr).setStyleSheet(secondary_ss)
        for attr in ('_btn_brw', '_btn_add', '_btn_add_folder'):
            if hasattr(self, attr): getattr(self, attr).setStyleSheet("")
        self._opt_bar.setStyleSheet(
            f"QWidget#tf_opt_bar{{background:{SRF2};border:1px solid {BORDER};"
            f"border-radius:8px;}}"
            f"QWidget#tf_opt_bar QComboBox{{background:{SRF2};border-color:{BORDER};}}"
            f"QWidget#tf_opt_bar QComboBox::drop-down{{background:{BORDER};}}")
        if hasattr(self, '_combo_lang_mode'):
            self._combo_lang_mode.setStyleSheet(
                f"QComboBox{{background:{SRF2};border:1.5px solid {BORDER};"
                f"border-radius:8px;color:{TEXT};"
                f"padding:2px 28px 2px 8px;font-size:13px;min-height:18px;}}"
                f"QComboBox:focus{{border-color:{ACCENT};}}"
                f"QComboBox:hover{{border-color:{INPUT_H};}}"
                f"QComboBox::drop-down{{subcontrol-origin:padding;"
                f"subcontrol-position:right center;width:24px;border:none;"
                f"border-left:1.5px solid {BORDER};"
                f"border-top-right-radius:8px;border-bottom-right-radius:8px;"
                f"background:{BORDER};}}"
                f"QComboBox::down-arrow{{image:{_combo_arrow_url(MUTED)};width:10px;height:6px;}}"
                f"QComboBox:hover::down-arrow{{image:{_combo_arrow_url(TEXT)};}}"
                f"QComboBox:focus::down-arrow{{image:{_combo_arrow_url(ACCENT)};}}")
        if hasattr(self, '_save_bar'):
            self._save_bar.setStyleSheet(
                f"QWidget#bulk_save_bar{{background:{SRF2};border:1px solid {BORDER};border-radius:8px;}}")
        if hasattr(self, '_lbl_save_desc'):
            self._lbl_save_desc.setStyleSheet(f"color:{MUTED};font-size:11px;background:transparent;")
        self._progress_bar.setStyleSheet(self._progress_ss())
        if hasattr(self, '_file_progress_bar'):
            self._file_progress_bar.setStyleSheet(
                f"QProgressBar{{border:none;background:{BORDER};border-radius:2px;}}"
                f"QProgressBar::chunk{{background:{ACCENT};border-radius:2px;opacity:0.7;}}")
        for lbl in ('_lbl_total_progress', '_lbl_file_progress'):
            if hasattr(self, lbl):
                getattr(self, lbl).setStyleSheet(
                    f"font-size:11px;color:{MUTED};"
                    f"font-family:'Consolas','Courier New','Menlo',monospace;")
        _isz = QSize(20,20)
        for attr, key in [('_btn_del','trash'),('_btn_clr','trash'),
                          ('_btn_up','arrow_up'),('_btn_dn','arrow_down')]:
            if hasattr(self, attr): getattr(self, attr).setIcon(_svg_icon(key, ACCENT)); getattr(self, attr).setIconSize(_isz)


class TextMergeWorker(QThread):
    """Background worker for reading merge files."""
    progress = Signal(int)          # 0–100
    done     = Signal(str, list)    # merged_text, enc_summary
    error    = Signal(str, str)     # title, message

    def __init__(self, file_list, enc_map, use_sep, extract_fn):
        super().__init__()
        self.file_list  = file_list
        self.enc_map    = enc_map
        self.use_sep    = use_sep
        self._extract   = extract_fn

    def run(self):
        _prevent_sleep()
        try:
            merged = []; enc_summary = []
            total = max(len(self.file_list), 1)
            for i, path in enumerate(self.file_list):
                self.progress.emit(int(i / total * 95))
                read_enc = self.enc_map.get(path, "utf-8")
                ext = os.path.splitext(path)[1].lower()
                try:
                    text = self._extract(
                        path,
                        enc=read_enc if ext not in (".docx", ".pdf", ".xlsx", ".hwpx") else "utf-8"
                    )
                    if self.use_sep:
                        sep = f"{'─'*60}\n▶ {os.path.basename(path)}\n{'─'*60}"
                        merged.append(f"{sep}\n{text}")
                    else:
                        merged.append(text)
                    enc_summary.append(f"  • {os.path.basename(path)}  ({read_enc.upper()})")
                    _glog(f"  ✅ [Text Merger] Read: {os.path.basename(path)}")
                except ImportError as e:
                    self.error.emit(_t('dlg_error_title'), str(e)); return
                except Exception as e:
                    self.error.emit(_t('dlg_error_title'),
                                    f"{os.path.basename(path)}\n{e}"); return
            self.progress.emit(100)
            self.done.emit("\n".join(merged), enc_summary)
        finally:
            _allow_sleep()


class TextMergerPanel(QWidget):
    SUPPORTED_EXT={".txt",".md",".csv",".log",".json",".xml",".html",".py",".docx",".pdf",".xlsx",".hwpx"}
    # v1.0.5: save-encoding dropdown (internal key, i18n key) mapping
    # — internal key is the existing value used for codec mapping / settings storage (was currentText through v1.0.4)
    # — i18n key is used per language to fetch the displayed label (e.g. extension point for 'UTF-8 (recommended)' style)
    # Order = combobox display order (preserves v1.0.4 indices 0~7 for compatibility)
    _ENC_ITEMS = [
        ("UTF-8",     'merge_enc_utf8'),
        ("UTF-8-BOM", 'merge_enc_utf8_bom'),
        ("EUC-KR",    'merge_enc_euckr'),
        ("CP949",     'merge_enc_cp949'),
        ("UTF-16",    'merge_enc_utf16'),
        ("Shift-JIS", 'merge_enc_shiftjis'),
        ("GBK",       'merge_enc_gbk'),
        ("Big5",      'merge_enc_big5'),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_list=[]; self.enc_map={}; self.enc_confidence={}; self.line_cache={}; self.save_dir=""; self._undo_data=None
        self._merge_worker=None
        self._build()

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)

        # ── Divider (consistent with other panels) ─
        sep = QFrame(); sep.setFrameShape(QFrame.HLine); sep.setObjectName("tab_sep")
        root.addWidget(sep)

        # ── Two-column body ─────────────────────────
        body = QWidget()
        body_lay = QHBoxLayout(body)
        body_lay.setContentsMargins(14, 12, 14, 12); body_lay.setSpacing(14)

        # ══ Left: file list ═════════════════════════
        left = QWidget()
        ll = QVBoxLayout(left); ll.setContentsMargins(0, 0, 0, 0); ll.setSpacing(6)

        # ── Drop zone ──────────────────────────
        self._drop_zone = MergeDropZone()
        self._drop_zone.setObjectName("mergeDropZone")
        self._drop_zone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._drop_zone.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._drop_zone.setMinimumHeight(130); self._drop_zone.setMaximumHeight(130)
        self._drop_zone.setTextFormat(Qt.TextFormat.RichText)
        self._drop_zone.files_dropped.connect(self._add_file_paths)
        self._refresh_drop_zone()
        ll.addWidget(self._drop_zone)

        # ── Top button row ─────────────────────
        top_btn_row = QHBoxLayout(); top_btn_row.setSpacing(6)
        self._btn_add = QPushButton(_t('btn_add_file'))
        self._btn_add.setObjectName("btn_primary"); self._btn_add.setFixedHeight(36); self._btn_add.setMinimumWidth(90)
        self._btn_add.setIcon(_svg_icon('document', 'white')); self._btn_add.setIconSize(QSize(20,20))
        self._btn_add.clicked.connect(self._add_files_dialog)
        self._btn_add_folder = QPushButton(_t('btn_add_folder'))
        self._btn_add_folder.setObjectName("btn_folder_add"); self._btn_add_folder.setFixedHeight(36); self._btn_add_folder.setMinimumWidth(90)
        self._btn_add_folder.setIcon(_svg_icon('folder_open', 'white')); self._btn_add_folder.setIconSize(QSize(20,20))
        self._btn_add_folder.clicked.connect(self._add_folder_dialog)
        self._btn_del_all = QPushButton(_t('btn_del_all')); self._btn_del_all.setFixedHeight(36); self._btn_del_all.setMinimumWidth(80)
        self._btn_del_all.setIcon(_svg_icon('trash', ACCENT)); self._btn_del_all.setIconSize(QSize(20,20))
        self._btn_del_all.clicked.connect(self._delete_all)
        top_btn_row.addWidget(self._btn_add)
        top_btn_row.addWidget(self._btn_add_folder)
        top_btn_row.addStretch()
        top_btn_row.addWidget(self._btn_del_all)
        ll.addLayout(top_btn_row)

        # ── File tree (sortable via header click) ─
        self._sort_asc = False  # Initialize to False so the first click sorts ascending
        self._tree = MergeFileTree()
        self._tree.setItemDelegateForColumn(0, MergeEncodingDelegate(self._tree))
        self._tree.files_dropped.connect(self._add_file_paths)
        self._tree.order_changed.connect(self._sync_after_drag)
        self._tree.itemSelectionChanged.connect(self._update_sel_label)
        # sectionClicked: fires on click release (may conflict with DragDrop mode in some environments)
        # sectionPressed: fires immediately on click — connect both signals to ensure reliable behavior
        self._tree.header().sectionClicked.connect(lambda _: self._sort_files())
        self._tree.header().setSortIndicatorShown(True)
        self._tree.header().setSectionsClickable(True)  # Prevent click deactivation when setSortingEnabled(False)
        ll.addWidget(self._tree, stretch=1)

        # Folder-scan progress bar (hidden in normal state)
        self._scan_bar = QProgressBar()
        self._scan_bar.setRange(0, 100); self._scan_bar.setValue(0)
        self._scan_bar.setFixedHeight(5); self._scan_bar.setTextVisible(False)
        self._scan_bar.setStyleSheet(
            f"QProgressBar{{border:none;background:{BORDER};border-radius:2px;}}"
            f"QProgressBar::chunk{{background:{ACCENT};border-radius:2px;opacity:0.7;}}")
        self._scan_bar.setVisible(False)
        ll.addWidget(self._scan_bar)
        self._scan_lbl = QLabel("")
        self._scan_lbl.setStyleSheet(
            f"font-size:11px;color:{MUTED};"
            f"font-family:'Consolas','Courier New','Menlo',monospace;")
        self._scan_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._scan_lbl.setFixedHeight(16)
        self._scan_lbl.setVisible(False)
        ll.addWidget(self._scan_lbl)
        self._scan_worker = None
        bot_btn_row = QHBoxLayout(); bot_btn_row.setSpacing(6)
        self._btn_del = QPushButton(_t('btn_del_sel')); self._btn_del.setFixedHeight(36); self._btn_del.setMinimumWidth(80)
        self._btn_del.setIcon(_svg_icon('trash', ACCENT)); self._btn_del.setIconSize(QSize(20,20))
        self._btn_del.clicked.connect(self._delete_selected)
        self._btn_up = QPushButton(_t('btn_up')); self._btn_up.setFixedHeight(36); self._btn_up.setMinimumWidth(70)
        self._btn_up.setIcon(_svg_icon('arrow_up', ACCENT)); self._btn_up.setIconSize(QSize(16,16))
        self._btn_up.clicked.connect(self._move_up)
        self._btn_dn = QPushButton(_t('btn_down')); self._btn_dn.setFixedHeight(36); self._btn_dn.setMinimumWidth(70)
        self._btn_dn.setIcon(_svg_icon('arrow_down', ACCENT)); self._btn_dn.setIconSize(QSize(16,16))
        self._btn_dn.clicked.connect(self._move_down)
        bot_btn_row.addWidget(self._btn_del)
        bot_btn_row.addWidget(self._btn_up)
        bot_btn_row.addWidget(self._btn_dn)
        bot_btn_row.addStretch()
        self._lbl_selection = QLabel(_t("merge_sel_none"))
        self._lbl_selection.setStyleSheet(f"font-size:12px;color:{MUTED};")
        bot_btn_row.addWidget(self._lbl_selection)
        ll.addLayout(bot_btn_row)

        body_lay.addWidget(left, stretch=3)

        # ══ Right: settings + actions ═══════════════
        right = QWidget()
        rl = QVBoxLayout(right); rl.setContentsMargins(0, 0, 0, 0); rl.setSpacing(10)

        # ── Save settings GroupBox ──────────────────
        save_gb = QGroupBox(_t("merge_save_settings")); self._save_gb=save_gb
        sg = QVBoxLayout(save_gb); sg.setContentsMargins(10, 6, 10, 8); sg.setSpacing(8)

        enc_row = QHBoxLayout(); enc_row.setSpacing(8)
        self._lbl_enc=QLabel(_t("conv_save_enc")); self._lbl_enc.setObjectName("field_lbl"); enc_row.addWidget(self._lbl_enc)
        self._combo_enc = _ThemedCombo()
        # v1.0.5: separate internal key + display label (preserve old key in userData → automatic settings compatibility)
        for _enc_key, _i18n_key in self._ENC_ITEMS:
            self._combo_enc.addItem(_t(_i18n_key), _enc_key)
        enc_row.addWidget(self._combo_enc, stretch=1)
        self._combo_enc.setFixedHeight(30)
        self._combo_enc.setStyleSheet(
            f"QComboBox{{background:{SURFACE};border:1.5px solid {BORDER};"
            f"border-radius:8px;color:{TEXT};"
            f"padding:3px 28px 3px 10px;font-size:13px;min-height:18px;}}"
            f"QComboBox:focus{{border-color:{ACCENT};}}"
            f"QComboBox:hover{{border-color:{INPUT_H};}}"
            f"QComboBox::drop-down{{subcontrol-origin:padding;"
            f"subcontrol-position:right center;width:26px;border:none;"
            f"border-left:1px solid {BORDER};"
            f"border-top-right-radius:8px;border-bottom-right-radius:8px;"
            f"background:{SRF2};}}"
            f"QComboBox::down-arrow{{image:{_combo_arrow_url(MUTED)};width:10px;height:6px;}}"
            f"QComboBox:hover::down-arrow{{image:{_combo_arrow_url(TEXT)};}}"
            f"QComboBox:focus::down-arrow{{image:{_combo_arrow_url(ACCENT)};}}")
        sg.addLayout(enc_row)

        # v1.0.6: save-encoding auto-recommendation row (label + apply button)
        # - 0 files: show legacy hint ("If unsure, choose UTF-8")
        # - 1+ files: show "💡 Recommended: XXX" + [Apply] button
        rec_row = QHBoxLayout(); rec_row.setSpacing(6); rec_row.setContentsMargins(2, 0, 0, 0)
        # v1.0.5 variable name preserved (_lbl_enc_hint) → semantic extension: hint OR recommendation label
        self._lbl_enc_hint = QLabel(_t('merge_enc_hint'))
        self._lbl_enc_hint.setStyleSheet(f"color:{MUTED};font-size:11px;")
        self._lbl_enc_hint.setWordWrap(True)
        rec_row.addWidget(self._lbl_enc_hint, stretch=1)
        # v1.0.6 new: recommendation Apply button (hidden when 0 files)
        self._btn_enc_recommend_apply = QPushButton(_t('merge_enc_recommend_apply'))
        self._btn_enc_recommend_apply.setCursor(Qt.PointingHandCursor)
        self._btn_enc_recommend_apply.setFixedHeight(22)
        self._btn_enc_recommend_apply.setStyleSheet(
            f"QPushButton{{background:{ACCENT};color:white;border:none;"
            f"border-radius:4px;padding:2px 10px;font-size:11px;font-weight:600;}}"
            f"QPushButton:hover{{background:{INPUT_H};}}"
            f"QPushButton:disabled{{background:{DISABLED};color:{MUTED};}}")
        self._btn_enc_recommend_apply.clicked.connect(self._apply_enc_recommendation)
        self._btn_enc_recommend_apply.setVisible(False)  # Initially 0 files → hidden
        rec_row.addWidget(self._btn_enc_recommend_apply)
        sg.addLayout(rec_row)

        # v1.0.6: cache the currently recommended encoding key (referenced by Apply button)
        self._current_recommendation = None

        self._lbl_path_label=QLabel(_t("merge_save_path")); self._lbl_path_label.setObjectName("field_lbl"); sg.addWidget(self._lbl_path_label)
        self._lbl_save_path = QLabel(_t("merge_path_none"))
        self._lbl_save_path.setStyleSheet(f"color:{TEXT};font-size:13px;")
        self._lbl_save_path.setWordWrap(True); self._lbl_save_path.setMinimumHeight(18)
        sg.addWidget(self._lbl_save_path)
        path_row = QHBoxLayout(); path_row.setSpacing(6)
        self._btn_browse = QPushButton(_t("merge_path_pick"))
        self._btn_browse.clicked.connect(self._browse_save_path)
        self._btn_clear_path = QPushButton(_t("merge_path_reset"))
        self._btn_clear_path.clicked.connect(self._clear_save_path)
        path_row.addWidget(self._btn_browse); path_row.addWidget(self._btn_clear_path); path_row.addStretch()
        sg.addLayout(path_row)

        self._chk_sep = QCheckBox(_t("merge_sep")); sg.addWidget(self._chk_sep)
        rl.addWidget(save_gb)

        # ── File statistics ─────────────────────────
        self._lbl_stats = QLabel(_t("merge_stats", n=0, lines=0))
        self._lbl_stats.setObjectName("count_lbl"); rl.addWidget(self._lbl_stats)

        rl.addSpacing(12)

        # ── Merge button + status ───────────────────
        self._btn_merge = QPushButton(_t("merge_btn")); self._btn_merge.setObjectName("btn_merge")
        self._btn_merge.setObjectName("btn_merge"); self._btn_merge.setFixedHeight(50)
        self._btn_merge.setIcon(_svg_icon('save', 'white')); self._btn_merge.setIconSize(QSize(22,22))
        self._btn_merge.clicked.connect(self._merge_files); rl.addWidget(self._btn_merge)

        self._btn_undo = QPushButton(_t('btn_undo')); self._btn_undo.setObjectName("btn_undo")
        self._btn_undo.setFixedHeight(44); self._btn_undo.setEnabled(False)
        self._btn_undo.clicked.connect(self._undo); rl.addWidget(self._btn_undo)

        self._pb = QProgressBar()
        self._pb.setRange(0, 100); self._pb.setValue(0)
        self._pb.setTextVisible(False); self._pb.setFixedHeight(5)
        self._pb.setVisible(False)
        self._pb.setStyleSheet(
            f"QProgressBar{{border:none;background:{BORDER};border-radius:2px;}}"
            f"QProgressBar::chunk{{background:{ACCENT};border-radius:2px;}}")
        rl.addWidget(self._pb)
        self._lbl_status = QLabel(_t("merge_status_ready"))
        self._lbl_status.setStyleSheet("font-size:13px;"); rl.addWidget(self._lbl_status)

        body_lay.addWidget(right, stretch=2)
        root.addWidget(body, stretch=1)

    # v1.0.4: removed _detect_encoding() — unified into alchemy_detect_encoding.
    # Previously: BOM detection + chardet (32768 bytes, threshold 0.5)
    # After unification: alchemy_detect_encoding absorbs all behavior (CJK whitelist, normalization, threshold separation)

    def _extract_text(self,path,enc="utf-8"):
        ext=os.path.splitext(path)[1].lower()
        if ext==".docx":
            if not DOCX_AVAILABLE: raise ImportError(_t('lib_required_msg', lib='python-docx'))
            doc=_docx.Document(path); return "\n".join(p.text for p in doc.paragraphs)
        elif ext==".pdf":
            if not PDF_AVAILABLE: raise ImportError(_t('lib_required_msg', lib='pdfplumber'))
            with pdfplumber.open(path) as pdf: pages=[page.extract_text() or "" for page in pdf.pages]
            return "\n".join(pages)
        elif ext==".xlsx":
            if not XLSX_AVAILABLE: raise ImportError(_t('lib_required_msg', lib='openpyxl'))
            wb=openpyxl.load_workbook(path,read_only=True,data_only=True); lines=[]
            for sheet in wb.worksheets:
                lines.append(f"[{sheet.title}]")
                for row in sheet.iter_rows(values_only=True): lines.append("\t".join("" if v is None else str(v) for v in row))
            return "\n".join(lines)
        elif ext==".hwpx":
            # v1.0.6: HWPX (KS X 6101 OWPML) plain-text extraction
            if not HWPX_AVAILABLE: raise ImportError(_t('lib_required_msg', lib='python-hwpx'))
            with _hwpx.HwpxDocument.open(path) as doc: return doc.export_text()
        else:
            with open(path,"r",encoding=enc,errors="replace") as f: return f.read()

    def _refresh_drop_zone(self):
        t = _T
        self._drop_zone.setStyleSheet(
            f"QLabel#mergeDropZone{{border:1.5px dashed {t['BORDER']};"
            f"border-radius:10px;background:{t['SURFACE']};padding:12px;}}")
        self._drop_zone.setWordWrap(True)
        self._drop_zone.setText(
            f"<div style='text-align:center;'>"
            f"<div style='font-size:24px;'>📋</div>"
            f"<div style='color:{t['MUTED']};font-size:13px;margin-top:4px;'>{_t('merge_drop')}</div>"
            f"<div style='color:{t['DISABLED']};font-size:13px;margin-top:4px;'>txt · md · csv · docx · pdf · xlsx · hwpx {_t('merge_ext_supported')}</div>"
            f"</div>")

    def _add_files_dialog(self):
        files,_=QFileDialog.getOpenFileNames(self,_t('btn_add_file'),"","Supported Files (*.txt *.md *.csv *.log *.json *.xml *.html *.py *.docx *.pdf *.xlsx *.hwpx);;All Files (*)")
        self._add_file_paths(files)

    def _add_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(self, _t('btn_add_folder'))
        if not folder: return
        if self._scan_worker and self._scan_worker.isRunning():
            try:
                self._scan_worker.sig_progress.disconnect()
                self._scan_worker.sig_found.disconnect()
                self._scan_worker.sig_done.disconnect()
                self._scan_worker.sig_error.disconnect()
            except Exception: pass
            self._scan_worker.abort(); self._scan_worker.wait(1000)
        self._set_scan_ui(True)
        self._scan_worker = FolderScanWorker(
            folder, exts=self.SUPPORTED_EXT, recursive=True)
        self._scan_worker.sig_progress.connect(self._scan_bar.setValue)
        self._scan_worker.sig_found.connect(
            lambda n: self._scan_lbl.setText(_t('bulk_scanning', n=n)))
        self._scan_worker.sig_done.connect(self._on_scan_done)
        self._scan_worker.sig_error.connect(self._on_scan_error)
        self._scan_worker.start()

    def _set_scan_ui(self, scanning: bool):
        self._scan_bar.setVisible(scanning)
        self._scan_bar.setValue(0)
        self._scan_lbl.setVisible(scanning)
        if not scanning: self._scan_lbl.setText("")
        for btn in (self._btn_add, self._btn_add_folder, self._btn_del_all,
                    self._btn_del, self._btn_up, self._btn_dn, self._btn_merge):
            btn.setEnabled(not scanning)
        if scanning:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        else:
            QApplication.restoreOverrideCursor()

    def _on_scan_done(self, paths: list):
        self._set_scan_ui(False)
        if not paths:
            _dlg_warn(self, _t('dlg_ok'), _t('merge_no_support')); return
        self._add_file_paths(paths)

    def _on_scan_error(self, msg: str):
        self._set_scan_ui(False)
        _dlg_error(self, _t('dlg_error_title'), msg)

    def _add_files_from_folder(self, folder):
        """Handle dropped folder — delegate directly to the worker."""
        if self._scan_worker and self._scan_worker.isRunning():
            try:
                self._scan_worker.sig_progress.disconnect()
                self._scan_worker.sig_found.disconnect()
                self._scan_worker.sig_done.disconnect()
                self._scan_worker.sig_error.disconnect()
            except Exception: pass
            self._scan_worker.abort(); self._scan_worker.wait(1000)
        self._set_scan_ui(True)
        self._scan_worker = FolderScanWorker(
            folder, exts=self.SUPPORTED_EXT, recursive=True)
        self._scan_worker.sig_progress.connect(self._scan_bar.setValue)
        self._scan_worker.sig_found.connect(
            lambda n: self._lbl_status.setText(_t('bulk_scanning', n=n)))
        self._scan_worker.sig_done.connect(self._on_scan_done)
        self._scan_worker.sig_error.connect(self._on_scan_error)
        self._scan_worker.start()

    def _add_file_paths(self,paths):
        added=0; expanded=[]; hwp_legacy_count=0  # v1.0.6: legacy HWP count
        for path in paths:
            if not path: continue
            if os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for fname in sorted(files):
                        fext = os.path.splitext(fname)[1].lower()
                        if fext in self.SUPPORTED_EXT:
                            expanded.append(os.path.join(root, fname))
                        elif fext == ".hwp":  # v1.0.6: detect legacy HWP inside folder
                            hwp_legacy_count += 1
            else:
                expanded.append(path)
                # v1.0.6: count directly added .hwp files (before SUPPORTED_EXT check)
                if os.path.splitext(path)[1].lower() == ".hwp":
                    hwp_legacy_count += 1
        for path in expanded:
            if not os.path.isfile(path): continue
            if os.path.splitext(path)[1].lower() not in self.SUPPORTED_EXT: continue
            if path in self.file_list: continue
            ext=os.path.splitext(path)[1].lower()
            if ext in (".docx",".pdf",".xlsx",".hwpx"):
                enc=ext[1:].upper(); conf=1.0
            else:
                enc, conf = alchemy_detect_encoding(path)
            self.enc_map[path]=enc; self.enc_confidence[path]=conf; self.file_list.append(path)
            if ext in (".docx",".pdf",".xlsx",".hwpx"): self.line_cache[path]=0
            else:
                try:
                    with open(path,"r",encoding=enc,errors="replace") as _f: self.line_cache[path]=sum(1 for _ in _f)
                except Exception: self.line_cache[path]=0
            lines=self.line_cache[path]
            item=QTreeWidgetItem([os.path.basename(path), os.path.dirname(path)])
            # v1.0.4: if confidence is below 90%, append a chardet hint to the tooltip (text files only)
            tip = path
            if ext not in (".docx",".pdf",".xlsx",".hwpx") and 0 < conf < 0.90:
                tip = f"{path}\n\n{_t('merge_low_conf_hint')}"
            item.setToolTip(0, tip)
            item.setData(0, MergeEncodingDelegate._BADGE_ROLE, enc)
            item.setData(0, MergeEncodingDelegate._CONF_ROLE,  conf)
            item.setData(0, MergeEncodingDelegate._LINES_ROLE, lines)
            item.setData(0, MergeEncodingDelegate._PATH_ROLE,  path)  # v1.0.6: pure path
            self._tree.addTopLevelItem(item); added+=1
        if added:
            self._update_stats(); self._lbl_status.setText(_t('merge_status_add', n=added))
            self._refresh_recommendation()  # v1.0.6: refresh recommendation
            _glog(f"📋 [Text Merger] Added {added} files (total {len(self.file_list)})")
        # v1.0.6: if legacy HWP files were present, show one consolidated dialog (encourages HWPX conversion)
        if hwp_legacy_count > 0:
            _glog(f"⚠ [Text Merger] Skipped {hwp_legacy_count} legacy HWP files — HWPX conversion notice shown")
            _dlg_warn(self, _t('merge_hwp_legacy_title'),
                      _t('merge_hwp_legacy_msg', n=hwp_legacy_count), rich_text=True)

    def _delete_selected(self):
        items=self._tree.selectedItems()
        if not items: return
        for item in items:
            # v1.0.6: read pure path from _PATH_ROLE instead of tooltip (fixes tooltip-pollution bug for low-confidence files)
            path = item.data(0, MergeEncodingDelegate._PATH_ROLE)
            if not path:  # Fallback: when _PATH_ROLE is missing (legacy paths, defensive handling)
                path = item.toolTip(0).split("\n\n", 1)[0]
            self.enc_map.pop(path,None); self.enc_confidence.pop(path,None); self.line_cache.pop(path,None)
            idx=self._tree.indexOfTopLevelItem(item); self._tree.takeTopLevelItem(idx)
            if path in self.file_list: self.file_list.remove(path)
        self._update_stats(); self._lbl_status.setText(_t('merge_status_del', n=len(items)))
        self._refresh_recommendation()  # v1.0.6: refresh recommendation

    def _delete_all(self):
        if not self.file_list: return
        if _dlg_question(self, _t('dlg_confirm_title'), _t('merge_clr_confirm')):
            self._tree.clear(); self.file_list.clear(); self.enc_map.clear()
            self.enc_confidence.clear(); self.line_cache.clear()
            self._update_stats(); self._lbl_status.setText(_t('merge_status_clr'))
            self._refresh_recommendation()  # v1.0.6: refresh recommendation (0 files → revert to hint display)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete: self._delete_selected()

    def _update_sel_label(self):
        def short(text, mx=20): return text if len(text)<=mx else text[:mx-1]+"…"
        selected=self._tree.selectedItems()
        if not selected: self._lbl_selection.setText(_t("merge_sel_none"))
        elif len(selected)==1: self._lbl_selection.setText(_t("merge_sel_one", name=short(selected[0].text(0),40)))
        else:
            names=", ".join(short(i.text(0)) for i in selected[:2])
            suffix=f" +{len(selected)-2} more" if len(selected)>2 else ""
            self._lbl_selection.setText(_t("merge_sel_multi", n=len(selected), names=names, more=suffix))

    def _move_up(self):
        rows=sorted([self._tree.indexOfTopLevelItem(i) for i in self._tree.selectedItems()])
        if not rows or rows[0]==0: return
        for row in rows: self._swap_rows(row, row-1)
        self._tree.clearSelection()
        for row in rows: self._tree.topLevelItem(row-1).setSelected(True)

    def _move_down(self):
        rows=sorted([self._tree.indexOfTopLevelItem(i) for i in self._tree.selectedItems()])
        if not rows or rows[-1]==self._tree.topLevelItemCount()-1: return
        for row in reversed(rows): self._swap_rows(row, row+1)
        self._tree.clearSelection()
        for row in rows: self._tree.topLevelItem(row+1).setSelected(True)

    def _swap_rows(self, i, j):
        self.file_list[i],self.file_list[j]=self.file_list[j],self.file_list[i]
        item=self._tree.takeTopLevelItem(i); self._tree.insertTopLevelItem(j, item)

    def _sync_after_drag(self):
        # v1.0.6: use _PATH_ROLE instead of tooltip (fixes tooltip-pollution bug for low-confidence files)
        def _get_path(it):
            p = it.data(0, MergeEncodingDelegate._PATH_ROLE)
            return p if p else it.toolTip(0).split("\n\n", 1)[0]
        new_list = [_get_path(self._tree.topLevelItem(i))
                    for i in range(self._tree.topLevelItemCount())]
        self.file_list = new_list
        self._update_stats()

    def _sort_files(self):
        if self._tree.topLevelItemCount() == 0: return
        self._sort_asc = not self._sort_asc
        order = Qt.SortOrder.AscendingOrder if self._sort_asc else Qt.SortOrder.DescendingOrder
        self._tree.header().setSortIndicator(0, order)
        self.file_list.sort(key=natural_sort_key, reverse=not self._sort_asc)
        self._tree.clear()
        for path in self.file_list:
            item = QTreeWidgetItem([os.path.basename(path), os.path.dirname(path)])
            enc = self.enc_map.get(path, 'utf-8')
            conf = self.enc_confidence.get(path, 0.0)
            lines = self.line_cache.get(path, 0)
            # v1.0.6: append hint note to low-confidence text files (same logic as add-file flow)
            ext = os.path.splitext(path)[1].lower()
            tip = path
            if ext not in (".docx",".pdf",".xlsx",".hwpx") and 0 < conf < 0.90:
                tip = f"{path}\n\n{_t('merge_low_conf_hint')}"
            item.setToolTip(0, tip)
            item.setData(0, MergeEncodingDelegate._BADGE_ROLE, enc)
            item.setData(0, MergeEncodingDelegate._CONF_ROLE, conf)
            item.setData(0, MergeEncodingDelegate._LINES_ROLE, lines)
            item.setData(0, MergeEncodingDelegate._PATH_ROLE, path)  # v1.0.6: pure path
            self._tree.addTopLevelItem(item)
        self._update_stats()

    def _update_stats(self):
        total=sum(self.line_cache.get(p,0) for p in self.file_list)
        self._lbl_stats.setText(_t("merge_stats", n=len(self.file_list), lines=f"{total:,}"))

    def _browse_save_path(self):
        folder=QFileDialog.getExistingDirectory(self,_t("merge_path_pick"),self.save_dir or os.path.expanduser("~"))
        if folder:
            self.save_dir=folder; self._lbl_save_path.setText(folder); self._lbl_save_path.setToolTip(folder)
            self._lbl_status.setText(_t('merge_path_set', path=folder))

    def _clear_save_path(self):
        self.save_dir=""; self._lbl_save_path.setText(_t('merge_path_none')); self._lbl_status.setText(_t('merge_path_reset_done'))

    # v1.0.6: Auto-recommendation feature ──────────────────
    def _refresh_recommendation(self):
        """Refresh auto-recommendation on file add/remove/language switch (A1'' policy)."""
        if not self.file_list:
            # 0 files: show legacy hint (preserve v1.0.5 behavior) + hide Apply button
            self._lbl_enc_hint.setText(_t('merge_enc_hint'))
            self._btn_enc_recommend_apply.setVisible(False)
            self._current_recommendation = None
            return
        rec_key, rec_label = merger_recommend_save_encoding(
            self.enc_map, self.enc_confidence)
        self._current_recommendation = rec_key
        self._lbl_enc_hint.setText(_t('merge_enc_recommend', enc=rec_label))
        self._btn_enc_recommend_apply.setVisible(True)

    def _apply_enc_recommendation(self):
        """Apply the recommended encoding to the dropdown (new in v1.0.6)."""
        if not self._current_recommendation: return
        idx = self._combo_enc.findData(self._current_recommendation)
        if idx >= 0:
            self._combo_enc.setCurrentIndex(idx)
            _glog(f"💡 [Text Merger] Recommended encoding applied: {self._current_recommendation}")

    def _merge_files(self):
        if not self.file_list: _dlg_warn(self, _t('dlg_warning'), _t('merge_no_files')); return
        if self._merge_worker and self._merge_worker.isRunning(): return
        # v1.0.5: get internal key from userData (compatible with existing codec mapping regardless of display label)
        self._save_enc = self._combo_enc.currentData() or self._combo_enc.currentText()
        _glog(f"▶ [Text Merger] Merge started — {len(self.file_list)} files")
        self._btn_merge.setEnabled(False)
        self._pb.setValue(0); self._pb.setVisible(True)
        self._lbl_status.setText(_t('merge_reading'))
        self._merge_worker = TextMergeWorker(
            list(self.file_list), dict(self.enc_map),
            self._chk_sep.isChecked(), self._extract_text
        )
        self._merge_worker.progress.connect(self._pb.setValue)
        self._merge_worker.done.connect(self._on_merge_done)
        self._merge_worker.error.connect(self._on_merge_error)
        self._merge_worker.start()

    def _on_merge_done(self, merged_text, enc_summary):
        """Read complete — show save dialog (main thread)."""
        self._pb.setVisible(False)
        self._btn_merge.setEnabled(True)
        save_enc = self._save_enc
        # v1.0.4: added codec mapping for CJK encodings
        _enc_codec = {"UTF-8-BOM": "utf-8-sig",
                      "Shift-JIS": "shift_jis",
                      "GBK": "gbk",
                      "Big5": "big5"}.get(save_enc, save_enc)
        default = os.path.join(self.save_dir, "merged.txt") if self.save_dir else os.path.join(_CFG.get('output_dir', str(_OUTPUT_DIR)), "merged.txt")
        save_path, _ = QFileDialog.getSaveFileName(
            self, _t('dlg_done'), default, "Text Files (*.txt);;All Files (*)"
        )
        if not save_path:
            self._lbl_status.setText(_t('merge_status_ready')); return
        # v1.0.4: pre-save encoding compatibility check — warn when characters would be corrupted
        save_errors = 'strict'
        has_loss, bad_kinds, bad_total, total_chars, samples = alchemy_check_encoding_compat(merged_text, _enc_codec)
        if has_loss:
            sample_str = html.escape(' '.join(samples)) if samples else ''
            pct = bad_total * 100 // total_chars if total_chars else 0
            warn_msg = _t('merge_enc_warn_msg',
                          enc=save_enc, kinds=bad_kinds, total=bad_total,
                          pct=pct, samples=sample_str)
            if not _dlg_question(self, _t('merge_enc_warn_title'), warn_msg, min_width=460, rich_text=True):
                _glog(f"  ⚠ [Text Merger] Save canceled (encoding compatibility warning): {save_enc}, {bad_kinds} kinds / {bad_total} chars ({pct}%) loss expected")
                self._lbl_status.setText(_t('merge_status_ready')); return
            save_errors = 'replace'  # User consent → replace with ? on save
            _glog(f"  ⚠ [Text Merger] Save proceeded ignoring compatibility warning: {save_enc}, {bad_total} chars replaced with ?")
        try:
            with open(save_path, "w", encoding=_enc_codec, errors=save_errors) as f: f.write(merged_text)
            _glog(f"  ✅ [Text Merger] Saved: {save_path}  ({save_enc})")
            self._undo_data = ('file', save_path)
            self._btn_undo.setEnabled(True)
            msg = (f"✅ {_t('dlg_done')} ({save_enc})\n{save_path}"
                   f"\n\nEncoding:\n{chr(10).join(enc_summary)}")
            if _dlg_info_action(self, _t('dlg_done'), msg, _t('merge_open_explorer')):
                subprocess.Popen(
                    f'explorer /select,"{os.path.normpath(save_path)}"',
                    shell=True)
            self._lbl_status.setText(_t('merge_save_done', enc=save_enc, path=save_path))
        except Exception as e:
            _glog(f"  ❌ [Text Merger] Save failed: {e}")
            _dlg_error(self, _t('dlg_save_err'), str(e))

    def _on_merge_error(self, title, msg):
        """Read error."""
        self._pb.setVisible(False)
        self._btn_merge.setEnabled(True)
        self._lbl_status.setText(_t('merge_save_err'))
        _glog(f"  ❌ [Text Merger] {title}: {msg}")
        _dlg_error(self, title, msg)


    def is_busy(self) -> bool:
        """True if the merge worker is running."""
        return bool(self._merge_worker and self._merge_worker.isRunning())

    def _stop_worker(self):
        if self._merge_worker and self._merge_worker.isRunning():
            try:
                self._merge_worker.done.disconnect()
                self._merge_worker.error.disconnect()
                self._merge_worker.progress.disconnect()
            except Exception:
                pass
            self._merge_worker.quit()
            if not self._merge_worker.wait(2000):
                self._merge_worker.terminate(); self._merge_worker.wait(500)
        if self._scan_worker and self._scan_worker.isRunning():
            self._scan_worker.abort(); self._scan_worker.wait(1000)
            self._set_scan_ui(False)

    def _undo(self):
        """Restore by deleting the last merged file."""
        if not self._undo_data: return
        kind, path = self._undo_data
        _glog(f"↩ [Text Merger] Undo — {path}")
        try:
            if os.path.exists(path):
                os.remove(path)
                self._undo_data = None
                self._btn_undo.setEnabled(False)
                self._lbl_status.setText(_t('merge_status_ready'))
                _glog(f"  ✅ File deleted: {path}")
                _dlg_info(self, _t('dlg_undo'), f"{_t('merge_undo_done')}\n{path}")
            else:
                _dlg_warn(self, _t('dlg_undo'), f"{_t('merge_undo_miss')}\n{path}")
                self._undo_data = None
                self._btn_undo.setEnabled(False)
        except OSError as e:
            _glog(f"  ❌ Delete failed: {e}")
            _dlg_error(self, _t('dlg_undo_fail'), str(e))

    def refresh_btn_styles(self):
        """Refresh buttons that the QSS cascade does not reach on theme switch."""
        if hasattr(self, '_pb'):
            self._pb.setStyleSheet(
                f"QProgressBar{{border:none;background:{BORDER};border-radius:2px;}}"
                f"QProgressBar::chunk{{background:{ACCENT};border-radius:2px;}}")
        secondary_ss = (f"QPushButton{{background:{SURFACE};border:1.5px solid {BTN_BORDER_H};"
                        f"color:{TEXT};border-radius:8px;padding:5px 12px;}}"
                        f"QPushButton:hover{{background:{SRF2};border-color:{ACCENT};}}"
                        f"QPushButton:pressed{{background:{BTN_PRESSED};}}"
                        f"QPushButton:disabled{{background:{SRF2};color:{DISABLED};}}")
        for attr in ('_btn_browse', '_btn_clear_path',
                     '_btn_del', '_btn_del_all', '_btn_up', '_btn_dn'):
            if hasattr(self, attr): getattr(self, attr).setStyleSheet(secondary_ss)
        if hasattr(self, '_btn_undo'): self._btn_undo.setStyleSheet(secondary_ss)
        # _btn_add / _btn_add_folder use objectName QSS (btn_primary / btn_folder_add) —
        # applying secondary_ss directly would invalidate the QSS, so we only reset stylesheet
        for attr in ('_btn_add', '_btn_add_folder'):
            if hasattr(self, attr): getattr(self, attr).setStyleSheet("")
        # Refresh SVG icon colors
        _isz = QSize(20,20)
        for attr, key in [('_btn_del','trash'),('_btn_del_all','trash'),
                          ('_btn_up','arrow_up'),('_btn_dn','arrow_down')]:
            if hasattr(self, attr): getattr(self, attr).setIcon(_svg_icon(key, ACCENT)); getattr(self, attr).setIconSize(_isz)
        # Refresh combobox inline style
        if hasattr(self, '_combo_enc'): self._combo_enc.setStyleSheet(_themed_combo_ss())
        # Refresh drop zone
        if hasattr(self, '_refresh_drop_zone'): self._refresh_drop_zone()

    # ── v1.0.5: status-message re-translation helpers ─────────
    def _match_status_template(self, text, key):
        """Check whether the current _lbl_status text matches one of the templates of a translation key.
        Placeholders ({n}, {path}, {enc}, etc.) are converted to `.+?` for regex matching.

        Args:
            text: the string currently shown in _lbl_status
            key: the translation key to test (e.g. 'merge_status_add')

        Returns:
            bool: True if at least one of the 5 language templates matches
        """
        import re as _re
        for tmpl in _all_translations_of(key):
            if not tmpl:
                continue
            # Escape the template, then replace {xxx} placeholders with .+?
            pattern = _re.escape(tmpl)
            pattern = _re.sub(r'\\\{[a-zA-Z_][a-zA-Z0-9_]*\\\}', r'.+?', pattern)
            if _re.fullmatch(pattern, text):
                return True
        return False

    def _retranslate_status(self):
        """Re-render _lbl_status content in the current language.
        Static text is re-rendered directly; recoverable dynamic text is reconstructed from the source info;
        unrecoverable text is reset to 'merge_status_ready'.
        Resolves the long-standing bug (since pre-v1.0.4) where Korean status messages persisted after a language switch."""
        cur = self._lbl_status.text()
        if not cur:
            return

        # ── 1) Static states without placeholders — simple mapping then re-render
        for key in ('merge_status_ready', 'merge_status_clr', 'merge_reading',
                    'merge_save_err', 'merge_path_reset_done'):
            if cur in _all_translations_of(key):
                self._lbl_status.setText(_t(key))
                return

        # ── 2) Recoverable dynamic states — reconstruct from source info
        # merge_status_add — restore from current file count
        if self._match_status_template(cur, 'merge_status_add'):
            self._lbl_status.setText(_t('merge_status_add', n=len(self.file_list)))
            return
        # merge_path_set — restore from current save path (only if save_dir is valid)
        if self._match_status_template(cur, 'merge_path_set'):
            if self.save_dir:
                self._lbl_status.setText(_t('merge_path_set', path=self.save_dir))
            else:
                self._lbl_status.setText(_t('merge_status_ready'))
            return

        # ── 3) Unrecoverable states — reset to 'ready' (source info lost)
        for key in ('merge_status_del', 'merge_save_done', 'bulk_scanning'):
            if self._match_status_template(cur, key):
                _glog(f"[Text Merger] Status reset due to language switch: {key!r} → 'merge_status_ready'")
                self._lbl_status.setText(_t('merge_status_ready'))
                return

        # ── 4) Unknown states — leave untouched (defensive handling)
        # e.g. external plugins or future messages

    def retranslate(self):
        self._tree.update()  # Refresh empty-state text
        self._tree.setHeaderLabels([_t('tag_col_filename'), _t('tag_col_path')])
        self._refresh_drop_zone()
        self._lbl_selection.setText(_t("merge_sel_none"))
        # v1.0.5: re-translate status messages (previously only the 'ready' state was refreshed — bug fix)
        self._retranslate_status()
        self._save_gb.setTitle(_t('merge_save_settings'))
        self._lbl_enc.setText(_t('merge_save_enc'))
        # v1.0.5: refresh combobox item display labels (userData preserved)
        for _i, (_enc_key, _i18n_key) in enumerate(self._ENC_ITEMS):
            self._combo_enc.setItemText(_i, _t(_i18n_key))
        # v1.0.6: refresh save-encoding label + recommendation Apply button (on language switch)
        # _refresh_recommendation() handles 0 files → hint, 1+ files → recommendation label automatically
        if hasattr(self, '_btn_enc_recommend_apply'):
            self._btn_enc_recommend_apply.setText(_t('merge_enc_recommend_apply'))
        if hasattr(self, '_lbl_enc_hint'): self._refresh_recommendation()
        self._lbl_path_label.setText(_t('merge_save_path'))
        if not self.save_dir: self._lbl_save_path.setText(_t('merge_path_none'))
        self._btn_browse.setText(_t('merge_path_pick'))
        self._btn_clear_path.setText(_t('merge_path_reset'))
        self._chk_sep.setText(_t('merge_sep'))
        self._btn_add.setText(_t('btn_add_file'))
        if hasattr(self, '_btn_add_folder'): self._btn_add_folder.setText(_t('btn_add_folder'))
        self._btn_del.setText(_t('btn_del_sel'))
        self._btn_del_all.setText(_t('btn_del_all'))
        self._btn_up.setText(_t('btn_up'))
        self._btn_dn.setText(_t('btn_down'))
        self._btn_merge.setText(_t('merge_btn'))
        if hasattr(self, '_btn_undo'): self._btn_undo.setText(_t('btn_undo'))
        self._update_stats()
    # ── Settings save / restore ─────────────────
    def get_config(self) -> dict:
        return {
            'save_dir':  self.save_dir,
            # v1.0.5: store internal key, not the display label (stable across language switches)
            'combo_enc': self._combo_enc.currentData() or self._combo_enc.currentText(),
            'sep_check': self._chk_sep.isChecked(),
        }

    def apply_config(self, d: dict):
        if not d: return
        if d.get('save_dir') and os.path.isdir(d['save_dir']):
            self.save_dir = d['save_dir']
            self._lbl_save_path.setText(self.save_dir)
            self._lbl_save_path.setToolTip(self.save_dir)
        enc = d.get('combo_enc', 'UTF-8')
        # v1.0.5: look up by internal key (userData) first → fall back to display text (compatible with v1.0.4 settings)
        idx = self._combo_enc.findData(enc)
        if idx < 0: idx = self._combo_enc.findText(enc)
        if idx >= 0: self._combo_enc.setCurrentIndex(idx)
        self._chk_sep.setChecked(d.get('sep_check', False))


# ═══════════════════════════════════════════════
# Settings Dialog
# ═══════════════════════════════════════════════


# ═══════════════════════════════════════════════
# Common dialog helpers with theme support
# ═══════════════════════════════════════════════
def _dlg_icon_pix(kind: str, size: int = 44) -> QPixmap:
    """Soft circular background + vector glyph — no fonts used, compatible with all themes."""
    pix = QPixmap(size, size); pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)

    cx, cy, s = size / 2.0, size / 2.0, float(size)
    c = QColor(MUTED)

    # ── Layer 1: glow ─────────────────────────
    glow = QColor(c); glow.setAlpha(22)
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(glow)
    p.drawEllipse(QRectF(0, 0, s, s))

    # ── Layer 2: main circle fill ─────────────
    m = s * 0.055
    fill = QColor(c); fill.setAlpha(52)
    p.setBrush(fill)
    p.drawEllipse(QRectF(m, m, s - m*2, s - m*2))

    # ── Layer 3: ring border ──────────────────
    ring = QColor(c); ring.setAlpha(115)
    p.setPen(QPen(ring, 1.1)); p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawEllipse(QRectF(m, m, s - m*2, s - m*2))

    # ── Layer 4: glyph ────────────────────────
    sym = QColor(MUTED); sym.setAlpha(215)

    if kind == 'question':
        # ? → QPainterPath: arc(270°) + tail curve + dot
        ar = s * 0.152
        ax, ay = cx, cy - s * 0.095
        arc_rect = QRectF(ax - ar, ay - ar, ar * 2, ar * 2)
        path = QPainterPath()
        path.arcMoveTo(arc_rect, 90)
        path.arcTo(arc_rect, 90, -270)
        path.cubicTo(ax - ar - s*0.01, ay + s*0.11,
                     cx - s*0.02,       cy + s*0.075,
                     cx,                cy + s*0.09)
        pw = QPen(sym, s * 0.108, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        p.setPen(pw); p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(sym)
        p.drawEllipse(QPointF(cx, cy + s * 0.295), s * 0.068, s * 0.068)

    elif kind == 'info':
        # i → small dot + thick vertical line
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(sym)
        p.drawEllipse(QPointF(cx, cy - s*0.195), s*0.072, s*0.072)
        pw = QPen(sym, s * 0.112, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        p.setPen(pw); p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawLine(QPointF(cx, cy - s*0.048), QPointF(cx, cy + s*0.215))

    elif kind == 'warn':
        # ! → thick vertical line + dot below
        pw = QPen(sym, s * 0.112, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        p.setPen(pw); p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawLine(QPointF(cx, cy - s*0.215), QPointF(cx, cy + s*0.045))
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(sym)
        p.drawEllipse(QPointF(cx, cy + s * 0.200), s * 0.072, s * 0.072)

    else:  # error
        # × → two thick lines, rounded ends
        pw = QPen(sym, s * 0.112, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        p.setPen(pw)
        d = s * 0.158
        p.drawLine(QPointF(cx - d, cy - d), QPointF(cx + d, cy + d))
        p.drawLine(QPointF(cx + d, cy - d), QPointF(cx - d, cy + d))

    p.end()
    return pix



def _build_dlg(parent, title: str, msg: str, kind: str, rich_text: bool = False) -> QDialog:
    """Build a common dialog skeleton. Buttons are added by the caller.

    v1.0.4: when rich_text=True, render the message as HTML (default False, preserves prior behavior).
    """
    dlg = QDialog(parent)
    dlg.setWindowTitle(title)
    try:
        dlg.setWindowIcon(_make_app_icon())
    except Exception:
        pass
    dlg.setMinimumWidth(360)
    dlg.setWindowFlags(dlg.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
    dlg.setStyleSheet(
        f"QDialog{{background:{SURFACE};}} "
        f"QLabel{{background:transparent;color:{TEXT};}}"
    )
    root = QVBoxLayout(dlg)
    root.setContentsMargins(28, 24, 28, 20)
    root.setSpacing(16)

    # Icon + message row
    row = QHBoxLayout(); row.setSpacing(16); row.setAlignment(Qt.AlignmentFlag.AlignTop)
    ico_lbl = QLabel()
    ico_lbl.setPixmap(_dlg_icon_pix(kind, 44))
    ico_lbl.setFixedSize(44, 44)
    ico_lbl.setStyleSheet("background:transparent;")
    msg_lbl = QLabel(msg)
    msg_lbl.setWordWrap(True)
    # v1.0.4: choose HTML or plain rendering based on rich_text option
    msg_lbl.setTextFormat(Qt.TextFormat.RichText if rich_text else Qt.TextFormat.PlainText)
    msg_lbl.setStyleSheet(f"color:{TEXT};font-size:13px;background:transparent;")
    row.addWidget(ico_lbl); row.addWidget(msg_lbl, 1)
    root.addLayout(row)

    # Divider
    sep = QFrame(); sep.setFrameShape(QFrame.HLine)
    sep.setStyleSheet(f"background:{BORDER};max-height:1px;border:none;")
    root.addWidget(sep)

    return dlg, root


def _themed_combo_ss(bg: str = None) -> str:
    """Generate a QComboBox inline stylesheet for the current theme — used by refresh_btn_styles."""
    _bg = bg or SURFACE
    return (
        f"QComboBox{{background:{_bg};border:1.5px solid {BORDER};"
        f"border-radius:8px;color:{TEXT};"
        f"padding:3px 28px 3px 10px;font-size:13px;min-height:18px;}}"
        f"QComboBox:focus{{border-color:{ACCENT};}}"
        f"QComboBox:hover{{border-color:{INPUT_H};}}"
        f"QComboBox::drop-down{{subcontrol-origin:padding;"
        f"subcontrol-position:right center;width:26px;border:none;"
        f"border-left:1px solid {BORDER};"
        f"border-top-right-radius:8px;border-bottom-right-radius:8px;"
        f"background:{SRF2};}}"
        f"QComboBox::down-arrow{{image:{_combo_arrow_url(MUTED)};width:10px;height:6px;}}"
        f"QComboBox:hover::down-arrow{{image:{_combo_arrow_url(TEXT)};}}"
        f"QComboBox:focus::down-arrow{{image:{_combo_arrow_url(ACCENT)};}}"
    )


def _btn_style(accent=False) -> str:
    if accent:
        return (f"QPushButton{{background:{ACCENT};border:none;color:white;"
                f"border-radius:8px;padding:9px 28px;font-size:12px;font-weight:600;"
                f"min-width:80px;}}"
                f"QPushButton:hover{{background:{ACCENT_HOVER};}}")
    return (f"QPushButton{{background:{SURFACE};border:1.5px solid {BTN_BORDER_H};color:{TEXT};"
            f"border-radius:8px;padding:9px 28px;font-size:12px;font-weight:600;"
            f"min-width:80px;}}"
            f"QPushButton:hover{{background:{SRF2};}}")


def _dlg_info(parent, title: str, msg: str):
    """Info dialog (OK button)."""
    dlg, root = _build_dlg(parent, title or _t('dlg_info'), msg, "info")
    br = QHBoxLayout(); br.addStretch()
    ok = QPushButton(_t('dlg_ok')); ok.setStyleSheet(_btn_style(True))
    ok.clicked.connect(dlg.accept); br.addWidget(ok)
    root.addLayout(br); dlg.exec()


def _dlg_warn(parent, title: str, msg: str, rich_text: bool = False):
    """Warning dialog (OK button). v1.0.6: rich_text parameter added (default False)."""
    dlg, root = _build_dlg(parent, title or _t('dlg_warning'), msg, "warn", rich_text=rich_text)
    br = QHBoxLayout(); br.addStretch()
    ok = QPushButton(_t('dlg_ok')); ok.setStyleSheet(_btn_style(True))
    ok.clicked.connect(dlg.accept); br.addWidget(ok)
    root.addLayout(br); dlg.exec()


def _dlg_error(parent, title: str, msg: str):
    """Error dialog (OK button)."""
    dlg, root = _build_dlg(parent, title or _t('dlg_error_title'), msg, "error")
    br = QHBoxLayout(); br.addStretch()
    ok = QPushButton(_t('dlg_ok')); ok.setStyleSheet(_btn_style(True))
    ok.clicked.connect(dlg.accept); br.addWidget(ok)
    root.addLayout(br); dlg.exec()


def _dlg_question(parent, title: str, msg: str, min_width: int = 360, rich_text: bool = False) -> bool:
    """Yes/No question dialog. True = Yes.

    v1.0.4: when rich_text=True, render the message as HTML (default False).
    """
    dlg, root = _build_dlg(parent, title or _t('dlg_confirm_title'), msg, "question", rich_text=rich_text)
    dlg.setMinimumWidth(min_width)
    br = QHBoxLayout(); br.setSpacing(10); br.addStretch()
    no  = QPushButton(_t('dlg_no'));  no.setStyleSheet(_btn_style(False))
    yes = QPushButton(_t('dlg_yes')); yes.setStyleSheet(_btn_style(True))
    yes.setDefault(True)
    no.clicked.connect(dlg.reject); yes.clicked.connect(dlg.accept)
    br.addWidget(no); br.addWidget(yes)
    root.addLayout(br)
    # Unify the width of both buttons to the larger one (compensates for Yes/No text length difference)
    dlg.show()
    btn_w = max(no.sizeHint().width(), yes.sizeHint().width())
    no.setFixedWidth(btn_w); yes.setFixedWidth(btn_w)
    return dlg.exec() == QDialog.Accepted


def _dlg_info_action(parent, title: str, msg: str, action_label: str) -> bool:
    """Info dialog + action button. True = action button clicked."""
    dlg, root = _build_dlg(parent, title or _t('dlg_done'), msg, "info")
    br = QHBoxLayout(); br.setSpacing(10); br.addStretch()
    act = QPushButton(action_label); act.setStyleSheet(_btn_style(False))
    ok  = QPushButton(_t('dlg_ok')); ok.setStyleSheet(_btn_style(True))
    ok.setDefault(True)
    act.clicked.connect(lambda: (dlg.done(2),))
    ok.clicked.connect(dlg.accept)
    br.addWidget(act); br.addWidget(ok)
    root.addLayout(br)
    # Unify the width of both buttons to the larger one
    dlg.show()
    btn_w = max(act.sizeHint().width(), ok.sizeHint().width())
    act.setFixedWidth(btn_w); ok.setFixedWidth(btn_w)
    return dlg.exec() == 2


def _show_first_run_notice(parent):
    """First-run notice popup for generated files/folders — 3-slide horizontal transition."""
    from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QPoint

    SLIDE_W = 500
    SLIDE_H = 268
    N_SLIDES = 3

    dlg = QDialog(parent)
    dlg.setWindowTitle("Welcome to File Nexus Suite")
    try: dlg.setWindowIcon(_make_app_icon())
    except Exception: pass
    dlg.setFixedWidth(SLIDE_W)
    dlg.setWindowFlags(dlg.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
    dlg.setStyleSheet(
        f"QDialog{{background:{SURFACE};}} "
        f"QLabel{{background:transparent;color:{TEXT};}}"
    )

    root = QVBoxLayout(dlg)
    root.setContentsMargins(0, 0, 0, 0)
    root.setSpacing(0)

    # ── Top fixed header ──────────────────────────
    hdr = QWidget()
    hdr_lay = QVBoxLayout(hdr)
    hdr_lay.setContentsMargins(28, 24, 28, 14)
    hdr_lay.setSpacing(10)
    title_lbl = QLabel(f"<b>{_t('first_run_title')}</b>")
    title_lbl.setStyleSheet(f"font-size:15px;color:{TEXT};")
    title_lbl.setTextFormat(Qt.TextFormat.RichText)
    hdr_lay.addWidget(title_lbl)
    sep_top = QFrame(); sep_top.setFrameShape(QFrame.HLine)
    sep_top.setStyleSheet(f"background:{BORDER};max-height:1px;border:none;")
    hdr_lay.addWidget(sep_top)
    root.addWidget(hdr)

    # ── Slide clip container ──────────────────────
    clip = QWidget()
    clip.setFixedSize(SLIDE_W, SLIDE_H)
    root.addWidget(clip)

    strip = QWidget(clip)
    strip.setGeometry(0, 0, SLIDE_W * N_SLIDES, SLIDE_H)

    # ── Slide 1: generated files / folders notice ─
    slide1 = QWidget(strip)
    slide1.setGeometry(0, 0, SLIDE_W, SLIDE_H)
    s1_lay = QVBoxLayout(slide1)
    s1_lay.setContentsMargins(28, 10, 28, 10)
    s1_lay.setSpacing(9)

    desc_lbl = QLabel(_t('first_run_desc'))
    desc_lbl.setWordWrap(True)
    desc_lbl.setStyleSheet(f"font-size:12px;color:{MUTED};")
    s1_lay.addWidget(desc_lbl)

    _is_onedir = (getattr(sys, 'frozen', False) and
                  not getattr(sys, '_MEIPASS', '').endswith('.pkg') and
                  (_app_dir() / '_internal').exists())
    items = [
        ("📄", "FileNexusSuite.json", _t('first_run_item_json')),
        ("📁", "Output/",            _t('first_run_item_output')),
        ("📁", "logs/",               _t('first_run_item_log')),
    ]
    if _is_onedir:
        items.append(("⚠️", "_internal/", _t('first_run_item_internal')))

    for icon, name, desc in items:
        row = QHBoxLayout(); row.setSpacing(8)
        ico = QLabel(icon); ico.setFixedWidth(22)
        ico.setStyleSheet("font-size:15px;background:transparent;")
        name_color = "#C04030" if name == "_internal/" else ACCENT
        name_lbl = QLabel(f"<b>{name}</b>")
        name_lbl.setStyleSheet(
            f"font-size:12px;color:{name_color};background:transparent;"
            f"min-width:155px;max-width:155px;")
        name_lbl.setTextFormat(Qt.TextFormat.RichText)
        desc_l = QLabel(desc)
        desc_l.setWordWrap(True)
        desc_l.setStyleSheet(f"font-size:12px;color:{MUTED};background:transparent;")
        row.addWidget(ico); row.addWidget(name_lbl); row.addWidget(desc_l, 1)
        s1_lay.addLayout(row)

    s1_lay.addStretch()
    tip_lbl = QLabel(f"💡 {_t('first_run_tip')}")
    tip_lbl.setWordWrap(True)
    tip_lbl.setStyleSheet(f"font-size:11px;color:{MUTED};")
    s1_lay.addWidget(tip_lbl)

    # ── Slide 2: tab feature notice ───────────────
    slide2 = QWidget(strip)
    slide2.setGeometry(SLIDE_W, 0, SLIDE_W, SLIDE_H)
    s2_lay = QVBoxLayout(slide2)
    s2_lay.setContentsMargins(28, 12, 28, 10)
    s2_lay.setSpacing(6)

    tabs_title = QLabel(f"<b>{_t('first_run_tabs_title')}</b>")
    tabs_title.setStyleSheet(f"font-size:13px;color:{TEXT};")
    tabs_title.setTextFormat(Qt.TextFormat.RichText)
    s2_lay.addWidget(tabs_title)

    tab_items = [
        ('document_line', "Text Merger",    _t('first_run_tab_merger')),
        ('folder_open_line',"Text Converter",_t('first_run_tab_converter')),
        ('tag_line',       "Tag Editor",    _t('first_run_tab_tag')),
        ('folder_line',    "Batch Renamer", _t('first_run_tab_batch')),
        ('wrench_line',    "Text Fixer",    _t('first_run_tab_fixer')),
        ('broom',          "Bulk Fixer",    _t('first_run_tab_bulk')),
    ]
    for icon_key, tab_name, tab_desc in tab_items:
        tab_row = QHBoxLayout(); tab_row.setSpacing(8)
        # Icon (SVG rendered via QLabel)
        ico_lbl = QLabel()
        ico_pix = _svg_icon(icon_key, ACCENT, size=14)
        ico_lbl.setPixmap(ico_pix.pixmap(QSize(14, 14)) if hasattr(ico_pix, 'pixmap') else QPixmap())
        ico_lbl.setFixedSize(16, 20)
        ico_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Tab name
        name_lbl2 = QLabel(f"<b>{tab_name}</b>")
        name_lbl2.setStyleSheet(
            f"font-size:12px;color:{ACCENT};background:transparent;"
            f"min-width:120px;max-width:120px;")
        name_lbl2.setTextFormat(Qt.TextFormat.RichText)
        # Description
        desc_lbl2 = QLabel(tab_desc)
        desc_lbl2.setStyleSheet(f"font-size:11px;color:{MUTED};background:transparent;")
        desc_lbl2.setWordWrap(True)
        tab_row.addWidget(ico_lbl)
        tab_row.addWidget(name_lbl2)
        tab_row.addWidget(desc_lbl2, 1)
        s2_lay.addLayout(tab_row)

    s2_lay.addStretch()

    # ── Slide 3: UI notice ────────────────────────
    slide3 = QWidget(strip)
    slide3.setGeometry(SLIDE_W * 2, 0, SLIDE_W, SLIDE_H)
    s3_lay = QVBoxLayout(slide3)
    s3_lay.setContentsMargins(28, 14, 28, 10)
    s3_lay.setSpacing(18)

    ui_title = QLabel(f"<b>{_t('first_run_ui_title')}</b>")
    ui_title.setStyleSheet(f"font-size:13px;color:{TEXT};")
    ui_title.setTextFormat(Qt.TextFormat.RichText)
    s3_lay.addWidget(ui_title)

    ui_items = [
        _t('first_run_ui_help'),
        _t('first_run_ui_batch'),
    ]
    for desc in ui_items:
        desc3 = QLabel(desc); desc3.setWordWrap(True)
        desc3.setStyleSheet(f"font-size:13px;color:{MUTED};background:transparent;")
        s3_lay.addWidget(desc3)

    s3_lay.addStretch()

    # ── Bottom fixed footer ───────────────────────
    ftr = QWidget()
    ftr_lay = QVBoxLayout(ftr)
    ftr_lay.setContentsMargins(28, 6, 28, 20)
    ftr_lay.setSpacing(8)

    sep_bot = QFrame(); sep_bot.setFrameShape(QFrame.HLine)
    sep_bot.setStyleSheet(f"background:{BORDER};max-height:1px;border:none;")
    ftr_lay.addWidget(sep_bot)

    # Dot indicator (● ○ ○)
    dot_row = QHBoxLayout()
    dot_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
    dot_row.setSpacing(8)
    dots = []
    for i in range(N_SLIDES):
        d = QLabel("●" if i == 0 else "○")
        d.setStyleSheet(f"font-size:10px;color:{ACCENT if i == 0 else MUTED};background:transparent;")
        dot_row.addWidget(d)
        dots.append(d)
    ftr_lay.addLayout(dot_row)

    # Prev / Next-Confirm buttons
    btn_row = QHBoxLayout(); btn_row.setSpacing(8)
    prev_btn = QPushButton(_t('tf_diff_prev'))
    prev_btn.setStyleSheet(_btn_style(False))
    prev_btn.setFixedWidth(100)
    prev_btn.setVisible(False)
    next_btn = QPushButton(_t('tf_diff_next'))
    next_btn.setStyleSheet(_btn_style(True))
    next_btn.setFixedWidth(100)
    next_btn.setDefault(True)
    btn_row.addStretch()
    btn_row.addWidget(prev_btn)
    btn_row.addWidget(next_btn)
    ftr_lay.addLayout(btn_row)
    root.addWidget(ftr)

    # ── Slide transition animation ────────────────
    _cur = [0]

    anim = QPropertyAnimation(strip, b"pos")
    anim.setDuration(300)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _refresh_dots(idx):
        for i, d in enumerate(dots):
            if i == idx:
                d.setText("●")
                d.setStyleSheet(f"font-size:10px;color:{ACCENT};background:transparent;")
            else:
                d.setText("○")
                d.setStyleSheet(f"font-size:10px;color:{MUTED};background:transparent;")

    def _go(idx):
        _cur[0] = idx
        anim.stop()
        anim.setStartValue(strip.pos())
        anim.setEndValue(QPoint(-SLIDE_W * idx, 0))
        anim.start()
        _refresh_dots(idx)
        prev_btn.setVisible(idx > 0)
        next_btn.setText(_t('dlg_ok') if idx == N_SLIDES - 1 else _t('tf_diff_next'))

    def _on_next():
        if _cur[0] < N_SLIDES - 1:
            _go(_cur[0] + 1)
        else:
            dlg.accept()

    def _on_prev():
        if _cur[0] > 0:
            _go(_cur[0] - 1)

    prev_btn.clicked.connect(_on_prev)
    next_btn.clicked.connect(_on_next)

    dlg.exec()

# ═══════════════════════════════════════════════
# Shortcut input capture button
# ═══════════════════════════════════════════════
class _KeyCaptureButton(QPushButton):
    """Click → wait for key input → capture done or ESC cancel."""
    key_captured = Signal(str)

    def __init__(self, key_str='', parent=None):
        super().__init__(parent)
        self._capturing = False
        self._key_str = key_str
        self.setFixedWidth(150)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.clicked.connect(self._toggle_capture)
        self._refresh_style()
        self.setText(self._key_str or _t('sc_none'))

    def _toggle_capture(self):
        if self._capturing: self._stop_capture()
        else:               self._start_capture()

    def _start_capture(self):
        self._capturing = True
        self.setText(_t('sc_press'))
        self._refresh_style()
        self.grabKeyboard()

    def _stop_capture(self, key_str=None):
        self._capturing = False
        self.releaseKeyboard()
        if key_str is not None:
            self._key_str = key_str
            self.key_captured.emit(key_str)
        self.setText(self._key_str or _t('sc_none'))
        self._refresh_style()

    def _refresh_style(self):
        if self._capturing:
            self.setStyleSheet(
                f"QPushButton{{background:{_accent_alpha(0.10)};border:2px solid {ACCENT};"
                f"border-radius:6px;color:{ACCENT};padding:5px 10px;font-size:11px;}}")
        else:
            self.setStyleSheet(
                f"QPushButton{{background:{SURFACE};border:1.5px solid {BORDER};"
                f"border-radius:6px;color:{TEXT};padding:5px 10px;font-size:12px;"
                f"font-family:'D2Coding','Malgun Gothic','맑은 고딕','Consolas',monospace;}}"
                f"QPushButton:hover{{border-color:{INPUT_H};}}")

    def keyPressEvent(self, e):
        if not self._capturing: super().keyPressEvent(e); return
        key = e.key()
        if key == Qt.Key.Key_Escape: self._stop_capture(); return
        if key in (Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta): return
        mods = e.modifiers()
        parts = []
        if mods & Qt.KeyboardModifier.ControlModifier: parts.append('Ctrl')
        if mods & Qt.KeyboardModifier.ShiftModifier:   parts.append('Shift')
        if mods & Qt.KeyboardModifier.AltModifier:     parts.append('Alt')
        name = QKeySequence(key).toString()
        if name: parts.append(name)
        if parts: self._stop_capture('+'.join(parts))




# ═══════════════════════════════════════════════
# Shorten tooltip delay — default 700ms → 250ms
# ═══════════════════════════════════════════════
class _FastToolTipStyle(QProxyStyle):
    """Fusion-style based, only the tooltip wake-up delay is shortened."""
    def __init__(self):
        super().__init__("Fusion")

    def styleHint(self, hint, option=None, widget=None, returnData=None):
        if hint == QStyle.StyleHint.SH_ToolTip_WakeUpDelay:
            return 250
        return super().styleHint(hint, option, widget, returnData)


# ═══════════════════════════════════════════════
# QComboBox custom delegate — bypass native rendering
# ═══════════════════════════════════════════════
class _ComboItemDelegate(QStyledItemDelegate):
    """Paint QComboBox popup items directly — workaround for the QSS-selection-ignored issue."""
    def paint(self, painter, option, index):
        painter.save()
        is_selected = bool(option.state & QStyle.State_Selected)
        rect = option.rect
        if is_selected:
            painter.fillRect(rect, QColor(ACCENT))
            painter.setPen(QColor("#FFFFFF"))
        else:
            painter.fillRect(rect, QColor(SURFACE))
            painter.setPen(QColor(TEXT))
        text = index.data(Qt.ItemDataRole.DisplayRole) or ""
        painter.drawText(rect.adjusted(14, 0, -8, 0), Qt.AlignmentFlag.AlignVCenter, text)
        painter.restore()

    def sizeHint(self, option, index):
        sh = super().sizeHint(option, index)
        return sh.__class__(sh.width(), max(sh.height(), 26))


class _ThemedCombo(QComboBox):
    """QComboBox with the delegate auto-applied."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view().setItemDelegate(_ComboItemDelegate(self))


class _DiagonalPreview(QFrame):
    """Diagonal light/dark split preview for the auto-theme card."""
    _LT_BG  = '#F0EFEB'; _DK_BG  = '#1C1C1C'
    _LT_SRF = '#FFFFFF';  _DK_SRF = '#2C2C2C'
    _LT_LN  = '#C8C5BE';  _DK_LN  = '#454545'
    _ACCENT = '#CC785C'

    def __init__(self):
        super().__init__()
        self.setFixedSize(118, 68)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        self.setStyleSheet("border:none; background:transparent;")

    def paintEvent(self, _):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height(); r = 10; mid = w // 2

        # ── Top rounded-corner clipping (precise arcs via addRoundedRect) ──
        clip = QPainterPath()
        clip.addRoundedRect(QRectF(0, 0, w, h + r), r, r)  # Extend down by r to hide bottom rounding
        p.setClipPath(clip)

        # ── Light (left half) ─────────────────────
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor(self._LT_BG)))
        p.drawRect(QRect(0, 0, mid, h))

        # ── Dark (right half) ─────────────────────
        p.setBrush(QBrush(QColor(self._DK_BG)))
        p.drawRect(QRect(mid, 0, mid, h))

        # ── Vertical divider ──────────────────────
        p.setPen(QPen(QColor(255, 255, 255, 60), 1))
        p.drawLine(QPointF(mid, 0), QPointF(mid, h))

        # ── Light-side mini UI ────────────────────
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor(self._ACCENT)))
        p.drawEllipse(QPointF(10, 13), 3, 3)
        p.setBrush(QBrush(QColor(self._LT_LN)))
        p.drawRoundedRect(QRect(17, 11, 28, 4), 2, 2)
        p.drawRoundedRect(QRect(9, 23, 38, 3), 1, 1)
        p.drawRoundedRect(QRect(9, 29, 28, 3), 1, 1)
        p.setBrush(QBrush(QColor(self._ACCENT)))
        p.drawRoundedRect(QRect(30, 38, 16, 7), 3, 3)

        # ── Dark-side mini UI ─────────────────────
        p.setBrush(QBrush(QColor(self._DK_LN)))
        p.drawRoundedRect(QRect(mid+8, 11, 28, 4), 2, 2)
        p.drawRoundedRect(QRect(mid+6, 23, 38, 3), 1, 1)
        p.drawRoundedRect(QRect(mid+6, 29, 24, 3), 1, 1)
        p.setBrush(QBrush(QColor(self._ACCENT)))
        p.drawEllipse(QPointF(mid+8, 13), 3, 3)
        p.drawRoundedRect(QRect(mid+28, 38, 16, 7), 3, 3)

        p.end()


class _ThemeCard(QFrame):
    """Theme card — drawn directly with QPainter for perfect corner clipping."""
    _DP_LT_BG = '#F0EFEB'; _DP_DK_BG = '#1C1C1C'
    _DP_LT_LN = '#C8C5BE'; _DP_DK_LN = '#454545'
    _DP_ACCENT = '#CC785C'

    def __init__(self, name, cfg, selected, on_click, on_double_click=None):
        super().__init__()
        self._name = name; self._cfg = cfg
        self._selected = selected
        self._on_click = on_click; self._on_double_click = on_double_click
        self._label_text = _theme_label(name)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        self.setStyleSheet("background:transparent; border:none;")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(118, 104)

    def set_selected(self, val):
        self._selected = val; self.update()

    def set_label(self, text):
        self._label_text = text; self.update()

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        c = self._cfg
        w, h, r, ph, lh = 118, 104, 10.0, 68, 36

        # Whole-card clipping
        clip = QPainterPath()
        clip.addRoundedRect(QRectF(0, 0, w, h), r, r)
        p.setClipPath(clip)

        # Preview area
        p.setPen(Qt.PenStyle.NoPen)
        if self._name == 'auto':
            self._paint_auto(p, w, ph)
        else:
            self._paint_preview(p, c, w, ph)

        # Label area
        p.setBrush(QBrush(QColor(c['lbl_bg'])))
        p.drawRect(QRectF(0, ph, w, lh))

        # Border after clip release
        p.setClipping(False)
        bw = 2.5 if self._selected else 1.5
        pen = QPen(QColor(c['sel_border'] if self._selected else c['card_border']), bw)
        p.setPen(pen); p.setBrush(Qt.BrushStyle.NoBrush)
        inset = bw / 2
        p.drawRoundedRect(QRectF(inset, inset, w - bw, h - bw), r, r)

        # Label text
        font = self.font(); font.setPixelSize(11)
        font.setWeight(QFont.Weight.DemiBold if self._selected else QFont.Weight.Normal)
        p.setFont(font)
        p.setPen(QColor(c['lbl_text']))
        p.drawText(QRect(10, ph, w - 44, lh),
                   Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                   self._label_text)
        if self._selected:
            font2 = self.font(); font2.setPixelSize(12); font2.setWeight(QFont.Weight.Bold)
            p.setFont(font2)
            p.setPen(QColor(c['sel_border']))
            p.drawText(QRect(0, ph, w - 8, lh),
                       Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, "\u2713")
        p.end()

    def _paint_preview(self, p, c, w, ph):
        p.setBrush(QBrush(QColor(c['card_bg']))); p.drawRect(QRectF(0, 0, w, ph))
        p.setBrush(QBrush(QColor(c['accent']))); p.drawEllipse(QPointF(16, 15), 3, 3)
        p.setBrush(QBrush(QColor(c['line1']))); p.drawRoundedRect(QRectF(23, 13, 76, 4), 2, 2)
        p.setBrush(QBrush(QColor(c['surface']))); p.drawRoundedRect(QRectF(10, 24, 98, 34), 4, 4)
        p.setBrush(QBrush(QColor(c['line2'])))
        p.drawRoundedRect(QRectF(17, 31, 82, 4), 2, 2)
        p.drawRoundedRect(QRectF(17, 39, 60, 3), 1, 1)
        p.setBrush(QBrush(QColor(c['accent']))); p.drawRoundedRect(QRectF(83, 47, 18, 7), 3, 3)

    def _paint_auto(self, p, w, ph):
        mid = w // 2
        p.setBrush(QBrush(QColor(self._DP_LT_BG))); p.drawRect(QRectF(0, 0, mid, ph))
        p.setBrush(QBrush(QColor(self._DP_DK_BG))); p.drawRect(QRectF(mid, 0, mid, ph))
        p.setPen(QPen(QColor(255, 255, 255, 60), 1))
        p.drawLine(QPointF(mid, 0), QPointF(mid, ph)); p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor(self._DP_ACCENT))); p.drawEllipse(QPointF(10, 13), 3, 3)
        p.setBrush(QBrush(QColor(self._DP_LT_LN)))
        p.drawRoundedRect(QRectF(17, 11, 28, 4), 2, 2)
        p.drawRoundedRect(QRectF(9, 23, 38, 3), 1, 1)
        p.drawRoundedRect(QRectF(9, 29, 28, 3), 1, 1)
        p.setBrush(QBrush(QColor(self._DP_ACCENT))); p.drawRoundedRect(QRectF(30, 38, 16, 7), 3, 3)
        p.setBrush(QBrush(QColor(self._DP_DK_LN)))
        p.drawRoundedRect(QRectF(mid+8, 11, 28, 4), 2, 2)
        p.drawRoundedRect(QRectF(mid+6, 23, 38, 3), 1, 1)
        p.drawRoundedRect(QRectF(mid+6, 29, 24, 3), 1, 1)
        p.setBrush(QBrush(QColor(self._DP_ACCENT)))
        p.drawEllipse(QPointF(mid+8, 13), 3, 3)
        p.drawRoundedRect(QRectF(mid+28, 38, 16, 7), 3, 3)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton: self._on_click(self._name)

    def mouseDoubleClickEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._on_click(self._name)
            if self._on_double_click: self._on_double_click(self._name)


# ── App icon (base64 embedded — no external file required) ────────────

_APP_ICON_B64 = (
    "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"
    "SUVORK5CYII="
)


def _make_app_icon() -> QIcon:
    """Convert a base64-embedded ICO (with transparent PNGs) into a multi-size QIcon."""
    raw = base64.b64decode(_APP_ICON_B64)
    icon = QIcon()
    for sz in (16, 32, 48, 64, 128, 256):
        buf = QBuffer()
        buf.setData(raw)
        buf.open(QIODevice.ReadOnly)
        reader = QImageReader(buf)
        reader.setScaledSize(QSize(sz, sz))
        img = reader.read()
        buf.close()
        if not img.isNull():
            icon.addPixmap(QPixmap.fromImage(img), QIcon.Normal, QIcon.Off)
    if icon.isNull():
        # fallback
        pix = QPixmap()
        pix.loadFromData(raw, "ICO")
        icon = QIcon(pix)
    return icon

def _make_gear_icon(size: int = 32) -> QIcon:
    """Render the ⚙ glyph onto a QPixmap to use as a window icon. No external file needed."""
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.TextAntialiasing)
    f = QFont("Segoe UI Symbol", int(size * 0.68))
    p.setFont(f)
    p.setPen(QColor(MUTED))

    p.drawText(QRect(0, 0, size, size), Qt.AlignmentFlag.AlignCenter, "⚙")
    p.end()
    return QIcon(pix)


# ═══════════════════════════════════════════════
# Help standalone window — sidebar layout
# ═══════════════════════════════════════════════
class HelpDialog(QDialog):
    """Standalone help window opened from the main UI — sidebar navigation."""
    def __init__(self, parent=None):
        super().__init__(parent)
        lang = _current_lang
        self.setWindowTitle(_t('help_window_title', ver=APP_VERSION))
        self.setMinimumSize(700, 560)
        self.resize(760, 640)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setStyleSheet(f"QDialog{{background:{BG};}}")
        self._nav_btns = []
        self._build()

    def _build(self):
        from PySide6.QtWidgets import QTextBrowser, QStackedWidget
        from PySide6.QtGui import QColor

        intro, sections = _build_help_html(_data_only=True)

        def _mix(h1, h2, r=0.12):
            c1=QColor(h1); c2=QColor(h2)
            return f"#{int(c1.red()*(1-r)+c2.red()*r):02X}{int(c1.green()*(1-r)+c2.green()*r):02X}{int(c1.blue()*(1-r)+c2.blue()*r):02X}"

        root = QHBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        # ── Sidebar ──────────────────────────────────
        sb = QFrame(); sb.setFixedWidth(168)
        sb.setStyleSheet(f"QFrame{{background:{SRF2};border-right:1px solid {BORDER};}}")
        sl = QVBoxLayout(sb); sl.setContentsMargins(10,20,10,16); sl.setSpacing(4)

        sb_title = QLabel(_t('help_sidebar_title'))
        sb_title.setStyleSheet(f"font-size:13px;font-weight:700;color:{TEXT};padding-left:6px;padding-bottom:10px;")
        sl.addWidget(sb_title)
        div = QFrame(); div.setFrameShape(QFrame.HLine); div.setFixedHeight(1)
        div.setStyleSheet(f"background:{BORDER};border:none;margin-bottom:6px;")
        sl.addWidget(div)

        # ── Content area ─────────────────────────────
        right = QFrame(); right.setStyleSheet(f"QFrame{{background:{SURFACE};}}")
        rl = QVBoxLayout(right); rl.setContentsMargins(20,20,20,16); rl.setSpacing(0)

        stack = QStackedWidget(); stack.setStyleSheet("background:transparent;")

        browser_style = (
            f"QTextBrowser{{background:{SRF2};border:1px solid {BORDER};"
            f"border-radius:10px;padding:6px;color:{TEXT};font-size:13px;}}"
            f"QScrollBar:vertical{{background:{BG};width:8px;border-radius:4px;}}"
            f"QScrollBar::handle:vertical{{background:{BORDER};border-radius:4px;min-height:24px;}}"
            f"QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0px;}}"
        )

        body_style = (f"background:{BG};color:{TEXT};"
                      f"font-family:'Pretendard','Segoe UI Variable','Segoe UI','Malgun Gothic',sans-serif;"
                      f"font-size:13px;margin:0;padding:0;")

        # Intro page
        intro_html = (
            f'<html><body style="{body_style}">'
            f'<div style="background:{_mix(SURFACE,ACCENT,0.06)};border:1px solid {_mix(ACCENT,SURFACE,0.6)};'
            f'border-radius:10px;padding:16px 18px;margin:0 0 12px;">'
            f'<div style="font-size:15px;font-weight:700;color:{ACCENT};margin-bottom:7px;">'
            f'File Nexus Suite <span style="font-size:11px;font-weight:400;color:{MUTED};">v{APP_VERSION}</span></div>'
            f'<div style="font-size:13px;color:{TEXT};line-height:1.75;">{intro}</div>'
            f'</div></body></html>'
        )
        b0 = QTextBrowser(); b0.setStyleSheet(browser_style); b0.setHtml(intro_html)
        stack.addWidget(b0)

        # Per-section pages — uses _render_section
        from PySide6.QtGui import QColor as _QC  # for color mixing
        for entry in sections:
            b = QTextBrowser(); b.setStyleSheet(browser_style)
            # Build single-section HTML
            # Direct section render
            # Direct section render
            def _mx(h1,h2,r=0.12):
                c1=_QC(h1);c2=_QC(h2)
                return f"#{int(c1.red()*(1-r)+c2.red()*r):02X}{int(c1.green()*(1-r)+c2.green()*r):02X}{int(c1.blue()*(1-r)+c2.blue()*r):02X}"
            tip_bg=_mx(SURFACE,ACCENT,0.07); tip_bdr=_mx(ACCENT,SURFACE,0.4)
            warn_bg=_mx(SURFACE,"#D04030",0.08); warn_bdr="#D05040"
            note_bg=_mx(SURFACE,"#5080D0",0.07); note_bdr=_mx("#5080D0",SURFACE,0.4)
            feat_bg=_mx(SURFACE,ACCENT,0.05); feat_bdr=_mx(ACCENT,SURFACE,0.5)
            _CIRCLED=['①','②','③','④','⑤','⑥','⑦','⑧','⑨','⑩',
                      '⑪','⑫','⑬','⑭','⑮','⑯','⑰','⑱','⑲','⑳']

            icon,title,subtitle,desc,items = entry
            is_sc = any(i[0]=='shortcut' for i in items)
            step_n = 0
            p = [f'<html><body style="{body_style}">']
            p.append(f'<div style="background:{SURFACE};border:1px solid {BORDER};border-radius:12px;overflow:hidden;">')
            p.append(f'<div style="padding:13px 18px 11px;border-bottom:1px solid {BORDER};">'
                     f'<span style="font-size:18px;margin-right:10px;">{icon}</span>'
                     f'<span style="font-size:14px;font-weight:700;color:{TEXT};">{title}')
            if subtitle:
                p.append(f'<span style="font-size:12px;font-weight:400;color:{MUTED};margin-left:8px;">{subtitle}</span>')
            p.append('</span>')
            if desc:
                p.append(f'<div style="font-size:13px;color:{MUTED};margin-top:7px;line-height:1.65;">{desc}</div>')
            p.append('</div><div style="padding:16px 12px 14px;">')
            if is_sc:
                for item in items:
                    if item[0]=='shortcut':
                        _,k,d=item
                        key_parts = k.split('+')
                        key_html = f'<span style="color:{MUTED};font-size:11px;margin:0 4px;font-weight:400;">+</span>'.join(
                            f'<span style="display:inline-block;background:{SRF2};'
                            f'border:1px solid {TEXT};border-bottom:2px solid {TEXT};'
                            f'border-radius:4px;padding:3px 10px;font-size:12px;font-weight:700;'
                            f'font-family:monospace;color:{TEXT};white-space:nowrap;">{kp.strip()}</span>'
                            for kp in key_parts
                        )
                        p.append(
                            f'<div style="padding:8px 14px;margin:0 0 5px;border-radius:8px;'
                            f'background:{BG};border:1px solid {BORDER};">'
                            f'<table style="border-spacing:0;border-collapse:collapse;">'
                            f'<tr>'
                            f'<td style="vertical-align:middle;padding-right:16px;white-space:nowrap;">{key_html}</td>'
                            f'<td style="color:{MUTED};font-size:13px;vertical-align:middle;">{d}</td>'
                            f'</tr></table></div>'
                        )
                    elif item[0]=='tip':
                        tt=item[1]; hi=tt[:2].strip() and ord(tt[0])>127
                        ic='' if hi else f'<span style="color:{ACCENT};font-weight:700;margin-right:5px;">💡</span>'
                        p.append(f'<div style="border-left:3px solid {tip_bdr};background:{tip_bg};border-radius:0 7px 7px 0;padding:9px 14px;margin:10px 0 0;font-size:13px;color:{TEXT};line-height:1.7;">{ic}{tt}</div>')
                p.append('')
            else:
                for item in items:
                    kind=item[0]
                    if kind=='step':
                        step_n+=1; num=_CIRCLED[step_n-1] if step_n<=20 else f'{step_n}.'
                        content=item[1]
                        if ' — ' in content:
                            cut=content.index(' — ')
                            title_part=content[:cut]
                            desc_part=content[cut+3:]
                            inner=(
                                f'<div style="font-size:13px;font-weight:700;color:{TEXT};">{title_part}</div>'
                                f'<div style="font-size:13px;color:{TEXT};line-height:1.7;margin-top:3px;">{desc_part}</div>'
                            )
                        else:
                            inner=f'<div style="font-size:13px;color:{TEXT};line-height:1.75;">{content}</div>'
                        p.append(
                            f'<div style="margin:0 0 10px 6px;">'
                            f'<table style="border-spacing:0;border-collapse:collapse;">'
                            f'<tr>'
                            f'<td style="color:{ACCENT};font-weight:700;font-size:13px;'
                            f'vertical-align:top;padding-right:7px;white-space:nowrap;">{num}</td>'
                            f'<td>{inner}</td>'
                            f'</tr></table></div>'
                        )
                    elif kind=='divider':
                        p.append(f'<hr style="border:none;border-top:1px solid {BORDER};margin:5px 0 8px 0;">')
                    elif kind=='info':
                        p.append(f'<div style="border-left:3px solid {BORDER};background:{SRF2};border-radius:0 7px 7px 0;padding:8px 12px;margin:4px 0 7px 6px;font-size:13px;color:{MUTED};line-height:1.7;"><span style="font-weight:700;margin-right:5px;">ℹ</span>{item[1]}</div>')
                    elif kind=='formats':
                        fmts=item[1]
                        from PySide6.QtGui import QColor as _FQC
                        def _fmix(h1,h2,r,_C=_FQC):
                            c1=_C(h1);c2=_C(h2)
                            return f"#{int(c1.red()*(1-r)+c2.red()*r):02X}{int(c1.green()*(1-r)+c2.green()*r):02X}{int(c1.blue()*(1-r)+c2.blue()*r):02X}"
                        pills=[]
                        for label,ftype in fmts:
                            if ftype=='native':
                                pb=_fmix(ACCENT,SURFACE,0.78); pf=ACCENT; pd=_fmix(ACCENT,SURFACE,0.55)
                            else:
                                pb=_fmix('#808080',SURFACE,0.88); pf=MUTED; pd=_fmix('#808080',SURFACE,0.65)
                            pills.append(f'<span style="display:inline-block;background:{pb};border:1px solid {pd};border-radius:4px;padding:2px 9px;font-size:12px;font-weight:700;font-family:monospace;color:{pf};">{label}</span>')
                        p.append(f'<div style="margin:0 0 10px 6px;"><div style="font-size:12px;color:{MUTED};margin-bottom:9px;"><span style="color:{ACCENT};font-size:10px;">●</span> 기본 지원 &nbsp;&nbsp;<span style="color:{MUTED};font-size:10px;">●</span> 라이브러리 설치 필요 <span style="font-size:11px;">(python-docx · pdfplumber · openpyxl · python-hwpx)</span></div>{" ".join(pills)}</div>')
                    elif kind=='sub':
                        p.append(f'<div style="margin:-3px 0 8px 26px;color:{MUTED};font-size:13px;line-height:1.7;">{item[1]}</div>')
                    elif kind=='note':
                        p.append(f'<div style="border-left:3px solid {note_bdr};background:{note_bg};border-radius:0 7px 7px 0;padding:8px 12px;margin:0 0 8px 6px;font-size:13px;color:{TEXT};line-height:1.7;"><span style="color:#5080D0;font-weight:700;margin-right:5px;">ℹ️</span>{item[1]}</div>')
                    elif kind=='tip':
                        p.append(f'<div style="border-left:3px solid {tip_bdr};background:{tip_bg};border-radius:0 7px 7px 0;padding:8px 12px;margin:3px 0 7px 6px;font-size:13px;color:{TEXT};line-height:1.7;"><span style="color:{ACCENT};font-weight:700;margin-right:5px;">💡</span>{item[1]}</div>')
                    elif kind=='warn':
                        p.append(f'<div style="border-left:3px solid {warn_bdr};background:{warn_bg};border-radius:0 7px 7px 0;padding:8px 12px;margin:3px 0 7px 6px;font-size:13px;color:#9B2A10;line-height:1.7;"><span style="font-weight:700;margin-right:5px;">⚠️</span>{item[1]}</div>')
                    elif kind=='feature':
                        _,ft,fd=item
                        p.append(f'<div style="background:{feat_bg};border:1px solid {feat_bdr};border-radius:8px;padding:10px 12px;margin:3px 0 8px 6px;">'
                                  f'<div style="font-size:13px;font-weight:700;color:{ACCENT};margin-bottom:4px;">{ft}</div>'
                                  f'<div style="font-size:13px;color:{TEXT};line-height:1.7;">{fd}</div></div>')
                    elif kind=='example':
                        _,before,after=item
                        p.append(
                            f'<div style="margin:3px 0 7px 6px;">'
                            f'<table style="background:{SRF2};border:1px solid {BORDER};'
                            f'border-radius:6px;border-spacing:0;border-collapse:collapse;">'
                            f'<tr>'
                            f'<td style="font-family:monospace;color:{MUTED};font-size:13px;'
                            f'padding:5px 10px 5px 12px;white-space:nowrap;">{before}</td>'
                            f'<td style="color:{MUTED};font-size:15px;padding:5px 10px;white-space:nowrap;">→</td>'
                            f'<td style="font-family:monospace;color:{ACCENT};font-size:13px;'
                            f'font-weight:700;padding:5px 12px 5px 10px;white-space:nowrap;">{after}</td>'
                            f'</tr></table></div>'
                        )
            p.append('</div></div></body></html>')
            b.setHtml(''.join(p))
            stack.addWidget(b)

        rl.addWidget(stack, stretch=1)

        # Close button
        btn_row = QHBoxLayout(); btn_row.addStretch()
        btn_close = QPushButton(_t('btn_close')); btn_close.setFixedWidth(80)
        btn_close.setStyleSheet(
            f"QPushButton{{background:{SURFACE};border:1.5px solid {BORDER};color:{TEXT};"
            f"border-radius:8px;padding:8px 0;font-size:13px;}}"
            f"QPushButton:hover{{background:{SRF2};}}"
        )
        btn_close.clicked.connect(self.close)
        btn_row.addWidget(btn_close)
        rl.addSpacing(10); rl.addLayout(btn_row)

        # Sidebar nav buttons
        # Section emoji → SVG icon-key mapping
        _section_icons = {
            'Text Merger':      'document_line',
            'Text Converter':   'folder_open_line',
            'Tag Editor':       'tag_line',
            'Batch Renamer':    'folder_line',
            'Text Fixer':       'wrench_line',
            'Bulk Fixer':       'broom_line',
            '단축키 및 기타':    'keyboard_line',
            'Shortcuts & More': 'keyboard_line',
            'ショートカット等':   'keyboard_line',
            '快捷键及其他':      'keyboard_line',
            '快速鍵及其他':      'keyboard_line',
            '생성 파일 안내':    'license_line',
            'Generated Files':   'license_line',
            '生成ファイル案内':  'license_line',
            '生成文件说明':      'license_line',
            '生成檔案說明':      'license_line',
        }

        def _nav(label, idx, icon_key=None):
            btn = QPushButton(label); btn.setFixedHeight(36)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            if icon_key:
                btn.setIcon(_svg_icon(icon_key, MUTED)); btn.setIconSize(QSize(16,16))
            btn.clicked.connect(lambda _, i=idx: self._switch(i))
            self._nav_btns.append(btn); sl.addWidget(btn)

        _nav(_t('help_section_intro'), 0, 'info_line')
        for i, entry in enumerate(sections):
            icon_key = _section_icons.get(entry[1], 'document_line')
            _nav(entry[1], i+1, icon_key)

        sl.addStretch()
        root.addWidget(sb); root.addWidget(right)
        self._stack = stack
        self._switch(0)

    def _switch(self, idx):
        self._stack.setCurrentIndex(idx)
        _icon_keys = ['info_line','document_line','folder_open_line','tag_line',
                      'folder_line','wrench_line','broom_line','keyboard_line','license_line']
        for i, btn in enumerate(self._nav_btns):
            active = (i == idx)
            btn.setStyleSheet(
                f"QPushButton{{background:{_accent_alpha(0.12) if active else 'transparent'};"
                f"border:none;border-radius:8px;text-align:left;padding:8px 12px;"
                f"color:{ACCENT if active else MUTED};font-size:12px;"
                f"font-weight:{'600' if active else '400'};}}"
                f"QPushButton:hover{{background:{_accent_alpha(0.12) if active else SRF2};}}"
            )
            if i < len(_icon_keys):
                btn.setIcon(_svg_icon(_icon_keys[i], ACCENT if active else MUTED))
                btn.setIconSize(QSize(16,16))

    def refresh(self):
        pass  # Recreated each time it opens (exec() is modal)


class SettingsDialog(QDialog):
    _CARD_CFG={
        'light': {'card_bg':'#F0EFEB','card_border':'#D8D5CE','sel_border':'#4A90D9','surface':'#FFFFFF','accent':'#CC785C','line1':'#C8C5BE','line2':'#E0DDD8','lbl_bg':'#FFFFFF','lbl_text':'#1A1A1A'},
        'dark':  {'card_bg':'#1A1A1A','card_border':'#3D3D3D','sel_border':'#4A90D9','surface':'#2C2C2C','accent':'#CC785C','line1':'#3D3D3D','line2':'#454545','lbl_bg':'#242424','lbl_text':'#EBEBEB'},
        'sakura':{'card_bg':'#FEF0F4','card_border':'#F0C8D4','sel_border':'#D4637A','surface':'#FFFFFF','accent':'#D4637A','line1':'#E8C5D0','line2':'#F5DDE5','lbl_bg':'#FFF5F8','lbl_text':'#2C1F26'},
        'auto':  {'card_bg':'#E8E8E8','card_border':'#CBCBCB','sel_border':'#4A90D9','surface':'#FFFFFF','accent':'#CC785C','line1':'#CCCCCC','line2':'#E0E0E0','lbl_bg':'#EFEFEF','lbl_text':'#1A1A1A'},
        'choco':  {'card_bg':'#1E1916','card_border':'#3D3530','sel_border':'#B87333','surface':'#2D2720','accent':'#B87333','line1':'#3D3530','line2':'#453830','lbl_bg':'#26211D','lbl_text':'#EDE8E2'},
        'mint':     {'card_bg':'#EBF5EE','card_border':'#C5DFC9','sel_border':'#5C9E70','surface':'#FFFFFF','accent':'#5C9E70','line1':'#A8CEB0','line2':'#C5DFC9','lbl_bg':'#F4F9F1','lbl_text':'#1C2E20'},
        'ocean':    {'card_bg':'#E0EFFC','card_border':'#A8CEE8','sel_border':'#2878B8','surface':'#FFFFFF','accent':'#2878B8','line1':'#82B8D8','line2':'#A8CEE8','lbl_bg':'#EEF6FF','lbl_text':'#0A1E30'},
        'sand':   {'card_bg':'#F5EDE0','card_border':'#E0C4A0','sel_border':'#B86838','surface':'#FFFFFF','accent':'#B86838','line1':'#C8A07A','line2':'#E0C4A0','lbl_bg':'#FBF5EE','lbl_text':'#281808'},
        'honey':   {'card_bg':'#FAF5DC','card_border':'#E8D880','sel_border':'#C8A030','surface':'#FFFFFF','accent':'#C8A030','line1':'#D8C060','line2':'#E8D880','lbl_bg':'#FDFAF0','lbl_text':'#2A2200'},
        'lavender': {'card_bg':'#EEE9FF','card_border':'#C8BAE8','sel_border':'#6D4FC2','surface':'#FFFFFF','accent':'#6D4FC2','line1':'#A892D8','line2':'#C8BAE8','lbl_bg':'#F7F5FF','lbl_text':'#1E1535'},
    }
    _SECTIONS=[('appearance','🎨','테마'), ('language','🌐','언어 설정'), ('shortcuts','⌨','단축키'), ('license','📄','라이선스')]


    # Apply-immediately signals (window stays open)
    theme_applied     = Signal(str)
    shortcuts_applied = Signal(dict)
    language_applied  = Signal(str)
    output_dir_applied = Signal(str)

    def __init__(self, parent, current_theme='light', current_shortcuts=None, current_language='ko'):
        super().__init__(parent)
        self._chosen=current_theme; self._cards={}; self._nav_btns={}; self._cur='appearance'
        self._shortcuts = dict(current_shortcuts or {})
        self._capture_btns = {}
        self._chosen_lang = current_language
        self._lang_radios = {}
        self.setWindowTitle(_t("settings_title")); self.setFixedSize(820, 580)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setWindowIcon(_make_gear_icon())
        self.setStyleSheet(f"QDialog{{background:{BG};}} QLabel{{background:transparent;color:{TEXT};}}")
        root=QHBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        # ── Sidebar ──────────────────────────────────
        sb=QFrame(); sb.setFixedWidth(176)
        sb.setStyleSheet(f"QFrame{{background:{SRF2};border-right:1px solid {BORDER};}}")
        self._sb=sb
        sl=QVBoxLayout(sb); sl.setContentsMargins(10,20,10,16); sl.setSpacing(4)
        title=QLabel(_t("settings_title")); title.setStyleSheet(f"font-size:16px;font-weight:700;color:{TEXT};padding-left:6px;padding-bottom:10px;"); sl.addWidget(title)
        self._dlg_title=title
        sep=QFrame(); sep.setFrameShape(QFrame.HLine); sep.setFixedHeight(1); sep.setStyleSheet(f"background:{BORDER};border:none;margin-bottom:6px;"); sl.addWidget(sep)
        self._sb_sep=sep
        _nav_keys={"appearance":"settings_nav_theme","shortcuts":"settings_nav_shortcuts","language":"settings_nav_language","license":"settings_nav_license"}
        _nav_icons={"appearance":"theme_line","language":"globe_line","shortcuts":"keyboard_line","license":"license_line"}
        for sid,icon,label in self._SECTIONS:
            btn=QPushButton(_t(_nav_keys.get(sid,sid))); btn.setFixedHeight(38); btn.setCursor(Qt.CursorShape.PointingHandCursor)
            nav_icon_key = _nav_icons.get(sid)
            if nav_icon_key:
                btn.setIcon(_svg_icon(nav_icon_key, MUTED)); btn.setIconSize(QSize(18,18))
            btn.clicked.connect(lambda _,s=sid: self._switch(s)); self._nav_btns[sid]=btn; sl.addWidget(btn)
        sl.addStretch()
        # Version label — bottom of sidebar
        ver_lbl = QLabel(f"v{APP_VERSION}")
        ver_lbl.setStyleSheet(f"color:{MUTED};font-size:11px;padding-left:6px;padding-bottom:4px;")
        self._ver_lbl = ver_lbl  # v1.0.6: store on self for refresh on theme switch
        sl.addWidget(ver_lbl)
        root.addWidget(sb)

        # ── Content area ─────────────────────────────
        right=QFrame(); right.setStyleSheet(f"QFrame{{background:{SURFACE};}}")
        self._right=right
        rl=QVBoxLayout(right); rl.setContentsMargins(28,24,28,20); rl.setSpacing(0)
        self._stack=QStackedWidget(); self._stack.setStyleSheet("background:transparent;"); self._pidx={}
        for sid,_,_ in self._SECTIONS:
            page=getattr(self,f"_page_{sid}")(); idx=self._stack.addWidget(page); self._pidx[sid]=idx
        rl.addWidget(self._stack,stretch=1)

        # ── Bottom bar (divider + status + buttons) ──
        div=QFrame(); div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"background:{BORDER};max-height:1px;border:none;")
        self._bot_div=div
        rl.addSpacing(10); rl.addWidget(div); rl.addSpacing(12)

        bot=QHBoxLayout(); bot.setSpacing(10)
        self._status_lbl=QLabel("")
        self._status_lbl.setStyleSheet(f"color:{ACCENT};font-size:12px;font-weight:600;")
        bot.addWidget(self._status_lbl); bot.addStretch()
        bc=QPushButton(_t("btn_close")); bc.setFixedWidth(80)
        bc.setStyleSheet(f"QPushButton{{background:{SURFACE};border:1.5px solid {BORDER};color:{TEXT};"
                         f"border-radius:8px;padding:8px 0;font-size:13px;}}"
                         f"QPushButton:hover{{background:{SRF2};}}")
        self._bc=bc; bc.clicked.connect(self.close)
        bo=QPushButton(_t("btn_apply")); bo.setFixedWidth(80)
        bo.setStyleSheet(f"QPushButton{{background:{ACCENT};border:none;color:white;"
                         f"border-radius:8px;padding:8px 0;font-size:13px;font-weight:600;}}"
                         f"QPushButton:hover{{background:{ACCENT_HOVER};}}")
        self._bo=bo; bo.setDefault(True); bo.clicked.connect(self._apply_now)
        bot.addWidget(bc); bot.addWidget(bo)
        rl.addLayout(bot)
        root.addWidget(right)
        self._switch('appearance')

    def _switch(self,sid):
        self._cur=sid; self._stack.setCurrentIndex(self._pidx[sid])
        for s,btn in self._nav_btns.items():
            active=(s==sid)
            btn.setStyleSheet(f"QPushButton{{background:{_accent_alpha(0.12) if active else 'transparent'};border:none;border-radius:8px;text-align:left;padding:9px 14px;color:{ACCENT if active else MUTED};font-size:13px;font-weight:{'600' if active else '500'};}}QPushButton:hover{{background:{_accent_alpha(0.12) if active else SRF2};}}")
        # License tab has no settings to apply → hide Apply button
        show_apply = sid not in ('license',)
        self._bo.setVisible(show_apply)

    def _refresh_theme(self):
        """Refresh dialog frame + recreate pages after a theme change.

        v1.0.8: page-internal widgets are recreated in bulk via _recreate_pages()
        to prevent inline-stylesheet residue (the workaround mechanism is automated).
        This method is responsible only for the dialog frame widgets.
        """
        # Refresh dialog frame
        self.setStyleSheet(f"QDialog{{background:{BG};}} QLabel{{background:transparent;color:{TEXT};}}")
        self._sb.setStyleSheet(f"QFrame{{background:{SRF2};border-right:1px solid {BORDER};}}")
        self._dlg_title.setStyleSheet(f"font-size:16px;font-weight:700;color:{TEXT};padding-left:6px;padding-bottom:10px;")
        self._sb_sep.setStyleSheet(f"background:{BORDER};border:none;margin-bottom:6px;")
        # v1.0.8: complete _ver_lbl refresh — v1.0.6 left a "store on self for refresh" comment but the refresh was missing
        self._ver_lbl.setStyleSheet(f"color:{MUTED};font-size:11px;padding-left:6px;padding-bottom:4px;")
        self._right.setStyleSheet(f"QFrame{{background:{SURFACE};}}")
        self._bot_div.setStyleSheet(f"background:{BORDER};max-height:1px;border:none;")
        self._status_lbl.setStyleSheet(f"color:{ACCENT};font-size:12px;font-weight:600;")
        self._bc.setStyleSheet(
            f"QPushButton{{background:{SURFACE};border:1.5px solid {BORDER};color:{TEXT};"
            f"border-radius:8px;padding:8px 0;font-size:13px;}}"
            f"QPushButton:hover{{background:{SRF2};}}")
        self._bo.setStyleSheet(
            f"QPushButton{{background:{ACCENT};border:none;color:white;"
            f"border-radius:8px;padding:8px 0;font-size:13px;font-weight:600;}}"
            f"QPushButton:hover{{background:{ACCENT_HOVER};}}")
        # Refresh dialog window title
        self.setWindowTitle(_t("settings_title"))
        # v1.0.8: page recreation — structural fix for inline-stylesheet color residue
        # (catches the label/frame color residue bug present since v1.0.5; covers 22 widgets that were missing refresh)
        self._recreate_pages()

    # ── v1.0.8: page recreation (structural fix for label color-residue bug) ─
    def _recreate_pages(self):
        """v1.0.8: Recreate pages on theme/language change to bulk-refresh inline-stylesheet colors and
        translated text.

        Background: page-internal widgets embed color values via f-string in their inline stylesheet,
        which freezes them to the theme at creation time (a structural limit since v1.0.5).
        Rather than accumulating per-widget refresh lines for 22 widgets in _refresh_theme,
        we automate the same mechanism as the workaround (re-opening the settings window).

        Page state preservation:
        - Appearance: self._chosen (currently selected theme) — auto-restores card "selected" state
        - Language: self._chosen_lang (currently selected language) — auto-restores radio check
        - Shortcuts: self._shortcuts (current shortcut mapping) — auto-restores capture-button text
        - Output folder: self._odir_edit text — preserves unapplied input
        - License: stateless
        """
        # 1. Safely terminate any in-progress shortcut capture (closeEvent pattern)
        for btn in self._capture_btns.values():
            if btn._capturing:
                btn._stop_capture()

        # 2. Preserve unapplied output-folder input (user typed but hasn't clicked Apply)
        odir_temp = self._odir_edit.text() if hasattr(self, '_odir_edit') else None

        # 3. Remove existing page widgets
        while self._stack.count() > 0:
            old = self._stack.widget(0)
            self._stack.removeWidget(old)
            old.deleteLater()

        # 4. Reset container dicts (will be repopulated as new pages are created)
        self._capture_btns.clear()
        self._lang_radios.clear()
        self._cards.clear()
        self._pidx = {}

        # 5. Create new pages (with current theme/language colors and text)
        for sid, _, _ in self._SECTIONS:
            page = getattr(self, f"_page_{sid}")()
            idx = self._stack.addWidget(page)
            self._pidx[sid] = idx

        # 6. Restore unapplied output-folder input
        if odir_temp is not None and hasattr(self, '_odir_edit'):
            self._odir_edit.setText(odir_temp)

        # 7. Switch to current page (includes nav-button active style refresh)
        self._switch(self._cur)

    # ── Apply settings (window stays open) ───────────
    def _apply_now(self):
        """Apply button — apply theme + shortcuts + language + output folder immediately, keep window open."""
        self.theme_applied.emit(self._chosen)
        self.shortcuts_applied.emit(dict(self._shortcuts))
        self.language_applied.emit(self._chosen_lang)
        # Save output folder + emit signal
        if hasattr(self, '_odir_edit'):
            odir = self._odir_edit.text().strip() or str(_OUTPUT_DIR)
            _CFG._data['output_dir'] = odir
            try: Path(odir).mkdir(parents=True, exist_ok=True)
            except OSError: pass
            self.output_dir_applied.emit(odir)
        self._refresh_theme()
        self._retranslate_dialog()
        self._show_status(_t("settings_applied"))

    def _apply_theme_now(self, name):
        """Theme card double-click — apply only that theme immediately, keep window open."""
        self._chosen = name
        # v1.0.8: removed the card.set_selected loop — _recreate_pages creates new cards with
        # selected=(name==self._chosen) automatically, making the loop unnecessary
        self.theme_applied.emit(name)
        self._refresh_theme()
        self._retranslate_dialog()  # v1.0.6 §2.1 A: stay consistent with _apply_now
        self._show_status(f"✅  '{_theme_label(name)}' {_t('settings_applied')}")

    def _show_status(self, msg: str, ms: int = 2500):
        self._status_lbl.setText(msg)
        QTimer.singleShot(ms, lambda: self._status_lbl.setText("") if self.isVisible() else None)

    def _page_appearance(self):
        page=QWidget(); page.setStyleSheet("background:transparent;"); lay=QVBoxLayout(page); lay.setContentsMargins(0,0,0,0); lay.setSpacing(6)
        title=QLabel(_t("settings_theme_title")); title.setStyleSheet(f"font-size:14px;font-weight:700;color:{TEXT};"); lay.addWidget(title)
        self._theme_page_title=title
        hint=QLabel(_t("settings_theme_hint"))
        hint.setStyleSheet(f"color:{MUTED};font-size:13px;")
        self._theme_page_hint=hint
        lay.addWidget(hint)
        lay.addSpacing(10)
        grid=QGridLayout(); grid.setSpacing(14); grid.setContentsMargins(0,0,0,0)
        names=('light','auto','dark',
               'ocean','mint','sand','honey',
               'sakura','lavender','choco')
        for i, name in enumerate(names):
            cfg=self._CARD_CFG[name]
            card=_ThemeCard(name=name, cfg=cfg, selected=(name==self._chosen),
                            on_click=self._select, on_double_click=self._apply_theme_now)
            self._cards[name]=card; grid.addWidget(card, i//4, i%4)
        grid.setColumnStretch(4, 1)
        lay.addLayout(grid)

        lay.addStretch(); return page

    def _pick_output_dir(self):
        d = QFileDialog.getExistingDirectory(self, _t('settings_output_dir'),
                                              self._odir_edit.text() or str(Path.home()))
        if d:
            self._odir_edit.setText(d)

    def _select(self,name):
        self._chosen=name
        for n,card in self._cards.items(): card.set_selected(n==name)

    def chosen_theme(self): return self._chosen
    def chosen_shortcuts(self): return dict(self._shortcuts)


    def _page_language(self):
        page=QWidget(); page.setStyleSheet("background:transparent;")
        lay=QVBoxLayout(page); lay.setContentsMargins(0,0,0,0); lay.setSpacing(16)

        title=QLabel(_t("settings_lang_title"))
        title.setStyleSheet(f"font-size:14px;font-weight:700;color:{TEXT};")
        lay.addWidget(title)
        self._lang_page_title=title

        desc=QLabel(_t("settings_lang_desc"))
        desc.setStyleSheet(f"color:{MUTED};font-size:12px;")
        desc.setWordWrap(True)
        self._lang_page_desc=desc
        lay.addWidget(desc)

        sep=QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background:{BORDER};max-height:1px;border:none;")
        lay.addWidget(sep)

        lang_frame=QFrame()
        lang_frame.setStyleSheet(
            f"QFrame{{background:{SRF2};border:1px solid {BORDER};"
            f"border-radius:10px;}}")
        lfl=QVBoxLayout(lang_frame); lfl.setContentsMargins(20,16,20,16); lfl.setSpacing(12)

        bg=QButtonGroup(self)
        for code, label in SUPPORTED_LANGUAGES:
            rb=QRadioButton(label)
            rb.setChecked(code == self._chosen_lang)
            rb.setStyleSheet(f"QRadioButton{{font-size:14px;color:{MUTED};spacing:10px;}}"
                             f"QRadioButton::indicator{{width:17px;height:17px;border:1.5px solid {INPUT_H};border-radius:9px;background:{SURFACE};}}"
                             f"QRadioButton::indicator:checked{{border:2px solid {ACCENT};background:{ACCENT};}}")
            rb.toggled.connect(lambda checked, c=code: self._on_lang_selected(c) if checked else None)
            bg.addButton(rb)
            lfl.addWidget(rb)
            self._lang_radios[code] = rb

        lay.addWidget(lang_frame)

        # ── Output folder section ────────────────────
        lay.addSpacing(8)
        sep2 = QFrame(); sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet(f"background:{BORDER};max-height:1px;border:none;")
        lay.addWidget(sep2)
        lay.addSpacing(4)
        odir_title = QLabel(_t('settings_output_dir'))
        odir_title.setStyleSheet(f"font-size:13px;font-weight:600;color:{TEXT};")
        lay.addWidget(odir_title)
        self._lang_odir_title = odir_title
        odir_row = QHBoxLayout(); odir_row.setSpacing(6)
        self._odir_edit = QLineEdit()
        self._odir_edit.setText(_CFG.get('output_dir', str(_OUTPUT_DIR)))
        self._odir_edit.setPlaceholderText(str(_OUTPUT_DIR))
        self._odir_edit.setFixedHeight(32)
        self._odir_edit.setStyleSheet(
            f"QLineEdit{{background:{SURFACE};border:1px solid {BORDER};"
            f"border-radius:6px;padding:2px 8px;color:{TEXT};font-size:13px;}}"
            f"QLineEdit:focus{{border-color:{ACCENT};}}")
        odir_btn = QPushButton(_t('conv_btn_pick'))
        odir_btn.setFixedHeight(32)
        odir_btn.setStyleSheet(
            f"QPushButton{{background:{SURFACE};border:1px solid {BORDER};"
            f"color:{TEXT};border-radius:6px;padding:2px 10px;font-size:13px;}}"
            f"QPushButton:hover{{border-color:{ACCENT};color:{ACCENT};}}")
        odir_btn.clicked.connect(self._pick_output_dir)
        odir_reset = QPushButton(_t('merge_path_reset'))
        odir_reset.setFixedHeight(32)
        odir_reset.setStyleSheet(odir_btn.styleSheet())
        odir_reset.clicked.connect(lambda: self._odir_edit.setText(str(_OUTPUT_DIR)))
        odir_row.addWidget(self._odir_edit, 1)
        odir_row.addWidget(odir_btn)
        odir_row.addWidget(odir_reset)
        lay.addLayout(odir_row)

        lay.addStretch()
        return page

    def _on_lang_selected(self, code):
        self._chosen_lang = code


    def _retranslate_dialog(self):
        """Refresh dialog frame text after a language change.

        v1.0.8: page-internal text is recreated in bulk by _recreate_pages().
        This method is responsible only for frame text — sidebar, nav buttons, bottom buttons, etc.
        """
        # Sidebar title
        self._dlg_title.setText(_t('settings_title'))
        # Nav buttons — translation strings already include icons
        for (sid, _, __), key in zip(self._SECTIONS,
                ['settings_nav_theme', 'settings_nav_language', 'settings_nav_shortcuts', 'settings_nav_license']):
            self._nav_btns[sid].setText(_t(key))
        # Bottom buttons
        self._bc.setText(_t('btn_close'))
        self._bo.setText(_t('btn_apply'))
        # v1.0.8: page-internal text is handled in bulk by _recreate_pages()

    def closeEvent(self, event):
        """On forced dialog close, ensure the in-progress keyboard capture is released."""
        for btn in self._capture_btns.values():
            if btn._capturing: btn._stop_capture()
        super().closeEvent(event)

    def _page_shortcuts(self):
        page=QWidget(); page.setStyleSheet("background:transparent;")
        lay=QVBoxLayout(page); lay.setContentsMargins(0,0,0,0); lay.setSpacing(10)

        title=QLabel(_t("settings_sc_title"))
        title.setStyleSheet(f"font-size:14px;font-weight:700;color:{TEXT};")
        lay.addWidget(title)
        self._sc_page_title=title

        desc=QLabel(_t("settings_sc_desc"))
        desc.setStyleSheet(f"color:{MUTED};font-size:12px;")
        self._sc_page_desc=desc
        lay.addWidget(desc)

        # Header row
        hdr=QHBoxLayout(); hdr.setContentsMargins(0,6,0,2)
        self._sc_hdr_labels=[]
        for txt, w in [(_t("settings_sc_action"), 210), (_t("settings_sc_key"), 140), ("", 60)]:
            lbl=QLabel(txt); lbl.setStyleSheet(f"color:{MUTED};font-size:11px;font-weight:600;letter-spacing:0.5px;")
            if w: lbl.setFixedWidth(w)
            hdr.addWidget(lbl); self._sc_hdr_labels.append(lbl)
        hdr.addStretch(); lay.addLayout(hdr)

        sep=QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background:{BORDER};max-height:1px;border:none;")
        lay.addWidget(sep)

        # Shortcut row
        _sc_label_keys = {'tab_1':'sc_tab_merger','tab_2':'sc_tab_converter',
                          'tab_3':'sc_tab_tag','tab_4':'sc_tab_batch',
                          'tab_5':'sc_tab_fixer','tab_6':'sc_tab_bulk'}
        self._sc_label_keys = _sc_label_keys
        self._sc_action_lbls = {}
        self._sc_reset_btns = {}  # v1.0.6: store on self for refresh on theme/language change
        for sid, info in SHORTCUT_DEFS.items():
            current = self._shortcuts.get(sid, info['default'])
            row=QHBoxLayout(); row.setSpacing(10); row.setContentsMargins(0,4,0,4)

            action_lbl=QLabel(_t(_sc_label_keys.get(sid, sid)))
            action_lbl.setFixedWidth(210)
            action_lbl.setStyleSheet(f"color:{TEXT};font-size:13px;")
            self._sc_action_lbls[sid] = action_lbl

            btn=_KeyCaptureButton(current)
            btn.key_captured.connect(lambda k, s=sid: self._on_key_captured(s, k))
            self._capture_btns[sid]=btn

            reset_btn=QPushButton(_t("btn_reset"))
            reset_btn.setMinimumWidth(58)
            reset_btn.clicked.connect(lambda _, s=sid: self._reset_one(s))
            reset_btn.setStyleSheet(
                f"QPushButton{{background:{SRF2};border:1px solid {BORDER};"
                f"border-radius:6px;color:{MUTED};padding:5px 8px;font-size:12px;}}"
                f"QPushButton:hover{{border-color:{INPUT_H};color:{TEXT};}}")
            self._sc_reset_btns[sid] = reset_btn  # v1.0.6: store on self

            row.addWidget(action_lbl); row.addWidget(btn); row.addWidget(reset_btn)
            row.addStretch(); lay.addLayout(row)

        lay.addStretch()

        # Reset-all defaults button
        sep2=QFrame(); sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet(f"background:{BORDER};max-height:1px;border:none;")
        lay.addWidget(sep2)

        foot=QHBoxLayout()
        note=QLabel(_t("settings_sc_note")); self._sc_note=note
        note.setStyleSheet(f"color:{MUTED};font-size:13px;")
        reset_all=QPushButton(_t("btn_reset_all"))
        reset_all.clicked.connect(self._reset_all)
        reset_all.setStyleSheet(
            f"QPushButton{{background:{SRF2};border:1px solid {BORDER};"
            f"border-radius:7px;color:{MUTED};padding:6px 14px;font-size:12px;}}"
            f"QPushButton:hover{{border-color:{INPUT_H};color:{TEXT};}}")
        self._sc_reset_all_btn = reset_all  # v1.0.6: store on self for refresh on theme/language change
        foot.addWidget(note); foot.addStretch(); foot.addWidget(reset_all)
        lay.addLayout(foot)
        return page

    def _on_key_captured(self, sid, key_str):
        self._shortcuts[sid] = key_str

    def _reset_one(self, sid):
        default = SHORTCUT_DEFS[sid]['default']
        self._shortcuts[sid] = default
        btn = self._capture_btns.get(sid)
        if btn: btn._key_str=default; btn.setText(default); btn._refresh_style()

    def _reset_all(self):
        for sid in SHORTCUT_DEFS: self._reset_one(sid)

    def _page_license(self):
        """License page — open-source notices."""
        page = QWidget(); page.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(page); lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(8)

        title = QLabel(_t("settings_nav_license").strip())
        title.setStyleSheet(f"font-size:14px;font-weight:700;color:{TEXT};")
        self._license_page_title = title
        lay.addWidget(title)

        from PySide6.QtWidgets import QTextBrowser
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setStyleSheet(
            f"QTextBrowser{{background:{SRF2};border:1px solid {BORDER};"
            f"border-radius:10px;padding:4px;color:{TEXT};font-size:13px;}}"
            f"QScrollBar:vertical{{background:{BG};width:8px;border-radius:4px;}}"
            f"QScrollBar::handle:vertical{{background:{BORDER};border-radius:4px;min-height:24px;}}"
            f"QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0px;}}"
        )
        browser.setHtml(_build_license_html())
        self._license_browser = browser
        lay.addWidget(browser, stretch=1)
        return page


def _get_help_data():
    """Return (intro, sections) for the current language."""
    lang = _current_lang
    return _build_help_html(_data_only=True, _lang=lang)


def _build_help_html(_data_only=False, _lang=None) -> str:
    """Help HTML for the current language — commercial-manual quality."""
    lang = _lang or _current_lang
    bg = SURFACE; text = TEXT; muted = MUTED
    accent = ACCENT; border = BORDER; srf2 = SRF2; bg2 = BG

    from PySide6.QtGui import QColor
    def _mix(h1, h2, r=0.12):
        c1=QColor(h1); c2=QColor(h2)
        return f"#{int(c1.red()*(1-r)+c2.red()*r):02X}{int(c1.green()*(1-r)+c2.green()*r):02X}{int(c1.blue()*(1-r)+c2.blue()*r):02X}"
    tip_bg   = _mix(bg, accent, 0.07); tip_bdr = _mix(accent, bg, 0.4)
    warn_bg  = _mix(bg, "#D04030", 0.08); warn_bdr = "#D05040"
    note_bg  = _mix(bg, "#5080D0", 0.07); note_bdr = _mix("#5080D0", bg, 0.4)

    # ─────────────────────────────────────────────────────────────
    # Per-language content
    # ─────────────────────────────────────────────────────────────
    if lang == 'ko':
      intro = ("File Nexus Suite는 텍스트·전자책·미디어 파일 작업에 특화된 통합 파일 도구입니다. 텍스트 병합, EPUB 변환, 파일명 태그 편집, 일괄 이름 변경, 줄바꿈 교정, 일괄 교정 — 여섯 가지 핵심 기능이 하나의 창 안에 있습니다.")
      sections = [

        ("📋", "Text Merger", "여러 파일을 하나의 텍스트 파일로 병합합니다",
         "아래 형식의 파일을 원하는 순서로 이어붙여 하나의 텍스트 파일로 만듭니다. DOCX·PDF·XLSX는 해당 라이브러리가 설치된 경우에만 텍스트를 추출할 수 있습니다.",
         [
          ("formats",[('TXT', 'native'), ('MD', 'native'), ('CSV', 'native'), ('LOG', 'native'), ('JSON', 'native'), ('XML', 'native'), ('HTML', 'native'), ('PY', 'native'), ('DOCX', 'lib'), ('PDF', 'lib'), ('XLSX', 'lib'), ('HWPX', 'lib')]),
          ("step","<b>파일 추가</b> — <code>[📄 파일 추가]</code> 버튼 또는 파일을 목록 위로 드래그 앤 드롭합니다. 지원하지 않는 형식은 자동으로 걸러집니다."),
          ("step","<b>순서 조정</b> — 목록 항목을 드래그하거나 <code>[위로]</code> / <code>[아래로]</code> 버튼으로 병합 순서를 정합니다. 병합 결과물에 파일 순서가 그대로 반영됩니다."),
          ("step","<b>인코딩 설정</b> — 각 파일 오른쪽 콤보박스에서 <b>읽기 인코딩</b>을 선택하고, 우측 '저장 설정' 패널에서 <b>저장 인코딩</b>을 선택합니다."),
          ("step","<b>파일 구분선</b> (선택) — '파일 구분선 삽입' 체크박스를 켜면 각 파일 사이에 파일명을 포함한 구분선이 자동으로 삽입됩니다."),
          ("step","<b>저장 경로 지정</b> (선택) — <code>[경로 지정]</code> 버튼으로 저장 위치를 미리 지정하면 <code>[▶ 병합 및 저장]</code> 클릭 시 자동 저장됩니다. 경로를 지정하지 않으면 실행 시 저장 대화상자가 나타납니다."),
          ("step","<b><code>[▶ 병합 및 저장]</code></b> 클릭 — 완료 메시지에서 파일별 인코딩 요약을 확인할 수 있습니다."),
          ("divider",),
          ("tip","<b>인코딩 자동 감지</b> — chardet 라이브러리가 설치되어 있으면 파일 추가 시 인코딩을 자동 감지합니다. 신뢰도가 낮으면 콤보박스에서 직접 선택하세요."),
          ("tip","<b>저장 인코딩 선택 기준</b> — UTF-8: 범용 권장 / UTF-8-BOM: Excel에서 한글이 깨지지 않음 / EUC-KR·CP949: 구형 한국어 프로그램 호환 / UTF-16: 특수 목적 / <b>Shift-JIS·GBK·Big5</b>: 일본어·중국어(간체·번체) 시스템 호환"),
          ("tip","<b>파일 구분선 형식</b> — 구분선을 켜면 각 파일 앞에 <code>───── ▶ 파일이름.txt ──────</code> 형식의 줄이 삽입됩니다."),
          ("info","파일 읽기 중 오류가 발생하면 해당 파일만 건너뛰고 나머지는 정상적으로 병합됩니다. 오류 내용은 완료 메시지에 표시됩니다."),
          ("warn","<code>[실행 취소]</code> 버튼은 병합 결과 파일 자체를 삭제합니다. <b>원본 파일은 전혀 변경되지 않습니다.</b>"),
         ]),

        ("🔄", "Text Converter", "TXT ↔ EPUB 파일 형식을 변환합니다",
         "소설·원고 작업에 특화된 형식 변환 도구입니다. TXT → EPUB 변환으로 전자책을 만들거나, EPUB → TXT 추출로 텍스트를 편집 가능한 형태로 꺼낼 수 있습니다. 여러 파일을 한 번에 일괄 변환할 수 있습니다.",
         [
          ("note","상단의 <code>[TXT → EPUB]</code> 또는 <code>[EPUB → TXT]</code> 탭을 먼저 선택하세요."),
          ("step","<b>파일 추가</b> — <code>[📄 파일 추가]</code> 버튼 또는 드래그 앤 드롭으로 변환할 파일을 불러옵니다."),
          ("step","<b>TXT → EPUB 설정</b> — 오른쪽 '책 정보' 패널에서 <b>책 제목·저자·언어</b>를 입력하고 <b>챕터 구분 방식</b>을 선택합니다."),
          ("step","<b>EPUB → TXT 설정</b> — 오른쪽 '변환 옵션' 패널에서 챕터 구분선 삽입·챕터 제목 포함·연속 빈 줄 정리·저장 인코딩을 설정합니다."),
          ("step","<b>출력 폴더 지정</b> (선택) — 기본 출력 폴더는 설정에서 지정한 폴더(기본: <code>Output/</code>)입니다. 저장 완료 후 출력 폴더가 자동으로 열립니다."),
          ("step","<b><code>[▶ 변환 시작]</code></b> 클릭 — 파일이 여러 개면 진행 표시줄에서 각 파일의 변환 상태를 확인할 수 있습니다."),
          ("divider",),
          ("feature","TXT → EPUB 챕터 구분 방식","원고의 챕터 표기 방식에 맞는 옵션을 선택하세요. <b>구분선 기준</b> — <code>===</code>, <code>---</code>, <code>★★★</code> 등 반복 기호로 이루어진 줄을 챕터 경계로 인식합니다. <b>빈 줄 3개 이상 기준</b> — 연속 3줄 이상 빈 구간을 챕터 경계로 인식합니다. <b>전체를 한 챕터로</b> — 파일 전체를 하나의 챕터로 처리합니다."),
          ("feature","EPUB → TXT 변환 옵션","<b>챕터 구분선 추가</b> — 챕터 경계에 구분선을 삽입합니다 (기본: 켜짐). <b>챕터 제목 포함</b> — EPUB에 저장된 챕터 제목을 구분선 아래에 표시합니다 (기본: 켜짐). <b>연속 빈 줄 정리</b> — 추출 과정에서 생기는 과도한 빈 줄을 정리합니다 (기본: 켜짐). <b>저장 인코딩</b> — 출력 TXT 파일의 인코딩을 선택합니다 (기본: UTF-8)."),
          ("tip","출력 폴더를 지정하면 원본 폴더를 건드리지 않고 변환 결과만 한 곳에 모을 수 있어 편리합니다."),
          ("tip","변환 중 창을 닫으면 진행이 중단될 수 있습니다. 변환이 완료될 때까지 기다려 주세요."),
         ]),

        ("🏷️", "Tag Editor", "파일명에서 태그를 추가하거나 제거합니다",
         "파일명의 <code>[임시]</code>, <code>[최종]</code> 같은 대괄호 태그를 일괄 추가·제거하고, 불필요한 0 패딩도 한 번에 정리합니다.",
         [
          ("note","작업 종류에 따라 상단 탭에서 <b>[태그 제거]</b> / <b>[태그 추가]</b> / <b>[앞자리 0 제거]</b> 를 선택하세요."),
          ("step","<b>파일 또는 폴더 추가</b> — <code>[📄 파일 추가]</code> / <code>[📂 폴더 추가]</code> 버튼 또는 드래그 앤 드롭으로 대상을 불러옵니다. 폴더를 추가하면 '하위 폴더 포함' 옵션에 따라 재귀적으로 파일을 읽어옵니다."),
          ("step","<b>필터 설정</b> — 왼쪽 하단 '필터 설정' 패널에서 대상 확장자를 지정합니다 (쉼표로 구분). '모든 확장자 대상'을 켜면 확장자 무관하게 전체 파일을 처리합니다."),
          ("step","<b>옵션 설정</b> — 오른쪽 패널에서 각 모드에 맞는 옵션을 설정합니다."),
          ("step","<b>미리보기 확인</b> — <code>[미리보기]</code>를 클릭해 '원본 파일명 → 변경 후 파일명' 표를 확인합니다. <b>결과를 반드시 확인한 후 적용하세요.</b>"),
          ("step","<b>적용</b> — 결과가 올바르면 <code>[적용]</code>을 클릭합니다."),
          ("divider",),
          ("feature","태그 제거","오른쪽 패널 태그 입력란에 특정 태그를 입력하면 그 태그만 제거합니다. <b>입력란을 비워두면 파일명의 모든 <code>[ ]</code> 형식 태그를 제거합니다.</b> 예) 입력란에 <code>최종</code> 입력 → <code>[최종]</code>만 제거, 나머지 태그는 그대로 유지"),
          ("feature","태그 추가","오른쪽 패널에서 추가할 태그와 삽입 위치(파일명 <b>앞</b> / <b>뒤</b>)를 선택합니다. 동일한 태그가 이미 있으면 중복 추가되지 않습니다."),
          ("feature","앞자리 0 제거","파일명 앞에 붙은 불필요한 0을 자동으로 제거합니다 (001 → 1, 007 → 7). 단, <code>2024-01-01</code>처럼 하이픈으로 연결된 <b>날짜 형식의 숫자는 건드리지 않고 그대로 보존됩니다.</b>"),
          ("example","회의록 001.docx","회의록 1.docx"),
          ("example","강의자료 007 최종본.pdf","강의자료 7 최종본.pdf"),
          ("example","2024-01-01 일기.txt","2024-01-01 일기.txt  ← 보호, 변경 없음"),
          ("warn","<b>파일명 변경 후 [실행 취소]로 한 번 복구할 수 있습니다.</b> 단, 새 작업을 실행하거나 창을 닫으면 복구 데이터가 사라집니다. <code>[미리보기]</code>로 결과를 반드시 확인한 후 <code>[적용]</code>하세요."),
         ]),

        ("📁", "Batch Renamer", "폴더 및 파일 이름을 일괄 변경합니다",
         "하위 폴더 또는 파일의 이름을 패턴 기반으로 한 번에 바꿉니다. 번호를 자동으로 인식하는 '스마트 추출'과 번호를 직접 지정하는 '순차 번호' 두 방식을 지원합니다.",
         [
          ("note","상단 탭에서 <b>[폴더 이름 변경]</b> 또는 <b>[파일 이름 변경]</b> 을 먼저 선택하세요."),
          ("step","<b>대상 폴더 지정</b> — <code>[📂 폴더 선택]</code> 또는 드래그 앤 드롭으로 <b>상위 폴더</b>를 지정합니다. 지정한 폴더 자체는 변경되지 않고, <b>그 안의 하위 항목만</b> 이름이 바뀝니다."),
          ("step","<b>방식 선택</b> — 오른쪽 패널에서 '스마트 추출' 또는 '순차 번호'를 선택합니다."),
          ("step","<b>미리보기 확인</b> — <code>[미리보기]</code>를 클릭해 변경 결과를 확인합니다. 이름이 충돌하는 경우 표에서 경고가 표시됩니다."),
          ("step","<b>이름 변경 실행</b> — <code>[이름 변경 실행]</code>을 클릭합니다. 실행 직후 <code>[실행 취소]</code>로 한 번 복구할 수 있습니다."),
          ("divider",),
          ("feature","🔍 스마트 추출","기존 이름에서 숫자를 자동으로 추출해 재구성합니다. <b>공통 접두어 처리</b> — 자동 감지 / 직접 지정 / 제거 안 함 중 선택. <b>접두사·접미사</b> — 재구성된 이름 앞뒤에 추가할 텍스트를 입력합니다."),
          ("feature","🔢 순차 번호","처음부터 끝까지 순서대로 번호를 부여합니다. <b>시작 번호</b> — 00 또는 01부터 선택. <b>자릿수</b> — 자동 또는 2·3·4자리 고정. <b>접두사·접미사</b> — 번호 앞뒤에 붙일 텍스트. <b>이름 보존</b> — '숫자만' 또는 '숫자 + 원래이름'. <b>번호 리셋</b> — '전체 연속' 또는 '그룹마다 리셋'."),
          ("tip","파일 이름 변경에서 확장자는 항상 자동으로 유지됩니다."),
          ("tip","폴더를 드래그하면 하위 폴더까지 재귀적으로 탐색하여 자동으로 그룹을 구성합니다."),
          ("tip","이름 변경 실행 전 대상 폴더를 열어둔 탐색기 창은 자동으로 닫히며, 이름 변경 완료 후 자동으로 다시 열립니다."),
          ("warn","<b>이름 변경은 즉시 적용됩니다.</b> 실행 직후 <code>[실행 취소]</code>로 복구할 수 있지만, 새 작업을 실행하거나 창을 닫으면 복구 데이터가 사라집니다."),
          ("warn","지정한 상위 폴더 자체는 변경되지 않습니다. 하위 항목만 대상입니다."),
         ]),

        ("✦", "Text Fixer", "OCR·전자책 텍스트의 줄바꿈을 교정합니다",
         "PDF나 EPUB에서 추출한 텍스트는 페이지 너비에서 줄이 강제로 잘리는 문제가 있습니다. Text Fixer는 이를 지능적으로 복원하고 단락 구조를 정리합니다.",
         [
          ("note","<b>텍스트 입력 방법</b> — 상단 드롭존에 .txt 파일을 드래그하거나, <code>[📂 파일 열기]</code>로 불러오거나, 왼쪽 '원본 텍스트' 창에 직접 붙여넣기 할 수 있습니다."),
          ("step","<b>텍스트 입력</b> — 텍스트를 불러오거나 왼쪽 창에 붙여넣습니다."),
          ("step","<b>옵션 선택</b> — 아래 네 가지 옵션을 필요에 따라 조합합니다. 처음에는 <b>① + ④</b> 조합으로 시작해 보세요."),
          ("step","<b><code>[✦ 수정 실행]</code></b> 클릭 — 왼쪽(원본)과 오른쪽(결과) 창을 나란히 비교해 결과를 확인하세요."),
          ("step","<b>저장</b> — 결과가 마음에 들면 <code>[저장 ▼]</code>을 클릭합니다. 마음에 들지 않으면 <code>[실행 취소]</code>로 원본을 복원한 뒤 옵션을 바꿔 다시 시도하세요."),
          ("divider",),
          ("feature","① 줄바꿈 병합 (빈 줄 기준)","빈 줄을 기준으로 단락을 나누고, 단락 안에서 강제로 잘린 줄을 하나로 이어붙입니다. <b>이어붙이지 않는 경우</b> — 마침표·느낌표·물음표·따옴표 등으로 끝나는 줄, 그리고 <code>───</code>·<code>===</code>·<code>★★★</code> 같은 구분선은 이어붙이지 않습니다. PDF·EPUB 텍스트 교정의 핵심 옵션입니다. 대부분의 경우 먼저 켜세요."),
          ("feature","② 자동 단락 분리 (최대 N자)","① 옵션으로 병합 후 너무 길어진 줄을 문장 경계에서 N자 기준으로 나눕니다. 짧은 문장끼리는 N자 안에서 자동으로 묶입니다. 기본값 100자. 소설 원고처럼 문장이 길게 이어지는 경우 150~200자로 늘려 보세요."),
          ("feature","③ 문장마다 빈 줄 삽입","마침표·따옴표로 끝나는 줄 뒤, 또는 대화문(<code>\"</code>) 앞에 빈 줄을 자동 삽입합니다. 대화가 많은 소설 원고에서 문단 가독성을 높일 때 사용합니다."),
          ("feature","④ 과도한 빈 줄 축소 (최대 N줄)","연속으로 이어지는 빈 줄을 최대 N줄로 줄입니다. 기본값 1줄 권장. 여러 섹션으로 구성된 문서는 2줄로 설정하세요."),
          ("divider",),
          ("tip","<b>추천 조합</b> — PDF·EPUB 추출 텍스트 교정: <b>① + ④</b> / 대화 중심 소설 원고: <b>① + ③</b> / OCR 결과물·긴 단락 정리: <b>① + ② + ④</b>"),
          ("tip","<b>저장 방식</b> — <b>원본 위치에 [Fixed] 태그로 저장</b>: 원본은 그대로 두고 교정본을 <code>[Fixed]파일명.txt</code>로 저장 / <b>다른 이름으로 저장</b>: 위치와 파일명 직접 지정 / <b>실행 취소</b>: 수정 전 원본 텍스트를 왼쪽 창에 복원 (수정 실행 후 1회 가능)"),
          ("tip","🟡 <b>노란 줄</b> = 여러 줄이 병합된 부분 / 🟠 <b>주황 줄</b> = 빈 줄이 제거된 위치. 결과 창에서 변경 위치를 시각적으로 확인할 수 있습니다. 3,000줄 이상의 대용량 파일은 하이라이팅이 생략됩니다."),
          ("tip","하단 통계 바에서 <b>병합 횟수·빈 줄 제거 수·원본 줄 수·최종 줄 수</b>를 확인할 수 있습니다."),
          ("tip","<b>Ctrl+F</b>로 원본·수정본 텍스트에서 키워드를 검색할 수 있습니다. Enter로 다음, Shift+Enter로 이전 결과로 이동합니다."),
          ("warn","저장은 항상 <b>UTF-8</b> 인코딩으로 이루어집니다. 원본 인코딩(EUC-KR 등)을 유지해야 하는 경우 별도로 인코딩을 변환하세요."),
          ("divider",),
          ("note","<b>부분 손상 파일 처리</b> — 일부 바이트가 손상된 파일도 열 수 있습니다. 깨진 문자는 <code>�</code> (U+FFFD) 로 표시되며, 상태 표시줄에 <b>⚠</b> 아이콘과 '부분 인코딩 실패' 경고가 표시됩니다."),
          ("tip","Text Fixer는 <b>단일 파일 정밀 검토</b>에 최적화되어 있습니다. 손상된 파일을 열어 깨진 위치를 직접 확인하고, 필요하면 그 구간만 수동으로 편집하거나 원본을 다시 확보할지 판단할 수 있습니다."),
          ("warn","수만 자 이상의 대량 손상이 있는 파일은 교정해도 품질 회복이 어렵습니다. 원본 출처에서 재다운로드를 먼저 고려하세요. Bulk Fixer에서는 이런 파일을 자동으로 스킵하여 원본을 보호합니다."),
         ]),

        ("✦", "Bulk Fixer", "여러 TXT 파일의 줄바꿈을 일괄 교정합니다",
         "Text Fixer의 교정 기능을 여러 파일에 한꺼번에 적용합니다. OCR·전자책에서 추출한 TXT 파일 다수를 한 번에 정리할 때 사용합니다.",
         [
          ("step","<b>파일 추가</b> — <code>[📄 파일 추가]</code> 또는 <code>[📂 폴더 추가]</code>로 TXT 파일을 불러옵니다. 파일 목록에 폴더를 직접 드래그 앤 드롭해도 하위 <code>.txt</code> 파일이 재귀적으로 수집됩니다."),
          ("step","<b>교정 옵션 선택</b> — 오른쪽 패널에서 병합 모드(자동/한국어/영어)와 네 가지 교정 옵션을 설정합니다. <b>프리셋</b> 콤보박스에서 '일반 문서' 또는 '책·소설'을 선택하면 옵션이 한 번에 설정됩니다."),
          ("step","<b>저장 설정</b> — 출력 폴더를 지정하거나 비워두면 원본 파일과 같은 위치에 <code>[Fixed]파일명.txt</code>로 저장됩니다. <b>폴더 구조 유지</b> 체크박스를 켜면 출력 폴더 안에 원본의 하위 폴더 구조가 그대로 재현됩니다."),
          ("step","<b><code>[▶ 일괄 교정 시작]</code></b> 클릭 — 진행률이 표시되며, 완료 후 성공·실패 파일 수를 알려줍니다."),
          ("tip","파일 목록에서 항목을 클릭하면 오른쪽 미리보기 창에서 해당 파일의 교정 결과를 미리 확인할 수 있습니다."),
          ("tip","<b>출력 폴더</b> 기본값은 <code>Output/</code> 폴더입니다. ⚙ 설정에서 전역으로 변경하거나 각 탭에서 개별 지정할 수 있습니다. 저장 완료 후 자동으로 열립니다."),
          ("warn","TXT 파일만 지원합니다. DOCX·PDF 등 다른 형식은 먼저 Text Converter로 TXT로 변환한 뒤 사용하세요."),
          ("divider",),
          ("note","<b>인코딩 손상 파일 자동 분류</b> — Bulk Fixer는 부분 손상 파일을 감지하면 손상 정도에 따라 3단계로 나누어 처리합니다:<br>• <b>Tier 1</b> (1~500자 손상): 교정 후 리포트 파일 생성<br>• <b>Tier 2</b> (501~5,000자 손상): 교정 후 리포트 파일 생성 (검토 권장)<br>• <b>Tier 3</b> (5,001자 이상): <b>자동 스킵 (원본 보호)</b> + 리포트 파일만 생성"),
          ("tip","리포트 파일은 <code>{원본파일명}.encoding_report.txt</code> 형태로 교정본 옆에 생성됩니다. 어느 줄·어느 컬럼이 손상됐는지 최대 5,000건까지 상세 기록됩니다."),
          ("warn","Tier 3로 스킵된 파일은 <b>Text Fixer에서 개별 검토</b>하세요. 대량 손상은 잘못된 인코딩 감지이거나 원본 파일 자체의 문제일 가능성이 높아, 일괄 교정 대신 원본을 재확보하는 것이 낫습니다."),
         ]),

        ("⌨️", "단축키 및 기타", "",
         "",
         [
          ("shortcut","Ctrl+1","Text Merger 탭으로 이동"),
          ("shortcut","Ctrl+2","Text Converter 탭으로 이동"),
          ("shortcut","Ctrl+3","Tag Editor 탭으로 이동"),
          ("shortcut","Ctrl+4","Batch Renamer 탭으로 이동"),
          ("shortcut","Ctrl+5","Text Fixer 탭으로 이동"),
          ("shortcut","Ctrl+6","Bulk Fixer 탭으로 이동"),
          ("shortcut","Ctrl+F","Text Fixer에서 텍스트 검색"),
          ("shortcut","⚙ 버튼 (우상단)","설정 창 열기 — 테마·언어·단축키 변경 가능"),
          ("tip","설정(테마·언어·단축키)은 앱 종료 시 자동 저장되며, 다음 실행 시 복원됩니다."),
          ("tip","모든 탭에서 파일을 <b>드래그 앤 드롭</b>으로 바로 불러올 수 있습니다. 폴더를 드롭하면 해당 폴더의 지원 파일이 일괄 추가됩니다."),
          ("tip","🔋 <b>절전 방지</b> — Text Merger·Text Converter·Text Fixer·Bulk Fixer에서 작업이 실행되는 동안 Windows 절전 모드 진입이 자동으로 차단됩니다. 작업 완료 또는 오류 발생 시 즉시 해제됩니다. 화면 잠금은 절전과 무관하므로 작업 중에도 정상 동작합니다."),
         ]),


        ("📁", "생성 파일 안내", "프로그램 사용 중 자동으로 생성되는 파일과 폴더",
         "File Nexus Suite는 설정 저장, 기본 출력, 오류 기록을 위해 프로그램 실행 파일과 같은 폴더에 아래 항목을 자동으로 생성합니다.",
         [
          ("step","<b>FileNexusSuite.json</b> — 테마·언어·단축키·각 탭 설정이 저장되는 환경설정 파일입니다. 앱 종료 시 자동 저장되고, 다음 실행 시 복원됩니다."),
          ("step","<b>Output/</b> — Text Converter, Bulk Fixer, Text Fixer의 기본 출력 폴더입니다. 첫 실행 시 자동 생성됩니다. ⚙ 설정에서 위치를 전역으로 변경할 수 있으며, 저장 완료 시 자동으로 열립니다."),
          ("step","<b>logs/crash_*.log</b> — 예기치 않은 오류 발생 시 자동으로 생성되는 크래시 로그입니다. 최근 3개만 유지되며 오래된 파일은 자동 삭제됩니다."),
          ("warn","<b>_internal/</b> — exe 빌드(폴더 형태) 시 자동 생성되는 Python 런타임 폴더입니다. <b>삭제하면 프로그램이 실행되지 않습니다.</b>"),
          ("tip","생성된 파일과 폴더는 직접 삭제해도 무방합니다. 다음 실행 시 필요한 항목은 자동으로 다시 생성됩니다."),
         ]),

      ]

    elif lang == 'en':
      intro = 'File Nexus Suite is an integrated file utility for managing text, e-books, and media files. Text merging, EPUB conversion, file-name tag editing, batch renaming, line-break correction, and bulk fixing — six core features, all in one window.'
      sections = [
        ('📋','Text Merger','Merge multiple files into a single text file',
         'Combine files of the formats below into one text file in any order. DOCX, PDF, and XLSX require the respective libraries to be installed.',
         [
          ('formats',[('TXT', 'native'), ('MD', 'native'), ('CSV', 'native'), ('LOG', 'native'), ('JSON', 'native'), ('XML', 'native'), ('HTML', 'native'), ('PY', 'native'), ('DOCX', 'lib'), ('PDF', 'lib'), ('XLSX', 'lib'), ('HWPX', 'lib')]),
          ('step','<b>Add files</b> — Click <code>[📄 Add Files]</code> or drag and drop files onto the list. Unsupported formats are filtered out automatically.'),
          ('step','<b>Set order</b> — Drag items in the list or use <code>[Up]</code> / <code>[Down]</code> to set the merge order.'),
          ('step',"<b>Set encoding</b> — Select the <b>read encoding</b> for each file via the combo box, and choose the <b>save encoding</b> in the 'Save Settings' panel."),
          ('step',"<b>File separator</b> (optional) — Enable 'Insert File Separator' to automatically insert a divider line with the filename between each file."),
          ('step','<b>Set save path</b> (optional) — Click <code>[Set Path]</code> to pre-select a save location. If not set, a save dialog will appear when you run the merge.'),
          ('step','<b><code>[▶ Merge & Save]</code></b> — Click to merge. The completion message shows a per-file encoding summary.'),
          ('divider',),
          ('tip','<b>Auto encoding detection</b> — If chardet is installed, encoding is detected automatically when files are added. If accuracy is low, select manually.'),
          ('tip','<b>Save encoding guide</b> — UTF-8: general use / UTF-8-BOM: prevents garbled text in Excel / EUC-KR·CP949: legacy Korean apps / UTF-16: special use / <b>Shift-JIS·GBK·Big5</b>: Japanese / Chinese (Simplified·Traditional) legacy systems'),
          ('tip','<b>Separator format</b> — When enabled, the following line is inserted before each file: <code>───── ▶ filename.txt ──────</code>'),
          ('info','If a file fails to read, it is skipped and the rest are merged normally. Errors are shown in the completion message.'),
          ('warn','<code>[Undo]</code> deletes the merged output file. <b>Original files are never modified.</b>'),
         ]),

        ('🔄','Text Converter','Convert between TXT and EPUB formats',
         'Convert TXT files into EPUB e-books, or extract text from EPUB files. Multiple files are converted automatically in sequence.',
         [
          ('note','Select <b>[TXT → EPUB]</b> or <b>[EPUB → TXT]</b> at the top first.'),
          ('step','<b>Add files</b> — Click <code>[📄 Add Files]</code> or drag and drop.'),
          ('step',"<b>TXT → EPUB settings</b> — Enter <b>title, author, and language</b> in the 'Book Info' panel and choose a <b>chapter splitting method</b>."),
          ('step',"<b>EPUB → TXT settings</b> — Configure chapter separator, title inclusion, blank line cleanup, and save encoding in the 'Conversion Options' panel."),
          ('step','<b>Output folder</b> (optional) — The default output folder is set in ⚙ Settings (default: <code>Output/</code>). The folder opens automatically after saving.'),
          ('step','<b><code>[▶ Start Conversion]</code></b> — The progress bar shows the status of each file.'),
          ('divider',),
          ('feature','TXT → EPUB Chapter Splitting','<b>Divider-based</b> — Lines made of repeating symbols like <code>===</code>, <code>---</code>, or <code>★★★</code> are treated as chapter boundaries.<br><br><b>3+ blank lines</b> — Sections separated by 3 or more consecutive blank lines are treated as chapters.<br><br><b>Single chapter</b> — The entire file is treated as one chapter.'),
          ('feature','EPUB → TXT Conversion Options','<b>Add chapter separator</b> — Inserts a divider at each chapter boundary (default: on).<br><b>Include chapter titles</b> — Displays chapter titles from the EPUB below the divider (default: on).<br><b>Clean up blank lines</b> — Removes excessive blank lines generated during extraction (default: on).<br><b>Save encoding</b> — Choose the encoding for the output TXT file (default: UTF-8).'),
          ('tip','Setting an output folder keeps results separate from your originals, making it easy to collect all converted files in one place.'),
          ('tip','Do not close the window while conversion is in progress — it may interrupt the process.'),
         ]),

        ('🏷️','Tag Editor','Add or remove tags from file names in bulk',
         'Batch-add or batch-remove bracket tags like <code>[Draft]</code> or <code>[Final]</code> from file names, and clean up leading zeros all at once.',
         [
          ('note','Choose <b>[Remove Tags]</b>, <b>[Add Tags]</b>, or <b>[Remove Leading Zeros]</b> from the top tab first.'),
          ('step',"<b>Add files or folders</b> — Use <code>[📄 Add Files]</code> / <code>[📂 Add Folder]</code> or drag and drop. Adding a folder reads files recursively based on the 'Include subfolders' option."),
          ('step',"<b>Filter settings</b> — Specify target extensions in the 'Filter' panel (comma-separated). Enable 'All extensions' to process all files regardless of type."),
          ('step','<b>Configure options</b> — Set mode-specific options in the right panel.'),
          ('step',"<b>Preview</b> — Click <code>[Preview]</code> to see the 'Before → After' table. <b>Always verify before applying.</b>"),
          ('step','<b>Apply</b> — Click <code>[Apply]</code> if the results look correct.'),
          ('divider',),
          ('feature','Remove Tags','Enter a specific tag in the tag field to remove only that tag. <b>Leave the field empty to remove all <code>[ ]</code> bracket tags.</b><br><br>Example: entering <code>Final</code> removes only <code>[Final]</code>, leaving other tags intact.'),
          ('feature','Add Tags','Choose the tag to add and its position (<b>front</b> or <b>back</b> of the filename) in the right panel. If the tag already exists, it will not be added again.'),
          ('feature','Remove Leading Zeros','Automatically removes leading zeros from file names (001 → 1, 007 → 7). <b>Numbers connected by hyphens, such as dates, are automatically protected.</b>'),
          ('example','Meeting notes 001.docx','Meeting notes 1.docx'),
          ('example','Lecture 007 final.pdf','Lecture 7 final.pdf'),
          ('example','2024-01-01 diary.txt','2024-01-01 diary.txt  ← protected, no change'),
          ('warn','<b>File renaming can be undone once with [Undo] immediately after applying.</b> However, the undo data is lost if you run another task or close the window. Always verify with <code>[Preview]</code> before clicking <code>[Apply]</code>.'),
         ]),

        ('📁','Batch Renamer','Rename folders and files in bulk',
         "Rename subfolders or files using pattern-based rules. Supports 'Smart Extract' (auto-detect) and 'Sequential Number' (manual) modes.",
         [
          ('note','Select <b>[Folder Rename]</b> or <b>[File Rename]</b> from the top tab first.'),
          ('step','<b>Select target folder</b> — Use <code>[📂 Select Folder]</code> or drag and drop to specify the <b>parent folder</b>. The folder itself is not changed — only its <b>contents</b> are renamed.'),
          ('step',"<b>Select method</b> — Choose 'Smart Extract' or 'Sequential Number' in the right panel."),
          ('step','<b>Preview</b> — Click <code>[Preview]</code> to review changes. Conflicts are highlighted in the table.'),
          ('step','<b>Rename</b> — Click <code>[Rename]</code>. You can undo once with <code>[Undo]</code> immediately after.'),
          ('divider',),
          ('feature','🔍 Smart Extract','Automatically extracts numbers from existing names and reconstructs them.<br><br><b>Common prefix handling</b> — Auto-detect / Manual entry / Keep as-is.<br><b>Prefix · Suffix</b> — Text to add before or after the reconstructed name.'),
          ('feature','🔢 Sequential Number',"Assigns numbers in sequence from first to last. All options are set manually.<br><br><b>Start number</b> — Choose 00 or 01. <b>Digits</b> — Auto or fixed 2/3/4. <b>Prefix · Suffix</b> — Text around the number. <b>Name preservation</b> — 'Number only' or 'Number + original name'. <b>Number reset</b> — 'Continuous' or 'Reset per group'."),
          ('tip','File extensions are always preserved automatically.'),
          ('tip','Dragging a folder recursively scans subfolders and builds groups automatically.'),
          ('tip','Explorer windows open to the target folder are automatically closed before renaming and reopened when done.'),
          ('warn','<b>Renaming takes effect immediately.</b> You can undo once with <code>[Undo]</code>, but the data is lost when you run another task or close the window.'),
          ('warn','The specified parent folder itself is not modified. Only its contents are renamed.'),
         ]),

        ('✦','Text Fixer','Repair line breaks in OCR and e-book text',
         'Text extracted from PDFs or EPUBs often has forced line breaks at page width. Text Fixer intelligently restores paragraph structure.',
         [
          ('note',"<b>Input methods</b> — Drag a .txt file onto the drop zone, use <code>[📂 Open File]</code>, or paste text directly into the left 'Original Text' pane."),
          ('step','<b>Load text</b> — Open a file or paste text into the left pane.'),
          ('step','<b>Choose options</b> — Combine the four options as needed. Start with <b>① + ④</b> for most cases.'),
          ('step','<b><code>[✦ Fix]</code></b> — Compare the left (original) and right (result) panes side by side.'),
          ('step','<b>Save</b> — Click <code>[Save ▼]</code> if satisfied. If not, use <code>[Undo]</code> to restore the original and retry with different options.'),
          ('divider',),
          ('feature','① Merge Line Breaks (blank-line basis)','Splits text into paragraphs by blank lines, then merges forced line breaks within each paragraph. <b>Not merged</b> — Lines ending with period, exclamation, question mark, or quote; and divider lines like <code>───</code>, <code>===</code>, <code>★★★</code>. This is the core option for fixing PDF/EPUB text. Enable it first in most cases.'),
          ('feature','② Auto Paragraph Split (max N chars)','After merging, splits overly long lines at sentence boundaries based on a character limit. Short sentences are grouped together within the limit. Default: 100 chars. Try 150-200 for long-sentence manuscripts.'),
          ('feature','③ Insert Blank Line Between Sentences','Inserts a blank line after lines ending with period/quote, or before dialogue. Useful for improving readability in dialogue-heavy text.'),
          ('feature','④ Reduce Excessive Blank Lines (max N lines)','Collapses consecutive blank lines to a maximum of N. Default 1 is recommended. Use 2 for multi-section documents.'),
          ('divider',),
          ('tip','<b>Recommended combinations</b> — PDF/EPUB text: <b>① + ④</b> / Dialogue-heavy text: <b>① + ③</b> / OCR output with long paragraphs: <b>① + ② + ④</b>'),
          ('tip','<b>Save options</b> — <b>Save as [Fixed] beside original</b>: keeps original, saves corrected version as <code>[Fixed]filename.txt</code> / <b>Save As</b>: choose location and name / <b>Undo</b>: restores the pre-fix text in the left pane (available once after running Fix)'),
          ('tip','🟡 <b>Yellow lines</b> = lines merged from multiple / 🟠 <b>Orange lines</b> = blank line removed. Highlighting is skipped for files over 3,000 lines.'),
          ('tip','The status bar at the bottom shows <b>merge count, blank lines removed, original line count, and final line count</b>.'),
          ('tip','Press <b>Ctrl+F</b> to search within the source and result text. Enter jumps to the next match, Shift+Enter to the previous.'),
          ('warn','Files are always saved as <b>UTF-8</b>. Convert the encoding separately if you need to preserve the original (e.g. EUC-KR).'),
          ('divider',),
          ('note',"<b>Partially corrupted files</b> — Files with damaged bytes can still be opened. Corrupted characters are shown as <code>�</code> (U+FFFD), and the status bar shows a <b>⚠</b> icon with a 'Partial encoding failure' warning."),
          ('tip','Text Fixer is optimized for <b>detailed inspection of a single file</b>. Open corrupted files to see exactly where the damage is, edit those spots manually, or decide whether to re-acquire the original.'),
          ('warn','Files with tens of thousands of corrupted characters rarely recover well. Re-downloading from the source is usually better. Bulk Fixer automatically skips such files to protect the originals.'),
         ]),

        ('✦','Bulk Fixer','Batch-correct line breaks across multiple TXT files',
         'Applies the Text Fixer correction engine to many files at once. Ideal for cleaning up batches of TXT files extracted from OCR or e-books.',
         [
          ('step','<b>Add files</b> — Use <code>[📄 Add files]</code> or <code>[📂 Add folder]</code> to load TXT files. You can also drag and drop folders directly onto the file list to recursively collect <code>.txt</code> files.'),
          ('step','<b>Set options</b> — Choose the merge mode (Auto / Korean / English) and correction options in the right panel. Use the <b>Preset</b> dropdown to quickly apply "General document" or "Book / Novel" settings.'),
          ('step','<b>Save settings</b> — Specify an output folder, or leave it empty to save as <code>[Fixed]filename.txt</code> beside each original file. Enable <b>Preserve folder structure</b> to recreate the original subfolder hierarchy inside the output folder.'),
          ('step','<b>Click <code>[▶ Start batch fix]</code></b> — Progress is shown during processing; a summary of successes and failures is displayed on completion.'),
          ('tip','Click any file in the list to preview the corrected result in the preview panel on the right.'),
          ('tip','The default output folder is <code>Output/</code>. You can change it globally in ⚙ Settings or per-tab individually. The folder opens automatically after saving.'),
          ('warn','Only TXT files are supported. Convert DOCX, PDF, etc. to TXT with Text Converter first.'),
          ('divider',),
          ('note','<b>Automatic corruption tiering</b> — Bulk Fixer classifies partially corrupted files into three tiers based on damage severity:<br>• <b>Tier 1</b> (1–500 damaged chars): Fixed + report generated<br>• <b>Tier 2</b> (501–5,000 damaged chars): Fixed + report generated (review recommended)<br>• <b>Tier 3</b> (5,001+ damaged chars): <b>Automatically skipped (original preserved)</b> + report only'),
          ('tip','Reports are created next to the fixed output as <code>{original_filename}.encoding_report.txt</code>, detailing damaged line/column positions for up to 5,000 entries.'),
          ('warn','Files skipped as Tier 3 should be <b>individually reviewed in Text Fixer</b>. Heavy corruption usually means wrong encoding detection or a corrupted source, so re-acquiring the original is often better than forcing correction.'),
         ]),

        ('⌨️','Shortcuts & Tips','',
         'Use keyboard shortcuts to navigate quickly. All shortcuts can be customized in Settings.',
         [
          ('shortcut','Ctrl+1','Go to Text Merger'),
          ('shortcut','Ctrl+2','Go to Text Converter'),
          ('shortcut','Ctrl+3','Go to Tag Editor'),
          ('shortcut','Ctrl+4','Go to Batch Renamer'),
          ('shortcut','Ctrl+5','Go to Text Fixer'),
          ('shortcut','Ctrl+6','Go to Bulk Fixer'),
          ('shortcut','Ctrl+F','Search text in Text Fixer'),
          ('shortcut','⚙ button (top right)','Open Settings — change theme, language, and shortcuts'),
          ('tip','Settings (theme, language, shortcuts) are saved automatically on exit and restored on next launch.'),
          ('tip','<b>Drag and drop</b> is supported in all tabs. Dropping a folder adds all supported files inside it at once.'),
          ('tip','🔋 <b>Sleep Prevention</b> — While Text Merger, Text Converter, Text Fixer, or Bulk Fixer is running, Windows sleep mode is automatically blocked. It is released immediately when the task completes or an error occurs. Screen lock is unaffected.'),
         ]),


        ('📁','File creation notice','Files and folders created automatically during use',
         'File Nexus Suite automatically creates the following items in the program folder for settings storage, default output, and error logging.',
         [
          ('step','<b>FileNexusSuite.json</b> — Stores your theme, language, shortcuts, and tab settings. Saved on exit, restored on next launch.'),
          ('step','<b>Output/</b> — Default output folder for Text Converter, Bulk Fixer, and Text Fixer. Created automatically on first launch. Change the location globally in ⚙ Settings; the folder opens automatically after saving.'),
          ('step','<b>logs/crash_*.log</b> — Crash logs generated when an unexpected error occurs. Only the 3 most recent logs are kept; older ones are deleted automatically.'),
          ('warn','<b>_internal/</b> — Created automatically in folder-style exe builds. Contains the Python runtime. <b>Deleting it will prevent the program from running.</b>'),
          ('tip','You can safely delete any of these files or folders. Required items will be recreated automatically on the next launch.'),
         ]),

      ]

    elif lang == 'ja':
      intro = 'File Nexus Suite はテキスト・電子書籍・メディアファイル作業に特化した統合ファイルツールです。テキスト結合、EPUB変換、ファイル名タグ編集、一括リネーム、改行校正、一括補正 — 6つの主要機能が1つのウィンドウにまとまっています。'
      sections = [
        ('📋','Text Merger','複数ファイルを1つのテキストファイルに結合します',
         '以下の形式のファイルを任意の順序で結合して1つのテキストファイルを作成します。DOCX・PDF・XLSXは対応ライブラリがインストールされている場合のみ利用できます。',
         [
          ('formats',[('TXT', 'native'), ('MD', 'native'), ('CSV', 'native'), ('LOG', 'native'), ('JSON', 'native'), ('XML', 'native'), ('HTML', 'native'), ('PY', 'native'), ('DOCX', 'lib'), ('PDF', 'lib'), ('XLSX', 'lib'), ('HWPX', 'lib')]),
          ('step','<b>ファイル追加</b> — <code>[📄 ファイル追加]</code>ボタンまたはドラッグ＆ドロップでリストに追加します。未対応の形式は自動的に除外されます。'),
          ('step','<b>順序調整</b> — リスト内でドラッグするか<code>[上へ]</code>/<code>[下へ]</code>で結合順序を設定します。'),
          ('step','<b>エンコード設定</b> — 各ファイルの<b>読み込みエンコード</b>をコンボボックスで選択し、右の「保存設定」パネルで<b>保存エンコード</b>を選択します。'),
          ('step','<b>ファイル区切り線</b>（任意）— 「ファイル区切り線を挿入」をオンにすると、各ファイル間にファイル名入りの区切り線が自動挿入されます。'),
          ('step','<b>保存先指定</b>（任意）— <code>[パス指定]</code>で保存先を設定すると実行時に自動保存されます。未設定の場合は保存ダイアログが表示されます。'),
          ('step','<b><code>[▶ 結合・保存]</code></b> — クリックして結合を実行します。完了メッセージでファイルごとのエンコード概要を確認できます。'),
          ('divider',),
          ('tip','<b>エンコード自動検出</b> — chardetがインストールされていると、ファイル追加時にエンコードを自動検出します。精度が低い場合はコンボボックスで手動選択してください。'),
          ('tip','<b>保存エンコード選択の目安</b> — UTF-8：汎用推奨 / UTF-8-BOM：Excelで文字化けしない / EUC-KR・CP949：韓国語レガシーアプリ向け / UTF-16：特殊用途 / <b>Shift-JIS・GBK・Big5</b>：日本語・中国語（簡体字・繁体字）レガシーシステム互換'),
          ('tip','<b>区切り線の形式</b> — オンにすると各ファイルの前に <code>───── ▶ ファイル名.txt ──────</code> 形式の行が挿入されます。'),
          ('info','ファイルの読み込みに失敗した場合、そのファイルのみスキップして残りは正常に結合されます。エラー内容は完了メッセージに表示されます。'),
          ('warn','<code>[元に戻す]</code>ボタンは結合済み出力ファイルを削除します。<b>元のファイルは一切変更されません。</b>'),
         ]),

        ('🔄','Text Converter','TXT ↔ EPUB 形式を変換します',
         'TXTファイルをEPUB電子書籍に変換したり、EPUBからテキストを抽出したりできます。複数ファイルを順番に自動一括変換します。',
         [
          ('note','上部の<b>[TXT → EPUB]</b>または<b>[EPUB → TXT]</b>タブを先に選択してください。'),
          ('step','<b>ファイル追加</b> — <code>[📄 ファイル追加]</code>またはドラッグ＆ドロップで読み込みます。'),
          ('step','<b>TXT → EPUB 設定</b> — 「書籍情報」パネルで<b>タイトル・著者・言語</b>を入力し、<b>章の分割方式</b>を選択します。'),
          ('step','<b>EPUB → TXT 設定</b> — 「変換オプション」パネルで章区切り挿入・章タイトル含有・連続空行の整理・保存エンコードを設定します。'),
          ('step','<b>出力フォルダ指定</b>（任意）— デフォルト出力フォルダは⚙設定で指定したフォルダ（初期値：<code>Output/</code>）です。保存完了後に出力フォルダが自動的に開きます。'),
          ('step','<b><code>[▶ 変換開始]</code></b> — 複数ファイルの場合、プログレスバーで各ファイルの変換状況を確認できます。'),
          ('divider',),
          ('feature','TXT → EPUB 章の分割方式','<b>区切り線基準</b> — <code>===</code>、<code>---</code>、<code>★★★</code>などの反復記号で構成される行を章の境界として認識します。<br><br><b>空行3行以上基準</b> — 連続3行以上の空白区間を章の境界として認識します。<br><br><b>全体を1章として処理</b> — ファイル全体を1つの章として扱います。'),
          ('feature','EPUB → TXT 変換オプション','<b>章区切り線を追加</b> — 章の境界に区切り線を挿入します（デフォルト：オン）。<br><b>章タイトルを含む</b> — EPUBに保存された章タイトルを区切り線の下に表示します（デフォルト：オン）。<br><b>連続空行の整理</b> — 抽出時に生じる過剰な空行を整理します（デフォルト：オン）。<br><b>保存エンコード</b> — 出力TXTファイルのエンコードを選択します（デフォルト：UTF-8）。'),
          ('tip','出力フォルダを指定すると、元のフォルダを変更せずに変換結果だけ一か所にまとめられます。'),
          ('tip','変換中はウィンドウを閉じないでください。変換が中断される場合があります。'),
         ]),

        ('🏷️','Tag Editor','ファイル名のタグを一括追加・削除します',
         'ファイル名の<code>[一時]</code>・<code>[最終]</code>などの角括弧タグを一括処理し、先頭の不要な0も一度にまとめて整理できます。',
         [
          ('note','作業の種類に応じて上部タブから<b>[タグ削除]</b>/<b>[タグ追加]</b>/<b>[先頭0削除]</b>を選択してください。'),
          ('step','<b>ファイル・フォルダ追加</b> — <code>[📄 ファイル追加]</code>/<code>[📂 フォルダ追加]</code>またはドラッグ＆ドロップで対象を読み込みます。フォルダを追加すると「サブフォルダを含む」オプションに従って再帰的にファイルを読み込みます。'),
          ('step','<b>フィルター設定</b> — 左下の「フィルター設定」パネルで対象拡張子を指定します（カンマ区切り）。「すべての拡張子を対象」をオンにすると拡張子に関わらず全ファイルを処理します。'),
          ('step','<b>オプション設定</b> — 右パネルで各モードのオプションを設定します。'),
          ('step','<b>プレビュー確認</b> — <code>[プレビュー]</code>をクリックして「元のファイル名 → 変更後のファイル名」の表を確認します。<b>必ず確認してから適用してください。</b>'),
          ('step','<b>適用</b> — 結果が正しければ<code>[適用]</code>をクリックします。'),
          ('divider',),
          ('feature','タグ削除','タグ入力欄に特定のタグを入力するとそのタグのみ削除します。<b>入力欄を空にすると、ファイル名のすべての<code>[ ]</code>形式タグを削除します。</b><br><br>例）<code>最終</code>と入力 → <code>[最終]</code>のみ削除、他のタグはそのまま'),
          ('feature','タグ追加','右パネルで追加するタグと挿入位置（ファイル名の<b>前</b>/<b>後</b>）を選択します。同じタグが既に存在する場合は重複追加されません。'),
          ('feature','先頭0削除','ファイル名先頭の不要な0を自動削除します（001 → 1、007 → 7）。<b>ハイフンでつながれた日付形式の数字は自動的に保護されます。</b>'),
          ('example','会議録 001.docx','会議録 1.docx'),
          ('example','講義資料 007 最終版.pdf','講義資料 7 最終版.pdf'),
          ('example','2024-01-01 日記.txt','2024-01-01 日記.txt  ← 保護、変更なし'),
          ('warn','<b>ファイル名変更後、[元に戻す]で一度だけ復元できます。</b>ただし、新しい作業を実行したりウィンドウを閉じると復元データが消えます。<code>[プレビュー]</code>で必ず確認してから<code>[適用]</code>してください。'),
         ]),

        ('📁','Batch Renamer','フォルダ・ファイルを一括リネームします',
         'サブフォルダまたはファイルをパターンに基づいて一括でリネームします。番号を自動認識する「スマート抽出」と番号を直接指定する「連番」の2方式に対応しています。',
         [
          ('note','上部タブから<b>[フォルダ名変更]</b>または<b>[ファイル名変更]</b>を先に選択してください。'),
          ('step','<b>対象フォルダ指定</b> — <code>[📂 フォルダ選択]</code>またはドラッグ＆ドロップで<b>上位フォルダ</b>を指定します。指定したフォルダ自体は変更されず、<b>その中の下位項目のみ</b>名前が変わります。'),
          ('step','<b>方式選択</b> — 右パネルで「スマート抽出」または「連番」を選択します。'),
          ('step','<b>プレビュー確認</b> — <code>[プレビュー]</code>をクリックして変更結果を確認します。名前が競合する場合は表で警告が表示されます。'),
          ('step','<b>名前変更実行</b> — <code>[名前変更実行]</code>をクリックします。実行直後に<code>[元に戻す]</code>で一度だけ復元できます。'),
          ('divider',),
          ('feature','🔍 スマート抽出','既存の名前から番号を自動抽出して再構成します。<br><br><b>共通接頭辞の処理</b> — 自動検出 / 手動指定 / そのまま維持。<br><b>接頭辞・接尾辞</b> — 再構成された名前の前後に追加するテキストを入力します。'),
          ('feature','🔢 連番','最初から最後まで順番に番号を付けます。すべてのオプションを手動で設定します。<br><br><b>開始番号</b> — 00または01から選択。<b>桁数</b> — 自動または2・3・4桁固定。<b>接頭辞・接尾辞</b> — 番号の前後に付けるテキスト。<b>名前の保持</b> — 「番号のみ」または「番号+元の名前」。<b>番号リセット</b> — 「全体連番」または「グループごとにリセット」。'),
          ('tip','ファイル名変更では拡張子が常に自動保持されます。'),
          ('tip','フォルダをドラッグすると、サブフォルダまで再帰的にスキャンしてグループを自動構成します。'),
          ('tip','名前変更の実行前に対象フォルダを開いているエクスプローラーウィンドウは自動的に閉じられ、完了後に自動で再度開かれます。'),
          ('warn','<b>名前変更は即時に適用されます。</b>実行直後は<code>[元に戻す]</code>で復元できますが、新しい作業を実行したりウィンドウを閉じると復元データが消えます。'),
          ('warn','指定した上位フォルダ自体は変更されません。下位項目のみが対象です。'),
         ]),

        ('✦','Text Fixer','OCR・電子書籍テキストの改行を校正します',
         'PDFやEPUBから抽出したテキストはページ幅で強制改行される問題があります。Text Fixerはこれを自動復元して段落構造を整理します。',
         [
          ('note','<b>テキスト入力方法</b> — .txtファイルをドロップゾーンにドラッグ、<code>[📂 ファイルを開く]</code>、または左の「元のテキスト」欄に直接貼り付け。'),
          ('step','<b>テキスト入力</b> — ファイルを読み込むか、左のテキスト欄に貼り付けます。'),
          ('step','<b>オプション選択</b> — 4つのオプションを必要に応じて組み合わせます。最初は<b>① + ④</b>の組み合わせから始めてみてください。'),
          ('step','<b><code>[✦ 修正実行]</code></b> — 左（元のテキスト）と右（結果）を並べて比較しながら確認してください。'),
          ('step','<b>保存</b> — 結果が良ければ<code>[保存 ▼]</code>をクリックします。気に入らない場合は<code>[元に戻す]</code>で復元してオプションを変えて再試行してください。'),
          ('divider',),
          ('feature','① 改行結合（空行基準）','空行で段落を区切り、段落内で強制的に折り返された行を1つにつなげます。<b>つなげない場合</b> — 句点・感嘆符・疑問符・引用符などで終わる行、および<code>───</code>・<code>===</code>・<code>★★★</code>のような区切り線はつなげません。PDF・EPUBテキスト校正の核心オプションです。ほとんどの場合、最初にオンにしてください。'),
          ('feature','② 自動段落分割（最大N文字）','①で結合後に長くなりすぎた行を文章境界でN文字基準に分割します。短い文章同士はN文字以内で自動的にまとめられます。デフォルト100文字。長い文が続く場合は150〜200文字に増やしてみてください。'),
          ('feature','③ 文ごとに空行を挿入','句点・引用符で終わる行の後、またはセリフの前に空行を自動挿入します。会話が多いテキストで段落の読みやすさを高めるときに使います。'),
          ('feature','④ 過剰な空行を削減（最大N行）','連続する空行を最大N行に削減します。デフォルト1行推奨。複数セクションがある文書は2行に設定してください。'),
          ('divider',),
          ('tip','<b>推奨の組み合わせ</b> — PDF・EPUBテキスト校正：<b>① + ④</b> / 会話中心のテキスト：<b>① + ③</b> / OCR結果・長い段落の整理：<b>① + ② + ④</b>'),
          ('tip','<b>保存方式</b> — <b>元の場所に[Fixed]タグ付きで保存</b>：元のファイルはそのまま、校正版を<code>[Fixed]ファイル名.txt</code>として保存 / <b>名前を付けて保存</b>：場所とファイル名を直接指定 / <b>元に戻す</b>：修正前の元のテキストを左ペインに復元（修正実行後1回のみ可能）'),
          ('tip','🟡 <b>黄色の行</b> = 複数行が結合された部分 / 🟠 <b>オレンジの行</b> = 空行が削除された位置。3,000行以上の大容量ファイルはハイライトが省略されます。'),
          ('tip','下部の統計バーで<b>結合回数・空行削除数・元の行数・最終行数</b>を確認できます。'),
          ('tip','<b>Ctrl+F</b>で原文・修正文のテキスト検索ができます。Enterで次へ、Shift+Enterで前へ移動します。'),
          ('warn','保存は常に<b>UTF-8</b>エンコードで行われます。元のエンコード（EUC-KRなど）を維持する必要がある場合は別途変換してください。'),
          ('divider',),
          ('note','<b>部分的に破損したファイルの処理</b> — 一部のバイトが破損したファイルも開けます。破損した文字は<code>�</code>（U+FFFD）で表示され、ステータスバーに<b>⚠</b>アイコンと「部分エンコーディング失敗」の警告が表示されます。'),
          ('tip','Text Fixerは<b>単一ファイルの精密レビュー</b>に最適化されています。破損ファイルを開いて壊れた位置を直接確認し、その箇所を手動編集したり、原本の再取得を判断できます。'),
          ('warn','数万文字以上の大量破損があるファイルは、補正しても品質回復が困難です。まず原本元からの再ダウンロードを検討してください。Bulk Fixerではこのようなファイルを自動スキップして原本を保護します。'),
         ]),

        ('✦','Bulk Fixer','複数のTXTファイルの改行を一括補正します',
         'Text Fixerの補正エンジンを複数ファイルに一括適用します。OCRや電子書籍から抽出したTXTファイルをまとめて整理する際に使用します。',
         [
          ('step','<b>ファイル追加</b> — <code>[📄 ファイル追加]</code>または<code>[📂 フォルダ追加]</code>でTXTファイルを読み込みます。ファイル一覧にフォルダを直接ドラッグ＆ドロップしても、サブフォルダの<code>.txt</code>ファイルが再帰的に収集されます。'),
          ('step','<b>オプション選択</b> — 右パネルで結合モード（自動/韓国語/英語）と4つの補正オプションを設定します。<b>プリセット</b>から「一般文書」または「書籍・小説」を選ぶとオプションが一括設定されます。'),
          ('step','<b>保存設定</b> — 出力フォルダを指定するか、空欄のままにすると元ファイルと同じ場所に<code>[Fixed]ファイル名.txt</code>として保存されます。<b>フォルダ構造を維持</b>にチェックを入れると、出力フォルダ内に元のサブフォルダ構造が再現されます。'),
          ('step','<b><code>[▶ 一括補正開始]</code>をクリック</b> — 処理中は進捗が表示され、完了後に成功・失敗ファイル数が通知されます。'),
          ('tip','ファイル一覧の項目をクリックすると、右のプレビューパネルで補正結果を確認できます。'),
          ('tip','デフォルトの出力フォルダは<code>Output/</code>です。⚙設定でグローバルに変更するか、各タブで個別に指定できます。保存完了後に自動で開きます。'),
          ('warn','TXTファイルのみ対応です。DOCX・PDFなどは先にText ConverterでTXTに変換してください。'),
          ('divider',),
          ('note','<b>エンコーディング破損ファイルの自動分類</b> — Bulk Fixerは部分破損ファイルを検出すると、破損の程度に応じて3段階に分けて処理します：<br>• <b>Tier 1</b>（1〜500文字破損）：補正後にレポート生成<br>• <b>Tier 2</b>（501〜5,000文字破損）：補正後にレポート生成（レビュー推奨）<br>• <b>Tier 3</b>（5,001文字以上）：<b>自動スキップ（原本保護）</b> + レポートのみ生成'),
          ('tip','レポートファイルは<code>{元ファイル名}.encoding_report.txt</code>の形で補正版の隣に生成されます。どの行・どの列が破損したかを最大5,000件まで詳細記録します。'),
          ('warn','Tier 3でスキップされたファイルは<b>Text Fixerで個別にレビュー</b>してください。大量破損はエンコーディング誤検出か原本ファイル自体の問題である可能性が高く、一括補正よりも原本の再取得が良策です。'),
         ]),

        ('⌨️','ショートカット & Tips','',
         'キーボードショートカットで素早く操作できます。設定画面でカスタマイズ可能です。',
         [
          ('shortcut','Ctrl+1','Text Mergerへ移動'),
          ('shortcut','Ctrl+2','Text Converterへ移動'),
          ('shortcut','Ctrl+3','Tag Editorへ移動'),
          ('shortcut','Ctrl+4','Batch Renamerへ移動'),
          ('shortcut','Ctrl+5','Text Fixerへ移動'),
          ('shortcut','Ctrl+6','Bulk Fixerへ移動'),
          ('shortcut','Ctrl+F','Text Fixerでテキスト検索'),
          ('shortcut','⚙ ボタン（右上）','設定を開く — テーマ・言語・ショートカットを変更可能'),
          ('tip','設定（テーマ・言語・ショートカット）は終了時に自動保存され、次回起動時に復元されます。'),
          ('tip','すべてのタブで<b>ドラッグ＆ドロップ</b>でファイルを読み込めます。フォルダをドロップすると対応ファイルが一括追加されます。'),
          ('tip','🔋 <b>スリープ防止</b> — Text Merger・Text Converter・Text Fixer・Bulk Fixerでタスク実行中はWindowsのスリープが自動でブロックされます。完了またはエラー発生時に即座に解除されます。画面ロックはスリープとは無関係で、処理中も通常どおり動作します。'),
         ]),


        ('📁','生成ファイル案内','プログラム使用中に自動生成されるファイルとフォルダ',
         'File Nexus Suiteは設定保存、デフォルト出力、エラー記録のため、実行ファイルと同じフォルダに以下を自動生成します。',
         [
          ('step','<b>FileNexusSuite.json</b> — テーマ・言語・ショートカット・各タブ設定を保存する環境設定ファイルです。終了時に自動保存され、次回起動時に復元されます。'),
          ('step','<b>Output/</b> — Text Converter、Bulk Fixer、Text Fixerのデフォルト出力フォルダです。初回起動時に自動生成されます。⚙設定で場所をグローバルに変更でき、保存完了時に自動で開きます。'),
          ('step','<b>logs/crash_*.log</b> — 予期しないエラー発生時に自動生成されるクラッシュログです。最新3件のみ保持され、古いファイルは自動削除されます。'),
          ('warn','<b>_internal/</b> — フォルダ形式のexeビルド時に自動生成されるPythonランタイムフォルダです。<b>削除するとプログラムが起動できなくなります。</b>'),
          ('tip','これらのファイルやフォルダは直接削除しても問題ありません。次回起動時に必要なものは自動的に再生成されます。'),
         ]),

      ]

    elif lang == 'zh_cn':
      intro = 'File Nexus Suite 是专为文本、电子书及媒体文件作业设计的综合文件工具。文本合并、EPUB转换、文件名标签编辑、批量重命名、换行校正、批量校正 — 六大核心功能集于一个窗口之中。'
      sections = [
        ('📋','Text Merger','将多个文件合并为一个文本文件',
         '将以下格式的文件按您选择的顺序合并为一个文本文件。DOCX、PDF、XLSX需安装对应库后才能提取文本。',
         [
          ('formats',[('TXT', 'native'), ('MD', 'native'), ('CSV', 'native'), ('LOG', 'native'), ('JSON', 'native'), ('XML', 'native'), ('HTML', 'native'), ('PY', 'native'), ('DOCX', 'lib'), ('PDF', 'lib'), ('XLSX', 'lib'), ('HWPX', 'lib')]),
          ('step','<b>添加文件</b> — 点击<code>[📄 添加文件]</code>或将文件拖放到列表中。不支持的格式会自动过滤。'),
          ('step','<b>调整顺序</b> — 在列表中拖动或使用<code>[上移]</code>/<code>[下移]</code>设置合并顺序。'),
          ('step','<b>设置编码</b> — 从每个文件右侧的下拉框中选择<b>读取编码</b>，在右侧「保存设置」面板中选择<b>保存编码</b>。'),
          ('step','<b>文件分隔线</b>（可选）— 勾选「插入文件分隔线」后，合并时会在每个文件之间自动插入含文件名的分隔线。'),
          ('step','<b>指定保存路径</b>（可选）— 点击<code>[指定路径]</code>预先设置保存位置，执行时自动保存。未设置则在执行时弹出保存对话框。'),
          ('step','<b><code>[▶ 合并保存]</code></b> — 点击执行合并。完成消息中可查看各文件的编码摘要。'),
          ('divider',),
          ('tip','<b>编码自动检测</b> — 安装chardet后，添加文件时将自动检测编码。准确度低时请从下拉框手动选择。'),
          ('tip','<b>保存编码选择参考</b> — UTF-8：通用推荐 / UTF-8-BOM：Excel中不乱码 / EUC-KR·CP949：韩语旧版程序兼容 / UTF-16：特殊用途 / <b>Shift-JIS·GBK·Big5</b>：日文·中文（简体·繁体）旧版系统兼容'),
          ('tip','<b>分隔线格式</b> — 启用后，每个文件前插入 <code>───── ▶ 文件名.txt ──────</code> 格式的行。'),
          ('info','读取文件时若出现错误，仅跳过该文件，其余文件正常合并。错误内容显示在完成消息中。'),
          ('warn','<code>[撤销]</code>按钮将删除合并的输出文件。<b>原始文件不会有任何修改。</b>'),
         ]),

        ('🔄','Text Converter','在TXT和EPUB格式之间转换',
         '将TXT文件转换为EPUB电子书，或从EPUB中提取文本。添加多个文件后将按顺序自动批量转换。',
         [
          ('note','请先选择顶部的<b>[TXT → EPUB]</b>或<b>[EPUB → TXT]</b>选项卡。'),
          ('step','<b>添加文件</b> — 点击<code>[📄 添加文件]</code>或拖放。'),
          ('step','<b>TXT → EPUB 设置</b> — 在右侧「书籍信息」面板中输入<b>书名、作者、语言</b>，并选择<b>章节分割方式</b>。'),
          ('step','<b>EPUB → TXT 设置</b> — 在右侧「转换选项」面板中设置章节分隔线插入、章节标题包含、连续空行整理及保存编码。'),
          ('step','<b>输出文件夹</b>（可选）— 默认输出文件夹由⚙设置中的全局配置决定（默认：<code>Output/</code>）。保存完成后输出文件夹会自动打开。'),
          ('step','<b><code>[▶ 开始转换]</code></b> — 多文件时进度条显示各文件的转换状态。'),
          ('divider',),
          ('feature','TXT → EPUB 章节分割方式','<b>分隔线基准</b> — 由<code>===</code>、<code>---</code>、<code>★★★</code>等重复符号构成的行被识别为章节边界。<br><br><b>连续3行以上空行</b> — 连续3行以上的空白段落被识别为章节边界。<br><br><b>全部作为一个章节</b> — 将整个文件作为一个章节处理。'),
          ('feature','EPUB → TXT 转换选项','<b>添加章节分隔线</b> — 在章节边界插入分隔线（默认：开启）。<br><b>包含章节标题</b> — 在分隔线下方显示EPUB中保存的章节标题（默认：开启）。<br><b>整理连续空行</b> — 整理提取过程中产生的多余空行（默认：开启）。<br><b>保存编码</b> — 选择输出TXT文件的编码（默认：UTF-8）。'),
          ('tip','指定输出文件夹后，可在不修改原文件的情况下将转换结果集中保存在一处。'),
          ('tip','转换过程中请勿关闭窗口，否则可能中断转换。'),
         ]),

        ('🏷️','Tag Editor','批量添加或删除文件名中的标签',
         '批量添加或删除文件名中的<code>[临时]</code>、<code>[最终]</code>等括号标签，同时一次性整理多余的前导0。',
         [
          ('note','请根据操作类型从顶部选项卡选择<b>[删除标签]</b>/<b>[添加标签]</b>/<b>[删除前导零]</b>。'),
          ('step','<b>添加文件或文件夹</b> — 使用<code>[📄 添加文件]</code>/<code>[📂 添加文件夹]</code>或拖放添加目标。添加文件夹时，根据「包含子文件夹」选项递归读取文件。'),
          ('step','<b>筛选器设置</b> — 在左下角「筛选器设置」面板中指定目标扩展名（逗号分隔）。勾选「所有扩展名」则不限类型处理所有文件。'),
          ('step','<b>选项设置</b> — 在右侧面板中设置各模式的选项。'),
          ('step','<b>预览确认</b> — 点击<code>[预览]</code>查看「原文件名 → 修改后文件名」的对照表。<b>请务必确认后再应用。</b>'),
          ('step','<b>应用</b> — 结果正确后点击<code>[应用]</code>。'),
          ('divider',),
          ('feature','删除标签','在标签输入栏中输入特定标签，则仅删除该标签。<b>留空则删除文件名中所有<code>[ ]</code>格式的标签。</b><br><br>示例：输入<code>最终</code> → 仅删除<code>[最终]</code>，其余标签保留'),
          ('feature','添加标签','在右侧面板中选择要添加的标签和插入位置（文件名<b>前</b>/<b>后</b>）。若已存在相同标签，则不会重复添加。'),
          ('feature','删除前导零','自动删除文件名前端多余的0（001 → 1，007 → 7）。<b>由连字符连接的日期格式数字将自动受到保护。</b>'),
          ('example','会议记录 001.docx','会议记录 1.docx'),
          ('example','讲义资料 007 最终版.pdf','讲义资料 7 最终版.pdf'),
          ('example','2024-01-01 日记.txt','2024-01-01 日记.txt  ← 受保护，无变化'),
          ('warn','<b>文件名修改后可立即使用[撤销]恢复一次。</b>但执行新任务或关闭窗口后恢复数据将丢失。请务必先通过<code>[预览]</code>确认后再点击<code>[应用]</code>。'),
         ]),

        ('📁','Batch Renamer','批量重命名文件夹和文件',
         '使用基于模式的规则批量重命名子文件夹或文件。支持自动识别编号的「智能提取」和手动指定编号的「顺序编号」两种方式。',
         [
          ('note','请先从顶部选项卡选择<b>[文件夹重命名]</b>或<b>[文件重命名]</b>。'),
          ('step','<b>指定目标文件夹</b> — 使用<code>[📂 选择文件夹]</code>或拖放指定<b>上级文件夹</b>。指定的文件夹本身不会改变，只有<b>其内部的下级项目</b>才会被重命名。'),
          ('step','<b>选择方式</b> — 在右侧面板选择「智能提取」或「顺序编号」。'),
          ('step','<b>预览确认</b> — 点击<code>[预览]</code>查看修改结果。名称冲突时表格中会显示警告。'),
          ('step','<b>执行重命名</b> — 点击<code>[执行重命名]</code>。执行后可立即使用<code>[撤销]</code>恢复一次。'),
          ('divider',),
          ('feature','🔍 智能提取','自动从现有名称中提取编号并重新构建。<br><br><b>公共前缀处理</b> — 自动检测 / 手动指定 / 保留不变。<br><b>前缀·后缀</b> — 输入在重构名称前后添加的文本。'),
          ('feature','🔢 顺序编号','从头到尾按顺序分配编号。所有选项均手动指定。<br><br><b>起始编号</b> — 选择从00或01开始。<b>位数</b> — 自动或固定2/3/4位。<b>前缀·后缀</b> — 编号前后添加的文本。<b>名称保留</b> — 「仅编号」或「编号+原名称」。<b>编号重置</b> — 「全局连续」或「每组重置」。'),
          ('tip','文件重命名时扩展名始终自动保留。'),
          ('tip','拖放文件夹时会递归扫描子文件夹并自动构建分组。'),
          ('tip','执行重命名前，打开目标文件夹的资源管理器窗口会自动关闭，完成后自动重新打开。'),
          ('warn','<b>重命名会立即生效。</b>执行后可用<code>[撤销]</code>恢复，但执行新任务或关闭窗口后恢复数据将丢失。'),
          ('warn','指定的上级文件夹本身不会被修改，仅对其下级项目进行操作。'),
         ]),

        ('✦','Text Fixer','修复OCR和电子书文本的换行问题',
         '从PDF或EPUB提取的文本常因页面宽度出现强制换行。Text Fixer可智能还原段落结构。',
         [
          ('note','<b>文本输入方法</b> — 将.txt文件拖到放置区，使用<code>[📂 打开文件]</code>，或直接在左侧「原始文本」区域粘贴。'),
          ('step','<b>输入文本</b> — 打开文件或将文本粘贴到左侧区域。'),
          ('step','<b>选择选项</b> — 根据需要组合四个选项。大多数情况下先从<b>① + ④</b>开始尝试。'),
          ('step','<b><code>[✦ 执行修复]</code></b> — 左侧（原始）与右侧（结果）并排比较，确认修复效果。'),
          ('step','<b>保存</b> — 满意后点击<code>[保存 ▼]</code>。不满意则使用<code>[撤销]</code>还原，更换选项后重新尝试。'),
          ('divider',),
          ('feature','① 合并换行（以空行为基准）','以空行划分段落，然后合并段落内被强制折断的行。<b>不合并的情况</b> — 以句号、感叹号、问号、引号结尾的行，以及<code>───</code>、<code>===</code>、<code>★★★</code>等分隔线不参与合并。这是修复PDF/EPUB文本的核心选项，大多数情况下请先开启。'),
          ('feature','② 自动段落分割（最多N字）','①合并后过长的行在句子边界按N字标准分割。较短的句子在N字范围内自动组合。默认100字。句子较长时可尝试调整为150~200字。'),
          ('feature','③ 在句子之间插入空行','在以句号/引号结尾的行后，或对话前自动插入空行。适用于提高对话较多的文本的可读性。'),
          ('feature','④ 减少过多空行（最多N行）','将连续空行压缩为最多N行。默认1行。多节结构的文档建议设为2行。'),
          ('divider',),
          ('tip','<b>推荐组合</b> — PDF/EPUB文本修复：<b>① + ④</b> / 对话为主的文本：<b>① + ③</b> / OCR结果·长段落整理：<b>① + ② + ④</b>'),
          ('tip','<b>保存方式</b> — <b>在原位置以[Fixed]标签保存</b>：保留原文件，修复版另存为<code>[Fixed]文件名.txt</code> / <b>另存为</b>：手动指定位置和文件名 / <b>撤销</b>：将修复前的原始文本还原到左侧窗格（执行修复后可使用一次）'),
          ('tip','🟡 <b>黄色行</b> = 多行合并为一行 / 🟠 <b>橙色行</b> = 空行被删除的位置。超过3,000行的大文件将跳过高亮显示。'),
          ('tip','底部统计栏显示<b>合并次数、空行删除数、原始行数、最终行数</b>。'),
          ('tip','按<b>Ctrl+F</b>可在原文和修改后的文本中搜索关键词。Enter跳到下一个，Shift+Enter跳到上一个。'),
          ('warn','文件始终以<b>UTF-8</b>编码保存。如需保留原始编码（如EUC-KR），请另行转换。'),
          ('divider',),
          ('note','<b>部分损坏文件的处理</b> — 部分字节损坏的文件也可以打开。损坏的字符显示为<code>�</code>（U+FFFD），状态栏会显示<b>⚠</b>图标和"部分编码失败"警告。'),
          ('tip','Text Fixer 针对<b>单个文件的精细审核</b>进行了优化。打开损坏文件可直接查看损坏位置，手动编辑该段，或判断是否需要重新获取原件。'),
          ('warn','数万字符以上的大量损坏文件难以通过校正恢复质量。建议优先考虑从原来源重新下载。Bulk Fixer 会自动跳过此类文件以保护原件。'),
         ]),

        ('✦','Bulk Fixer','批量校正多个TXT文件的换行',
         '将Text Fixer的校正引擎批量应用于多个文件。适用于一次性整理从OCR或电子书中提取的大量TXT文件。',
         [
          ('step','<b>添加文件</b> — 使用<code>[📄 添加文件]</code>或<code>[📂 添加文件夹]</code>加载TXT文件。也可以将文件夹直接拖放到文件列表中，自动递归收集<code>.txt</code>文件。'),
          ('step','<b>设置选项</b> — 在右侧面板中选择合并模式（自动/韩语/英语）和四个校正选项。使用<b>预设</b>下拉框选择"一般文档"或"书籍·小说"可一键配置选项。'),
          ('step','<b>保存设置</b> — 指定输出文件夹，或留空则以<code>[Fixed]文件名.txt</code>保存在原文件旁边。勾选<b>保留文件夹结构</b>可在输出文件夹中重现原始子文件夹层级。'),
          ('step','<b>点击<code>[▶ 开始批量校正]</code></b> — 处理期间显示进度，完成后通知成功和失败文件数。'),
          ('tip','点击文件列表中的项目，可在右侧预览面板中预览校正结果。'),
          ('tip','默认输出文件夹为<code>Output/</code>。可在⚙设置中全局更改，也可在各标签页单独指定。保存完成后自动打开。'),
          ('warn','仅支持TXT文件。请先用Text Converter将DOCX、PDF等格式转换为TXT后再使用。'),
          ('divider',),
          ('note','<b>编码损坏文件自动分级</b> — Bulk Fixer 检测到部分损坏文件后，根据损坏程度分为三级处理：<br>• <b>Tier 1</b>（1~500字符损坏）：校正后生成报告<br>• <b>Tier 2</b>（501~5,000字符损坏）：校正后生成报告（建议审核）<br>• <b>Tier 3</b>（5,001字符以上）：<b>自动跳过（保护原文件）</b> + 仅生成报告'),
          ('tip','报告文件以<code>{原文件名}.encoding_report.txt</code>的形式生成在校正版旁边，详细记录哪些行、哪些列出现损坏，最多记录 5,000 条。'),
          ('warn','被 Tier 3 跳过的文件应<b>在 Text Fixer 中单独审核</b>。大量损坏通常意味着编码检测错误或原文件本身存在问题，与其强制批量校正，不如重新获取原件。'),
         ]),

        ('⌨️','快捷键 & 使用技巧','',
         '使用键盘快捷键快速操作，可在设置中自定义。',
         [
          ('shortcut','Ctrl+1','转到 Text Merger'),
          ('shortcut','Ctrl+2','转到 Text Converter'),
          ('shortcut','Ctrl+3','转到 Tag Editor'),
          ('shortcut','Ctrl+4','转到 Batch Renamer'),
          ('shortcut','Ctrl+5','转到 Text Fixer'),
          ('shortcut','Ctrl+6','转到 Bulk Fixer'),
          ('shortcut','Ctrl+F','在 Text Fixer 中搜索文本'),
          ('shortcut','⚙ 按钮（右上角）','打开设置 — 可更改主题、语言和快捷键'),
          ('tip','设置（主题、语言、快捷键）在退出时自动保存，下次启动时恢复。'),
          ('tip','所有选项卡均支持<b>拖放</b>加载文件。拖入文件夹时，将批量添加其中的支持文件。'),
          ('tip','🔋 <b>防止休眠</b> — Text Merger、Text Converter、Text Fixer 或 Bulk Fixer 执行任务期间，Windows 休眠模式将被自动阻止。任务完成或发生错误时立即解除。屏幕锁定与休眠无关，处理过程中仍可正常使用。'),
         ]),


        ('📁','生成文件说明','程序使用过程中自动创建的文件和文件夹',
         'File Nexus Suite会在程序所在文件夹中自动创建以下内容，用于保存设置、默认输出和错误记录。',
         [
          ('step','<b>FileNexusSuite.json</b> — 保存主题、语言、快捷键及各标签页设置的配置文件。退出时自动保存，下次启动时恢复。'),
          ('step','<b>Output/</b> — Text Converter、Bulk Fixer和Text Fixer的默认输出文件夹。首次启动时自动创建。可在⚙设置中全局更改位置，保存完成时自动打开。'),
          ('step','<b>logs/crash_*.log</b> — 发生意外错误时自动生成的崩溃日志。仅保留最近3个，旧文件自动删除。'),
          ('warn','<b>_internal/</b> — 文件夹形式exe构建时自动生成的Python运行时文件夹。<b>删除后程序将无法运行。</b>'),
          ('tip','可以直接删除这些文件和文件夹。下次启动时，所需内容将自动重新创建。'),
         ]),

      ]

    else:  # zh_tw
      intro = 'File Nexus Suite 是專為文字、電子書及媒體檔案作業設計的綜合檔案工具。文字合併、EPUB轉換、檔名標籤編輯、批次重新命名、換行校正、批次校正 — 六大核心功能集於一個視窗之中。'
      sections = [
        ('📋','Text Merger','將多個檔案合併為一個文字檔案',
         '將以下格式的檔案依您選擇的順序合併為一個文字檔案。DOCX、PDF、XLSX需安裝對應函式庫後才能擷取文字。',
         [
          ('formats',[('TXT', 'native'), ('MD', 'native'), ('CSV', 'native'), ('LOG', 'native'), ('JSON', 'native'), ('XML', 'native'), ('HTML', 'native'), ('PY', 'native'), ('DOCX', 'lib'), ('PDF', 'lib'), ('XLSX', 'lib'), ('HWPX', 'lib')]),
          ('step','<b>新增檔案</b> — 點擊<code>[📄 新增檔案]</code>或將檔案拖曳放置到清單中。不支援的格式會自動過濾。'),
          ('step','<b>調整順序</b> — 在清單中拖曳或使用<code>[上移]</code>/<code>[下移]</code>設定合併順序。'),
          ('step','<b>設定編碼</b> — 從每個檔案右側的下拉選單選擇<b>讀取編碼</b>，在右側「儲存設定」面板選擇<b>儲存編碼</b>。'),
          ('step','<b>檔案分隔線</b>（選填）— 勾選「插入檔案分隔線」後，合併時會在每個檔案之間自動插入含檔名的分隔線。'),
          ('step','<b>指定儲存路徑</b>（選填）— 點擊<code>[指定路徑]</code>預先設定儲存位置，執行時自動儲存。未設定則在執行時顯示儲存對話框。'),
          ('step','<b><code>[▶ 合併儲存]</code></b> — 點擊執行合併。完成訊息中可查看各檔案的編碼摘要。'),
          ('divider',),
          ('tip','<b>編碼自動偵測</b> — 安裝chardet後，新增檔案時將自動偵測編碼。準確度低時請從下拉選單手動選擇。'),
          ('tip','<b>儲存編碼選擇參考</b> — UTF-8：通用推薦 / UTF-8-BOM：Excel中不亂碼 / EUC-KR·CP949：韓語舊版程式相容 / UTF-16：特殊用途 / <b>Shift-JIS·GBK·Big5</b>：日文·中文（簡體·繁體）舊版系統相容'),
          ('tip','<b>分隔線格式</b> — 啟用後，每個檔案前插入 <code>───── ▶ 檔案名稱.txt ──────</code> 格式的行。'),
          ('info','讀取檔案時若發生錯誤，僅跳過該檔案，其餘檔案正常合併。錯誤內容顯示在完成訊息中。'),
          ('warn','<code>[復原]</code>按鈕將刪除合併的輸出檔案。<b>原始檔案不會有任何修改。</b>'),
         ]),

        ('🔄','Text Converter','在TXT和EPUB格式之間轉換',
         '將TXT檔案轉換為EPUB電子書，或從EPUB中擷取文字。新增多個檔案後將依序自動批次轉換。',
         [
          ('note','請先選擇頂部的<b>[TXT → EPUB]</b>或<b>[EPUB → TXT]</b>分頁。'),
          ('step','<b>新增檔案</b> — 點擊<code>[📄 新增檔案]</code>或拖放。'),
          ('step','<b>TXT → EPUB 設定</b> — 在右側「書籍資訊」面板中輸入<b>書名、作者、語言</b>，並選擇<b>章節分割方式</b>。'),
          ('step','<b>EPUB → TXT 設定</b> — 在右側「轉換選項」面板中設定章節分隔線插入、章節標題含入、連續空行整理及儲存編碼。'),
          ('step','<b>輸出資料夾</b>（選填）— 預設輸出資料夾由⚙設定中的全域設定決定（預設：<code>Output/</code>）。儲存完成後輸出資料夾會自動開啟。'),
          ('step','<b><code>[▶ 開始轉換]</code></b> — 多檔案時進度列顯示各檔案的轉換狀態。'),
          ('divider',),
          ('feature','TXT → EPUB 章節分割方式','<b>分隔線基準</b> — 由<code>===</code>、<code>---</code>、<code>★★★</code>等重複符號構成的行被識別為章節邊界。<br><br><b>連續3行以上空行</b> — 連續3行以上的空白段落被識別為章節邊界。<br><br><b>全部作為一個章節</b> — 將整個檔案作為一個章節處理。'),
          ('feature','EPUB → TXT 轉換選項','<b>新增章節分隔線</b> — 在章節邊界插入分隔線（預設：開啟）。<br><b>包含章節標題</b> — 在分隔線下方顯示EPUB中儲存的章節標題（預設：開啟）。<br><b>整理連續空行</b> — 整理擷取過程中產生的多餘空行（預設：開啟）。<br><b>儲存編碼</b> — 選擇輸出TXT檔案的編碼（預設：UTF-8）。'),
          ('tip','指定輸出資料夾後，可在不修改原檔案的情況下將轉換結果集中儲存在一處。'),
          ('tip','轉換過程中請勿關閉視窗，否則可能中斷轉換。'),
         ]),

        ('🏷️','Tag Editor','批次新增或移除檔名中的標籤',
         '批次新增或移除檔名中的<code>[暫存]</code>、<code>[最終]</code>等括號標籤，同時一次性整理多餘的前導0。',
         [
          ('note','請根據操作類型從頂部分頁選擇<b>[移除標籤]</b>/<b>[新增標籤]</b>/<b>[移除前導零]</b>。'),
          ('step','<b>新增檔案或資料夾</b> — 使用<code>[📄 新增檔案]</code>/<code>[📂 新增資料夾]</code>或拖放新增目標。新增資料夾時，依「包含子資料夾」選項遞迴讀取檔案。'),
          ('step','<b>篩選器設定</b> — 在左下角「篩選器設定」面板中指定目標副檔名（逗號分隔）。勾選「所有副檔名」則不限類型處理所有檔案。'),
          ('step','<b>選項設定</b> — 在右側面板中設定各模式的選項。'),
          ('step','<b>預覽確認</b> — 點擊<code>[預覽]</code>查看「原檔名 → 修改後檔名」的對照表。<b>請務必確認後再套用。</b>'),
          ('step','<b>套用</b> — 結果正確後點擊<code>[套用]</code>。'),
          ('divider',),
          ('feature','移除標籤','在標籤輸入欄中輸入特定標籤，則僅移除該標籤。<b>留空則移除檔名中所有<code>[ ]</code>格式的標籤。</b><br><br>範例：輸入<code>最終</code> → 僅移除<code>[最終]</code>，其他標籤保留'),
          ('feature','新增標籤','在右側面板中選擇要新增的標籤和插入位置（檔名<b>前</b>/<b>後</b>）。若已存在相同標籤，則不會重複新增。'),
          ('feature','移除前導零','自動移除檔名前端多餘的0（001 → 1、007 → 7）。<b>由連字號連接的日期格式數字將自動受到保護。</b>'),
          ('example','會議記錄 001.docx','會議記錄 1.docx'),
          ('example','講義資料 007 最終版.pdf','講義資料 7 最終版.pdf'),
          ('example','2024-01-01 日記.txt','2024-01-01 日記.txt  ← 受保護，無變化'),
          ('warn','<b>檔名修改後可立即使用[復原]還原一次。</b>但執行新任務或關閉視窗後還原資料將消失。請務必先透過<code>[預覽]</code>確認後再點擊<code>[套用]</code>。'),
         ]),

        ('📁','Batch Renamer','批次重新命名資料夾和檔案',
         '使用以模式為基礎的規則批次重新命名子資料夾或檔案。支援自動識別編號的「智慧提取」和手動指定編號的「順序編號」兩種方式。',
         [
          ('note','請先從頂部分頁選擇<b>[資料夾重新命名]</b>或<b>[檔案重新命名]</b>。'),
          ('step','<b>指定目標資料夾</b> — 使用<code>[📂 選擇資料夾]</code>或拖放指定<b>上層資料夾</b>。指定的資料夾本身不會改變，只有<b>其內部的下層項目</b>才會被重新命名。'),
          ('step','<b>選擇方式</b> — 在右側面板選擇「智慧提取」或「順序編號」。'),
          ('step','<b>預覽確認</b> — 點擊<code>[預覽]</code>查看修改結果。名稱衝突時表格中會顯示警告。'),
          ('step','<b>執行重新命名</b> — 點擊<code>[執行重新命名]</code>。執行後可立即使用<code>[復原]</code>還原一次。'),
          ('divider',),
          ('feature','🔍 智慧提取','自動從現有名稱中提取編號並重新建構。<br><br><b>共用前綴處理</b> — 自動偵測 / 手動指定 / 保留不變。<br><b>前綴·後綴</b> — 輸入在重構名稱前後新增的文字。'),
          ('feature','🔢 順序編號','從頭到尾按順序分配編號。所有選項均手動指定。<br><br><b>起始編號</b> — 選擇從00或01開始。<b>位數</b> — 自動或固定2/3/4位。<b>前綴·後綴</b> — 編號前後新增的文字。<b>名稱保留</b> — 「僅編號」或「編號+原名稱」。<b>編號重置</b> — 「全域連續」或「每組重置」。'),
          ('tip','檔案重新命名時副檔名始終自動保留。'),
          ('tip','拖放資料夾時會遞迴掃描子資料夾並自動建構分組。'),
          ('tip','執行重新命名前，開啟目標資料夾的檔案總管視窗會自動關閉，完成後自動重新開啟。'),
          ('warn','<b>重新命名會立即生效。</b>執行後可用<code>[復原]</code>還原，但執行新任務或關閉視窗後還原資料將消失。'),
          ('warn','指定的上層資料夾本身不會被修改，僅對其下層項目進行操作。'),
         ]),

        ('✦','Text Fixer','修復OCR和電子書文字的換行問題',
         '從PDF或EPUB擷取的文字常因頁面寬度出現強制換行。Text Fixer可智慧還原段落結構。',
         [
          ('note','<b>文字輸入方式</b> — 將.txt檔案拖曳至放置區，使用<code>[📂 開啟檔案]</code>，或直接在左側「原始文字」區域貼上。'),
          ('step','<b>輸入文字</b> — 開啟檔案或將文字貼到左側區域。'),
          ('step','<b>選擇選項</b> — 根據需要組合四個選項。大多數情況下先從<b>① + ④</b>開始嘗試。'),
          ('step','<b><code>[✦ 執行修復]</code></b> — 左側（原始）與右側（結果）並排比較，確認修復效果。'),
          ('step','<b>儲存</b> — 滿意後點擊<code>[儲存 ▼]</code>。不滿意則使用<code>[復原]</code>還原，更換選項後重新嘗試。'),
          ('divider',),
          ('feature','① 合併換行（以空行為基準）','以空行劃分段落，然後合併段落內被強制折斷的行。<b>不合併的情況</b> — 以句號、驚嘆號、問號、引號結尾的行，以及<code>───</code>、<code>===</code>、<code>★★★</code>等分隔線不參與合併。這是修復PDF/EPUB文字的核心選項，大多數情況下請先開啟。'),
          ('feature','② 自動段落分割（最多N字）','①合併後過長的行在句子邊界按N字標準分割。較短的句子在N字範圍內自動組合。預設100字。句子較長時可嘗試調整為150~200字。'),
          ('feature','③ 在句子之間插入空行','在以句號/引號結尾的行後，或對話前自動插入空行。適用於提高對話較多的文字的可讀性。'),
          ('feature','④ 減少過多空行（最多N行）','將連續空行壓縮為最多N行。預設1行。多節結構的文件建議設為2行。'),
          ('divider',),
          ('tip','<b>推薦組合</b> — PDF/EPUB文字修復：<b>① + ④</b> / 對話為主的文字：<b>① + ③</b> / OCR結果·長段落整理：<b>① + ② + ④</b>'),
          ('tip','<b>儲存方式</b> — <b>在原位置以[Fixed]標籤儲存</b>：保留原檔案，修復版另存為<code>[Fixed]檔名.txt</code> / <b>另存新檔</b>：手動指定位置和檔名 / <b>復原</b>：將修復前的原始文字還原到左側窗格（執行修復後可使用一次）'),
          ('tip','🟡 <b>黃色行</b> = 多行合併為一行 / 🟠 <b>橙色行</b> = 空行被刪除的位置。超過3,000行的大型檔案將跳過高亮顯示。'),
          ('tip','底部統計列顯示<b>合併次數、空行刪除數、原始行數、最終行數</b>。'),
          ('tip','按<b>Ctrl+F</b>可在原文和修改後的文字中搜尋關鍵字。Enter跳到下一個，Shift+Enter跳到上一個。'),
          ('warn','檔案始終以<b>UTF-8</b>編碼儲存。如需保留原始編碼（如EUC-KR），請另行轉換。'),
          ('divider',),
          ('note','<b>部分損毀檔案的處理</b> — 部分位元組損毀的檔案也可以開啟。損毀的字元顯示為<code>�</code>（U+FFFD），狀態列會顯示<b>⚠</b>圖示和「部分編碼失敗」警告。'),
          ('tip','Text Fixer 針對<b>單一檔案的精細審核</b>進行了最佳化。開啟損毀檔案可直接檢視損毀位置，手動編輯該段，或判斷是否需要重新取得原始檔案。'),
          ('warn','數萬字元以上的大量損毀檔案難以透過校正恢復品質。建議優先考慮從原來源重新下載。Bulk Fixer 會自動略過此類檔案以保護原始檔案。'),
         ]),

        ('✦','Bulk Fixer','批量校正多個TXT檔案的換行',
         '將Text Fixer的校正引擎批量應用於多個檔案。適用於一次性整理從OCR或電子書中提取的大量TXT檔案。',
         [
          ('step','<b>新增檔案</b> — 使用<code>[📄 新增檔案]</code>或<code>[📂 新增資料夾]</code>載入TXT檔案。也可以將資料夾直接拖放到檔案清單中，自動遞迴收集<code>.txt</code>檔案。'),
          ('step','<b>設定選項</b> — 在右側面板中選擇合併模式（自動/韓語/英語）和四個校正選項。使用<b>預設</b>下拉選單選擇「一般文件」或「書籍·小說」可一鍵配置選項。'),
          ('step','<b>儲存設定</b> — 指定輸出資料夾，或留空則以<code>[Fixed]檔名.txt</code>儲存在原檔案旁邊。勾選<b>保留資料夾結構</b>可在輸出資料夾中重現原始子資料夾層級。'),
          ('step','<b>點擊<code>[▶ 開始批量校正]</code></b> — 處理期間顯示進度，完成後通知成功和失敗檔案數。'),
          ('tip','點擊檔案清單中的項目，可在右側預覽面板中預覽校正結果。'),
          ('tip','預設輸出資料夾為<code>Output/</code>。可在⚙設定中全域更改，也可在各分頁單獨指定。儲存完成後自動開啟。'),
          ('warn','僅支援TXT檔案。請先用Text Converter將DOCX、PDF等格式轉換為TXT後再使用。'),
          ('divider',),
          ('note','<b>編碼損毀檔案自動分級</b> — Bulk Fixer 偵測到部分損毀檔案後，依據損毀程度分為三級處理：<br>• <b>Tier 1</b>（1~500字元損毀）：校正後產生報告<br>• <b>Tier 2</b>（501~5,000字元損毀）：校正後產生報告（建議審核）<br>• <b>Tier 3</b>（5,001字元以上）：<b>自動略過（保護原始檔案）</b> + 僅產生報告'),
          ('tip','報告檔案以<code>{原檔名}.encoding_report.txt</code>的形式產生在校正版旁邊，詳細記錄哪些行、哪些欄出現損毀，最多記錄 5,000 筆。'),
          ('warn','被 Tier 3 略過的檔案應<b>在 Text Fixer 中個別審核</b>。大量損毀通常意味著編碼偵測錯誤或原始檔案本身有問題，與其強制批量校正，不如重新取得原始檔案。'),
         ]),

        ('⌨️','快捷鍵 & 使用技巧','',
         '使用鍵盤快捷鍵快速操作，可在設定中自訂。',
         [
          ('shortcut','Ctrl+1','前往 Text Merger'),
          ('shortcut','Ctrl+2','前往 Text Converter'),
          ('shortcut','Ctrl+3','前往 Tag Editor'),
          ('shortcut','Ctrl+4','前往 Batch Renamer'),
          ('shortcut','Ctrl+5','前往 Text Fixer'),
          ('shortcut','Ctrl+6','前往 Bulk Fixer'),
          ('shortcut','Ctrl+F','在 Text Fixer 中搜尋文字'),
          ('shortcut','⚙ 按鈕（右上角）','開啟設定 — 可更改主題、語言和快捷鍵'),
          ('tip','設定（主題、語言、快捷鍵）在關閉時自動儲存，下次啟動時還原。'),
          ('tip','所有分頁均支援<b>拖放</b>載入檔案。拖入資料夾時，將批次新增其中的支援檔案。'),
          ('tip','🔋 <b>防止休眠</b> — Text Merger、Text Converter、Text Fixer 或 Bulk Fixer 執行任務期間，Windows 休眠模式將被自動封鎖。任務完成或發生錯誤時立即解除。螢幕鎖定與休眠無關，處理過程中仍可正常使用。'),
         ]),


        ('📁','生成檔案說明','程式使用過程中自動建立的檔案和資料夾',
         'File Nexus Suite會在程式所在資料夾中自動建立以下內容，用於儲存設定、預設輸出和錯誤記錄。',
         [
          ('step','<b>FileNexusSuite.json</b> — 儲存主題、語言、快捷鍵及各分頁設定的設定檔。結束時自動儲存，下次啟動時還原。'),
          ('step','<b>Output/</b> — Text Converter、Bulk Fixer和Text Fixer的預設輸出資料夾。首次啟動時自動建立。可在⚙設定中全域更改位置，儲存完成時自動開啟。'),
          ('step','<b>logs/crash_*.log</b> — 發生意外錯誤時自動生成的當機日誌。僅保留最近3個，舊檔案自動刪除。'),
          ('warn','<b>_internal/</b> — 資料夾形式exe建置時自動生成的Python執行環境資料夾。<b>刪除後程式將無法執行。</b>'),
          ('tip','可以直接刪除這些檔案和資料夾。下次啟動時，所需內容將自動重新建立。'),
         ]),

      ]

    # ─────────────────────────────────────────────────────────────
    # Data-only return (for HelpDialog sidebar)
    # ─────────────────────────────────────────────────────────────
    if _data_only:
        return intro, sections

    # ─────────────────────────────────────────────────────────────
    # Single-section HTML render helper
    # ─────────────────────────────────────────────────────────────
    def _render_section(entry):
        icon, title, subtitle, desc, items = entry
        is_sc = any(i[0] == 'shortcut' for i in items)
        step_n = 0
        feat_bg  = _mix(bg, accent, 0.05)
        feat_bdr = _mix(accent, bg, 0.5)
        _CIRCLED = ['①','②','③','④','⑤','⑥','⑦','⑧','⑨','⑩',
                    '⑪','⑫','⑬','⑭','⑮','⑯','⑰','⑱','⑲','⑳']
        p = []
        p.append(f'''<div style="background:{bg};border:1px solid {border};border-radius:12px;margin:0 0 14px;overflow:hidden;">''')
        p.append(
            f'''<div style="padding:13px 18px 11px;border-bottom:1px solid {border};">'''
            f'''<span style="font-size:18px;margin-right:10px;">{icon}</span>'''
            f'''<span style="font-size:14px;font-weight:700;color:{text};">{title}'''
        )
        if subtitle:
            p.append(f'''  <span style="font-size:11px;font-weight:400;color:{muted};margin-left:8px;">{subtitle}</span>''')
        p.append('</span>')   # close title span
        if desc:
            p.append(f'''<div style="font-size:12px;color:{muted};margin-top:4px;line-height:1.6;">{desc}</div>''')
        p.append('</div>')   # close header div
        p.append('''<div style="padding:14px 18px 14px;">''')
        if is_sc:
            for item in items:
                if item[0] == 'shortcut':
                    _, k, d = item
                    key_parts = k.split('+')
                    key_html = f'<span style="color:{muted};font-size:10px;margin:0 3px;font-weight:400;">+</span>'.join(
                        f'<span style="display:inline-block;background:{srf2};'
                        f'border:1px solid {text};border-bottom:2px solid {text};'
                        f'border-radius:4px;padding:2px 9px;font-size:11px;font-weight:700;'
                        f'font-family:monospace;color:{text};white-space:nowrap;">{kp.strip()}</span>'
                        for kp in key_parts
                    )
                    p.append(
                        f'''<div style="padding:7px 12px;margin:0 0 5px;border-radius:8px;'''
                        f'''background:{bg2};border:1px solid {border};">'''
                        f'''{key_html}'''
                        f'''<span style="color:{muted};font-size:12px;margin-left:14px;">{d}</span></div>'''
                    )
                elif item[0] == 'tip':
                    tip_text = item[1]
                    has_icon = tip_text[:2].strip() and ord(tip_text[0]) > 127
                    icon_html = '' if has_icon else f'<span style="color:{accent};font-weight:700;margin-right:5px;">💡</span>'
                    p.append(
                        f'''<div style="border-left:3px solid {tip_bdr};background:{tip_bg};'''
                        f'''border-radius:0 7px 7px 0;padding:8px 14px;margin:10px 0 0;'''
                        f'''font-size:12px;color:{text};line-height:1.7;">{icon_html}{tip_text}</div>'''
                    )
        else:
            for item in items:
                kind = item[0]
                if kind == 'step':
                    step_n += 1
                    num = _CIRCLED[step_n-1] if step_n <= 20 else f'{step_n}.'
                    p.append(
                        f'''<div style="margin:0 0 8px 18px;font-size:13px;'''
                        f'''color:{text};line-height:1.75;">'''
                        f'''<span style="color:{accent};font-weight:700;'''
                        f'''margin-right:5px;">{num}</span>{item[1]}</div>'''
                    )
                elif kind == 'sub':
                    p.append(f'''<div style="margin:-4px 0 8px 52px;color:{muted};font-size:13px;line-height:1.7;">{item[1]}</div>''')
                elif kind == 'note':
                    p.append(
                        f'''<div style="border-left:3px solid {note_bdr};background:{note_bg};'''
                        f'''border-radius:0 7px 7px 0;padding:8px 14px;margin:0 0 10px 18px;'''
                        f'''font-size:12px;color:{text};line-height:1.7;">'''
                        f'''<span style="color:#5080D0;font-weight:700;margin-right:5px;">ℹ️</span>{item[1]}</div>'''
                    )
                elif kind == 'tip':
                    p.append(
                        f'''<div style="border-left:3px solid {tip_bdr};background:{tip_bg};'''
                        f'''border-radius:0 7px 7px 0;padding:8px 14px;margin:4px 0 8px 18px;'''
                        f'''font-size:12px;color:{text};line-height:1.7;">'''
                        f'''<span style="color:{accent};font-weight:700;margin-right:5px;">💡</span>{item[1]}</div>'''
                    )
                elif kind == 'warn':
                    p.append(
                        f'''<div style="border-left:3px solid {warn_bdr};background:{warn_bg};'''
                        f'''border-radius:0 7px 7px 0;padding:8px 14px;margin:4px 0 8px 18px;'''
                        f'''font-size:12px;color:#9B2A10;line-height:1.7;">'''
                        f'''<span style="font-weight:700;margin-right:5px;">⚠️</span>{item[1]}</div>'''
                    )
                elif kind == 'feature':
                    _, ftitle, fdesc = item
                    p.append(
                        f'''<div style="background:{feat_bg};border:1px solid {feat_bdr};'''
                        f'''border-radius:8px;padding:10px 14px;margin:4px 0 10px 18px;">'''
                        f'''<div style="font-size:13px;font-weight:700;color:{accent};margin-bottom:5px;">{ftitle}</div>'''
                        f'''<div style="font-size:13px;color:{text};line-height:1.7;">{fdesc}</div>'''
                        f'''</div>'''
                    )
                elif kind == 'divider':
                    # Visual divider between the step group and tip / warn blocks
                    p.append(
                        f'''<hr style="border:none;border-top:1px solid {border};margin:6px 0 10px 18px;">'''
                    )
                elif kind == 'info':
                    # Neutral-gray info box — lower intensity than note (blue) / tip (accent) / warn (red)
                    p.append(
                        f'''<div style="border-left:3px solid {border};background:{srf2};'''
                        f'''border-radius:0 7px 7px 0;padding:8px 14px;margin:4px 0 8px 18px;'''
                        f'''font-size:12px;color:{muted};line-height:1.7;">'''
                        f'''<span style="font-weight:700;margin-right:5px;">ℹ</span>{item[1]}</div>'''
                    )
                elif kind == 'formats':
                    # Pill row visualizing supported file formats
                    # item = ('formats', [(label, ftype), ...])
                    # ftype: 'native' = native support, 'lib' = requires installing a library
                    fmts = item[1]
                    pills = []
                    for label, ftype in fmts:
                        if ftype == 'native':
                            pill_bg  = _mix(accent, bg, 0.78)
                            pill_fg  = accent
                            pill_bdr = _mix(accent, bg, 0.55)
                        else:
                            pill_bg  = _mix('#808080', bg, 0.88)
                            pill_fg  = muted
                            pill_bdr = _mix('#808080', bg, 0.65)
                        pills.append(
                            f'<span style="display:inline-block;background:{pill_bg};'
                            f'border:1px solid {pill_bdr};border-radius:4px;'
                            f'padding:2px 8px;font-size:11px;font-weight:700;'
                            f'font-family:monospace;color:{pill_fg};margin:2px 4px 2px 0;">'
                            f'{label}</span>'
                        )
                    legend_dot_on  = f'<span style="color:{accent};font-size:9px;">●</span>'
                    legend_dot_off = f'<span style="color:{muted};font-size:9px;">●</span>'
                    p.append(
                        f'<div style="margin:0 0 12px 18px;">'
                        f'<div style="font-size:11px;color:{muted};margin-bottom:6px;">'
                        f'{legend_dot_on} 기본 지원 &nbsp;&nbsp;'
                        f'{legend_dot_off} 라이브러리 설치 필요 '
                        f'<span style="font-size:10px;">(python-docx · pdfplumber · openpyxl)</span></div>'
                        f'{"".join(pills)}'
                        f'</div>'
                    )
                elif kind == 'example':
                    _, before, after = item
                    p.append(
                        f'<div style="margin:3px 0 8px 18px;">'
                        f'<table style="background:{srf2};border:1px solid {border};'
                        f'border-radius:6px;border-spacing:0;border-collapse:collapse;">'
                        f'<tr>'
                        f'<td style="font-family:monospace;color:{muted};font-size:13px;'
                        f'padding:5px 10px 5px 12px;white-space:nowrap;">{before}</td>'
                        f'<td style="color:{muted};font-size:15px;padding:5px 10px;white-space:nowrap;">→</td>'
                        f'<td style="font-family:monospace;color:{accent};font-size:13px;'
                        f'font-weight:700;padding:5px 12px 5px 10px;white-space:nowrap;">{after}</td>'
                        f'</tr></table></div>'
                    )
        p.append('</div></div>')
        return ''.join(p)

    # ─────────────────────────────────────────────────────────────
    # HTML render (full page — legacy compatibility)
    # ─────────────────────────────────────────────────────────────

    parts = [
        f'''<html><body style="background:{bg2};color:{text};'''
        f'''font-family:'Pretendard','Segoe UI Variable','Segoe UI','Malgun Gothic','Yu Gothic UI','Microsoft YaHei UI',sans-serif;'''
        f'''font-size:13px;margin:0;padding:0;">'''
    ]

    # App intro banner
    parts.append(
        f'''<div style="background:{_mix(bg,accent,0.06)};border:1px solid {_mix(accent,bg,0.6)};'''
        f'''border-radius:10px;padding:14px 18px;margin:0 0 16px;">'''
        f'''<div style="margin-bottom:6px;">'''
        f'''<span style="font-size:14px;font-weight:700;color:{accent};">File Nexus Suite</span>'''
        f'''<span style="font-size:10px;font-weight:700;color:{bg};background:{accent};'''
        f'''border-radius:4px;padding:1px 7px;margin-left:8px;letter-spacing:0.3px;">v{APP_VERSION}</span>'''
        f'''</div>'''
        f'''<div style="font-size:12px;color:{muted};line-height:1.7;">{intro}</div>'''
        f'''</div>'''
    )

    for entry in sections:
        parts.append(_render_section(entry))

    parts.append('''</body></html>''')
    return ''.join(parts)



def _build_license_html() -> str:
    """Open-source license-notice HTML."""
    bg      = SURFACE
    text    = TEXT
    muted   = MUTED
    accent  = ACCENT
    border  = BORDER
    srf2    = SRF2

    entries = [
        {
            "category": "🐍 Runtime",
            "items": [
                {
                    "name": "Python",
                    "version": "3.x",
                    "license": "Python Software Foundation License v2 (PSF-2.0)",
                    "copyright": "Copyright © 2001–present Python Software Foundation",
                    "url": "https://www.python.org",
                    "note": "Python programming language runtime. PSF License requires this copyright notice to be retained in distributions.",
                },
            ],
        },
        {
            "category": "🖥️ GUI Framework",
            "items": [
                {
                    "name": "PySide6",
                    "version": "6.x",
                    "license": "GNU Lesser General Public License v3 (LGPL-3.0)",
                    "copyright": "Copyright © The Qt Company Ltd.",
                    "url": "https://doc.qt.io/qtforpython-6/",
                    "note": "Official Python bindings for Qt 6, developed by The Qt Company. Licensed under LGPL v3.\n\nFile Nexus Suite is built with PyInstaller. Users may replace this LGPL library by rebuilding from source — see the GitHub repository for build instructions.",
                },
            ],
        },
        {
            "category": "📚 Libraries",
            "items": [
                {
                    "name": "chardet",
                    "version": "—",
                    "license": "GNU Lesser General Public License v2.1 (LGPL-2.1)",
                    "copyright": "Copyright © 2001–present Mark Pilgrim and chardet contributors",
                    "url": "https://github.com/chardet/chardet",
                    "note": "Character encoding detection for text file import. Optional — loaded at runtime only if installed.\n\nFile Nexus Suite is built with PyInstaller. Users may replace this LGPL library by rebuilding from source — see the GitHub repository for build instructions.",
                },
                {
                    "name": "python-docx",
                    "version": "—",
                    "license": "MIT License",
                    "copyright": "Copyright © 2013 Steve Canny",
                    "url": "https://github.com/python-openxml/python-docx",
                    "note": "DOCX file reading for Text Merger. Optional — loaded at runtime only if installed.",
                },
                {
                    "name": "pdfplumber",
                    "version": "—",
                    "license": "MIT License",
                    "copyright": "Copyright © 2019 Jeremy Singer-Vine",
                    "url": "https://github.com/jsvine/pdfplumber",
                    "note": "PDF text extraction for Text Merger. Optional — loaded at runtime only if installed.",
                },
                {
                    "name": "openpyxl",
                    "version": "—",
                    "license": "MIT License",
                    "copyright": "Copyright © 2010 openpyxl contributors",
                    "url": "https://openpyxl.readthedocs.io",
                    "note": "XLSX file reading for Text Merger. Optional — loaded at runtime only if installed.",
                },
                {
                    "name": "python-hwpx",
                    "version": "—",
                    "license": "MIT License",
                    "copyright": "Copyright © Kyuhyun Koh (고규현)",
                    "url": "https://github.com/airmang/python-hwpx",
                    "note": "HWPX (KS X 6101 OWPML) text extraction for Text Merger. Pure-Python, no Hancom Office required. Optional — loaded at runtime only if installed.",
                },
            ],
        },
        {
            "category": "🎨 Icons",
            "items": [
                {
                    "name": "File Nexus Suite Icon Set",
                    "version": "—",
                    "license": "Free to use — No attribution required",
                    "copyright": "Created by Microsoft Copilot",
                    "url": "",
                    "note": "SVG vector icon set (line / filled styles) used for tabs, buttons, header, and settings navigation.\nNo external icon libraries were used. No additional copyright notice required.\n\nLine(라인) 스타일: 탭 아이콘, 헤더 버튼, 설정 네비게이션용\nFilled(채움) 스타일: 액션 버튼, 상태 버튼용\n\nIncluded icons: document, folder, folder_open, tag, refresh, wrench, magnifier,\nsave, trash, broom, question, info, list, clipboard, arrow_up, arrow_down, check",
                },
            ],
        },
        {
            "category": "📄 Application",
            "items": [
                {
                    "name": "File Nexus Suite",
                    "version": "—",
                    "license": "MIT License",
                    "copyright": "Copyright © 2026 Hanrim",
                    "url": "",
                    "note": "본 소프트웨어는 MIT 라이선스로 배포됩니다.\n저작권 고지를 유지하는 조건으로 사용·수정·재배포·판매가 모두 자유롭게 허용됩니다.\n\n개인 작업 도구로 시작했지만, 같은 작업을 하는 다른 분들에게도\n도움이 되기를 바라며 MIT 라이선스로 공개합니다.\n\n전체 소스 코드는 GitHub 저장소에서 공개됩니다:\nhttps://github.com/MerciHanrim/FileNexusSuite\n\n본 프로젝트는 AI 페어 프로그래밍(Claude)으로 개발되었습니다.\n기획·UX 설계·품질 관리는 Hanrim이 담당하고, 코드 작성은 AI와 협업하여 진행했습니다.\n\nThis software is distributed under the MIT License.\nFree to use, modify, redistribute, and sell, provided that the copyright notice is retained.\n\nOriginally built as a personal tool, now released under MIT\nin the hope it may help others with similar workflows.\n\nFull source code is publicly available at:\nhttps://github.com/MerciHanrim/FileNexusSuite\n\nThis project was developed using AI pair programming (Claude).\nPlanning, UX design, and quality management were done by Hanrim,\nwith code written in collaboration with AI.",
                },
            ],
        },
    ]

    parts = [f'<html><body style="background:{bg};color:{text};'
             f'font-family:\'Pretendard\',\'Segoe UI Variable\',\'Segoe UI\',\'Malgun Gothic\',\'Yu Gothic UI\',\'Microsoft YaHei UI\',sans-serif;'
             f'font-size:13px;margin:16px 20px 24px;">']

    # Localized summary banner
    summary = _t('license_summary')
    parts.append(
        f'<div style="background:{srf2};border:1px solid {accent}33;border-radius:9px;'
        f'padding:11px 16px;margin-bottom:18px;font-size:13px;color:{text};">'
        f'<span style="color:{accent};font-weight:700;margin-right:6px;">📋</span>'
        f'{summary}</div>'
    )

    for section in entries:
        parts.append(
            f'<div style="font-size:14px;font-weight:700;color:{accent};'
            f'border-bottom:2px solid {accent};padding-bottom:5px;margin:0 0 12px;">'
            f'{section["category"]}</div>'
        )
        for item in section["items"]:
            url_part = (
                f'<a href="{item["url"]}" style="color:{accent};font-size:11px;'
                f'text-decoration:none;">{item["url"]}</a>'
                if item["url"] else ""
            )
            parts.append(f'''
<div style="background:{srf2};border:1px solid {border};border-radius:9px;
            padding:13px 16px;margin-bottom:10px;">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:4px;">
    <span style="font-size:14px;font-weight:700;color:{text};">{item["name"]}</span>
    <span style="font-size:11px;color:{muted};background:{bg};border:1px solid {border};
                 border-radius:5px;padding:2px 9px;">{item["license"]}</span>
  </div>
  <div style="font-size:11px;color:{muted};margin:4px 0 2px;">{item["copyright"]}</div>
  {f'<div style="margin:3px 0;">{url_part}</div>' if url_part else ''}
  <div style="font-size:12px;color:{text};margin-top:7px;line-height:1.6;
              border-top:1px solid {border};padding-top:7px;">{item["note"]}</div>
</div>
''')
        parts.append('<div style="height:8px;"></div>')

    parts.append('</body></html>')
    return ''.join(parts)


# ═══════════════════════════════════════════════
# Main AppSuite window
# ═══════════════════════════════════════════════
class AppSuite(QMainWindow):
    def __init__(self):
        super().__init__()
        # ── Apply saved theme before building (prevents flash) ──
        _pre = _CFG.load()
        _saved = _pre.get('theme', 'auto')
        self._theme_name = _saved if (_saved in THEMES or _saved == 'auto') else 'auto'
        _effective = _resolve_theme(self._theme_name)
        if _effective != 'light':
            global _T, STYLE
            _T = THEMES[_effective]
            STYLE = make_style(_T)
            _unpack(_T)

        self.setWindowTitle("File Nexus Suite")
        self.setWindowIcon(_make_app_icon())
        self.setMinimumSize(1100,840)
        self.resize(1160,880)
        QApplication.instance().setStyleSheet(STYLE)
        self._build()
        # Register the global log function — _glog() can now be called from panels
        global _g_log_fn
        _g_log_fn = self._log
        self._refresh_dbg_toggle_style()
        self._load_config()
        self.retranslate_ui()
        self._setup_shortcuts()
        # Initial button-style application (in case apply_theme is not called)
        self._batch_panel.refresh_btn_styles()
        self._text_panel.refresh_btn_styles()
        self._tag_panel.refresh_btn_styles()
        self._merge_panel.refresh_btn_styles()
        self._fixer_panel.refresh_btn_styles()
        # First-run notice popup (shown when first_run_shown is missing in config)
        if not _CFG.get('first_run_shown', False):
            QTimer.singleShot(300, lambda: self._show_first_run())

    def _show_first_run(self):
        _show_first_run_notice(self)
        _CFG.update('first_run_shown', True)
        _CFG.save(_CFG._data)

    def dragEnterEvent(self,e): e.ignore()
    def dropEvent(self,e): e.ignore()


    # v1.0.6 #7 v2: 3 dead-code methods left over before SettingsDialog was extracted into its own QDialog
    # (_page_language / _on_lang_selected / _retranslate_dialog) were removed.
    # Full-grep verification: 0 callers + self._lang_radios is never initialized,
    # so they're unreachable at runtime. closeEvent is preserved as it is a normal AppSuite feature.

    def closeEvent(self, event):
        # Check working panels — if any worker is running, show a confirmation popup
        busy_panels = []
        for attr, label in [
            ('_merge_panel', 'Text Merger'),
            ('_text_panel',  'Text Converter'),
            ('_tag_panel',   'Tag Editor'),
            ('_fixer_panel', 'Text Fixer'),
            ('_bulk_panel',  'Bulk Fixer'),
        ]:
            panel = getattr(self, attr, None)
            if panel and hasattr(panel, 'is_busy') and panel.is_busy():
                busy_panels.append(label)

        if busy_panels:
            dlg = QDialog(self)
            dlg.setWindowTitle(_t('close_busy_title'))
            try: dlg.setWindowIcon(_make_app_icon())
            except Exception: pass
            dlg.setMinimumWidth(380)
            dlg.setWindowFlags(dlg.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
            dlg.setStyleSheet(
                f"QDialog{{background:{SURFACE};}} QLabel{{background:transparent;color:{TEXT};}}")
            root = QVBoxLayout(dlg)
            root.setContentsMargins(24, 20, 24, 16); root.setSpacing(12)

            row = QHBoxLayout(); row.setSpacing(14); row.setAlignment(Qt.AlignmentFlag.AlignTop)
            ico = QLabel(); ico.setPixmap(_dlg_icon_pix('warn', 40))
            ico.setFixedSize(40, 40); ico.setStyleSheet("background:transparent;")
            msg_text = '  '.join(f'▸ {p}' for p in busy_panels) + f'\n\n{_t("close_busy_msg")}'
            msg = QLabel(msg_text)
            msg.setWordWrap(True)
            msg.setStyleSheet(f"font-size:13px;color:{TEXT};")
            row.addWidget(ico); row.addWidget(msg, 1)
            root.addLayout(row)

            sep = QFrame(); sep.setFrameShape(QFrame.HLine)
            sep.setStyleSheet(f"background:{BORDER};max-height:1px;border:none;")
            root.addWidget(sep)

            br = QHBoxLayout(); br.setSpacing(8); br.addStretch()
            btn_cancel = QPushButton(_t('close_busy_cancel'))
            btn_cancel.setStyleSheet(_btn_style(False))
            btn_cancel.clicked.connect(dlg.reject)
            btn_exit = QPushButton(_t('close_busy_exit'))
            btn_exit.setStyleSheet(
                "QPushButton{background:#C04030;border:none;color:white;"
                "border-radius:8px;padding:9px 28px;font-size:12px;font-weight:600;}"
                "QPushButton:hover{background:#A03020;}")
            btn_exit.clicked.connect(dlg.accept)
            btn_cancel.setDefault(True)
            br.addWidget(btn_cancel); br.addWidget(btn_exit)
            root.addLayout(br)

            if dlg.exec() != QDialog.DialogCode.Accepted:
                event.ignore()
                return

        self._save_config()
        if hasattr(self, '_merge_panel'): self._merge_panel._stop_worker()
        if hasattr(self, '_text_panel'):  self._text_panel._stop_worker()
        if hasattr(self, '_tag_panel'):   self._tag_panel._stop_worker()
        if hasattr(self, '_fixer_panel'): self._fixer_panel._stop_worker()
        if hasattr(self, '_bulk_panel'):  self._bulk_panel._stop_worker()
        # Record clean shutdown to the session log file
        global _session_log_fp
        if _session_log_fp:
            try:
                _session_log_fp.write(f"\n[{datetime.now().strftime('%H:%M:%S')}] ✅ App exited normally\n")
                _session_log_fp.close()
            except Exception:
                pass
            _session_log_fp = None
        super().closeEvent(event)

    def _load_config(self):
        cfg = _CFG._data          # __init__ already called load() — avoid duplicate file I/O
        global _current_lang
        _current_lang = cfg.get('language', _detect_os_lang())
        theme = cfg.get('theme', 'auto')
        if theme != self._theme_name:
            self._theme_name = theme
            self.apply_theme(theme)
        self._batch_panel.apply_config(cfg.get('batch', {}))
        self._text_panel.apply_config(cfg.get('text_converter', {}))
        self._tag_panel.apply_config(cfg.get('tag_editor', {}))
        self._merge_panel.apply_config(cfg.get('text_merger', {}))
        self._fixer_panel.apply_config(cfg.get('text_fixer', {}))
        self._bulk_panel.apply_config(cfg.get('bulk_fixer', {}))

    def _save_config(self):
        _CFG.save({
            'theme':            self._theme_name,
            'shortcuts':        _CFG.get('shortcuts', {}),
            'language':         _CFG.get('language', 'ko'),
            'first_run_shown':  _CFG.get('first_run_shown', False),
            'output_dir':       _CFG.get('output_dir', str(_OUTPUT_DIR)),
            'batch':            self._batch_panel.get_config(),
            'text_converter':   self._text_panel.get_config(),
            'tag_editor':       self._tag_panel.get_config(),
            'text_merger':      self._merge_panel.get_config(),
            'text_fixer':       self._fixer_panel.get_config(),
            'bulk_fixer':       self._bulk_panel.get_config(),
        })

    def _setup_shortcuts(self):
        tabs = self.findChild(QTabWidget, "main_tabs")
        if not tabs: return
        cfg_sc = _CFG.get('shortcuts', {})
        # Create QShortcut for the first time, or reuse
        if not hasattr(self, '_tab_shortcuts'):
            self._tab_shortcuts = []
            for i in range(6):
                def _switch(idx=i): tabs.setCurrentIndex(idx)
                sc = QShortcut(self); sc.activated.connect(_switch)
                self._tab_shortcuts.append(sc)
        for i, sid in enumerate(['tab_1','tab_2','tab_3','tab_4','tab_5','tab_6']):
            key = cfg_sc.get(sid, SHORTCUT_DEFS[sid]['default'])
            self._tab_shortcuts[i].setKey(QKeySequence(key))

    def _log(self,msg):
        ts=datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.dbg.append(f'<span style="color:{MUTED};">[{ts}]</span> {msg}')

    def _build(self):
        cw=QWidget(); self.setCentralWidget(cw)
        root=QVBoxLayout(cw); root.setContentsMargins(20,16,20,16); root.setSpacing(10)
        # Header (copyright removed — moved to bottom footer)
        hdr=QHBoxLayout()
        self._hdr_title=QLabel("File Nexus Suite")
        self._hdr_title.setStyleSheet(f"color:{ACCENT};font-size:18px;font-weight:700;letter-spacing:-0.5px;font-family:'Pretendard','Segoe UI Variable','Segoe UI','Malgun Gothic','Yu Gothic UI','Microsoft YaHei UI',sans-serif;")
        self._hdr_ver=QLabel(f"v{APP_VERSION}")
        self._hdr_ver.setStyleSheet(f"color:{MUTED};font-size:12px;font-weight:400;padding-top:5px;letter-spacing:0.2px;")
        self._hdr_ver.setVisible(False)
        self._hdr_sep=QLabel("·")
        self._hdr_sep.setStyleSheet(f"color:{MUTED};font-size:14px;padding-top:2px;")
        self._hdr_sub=QLabel(_t("app_subtitle"))
        self._hdr_sub.setStyleSheet(f"color:{MUTED};font-size:13px;font-weight:400;padding-top:3px;letter-spacing:0.2px;")
        self._hdr_ver_inline = QLabel(f"v{APP_VERSION}")
        self._hdr_ver_inline.setStyleSheet(f"color:{MUTED};font-size:11px;font-weight:400;letter-spacing:0.3px;padding-top:5px;")
        hdr.addWidget(self._hdr_title); hdr.addSpacing(10); hdr.addWidget(self._hdr_sep); hdr.addSpacing(10); hdr.addWidget(self._hdr_sub); hdr.addSpacing(8); hdr.addWidget(self._hdr_ver_inline); hdr.addStretch()
        self._btn_help=_HelpButton(); self._btn_help.setFixedSize(38,38)
        self._btn_help.setIcon(_svg_icon('question_line', TEXT)); self._btn_help.setIconSize(QSize(26,26))
        self._btn_help.setObjectName("btn_help"); self._btn_help.setToolTip("도움말")
        self._btn_help.clicked.connect(self._open_help); hdr.addWidget(self._btn_help)
        hdr.addSpacing(6)
        self._btn_settings=_GearButton(); self._btn_settings.setFixedSize(38,38)
        self._btn_settings.setIcon(_svg_icon('gear_line', TEXT)); self._btn_settings.setIconSize(QSize(22,22))
        self._btn_settings.setObjectName("btn_settings"); self._btn_settings.setToolTip(_t("settings_tooltip"))
        self._btn_settings.clicked.connect(self._open_settings); hdr.addWidget(self._btn_settings)
        root.addLayout(hdr)
        self._hdr_div=QFrame(); self._hdr_div.setFrameShape(QFrame.HLine)
        self._hdr_div.setStyleSheet(f"background:{BORDER};max-height:1px;border:none;"); root.addWidget(self._hdr_div)
        # Main tabs
        main_tabs=QTabWidget(); main_tabs.setObjectName("main_tabs")
        main_tabs.setIconSize(QSize(18, 18))
        self._merge_panel=TextMergerPanel();   main_tabs.addTab(self._merge_panel,  "  Text Merger")
        self._text_panel=TextConverterPanel(); main_tabs.addTab(self._text_panel,   "  Text Converter")
        self._tag_panel=TagEditorPanel();      main_tabs.addTab(self._tag_panel,    "  Tag Editor")
        self._batch_panel=BatchRenamerPanel(); main_tabs.addTab(self._batch_panel,  "  Batch Renamer")
        self._fixer_panel=TextFixerPanel();    main_tabs.addTab(self._fixer_panel,  "  Text Fixer")
        self._bulk_panel=BulkFixerPanel();     main_tabs.addTab(self._bulk_panel,   "  Bulk Fixer")
        # Apply SVG tab icons
        _tab_icons = ['document_line', 'folder_open_line', 'tag_line', 'folder_line', 'wrench_line', 'broom_line']
        for i, key in enumerate(_tab_icons):
            main_tabs.setTabIcon(i, _svg_icon(key, ACCENT))
        self._main_tabs = main_tabs

        # Reset sub-tabs to first when main tab changes
        def _on_main_tab_changed(idx):
            if idx == 1:  # Text Converter
                self._text_panel._switch('txt2epub')
            elif idx == 2:  # Tag Editor
                self._tag_panel._switch_mode('remove')
            elif idx == 3:  # Batch Renamer
                self._batch_panel._switch_main_tab('folder')
        main_tabs.currentChanged.connect(_on_main_tab_changed)
        root.addWidget(main_tabs,stretch=1)
        # Debug log (collapsed by default)
        dbg_frame=QFrame(); dbg_frame.setFrameShape(QFrame.NoFrame)
        dl=QVBoxLayout(dbg_frame); dl.setContentsMargins(8,4,0,0); dl.setSpacing(3)

        dh=QHBoxLayout(); dh.setContentsMargins(0,0,0,0)
        self._dbg_toggle=QPushButton("Debug Log  ▼")
        self._dbg_toggle.setObjectName("btn_dbg_clear")
        self._dbg_toggle.setIcon(_svg_icon('magnifier', MUTED, size=14))
        self._dbg_toggle.setIconSize(QSize(14,14))
        self._dbg_toggle.setStyleSheet("")
        self._dbg_toggle.clicked.connect(self._toggle_dbg)
        bc=QPushButton(_t("btn_clear")); bc.setObjectName("btn_dbg_clear"); bc.setMaximumWidth(70)
        dh.addWidget(self._dbg_toggle); dh.addStretch()
        self._dbg_clear_btn=bc; dh.addWidget(bc)
        dl.addLayout(dh)

        self.dbg=QTextEdit(); self.dbg.setObjectName("dbg_edit")
        self.dbg.setReadOnly(True); self.dbg.setFixedHeight(110)
        bc.clicked.connect(self.dbg.clear)
        dl.addWidget(self.dbg)
        root.addWidget(dbg_frame)
        # Default collapsed state
        self._dbg_expanded = False
        self.dbg.setVisible(False)
        self._dbg_clear_btn.setVisible(False)
        self._log("✅ File Nexus Suite 시작 — 탭을 선택하여 원하는 기능을 사용하세요")
        # Bottom copyright footer (always pinned)
        self._footer_copyright=QLabel("Copyright © 2026 Hanrim")
        self._footer_copyright.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._footer_copyright.setStyleSheet(f"color:{MUTED};font-size:12px;padding-top:2px;")
        root.addWidget(self._footer_copyright)

    def _toggle_dbg(self):
        self._dbg_expanded = not self._dbg_expanded
        self.dbg.setVisible(self._dbg_expanded)
        self._dbg_clear_btn.setVisible(self._dbg_expanded)
        arrow = "▲" if self._dbg_expanded else "▼"
        self._dbg_toggle.setText(f"Debug Log  {arrow}")
        self._refresh_dbg_toggle_style()

    def _refresh_dbg_toggle_style(self):
        self._dbg_toggle.setStyleSheet(
            f"QPushButton{{background:transparent;border:none;color:{MUTED};"
            f"font-size:11px;font-weight:600;text-align:left;padding:0;}}"
            f"QPushButton:hover{{color:{TEXT};}}"
        )
        self._dbg_toggle.setIcon(_svg_icon('magnifier', MUTED, size=14))
        self._dbg_toggle.setIconSize(QSize(14,14))

    def _open_help(self):
        dlg = HelpDialog(self)
        dlg.exec()

    def _open_settings(self):
        dlg=SettingsDialog(self, current_theme=self._theme_name,
                           current_shortcuts=_CFG.get('shortcuts', {}),
                           current_language=_CFG.get('language', _detect_os_lang()))
        # Connect signals — apply / double-click reflects immediately, window stays open
        def _on_theme(name):
            if name != self._theme_name:
                self._theme_name = name; self.apply_theme(name)
        def _on_shortcuts(sc):
            if sc != _CFG.get('shortcuts', {}):
                _CFG.update('shortcuts', sc); self._setup_shortcuts()
        def _on_language(lang):
            global _current_lang
            _current_lang = lang
            _CFG.update('language', lang)
            _glog(f"🌐 Language changed: {lang}")
            self.retranslate_ui()
        def _on_output_dir(odir):
            _CFG.update('output_dir', odir)
            _glog(f"📂 Output folder changed: {odir}")
        dlg.theme_applied.connect(_on_theme)
        dlg.shortcuts_applied.connect(_on_shortcuts)
        dlg.language_applied.connect(_on_language)
        dlg.output_dir_applied.connect(_on_output_dir)
        dlg.exec()  # Stay modal — close only via the close button


    def retranslate_ui(self):
        """Refresh app-wide UI strings on language change."""
        try:
            self._hdr_sub.setText(_t('app_subtitle'))
            # Main tab names
            if hasattr(self, '_main_tabs'):
                tabs = self._main_tabs
                tabs.setTabText(0, "  Text Merger")
                tabs.setTabText(1, "  Text Converter")
                tabs.setTabText(2, "  Tag Editor")
                tabs.setTabText(3, "  Batch Renamer")
                tabs.setTabText(4, "  Text Fixer")
                tabs.setTabText(5, "  Bulk Fixer")
            # Debug toggle
            if hasattr(self, '_dbg_toggle'):
                arrow = "▲" if self.dbg.isVisible() else "▼"
                self._dbg_toggle.setText(f"{_t('debug_log')}  {arrow}")
            if hasattr(self, '_dbg_clear_btn'):
                self._dbg_clear_btn.setText(_t('btn_clear'))
            # Per-panel retranslate
            self._merge_panel.retranslate()
            self._text_panel.retranslate()
            self._tag_panel.retranslate()
            self._batch_panel.retranslate()
            self._fixer_panel.retranslate()
            self._bulk_panel.retranslate()
        except Exception as e:
            _glog(f"⚠ retranslate_ui error: {e}")


    def apply_theme(self, name):
        global _T, STYLE
        resolved = _resolve_theme(name)          # 'auto' → 'light' or 'dark'
        if resolved not in THEMES:               # Fallback for deleted theme keys
            resolved = 'light'
        _T = THEMES[resolved]; STYLE = make_style(_T); _unpack(_T)
        QApplication.instance().setStyleSheet(STYLE)
        pal = self._make_palette(_T)
        QApplication.instance().setPalette(pal)

        # ── Header inline style ─────────────────
        self._hdr_title.setStyleSheet(
            f"color:{ACCENT};font-size:18px;font-weight:700;letter-spacing:-0.5px;"
            f"font-family:'Pretendard','Segoe UI Variable','Segoe UI','Malgun Gothic','Yu Gothic UI','Microsoft YaHei UI',sans-serif;")
        self._hdr_ver.setStyleSheet(f"color:{MUTED};font-size:12px;font-weight:400;padding-top:5px;letter-spacing:0.2px;")
        if hasattr(self, '_hdr_ver_inline'):
            self._hdr_ver_inline.setStyleSheet(f"color:{MUTED};font-size:11px;font-weight:400;letter-spacing:0.3px;padding-top:2px;")
        self._hdr_sep.setStyleSheet(f"color:{MUTED};font-size:14px;padding-top:2px;")
        self._hdr_sub.setStyleSheet(
            f"color:{MUTED};font-size:13px;font-weight:400;padding-top:3px;letter-spacing:0.2px;"
            f"font-family:'Pretendard','Segoe UI Variable','Segoe UI','Malgun Gothic','Yu Gothic UI','Microsoft YaHei UI',sans-serif;")
        self._hdr_div.setStyleSheet(
            f"background:{BORDER};max-height:1px;border:none;")
        self._footer_copyright.setStyleSheet(
            f"color:{MUTED};font-size:12px;padding-top:2px;")

        # ── Batch Renamer drop zone + tab buttons ──
        for drop in [self._batch_panel._f_drop, self._batch_panel._p_drop]:
            drop.set_idle()
        self._batch_panel._update_main_tab_style()
        self._batch_panel._update_opt_tab_style()
        self._batch_panel._sa_folder.refresh_style()
        self._batch_panel._sa_file.refresh_style()
        self._batch_panel.refresh_btn_styles()   # Refresh buttons not reached by QSS
        self._text_panel.refresh_btn_styles()    # Refresh buttons not reached by QSS
        self._tag_panel.refresh_btn_styles()     # Refresh buttons not reached by QSS
        self._merge_panel.refresh_btn_styles()   # Refresh buttons not reached by QSS
        self._fixer_panel.refresh_btn_styles()   # Refresh buttons not reached by QSS
        self._bulk_panel.refresh_btn_styles()    # Refresh buttons not reached by QSS

        # ── Tag Editor drop zone + option panel + tab buttons ─
        self._tag_panel._drop_zone.set_idle()

        # ── Tag Editor option-panel frame ────────
        panel_ss = (f"QFrame#tag_opt_frame{{background:{SRF2};border:1px solid {BORDER};"
                    f"border-radius:8px;}}")
        self._tag_panel._remove_panel.setStyleSheet(panel_ss)
        self._tag_panel._add_panel.setStyleSheet(panel_ss)

        # ── Tag Editor tab buttons ───────────────
        self._tag_panel._update_tab_style()
        self._tag_panel._refresh_tree_styles()
        if hasattr(self._tag_panel, '_lbl_rm_pos'):
            self._tag_panel._lbl_rm_pos.setStyleSheet(f"font-size:13px;color:{MUTED};")
        if hasattr(self._tag_panel, '_lbl_rm_tag'):
            self._tag_panel._lbl_rm_tag.setStyleSheet(f"font-size:13px;color:{MUTED};")

        # ── Text Converter tab buttons ───────────
        self._text_panel._switch(self._text_panel._mode)

        # ── Text Merger drop zone + tree refresh ──
        self._merge_panel._tree.viewport().update()
        self._merge_panel._refresh_drop_zone()

        # ── Debug Log toggle button ──────────────
        self._refresh_dbg_toggle_style()

        # ── Tab SVG icon color refresh ───────────
        if hasattr(self, '_main_tabs'):
            _tab_icons = ['document_line', 'folder_open_line', 'tag_line', 'folder_line', 'wrench_line', 'broom_line']
            for i, key in enumerate(_tab_icons):
                self._main_tabs.setTabIcon(i, _svg_icon(key, ACCENT))

        # ── Header button icon refresh ───────────
        if hasattr(self, '_btn_help'):
            self._btn_help.setIcon(_svg_icon('question_line', TEXT)); self._btn_help.setIconSize(QSize(26,26))
        if hasattr(self, '_btn_settings'):
            self._btn_settings.setIcon(_svg_icon('gear_line', TEXT)); self._btn_settings.setIconSize(QSize(22,22))

        # ── SettingsDialog / dialogs auto-refresh on re-open ──

    @staticmethod
    def _make_palette(t):
        pal=QPalette()
        pal.setColor(QPalette.Window,QColor(t['BG']))
        pal.setColor(QPalette.WindowText,QColor(t['TEXT']))
        pal.setColor(QPalette.Base,QColor(t['SURFACE']))
        pal.setColor(QPalette.AlternateBase,QColor(t['SRF2']))
        pal.setColor(QPalette.Text,QColor(t['TEXT']))
        pal.setColor(QPalette.Button,QColor(t['SURFACE']))
        pal.setColor(QPalette.ButtonText,QColor(t['TEXT']))
        pal.setColor(QPalette.Highlight,QColor(t['ACCENT']))
        pal.setColor(QPalette.HighlightedText,QColor("#FFFFFF"))
        return pal

# ── Entry point ──────────────────────────────
if __name__ == "__main__":
    # ── Single-instance guarantee (before QApplication is created) ─
    _si_lock = _check_single_instance()
    _crash_log_dir = _setup_crash_logger()  # Auto-save crash logs

    # Windows taskbar icon fix — set AppUserModelID
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("FileNexusSuite")
        except Exception:
            pass

    app=QApplication(sys.argv)
    app.setStyle(_FastToolTipStyle())
    _app_font = QFont("Segoe UI Variable", 10)
    if not _app_font.exactMatch():
        _app_font = QFont("Segoe UI", 10)
    _app_font.setHintingPreference(QFont.PreferFullHinting)
    app.setFont(_app_font)
    app.setWindowIcon(_make_app_icon())   # Taskbar icon
    pal=QPalette()
    pal.setColor(QPalette.Window,QColor(BG))
    pal.setColor(QPalette.WindowText,QColor(TEXT))
    pal.setColor(QPalette.Base,QColor(SURFACE))
    pal.setColor(QPalette.AlternateBase,QColor(SRF2))
    pal.setColor(QPalette.Text,QColor(TEXT))
    pal.setColor(QPalette.Button,QColor(SURFACE))
    pal.setColor(QPalette.ButtonText,QColor(TEXT))
    pal.setColor(QPalette.Highlight,QColor(ACCENT))
    pal.setColor(QPalette.HighlightedText,QColor("#FFFFFF"))
    app.setPalette(pal)
    win=AppSuite()
    win.show()
    sys.exit(app.exec())
