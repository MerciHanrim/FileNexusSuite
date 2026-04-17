## v1.0.2 — 종료 보호 누락 + 중국어 번역 누락 + EPUB 챕터 중복 수정 / Close-Guard Fix + Chinese Translation Fix + EPUB Chapter Fix

### 버그 수정 / Bug Fixes
- **Tag Editor 종료 보호 누락** — 폴더 스캔 진행 중 X 버튼/Alt+F4 종료 시 "작업 중 종료 확인" 팝업이 뜨지 않던 문제 / Fixed Tag Editor not showing busy-confirmation dialog when closing during folder scan
  - `TagEditorPanel.is_busy()` 메서드 추가 + `closeEvent` busy 체크 리스트에 `_tag_panel` 포함 / Added `is_busy()` method to TagEditorPanel and registered it in `closeEvent` busy check
  - 다른 5개 패널과 동일한 종료 보호 동작 확보 / Now matches the close-guard behavior of the other 5 panels
- **중국어 UI Bulk Fixer 설명 라벨 한국어 노출** — `bulk_save_desc` 키가 zh_cn / zh_tw 사전에서 누락되어 한국어 원문이 표시되던 문제 / Fixed `bulk_save_desc` label showing Korean text in Chinese (Simplified/Traditional) UI due to missing translation keys
  - 영향 위치: Bulk Fixer 패널 저장 모드 설명 라벨 (`_lbl_save_desc`) / Affected: Bulk Fixer save-mode description label
- **TXT → EPUB 챕터 제목 본문 중복** — 첫 줄을 챕터 제목으로 자동 인식할 때 본문에도 같은 줄이 남아 `<h1>` + 첫 단락이 중복 표시되던 문제 / Fixed TXT → EPUB conversion duplicating the first line as both heading and first paragraph
  - 첫 줄을 제목으로 채택한 경우 본문에서 자동 제거 / Title line is now removed from body content when adopted as chapter heading

### 코드 위생 / Code Hygiene
- **bare `except:` 좁힘** — `TextFixerPanel._start_keep_top()`의 Qt 시그널 disconnect 패턴을 `except (RuntimeError, TypeError):`로 명시화 / Narrowed bare `except:` clauses in Qt signal disconnect pattern
- **무의미한 `replace()` 체인 제거** — `TextConverterPanel.retranslate`의 `replace('epub2txt','epub2txt').replace('txt2epub','txt2epub')` 단순화 / Simplified meaningless `replace().replace()` chain
- **미사용 import / 변수 5건 제거** — `QListWidgetItem`, 중복 `import math`, 미사용 지역변수, `from itertools import chain`, placeholder 없는 f-string / Removed 5 unused imports/variables flagged by pyflakes

### 번역 / Translation
- 신규 키 1개 × 2개 언어 / 1 new key × 2 languages: `bulk_save_desc` (zh_cn, zh_tw)
- ko / en / ja는 v1.0.1부터 정의되어 있던 키 / Already defined in ko / en / ja since v1.0.1

### 알려진 이슈 / Known Issues
- `zh_cn` 사전에 188개 키가 두 블록에 걸쳐 중복 정의되어 있음 — 모든 중복 키가 같은 값이라 동작에 영향 없음, 향후 정리 예정 / `zh_cn` dictionary has 188 keys duplicated across two blocks (all with identical values, no functional impact) — cleanup planned

### 검토 / Review
- Claude Opus 4.7 기반 정적 분석 + 비즈니스 로직 검토 / Reviewed with Claude Opus 4.7 (static analysis + business logic audit)
- pyflakes 경고 / pyflakes warnings: 5 → 0
- bare `except:` 사용 / bare `except:` usages: 2 → 0
