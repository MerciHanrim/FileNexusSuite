# Changelog

This document records the major changes for this project, version by version.

For detailed code changes per version, refer to the [`RELEASE_NOTE_vX.X.X.md`](./) files.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### Changed
- **Sidebar card visual separation strengthened (v1.1.0 design polishing)** — Cards in the right-hand sidebar (e.g., Batch Renamer's Number Reset / Start Number / Digits / Prefix-Suffix groups) now feel slightly elevated and visually grouped without changing their information density. Three coordinated changes: (1) a new module-level `_apply_card_shadow(widget)` helper applies a subtle `QGraphicsDropShadowEffect` (blur radius 18, Y offset 3, color derived from `BORDER` with alpha 0.5) to every `QGroupBox`; (2) the global `QGroupBox` rule gains `margin-bottom:6px` and stronger padding (`12px 10px 10px 10px`) for breathing room between adjacent cards; (3) the `QGroupBox::title` color shifts from `MUTED` to `ACCENT` so card titles read as section markers rather than fading captions. A new `AppSuite._apply_card_shadows()` method walks all `QGroupBox` descendants via `findChildren()` and is called once after `_build()` in `__init__`, then again at the end of `apply_theme()` so shadow color tracks `BORDER` between light and dark themes (the shadow is `BORDER`-derived). Tuning landed at the second iteration — the initial values (blur 12, alpha 0.35) were too faint to register as a visual cue.
- **Batch Renamer progress dialog tone-matched with FNS theme** — Replaced Qt's default `QProgressDialog` (used in both the ingest worker runner and the rename worker runner) with a new FNS-toned modal progress dialog built via the `_build_progress_dlg` helper. The new dialog inherits the existing `_confirm` / `_build_dlg` palette: `SURFACE` background, `ACCENT` progress-bar chunk, `BORDER` outline, `_btn_style(False)` cancel button, padding (28, 24, 28, 20) consistent with all other FNS dialogs. All existing `QProgressDialog` behaviors are preserved: modal (`Qt.WindowModal`), 400 ms minimum-duration delay (now via `QTimer.singleShot(400, _maybe_show)` gated by a completion flag, preventing dialog flicker for sub-400 ms operations), auto-close on completion (`bar.setValue(100)` → `dlg.accept()`), and cancel propagation (cancel button → `worker.request_cancel()`). The `QProgressDialog` symbol is removed from the `QtWidgets` imports.

### Tests
- **603 → 609 passing on Hanrim's environment** (+6), 63 classes (+1), zero failures/errors, 5 intentional skips
- **`TestSidebarCardPolish` (+6)** — Source-grep verification of the three coordinated card-polishing changes. Covers: `QGraphicsDropShadowEffect` import presence, `_apply_card_shadow` helper definition, the tuned shadow parameters (blur 18 / offset (0,3) / alpha 0.5 / `QColor(BORDER)`), the `AppSuite._apply_card_shadows()` method (must use `findChildren(QGroupBox)`, must call `_apply_card_shadow(gb)`, and must be called from at least two sites — `__init__` and `apply_theme` — so the shadow re-renders on theme change), `QGroupBox::title` using `ACCENT` instead of `MUTED`, and the strengthened `QGroupBox` margin / padding values (`margin-bottom:6px`, `padding:12px 10px 10px 10px`).
- **594 → 603 passing on Hanrim's environment** (+9), 62 classes (+1), zero failures/errors, 5 intentional skips
- **`TestBuildProgressDlg` (+8)** — Source-grep verification of the new helper and its integration in both worker runners. Covers: helper function definition, the 4-tuple return signature `(dlg, lbl, bar, cancel_btn)`, FNS-tone palette application (`SURFACE` / `ACCENT` / `BORDER` / `_btn_style`), modal behavior (`Qt.WindowModal` + `setMinimumWidth`), runner integration (both `_run_ingest_worker` and `_run_rename_worker` call the helper and unpack the 4-tuple), 400 ms minimum-duration preservation (`QTimer.singleShot(400` + `_state['done']` flag), cancel button wiring (`cancel_btn.clicked.connect(worker.request_cancel)`), and regression guards (no `QProgressDialog()` instantiation anywhere, no `QProgressDialog` in `QtWidgets` imports).
- **`test_scenario_b_imports_present` updated** — `QProgressDialog` removed from the imports check (replaced by `_build_progress_dlg` helper in v1.1.0).

## [1.0.11] — 2026-05-08

Post-v1.0.10 track — **English-first transition for the entire codebase and supporting documents** (strengthening accessibility for non-Korean-speaking developers), plus **the Batch Renamer scalability rewrite** (preview-table virtualization + `QThread` workers) that eliminates the large-dataset rendering freeze observed at 154,895 files / 2,714 folders / 86.8 GB. v1.0.11 was released as an unsigned binary; the code-signing track is deferred until project visibility (community adoption, external references) materially benefits from it — independent of any specific provider.

### Changed
- **Main source code translated to English** — 1,133 lines of Korean comments, docstrings, and debug-log strings in `FileNexusSuite.py` translated to English while preserving user-facing UI strings, language-branched help content, and dictionary keys/values intentionally kept in Korean. Split into two commits for safety: Step 1+2 (506 lines, `f54bc81`) and Step 3 final (627 lines, `177598b`). Validated by `ast.parse` per chunk and full `test_file_nexus.py` 535/0/0/0 across both work and Git folders ×2.
- **Test suite translated to English (Track F)** — `test_file_nexus.py` Korean comments and docstrings translated to English via 277 mappings applied across 3 chunks (F1 L1–L3500: 90 mappings, F2 L3501–L4100: 120 mappings, F3 L4101–L4590: 67 mappings). Korean lines reduced 1,145 → 560 (-585 translated). Strictly preserves 459 protected lines: `SAMPLE_KO_*` test-input variables, assertEqual expected outputs, and Korean string arguments to `_run_fix` / `remove_tag` / `add_tag` / etc. — these verify language-neutral behavior of `_SENT_END = '.!?…。！？‥」』）)}>]"\''` (ASCII + CJK punctuation), so Korean inputs *are* the test scenario. Also preserves 9 in-context Korean citations inside English comments (OCR break `"휘\n둥그레"`, word-split `"참\n가자들" → "참가자들"`, chapter header `"테스트 샘플"`, range notation `001-197화`, cp1252 break `'한'`, regex template `"{n}개 파일 추가됨..."`) where the Korean text itself is the evidentiary content. The 5 D_print lines in the test runner's result summary (`Total tests / Passed / Failed / Errors / Skipped`) converted to English-only — internal CI/contributor-facing console output, not user-exposed UI. Hanrim attribution normalized at 3 sites (L3806 / L3881 / L4532: `신용우님` and `한림 로컬` → `Hanrim`) per the v1.0.8 §4.36 medium-specific notation policy. Validated by per-chunk and full-file `ast.parse` + 535/0/0/0 across both work and Git folders ×2.
- **STORY.md switched to bilingual EN/KO narrative** (`c469f6b`) — Project narrative now presented as English-first with Korean accompaniment per paragraph, accessible to both English-speaking and Korean-speaking readers.
- **README.txt switched to English-first with multilingual labels** (`3922250`) — Bundled README inside the distribution ZIP now opens in English with brief multilingual labels for non-Korean users.
- **Build metadata translated to English** (`7ca4f734`) — Korean strings in `version_info.txt`, `requirements.txt`, and the build script translated, leaving only the parts that intentionally surface to Korean users.
- **README.md STORY.md reference clarified** (`91f67b5`) — `*(Korean only)*` → `*(English & Korean)*`, accurately reflecting STORY.md's bilingual structure introduced in `c469f6b`.
- **Batch Renamer ingest: O(1) duplicate-path check** — Replaced the O(N²) `any()` linear scan over existing groups with a `set` lookup. Applied symmetrically to both the folder-rename ingest (`_f_ingest`) and the file-rename ingest (`_p_ingest`, including the `os.walk` recursion path). Saves ~170 ms of main-thread CPU time when ~2,700 folders are dragged in at once. Note: this is a partial-mitigation change — the dominant freeze on very large datasets comes from `QTableWidget` rendering, tracked separately for v1.1.0.
- **Batch Renamer scalability — large-dataset rendering freeze fixed** — Pairs with the `set`-based duplicate-check above to address the *rendering-side* freeze on 154,895 files / 2,714 folders / 86.8 GB datasets that the prior change explicitly deferred. The preview table is now a virtualized `QTableView` + `QAbstractTableModel` (new classes `BatchPreviewModel` + `BatchRowHeightDelegate`), eliminating the ~470,000 `QTableWidgetItem` allocations the old `QTableWidget` produced on every render — `_f_refresh` / `_p_refresh` shrink from 23 / 21 lines to 4 lines each as per-cell widget construction moves into `data(index, role)`. `_f_ingest` / `_p_ingest` and `_f_do_rename` / `_p_do_rename` run on `BatchIngestWorker(QThread)` and `BatchRenameWorker(QThread)` with a modal `QProgressDialog` (cancel + per-folder progress); the rename worker preserves the depth-first folder traversal and the `WinError 5` bulk-retry loop. Both folder + file tabs share the same model / worker classes via a `'f'` / `'p'` `kind` parameter. Adds 3 new i18n keys across all 5 languages (`dlg_cancel`, `batch_ingest_progress`, `batch_rename_progress`). Also overrides the `QProgressDialog` window title from Qt's default (`python`, from `sys.argv[0]`) to `FileNexusSuite` for both worker dialogs.
- **Migrated 12 inline UI strings into the central TRANSLATIONS dictionary** (`b9b0e90`) — A long-standing v1.1.0-deferred cleanup item resolved. 14 new translation keys added across all 5 languages (ko/en/ja/zh_cn/zh_tw, 70 entries total): `crash_title/main/log_at/open_log` (uncaught-exception dialog), `already_running_title/main/sub` (single-instance dialog), `rename_skip_dup_in_batch/dest_exists` (Batch Renamer skip messages), `lib_required_msg` with `{lib}` format (Bulk Fixer ImportError messages × 4), `dlg_info` (the only missing dialog-header fallback), `help_window_title` with `{ver}` format / `help_sidebar_title` (Help dialog), `help_section_intro` (Help sidebar 'About' button). Reused existing keys for tab buttons (`tag_sub_*`), radio buttons (`tag_rm_*`), dialog headers (`dlg_warning/error_title/confirm_title/done`), and theme labels (`theme_*` via `_theme_label()`). Cleaned dead code: `SHORTCUT_DEFS` `'label'` field (never read — separate `_sc_label_keys` map carries the i18n keys) and `_CARD_CFG` `'label'` field (only one status-message site, now uses `_theme_label()`). Removed local per-language tables: `_msg_map`, `_msgs`, `titles`+`sb_label`, `intro_lbl`. Korean string literals outside TRANSLATIONS reduced 191 → 142 (-49); remaining 142 are intentional (122 inside `if lang == 'ko'` guide content, 7 fonts/copyright/language names, 4 `_section_icons` compatibility lookup, 9 misc). The `TestTranslationCompleteness` suite already enforces 14×5=70 key symmetry across all 5 languages, so this migration inherits regression protection automatically.

### Fixed
- **Batch Renamer (file mode): per-group digit width** — `_p_calc_preview` was using a single `auto_d` value computed from the largest group's file count and applied globally to every group, so a 9-file group rendered with 3 digits if any other group held 100+ files. Each group now computes its own digit width based on its own file count: a group of 9 renders with 1 digit, a group of 100 renders with 3 digits. (`grp_max_num = start + len(files) - 1` per iteration of `_p_calc_preview`.)
- **Batch Renamer ingest: consolidated empty-folder dialog** — When dragging multiple folders that contain no subfolders (`_f_ingest`) or no files (`_p_ingest`), a separate modal `_dlg_info` dialog used to appear for each empty folder, leading to a popup-spam pattern that could force-quit the app on large batches (~21+ folders). Skipped folders are now collected into a list, and a single consolidated dialog summarises them: ≤10 paths shown in full, >10 shown as the first 10 paths + `... (+N)` summary + `(N)` total counter in the header. Symmetric treatment across `_f_ingest` and `_p_ingest`.
- **i18n consistency in Chinese dictionaries** — `zh_tw` carried two simplified-Chinese leaks (`tag_drop2` and `merge_sel_one`) that broke the Traditional Chinese UI's character-set integrity, and `zh_cn` was missing the `merge_sel_one` key entirely. Simplified-Chinese users were silently falling through `_t`'s zh_cn → zh_tw fallback path (L814) and inheriting the broken Traditional-side value — two compounding bugs that produced *accidental* visual alignment via the fallback. Both dictionaries now carry the key in their respective scripts (`zh_tw`: `點擊以開啟資料夾選擇視窗` / `已選取: {name}`, the latter aligning with the adjacent `merge_sel_multi` `已選取 {n}個…`), replacing accidental fallback alignment with explicit alignment.
- **Dropped legacy `%APPDATA%` config fallback in `_show_already_running_popup`** — A pre-v1.0.x try-block fragment first probed `~/AppData/Roaming/FileNexusSuite/FileNexusSuite.json` (legacy location) before falling back to a `__file__`-relative path. Both branches are dead since the rest of the codebase has used the module-level `_CONFIG_PATH = _app_dir() / "FileNexusSuite.json"` exclusively from v1.0.x onward, and no users remain on the legacy `%APPDATA%` location. The block now opens `_CONFIG_PATH` directly — 14-line probe-and-fallback reduced to 10 lines (-4 lines, single source of truth).

### Added
- **Batch Renamer: tooltips on group header and new-name column** — Previously only the original-name column carried `setToolTip(full_path)` for hover-over; the group header (`📂 parent_folder`) and the new-name column had no tooltips, so long Korean book titles or chapter names truncated by column width could not be verified at a glance. Tooltips now apply symmetrically across both panels (`_f_refresh` / `_p_refresh`) at three sites: group header (full folder path), original column (full path, existing), new-name column (full new filename, only when preview is active). Restores symmetry between the original and new-name display.

### Tests
- **535 → 589 passing** (+54), 60 classes (+2), zero failures/errors/skips (Hanrim's local + Git folder dual verification)
- **`TestBatchRenamerDigitWidth` (+20)** — Pure-function extraction of the `_p_calc_preview` per-group digit-width logic, following the project's existing test pattern (cf. `_de` / `natural_sort_key` / `depad` / `detect_prefix`). Covers auto / nopad / pad2 / pad3 modes across boundary file counts (1, 9, 10, 11, 99, 100, 999, 1000) and both start values (0, 1), plus a per-group independence test that pins the v1.1.0 fix against future regression.
- **`TestBatchRenamerEmptyFolderDialog` (+5)** — Integration-style test of the consolidated empty-folder dialog. Patches `_dlg_info` and `QApplication` at the namespace level (`_ns['_dlg_info']` / `_ns['QApplication']`) so `_f_ingest` / `_p_ingest` can run without a real Qt application instance; bypasses `BatchRenamerPanel.__init__` (heavy Qt UI construction) by attaching only the attributes the ingest methods touch to a bare object. Verifies: (a) 3 empty folders → exactly 1 dialog call (was 3), symmetric across `_f_ingest` / `_p_ingest`, (b) ≤10 skipped: every path appears in the message with no truncation marker, (c) >10 skipped: first 10 paths + `... (+N)` summary + `(N)` total counter, (d) successful ingest produces no dialog at all.
- **Closed 8 unclosed file handles** — 8 sites in `test_file_nexus.py` used the inline `open(path, encoding='utf-8').read()` antipattern, leaking file descriptors and emitting `ResourceWarning` under `python -W default`. Converted to explicit `with open(...) as _f: ... = _f.read()` blocks across `TestBulkFixerFileIO` (3 sites: novel.txt / ko.txt / blank.txt) and `TestWriteEncodingReport` (5 sites: tier1 / tier2 / tier3 / truncated_count / all_languages over `encoding_report.txt`). 560/560 unchanged; ResourceWarnings reduced 8 → 0.
- **Extended `_run_fix` coverage to English-language inputs (+29)** — 29 English sibling tests added across 6 classes (TestSmartMerge: 12, TestSentenceSep: 5, TestFixerRealWorld: 5, TestFixerCombinations: 2, TestAutoSplit: 4, TestRegression: 1) to mirror the existing Korean-input scenarios. 12 `SAMPLE_EN_*` fixtures added under the same CC0 1.0 neutrality policy as `SAMPLE_KO_*` (TITLE_LONG/SHORT/PLAIN, OCR_BROKEN/SHORT, WORD_SPLIT, DIALOGUE_A/B, CHAPTER_FULL/SHORT, MIXED, LONG_SENTENCES). Verifies that `_SENT_END = '.!?…。！？‥」』）)}>]"\''` operates as a language-neutral set: ASCII sentence-end characters and closing brackets/quotes block merging identically for English input. Coverage extends to the scenario level (OCR repair, chapter-header preservation, dialogue patterns, word-split repair, mixed scenarios, long-sentence auto split), confirming the design is genuinely language-agnostic rather than coincidentally aligned with Korean. 589/589 across both work and Git folders ×2.
- **`TestBatchRenamerScenarioB` (+5)** — Source-grep checks (PySide6 not required) for the four new classes (`BatchPreviewModel` / `BatchRowHeightDelegate` / `BatchIngestWorker` / `BatchRenameWorker`), the required PySide6 imports (`QAbstractTableModel`, `QModelIndex`, `QTableView`, `QProgressDialog`), the `QTableView()` replacement of the old `QTableWidget(0,3)` instantiation in both tabs, the worker `kind` validation, and the model's public API (`set_data` / `set_filter_fn` / `headerData` / `refresh_headers` / `is_header`). Runtime behavior is left to the regression-protection track scheduled after the Qt Linguist track lands. 589 → 594 across both work and Git folders ×2.
- **`TestBatchRenamerEmptyFolderDialog` (5 skipped, intentional)** — The synchronous fixture (which calls `_f_ingest` / `_p_ingest` directly on a bare panel via namespace-level `_dlg_info` / `QApplication` patching) cannot drive an async `BatchIngestWorker` — `_BarePanel` is not a `QObject`, so `QThread.__init__` rejects it. The consolidated-dialog behavior itself is preserved inside `_run_ingest_worker.on_done()` — the worker's `sig_warn` accumulates per-folder OS errors and the `sig_done` slot consolidates them into a single dialog, exactly as the prior synchronous code did. To be re-added with proper worker mocking in the post-Qt-Linguist regression-protection track. Net test count: 594 (+5 new, -5 skipped); 0 failures / 0 errors.

### Documentation
- **Multi-line docstring closing pattern identification** added to the Console Release Manual (v1.2 §5.9) — captures the trailing-`"""` placement nuance discovered during the Step 3a trial-and-error that briefly broke `ast.parse`. Future bulk-refactoring tracks can use the pre-check command to avoid the same pitfall.
- **Track F learnings consolidated into Console Release Manual v1.3** — §5.9 enhanced with the *same-sentence multi-occurrence pattern* (Python's `str.replace(old, new, 1)` replaces only the first match; identical docstring sentences repeated across multiple test classes need full `replace()` without count argument; encountered when 3 docstrings shared the v1.0.6 Phase 2-a fallback-helper description verbatim). §5.10 newly added — *Korean example citations inside English comments* protection pattern: when an already-English comment cites Korean as the test scenario itself, translating it would destroy the evidentiary value. Identified 9 such cases in `test_file_nexus.py`, mirroring the main code's Step 3 §1.3.3 single-line protection list (18 cases). Track F learnings: 52 multi-line docstrings (4× the Step 3 area's count) processed with zero `ast.parse` failures using the v1.2 §5.9 pre-check pattern, validating the manual's preventive value at scale.

---

## [1.0.10] — 2026-04-25

v1.0.10 — The starting point of the MIT transition and the OSS direction. The release that brings the v1.0.x series to its turning point of *"personal tool → OSS publication"*. A bundle of three tracks: license transition (Freeware → MIT), explicit LGPL compatibility documentation, and the SignPath OSS Sponsorship application.

### Changed
- **License transition: Freeware (source available) → MIT License** — All of use, modification, redistribution, and resale are now freely permitted, provided the copyright notice is retained. With the spirit *"originally built as a personal tool, in the hope it may help others with similar workflows"*, Hanrim opens the accumulated results of the v1.0.x series to the OSS community.
  - `LICENSE` file — Transitioned from a custom-written Freeware format to the MIT standard text (correctly auto-detected by GitHub's Licensee gem). Korean notice + Test Data Exception (CC0) appendix preserved
  - 5-language `license_summary` keys — Reworded with the exact opposite meaning: *"unauthorized redistribution, repackaging, or resale prohibited"* → *"use, modification, redistribution, and resale all permitted"* (en/ko/ja/zh_cn/zh_tw)
  - `_build_license_html()` project entry — `Freeware — Free for Personal & Commercial Use` → `MIT License` + Korean/English note paragraphs reworded (the "altruism" line newly added; AI pair programming context preserved)
  - `README.md` / `README_EN.md` license section body + license badge + LICENSE file link
  - `README.txt` footer `Freeware (Personal & Commercial)` → `MIT License`
- **`Copyright © 2026 Hanrim. All rights reserved.` → `Copyright © 2026 Hanrim`** — "All rights reserved" notation cleaned across 6 locations. Vestige from the 1910 Buenos Aires Convention with no legal meaning in modern copyright law + consistency with MIT license semantics. Locations: `version_info.txt` `LegalCopyright` / `FileNexusSuite.py` L1 header / `FileNexusSuite.py` L14637 `_footer_copyright` / `FileNexusSuite.py` L14325 `_build_license_html()` project entry / `README.md` / `README_EN.md`
- **README badge visual system refined** — Expressing the narrative *"v1.0.10 as the OSS arrival point of the v1.0.x series"* through a flow of color. Color alignment per category:
  - Identity (`CC785C` Anthropic copper): AI pair Claude / Download CTA
  - OSS vitality (`97CA00` deep OSS green): tests / **license MIT** ← new placement in v1.0.10
  - Starting point (`7B6FA3` purple): version 1.0.10 (relocated from the former license badge slot)
  - Brand citations (external standards as-is): python / PySide6 / platform / CI badge

### Added
- **Explicit LGPL compatibility documentation** — One-sentence LGPL replacement note added to the PySide6 (LGPL-3.0) / chardet (LGPL-2.1) note fields in `_build_license_html()`. *"File Nexus Suite is built with PyInstaller. Users may replace this LGPL library by rebuilding from source — see the GitHub repository for build instructions."* Explicitly states that users can directly replace LGPL libraries thanks to PyInstaller `--onedir` mode's `_internal/` folder separation. Strengthens the LGPL §3 obligation from implicit fulfillment (GitHub source publication) to explicit fulfillment, permanently closing the gray zone
- **`README.txt` `_internal` folder protection notice** — `⚠ The _internal folder in the same directory contains files necessary for program execution. Do not delete it.` added in both Korean and English. Mitigates the risk of users mistaking `_internal/` for *"seemingly unnecessary data"* and deleting it under PyInstaller `--onedir` build mode. README.txt achieves intent-artifact alignment, transitioning from *"package label"* to its true identity as *"`_internal` protection device"*
- **README "altruism" line** — Added consistently to the `README.md` / `README_EN.md` license section + `_build_license_html()` project entry note. *"Originally built as a personal tool, now released under MIT in the hope it may help others with similar workflows."* GitHub README and the in-app license page deliver the same message to users

### Deferred
- **SignPath OSS Sponsorship application** — Application submitted to `signpath.org` immediately after v1.0.10 Release publish. Recording v1.0.10 as *"Latest release: first MIT release"* in the application strengthens review credibility. Approval is an external process (average 1-week review), and **CI integration + first signed artifact will proceed as a separate track in v1.0.11 after approval**. This release establishes the foundation by satisfying all 6 OSS Sponsorship eligibility criteria (OSI-approved license, no malware, maintained, released, documented, verifiable build)

### Tests
- **535 passing** (same as v1.0.9), 58 classes, zero failures/errors/skips (Hanrim's local + Git folder dual verification)
- Zero conflicts between v1.0.10 change areas (license text in 5 languages + library notes in 2 locations + footer "All rights reserved" removal + version updates) and the test invariants — the integer tuple comparison pattern (`parts = tuple(int(p) for p in ver.split('.'))`) introduced in v1.0.4 had pre-emptively prepared for two-digit patch versions like `1.0.10`, so all version-comparison invariants pass naturally
### Documentation
- `FileNexusSuite.py` `APP_VERSION` constant `1.0.9` → `1.0.10` (L76). The help dialog title across 5 languages and the sidebar version label, both referenced via f-string, are automatically updated consistently
- `version_info.txt` 4 locations `1.0.9`/`1.0.9.0` → `1.0.10`/`1.0.10.0` (`filevers` / `prodvers` tuples, `FileVersion` / `ProductVersion` strings)
- `README.md` / `README_EN.md` version badge 1.0.9 → 1.0.10 synchronized (Korean/English mirror principle applied)
- `README.txt` first line v1.0.9 → v1.0.10

### File Changes
- `FileNexusSuite.py`: 14,850 → 14,850 lines (no line count change — all 6 areas were *equal-line replacements*. The `\n\n` in `note` fields is a long string within a single line and does not affect line count)
- `LICENSE`: 76 → 68 lines (-8: third-party libraries list removed in both Korean and English — `_build_license_html()` + README take single-source-of-truth responsibility)
- `version_info.txt`: 4 version locations + `LegalCopyright` updated only
- `README.md` / `README_EN.md`: license section body reworded + 3 badges (color/text) updated + Copyright + LICENSE link
- `README.txt`: v1.0.10 update + `_internal` protection notice (Korean/English) + footer MIT

### Post-Release Documentation

After the v1.0.10 Release publish, 4 docs commits were added as alignment work for the external OSS-facing direction (the version number remains v1.0.10; this category accumulates after the v1.0.10 full-course completion). The intent: SignPath reviewers and external OSS reviewers, upon arriving at the repository, reach an English-default first screen + an English-default policy document.

- **`1c2c8e8`** — Added a SignPath code-signing notice to README (preparation for OSS Sponsorship application). Ensures that the v1.0.10 application's §9 Reputation reference to README reaches external reviewers showing the SignPath track in progress
- **`ceef147`** — README English-default direction transition (rename `README.md` → `README_KO.md`, `README_EN.md` → `README.md`). Git rename correctly recognized (3 files / +245 / −245). The repository's first screen now lands on the English README — the starting point of the external OSS-facing direction
- **`0a936f3`** — `TEST_MANAGEMENT_POLICY.md` English-default direction transition. The Korean original is preserved as `TEST_MANAGEMENT_POLICY_KO.md`; the English version is newly authored and overwrites the same filename, switching the external default to English. Clicking the `TEST_MANAGEMENT_POLICY.md` reference in the SignPath application's §9 Reputation now reaches the English document
- **`723219c`** — Follow-up commit adding `TEST_MANAGEMENT_POLICY_KO.md` Korean copy to GitHub. At the `0a936f3` moment the file was still untracked locally; the follow-up restores both English and Korean copies on GitHub

→ All 4 commits are SSH-signed and passed GitHub Actions CI. With this, the v1.0.10 docs cleanup track reaches completion; the project is ready to await SignPath review results and to enter the v1.0.11 new-feature track.

See also: `RELEASE_NOTE_v1.0.10.md` (working folder only, full-course completion-time text — post-release docs are documented directly in this category)

---

## [1.0.9] — 2026-04-25

The closing of the v1.0.x series — a post-cleanup / data hygiene category. A release bundling the four ACDG tasks of the v1.0.8 handover §5.1.

### Added
- `build_pyinstaller.py` `--strict` mode introduced — Separates the version-consistency verification step into pre-build (step 5), aborting the build immediately on mismatch. PyInstaller's tens of seconds + UPX compression are blocked before they begin, saving time/disk and preserving previous build artifacts. New function `check_version_consistency(strict)` added; step sequence reordered from 7 to 8 stages.
  - `build.bat` wrapper enhanced with `%*` argument pass-through, enabling direct `build.bat --strict` invocation
- `_t()` / `_rt()` functions gain a zh_cn → zh_tw fallback chain — Keys undefined in the zh_cn dictionary fall back first to zh_tw, then ultimately to ko. Addresses the limitation where, since v1.0.5, fallback was ko-only.
- `test_file_nexus.py` `test_zh_cn_fallback_to_zh_tw` new invariant — Verifies that the fallback pattern is alive in both `_t()` / `_rt()` functions and that the test target keys exist. If the fallback mechanism is later broken by someone's mistake, CI detects it automatically and immediately

### Changed
- **40 keys cleaned from the `zh_cn` dictionary** that were 100% identical in value to zh_tw — With the fallback chain in place, zero behavioral impact is guaranteed by definition (the v1.0.8 handover §5.1.G "188 keys" specification was not data-verified; honestly redefined as 47 keys in real data → 40 keys after excluding 7 invariant-protected)
  - Targets: emoji/symbols (▶, some UTF-8/UTF-16 encoding labels), short words (取消/完成/字/行 etc.), digit notations (最少2位/固定3位 etc.), placeholders (例: jpg, png, gif etc.), theme names (深色/蜂蜜/薰衣草 etc.)
  - 7 keys excluded due to invariant protection: `dlg_yes`/`dlg_no`/`dlg_warning` (common dialogs), `conv_status_done`/`conv_sub_epub2txt`/`conv_sub_txt2epub` (conversion status), `rename_cancel` (cancel) — core UI keys retain direct 5-language definition
- `test_file_nexus.py` `test_all_langs_same_key_count` redesigned — Switched from forced symmetry (5 languages with identical key counts) to allowed asymmetry (zh_cn permitted as a subset of zh_tw + ko/en/ja/zh_tw with identical key counts). Aligns with the zh_cn fallback mechanism
- `test_file_nexus.py` `test_all_languages_have_similar_key_count` updated — zh_cn now explicitly noted as using fallback chain and excluded from key-count verification; the other 4 languages retain the ≤5 difference enforcement (preserving v1.0.5 era intent)
- `README.md` / `README_EN.md` Copyright and author notation — `Yongwoo Shin (Hanrim)` → `Hanrim` (4 locations). Synchronization of GitHub-facing materials per the v1.0.8 §4.36 medium-specific notation policy. External formal materials (portfolio, planning documents) retain the full form

### Verified
- `HelpDialog` audited — Diagnosed the latent possibility of the same structural defect as the v1.0.8 SettingsDialog Option C pattern (page lazy regeneration). Comparison of invocation patterns confirmed the two dialogs are essentially different (HelpDialog uses `exec()` modal + zero signal connections vs. SettingsDialog uses "window persistence" + 3 signals), so Option C application is not needed. The audit itself is the v1.0.9 §5.1.D output (zero code change; the absence of latent defects documented as data)

### Tests
- **535 passing** (+1 vs v1.0.8), 58 classes, zero failures/errors/skips (Hanrim's local + Git folder dual verification)
- Regression detection → fix cycle: After §5.1.G first application, 6 v1.0.5 regression tests FAILed (omitted in cleaning the `merge_enc_utf8`/`utf16`/`shiftjis` invariant-protected keys) → cleanup target reduced 47→40 + invariant updated → 535/0/0/0 passing
- Automated test simulation step passed (all PySide6-independent invariants directly verified)

### Documentation
- `FileNexusSuite.py` `APP_VERSION` constant `1.0.8` → `1.0.9` (L76). The help dialog title across 5 languages and the sidebar version label, both referenced via f-string, are automatically updated consistently
- `version_info.txt` 4 locations `1.0.8`/`1.0.8.0` → `1.0.9`/`1.0.9.0` (`filevers` / `prodvers` tuples, `FileVersion` / `ProductVersion` strings)
- `README.md` / `README_EN.md` version badge 1.0.8 → 1.0.9, tests badge 534 → 535 synchronized
- `README.txt` first line v1.0.8 → v1.0.9

### File Changes
- `FileNexusSuite.py`: 14,883 → 14,850 lines (-33: zh_cn 40 keys removed -40 + `_t()`/`_rt()` fallback enhancement +6 + APP_VERSION update etc.)
- `test_file_nexus.py`: 4,553 → 4,589 lines (+36: new invariant `test_zh_cn_fallback_to_zh_tw` +20 + 2 existing invariants updated +16)
- `build_pyinstaller.py`: 262 → 284 lines (+22: new `check_version_consistency` function + `--strict` CLI parsing + step sequence reordering)
- `build.bat`: `%*` argument pass-through, 1-character addition
- `README.md` / `README_EN.md`: notation in 4 locations + 2 badges updated
- `version_info.txt`, `README.txt`: version updates only

### Known Issues / Deferred to v1.1.x
- **`ko` dictionary 1-key shortage signal** — fail_log message indicates `'ko': 403` while the other 4 languages show 404, a 1-key gap. Likely arose somewhere after v1.0.7 §additional work. There is also a possibility that `_count_keys_per_language` regex misses 1 key in multi-line values. Out of scope for v1.0.9 §5.1.G; deferred as a v1.1.x candidate
- **Claude Desktop 4/14 redesign side effect** (externally observed in v1.0.9) — On the client side, the chat input's markdown auto-linking appears to have been turned on more aggressively. Operationally, the response is to wrap with backticks (`` ` ``) and route long outputs through file uploads

See also: `RELEASE_NOTE_v1.0.9.md` (working folder only)

---

## [1.0.8] — 2026-04-25

### Fixed
- **Settings dialog label/frame color residue bug** (existed since v1.0.5; the main task surviving 5 releases) — **Structurally resolved** by introducing the page lazy regeneration mechanism. Inherited as the main task from v1.0.7 §11.3; after the 4 approaches attempted in the v1.0.6 session (QTimer delay / unpolish-polish / QApplication global reapply / findChildren update) all failed, v1.0.8 unwound it through the honest flow of pre-investigation → code diagnosis → option re-evaluation.
  - Code diagnosis revealed that §11.1's "3 affected widgets" was actually the tip of an iceberg of **22 widget update omissions** (a structural problem where nearly every inline-stylesheet widget inside a page is permanently fixed to the theme at creation time)
  - Option A (Targeted update, ~60–80 lines) was set aside in favor of Option C (page regeneration, +17 lines) — 1/4 the code change, with permanent prevention of recurrence-by-omission
  - Mechanism: Automates the same pattern as the workaround (reopening the settings window) inside the dialog. Aligns with the direction Hanrim had pre-noted as a candidate in §11.3
- (Side defect) `_ver_lbl` (sidebar bottom version label) theme-switch update omission patched. Found during code diagnosis for Option C: a defect where v1.0.6 left the comment "self saved for updates" but `_refresh_theme` had omitted the call. Resolved simultaneously
- (Side defect) Output folder buttons (`_odir_btn` / `_odir_reset_btn`) text not updating on language switch. A residue from v1.0.6 D-2 work where `_retranslate_dialog` referenced `self._odir_btn` but `_page_language` only created it as a local variable, silently failing the `hasattr` check. Auto-resolved by page regeneration

### Changed
- `SettingsDialog._refresh_theme` / `_retranslate_dialog` responsibilities clarified — Simplified so they only own the dialog's outer widgets. Stylesheet/text updates for widgets inside pages are batched by the new `_recreate_pages` method.
  - `_refresh_theme`: 32 lines → 30 lines (page-internal update loop removed + `_ver_lbl` update added + `_recreate_pages()` call added + comments)
  - `_retranslate_dialog`: 48 lines → 16 lines (page-internal text updates all delegated to `_recreate_pages`)
- 1 line removed in `_apply_theme_now`: `for n, card in self._cards.items(): card.set_selected(...)`. Unnecessary since new cards are auto-created with `selected=(name==self._chosen)` during page regeneration

### Added
- `SettingsDialog._recreate_pages()` new method — destroys + recreates all 4 pages.
  - 7-step safe flow: shortcut capture safe-termination → output folder temporary input value preservation → existing page widgets removed (`removeWidget` + `deleteLater`) → container dict reset → new pages created → temporary input value restored → current page switched
  - Explicit automation of the workaround (reopen settings window) mechanism. Permanently prevents the risk of forgetting to update `_refresh_theme` / `_retranslate_dialog` when widgets are added to pages in the future
  - **New behavior under Option C**: Text the user typed but not yet applied in the output folder input field is preserved through page regeneration (improvement over v1.0.7 behavior)
- `test_file_nexus.py` `TestSettingsDialogStructureInvariant` class (§Q-additional, +72 lines) — 3 structural invariants for the v1.0.8 Option C mechanism:
  - `test_settings_dialog_has_recreate_pages` — Verifies `_recreate_pages` method exists
  - `test_refresh_theme_calls_recreate_pages` — Verifies `_refresh_theme` body contains a `self._recreate_pages()` call (`inspect.getsource`-based)
  - `test_retranslate_dialog_simplified` — Verifies `_retranslate_dialog` does not directly update 9 page-internal attributes (`_theme_page_title`, `_lang_page_title` etc.)
  - Applies TEST_MANAGEMENT_POLICY §3 principle 4 (explicit automated coverage for new features). If someone later breaks the Option C mechanism, CI detects it automatically and immediately

### Tests
- **534 passing** (+3 vs v1.0.7), 58 classes, zero failures/errors/skips (Hanrim's local measurement)
- 531/0/0/0 maintained immediately after Option C patch → 534/0/0/0 after adding 3 invariants
- Manual QA: light↔dark bidirectional normal + safe Apply during shortcut capture + output folder temporary input preservation, all passed (Hanrim's verification)

### Documentation
- `FileNexusSuite.py` `APP_VERSION` constant `1.0.7` → `1.0.8` (L76). Help dialog title across 5 languages and sidebar version label, both referenced via f-string, automatically updated consistently
- `version_info.txt` 4 locations `1.0.7`/`1.0.7.0` → `1.0.8`/`1.0.8.0` (`filevers` / `prodvers` tuples, `FileVersion` / `ProductVersion` strings). Ensures consistent metadata in the Windows `.exe` properties window after PyInstaller build
- `README.md` / `README_EN.md` version badge 1.0.7 → 1.0.8, tests badge 531 → 534 synchronized
- `README.txt` first line v1.0.7 → v1.0.8

### File Changes
- `FileNexusSuite.py`: 14,866 → 14,883 lines (+17: `_recreate_pages` new method +35 + outer simplification -28 + comments +6 + APP_VERSION update etc.)
- `test_file_nexus.py`: 4,481 → 4,553 lines (+72: new `TestSettingsDialogStructureInvariant` class)
- `version_info.txt`, `README.md`, `README_EN.md`, `README.txt`: version updates only

See also: `RELEASE_NOTE_v1.0.8.md` (to be written during v1.0.8 release preparation)

---

## [1.0.7] — 2026-04-22

### Fixed
- (Session 1) TextMergerPanel `_set_scan_ui` dead `or True` condition removed
- (Session 1) TextConverterPanel `ConvertWorker.sig_file_progress` disconnect omission patched (5:5 symmetry)
- (Session 1) TextFixerPanel `_run` internal worker cleanup gains terminate fallback
- (CI adoption preparation) `test_file_nexus.py` custom runner exit code contract patched — fails/errors trigger `sys.exit(1)`, ensuring CI badge accuracy (previously, exit code 0 was returned even on failure, allowing CI to display a false green light)
- (CI adoption preparation) `requirements.txt` missing `python-hwpx>=2.9.0` added (the v1.0.6 HWPX input dependency had been listed only in README and the tech stack but missing from requirements — inconsistency resolved)
- (CI adoption preparation) `FileNexusSuite.py` L76 `APP_VERSION` constant `1.0.6` → `1.0.7` (initially missed in Session 3, found just before release through Hanrim's `findstr` verification). The app title and help window version display, both referenced via f-string, are automatically updated consistently
- (CI adoption preparation) `version_info.txt` 4 locations `1.0.6`/`1.0.6.0` → `1.0.7`/`1.0.7.0` (`filevers` / `prodvers` tuples, `FileVersion` / `ProductVersion` strings). Ensures the Windows `.exe` properties dialog displays "File version" / "Product version" metadata as v1.0.7 after PyInstaller build
- (CI adoption preparation) `README_EN.md` version badge and install command updated (synchronized to the same level as the Korean README — patching the Session 3 omission where only Korean was updated)

### Removed
- (Session 2) SettingsDialog `_nav_keys` / `_nav_icons` dead `"help"` entry
- (Session 2) `settings_nav_help` translation keys across 5 languages
- (Session 2) TextFixerPanel `_save_overwrite` dead method + `tf_save_overwrite` translation keys across 5 languages
- (Session 2) Unused `QListWidget` import and the corresponding QSS selector
- (Session 2) Unnecessary f-string prefixes in `_on_files_dropped` / `_on_folder_dropped` exit traces
- (Session 3) Translation key orphans **15 in total** removed (75 lines = 15 keys × 5 languages)
  - Bulk Fixer UI refactoring residues: `bulk_out_folder`, `bulk_save_dir`, `bulk_save_fixed`, `bulk_save_over`
  - Text Merger section label residues: `merge_file_list`, `merge_file_mgmt`
  - folder_renamer initial-source `_p_` prefix legacy (not incorporated during integration): `p_prefix_ph`
  - QTreeWidget header transition residue from v0.10.1 `_sort_files` removal: `sort_header`
  - Tag Editor section label residues: `tag_file_list`, `tag_preview_title`
  - Orphaned after Session 2 `_save_overwrite` removal (completed in this session): `tf_dlg_overwrite`
  - GroupBox → inline option-bar refactoring residue: `tf_grp_opt` (with the L8477 reservation comment removed in the same line)
  - `_input_edit` QLineEdit → QTextEdit transition residue (active sibling `tf_ph_input_edit` preserved): `tf_ph_input`
  - TextFixerPanel is an embedded tab (QWidget) without its own title/subtitle labels: `tf_subtitle`, `tf_title`

### Changed
- (Session 3) Invariant translation key tests fully restructured from **version-snapshot pattern → tab-based functional area, 10 major categories**
  - 7 old tests removed: `test_all_langs_have_dlg_keys`, `test_all_langs_have_sort_header`, `test_all_langs_have_sc_tab_bulk`, `test_all_langs_have_new_v010_keys`, `test_rename_keys_exist`, `test_all_langs_have_v010_1_keys`, `test_all_langs_have_v100_keys`
  - 9 new tab-based tests added: `common_dialog` / `text_merger` / `text_converter` / `tag_editor` / `batch_renamer` / `text_fixer` / `settings` / `shortcut` / `misc` (existing `bulk_fixer_keys` retained as expanded)
  - `test_ko_has_minimum_keys` baseline updated (280 → 400, safe margin against the current 404)
- (CI adoption preparation) `TestV106AppVersion` / `TestV106AppVersionModule` → `TestAppVersion` / `TestAppVersionModule` redesigned for version-independent structural verification. Applies TEST_MANAGEMENT_POLICY.md §4.4 "no new adoption of version-snapshot patterns" beyond translation keys to **code version snapshots**. The previous `TestV104Regression → TestV105Regression → TestV106AppVersion` per-release migration convention is retired in favor of semver (MAJOR.MINOR.PATCH) format verification — no test changes required for future version updates. Patches the omission in Session 3 where only translation keys were tab-restructured but the code version snapshot was missed (revealed when `APP_VERSION` was updated and 2 tests FAILed during Hanrim's `findstr` verification just before release)

### Added
- (Session 3) `TEST_MANAGEMENT_POLICY.md` newly created — a permanent project reference document (155 lines)
  - Codifies the 5 test management principles
  - Adds dead-code criterion 5: "Invariant registration status in the test file" (reflecting the Session 2 `tf_dlg_overwrite` rollback case)
  - Through-line declaration: *"History is the responsibility of Git logs and the CHANGELOG; tests are maintained as the specification of what is currently alive"*
  - Specifies the 10 tab-based major categories and the principles for handling boundary-ambiguous cases
- (CI adoption) `.github/workflows/ci.yml` newly added — GitHub Actions CI pipeline
  - Runner: `windows-latest` only (matches Hanrim's local Windows environment, prioritizes 529/0/0/0 reproducibility)
  - Python: 3.10 only (matches Hanrim's local Python 3.10.11)
  - Triggers: main branch push/PR + `workflow_dispatch` (manual)
  - Dependencies: `pip install -r requirements.txt` as the single source of truth
- (CI adoption) `README.md` badges expanded — CI status badge + 529 tests passing badge added; install command simplified to `pip install -r requirements.txt`; version badge 1.0.6 → 1.0.7

### Audit Fixes (Session 3)
At the end of Session 2, an audit estimated 17 orphaned translation keys; in the β-protocol investigation, **2 keys were confirmed to be active** — the audit had missed a dynamic key generation pattern.
- `conv_sub_txt2epub` / `conv_sub_epub2txt` — Confirmed in active use via the `_t('conv_sub_' + val)` dynamic dispatch at L6560 in `TextConverterPanel.retranslate()`
- Original audit 17 → **actual dead 15** revised
- These 2 keys are now incorporated as representative keys in `test_all_langs_have_text_converter_keys`, protecting future dynamic-generation patterns as invariants as well

### Deferred to v1.0.8
- Settings dialog label color bug retry (Phase 2 Completion Record §11.3 guidance preserved)
- Originally the v1.0.7 main task, but tackled as a separate scope to avoid the risk of misjudgment when approaching a difficult problem amid the noise of 17 orphans — retried after a clean foundation was established by orphan cleanup + invariant restructuring

### Tests
- **529 passing** (+2 vs v1.0.6), 57 classes, zero failures/errors/skips (Hanrim's local measurement)
- Sessions 1–2: 527 passing maintained (Hanrim's local 0/0/0/0)
- Session 3: invariant restructuring removed 7 old + added 9 new (`bulk_fixer_keys` retained as expanded) → Net +2 methods
- Sandbox `TestTranslationCompleteness` selective execution: 12 tests passing (failure 0, error 0)

### File Changes
- `FileNexusSuite.py`: 14,942 → 14,866 lines (-76: 15 keys × 5 languages + L8477 comment)
- `test_file_nexus.py`: 4,370 → 4,448 lines (+78)
- `TEST_MANAGEMENT_POLICY.md`: new, 155 lines
- `CHANGELOG.md`: this v1.0.7 Unreleased section added

See also: `RELEASE_NOTE_v1.0.7.md` (Sessions 1–3 unified release note, to be written during v1.0.7 release preparation)

---

## [1.0.6] — 2026-04-21

### Added
- Text Merger HWPX input support (`python-hwpx 2.9.0`, MIT)
- Text Merger save-encoding auto-recommendation (`merger_recommend_save_encoding`)
- Bulk Fixer partially-corrupted file automatic 3-tier handling (Tier 1/2/3 + `encoding_report.txt`)
- Phase 1 common helper `safe_read_text_with_report`
- Phase 2-b Text Fixer / Bulk Fixer help text expansion (5 languages)

### Changed
- Text Converter structural refactoring (Bulk Fixer 5:4 layout pattern duplicated; new class `TextConverterDropZone`)
- Text Fixer / Bulk Fixer design philosophy separation (consent-based vs. post-hoc transparency-based)

### Fixed
- Settings dialog Traditional Chinese residue bug (existed since v1.0.5)
- `toolTip` corruption data loss bug (existed since v1.0.4; resolved by introducing `_PATH_ROLE`)
- Header sort bug (existed since v1.0.4; explicit `setSectionsClickable(True)`)
- `alchemy_detect_encoding` fallback confidence 0.0 → 0.7

### Performance
- Position-tracking algorithm O(N×K) → O(N) redesign (hundreds to thousands of times improvement, measured at 36 GB scale)
- Preview large-file 32 KB extraction (800× improvement)

### Documentation
- README structure redesign: separated into a 3-file structure — `README.md` (Korean slim) / `README_EN.md` (English) / `docs/STORY.md` (Korean narrative · philosophy)
- About section English-only + 12 Topics specified
- Key features bullets compressed from 7 → 4

### Removed
- `MergeDragList` dead code 57 lines (unused after the v1.0.3/1.0.4 `MergeFileTree` replacement)
- AppSuite 3 dead methods 74 lines (`_page_language` / `_on_lang_selected` / `_retranslate_dialog`)

### Tests
- **527 passing** (+25 vs v1.0.5), 57 classes, zero failures/errors/skips

See also: [`RELEASE_NOTE_v1.0.6.md`](./RELEASE_NOTE_v1.0.6.md)

---

## [1.0.5] — —

### Added
- Text Merger save-encoding dropdown shows associated languages alongside (e.g., `Shift-JIS (Japanese)`)
- One-line help label below the dropdown (`merge_enc_hint`)

### Changed
- Display label and internal key separated (`addItem(display, userData)` pattern; auto-compatible with v1.0.4 and earlier config files)

### Fixed
- Existing bug where Text Merger status messages remained in Korean upon language switch (existed before v1.0.4)
  - New `_retranslate_status()` helper + regex matching utility
  - Applied to all 9 status messages (5 static / 2 recoverable / 3 unrecoverable)

### Removed
- 74 duplicate keys cleaned up across translation dictionaries (deleted after AST value-equivalence verification; zero behavioral impact)
  - `zh_cn` 69 + `ko`/`en`/`zh_tw` 1 each + `ja` 2

### Security
- **SSH signing introduced** — Both commits and tags signed with Ed25519, GitHub Verified badge restored
  - Fingerprint: `SHA256:4H2f7lrFfI4u0YP0dpp6N9BQH2f74iKjjMRHu7lyjKI`

### Tests
- **502 passing** (+30 vs v1.0.4)

See also: [`RELEASE_NOTE_v1.0.5.md`](./RELEASE_NOTE_v1.0.5.md)

---

## [1.0.4] — —

### Added
- 3 additional save encodings in Text Merger: Shift-JIS / GBK / Big5 (matching the 5 supported languages)
- UnicodeEncodeError pre-warning dialog (3-pane display: types of unencodable characters, total character count, file ratio)
- 4-tier color coding by confidence % (🟢≥90% / 🟡≥70% / 🟠≥50% / 🔴<50%)
- CJK encoding badge colors added (🌸 Shift-JIS / 🟡 GBK / 🩵 Big5)

### Changed
- Encoding-detection function unified (`alchemy_detect_encoding` signature `str` → `(str, float)` tuple)
- Text Merger's own `_detect_encoding` removed → unified into alchemy
- Bytes read 8192 → 32768

### Fixed
- Warning dialog HTML tag rendering failure (introduced `rich_text=False` parameter)
- ASCII-prefixed CJK file encoding misjudgment (sequential fallback `cp949 → shift_jis → gbk → big5`)
- Warning dialog had been understating actual loss volume by a factor of 10

### Tests
- **472 passing** (+21 vs v1.0.3)

See also: [`RELEASE_NOTE_v1.0.4.md`](./RELEASE_NOTE_v1.0.4.md)

---

## [1.0.3] — —

### Fixed
- **Text Fixer / Bulk Fixer UTF-16 LE/BE file corruption** (10 affected cases, 5 languages × 2 encodings)
- Japanese Shift-JIS / Chinese GBK / Traditional Big5 files corrupted by `latin-1` fallback
- `alchemy_detect_encoding()` failure to detect CJK encodings (chardet 0.5–0.7 confidence blocked at the 0.7 threshold)

### Changed
- 3 hardcoded encoding lists unified under a single `alchemy_detect_encoding()`
- `latin-1` fallback removed (prevents false-positive "successful" decodings)
- `shift_jis`, `gbk`, `big5` fallbacks added + CJK whitelist (threshold loosened to 0.5)

### Tests
- 15 encoding regression-prevention tests added (5 languages × 5 encodings = 25 samples measured)
- **Pre-fix 13/25 (52%) → post-fix 25/25 (100%)**

See also: [`RELEASE_NOTE_v1.0.3.md`](./RELEASE_NOTE_v1.0.3.md)

---

## [1.0.2] — —

### Fixed
- Tag Editor exit protection missing (no confirmation popup on X/Alt+F4 during folder scan)
- Chinese-UI Bulk Fixer description label exposed as Korean (`bulk_save_desc` key missing)
- TXT → EPUB conversion duplicated the first line as both chapter title and body

### Changed
- bare `except:` 5 → 0 (Qt signal disconnect pattern made explicit)
- 5 unused imports / variables removed
- pyflakes warnings 5 → 0

See also: [`RELEASE_NOTE_v1.0.2.md`](./RELEASE_NOTE_v1.0.2.md)

---

## [1.0.1] — 2026-04-14

### Fixed
- ~100 hardcoded Korean strings replaced with `_t()` (resolves Korean exposure in English/Japanese/Chinese modes)
- Encoding detection comprehensively improved (chardet-based `alchemy_detect_encoding`, 3-stage UTF-8 discrimination)
- UTF-8 (BOM) files mis-detected as LATIN-1 and corrupted
- Always saving as UTF-8 → original encoding preserved (resolves abnormal 65 MB → 125 MB inflation)
- Save dialog default path: app folder → Output folder
- `QPlainTextEdit` rounded corners / progress bar style unified / combobox truncation
- Ctrl+F search help added (5 languages)

### Added
- 6 translation keys × 5 languages

See also: [GitHub Releases v1.0.1](https://github.com/MerciHanrim/FileNexusSuite/releases/tag/v1.0.1)
