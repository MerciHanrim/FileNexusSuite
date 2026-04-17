# File Nexus Suite — 변경 내역

## v1.0.2 (2026-04-17) — Opus 4.7 검토 기반 버그 수정 + 코드 위생

### 버그 수정

- **Tag Editor 폴더 스캔 중 종료 시 경고 누락** (`L13277`, `L6212~6214`)
  - 폴더를 드래그 & 드롭한 직후 `_scan_worker` 가 실행 중일 때 X 버튼/Alt+F4 로 종료해도
    "작업 중 종료 확인" 다이얼로그가 뜨지 않고 즉시 종료되던 문제
  - 원인: `AppSuite.closeEvent()` 의 busy_panels 체크 리스트에 `_tag_panel` 누락
    + `TagEditorPanel` 에 `is_busy()` 메서드 자체가 없었음
  - 수정:
    1. `TagEditorPanel.is_busy()` 추가 (`return bool(self._scan_worker and self._scan_worker.isRunning())`)
    2. `closeEvent` busy_panels 리스트에 `('_tag_panel', 'Tag Editor')` 추가
  - 다른 5개 패널(Text Merger, Text Converter, Text Fixer, Bulk Fixer)과 동일한 종료 보호 동작 확보

- **중국어 UI 에서 Bulk Fixer 저장 옵션 설명이 한국어로 표시** (`L2422`, `L2756`)
  - `bulk_save_desc` 번역 키가 zh_cn / zh_tw 사전에서 누락되어
    `_t()` fallback 으로 한국어 원문이 그대로 표시되던 문제
  - 영향 위치: Bulk Fixer 패널 저장 모드 설명 라벨 (`_lbl_save_desc`, L8460)
  - 수정: 간체·번체 번역 추가
    - zh_cn: `'在文件名前加 [Fixed] 标签保存。如未指定输出文件夹，将保存在原文件相同位置。'`
    - zh_tw: `'在檔案名前加 [Fixed] 標籤儲存。如未指定輸出資料夾，將儲存在原檔案相同位置。'`

- **TXT → EPUB 변환 시 챕터 제목 본문 중복** (`txt_to_epub`, `L3559~3564`)
  - 첫 줄을 챕터 제목으로 자동 인식할 때, 본문에는 그 줄이 그대로 남아 있어서
    EPUB 리더에서 `<h1>제목</h1>` 다음 첫 단락에 같은 제목이 한 번 더 표시되던 문제
  - 수정: 첫 줄을 제목으로 채택한 경우 `p = "\n".join(lines[1:]).lstrip("\n")` 으로 본문에서 제거
  - 빈 제목인 경우는 기본 제목(`Chapter N`) 유지 + 본문 보존

### 코드 위생

- **bare `except:` 좁힘** (`L7277`, `L7287`)
  - `TextFixerPanel._start_keep_top()` 의 Qt 시그널 disconnect 패턴
  - `except:` → `except (RuntimeError, TypeError):` 로 명시화 (PEP-8 권장)
  - 동작 동일 — 의도하지 않은 예외 삼키기 방지

- **무의미한 `replace()` 체인 제거** (`TextConverterPanel.retranslate`, `L5806`)
  - `_t('conv_sub_'+val.replace('epub2txt','epub2txt').replace('txt2epub','txt2epub'))`
  - 같은 문자열로 replace 하는 명백한 잘못된 코드 — `_t('conv_sub_' + val)` 로 단순화

- **미사용 import / 변수 정리** (5건)
  - `L58`: `QListWidgetItem` 미사용 import 제거
  - `L3725`: `_ScrollHint.__init__` 의 `import math as _math` 제거 (`_tick` 메서드에서 별도 import 함)
  - `L5673~5674`: `_on_file_progress` 의 미사용 지역변수 `total`, `done` 제거
  - `L8779`: `BulkFixerPanel.retranslate` 의 미사용 `from itertools import chain` 제거
  - `L13161`: placeholder 없는 f-string `f"File Nexus Suite"` → 일반 문자열로

### 번역

- 신규 번역 키 1개 × 2개 언어: `bulk_save_desc` (zh_cn, zh_tw)
- ko / en / ja 는 기존 v1.0.1 부터 정의되어 있던 키

### 알려진 이슈 (미수정 — 동작에 영향 없음)

- `zh_cn` 사전이 두 블록(L2013~L2204, L2204~L2462)으로 나뉘어 188 개 키가 중복 정의되어 있음
  - 모든 중복 키가 같은 값으로 정의되어 있어 ast.literal_eval 결과는 정상 (379 개 키)
  - 향후 사전 정리 PR 별도 진행 권장 (회귀 위험으로 v1.0.2 범위에서는 제외)
- `merge_open_explorer` 키가 ko / en / ja / zh_cn / zh_tw 모두에서 1 회씩 중복 (값 동일)
- `ja` 의 `bulk_keep_structure` 키가 1 회 중복 (L1921 → L1922, 값 동일)

### 내부 / 빌드

- `APP_VERSION` `1.0.1` → `1.0.2`
- 단일 파일 라인 수: 13,681 → 13,689 (+8)
- pyflakes 경고: 5 건 → **0 건**
- bare `except:`: 2 건 → **0 건**

### 검토 방법

- Claude Opus 4.7 (Anthropic) 기반 정적 분석 + 비즈니스 로직 검토
- AST 파싱, pyflakes, 정규식 패턴 검색, 번역 키 정합성 검증

---

## v1.0.1 (2026-04-14) — 다국어 UI 수정 + 인코딩 수정

### 버그 수정
- **한국어 하드코딩 전수 교체** (~100곳) — 영문/일본어/중국어 모드에서 한국어가 노출되던 문제 해결
  - Batch Renamer: 버튼, 테이블 헤더, GroupBox, RadioButton, QLabel, QFileDialog, 에러 메시지, 확인/결과 다이얼로그 (~55곳)
  - Text Converter: GroupBox, 버튼, 라벨, QCheckBox, 콤보 아이템 (~15곳)
  - Tag Editor: 헤더, 필터, 라벨, RadioButton, QCheckBox (~20곳)
  - Text Merger: 저장 설정, QCheckBox, 경로 버튼, 완료 메시지 (~10곳)
  - 기타: MainWindow 헤더, First Run 이전/다음, 드롭존 호버 (~5곳)
- **Text Merger 저장 다이얼로그 기본 경로** — 앱 폴더 → Output 폴더로 수정
- **Text Fixer [Fixed] 저장 기본 경로** — 앱 폴더 → Output 폴더로 수정
- **QPlainTextEdit 라운드 모서리 누락** — `make_style()`에 CSS 규칙 추가
- **Text Converter 진행 바 통일** — Bulk Fixer 기준 (8px + 5px, 모노스페이스)
- **Merge Mode 콤보박스 잘림** — `setFixedWidth(100)` → 160px
- **Preset 콤보박스 잘림** — Bulk Fixer `setFixedWidth(120)` → 140px
- **영문 옵션 라벨 단축** — Merge lines / Insert blanks / Reduce blanks — max
- **Text Fixer Ctrl+F 검색 도움말 추가** (5개 언어, tip + 단축키 섹션)
- **드롭존 "지원" 하드코딩** — `_t('merge_ext_supported')` 교체
- **인코딩 감지 전면 개선** — `alchemy_detect_encoding()` chardet 기반으로 교체
  - UTF-8(BOM) → LATIN-1 오감지 문제 해결 (글자 깨짐 + 파일 용량 2배 증가)
  - 3단계 UTF-8 판별: BOM → 엄격 디코딩 → 허용오차(1% 미만)
  - latin-1/ISO-8859 계열 오감지 차단
  - 샘플 크기 8KB → 64KB 확대
- **원본 인코딩 보존 저장** — Text Fixer · Bulk Fixer 저장 시 UTF-8 고정 → 원본 인코딩 유지
- **Bulk Fixer 프리뷰 인코딩** — `alchemy_detect_encoding()` 적용, latin-1 fallback 제거
- **파일 선택 다이얼로그 타이틀 하드코딩** — `_t()` 교체

### 번역
- 신규 번역 키 6개 × 5개 언어: `batch_click_preview`, `batch_parent_folder`, `batch_folder_label`, `batch_confirm_items`, `batch_done_items`, `dlg_rename_partial_note`

### 도구
- `preview_ui.py` — 영문 라벨 통일, 진행 바 Bulk Fixer 스타일로 통일
- `build_pyinstaller.py` — UPX 제외 대상 DLL 추가 (`python3.dll` 등)

---

## v1.0.0 (2026-04-13) — 정식 릴리즈

### 기능 추가
- **Output 폴더 전역 설정** — 설정 → 일반 설정에서 출력 폴더를 전역으로 지정. Text Converter·Bulk Fixer·Text Fixer에 공통 적용
- **저장 완료 후 폴더 자동 열기** — Text Converter·Bulk Fixer·Text Fixer 저장 완료 시 결과 폴더 자동 오픈
- **Bulk Fixer 폴더 드롭 지원** — 폴더를 드래그하면 하위 `.txt` 파일 재귀 수집
- **Bulk Fixer 폴더 구조 유지 옵션** — 출력 폴더 지정 시 원본 폴더 구조 재현 (`_chk_keep_structure`)
- **Bulk Fixer 프리셋** — 일반 문서 / 책·소설 (Text Fixer와 동일)
- **도움말 버튼 애니메이션** (`_HelpButton`) — 호버 시 위로 살짝 올라갔다 돌아오는 사인파
- **설정 버튼 애니메이션** (`_GearButton`) — 호버 시 시계 방향 회전, 아이콘 22px
- **스크롤 힌트 애니메이션** (`_ScrollHint`) — 사인파 이동(±3px) + 페이드 동시 연출, 삼각형 9×5px

### UI/UX 폴리싱
- **버전 표기** — 타이틀바 제거 → 헤더 subtitle 옆 + 설정창 사이드바 하단
- **설정 탭 구조 개편** — 테마 / 일반 설정(언어+출력폴더) / 단축키 / 라이선스
- **섹션 헤더 통일** — `//` 슬래시 스타일로 전 탭 통일 (5개 언어)
- **`grp_title_lbl` 전역 스타일** — `QLabel#grp_title_lbl` CSS 추가 (MUTED + 11px + 700 + letter-spacing 1.2px)
- **Text Fixer 섹션 레이블** — `QGroupBox` → `QLabel(grp_title_lbl)` + `QWidget` 구조로 교체
- **Bulk Fixer abort 버튼** — "실행 취소" → "중단" (`btn_abort` 키 분리, 5개 언어)
- **Bulk Fixer 프로그레스 바** — 바 아래 우측 정렬 텍스트, 모노스페이스 폰트, 퍼센트 고정폭
- **Text Converter 프로그레스 바 통일** — Bulk Fixer 기준으로 통일 (전체 8px + 파일 5px, opacity 0.7, 우측 정렬 모노스페이스)
- **폴더 지정 다이얼로그 기본 경로** — 전역 output_dir 기준으로 열림

### 버그 수정
- **Text Fixer 수정본 표시 버그** — `QTextEdit` → `QPlainTextEdit` 교체, 대용량(49만+줄) 렌더링 한계 해결
- **스크롤 리셋 문제** — `rangeChanged` 안정화 감지 후 `valueChanged`로 0 유지
- **언어 전환 번역 누락** — Bulk Fixer `_btn_abort`, `_chk_keep_structure`, `_combo_preset` retranslate 추가
- **QPlainTextEdit 라운드 모서리 누락** — `make_style()`에 `QPlainTextEdit` CSS 규칙 추가 (`border-radius:8px`, QTextEdit과 동일)

### 번역
- 신규 번역 키 (5개 언어): `btn_abort`, `bulk_keep_structure`, `settings_output_dir`
- 도움말 최신화 (5개 언어): Text Fixer/Bulk Fixer 저장 방식, Output 폴더 설명, Batch Renamer
- Text Fixer **Ctrl+F 검색** 도움말 추가 (5개 언어, Text Fixer tip + 단축키 섹션)

### 테스트
- QPlainTextEdit mock 추가 (PySide6 미설치 환경 모듈 exec 실패 수정)
- BulkFixerWorker API 변경 반영: `save_mode` 제거 → `out_dir` + `keep_structure`
- `TestV100Regression` (소스 파싱 기반, 15개) 추가
- `TestV100RegressionModule` (모듈 로드 기반, 7개) 추가
- `TranslationCompleteness`에 v1.0.0 신규 키 검증 추가
- `RetranslateIntegrity`에 `_btn_abort` / `_chk_keep_structure` retranslate 검증 추가
- `TestBulkFixerFileIO`에 `test_keep_structure_creates_subdirs` 추가
- 411 → **436개** 전체 통과

### 도구
- `preview_ui.py` v1.0.0 최신화
  - `_HelpButton` / `_GearButton` / `_ScrollHint` 애니메이션 미리보기 추가
  - `SettingsDialog` (일반 설정 탭) 미리보기 추가
  - Bulk Fixer 2단 프로그레스 바 (전체 8px + 파일 5px, 우측 정렬 모노스페이스) 미리보기 추가
  - 기존 진행 바 3개도 Bulk Fixer 스타일로 통일 (바 아래 우측 정렬 모노스페이스)
  - 전체 섹션/버튼 라벨 영문 코드명으로 변경 (언어 전환 시 깨짐 방지)

---

## v0.12.1 (2026-04-12) — 버그 수정 릴리즈

### 크래시 / 플랫폼 버그

- **`QByteArray` 미임포트** (`L63`)
  - `_svg_html_img()`에서 `QByteArray()` 사용 중 `NameError` 발생
  - `from PySide6.QtCore import ... QByteArray` 추가

- **Linux subprocess 분기 오류** (`L2859`)
  - crash 로그 폴더 열기 시 `open` 명령 사용 → macOS 전용, Linux에서 실패
  - `sys.platform == "linux"` 분기 추가, `["xdg-open", _log_dir]` 사용

- **`locale.getdefaultlocale()` deprecated** (`L3128`)
  - Python 3.11+에서 DeprecationWarning 발생, 미래 버전 제거 예정
  - `locale.getlocale()` 우선 사용 + `getdefaultlocale()` fallback 유지

- **PyInstaller 빌드 후 한국어 환경에서 영문 실행** (`L3171` `_detect_os_lang`)
  - 원인: PyInstaller 환경에서 `locale.getlocale()`이 `'ko_KR'` 대신
    `'Korean_Korea'`(Windows 내부 형식)를 반환 → `startswith('ko')` 매칭 실패 → `'en'` 반환
  - 수정: `_detect_os_lang()` 3단계 우선순위로 재작성
    1. Windows 레지스트리 `Control Panel\International` → `LocaleName` 직접 읽기
       (`'ko-KR'` 반환 → `replace('-','_')` → `'ko_KR'` → 정상 매칭)
    2. `locale.getlocale()` fallback
    3. `locale.getdefaultlocale()` fallback
  - `winreg`는 기존 `_detect_system_theme()`에서도 동일하게 사용 중

### UI 오작동

- **TagEditorPanel 파일 추가·폴더 추가 버튼 아이콘 미표시** (`L5201~5204`)
  - `_btn_add_files`, `_btn_add_folder`에 `setObjectName()` 누락
  - QSS `#btn_primary`·`#btn_folder_add` 미적용 → 기본 밝은 배경에 흰 아이콘 = 투명
  - `setObjectName("btn_primary")`, `setObjectName("btn_folder_add")` 추가

- **미리보기 버튼 돋보기 아이콘 미표시** (Batch Renamer, Tag Editor)
  - `btn_preview` QSS: `background:SURFACE`(밝음) — `'white'` 아이콘 사용 → 흰 배경에 흰 아이콘
  - `_svg_icon_dual(key, normal_color, active_color)` 헬퍼 신규 추가 (`L297`)
  - Normal 상태: `ACCENT` 색, Active(hover) 상태: `'white'` 색
  - `refresh_btn_styles()`에 preview 아이콘 갱신 추가 (BatchRenamer, TagEditor)

- **확인 다이얼로그 "예"/"아니오" 버튼 크기 불일치**
  - "예"(1글자)와 "아니오"(3글자) 텍스트 길이 차이로 동일 padding에도 크기 달라짐
  - `_btn_style()`에 `min-width:80px` 추가
  - `_dlg_question()`, `_dlg_info_action()`: `dlg.show()` 후 `sizeHint().width()` 기반 너비 동기화

### 번역 누락 (15곳)

- **TextFixerPanel 저장 메뉴 액션 초기값** (`L6228~6232`)
  - `addAction('원본에 덮어쓰기')` 등 3개 → `_t('tf_save_overwrite')` 등으로 교체

- **QFileDialog 타이틀 4곳**
  - `TextFixerDropZone.mousePressEvent` (`L5947`): `'텍스트 파일 열기'` → `_t('tf_open')`
  - `TextFixerPanel._open_file()` (`L6382`): 동일
  - `TextFixerPanel._save_as()` (`L6548`): `'다른 이름으로 저장'` → `_t('tf_save_as')`
  - `TextConverterPanel._add_files()`, `_browse_out()`: 각각 `_t()` 교체

- **TextMergeWorker error.emit 제목** (`L7708~7710`)
  - `"라이브러리 오류"`, `"파일 오류"` → `_t('dlg_error_title')` + 파일명 기반 메시지

- **undo 완료 팝업 메시지 3곳**
  - BatchRenamer `_undo()` (`L3925`), TextConverter `_undo()` (`L5037`), TagEditor `_undo()` (`L5656`)
  - `f"실행 취소 완료: {n}개 복구"` → `_t('tag_apply_done', n=..., label=_t('dlg_undo'))`

- **TextConverter `_on_done` 완료 팝업** (`L4995~4996`)
  - `f"✅  {label} 변환 완료\n\n성공: {ok}개"` → `_t('bulk_status_done')` + `_t('dlg_done_err')` 조합

- **BulkFixerPanel `_on_done` fail 카운트** (`L7545`)
  - `f'  ({fail} failed)'` → `f'  {_t("dlg_done_err")} ×{fail}'`

- **BulkFixerWorker 인코딩 오류 메시지** (`L7087`)
  - `raise OSError('인코딩 감지 실패')` → `raise OSError(_t('tf_err_enc'))`

- **버튼 텍스트 다수** (TagEditor, TextConverter, BatchRenamer)
  - `_btn_add_files`, `_btn_add_folder`, `_btn_del_all`, `_btn_del_sel` 등 하드코딩 → `_t()` 교체

### 로직 버그

- **`retranslate()` status 비교 하드코딩** (3곳)
  - TextMerger, TextConverter, TagEditor `retranslate()` 내 status 레이블 비교 시
    각 언어 문자열을 배열로 하드코딩하던 방식 → 언어 추가 시 깨짐
  - `_all_translations_of(key)` 헬퍼 신규 추가 (`L774`)
    ```python
    def _all_translations_of(key: str) -> set:
        return {v.get(key, '') for v in TRANSLATIONS.values()
                if isinstance(v, dict) and v.get(key)}
    ```

### 빌드 파일

- **`build_pyinstaller.py` `--version-file` 옵션 누락**
  - `version_info.txt` 존재하나 빌드 명령에 미전달 → Windows 파일 속성 미반영
  - `--version-file version_info.txt` 추가 + `check_version_file()` 단계 추가

- **`build_pyinstaller.py` hidden imports 현행화**
  - 제거: `ebooklib`, `bs4`, `lxml` (코드에서 미사용)
  - 추가: `pdfplumber`, `docx`, `openpyxl`, `PySide6.QtSvg`

- **`version_info.txt`** `0.10.1.0` → `0.12.1.0`

- **`requirements.txt` 선택 의존성 누락**
  - `pdfplumber`, `python-docx`, `openpyxl` 추가

### 테스트

- `TestV012Regression` (소스 파싱 기반, 18개) 추가
- `TestV012RegressionModule` (모듈 로드 기반, 13개) 추가
- 384 → **411개** 전체 통과

---

## v0.12.0 (2026-04-12) — 세션 12

### SVG 아이콘 시스템 전면 구축

- `_SVG_PATHS: dict` — Filled 스타일 (17개 키, 24×24 viewBox path 데이터)
  - Primary 버튼용: `document`, `folder_open`, `folder`, `tag`, `refresh`, `wrench`,
    `magnifier`, `save`, `trash`, `broom`, `check`, `clipboard`, `arrow_up`, `arrow_down`,
    `question`, `list`, `info`
- `_SVG_LINE_ICONS: dict` — Line/Outline 스타일 (14개 키, `{color}` 플레이스홀더)
  - 탭·헤더·설정 nav용: `document_line`, `folder_open_line`, `tag_line`, `folder_line`,
    `wrench_line`, `broom_line`, `gear_line`, `question_line`, `theme_line`,
    `globe_line`, `keyboard_line`, `license_line`, `info_line`, `bell_line`
- `_svg_icon(key, color, size)` 함수
  - 2× 해상도 렌더링 (`QPixmap(size*2, size*2)` + `setDevicePixelRatio(2)`)
  - `'white'` 지정 시 `QIcon.Mode.Disabled` 픽스맵(MUTED 색) 자동 추가
  - `_SVG_LINE_ICONS` 우선 조회 → 없으면 `_SVG_PATHS` fallback
  - `PySide6.QtSvg` 미설치 시 `QIcon()` 반환 (graceful fallback)
- `_svg_html_img()` — 미사용 상태로 보존 (드롭존 SVG 시도 흔적)

### 아이콘 색상 규칙 확립

| 버튼 종류 | 배경 | 아이콘 색 |
|---|---|---|
| Primary | ACCENT | `'white'` 고정 |
| Secondary | SURFACE | `ACCENT` (refresh_btn_styles에서 갱신) |
| 탭 | 투명 | `ACCENT` (apply_theme에서 갱신) |
| 헤더 (?·⚙) | 투명 | `TEXT` |
| 설정 nav | 투명 | `MUTED`→`ACCENT`(활성) |

### 다크 테마 버그 수정

- TextConverter `_combo_enc`·`_combo_lang`·`_combo_ch` `refresh_btn_styles` 누락 → 흰 배경 수정
- TextFixer drop zone `set_idle()` 잘못된 속성명 수정
- Text Merger drop zone 테마 미반영 수정
- 보조 버튼 border: `BORDER` → `BTN_BORDER_H` (대비 개선)

### Primary 버튼 disabled 스타일

- 변경 전: 회색 처리 (`DISABLED` 배경)
- 변경 후: ACCENT 40% 반투명 (`_hex_rgba(ACCENT, 0.4)`)
- Preview/Outline 버튼 disabled: `SRF2` 유지

### Bulk Fixer 탭 아이콘

- `broom` (filled) → `broom_line` (line) 교체
- 이유: 다른 탭 아이콘과 스타일 통일 (모두 line 스타일 사용)

### 번역 키 정리

- 아이콘이 적용된 버튼들의 이모지 전면 제거 (5개 언어)
- 도움말 버튼 참조 텍스트 갱신

### 로그 관리

- crash 로그 최대 보관: 20개 → **3개**
- 세션 로그: 정상 종료 시 자동 삭제 (`atexit` + `_cleanup_session_log()`)
- `_session_crashed` 플래그로 크래시 여부 판별

---

## v0.11.0 (2026-04-12) — 세션 11

### 신규 기능

#### UI/UX
- **최초 실행 팝업** (`_show_first_run_notice`)
  - 생성 파일 안내: `FileNexusSuite.json`, `Output/`, `logs/crash_*.log`
  - `--onedir` 빌드 감지 시 `_internal/` 삭제 경고 (빨간색)
  - UI 가이드: 💡 도움말 버튼, Batch Renamer 사용법 안내
  - config `first_run_shown: true` 저장으로 재표시 방지
- **작업 중 종료 확인** (`closeEvent`)
  - Text Merger, Text Converter, Text Fixer, Bulk Fixer 작업 중 X버튼/Alt+F4 시 팝업
  - 취소(기본값) / 종료(빨간색) 버튼
  - 각 패널에 `is_busy()` 메서드 추가

#### Bulk Fixer
- 파일 목록: `QListWidget` → `QTreeWidget` 2컬럼 (파일명 | 경로)
  - 헤더 클릭으로 파일명 정렬 (▲/▼ 표시)
  - 드래그 후 `_sync()` 자동 호출
- 버튼 레이아웃: Text Merger와 동일 구조
  - 상단: [파일 추가] [폴더 추가] / [전체 삭제]
  - 하단: [선택 삭제] [↑ 위로] [↓ 아래로]
- 폴더 스캔 비동기 처리 (`FolderScanWorker`)
  - 4px 진행 바 + "탐색 중... N개 발견" 라벨
  - 스캔 중 버튼 비활성화 + WaitCursor

#### 진행 바
- **2단 진행 바** (전체 + 현재 파일 세분화)
  - 전체 진행: 0~100%
  - 현재 파일: 읽기(20%) → 교정(20~80%, 단락마다 갱신) → 저장(85%) → 완료(100%)
- `_fix_text`에 `progress_cb` 파라미터 추가
  - `chunk = max(n_lines // 20, 500)` 단위로 emit

#### 폴더 스캔 비동기
- `FolderScanWorker` 범용화: `exts`, `recursive` 파라미터
- Text Merger: `_add_folder_dialog()` → 워커 + 4px 진행 바
- Tag Editor: `_add_files_from_folder()` → 워커 + 4px 진행 바
- Batch Renamer: WaitCursor (단층 os.listdir, 풀 워커 불필요)

#### 기본 출력 폴더
- `_OUTPUT_DIR = _app_dir() / "Output"` 모듈 레벨 정의
- 앱 시작 시 자동 생성
- Text Converter, Bulk Fixer 기본값으로 적용

#### 도움말
- Bulk Fixer 섹션 추가 (5개 언어)
- 생성 파일 안내 섹션 추가 (5개 언어, `_internal/` 경고 포함)
- 핵심 기능 수 5 → 6 갱신
- Text Converter 출력 폴더 기본값 안내 갱신
- Batch Renamer 접이식 사용법 섹션 (우측 패널 상단 `// 사용법 ▼`)

#### 라이선스
- `All Rights Reserved` → `Freeware — Free for Personal & Commercial Use`
- 설정 > 라이선스 탭 상단에 현지어 요약 배너 추가 (5개 언어)

### 번역 키 추가 (~40개, 5개 언어 각각)
`first_run_title`, `first_run_desc`, `first_run_item_*`, `first_run_tip`,
`first_run_ui_*`, `first_run_item_internal`, `close_busy_*`,
`license_summary`, `bulk_scanning`, `merge_no_files` 외

### 버그 수정
- `merge_no_files` 번역 키 미정의 (런타임 KeyError)
- `closeEvent` `_batch_panel._stop_worker()` 없는 메서드 호출 오류
- f-string 플레이스홀더 없는 경고 수정 (4건)
- 미사용 import: `QAction`, 로컬 `QFont`
- 미사용 변수: `full_html`, `sec_html`, `_app`, `_tmp_app`, `surface`, `cfg`, `feat_bg/bdr`
- 루프 내 반복 `QColor as _QC` import → 루프 밖으로 이동

### 최적화
- TagEditor `_refresh_file_list`: `setUpdatesEnabled(False/True)` 적용
- `_mx` 함수 불필요한 기본값 파라미터 제거

### 도구
- `preview_ui.py` 신규: UI 미리보기 도구
  - 테마/언어 실시간 전환
  - 팝업/다이얼로그/진행 바/아이콘 미리보기
  - 파일별 2단 진행 바 시뮬레이션

---

## v0.10.1 (이전 세션) — 세션 10

### 신규 기능
- 하드코딩 다이얼로그 타이틀/메시지 전수 번역 키 교체 (~35개 신규 키)
- Bulk Fixer Ctrl+6 단축키 등록
- Text Converter 도움말 절전 방지 안내

### 버그 수정
- `_excepthook` 재진입 방지 플래그 (`_excepthook_lock`)
- 시그널 누수 4건: ConvertWorker `sig_files.disconnect()` 누락 등
- `closeEvent` 워커 미정리 보완

### 테스트
- 384개 자동화 테스트 체계 완성
- PySide6 미설치 환경 Mock 시스템
