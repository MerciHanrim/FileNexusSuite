## v1.0.1 — 다국어 UI 수정 + 인코딩 수정 / Multilingual UI Fix + Encoding Fix

### 버그 수정 / Bug Fixes
- **한국어 하드코딩 ~100곳 `_t()` 교체** — 영문/일본어/중국어 모드에서 한국어 노출 문제 해결 / Fixed Korean text appearing in English/Japanese/Chinese UI modes
  - Batch Renamer, Text Converter, Tag Editor, Text Merger, MainWindow
- **인코딩 감지 전면 개선** — Text Fixer · Bulk Fixer의 인코딩 감지를 chardet 기반(`alchemy_detect_encoding`)으로 교체 / Encoding detection overhauled with chardet-based detection
  - UTF-8(BOM) 파일이 LATIN-1로 오감지되어 글자가 깨지는 문제 해결 / Fixed UTF-8(BOM) files being misdetected as LATIN-1
  - 3단계 UTF-8 판별: BOM 확인 → 엄격 디코딩 → 허용오차(1% 미만) / 3-step UTF-8 detection: BOM → strict decode → error tolerance (<1%)
  - latin-1/ISO-8859 계열 오감지 차단 / Blocked false-positive latin-1/ISO-8859 detection
- **원본 인코딩 보존 저장** — 저장 시 항상 UTF-8로 변환하던 방식 → 원본 인코딩 유지 / Save now preserves original encoding instead of forcing UTF-8
  - 파일 용량 비정상 증가(65MB→125MB) 문제 해결 / Fixed abnormal file size inflation
- **저장 다이얼로그 기본 경로** — 앱 폴더 → Output 폴더로 수정 / Save dialog now opens Output folder (Text Merger, Text Fixer)
- **QPlainTextEdit 라운드 모서리** — `make_style()`에 CSS 규칙 추가 / Added CSS rule for rounded corners
- **진행 바 스타일 통일** — Text Converter를 Bulk Fixer 기준으로 통일 / Text Converter now matches Bulk Fixer style
- **콤보박스 잘림 수정** — Merge Mode (→160px), Preset (→140px) / Combo box clipping fixed
- **영문 옵션 라벨 단축** — Merge lines / Insert blanks / Reduce blanks / English option labels shortened
- **Ctrl+F 검색 도움말 추가** — Text Fixer 섹션 + 단축키 (5개 언어) / Ctrl+F search help added

### 번역 / Translation
- 신규 키 6개 × 5개 언어 / 6 new keys × 5 languages: `batch_click_preview`, `batch_parent_folder`, `batch_folder_label`, `batch_confirm_items`, `batch_done_items`, `dlg_rename_partial_note`

### 도구 / Tools
- `build_pyinstaller.py` — UPX 제외 대상 DLL 추가 / Added UPX exclude for `python3.dll` etc.
- `preview_ui.py` — 영문 라벨 통일, 진행 바 스타일 통일 / English labels, progress bar style unified
