# v1.0.6 — Text Converter 구조 리팩토링 + 부분 손상 파일 대응 + 설정 다이얼로그 번체 잔재 수정 / Text Converter refactoring + partial corruption handling + Settings dialog Traditional Chinese residue fix

Text Converter 레이아웃을 Bulk Fixer(v1.0.6) 패턴으로 재구성하여 드롭존 분리·5:4 레이아웃·하단 안내 박스 제거를 적용했고, 메모장에선 열리는데 Python strict 폴백이 모두 실패하던 **부분 손상 인코딩 파일** 대응을 추가했습니다(Phase 1 + Phase 2-a 티어드 자동 처리). Text Merger는 **HWPX 입력 지원**과 **A1'' 인코딩 자동 추천** 기능을 얻었고, v1.0.5부터 존재하던 **설정 다이얼로그 번체 중국어 잔재 버그**를 근본 수정했습니다. 데이터 손실 위험이 있던 `toolTip` 오염 버그와 헤더 정렬 버그도 함께 해결했고, 분 단위 걸리던 `O(N×K)` 위치 추적 알고리즘을 `O(N)`으로 재설계해 수백~수천 배 성능을 개선했습니다.

> Rebuilt the Text Converter layout along the Bulk Fixer (v1.0.6) pattern — drop-zone separation, 5:4 left-right ratio, bottom help-box removal — and added proper handling for **partially corrupted encoding files** that Notepad opens fine but Python's strict fallback all fail on (Phase 1 + Phase 2-a tiered automatic processing). Text Merger gained **HWPX input support** and **A1'' automatic encoding recommendation**, and a pre-existing **Settings dialog Traditional Chinese residue bug** (from v1.0.5) was rooted out. Also resolved the `toolTip` contamination bug (with data-loss risk) and header-sort bug, and redesigned the `O(N×K)` position-tracking algorithm to `O(N)` for hundreds-to-thousands times speedup on previously minute-long operations.

---

### ✨ 주요 기능 / Major Features

- **Phase 2-a — 인코딩 리포트 기능 + 티어드 자동 처리** / Phase 2-a — encoding report generation + tiered automatic processing
  - Bulk Fixer가 부분 손상 파일을 **세 티어로 자동 분류** / Bulk Fixer now automatically classifies partially corrupted files into **three tiers**
  - Tier 1 (손상 ≤500자): 처리 + 리포트 생성 / Tier 1 (≤500 corrupt chars): process + generate report
  - Tier 2 (손상 501~5000자): 처리 + 경고 수위 리포트 / Tier 2 (501~5000 corrupt chars): process + elevated-warning report
  - Tier 3 (손상 5001자+): **원본 보호** 스킵 + 리포트만 / Tier 3 (5001+ corrupt chars): **skip to preserve original** + report only
  - 리포트 파일명: `{원본파일명}.encoding_report.txt` (UTF-8 BOM 없음) / Report filename: `{original}.encoding_report.txt` (UTF-8 without BOM)
  - 실측 기반 임계값 결정 — `make_tier_test_data.py`로 경계값(499/5000/5001) 합성 데이터 회귀 검증 / Empirically-chosen thresholds — boundary values (499/5000/5001) validated via synthesized test data in `make_tier_test_data.py`
  - **설계 철학 분리**: Text Fixer(사용자 동의 기반) / Bulk Fixer(사후 투명성 기반) / **Philosophy separation**: Text Fixer (user-consent based) vs. Bulk Fixer (post-hoc transparency based)

- **#7 Text Converter 구조 리팩토링** / #7 Text Converter structural refactoring
  - 신규 클래스 `TextConverterDropZone` (109줄) — `BulkFixerDropZone` 복제 + `mode` 파라미터로 TXT↔EPUB 전환 시 텍스트·아이콘 자동 갱신 / New class `TextConverterDropZone` (109 lines) — cloned from `BulkFixerDropZone` + `mode` parameter auto-refreshing text/icon on TXT↔EPUB toggle
  - `TextConverterFileList` 단순화 — `InternalMove` → `DragDrop` 모드 전환, `setSectionsClickable(True)` 명시, `startDrag` CopyAction 강제 / Simplified `TextConverterFileList` — `InternalMove` → `DragDrop`, explicit `setSectionsClickable(True)`, forced `startDrag` CopyAction
  - 레이아웃 5:4 재구성 — 왼쪽(드롭존+파일목록) 확대, 오른쪽(옵션+출력폴더+변환버튼+진행바+상태) 재배치 / Layout restructured 5:4 — left panel (dropzone + file list) expanded, right panel (options + output folder + convert button + progress + status) rearranged
  - 하단 안내 박스 제거 (`conv_help` 5개 언어 번역 키 삭제) / Bottom help-box removed (`conv_help` translation keys dropped across 5 languages)
  - 폴더 드롭 미지원 — EPUB 생성 시 원본 폴더 구조 보존 이슈 방지 (의도된 설계) / Folder drop unsupported — intentional design to avoid EPUB source-folder structure preservation issues
  - **실기 QA 9/9 전수 통과** — 드롭존 양방향 / 모드 전환 / 내부 드래그 / 헤더 정렬 / 5:4 / 5개 언어 / 변환 E2E / toolTip 회귀 / 테마 전환 / IceCream Ebook Reader 외부 검증 포함 / **Manual QA 9/9 passed** — dropzone bidirectional / mode toggle / internal drag / header sort / 5:4 / 5 languages / round-trip conversion / toolTip regression / theme switch / with external IceCream Ebook Reader verification

- **Text Merger — HWPX 입력 지원** / Text Merger — HWPX input support
  - `python-hwpx 2.9.0` (MIT) 도입, `.hwpx` → 텍스트 추출 / Added `python-hwpx 2.9.0` (MIT), `.hwpx` → text extraction
  - `MergeEncodingDelegate`에 HWPX 배지(#9B59B6 보라색) 표시 / Purple HWPX badge (#9B59B6) on `MergeEncodingDelegate`
  - HWP(구형) 감지 시 통합 안내 다이얼로그 — 5개 언어 / HWP (legacy) detection shows a unified informational dialog across 5 languages
  - `lxml` 5.4.0으로 자동 다운그레이드 발생 (경고만, 동작 영향 없음) / `lxml` auto-downgraded to 5.4.0 (warning only, no functional impact)

- **Text Merger — A1'' 인코딩 자동 추천** / Text Merger — A1'' automatic encoding recommendation
  - 새 함수 `merger_recommend_save_encoding()` — 모든 텍스트 파일이 **같은 비유니코드 인코딩 + 신뢰도 ≥0.7**일 때 그 인코딩 추천, 그 외 UTF-8 / New function `merger_recommend_save_encoding()` — recommends the non-Unicode encoding if all files share it with confidence ≥0.7, otherwise UTF-8
  - UI: 드롭다운 아래 "💡 추천: XXX" 라벨 + [적용] 버튼 / UI: "💡 Recommended: XXX" label + [Apply] button beneath the dropdown
  - 파일 추가/선택삭제/전체삭제/언어전환 4지점에서 자동 갱신 / Auto-refresh at 4 trigger points: add files / delete selected / clear all / language switch

- **Phase 1 — 부분 손상 파일 안전 처리** / Phase 1 — safe handling of partially corrupted files
  - 공통 헬퍼 `safe_read_text_with_report()` — strict 폴백 8개 모두 실패 시 `errors='replace'`로 최종 재시도 / Shared helper `safe_read_text_with_report()` — final retry with `errors='replace'` when all 8 strict fallbacks fail
  - 깨진 바이트는 U+FFFD (`�`)로 대체 (Python 기본값, 유니코드 표준) / Corrupt bytes replaced with U+FFFD (`�`), Python's default and the Unicode standard
  - Text Fixer replace 모드 시 경고 다이얼로그 `tf_warn_partial_enc` (5개 언어) / Text Fixer replace mode shows warning dialog `tf_warn_partial_enc` in 5 languages
  - Bulk Fixer 미리보기·일괄 교정·Text Fixer 파일 로드 3곳 적용 / Applied in 3 locations: Bulk Fixer preview, Bulk Fixer worker, Text Fixer file load

- **Phase 2-b — Text Fixer / Bulk Fixer 도움말 확장** / Phase 2-b — Text Fixer / Bulk Fixer help section expansion
  - Text Fixer 도움말: "Partially corrupted files note" + 단일 파일 검토 도구 명시 + Tier 3 자동 스킵 안내 / Text Fixer help: "Partially corrupted files note" + single-file review tool explanation + Tier 3 auto-skip notice
  - Bulk Fixer 도움말: "Automatic corruption tiering note" (Tier 1/2/3 상세) + 리포트 파일명 형식 + Text Fixer 개별 검토 유도 / Bulk Fixer help: "Automatic corruption tiering note" (Tier 1/2/3 details) + report filename format + Text Fixer individual review guidance
  - 5개 언어 모두 시각 검수 통과 / Visual review passed in all 5 languages

---

### 🐛 버그 수정 / Bug Fixes

- **설정 다이얼로그 번체 중국어 잔재** / Settings dialog Traditional Chinese residue (v1.0.5부터 존재 / pre-existing since v1.0.5)
  - 현상: 繁體 → 한국어 전환 시 단축키 리셋 버튼에 `預設`, `重設所有快捷鍵` / 출력 폴더 라벨에 `輸出資料夾` / 버튼에 `選擇資料夾` / `重設` 등 번체 잔재 / Symptom: after switching 繁體 → Korean, residue like `預設`, `重設所有快捷鍵`, `輸出資料夾`, `選擇資料夾`, `重設` remained
  - 원인: `SettingsDialog._retranslate_dialog`가 일부 위젯 텍스트 갱신을 누락 (단축키 리셋 버튼 6개 + 전체 리셋 + 일반 설정 출력 폴더 라벨·버튼 + 라이선스 타이틀) / Root cause: `SettingsDialog._retranslate_dialog` missed text updates for 6 individual reset buttons + reset-all button + output folder label/buttons + license title
  - 수정 — 지시서 v2 기반: `_apply_theme_now`에 `_retranslate_dialog()` 호출 추가(§2.1), 위젯 self 저장 9개 보완(§2.2), `_retranslate_dialog`에 D-1/D-2/D-3 블록 확장(§2.4) / Fix — per Work Instruction v2: added `_retranslate_dialog()` call to `_apply_theme_now` (§2.1), preserved 9 widget self-references (§2.2), expanded `_retranslate_dialog` with D-1/D-2/D-3 blocks (§2.4)
  - AppSuite 내 데드 코드 3개 메서드 **74줄 완전 제거**(§2.5) — `_page_language` / `_on_lang_selected` / `_retranslate_dialog` (SettingsDialog가 별도 QDialog로 분리되기 전 잔재된 복제본) / Removed 3 dead methods (74 lines) in AppSuite (§2.5) — remnants from before `SettingsDialog` was split into a separate `QDialog`

- **`toolTip` 오염 데이터 손실 버그** / `toolTip` contamination data-loss bug (v1.0.4부터 존재 / pre-existing since v1.0.4)
  - 현상: 신뢰도 <0.90 파일의 툴팁에 안내문이 덧붙어 `item.toolTip(0)` 기반 경로 조회 실패 → 삭제한 파일이 병합 결과에 포함되는 **데이터 손실** / Symptom: low-confidence (<0.90) files had info appended to their toolTip, breaking `item.toolTip(0)` path lookups → deleted files included in merge output, causing **data loss**
  - 수정: `_PATH_ROLE = Qt.ItemDataRole.UserRole + 4` 신설, 순수 경로 저장 / Fix: new `_PATH_ROLE = Qt.ItemDataRole.UserRole + 4` storing pure paths
  - 3개 클래스 적용: `MergeEncodingDelegate`, `TextConverterFileList`, `BulkFixerFileList` / Applied to 3 classes: `MergeEncodingDelegate`, `TextConverterFileList`, `BulkFixerFileList`
  - 하위 호환 폴백 유지: `item.data(0, _PATH_ROLE) or item.toolTip(0)` / Backward-compat fallback retained: `item.data(0, _PATH_ROLE) or item.toolTip(0)`

- **헤더 정렬 버그** / Header sort bug (v1.0.4부터 존재 / pre-existing since v1.0.4)
  - 현상: `setSortingEnabled(False)` + `DragDrop` 모드 조합에서 헤더 클릭으로 정렬이 동작하지 않음 / Symptom: with `setSortingEnabled(False)` + `DragDrop` mode, header-click sorting stopped working
  - 원인: Qt의 기본 동작으로 `setSortingEnabled(False)` 시 헤더 섹션 클릭이 비활성화됨 / Cause: Qt disables header section clicks when `setSortingEnabled(False)`
  - 수정: `hdr.setSectionsClickable(True)` 명시 추가 (MergeFileTree v1.0.3/1.0.4 패턴 복제) / Fix: explicit `hdr.setSectionsClickable(True)` (pattern cloned from MergeFileTree v1.0.3/1.0.4)

- **alchemy_detect_encoding 폴백 신뢰도 0.0 → 0.7** / alchemy_detect_encoding fallback confidence 0.0 → 0.7
  - 폴백 루프 통과 시(cp949/shift_jis/gbk/big5) 신뢰도를 0.7로 상향 / Confidence raised to 0.7 on fallback-loop success (cp949/shift_jis/gbk/big5)
  - utf-8 strict 폴백도 0.0 → 0.7 (일관성) / utf-8 strict fallback also raised to 0.7 (consistency)
  - 짧은 한글 CP949 파일이 "70% CP949" 배지 + "💡 추천: CP949"로 정상 표시 / Short Korean CP949 files now correctly show "70% CP949" badge + "💡 Recommended: CP949"

---

### ⚡ 성능 개선 / Performance Improvements

- **O(N×K) → O(N) 위치 추적 재설계** / O(N×K) → O(N) position tracking redesign
  - 기존: 파일당 손상 바이트 K개 찾기 위해 N바이트 전수 순회 → K회 반복 = O(N×K) / Before: for each of K corrupt bytes, scanned all N bytes → O(N×K)
  - 신규: `codecs.register_error('_fns_track', ...)` 기반 **단일 패스**로 디코딩 중 위치 수집 → O(N) / After: single-pass position collection during decode via `codecs.register_error('_fns_track', ...)` → O(N)
  - 실측: 분 단위 → 수백 ms (**수백~수천 배 개선**, 36GB 규모 파일군에서 현실화) / Measured: minutes → hundreds of ms (**hundreds-to-thousands times faster**, observed at 36GB scale)

- **미리보기 대용량 파일 프리징 해소** / Preview large-file freeze resolved
  - `text[:32768].splitlines` 패턴으로 32KB만 추출 (800배 개선) / Extract only 32KB via `text[:32768].splitlines` pattern (800× faster)
  - 수백 MB 파일 미리보기 클릭 시 즉시 응답 / Instant response on preview click for multi-hundred-MB files

---

### 🧹 코드 위생 / Code Hygiene

- **죽은 코드 제거** / Dead code removal
  - `MergeDragList` 57줄 제거 (v1.0.3/1.0.4에서 `MergeFileTree`로 교체 후 미사용 상태) / Removed `MergeDragList` (57 lines) — unused since v1.0.3/1.0.4 replacement by `MergeFileTree`
  - AppSuite 내 중복 메서드 3개 74줄 제거 (`_page_language` / `_on_lang_selected` / `_retranslate_dialog`) — SettingsDialog 분리 이전 잔재 / Removed 3 duplicated methods in AppSuite (74 lines) — remnants from pre-dialog split

- **진단 인프라 구축** / Diagnostic infrastructure
  - `🔵 [Trace]` 3단계 세분 측정 (`_on_file_selected` 6지점 포함) / 3-level `🔵 [Trace]` profiling (including 6 points in `_on_file_selected`)
  - `docs/debug/` 3종 스크립트 신설 / 3 new scripts in `docs/debug/`:
    - `diagnose_ilsig.py` — 단일 파일 5단계 벤치마크 / single-file 5-stage benchmark
    - `scan_corrupted.py` — 전체 컬렉션 스캔 (임계값 50 기준) / full collection scan (threshold 50)
    - `make_tier_test_data.py` — 티어 경계값 합성 데이터 생성 / tier boundary synthetic data generator

---

### 🧪 테스트 자동화 / Test Automation

- **총 527개 테스트 통과** / **527 tests passing**, 57개 클래스 / 57 classes, 실패 0 / 오류 0 / 스킵 0 / 0 failed / 0 errors / 0 skipped ⭐
- Phase 2-a 신규 `TestSafeReadTextWithReport` / `TestDecodeWithFailureTracking` / `TestWriteEncodingReport` (3개 클래스 22개 테스트) / Phase 2-a new: 3 classes, 22 tests
- v1.0.6 성능 회귀 `TestBulkFixerPreviewLargeFile` / `TestPreviewExtractionPerformance` (2개 클래스 3개 테스트) / v1.0.6 perf regression: 2 classes, 3 tests
- APP_VERSION 분리: `TestV106AppVersion` / `TestV106AppVersionModule` (2개 클래스) — v1.0.5 회귀 클래스는 해당 버전 기타 회귀 계속 지켜봄 / APP_VERSION split out: 2 new classes — v1.0.5 regression classes retain their other v1.0.5-era regression coverage
- V103/V104 회귀 4건 A-2 확장 — Phase 2-a 헬퍼 경유 허용 / V103/V104 regression 4 tests extended (A-2) — allowing Phase 2-a helper-path invocation

---

### 🔍 검증 범위 / Verification Scope

- **단위 테스트** / Unit tests: **527 passing** (v1.0.5: 502 + v1.0.6 신규 25)
- **실기 검증** / Manual testing:
  - Text Converter 리팩토링 실기 QA 9/9 (IceCream Ebook Reader 외부 검증 포함) / Text Converter refactoring manual QA 9/9 (with external IceCream Ebook Reader verification)
  - Phase 2-a 티어 경계값 검증 — 합성 데이터 499/5000/5001자 파일로 분기 실측 / Phase 2-a tier boundary verification — tested via synthetic 499/5000/5001-char files
  - 설정 다이얼로그 번체 → 한국어 전환 잔재 해소 실기 확인 (繁體로 전환 → 단축키·일반설정·라이선스 탭 순회 → 한국어 복귀 → 모든 탭 잔재 없음) / Traditional → Korean switch residue fix verified manually (switch to 繁體 → cycle through tabs → return to Korean → no residue)
  - HWPX 입력 실제 한컴 파일로 검증 / HWPX input verified with actual Hancom files
  - 5개 언어 UI 전수 순회 검증 / UI navigated in all 5 languages
  - 36GB 규모 실제 파일군으로 O(N) 성능 실측 / O(N) performance measured on real 36GB-scale file corpus
- **빌드 검증** / Build verification:
  - Windows 파일 속성 대화상자에서 파일 버전 `1.0.6.0` / 제품 버전 `1.0.6.0` / 저작권 `Copyright © 2026 Hanrim` 실측 확인 / File Properties dialog confirms file version `1.0.6.0` / product version `1.0.6.0` / copyright `Copyright © 2026 Hanrim`

---

### 📦 구조적 변경 / Structural Changes

- **라인 수** / Line count: `FileNexusSuite.py` 13,886 → **14,971줄** (+1,085) — v1.0.5 원본 대비 / compared to v1.0.5 baseline
- **신규 지시서 문서** / New work-instruction documents:
  - `v1.0.6_TextConverter_Refactor_Work_Instruction.md` (381줄) — #7 리팩토링 단계별 구현 및 검증 기준 / #7 step-by-step implementation and verification criteria
  - `v1.0.6_SettingsDialog_RefreshRetranslate_Work_Instruction.md` (359줄) — 설정 다이얼로그 §2.1~§2.5 수정 지시서 / Settings dialog §2.1–§2.5 fix instructions
- **호칭 정리** / Attribution cleanup:
  - README.md 한글 본명 표기 제거 (L36 `[신용우(Hanrim)]` → `[Hanrim]`, L280에서도 동일) / Removed Korean-name display in README.md (L36, L280)
  - 공식 크레딧 `Yongwoo Shin (Hanrim)`은 영문 본문(L38) 및 Copyright(L268)에서 유지 / Formal credit `Yongwoo Shin (Hanrim)` retained in English narration (L38) and Copyright (L268)
  - 프로그램 내부 표기는 `Hanrim` 단독으로 일관 (파일 속성, 내부 주석 등) / In-program attribution uses `Hanrim` alone (file properties, internal comments, etc.)

---

### 🔐 릴리즈 서명 / Release Signing

- **v1.0.5부터 도입된 SSH 서명 유지** / SSH signing (introduced in v1.0.5) maintained
  - 커밋 + 태그 모두 Ed25519 SSH 키로 서명 → GitHub Verified 뱃지 / Both commit and tag signed with Ed25519 SSH key → GitHub Verified badge
  - Fingerprint: `SHA256:4H2f7lrFfI4u0YP0dpp6N9BQH2f74iKjjMRHu7lyjKI`

---

### 💬 검토 / Review

- Claude Opus 4.7 기반 AI 페어 프로그래밍 + 개발자 실기 QA 다단계 검증 / Multi-stage verification: Claude Opus 4.7 AI pair programming + developer manual QA

---

### ⚠ 알려진 이슈 / Known Issues

- **설정 다이얼로그 라벨/프레임 color 잔재** (v1.0.5부터 존재, v1.0.7 이월) / **Settings dialog label/frame color residue** (pre-existing since v1.0.5, deferred to v1.0.7)
  - 현상: 테마 [적용] 후 다른 탭 이동 시 **라이트 → 다크 방향에서만** 일부 위젯(언어 프레임 배경, 타이틀 라벨 color, 출력 폴더 관련 위젯)이 이전 테마 값으로 남음 / Symptom: after applying a theme change and switching tabs, **only in light → dark direction**, some widgets (language frame background, title label color, output-folder-related widgets) retain old-theme values
  - 워크어라운드: 설정창을 닫고 다시 열면 정상 복귀 / Workaround: close and reopen Settings window to restore normal appearance
  - 영향: 시각적 가독성 저하 (기능에는 영향 없음) / Impact: reduced visual readability (no functional impact)
  - v1.0.6 오후 세션에서 4가지 접근(QTimer 지연 / polish·unpolish / QApplication 전역 재적용 / findChildren().update()) 시도했으나 근본 해결 못 하여 원상복귀 + 이월 결정 / Four approaches attempted in v1.0.6 afternoon session (QTimer delay / polish·unpolish / QApplication global re-apply / findChildren().update()) — none resolved root cause, reverted to v1.0.5 state and deferred
  - v1.0.7에서 Qt QSS 동적 업데이트 메커니즘 사전 조사 후 재도전 예정 / v1.0.7 will revisit after Qt QSS dynamic-update mechanism research

---

### 📦 이 릴리즈에서 정리된 v1.0.5 이월 항목 / v1.0.5 Deferred Items Resolved in This Release

- ✅ `MergeDragList` 죽은 코드 제거 — #7 작업과 동반 정리 / `MergeDragList` dead code removed — along with #7 work
- ✅ Text Converter 구조 리팩토링 (인수인계 §5.2) — #7로 완료 / Text Converter structural refactoring (handover §5.2) — completed as #7
- ⏭ 언어 전환 시 "출력 폴더 변경" 로그 중복 — v1.0.7로 이월 (동작 영향 없음) / Duplicate "output folder changed" log on language switch — deferred to v1.0.7 (no functional impact)

---

**다운로드**: 아래 `FileNexusSuite_v1.0.6_win64.zip` 파일을 다운로드하고 압축을 해제한 뒤 `FileNexusSuite.exe`를 실행하세요.
**Download**: Download `FileNexusSuite_v1.0.6_win64.zip` below, extract, and run `FileNexusSuite.exe`.
