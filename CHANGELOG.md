# Changelog

**English** | [한국어](./CHANGELOG_KO.md)

This document records the major changes for this project, version by version.

For user-facing release notes, refer to the [GitHub Releases](https://github.com/MerciHanrim/FileNexusSuite/releases) page.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

**v1.0.x ~ v1.1.0 history:** [`docs/changelog/CHANGELOG_archive.md`](docs/changelog/CHANGELOG_archive.md)

---

## [1.1.3] — 2026-08-20

Started from a user report that EPUB→TXT conversion output was more than twice the size of the source EPUB. Investigation split into two threads — one a real defect: malformed, spec-violating EPUBs with non-HTML resources referenced directly in the spine had that binary data force-decoded as text. The other turned out, after investigation, not to be a bug at all: a format-inherent characteristic (EPUB is stored as a compressed zip, TXT is uncompressed — a well-formed EPUB is expected to look larger once converted). Only the former needed fixing; the TXT→EPUB zip compression level was also bumped to maximum along the way.

### Fixed
- **`epub_to_text()` — guard against binary mis-decoding from unvalidated spine media-type** — Manifest `<item>` parsing now also captures the `media-type` attribute, and spine traversal skips any item whose media-type isn't `application/xhtml+xml` / `text/html` / `text/x-oeb1-document` (i.e., non-HTML resources such as images incorrectly referenced directly in a malformed EPUB's spine). Items without a media-type attribute fall back to extension matching (`.html`/`.xhtml`). Previously such items had their binary content force-decoded via `decode("utf-8","replace")`, turning invalid bytes into U+FFFD replacement characters (3 bytes in UTF-8) and needlessly inflating the output text size.

### Changed
- **`txt_to_epub()` — explicit zip compression level** — `zipfile.ZipFile` now passes `compresslevel=9` instead of relying on zlib's default (~level 6), for maximum compression. Measured savings are marginal (~0.75%) but the change is cost-free.

---

## [1.1.2] — 2026-05-14

Text Merger gains an MD output format option. The previously fixed `.txt` output now offers a `.txt` / `.md` radio button selection; when MD is selected, file separators automatically switch to `## filename` header + `---` Markdown form. Internally, the app icon base64 data (`_APP_ICON_B64`, 1,090 lines) is extracted to `fns_icon.py`, reducing the main module's line count.

### Added
- **Text Merger — MD output format** — A `Output Format: TXT / MD` radio button group is added to the save settings area. When MD is selected, the default filename becomes `merged.md`, the save filter switches to `Markdown Files (*.md)`, and the file separator format changes to `## filename\n\ncontent\n\n---`. Disabling the separator checkbox preserves the existing no-separator merge behavior regardless of format. The output format selection is saved and restored with other settings. Translations for `Output Format:` added for all 5 languages.

### Internal
- **`fns_icon.py` extracted** — App icon base64 data (`_APP_ICON_B64`, 1,090 lines) extracted from the main module into `fns_icon.py`. Pure data file with no PySide6 dependency. Main module references it via `from fns_icon import _APP_ICON_B64`. No user-visible change.

---

## [1.1.1] — 2026-05-13

v1.1.1 follows v1.1.0's *modularization and design polishing* by bringing the help module into the Qt Linguist runtime fold and cleaning up the i18n defects still lingering in the main module. The release bundles two threads (help module's five-language Python branch removal with instance-method reorganization, and main module's six Korean-hardcode sites wrapped in `self.tr()`/`QT_TR_NOOP`/`QCoreApplication.translate`). The release is a pair programming collaborative work of Hanrim (@MerciHanrim) and Claude Opus 4.7, retaining the operational pattern accumulated since v1.0.5 — the help module migration started from Hanrim's direction of *bringing the help system into the same Qt Linguist workflow as the main UI* and landed as instance-method reorganization, while the main-module i18n cleanup followed a natural rhythm starting from a single help-button tooltip discovery and expanding into an AST-based audit of the entire main module.

### Changed
- **Help module Qt Linguist migration finalized (v1.1.1 localization track — help module joining)** — `fns_help.py`'s `_build_help_html()` reorganized from five-language Python branches (~1,100 lines) into three instance methods of `HelpDialog` (`_get_intro()`, `_get_sections()`, `_render_section()`). All user-visible help content unified under English base + `self.tr()` wrap, resolved at runtime via `QTranslator` against `help_*.qm`. `_section_icons` mapping switched from translated-title lookup to index-based lookup (`_SECTION_ICONS` class constant, 8 entries — stable across language switches). `_render_section()` absorbed as `HelpDialog._render_section(entry)` instance method, consolidating two previously duplicated render paths in `_build_help_html()`'s internal helper and `HelpDialog._build`'s inline render logic into a single render path. The legacy `_data_only=False` full-page render path (~180 lines) was removed along with the `_get_help_data()` module helper — neither was called by main or `preview_ui`. `fns_help.py` shrinks from ~1,486 → 829 lines (-657 lines, -44%). The Qt Linguist workflow established for main UI strings in v1.1.0 now extends consistently to help content.
- **`LicenseDialog` class introduced with reusable `build_html()` staticmethod** — `_build_license_html()` module function migrated to `LicenseDialog.build_html()` staticmethod, consolidating license HTML build responsibility into a single class. The same staticmethod is reused by `SettingsDialog`'s License tab (via `SettingsDialog._page_license()`) and by the standalone dialog (via `preview_ui.py._show_license()`). The license page's summary banner — "Licensed under the MIT License · Free to use, modify, distribute, and sell · Copyright notice must be retained." — switched from `QCoreApplication.translate()` to hard-coded English, since the MIT License is an English-standard legal text and English representation is the de facto standard for the license page. `preview_ui.py._show_license()` shortened from 18-line inline dialog build to a single `LicenseDialog(self).exec()` call.
- **Main module i18n defects cleaned up (v1.1.1 i18n hygiene track)** — Six remaining Korean-hardcode sites in the main module — leftovers from v1.0.x single-language code — cleaned up. AST-based audit (`audit_hardcoded_korean.py`, see Added below) classified defects by handling pattern, applying the appropriate wrap form to each. **Pattern A (within methods, `self.tr()` applied directly)** — `AppSuite`'s help button setToolTip and startup log message wrapped in `self.tr()`, displaying correctly in the configured UI language. **Pattern B (module-level functions, `QCoreApplication.translate` used)** — `epub_to_text()`'s EPUB metadata `'저자: '` output wrapped in `QCoreApplication.translate('EpubConverter', 'Author: ')`, the standard pattern for module-level functions without `self`. **Pattern C (class variables, marked with `QT_TR_NOOP` only)** — `SettingsDialog._SECTIONS`'s four sidebar labels (`'테마'`, `'언어 설정'`, `'단축키'`, `'라이선스'`) marked with `QT_TR_NOOP('Theme')`/`QT_TR_NOOP('Language')`/`QT_TR_NOOP('Shortcuts')`/`QT_TR_NOOP('License')`, with actual translation occurring at `self.tr(label)` call sites in `__init__`/`_build`. `audit_hardcoded_korean.py` retains its AST-based form, which re-detects three false-positive patterns (`LANG_NATIVE_FALLBACK`'s native locale names, `_combo_lang`'s EPUB metadata, CSS font-family Korean font identifiers); the false-positive list in the report serves as a guide for re-runs.
- **Code hygiene cleanup** — Removed 45 lines of dead module code; `svg_html_img` call reduced to no-op stub. No user-visible change; anchor retained for future work.

### Fixed
- **Text Converter Book Info panel layout breakage when Debug Log toggled** — In the Text Converter tab's right-hand Book Info panel, the labels of the four input fields (Title / Author / Language / Chapter Split) were hidden under the input boxes. When the Debug Log panel was expanded, the main window's vertical space shrank, widgets failed to receive sufficient height, and spacing collapsed. Fixed by wrapping the Book Info panel in `ScrollHintArea` to preserve input height and spacing under reduced vertical space, with the other two right-sidebar panels also preemptively wrapped in `ScrollHintArea` to block the same defect pattern from recurring. Issue had been present since v1.1.0.
- **Dead `_t` import in `preview_ui.py`** — At L24 of `preview_ui.py`, an import of the `_t` symbol from `FileNexusSuite` was causing an ImportError. The main module had already removed the `_t` symbol, but `preview_ui.py`'s import list missed the update. `_t` was never actually called inside `preview_ui.py` — a dead reference. Fixed by removing `_t,` from the import list. `preview_ui.py` line count ~753 → 738 (-15 lines, including the `_show_license()` shortening).

### Added
- **`audit_hardcoded_korean.py` audit tool** — New tool that performs an AST-based audit of Korean string literals lacking `self.tr()`/`QT_TR_NOOP`/`QCoreApplication.translate` wrap in `FileNexusSuite.py`. Excludes docstrings and detects translation-call arguments. Used during this release to classify six real defects and three false positives. Reusable for catching new i18n defects after future main-module changes. Relative-path fix applied during tool stabilization.

### Tests
- **513 → 512 passing on Hanrim's environment (-1 change)**, 0 failures / 0 errors / 5 intentional skips. Net change reflects `TestBuildHelpHtml` rewrite (below).
- **`TestBuildHelpHtml` rewritten — Qt Linguist runtime form** — The previous 9 test methods depended on the `_build_help_html(_data_only=False, _lang=...)` signature; with the `_lang` parameter removed, the test class was rewritten wholesale. The new form uses `QTranslator` install/remove cycles to verify per-language help rendering.
- **i18n defect cleanup verification tests added** — AST-based verification that all six main-module Korean hardcodes are properly wrapped (integrating `audit_hardcoded_korean.py`); verification that `LicenseDialog.build_html()` is callable as a staticmethod without instance creation.

---

> For the change history of earlier versions, see [`docs/changelog/CHANGELOG_archive.md`](docs/changelog/CHANGELOG_archive.md).
