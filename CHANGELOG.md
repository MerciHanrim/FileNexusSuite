# Changelog

본 프로젝트의 주요 변경사항을 버전별로 기록합니다.

각 버전의 코드 변경 상세는 [`RELEASE_NOTE_vX.X.X.md`](./) 파일을 참조하세요.
포맷은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/)를 따릅니다.

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
