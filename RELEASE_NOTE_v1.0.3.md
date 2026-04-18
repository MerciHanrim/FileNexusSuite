# v1.0.3 — 인코딩 감지 버그 수정 / Encoding detection bug fix

Text Fixer와 Bulk Fixer가 UTF-16 / Shift-JIS / GBK / Big5 인코딩 파일을 처리할 때 깨진 채 저장되던 버그를 수정했습니다. 5개 지원 언어 전체에서 모든 주요 인코딩이 정상 처리됩니다.

> Fixed a bug where Text Fixer and Bulk Fixer saved corrupted output for UTF-16 / Shift-JIS / GBK / Big5 encoded files. All major encodings are now handled correctly across all 5 supported languages.

---

### 버그 수정 / Bug Fixes

- **UTF-16 LE/BE 파일 깨짐** / UTF-16 LE/BE files corrupted
  - Text Fixer (파일 로드), Bulk Fixer (일괄 처리 및 미리보기)에서 발생
  - Triggered in Text Fixer (file load), Bulk Fixer (batch processing & preview)
  - 5개 언어 × 2개 UTF-16 인코딩 = 10개 케이스 영향
  - Affected 10 cases: 5 languages × 2 UTF-16 encodings

- **일본어 Shift-JIS / 중국어 GBK / 번체 Big5 파일 깨짐** / Japanese Shift-JIS, Chinese GBK, Traditional Chinese Big5 files corrupted
  - 3개 CJK ANSI 인코딩 파일이 디코딩 실패 후 `latin-1`로 강제 디코딩되어 깨짐
  - These 3 CJK ANSI encoded files were falling back to `latin-1`, producing corrupted output

- **`alchemy_detect_encoding()`의 GBK/Big5/Shift-JIS 감지 실패** / Encoding detector failed for GBK/Big5/Shift-JIS
  - chardet이 CJK 인코딩에 자주 0.5~0.7 신뢰도를 반환 → 기존 0.7 임계값에 막힘
  - chardet often returns 0.5~0.7 confidence for CJK encodings, blocked by 0.7 threshold
  - 수정: CJK 인코딩은 0.5 이상이면 신뢰, 기타는 0.7 유지
  - Fix: CJK encodings trusted at ≥0.5, others keep 0.7 threshold

### 코드 변경 / Code Changes

- 3곳의 하드코딩된 인코딩 목록을 기존 `alchemy_detect_encoding()` 함수로 통일
  - Unified 3 hardcoded encoding lists to use the existing `alchemy_detect_encoding()` function
- `latin-1` 폴백 제거 (잘못된 디코딩 "성공" 방지)
  - Removed `latin-1` fallback (which masked encoding errors)
- `shift_jis`, `gbk`, `big5` 폴백 추가 (5개 지원 언어 일치)
  - Added `shift_jis`, `gbk`, `big5` fallbacks (matching 5 supported languages)
- `alchemy_detect_encoding()` 개선: CJK 인코딩 화이트리스트 + 임계값 완화 + 이름 정규화
  - Improved `alchemy_detect_encoding()`: CJK whitelist + relaxed threshold + name normalization

### 테스트 / Testing

- 인코딩 회귀 방지 테스트 15개 추가 / Added 15 encoding regression tests
  - `TestBulkFixerFileIO`: 라운드트립 5개 / roundtrip tests × 5
  - `TestV103Regression`: 소스 검증 7개 / source-level checks × 7
  - `TestV103RegressionModule`: 모듈 검증 3개 / module-level checks × 3

### 검증 범위 / Verification Scope

- 5개 언어 × 5개 인코딩 = 25개 테스트 파일 / 25 test files (5 languages × 5 encodings)
  - 한국어·English·日本語·简体中文·繁體中文
  - UTF-8 / UTF-8 BOM / UTF-16 LE / UTF-16 BE / ANSI (각 언어별)
- **수정 전** / Before: 13/25 (52%)
- **수정 후** / After: **25/25 (100%)** ⭐
- 2종 프리셋(Normal, Novel) 모두 동일 결과 / Identical results for both Normal and Novel presets

### 알려진 이슈 / Known Issues

- `zh_cn` 사전 188개 키 중복 (동작 영향 없음, v1.0.2부터 식별)
  - 188 duplicate keys in `zh_cn` dictionary (no runtime impact, identified in v1.0.2)
  - 향후 별도 리팩토링 PR로 분리 예정 / Will be addressed in a separate refactoring PR
