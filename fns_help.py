# Copyright © 2026 Hanrim
# Licensed under the MIT License.
# Free to use, modify, redistribute, and sell, provided that the copyright notice is retained.

"""File Nexus Suite — Help system module (Phase 3, v1.1.1).

Help dialog, help button widget, and license dialog. Help content uses
Qt Linguist runtime translation (self.tr()) instead of hard-coded
per-language Python branches. License HTML build is delegated to a
dedicated LicenseDialog class whose static build_html() helper is
reused by SettingsDialog's License tab.

Contents:
  - _HelpButton: animated help button widget with sine-wave icon hover effect
  - HelpDialog: standalone help window with sidebar navigation. Help content
                lives as instance methods (_get_intro, _get_sections,
                _render_section) so self.tr() can wrap every translatable
                string. Section icons are looked up by index via the
                _SECTION_ICONS class constant instead of by translated title.
  - LicenseDialog: standalone license window. The build_html() staticmethod
                produces the open-source license HTML and is reused by the
                SettingsDialog License tab (and by preview_ui).

Phase 3 of the v1.1.1 help modularization track:
  - Removes the 5-language Python branches; the same content now lives as
    English base strings wrapped in self.tr().
  - Removes the legacy full-page HTML render path from _build_help_html().
  - Removes the _get_help_data() module helper.
  - Moves _build_license_html() into LicenseDialog.build_html().
  - The HelpDialog chrome strings (window title, sidebar title, Close,
    About) are part of the HelpDialog context and therefore ship in
    help_*.qm together with the help content.

Dependencies:
  - PySide6 (Qt widgets, GUI primitives)
  - FileNexusSuite main module — APP_VERSION, _tr_args, and theme color
    tokens (SURFACE, BG, SRF2, BORDER, TEXT, MUTED, ACCENT) are imported
    lazily inside each function/method body to avoid a circular import
    with the main module and to pick up runtime mutations (theme changes
    update the color globals).
"""

# ── Standard Library ─────────────────────
import math as _math

# ── PySide6 ──────────────────────────────
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QStackedWidget,
    QStyle, QStyleOptionButton, QStylePainter, QTextBrowser, QVBoxLayout
)


# ════════════════════════════════════════════════
# _HelpButton — animated help button widget
# ════════════════════════════════════════════════
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
        opt = QStyleOptionButton()
        self.initStyleOption(opt)
        p = QStylePainter(self)
        # Draw button background only (no icon yet)
        opt.icon = self.icon().__class__()  # empty icon
        p.drawControl(QStyle.ControlElement.CE_PushButton, opt)
        # Draw the icon with vertical offset
        icon = self.icon()
        if not icon.isNull():
            sz = self.iconSize()
            x = (self.width() - sz.width()) // 2
            y = (self.height() - sz.height()) // 2 + int(self._offset)
            icon.paint(p, x, y, sz.width(), sz.height())


# ════════════════════════════════════════════════
# HelpDialog — standalone help window with sidebar navigation
# ════════════════════════════════════════════════
class HelpDialog(QDialog):
    """Standalone help window opened from the main UI — sidebar navigation.

    Help content (intro text and 8 sections) is defined as English base
    strings wrapped in self.tr(); QTranslator picks the right runtime
    translation via help_*.qm. Section icons are mapped by index, not
    by translated title, so language switches don't break the icon lookup.
    """

    # Section icons by index — 8 fixed sections matching _get_sections() order
    _SECTION_ICONS = [
        'document_line',     # 0: Text Merger
        'folder_open_line',  # 1: Text Converter
        'tag_line',          # 2: Tag Editor
        'folder_line',       # 3: Batch Renamer
        'wrench_line',       # 4: Text Fixer
        'broom_line',        # 5: Bulk Fixer
        'keyboard_line',     # 6: Shortcuts & Tips
        'license_line',      # 7: File creation notice
    ]

    def __init__(self, parent=None):
        from FileNexusSuite import _tr_args, APP_VERSION, BG
        super().__init__(parent)
        self.setWindowTitle(_tr_args(self.tr('💡  Help — File Nexus Suite v%1'), APP_VERSION))
        self.setMinimumSize(700, 560)
        self.resize(760, 640)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setStyleSheet(f"QDialog{{background:{BG};}}")
        self._nav_btns = []
        self._build()

    # ── Help content (English base + self.tr()) ──────────────────
    def _get_intro(self) -> str:
        """Help intro paragraph shown on the About page."""
        return self.tr(
            "File Nexus Suite is an integrated file utility for managing text, "
            "e-books, and media files. Text merging, EPUB conversion, file-name "
            "tag editing, batch renaming, line-break correction, and bulk fixing "
            "— six core features, all in one window."
        )

    def _get_sections(self) -> list:
        """Return 8 help sections — English base strings wrapped in self.tr().

        Each entry is (icon, title, subtitle, desc, items). Items are
        tuples whose first element is the kind ('step', 'tip', 'warn',
        'info', 'note', 'feature', 'example', 'shortcut', 'formats',
        'divider', 'sub'). Non-translatable elements (format labels,
        shortcut keys, decorative dividers) are kept as plain literals.
        """
        tr = self.tr
        return [
            # ── 0: Text Merger ──────────────────────────────
            ('📋', tr('Text Merger'),
                   tr('Merge multiple files into a single text file'),
                   tr('Combine files of the formats below into one text file in any order. DOCX, PDF, and XLSX require the respective libraries to be installed.'),
             [
              ('formats', [('TXT', 'native'), ('MD', 'native'), ('CSV', 'native'), ('LOG', 'native'), ('JSON', 'native'), ('XML', 'native'), ('HTML', 'native'), ('PY', 'native'), ('DOCX', 'lib'), ('PDF', 'lib'), ('XLSX', 'lib'), ('HWPX', 'lib')]),
              ('step', tr('<b>Add files</b> — Click <code>[📄 Add Files]</code> or drag and drop files onto the list. Unsupported formats are filtered out automatically.')),
              ('step', tr('<b>Set order</b> — Drag items in the list or use <code>[Up]</code> / <code>[Down]</code> to set the merge order.')),
              ('step', tr("<b>Set encoding</b> — Select the <b>read encoding</b> for each file via the combo box, and choose the <b>save encoding</b> in the 'Save Settings' panel.")),
              ('step', tr("<b>File separator</b> (optional) — Enable 'Insert File Separator' to automatically insert a divider line with the filename between each file.")),
              ('step', tr('<b>Set save path</b> (optional) — Click <code>[Set Path]</code> to pre-select a save location. If not set, a save dialog will appear when you run the merge.')),
              ('step', tr('<b><code>[▶ Merge & Save]</code></b> — Click to merge. The completion message shows a per-file encoding summary.')),
              ('divider',),
              ('tip', tr('<b>Auto encoding detection</b> — If chardet is installed, encoding is detected automatically when files are added. If accuracy is low, select manually.')),
              ('tip', tr('<b>Save encoding guide</b> — UTF-8: general use / UTF-8-BOM: prevents garbled text in Excel / EUC-KR·CP949: legacy Korean apps / UTF-16: special use / <b>Shift-JIS·GBK·Big5</b>: Japanese / Chinese (Simplified·Traditional) legacy systems')),
              ('tip', tr('<b>Separator format</b> — When enabled, the following line is inserted before each file: <code>───── ▶ filename.txt ──────</code>')),
              ('info', tr('If a file fails to read, it is skipped and the rest are merged normally. Errors are shown in the completion message.')),
              ('warn', tr('<code>[Undo]</code> deletes the merged output file. <b>Original files are never modified.</b>')),
             ]),

            # ── 1: Text Converter ──────────────────────────
            ('🔄', tr('Text Converter'),
                   tr('Convert between TXT and EPUB formats'),
                   tr('Convert TXT files into EPUB e-books, or extract text from EPUB files. Multiple files are converted automatically in sequence.'),
             [
              ('note', tr('Select <b>[TXT → EPUB]</b> or <b>[EPUB → TXT]</b> at the top first.')),
              ('step', tr('<b>Add files</b> — Click <code>[📄 Add Files]</code> or drag and drop.')),
              ('step', tr("<b>TXT → EPUB settings</b> — Enter <b>title, author, and language</b> in the 'Book Info' panel and choose a <b>chapter splitting method</b>.")),
              ('step', tr("<b>EPUB → TXT settings</b> — Configure chapter separator, title inclusion, blank line cleanup, and save encoding in the 'Conversion Options' panel.")),
              ('step', tr('<b>Output folder</b> (optional) — The default output folder is set in ⚙ Settings (default: <code>Output/</code>). The folder opens automatically after saving.')),
              ('step', tr('<b><code>[▶ Start Conversion]</code></b> — The progress bar shows the status of each file.')),
              ('divider',),
              ('feature', tr('TXT → EPUB Chapter Splitting'),
                          tr('<b>Divider-based</b> — Lines made of repeating symbols like <code>===</code>, <code>---</code>, or <code>★★★</code> are treated as chapter boundaries.<br><br><b>3+ blank lines</b> — Sections separated by 3 or more consecutive blank lines are treated as chapters.<br><br><b>Single chapter</b> — The entire file is treated as one chapter.')),
              ('feature', tr('EPUB → TXT Conversion Options'),
                          tr('<b>Add chapter separator</b> — Inserts a divider at each chapter boundary (default: on).<br><b>Include chapter titles</b> — Displays chapter titles from the EPUB below the divider (default: on).<br><b>Clean up blank lines</b> — Removes excessive blank lines generated during extraction (default: on).<br><b>Save encoding</b> — Choose the encoding for the output TXT file (default: UTF-8).')),
              ('tip', tr('Setting an output folder keeps results separate from your originals, making it easy to collect all converted files in one place.')),
              ('tip', tr('Do not close the window while conversion is in progress — it may interrupt the process.')),
             ]),

            # ── 2: Tag Editor ──────────────────────────────
            ('🏷️', tr('Tag Editor'),
                    tr('Add or remove tags from file names in bulk'),
                    tr('Batch-add or batch-remove bracket tags like <code>[Draft]</code> or <code>[Final]</code> from file names, and clean up leading zeros all at once.'),
             [
              ('note', tr('Choose <b>[Remove Tags]</b>, <b>[Add Tags]</b>, or <b>[Remove Leading Zeros]</b> from the top tab first.')),
              ('step', tr("<b>Add files or folders</b> — Use <code>[📄 Add Files]</code> / <code>[📂 Add Folder]</code> or drag and drop. Adding a folder reads files recursively based on the 'Include subfolders' option.")),
              ('step', tr("<b>Filter settings</b> — Specify target extensions in the 'Filter' panel (comma-separated). Enable 'All extensions' to process all files regardless of type.")),
              ('step', tr('<b>Configure options</b> — Set mode-specific options in the right panel.')),
              ('step', tr("<b>Preview</b> — Click <code>[Preview]</code> to see the 'Before → After' table. <b>Always verify before applying.</b>")),
              ('step', tr('<b>Apply</b> — Click <code>[Apply]</code> if the results look correct.')),
              ('divider',),
              ('feature', tr('Remove Tags'),
                          tr('Enter a specific tag in the tag field to remove only that tag. <b>Leave the field empty to remove all <code>[ ]</code> bracket tags.</b><br><br>Example: entering <code>Final</code> removes only <code>[Final]</code>, leaving other tags intact.')),
              ('feature', tr('Add Tags'),
                          tr('Choose the tag to add and its position (<b>front</b> or <b>back</b> of the filename) in the right panel. If the tag already exists, it will not be added again.')),
              ('feature', tr('Remove Leading Zeros'),
                          tr('Automatically removes leading zeros from file names (001 → 1, 007 → 7). <b>Numbers connected by hyphens, such as dates, are automatically protected.</b>')),
              ('example', tr('Meeting notes 001.docx'), tr('Meeting notes 1.docx')),
              ('example', tr('Lecture 007 final.pdf'), tr('Lecture 7 final.pdf')),
              ('example', tr('2024-01-01 diary.txt'), tr('2024-01-01 diary.txt  ← protected, no change')),
              ('warn', tr('<b>File renaming can be undone once with [Undo] immediately after applying.</b> However, the undo data is lost if you run another task or close the window. Always verify with <code>[Preview]</code> before clicking <code>[Apply]</code>.')),
             ]),

            # ── 3: Batch Renamer ───────────────────────────
            ('📁', tr('Batch Renamer'),
                   tr('Rename folders and files in bulk'),
                   tr("Rename subfolders or files using pattern-based rules. Supports 'Smart Extract' (auto-detect) and 'Sequential Number' (manual) modes."),
             [
              ('note', tr('Select <b>[Folder Rename]</b> or <b>[File Rename]</b> from the top tab first.')),
              ('step', tr('<b>Select target folder</b> — Use <code>[📂 Select Folder]</code> or drag and drop to specify the <b>parent folder</b>. The folder itself is not changed — only its <b>contents</b> are renamed.')),
              ('step', tr("<b>Select method</b> — Choose 'Smart Extract' or 'Sequential Number' in the right panel.")),
              ('step', tr('<b>Preview</b> — Click <code>[Preview]</code> to review changes. Conflicts are highlighted in the table.')),
              ('step', tr('<b>Rename</b> — Click <code>[Rename]</code>. You can undo once with <code>[Undo]</code> immediately after.')),
              ('divider',),
              ('feature', tr('🔍 Smart Extract'),
                          tr('Automatically extracts numbers from existing names and reconstructs them.<br><br><b>Common prefix handling</b> — Auto-detect / Manual entry / Keep as-is.<br><b>Prefix · Suffix</b> — Text to add before or after the reconstructed name.')),
              ('feature', tr('🔢 Sequential Number'),
                          tr("Assigns numbers in sequence from first to last. All options are set manually.<br><br><b>Start number</b> — Choose 00 or 01. <b>Digits</b> — Auto or fixed 2/3/4. <b>Prefix · Suffix</b> — Text around the number. <b>Name preservation</b> — 'Number only' or 'Number + original name'. <b>Number reset</b> — 'Continuous' or 'Reset per group'.")),
              ('tip', tr('File extensions are always preserved automatically.')),
              ('tip', tr('Dragging a folder recursively scans subfolders and builds groups automatically.')),
              ('tip', tr('Explorer windows open to the target folder are automatically closed before renaming and reopened when done.')),
              ('warn', tr('<b>Renaming takes effect immediately.</b> You can undo once with <code>[Undo]</code>, but the data is lost when you run another task or close the window.')),
              ('warn', tr('The specified parent folder itself is not modified. Only its contents are renamed.')),
             ]),

            # ── 4: Text Fixer ──────────────────────────────
            ('✦', tr('Text Fixer'),
                  tr('Repair line breaks in OCR and e-book text'),
                  tr('Text extracted from PDFs or EPUBs often has forced line breaks at page width. Text Fixer intelligently restores paragraph structure.'),
             [
              ('note', tr("<b>Input methods</b> — Drag a .txt file onto the drop zone, use <code>[📂 Open File]</code>, or paste text directly into the left 'Original Text' pane.")),
              ('step', tr('<b>Load text</b> — Open a file or paste text into the left pane.')),
              ('step', tr('<b>Choose options</b> — Combine the four options as needed. Start with <b>① + ④</b> for most cases.')),
              ('step', tr('<b><code>[✦ Fix]</code></b> — Compare the left (original) and right (result) panes side by side.')),
              ('step', tr('<b>Save</b> — Click <code>[Save ▼]</code> if satisfied. If not, use <code>[Undo]</code> to restore the original and retry with different options.')),
              ('divider',),
              ('feature', tr('① Merge Line Breaks (blank-line basis)'),
                          tr('Splits text into paragraphs by blank lines, then merges forced line breaks within each paragraph. <b>Not merged</b> — Lines ending with period, exclamation, question mark, or quote; and divider lines like <code>───</code>, <code>===</code>, <code>★★★</code>. This is the core option for fixing PDF/EPUB text. Enable it first in most cases.')),
              ('feature', tr('② Auto Paragraph Split (max N chars)'),
                          tr('After merging, splits overly long lines at sentence boundaries based on a character limit. Short sentences are grouped together within the limit. Default: 100 chars. Try 150-200 for long-sentence manuscripts.')),
              ('feature', tr('③ Insert Blank Line Between Sentences'),
                          tr('Inserts a blank line after lines ending with period/quote, or before dialogue. Useful for improving readability in dialogue-heavy text.')),
              ('feature', tr('④ Reduce Excessive Blank Lines (max N lines)'),
                          tr('Collapses consecutive blank lines to a maximum of N. Default 1 is recommended. Use 2 for multi-section documents.')),
              ('divider',),
              ('tip', tr('<b>Recommended combinations</b> — PDF/EPUB text: <b>① + ④</b> / Dialogue-heavy text: <b>① + ③</b> / OCR output with long paragraphs: <b>① + ② + ④</b>')),
              ('tip', tr('<b>Save options</b> — <b>Save as [Fixed] beside original</b>: keeps original, saves corrected version as <code>[Fixed]filename.txt</code> / <b>Save As</b>: choose location and name / <b>Undo</b>: restores the pre-fix text in the left pane (available once after running Fix)')),
              ('tip', tr('🟡 <b>Yellow lines</b> = lines merged from multiple / 🟠 <b>Orange lines</b> = blank line removed. Highlighting is skipped for files over 3,000 lines.')),
              ('tip', tr('The status bar at the bottom shows <b>merge count, blank lines removed, original line count, and final line count</b>.')),
              ('tip', tr('Press <b>Ctrl+F</b> to search within the source and result text. Enter jumps to the next match, Shift+Enter to the previous.')),
              ('warn', tr('Files are always saved as <b>UTF-8</b>. Convert the encoding separately if you need to preserve the original (e.g. EUC-KR).')),
              ('divider',),
              ('note', tr("<b>Partially corrupted files</b> — Files with damaged bytes can still be opened. Corrupted characters are shown as <code>�</code> (U+FFFD), and the status bar shows a <b>⚠</b> icon with a 'Partial encoding failure' warning.")),
              ('tip', tr('Text Fixer is optimized for <b>detailed inspection of a single file</b>. Open corrupted files to see exactly where the damage is, edit those spots manually, or decide whether to re-acquire the original.')),
              ('warn', tr('Files with tens of thousands of corrupted characters rarely recover well. Re-downloading from the source is usually better. Bulk Fixer automatically skips such files to protect the originals.')),
             ]),

            # ── 5: Bulk Fixer ──────────────────────────────
            ('✦', tr('Bulk Fixer'),
                  tr('Batch-correct line breaks across multiple TXT files'),
                  tr('Applies the Text Fixer correction engine to many files at once. Ideal for cleaning up batches of TXT files extracted from OCR or e-books.'),
             [
              ('step', tr('<b>Add files</b> — Use <code>[📄 Add files]</code> or <code>[📂 Add folder]</code> to load TXT files. You can also drag and drop folders directly onto the file list to recursively collect <code>.txt</code> files.')),
              ('step', tr('<b>Set options</b> — Choose the merge mode (Auto / Korean / English) and correction options in the right panel. Use the <b>Preset</b> dropdown to quickly apply "General document" or "Book / Novel" settings.')),
              ('step', tr('<b>Save settings</b> — Specify an output folder, or leave it empty to save as <code>[Fixed]filename.txt</code> beside each original file. Enable <b>Preserve folder structure</b> to recreate the original subfolder hierarchy inside the output folder.')),
              ('step', tr('<b>Click <code>[▶ Start batch fix]</code></b> — Progress is shown during processing; a summary of successes and failures is displayed on completion.')),
              ('tip', tr('Click any file in the list to preview the corrected result in the preview panel on the right.')),
              ('tip', tr('The default output folder is <code>Output/</code>. You can change it globally in ⚙ Settings or per-tab individually. The folder opens automatically after saving.')),
              ('warn', tr('Only TXT files are supported. Convert DOCX, PDF, etc. to TXT with Text Converter first.')),
              ('divider',),
              ('note', tr('<b>Automatic corruption tiering</b> — Bulk Fixer classifies partially corrupted files into three tiers based on damage severity:<br>• <b>Tier 1</b> (1–500 damaged chars): Fixed + report generated<br>• <b>Tier 2</b> (501–5,000 damaged chars): Fixed + report generated (review recommended)<br>• <b>Tier 3</b> (5,001+ damaged chars): <b>Automatically skipped (original preserved)</b> + report only')),
              ('tip', tr('Reports are created next to the fixed output as <code>{original_filename}.encoding_report.txt</code>, detailing damaged line/column positions for up to 5,000 entries.')),
              ('warn', tr('Files skipped as Tier 3 should be <b>individually reviewed in Text Fixer</b>. Heavy corruption usually means wrong encoding detection or a corrupted source, so re-acquiring the original is often better than forcing correction.')),
             ]),

            # ── 6: Shortcuts & Tips ────────────────────────
            ('⌨️', tr('Shortcuts & Tips'), '',
                   tr('Use keyboard shortcuts to navigate quickly. All shortcuts can be customized in Settings.'),
             [
              ('shortcut', 'Ctrl+1', tr('Go to Text Merger')),
              ('shortcut', 'Ctrl+2', tr('Go to Text Converter')),
              ('shortcut', 'Ctrl+3', tr('Go to Tag Editor')),
              ('shortcut', 'Ctrl+4', tr('Go to Batch Renamer')),
              ('shortcut', 'Ctrl+5', tr('Go to Text Fixer')),
              ('shortcut', 'Ctrl+6', tr('Go to Bulk Fixer')),
              ('shortcut', 'Ctrl+F', tr('Search text in Text Fixer')),
              ('shortcut', tr('⚙ button (top right)'), tr('Open Settings — change theme, language, and shortcuts')),
              ('tip', tr('Settings (theme, language, shortcuts) are saved automatically on exit and restored on next launch.')),
              ('tip', tr('<b>Drag and drop</b> is supported in all tabs. Dropping a folder adds all supported files inside it at once.')),
              ('tip', tr('🔋 <b>Sleep Prevention</b> — While Text Merger, Text Converter, Text Fixer, or Bulk Fixer is running, Windows sleep mode is automatically blocked. It is released immediately when the task completes or an error occurs. Screen lock is unaffected.')),
             ]),

            # ── 7: File creation notice ────────────────────
            ('📁', tr('File creation notice'),
                   tr('Files and folders created automatically during use'),
                   tr('File Nexus Suite automatically creates the following items in the program folder for settings storage, default output, and error logging.'),
             [
              ('step', tr('<b>FileNexusSuite.json</b> — Stores your theme, language, shortcuts, and tab settings. Saved on exit, restored on next launch.')),
              ('step', tr('<b>Output/</b> — Default output folder for Text Converter, Bulk Fixer, and Text Fixer. Created automatically on first launch. Change the location globally in ⚙ Settings; the folder opens automatically after saving.')),
              ('step', tr('<b>logs/crash_*.log</b> — Crash logs generated when an unexpected error occurs. Only the 3 most recent logs are kept; older ones are deleted automatically.')),
              ('warn', tr('<b>_internal/</b> — Created automatically in folder-style exe builds. Contains the Python runtime. <b>Deleting it will prevent the program from running.</b>')),
              ('tip', tr('You can safely delete any of these files or folders. Required items will be recreated automatically on the next launch.')),
             ]),
        ]

    # ── HTML render helper (single section) ──────────────────────
    def _render_section(self, entry) -> str:
        """Render a single section to HTML. Used by _build() to populate
        each per-section page in the QStackedWidget. The rendering style
        matches the previous HelpDialog._build inline style (which served
        as the canonical form across v1.0.x and v1.1.0).
        """
        from FileNexusSuite import SURFACE, BG, SRF2, BORDER, TEXT, MUTED, ACCENT

        def _mix(h1, h2, r=0.12):
            c1 = QColor(h1); c2 = QColor(h2)
            return f"#{int(c1.red()*(1-r)+c2.red()*r):02X}{int(c1.green()*(1-r)+c2.green()*r):02X}{int(c1.blue()*(1-r)+c2.blue()*r):02X}"

        tip_bg  = _mix(SURFACE, ACCENT, 0.07);   tip_bdr  = _mix(ACCENT, SURFACE, 0.4)
        warn_bg = _mix(SURFACE, "#D04030", 0.08); warn_bdr = "#D05040"
        note_bg = _mix(SURFACE, "#5080D0", 0.07); note_bdr = _mix("#5080D0", SURFACE, 0.4)
        feat_bg = _mix(SURFACE, ACCENT, 0.05);   feat_bdr = _mix(ACCENT, SURFACE, 0.5)

        _CIRCLED = ['①','②','③','④','⑤','⑥','⑦','⑧','⑨','⑩',
                    '⑪','⑫','⑬','⑭','⑮','⑯','⑰','⑱','⑲','⑳']

        body_style = (
            f"background:{BG};color:{TEXT};"
            f"font-family:'Pretendard','Segoe UI Variable','Segoe UI','Malgun Gothic',sans-serif;"
            f"font-size:13px;margin:0;padding:0;"
        )

        icon, title, subtitle, desc, items = entry
        is_sc = any(i[0] == 'shortcut' for i in items)
        step_n = 0

        p = [f'<html><body style="{body_style}">']
        p.append(f'<div style="background:{SURFACE};border:1px solid {BORDER};border-radius:12px;overflow:hidden;">')
        p.append(
            f'<div style="padding:13px 18px 11px;border-bottom:1px solid {BORDER};">'
            f'<span style="font-size:18px;margin-right:10px;">{icon}</span>'
            f'<span style="font-size:14px;font-weight:700;color:{TEXT};">{title}'
        )
        if subtitle:
            p.append(f'<span style="font-size:12px;font-weight:400;color:{MUTED};margin-left:8px;">{subtitle}</span>')
        p.append('</span>')
        if desc:
            p.append(f'<div style="font-size:13px;color:{MUTED};margin-top:7px;line-height:1.65;">{desc}</div>')
        p.append('</div><div style="padding:16px 12px 14px;">')

        if is_sc:
            # Shortcut section — keys + descriptions only
            for item in items:
                if item[0] == 'shortcut':
                    _, k, d = item
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
                elif item[0] == 'tip':
                    tt = item[1]
                    has_icon = tt[:2].strip() and ord(tt[0]) > 127
                    ic = '' if has_icon else f'<span style="color:{ACCENT};font-weight:700;margin-right:5px;">💡</span>'
                    p.append(
                        f'<div style="border-left:3px solid {tip_bdr};background:{tip_bg};'
                        f'border-radius:0 7px 7px 0;padding:9px 14px;margin:10px 0 0;'
                        f'font-size:13px;color:{TEXT};line-height:1.7;">{ic}{tt}</div>'
                    )
        else:
            # Regular section — mixed item kinds
            for item in items:
                kind = item[0]
                if kind == 'step':
                    step_n += 1
                    num = _CIRCLED[step_n-1] if step_n <= 20 else f'{step_n}.'
                    content = item[1]
                    if ' — ' in content:
                        cut = content.index(' — ')
                        title_part = content[:cut]
                        desc_part = content[cut+3:]
                        inner = (
                            f'<div style="font-size:13px;font-weight:700;color:{TEXT};">{title_part}</div>'
                            f'<div style="font-size:13px;color:{TEXT};line-height:1.7;margin-top:3px;">{desc_part}</div>'
                        )
                    else:
                        inner = f'<div style="font-size:13px;color:{TEXT};line-height:1.75;">{content}</div>'
                    p.append(
                        f'<div style="margin:0 0 10px 6px;">'
                        f'<table style="border-spacing:0;border-collapse:collapse;">'
                        f'<tr>'
                        f'<td style="color:{ACCENT};font-weight:700;font-size:13px;'
                        f'vertical-align:top;padding-right:7px;white-space:nowrap;">{num}</td>'
                        f'<td>{inner}</td>'
                        f'</tr></table></div>'
                    )
                elif kind == 'divider':
                    p.append(f'<hr style="border:none;border-top:1px solid {BORDER};margin:5px 0 8px 0;">')
                elif kind == 'info':
                    p.append(
                        f'<div style="border-left:3px solid {BORDER};background:{SRF2};'
                        f'border-radius:0 7px 7px 0;padding:8px 12px;margin:4px 0 7px 6px;'
                        f'font-size:13px;color:{MUTED};line-height:1.7;">'
                        f'<span style="font-weight:700;margin-right:5px;">ℹ</span>{item[1]}</div>'
                    )
                elif kind == 'formats':
                    fmts = item[1]
                    pills = []
                    for label, ftype in fmts:
                        if ftype == 'native':
                            pb = _mix(ACCENT, SURFACE, 0.78); pf = ACCENT; pd = _mix(ACCENT, SURFACE, 0.55)
                        else:
                            pb = _mix('#808080', SURFACE, 0.88); pf = MUTED; pd = _mix('#808080', SURFACE, 0.65)
                        pills.append(
                            f'<span style="display:inline-block;background:{pb};border:1px solid {pd};'
                            f'border-radius:4px;padding:2px 9px;font-size:12px;font-weight:700;'
                            f'font-family:monospace;color:{pf};">{label}</span>'
                        )
                    legend = self.tr('Native support')
                    legend_lib = self.tr('Library required')
                    p.append(
                        f'<div style="margin:0 0 10px 6px;">'
                        f'<div style="font-size:12px;color:{MUTED};margin-bottom:9px;">'
                        f'<span style="color:{ACCENT};font-size:10px;">●</span> {legend} &nbsp;&nbsp;'
                        f'<span style="color:{MUTED};font-size:10px;">●</span> {legend_lib} '
                        f'<span style="font-size:11px;">(python-docx · pdfplumber · openpyxl · python-hwpx)</span>'
                        f'</div>{" ".join(pills)}</div>'
                    )
                elif kind == 'sub':
                    p.append(f'<div style="margin:-3px 0 8px 26px;color:{MUTED};font-size:13px;line-height:1.7;">{item[1]}</div>')
                elif kind == 'note':
                    p.append(
                        f'<div style="border-left:3px solid {note_bdr};background:{note_bg};'
                        f'border-radius:0 7px 7px 0;padding:8px 12px;margin:0 0 8px 6px;'
                        f'font-size:13px;color:{TEXT};line-height:1.7;">'
                        f'<span style="color:#5080D0;font-weight:700;margin-right:5px;">ℹ️</span>{item[1]}</div>'
                    )
                elif kind == 'tip':
                    p.append(
                        f'<div style="border-left:3px solid {tip_bdr};background:{tip_bg};'
                        f'border-radius:0 7px 7px 0;padding:8px 12px;margin:3px 0 7px 6px;'
                        f'font-size:13px;color:{TEXT};line-height:1.7;">'
                        f'<span style="color:{ACCENT};font-weight:700;margin-right:5px;">💡</span>{item[1]}</div>'
                    )
                elif kind == 'warn':
                    p.append(
                        f'<div style="border-left:3px solid {warn_bdr};background:{warn_bg};'
                        f'border-radius:0 7px 7px 0;padding:8px 12px;margin:3px 0 7px 6px;'
                        f'font-size:13px;color:#9B2A10;line-height:1.7;">'
                        f'<span style="font-weight:700;margin-right:5px;">⚠️</span>{item[1]}</div>'
                    )
                elif kind == 'feature':
                    _, ft, fd = item
                    p.append(
                        f'<div style="background:{feat_bg};border:1px solid {feat_bdr};'
                        f'border-radius:8px;padding:10px 12px;margin:3px 0 8px 6px;">'
                        f'<div style="font-size:13px;font-weight:700;color:{ACCENT};margin-bottom:4px;">{ft}</div>'
                        f'<div style="font-size:13px;color:{TEXT};line-height:1.7;">{fd}</div></div>'
                    )
                elif kind == 'example':
                    _, before, after = item
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
        return ''.join(p)

    # ── UI builder ───────────────────────────────────────────────
    def _build(self):
        from FileNexusSuite import (
            SURFACE, BG, SRF2, BORDER, TEXT, MUTED, ACCENT, APP_VERSION,
            _svg_icon, _accent_alpha,
        )

        def _mix(h1, h2, r=0.12):
            c1 = QColor(h1); c2 = QColor(h2)
            return f"#{int(c1.red()*(1-r)+c2.red()*r):02X}{int(c1.green()*(1-r)+c2.green()*r):02X}{int(c1.blue()*(1-r)+c2.blue()*r):02X}"

        intro = self._get_intro()
        sections = self._get_sections()

        root = QHBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)

        # ── Sidebar ──────────────────────────────────
        sb = QFrame(); sb.setFixedWidth(168)
        sb.setStyleSheet(f"QFrame{{background:{SRF2};border-right:1px solid {BORDER};}}")
        sl = QVBoxLayout(sb); sl.setContentsMargins(10, 20, 10, 16); sl.setSpacing(4)

        sb_title = QLabel(self.tr('💡  Help'))
        sb_title.setStyleSheet(f"font-size:13px;font-weight:700;color:{TEXT};padding-left:6px;padding-bottom:10px;")
        sl.addWidget(sb_title)
        div = QFrame(); div.setFrameShape(QFrame.HLine); div.setFixedHeight(1)
        div.setStyleSheet(f"background:{BORDER};border:none;margin-bottom:6px;")
        sl.addWidget(div)

        # ── Content area ─────────────────────────────
        right = QFrame(); right.setStyleSheet(f"QFrame{{background:{SURFACE};}}")
        rl = QVBoxLayout(right); rl.setContentsMargins(20, 20, 20, 16); rl.setSpacing(0)

        stack = QStackedWidget(); stack.setStyleSheet("background:transparent;")

        browser_style = (
            f"QTextBrowser{{background:{SRF2};border:1px solid {BORDER};"
            f"border-radius:10px;padding:6px;color:{TEXT};font-size:13px;}}"
            f"QScrollBar:vertical{{background:{BG};width:8px;border-radius:4px;}}"
            f"QScrollBar::handle:vertical{{background:{BORDER};border-radius:4px;min-height:24px;}}"
            f"QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0px;}}"
        )

        body_style = (
            f"background:{BG};color:{TEXT};"
            f"font-family:'Pretendard','Segoe UI Variable','Segoe UI','Malgun Gothic',sans-serif;"
            f"font-size:13px;margin:0;padding:0;"
        )

        # ── Intro page ───────────────────────────────
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

        # ── Per-section pages ────────────────────────
        for entry in sections:
            b = QTextBrowser(); b.setStyleSheet(browser_style)
            b.setHtml(self._render_section(entry))
            stack.addWidget(b)

        rl.addWidget(stack, stretch=1)

        # ── Close button ─────────────────────────────
        btn_row = QHBoxLayout(); btn_row.addStretch()
        btn_close = QPushButton(self.tr('Close')); btn_close.setFixedWidth(80)
        btn_close.setStyleSheet(
            f"QPushButton{{background:{SURFACE};border:1.5px solid {BORDER};color:{TEXT};"
            f"border-radius:8px;padding:8px 0;font-size:13px;}}"
            f"QPushButton:hover{{background:{SRF2};}}"
        )
        btn_close.clicked.connect(self.close)
        btn_row.addWidget(btn_close)
        rl.addSpacing(10); rl.addLayout(btn_row)

        # ── Sidebar nav buttons ──────────────────────
        def _nav(label, idx, icon_key=None):
            btn = QPushButton(label); btn.setFixedHeight(36)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            if icon_key:
                btn.setIcon(_svg_icon(icon_key, MUTED)); btn.setIconSize(QSize(16, 16))
            btn.clicked.connect(lambda _, i=idx: self._switch(i))
            self._nav_btns.append(btn); sl.addWidget(btn)

        _nav(self.tr('About'), 0, 'info_line')
        for i, entry in enumerate(sections):
            icon_key = self._SECTION_ICONS[i] if i < len(self._SECTION_ICONS) else 'document_line'
            _nav(entry[1], i + 1, icon_key)

        sl.addStretch()
        root.addWidget(sb); root.addWidget(right)
        self._stack = stack
        self._switch(0)

    def _switch(self, idx):
        from FileNexusSuite import SRF2, MUTED, ACCENT, _svg_icon, _accent_alpha
        self._stack.setCurrentIndex(idx)
        # Nav button 0 is About; buttons 1..8 are sections 0..7
        _icon_keys = ['info_line'] + list(self._SECTION_ICONS)
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
                btn.setIconSize(QSize(16, 16))

    def refresh(self):
        pass  # Recreated each time it opens (exec() is modal)


# ════════════════════════════════════════════════
# LicenseDialog — open-source license window
# ════════════════════════════════════════════════
class LicenseDialog(QDialog):
    """Standalone license window — open-source notices for runtime, GUI
    framework, libraries, and the application itself.

    The build_html() staticmethod returns the license HTML and is reused
    by SettingsDialog's License tab (FileNexusSuite.py) and by the
    UI preview tool (preview_ui.py). The license summary banner is
    hard-coded in English because MIT License is an English standard
    legal text and translating the one-line summary adds no value.
    The per-entry notes already contain bilingual (Korean/English)
    license summaries where appropriate.
    """

    @staticmethod
    def build_html() -> str:
        """Build the open-source license HTML.

        Returns the full <html><body>...</body></html> page for use in a
        QTextBrowser. All theme colors are resolved at call time so the
        result picks up the current theme.
        """
        from FileNexusSuite import SURFACE, SRF2, BORDER, TEXT, MUTED, ACCENT
        bg     = SURFACE
        text   = TEXT
        muted  = MUTED
        accent = ACCENT
        border = BORDER
        srf2   = SRF2

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
                        "copyright": "Copyright © Jeremy Singer-Vine and pdfplumber contributors",
                        "url": "https://github.com/jsvine/pdfplumber",
                        "note": "PDF text extraction for Text Merger. Optional — loaded at runtime only if installed.",
                    },
                    {
                        "name": "openpyxl",
                        "version": "—",
                        "license": "MIT License",
                        "copyright": "Copyright © 2010 openpyxl",
                        "url": "https://foss.heptapod.net/openpyxl/openpyxl",
                        "note": "XLSX file reading for Text Merger. Optional — loaded at runtime only if installed.",
                    },
                    {
                        "name": "python-hwpx",
                        "version": "—",
                        "license": "MIT License",
                        "copyright": "Copyright © python-hwpx contributors",
                        "url": "https://github.com/mete0r/pyhwp",
                        "note": "HWPX file reading for Text Merger. Optional — loaded at runtime only if installed.",
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

        parts = [
            f'<html><body style="background:{bg};color:{text};'
            f"font-family:'Pretendard','Segoe UI Variable','Segoe UI','Malgun Gothic','Yu Gothic UI','Microsoft YaHei UI',sans-serif;"
            f'font-size:13px;margin:16px 20px 24px;">'
        ]

        # Summary banner — English hard-coded (MIT License is English standard text)
        summary = 'Licensed under the MIT License · Free to use, modify, distribute, and sell · Copyright notice must be retained.'
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

    def __init__(self, parent=None):
        from FileNexusSuite import SURFACE, SRF2, BORDER, TEXT, BG, _make_app_icon, _btn_style
        super().__init__(parent)
        self.setWindowTitle(self.tr('License'))
        try:
            self.setWindowIcon(_make_app_icon())
        except Exception:
            pass
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setStyleSheet(f"QDialog{{background:{BG};}}")
        self.resize(560, 480)

        lay = QVBoxLayout(self); lay.setContentsMargins(16, 16, 16, 12); lay.setSpacing(10)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setStyleSheet(
            f"QTextBrowser{{background:{SURFACE};border:1px solid {BORDER};"
            f"border-radius:10px;padding:4px;color:{TEXT};font-size:13px;}}"
            f"QScrollBar:vertical{{background:{BG};width:8px;border-radius:4px;}}"
            f"QScrollBar::handle:vertical{{background:{BORDER};border-radius:4px;min-height:24px;}}"
            f"QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0px;}}"
        )
        browser.setHtml(LicenseDialog.build_html())
        lay.addWidget(browser, stretch=1)

        btn_row = QHBoxLayout(); btn_row.addStretch()
        btn_close = QPushButton(self.tr('Close')); btn_close.setFixedWidth(80)
        btn_close.setStyleSheet(_btn_style(True))
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        lay.addLayout(btn_row)
