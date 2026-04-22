# Changelog

본 프로젝트의 주요 변경사항을 버전별로 기록합니다.

각 버전의 코드 변경 상세는 [`RELEASE_NOTE_vX.X.X.md`](./) 파일을 참조하세요.
포맷은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/)를 따릅니다.

---

## [Unreleased] — v1.0.7

### Fixed
- (세션 1) TextMergerPanel `_set_scan_ui` 데드 `or True` 조건 제거
- (세션 1) TextConverterPanel `ConvertWorker.sig_file_progress` disconnect 누락 보완 (5:5 대칭)
- (세션 1) TextFixerPanel `_run` 내부 워커 정리에 terminate 폴백 추가
- (CI 도입 준비) `test_file_nexus.py` 커스텀 러너 exit code 계약 보완 — 실패/오류 시 `sys.exit(1)`, CI 뱃지 정확성 보장 (기존에는 실패해도 exit 0 반환하여 CI가 거짓 초록불을 띄울 수 있었음)
- (CI 도입 준비) `requirements.txt`에 `python-hwpx>=2.9.0` 누락 보완 (v1.0.6 HWPX 입력 지원 의존성이 README·기술 스택에만 명시되고 requirements에서 빠져 있던 불일치 해소)
- (CI 도입 준비) `FileNexusSuite.py` L76 `APP_VERSION` 상수 `1.0.6` → `1.0.7` 갱신 (세션 3 당초 누락, 릴리즈 직전 한림의 `findstr` 검증으로 발견). f-string으로 참조되는 앱 타이틀·도움말 창 버전 표시가 자동 일관 갱신됨
- (CI 도입 준비) `version_info.txt` 4곳 `1.0.6`/`1.0.6.0` → `1.0.7`/`1.0.7.0` 갱신 (`filevers` / `prodvers` 튜플, `FileVersion` / `ProductVersion` 문자열). PyInstaller 빌드 시 Windows `.exe` 속성 창의 "파일 버전" / "제품 버전" 메타데이터가 v1.0.7로 표시되도록 정합 확보
- (CI 첫 실행 hotfix) `requirements.txt`에서 `PySide6-Qt6-Qt6Svg>=6.4.0` 제거 — PyPI에 존재하지 않는 유령 패키지. 한림 로컬에서는 `pip install` 시 조용히 넘어가 발견되지 않았으나, CI의 깨끗한 환경에서 `ERROR: Could not find a version that satisfies the requirement` 실패로 드러남. PySide6 본체에 QtSvg 모듈이 이미 포함되어 있어 별도 설치 불필요 — CI 도입의 가치가 첫 실행에서 바로 입증된 사례
- (CI 도입 준비) `README_EN.md` version 뱃지 및 설치 명령어 갱신 (한국어 README와 동일 수준으로 동기화 — 세션 3에서 한국어만 갱신됐던 부분 보완)

### Removed
- (세션 2) SettingsDialog `_nav_keys` / `_nav_icons` 데드 `"help"` 엔트리
- (세션 2) `settings_nav_help` 번역키 5개 언어
- (세션 2) TextFixerPanel `_save_overwrite` 데드 메서드 + `tf_save_overwrite` 번역키 5개 언어
- (세션 2) 미사용 `QListWidget` import 및 대응 QSS 셀렉터
- (세션 2) `_on_files_dropped` / `_on_folder_dropped` 종료 trace의 불필요한 f-string prefix
- (세션 3) 번역키 고아 **15건** 전수 제거 (75줄 = 15키 × 5언어)
  - Bulk Fixer UI 리팩토링 잔재: `bulk_out_folder`, `bulk_save_dir`, `bulk_save_fixed`, `bulk_save_over`
  - Text Merger 섹션 라벨 잔재: `merge_file_list`, `merge_file_mgmt`
  - folder_renamer 초기 소스 `_p_` prefix 유산(통합 시 미편입): `p_prefix_ph`
  - v0.10.1 `_sort_files` 제거 시 QTreeWidget 헤더 전환 잔재: `sort_header`
  - Tag Editor 섹션 라벨 잔재: `tag_file_list`, `tag_preview_title`
  - 세션 2 `_save_overwrite` 제거 후 고아화 (본 세션 완결): `tf_dlg_overwrite`
  - GroupBox → 인라인 옵션 바 리팩토링 잔재: `tf_grp_opt` (L8477 보류 주석 1줄 함께 제거)
  - `_input_edit` QLineEdit → QTextEdit 전환 잔재 (활성 형제 `tf_ph_input_edit` 보존): `tf_ph_input`
  - TextFixerPanel은 임베디드 탭(QWidget)이라 title/subtitle 라벨 자체 없음: `tf_subtitle`, `tf_title`

### Changed
- (세션 3) invariant 번역키 테스트를 **버전 스냅샷 방식 → 탭 기반 기능 영역 10개 대분류**로 전면 재구성
  - 제거된 구 테스트 7개: `test_all_langs_have_dlg_keys`, `test_all_langs_have_sort_header`, `test_all_langs_have_sc_tab_bulk`, `test_all_langs_have_new_v010_keys`, `test_rename_keys_exist`, `test_all_langs_have_v010_1_keys`, `test_all_langs_have_v100_keys`
  - 신설된 탭 기반 테스트 9개: `common_dialog` / `text_merger` / `text_converter` / `tag_editor` / `batch_renamer` / `text_fixer` / `settings` / `shortcut` / `misc` (기존 `bulk_fixer_keys`는 확장 유지)
  - `test_ko_has_minimum_keys` 기준 수치 갱신 (280 → 400, 현 404개 기준 안전 마진)
- (CI 도입 준비) `TestV106AppVersion` / `TestV106AppVersionModule` → `TestAppVersion` / `TestAppVersionModule`로 버전 독립 구조 검증 재설계. TEST_MANAGEMENT_POLICY.md §4.4 "버전 스냅샷 방식 invariant 신규 도입 금지" 원칙을 번역키 외 **코드 버전 스냅샷**에도 적용. 기존 `TestV104Regression → TestV105Regression → TestV106AppVersion` 매 릴리즈 이월 관례를 폐기하고 세미버전(MAJOR.MINOR.PATCH) 포맷 검증으로 전환 — 향후 버전 번호 갱신 시 테스트 수정 불필요. 세션 3에서 번역키만 탭 기반으로 재구성하고 코드 버전 스냅샷을 놓친 부분의 사후 보완 (릴리즈 직전 한림의 `findstr` 검증 과정에서 `APP_VERSION` 갱신 후 2건 FAIL로 드러남)

### Added
- (세션 3) `TEST_MANAGEMENT_POLICY.md` 신설 — 프로젝트 영구 참조 문서 (155줄)
  - 5대 테스트 관리 원칙 명문화
  - 데드 판정 기준 5번 신설: "테스트 파일의 invariant 불변식 등록 여부" (세션 2 `tf_dlg_overwrite` 원상복귀 사례 반영)
  - 관통 축 선언: *"역사는 Git 이력과 CHANGELOG가 담당하고, 테스트는 현재 살아있는 명세로 유지된다"*
  - 탭 기반 대분류 10개 명세 및 경계 애매 케이스 처리 원칙
- (CI 도입) `.github/workflows/ci.yml` 신규 — GitHub Actions CI 파이프라인
  - 러너: `windows-latest` 단일 (한림 로컬 Windows 환경과 일치, 531/0/0/0 재현 최우선)
  - Python: 3.10 단일 (한림 로컬 Python 3.10.11과 일치)
  - 트리거: main 브랜치 push/PR + `workflow_dispatch`(수동)
  - 의존성: `pip install -r requirements.txt` 단일 진실 원천
- (CI 도입) `README.md` 뱃지 확장 — CI 상태 뱃지 + 531 tests passing 뱃지 추가, 설치 명령어를 `pip install -r requirements.txt`로 단순화, version 뱃지 1.0.6 → 1.0.7 갱신

### Audit Fixes (세션 3)
세션 2 말미의 전수 감사에서 17건 고아로 추정된 번역키 중 **2건이 β 프로토콜 조사 과정에서 실제로는 활성 키**임이 확인됨 — 감사가 동적 키 생성 패턴을 놓친 결과.
- `conv_sub_txt2epub` / `conv_sub_epub2txt` — `TextConverterPanel.retranslate()` L6560의 `_t('conv_sub_' + val)` 동적 디스패치로 정상 사용 중
- 원 감사 17건 → **실제 데드 15건**으로 수정
- 본 2건은 `test_all_langs_have_text_converter_keys` 대표 키로 편입되어 향후 동적 생성 패턴도 invariant로 보호

### Deferred to v1.0.8
- 설정 다이얼로그 라벨 color 버그 재도전 (Phase 2 Completion Record §11.3 가이드 보존)
- v1.0.7 원 본과제였으나 17건 고아 노이즈 상태에서 난제 접근 시 판단 오류 위험이 있어 스코프 분리 — 고아 정리·invariant 재구성 완료 후 깨끗한 기반에서 재도전

### Tests
- **531 passing** (+4 vs v1.0.6), 57개 클래스, 실패·오류·스킵 0 (한림 로컬 실측)
- 세션 1·2: 527 passing 유지 (한림 로컬 0/0/0/0)
- 세션 3: invariant 재구성으로 구 7개 제거 + 신규 9개 추가 (`bulk_fixer_keys` 확장 유지) → Net +2 메서드
- CI 도입: `TestV106AppVersion` 2건 제거 + `TestAppVersion` 4건 신설 (버전 독립 구조 검증) → Net +2 메서드
- 샌드박스 `TestTranslationCompleteness` + `TestAppVersion` 선택 실행: 16 tests passing (failure 0, error 0, skipped 2 — PySide6 모듈 로드 필요 건만 skip, 한림 로컬에서는 모두 실행·통과)

### File Changes
- `FileNexusSuite.py`: 14,942 → 14,866 줄 (-76: 15키 × 5언어 + L8477 주석)
- `test_file_nexus.py`: 4,370 → 4,448 줄 (+78)
- `TEST_MANAGEMENT_POLICY.md`: 신규 155줄
- `CHANGELOG.md`: 본 v1.0.7 Unreleased 섹션 추가

상세: `RELEASE_NOTE_v1.0.7.md` (세션 1·2·3 통합 릴리즈 노트, v1.0.7 릴리즈 준비 단계에서 작성 예정)

---

## [1.0.6] — 2026-04-21

### Added
- Text Merger HWPX 입력 지원 (`python-hwpx 2.9.0`, MIT)
- Text Merger 저장 인코딩 자동 추천 (`merger_recommend_save_encoding`)
- Bulk Fixer 부분 손상 파일 자동 3-티어 처리 (Tier 1/2/3 + `encoding_report.txt`)
- Phase 1 공통 헬퍼 `safe_read_text_with_report`
- Phase 2-b Text Fixer / Bulk Fixer 도움말 확장 (5개 언어)

### Changed
- Text Converter 구조 리팩토링 (Bulk Fixer 5:4 레이아웃 패턴 복제, 신규 클래스 `TextConverterDropZone`)
- Text Fixer / Bulk Fixer 설계 철학 분리 (사용자 동의 기반 vs 사후 투명성 기반)

### Fixed
- 설정 다이얼로그 번체 중국어 잔재 버그 (v1.0.5부터 존재)
- `toolTip` 오염 데이터 손실 버그 (v1.0.4부터 존재, `_PATH_ROLE` 신설로 해결)
- 헤더 정렬 버그 (v1.0.4부터 존재, `setSectionsClickable(True)` 명시)
- `alchemy_detect_encoding` 폴백 신뢰도 0.0 → 0.7

### Performance
- 위치 추적 알고리즘 O(N×K) → O(N) 재설계 (수백~수천 배 개선, 36GB 규모 실측)
- 미리보기 대용량 파일 32KB 추출 (800배 개선)

### Documentation
- README 구조 재설계: 3-파일 구조로 분리 — `README.md` (한국어 슬림) / `README_EN.md` (영어) / `docs/STORY.md` (한국어 서사·철학)
- About 섹션 영어 단독화 + Topics 12개 지정
- 주요 특징 불릿 7개 → 4개 압축

### Removed
- `MergeDragList` 데드 코드 57줄 (v1.0.3/1.0.4 `MergeFileTree` 교체 후 미사용)
- AppSuite 데드 메서드 3개 74줄 (`_page_language` / `_on_lang_selected` / `_retranslate_dialog`)

### Tests
- **527 passing** (+25 vs v1.0.5), 57개 클래스, 실패·오류·스킵 0

상세: [`RELEASE_NOTE_v1.0.6.md`](./RELEASE_NOTE_v1.0.6.md)

---

## [1.0.5] — —

### Added
- Text Merger 저장 인코딩 드롭다운 연관 언어 병기 (예: `Shift-JIS (일본어)`)
- 드롭다운 아래 한 줄 도움말 라벨 (`merge_enc_hint`)

### Changed
- 표시 라벨과 내부 키 분리 (`addItem(display, userData)` 패턴, v1.0.4 이하 설정 파일 자동 호환)

### Fixed
- 언어 전환 시 Text Merger 상태 메시지가 한국어로 남던 기존 버그 (v1.0.4 이전부터 존재)
  - `_retranslate_status()` 헬퍼 + 정규식 매칭 유틸 신설
  - 9종 상태 메시지 모두 적용 (정적 5 / 복원가능 2 / 복원불가 3)

### Removed
- 번역 사전 중복 키 74개 일괄 정리 (AST 값 동일성 검증 후 삭제, 동작 영향 0)
  - `zh_cn` 69개 + `ko`/`en`/`zh_tw` 각 1개 + `ja` 2개

### Security
- **SSH 서명 도입** — 커밋 + 태그 모두 Ed25519로 서명, GitHub Verified 뱃지 복귀
  - Fingerprint: `SHA256:4H2f7lrFfI4u0YP0dpp6N9BQH2f74iKjjMRHu7lyjKI`

### Tests
- **502 passing** (+30 vs v1.0.4)

상세: [`RELEASE_NOTE_v1.0.5.md`](./RELEASE_NOTE_v1.0.5.md)

---

## [1.0.4] — —

### Added
- Text Merger 저장 인코딩 3종 추가: Shift-JIS / GBK / Big5 (5개 지원 언어와 일치)
- UnicodeEncodeError 사전 경고 다이얼로그 (깨질 문자 종류·총 글자 수·파일 비율 3단 표시)
- 신뢰도 % 4단계 색상 코딩 (🟢≥90% / 🟡≥70% / 🟠≥50% / 🔴<50%)
- CJK 인코딩 배지 색상 추가 (🌸 Shift-JIS / 🟡 GBK / 🩵 Big5)

### Changed
- 인코딩 감지 함수 통합 (`alchemy_detect_encoding` 시그니처 `str` → `(str, float)` 튜플)
- Text Merger 자체 `_detect_encoding` 제거 → alchemy로 통합
- 읽는 바이트 8192 → 32768

### Fixed
- 경고 다이얼로그 HTML 태그 렌더링 실패 (`rich_text=False` 파라미터 도입)
- ASCII 도입부 CJK 파일 인코딩 오판정 (`cp949 → shift_jis → gbk → big5` 순차 폴백)
- 경고 다이얼로그가 실제 손실 규모를 1/10로 축소 표현하던 문제

### Tests
- **472 passing** (+21 vs v1.0.3)

상세: [`RELEASE_NOTE_v1.0.4.md`](./RELEASE_NOTE_v1.0.4.md)

---

## [1.0.3] — —

### Fixed
- **Text Fixer / Bulk Fixer UTF-16 LE/BE 파일 깨짐** (10개 케이스 영향, 5개 언어 × 2개 인코딩)
- 일본어 Shift-JIS / 중국어 GBK / 번체 Big5 파일이 `latin-1` 폴백으로 깨지던 문제
- `alchemy_detect_encoding()` CJK 인코딩 감지 실패 (chardet 0.5~0.7 신뢰도가 0.7 임계값에 막힘)

### Changed
- 3곳의 하드코딩된 인코딩 목록을 `alchemy_detect_encoding()` 하나로 통일
- `latin-1` 폴백 제거 (잘못된 디코딩 "성공" 방지)
- `shift_jis`, `gbk`, `big5` 폴백 추가 + CJK 화이트리스트 (임계값 0.5로 완화)

### Tests
- 인코딩 회귀 방지 테스트 15개 추가 (5개 언어 × 5개 인코딩 = 25개 샘플 실측)
- **수정 전 13/25 (52%) → 수정 후 25/25 (100%)**

상세: [`RELEASE_NOTE_v1.0.3.md`](./RELEASE_NOTE_v1.0.3.md)

---

## [1.0.2] — —

### Fixed
- Tag Editor 종료 보호 누락 (폴더 스캔 중 X/Alt+F4 시 확인 팝업 미표시)
- 중국어 UI Bulk Fixer 설명 라벨이 한국어로 노출 (`bulk_save_desc` 키 누락)
- TXT → EPUB 변환 시 첫 줄이 챕터 제목·본문에 중복 표시

### Changed
- bare `except:` 5건 → 0건 (Qt 시그널 disconnect 패턴 명시화)
- 미사용 import / 변수 5건 제거
- pyflakes 경고 5 → 0

상세: [`RELEASE_NOTE_v1.0.2.md`](./RELEASE_NOTE_v1.0.2.md)

---

## [1.0.1] — 2026-04-14

### Fixed
- 한국어 하드코딩 ~100곳 `_t()` 교체 (영문/일본어/중국어 모드 한국어 노출 해소)
- 인코딩 감지 전면 개선 (chardet 기반 `alchemy_detect_encoding`, UTF-8 3단계 판별)
- UTF-8(BOM) 파일이 LATIN-1로 오감지되어 깨지는 문제
- 저장 시 항상 UTF-8 변환 → 원본 인코딩 보존 (65MB → 125MB 비정상 증가 해소)
- 저장 다이얼로그 기본 경로 앱 폴더 → Output 폴더
- `QPlainTextEdit` 라운드 모서리 / 진행 바 스타일 통일 / 콤보박스 잘림
- Ctrl+F 검색 도움말 추가 (5개 언어)

### Added
- 번역 키 6개 × 5개 언어

상세: [GitHub Releases v1.0.1](https://github.com/MerciHanrim/FileNexusSuite/releases/tag/v1.0.1)
