# File Nexus Suite — 변경 내역

## [Unreleased] — v1.0.6 최종 릴리즈 후보

> **📦 릴리즈 후보 상태** — 2026-04-21 오후 세션 완료 시점 반영. 릴리즈 시 날짜/제목 확정 예정.
> 현재 기준: `FileNexusSuite.py` **14,971줄** (v1.0.5 원본 13,886줄 대비 +1,085줄)
> **문서 이력**: 2026-04-21 오후, #7 Text Converter 리팩토링 + 설정 다이얼로그 번체 잔재 수정 + APP_VERSION 갱신 완료 반영. 상세 검증 내역은 `docs/archive/v1.0.6_Phase2_Completion_Record.md` 참조.

### 완료 — Text Merger 기능 강화

- **인코딩 자동 추천 (A1'' 정책)** — `merger_recommend_save_encoding()` 함수 추가 (`L4091` 부근)
  - 모든 텍스트 파일이 **같은 비유니코드 인코딩 + 신뢰도 ≥ 0.7** → 그 인코딩 추천, 그 외 UTF-8
  - UI: 드롭다운 아래 "💡 추천: XXX" 라벨 + [적용] 버튼
  - 5개 언어 번역 키 추가 (`merge_enc_recommend`, `merge_enc_recommend_apply`)
  - 자동 갱신 트리거 4곳 (파일 추가/선택삭제/전체삭제/언어전환)
  - 14/14 시나리오 회귀 테스트 통과

- **HWPX 입력 지원** — `python-hwpx 2.9.0` (MIT) 도입
  - lxml 5.4.0으로 자동 다운그레이드 발생 (경고만)
  - `import hwpx as _hwpx` + `HWPX_AVAILABLE` 플래그 추가
  - `_extract_text`에 `elif ext==".hwpx"` 분기 (`HwpxDocument.open(path).export_text()`)
  - 모든 분기 7곳에 `.hwpx` 추가 (SUPPORTED_EXT, TextMergeWorker, 파일 추가, 다이얼로그 필터 등)
  - MergeEncodingDelegate에 HWPX 배지 (#9B59B6 보라색)
  - HWP(구형) 감지 시 통합 안내 다이얼로그 (`{n}`개 카운트) — 5개 언어
  - `_dlg_warn`에 `rich_text` 파라미터 추가 (기본 False, 회귀 영향 0)
  - 도움말 5개 언어 모두에 HWPX pill 추가
  - LICENSE 화면에 python-hwpx 항목 추가

### 완료 — alchemy_detect_encoding 신뢰도 개선

- **폴백 루프 통과 시 신뢰도 0.0 → 0.7** (cp949/shift_jis/gbk/big5) (`L3676`)
- **utf-8 strict 폴백도 0.0 → 0.7** (일관성)
- 짧은 한글 CP949 파일 → "70% CP949" 배지 + "💡 추천: CP949" 정상 동작

### 완료 — toolTip 오염 버그 근본 수정 (v1.0.4부터 존재한 기존 버그)

- **증상**: 신뢰도 < 0.90 파일의 툴팁에 안내문이 덧붙어 `item.toolTip(0)` 기반 경로 조회 실패
  - 삭제한 파일이 병합 결과에 포함되는 데이터 손실 버그
- **해결**: `_PATH_ROLE = Qt.ItemDataRole.UserRole + 4` 신설, 순수 경로 저장
- 3개 클래스에 적용: `MergeEncodingDelegate`, `TextConverterFileList` (`L4810`), `BulkFixerFileList` (`L8683`)
- 하위 호환 폴백: `item.data(0, _PATH_ROLE) or item.toolTip(0)`

### 완료 — Bulk Fixer 구조 리팩토링 (드롭존 분리)

- **신규 클래스 `BulkFixerDropZone(QLabel)`** 추가 (`L8540`)
  - 외부 파일/폴더 드롭 전용, `files_dropped`/`folder_dropped` 2개 시그널
  - `MergeDropZone` + `TextFixerDropZone` 패턴 융합
  - 파일/폴더 구분 감지, idle/hover 상태 스타일

- **`BulkFixerFileList` 재구성** (`L8638`):
  - `InternalMove` → `DragDrop` 모드 전환 (Qt의 자동 소스 삭제 버그 회피)
  - `startDrag` CopyAction 강제
  - 수동 `dropEvent` 구현 (`target is None` 빈 영역 → 맨 끝 이동 지원)
  - 외부 파일 드롭 처리 제거 (드롭존이 담당)
  - `paintEvent` 빈 상태 렌더링 제거
  - `order_changed` 시그널 추가

- **`BulkFixerPanel._build` 레이아웃 재구성**: 드롭존 상단 배치
- 드롭존 시그널 핸들러 2개 추가 (`_on_files_dropped`, `_on_folder_dropped`)
- `_set_scan_ui`에 드롭존 비활성화 추가 (스캔 중 추가 드롭 방지)
- `retranslate`/`refresh_btn_styles`에 드롭존 갱신 추가

### 완료 — 헤더 정렬 버그 수정 (v1.0.4부터 존재한 기존 버그)

- **증상**: `setSortingEnabled(False)` + `DragDrop` 모드 조합에서 헤더 클릭으로 정렬이 동작하지 않음
- **원인**: Qt의 기본 동작으로 `setSortingEnabled(False)` 시 헤더 섹션 클릭 비활성화됨
- **해결**: `hdr.setSectionsClickable(True)` 명시 추가 (MergeFileTree가 v1.0.3/1.0.4에서 적용한 패턴 복제)

### 완료 — Phase 1: 부분 인코딩 실패 파일 대응

- **배경**: 한국어 웹소설 수집 파일 등에서 **일부 바이트가 strict 디코딩 불가능**한 케이스 발견
  - 메모장에선 정상 표시되지만 Python의 폴백 루프 8개 모두 `UnicodeDecodeError`로 실패
  - 증상 1: Bulk Fixer에서 조용히 미리보기 비어있음
  - 증상 2: Text Fixer에서 "인코딩 오류" 다이얼로그 후 파일 로드 실패
  - 증상 3: 일괄 교정 시 해당 파일 실패 처리

- **공통 헬퍼 `safe_read_text_with_report`** 신규 추가 (`L3912`)
  - strict 폴백 8개 실패 시 `errors='replace'`로 최종 재시도
  - 깨진 바이트는 U+FFFD (`�`)로 대체 (Python 기본값, 유니코드 표준)
  - 반환 튜플: `(text, used_enc, mode, replace_count)` (Phase 2 확장 대비 구조)

- **3곳에 헬퍼 적용**:
  - `BulkFixerPanel._on_file_selected` 미리보기 (`L9593`)
  - `BulkFixerWorker.run` 일괄 교정 (`L9053`)
  - `TextFixerPanel.load_file` 파일 로드 (`L7962`)

- **Text Fixer replace 모드 시 경고 다이얼로그 추가**
  - `tf_warn_partial_enc` 번역 키 5개 언어
  - 파일명 / 사용 인코딩 / 대체된 문자 수 표시
  - 상태바에도 `⚠` 아이콘으로 표시

- **회귀 안전망**: strict 폴백 8개는 그대로 유지, 정상 파일 로직 변경 없음

### 완료 — Phase 2-a: 인코딩 리포트 기능 + 티어드 자동 처리

- **설계 철학 (확정)**: Text Fixer와 Bulk Fixer의 처리 철학을 분리 (§설계 결정 기록 참조)
  - Text Fixer = **사용자 동의 기반** — 단일 파일 집중, 다이얼로그만
  - Bulk Fixer = **사후 투명성 기반** — 대량 자동 처리, 리포트 파일 생성

- **신규 상수/헬퍼/함수**:
  - `MAX_TRACK_FAILURES = 5000` (`L3772`) — 실패 위치 추적 상한
  - `_fns_track_error_handler` + `codecs.register_error('_fns_track', ...)` 모듈 로드 시 등록 (`L3783-3805`)
  - `_decode_with_failure_tracking(raw, enc)` 헬퍼 (`L3808`) — 단일 O(N) 패스로 모든 실패 위치 수집
  - `safe_read_text_with_report` 시그니처 확장: **4-tuple → 6-tuple** `(text, used_enc, mode, replace_count, failures, total_failures)` (`L3912`)
  - `write_encoding_report(...)` 신규 함수 (`L3967`) — 리포트 파일 생성

- **리포트 파일 사양**:
  - 파일명 패턴: `{원본파일명}.encoding_report.txt`
  - 저장 위치: `output_dir` 지정 시 해당 폴더, 없으면 원본 파일 폴더 폴백
  - 인코딩: UTF-8 BOM 없음 (다른 에디터 호환)
  - 구성: 헤더 / 실패 위치 리스트 (최대 5000개) / 요약 통계 / 티어별 권장 조치

- **BulkFixerWorker 티어 분기** (`L8883`):
  - `TIER1_THRESHOLD = 500`, `TIER2_THRESHOLD = 5000`
  - **Tier 1** (1~500자 손상): 처리 + 리포트 생성, `warn` 카운트
  - **Tier 2** (501~5000자): 처리 + 리포트 생성 (경고 수위), `warn` 카운트
  - **Tier 3** (5001자+): **원본 보호 스킵** + 리포트만 생성, `skip` 카운트
  - 정상(strict): `ok` / I/O 예외: `fail` 카운트

- **시그널 확장**:
  - `sig_file_done`: `bool` → `str` (카테고리 `'ok'/'warn'/'skip'/'fail'`)
  - `sig_done`: `(ok, fail)` 2-param → `(ok, warn, skip, fail)` **4-param**

- **BulkFixerPanel._on_done** (`L9688`):
  - 4-카테고리 수신
  - 비정상(warn/skip/fail) 하나라도 있을 때만 티어 브레이크다운 다이얼로그 표시 (전부 정상이면 기존 UX 유지 — 방해 없음)
  - 출력 폴더 자동 열기 유지

- **번역 키 5개 언어 (ko/en/ja/zh_cn/zh_tw)**:
  - UI: `bulk_done_title`, `bulk_done_ok`, `bulk_done_warn`, `bulk_done_skip`, `bulk_done_fail`
  - 리포트 템플릿 (15개): `report_header`, `report_file`, `report_path`, `report_size`, `report_enc`, `report_fail_count`, `report_action`, `report_action_processed`, `report_action_skipped`, `report_time`, `report_line_col`, `report_bytes`, `report_context`, `report_summary_title`, `report_total_failures`, `report_truncated`, `report_advice_title`
  - 티어별 조치 문구 (3개): `report_advice_tier1`, `report_advice_tier2`, `report_advice_tier3`

- **실측 기반 설계 이력** (상세는 `v1.0.6_Phase2_Completion_Record.md` §2.6 참조)
  - Phase 2-a는 탁상 설계가 아닌 실측 데이터 기반 설계
  - 진단 도구 → 전체 스캔 → 합성 검증의 3단계 방법론 적용
  - 손상 임계값 500 → 50 조정으로 추가 28~29개 손상 파일 표면화
  - `make_tier_test_data.py`의 경계값 합성 데이터(499/5000/5001)로 재현 가능한 검증 확보

- **회귀 안전망**: Phase 1의 strict 폴백 8개·정상 파일 로직 모두 변경 없음, Text Fixer 경고 다이얼로그 유지

### 완료 — Phase 2-b: 도움말 고지

- **Text Fixer 도움말 섹션 추가** (`L13553-13556` 기준 영어, 5개 언어 전부)
  - "Partially corrupted files" note: 손상된 파일도 열 수 있으며 `�`로 표시 + 상태바 `⚠` 아이콘 설명
  - "detailed inspection of a single file" tip: Text Fixer가 단일 파일 집중 검토용임을 명시
  - Tier 3 자동 스킵 안내 warn: 수만 개 손상 파일은 재다운로드 권장, Bulk Fixer가 자동 스킵한다는 안내

- **Bulk Fixer 도움말 섹션 추가** (`L13569-13572`)
  - "Automatic corruption tiering" note: Tier 1/2/3 각 조건과 동작 상세
  - 리포트 파일명 형식 `{original_filename}.encoding_report.txt` 명시
  - Tier 3 스킵된 파일은 Text Fixer에서 개별 검토하라는 warn — 두 도구 역할 분담 명시

- **5개 언어 시각 검수 통과** (이전 세션 보고)

### 완료 — 실기 QA 중 발견된 프리징 이슈 해결

- **인코딩 실패 위치 추적 O(N×K) 프리징** (지침서 §4.4에서 예견된 성능 우려의 현실화)
  - 증상: 약 27MB급 대용량 파일 + 수천 에러 시 UI 분 단위 프리징
  - 수정 전: `while pos < len: raw[pos:].decode('strict')` — 매 반복 슬라이스 복사
  - 수정 후: `codecs.register_error` 기반 커스텀 에러 핸들러 + 단일 `raw.decode()` 호출 → C 레벨 O(N) 패스
  - 개선 폭: 분 단위 → 수백 ms (수백~수천 배)
  - 코드 위치: `_decode_with_failure_tracking` (`L3808-3909`)

- **Bulk Fixer 미리보기 대용량 파일 프리징**
  - 증상: 50만 줄급 대용량 파일 선택 시 `_on_file_selected` 12초 이상 프리징
  - 수정 전: `text.splitlines(keepends=True)[:80]` — 전체 27MB 파싱 후 50만 객체 생성, 80개만 사용
  - 수정 후: `text[:32768].splitlines(keepends=True)[:80]` — 32KB만 처리
  - 개선 폭: 연산량 약 800배 감소
  - 코드 위치: `BulkFixerPanel._on_file_selected` (`L9608`)

### 완료 — 진단 인프라 구축

- **진단 트레이스 로그** — `🔵 [Trace]` 3단계 세분 트레이스 (safe_read / preview 추출 / setPlainText 각각 측정)
  - `_on_file_selected` 내 6개 지점 (`L9583, 9596, 9600, 9610, 9615, 9619`)
  - 전체 트레이스 16개 (보고 기반)

- **디버그 스크립트 3종** (`docs/debug/`)
  - `diagnose_ilsig.py` (4 KB) — 단일 파일 대상 5단계 벤치마크: 32KB 읽기 / chardet / UTF-8 strict 전체 / 8개 인코딩 폴백 / 미리보기 추출. 원격 디버깅용 (결과 복사 → 공유 구조)
  - `scan_corrupted.py` (11 KB) — 전체 컬렉션 스캔, 임계값 50 기준 연속 깨짐 감지
  - `make_tier_test_data.py` (13 KB) — 티어 경계값 합성 데이터 생성 (499/5000/5001 포함 7종), ASCII 영역에만 `\xFF` 주입해 정확히 N개 U+FFFD 보장, `RANDOM_SEED=42` 재현성

### 완료 — 테스트 파일 Phase 2-a 통합

- **`test_file_nexus.py`** v1.0.5 기준 3,998줄 → **4,340줄** (+342줄). 3번 세션 미뤄진 최우선 작업을 완료
- **§추가O (Phase 2-a 인코딩 리포트 기능)** 신설 — 3개 테스트 클래스 22개 테스트
  - `TestSafeReadTextWithReport` (5건) — 6-tuple 반환 구조 + 정상/replace/없는 파일/UTF-8 BOM 케이스
  - `TestDecodeWithFailureTracking` (7건) — 위치 추적 알고리즘 (라인/컬럼, CRLF, MAX 상한 5000, context 공백 정규화, 잘못된 인코딩)
  - `TestWriteEncodingReport` (10건) — 리포트 생성·파일명 패턴·폴더 폴백·티어별 문구·5개 언어 번역 키 누락·BOM 없음 검증

- **§추가P (v1.0.6 버그 수정 회귀 방지)** 신설 — 2개 테스트 클래스 3개 테스트
  - `TestBulkFixerPreviewLargeFile` (1건) — `text[:NNNNN].splitlines` 패턴 소스 검증 (수정 전 패턴 잔재 차단 포함)
  - `TestPreviewExtractionPerformance` (2건) — 50만 줄 100ms 이내 + 32KB 상한 일관성 (Linux 환경 직접 재현 검증 시 **0.24ms** 측정)

- **V103/V104 회귀 테스트 4건 A-2 확장** — Phase 2-a 헬퍼 추상화로 인한 사이드 이펙트 해결
  - Phase 2-a 이후 `TextFixerPanel.load_file`·`BulkFixerWorker.run`·`BulkFixerPanel._on_file_selected` 3곳의 `alchemy_detect_encoding` 직접 호출이 `safe_read_text_with_report` 헬퍼 경유로 통합됨
  - 결과: `test_alchemy_used_in_*` 3건 및 `test_alchemy_callers_unpack_tuple` 1건이 기존 문자열 매칭 기준으로 실패
  - 해결 원칙: **"테스트 완화"가 아닌 "리팩토링 후 현실 반영"** — 기존 테스트의 본래 의도("이 3곳이 alchemy 기반 인코딩 감지를 사용하는가")는 헬퍼 경유로도 유지됨을 테스트 기준에 반영
  - `test_alchemy_used_in_text_fixer/bulk_worker/bulk_preview`: 직접 호출 OR `safe_read_text_with_report` 헬퍼 경유 둘 다 허용
  - `test_alchemy_callers_unpack_tuple`: 하한 6→4 조정 (정의 + 헬퍼 내부 + Text Converter + Text Merger = 4건이 Phase 2-a 이후 정상 수치). 튜플 언패킹 잔재 차단 로직은 유지

- **TestV105RegressionModule 가드 누락 수정** (§5.1 범위 밖 발견사항)
  - Linux + PySide6 불완전 Mock 환경에서 테스트 실행 시 6건 실패/오류로 표면화
  - 원인: `@unittest.skipUnless(HAS_MODULE, ...)` 데코레이터 누락 — v1.0.5 시점의 **고립된 개별 실수**
  - 전수 점검 결과 6개 `*RegressionModule` 클래스 중 이 1개만 가드 누락 (v0.10.0~v1.0.4 5개는 모두 정상)
  - 해결: 기존 5개가 일관되게 사용하던 문구 `"FileNexusSuite 로드 실패 (PySide6 필요)"`를 그대로 복사 적용
  - Windows + PySide6 정상 설치 환경에서는 `HAS_MODULE=True`라 증상이 드러나지 않았던 것으로 추정

- **최종 검증 결과** (Linux + PySide6 Mock 환경):
  - 총 527개 테스트 / **353 통과** / **0 실패** / **0 오류** / 174 스킵
  - 환경 차이로 인한 174 스킵은 Windows 환경에서 `HAS_MODULE=True`로 전환되어 실행 및 통과 예상
  - 작업 전 상태(351 통과 / 5 실패 / 3 오류) 대비 실패·오류 전량 해소

### 진행 예정 — #7: Text Converter 구조 리팩토링

- `TextConverterDropZone` 신규 추가 (현재 부재 확인됨)
- `TextConverterFileList` 단순화 (Bulk Fixer 패턴 복제)
- `TextConverterPanel._build` 레이아웃 재구성
  - 왼쪽: 드롭존(상단 72px) + 상단 버튼 + 파일 목록 + 하단 조작 버튼
  - 오른쪽: 모드별 옵션 + 출력 폴더 이동 + 변환/취소 버튼 + 진행바/상태 이동
  - 하단 안내 박스 제거 (5개 언어 번역 키 정리)
- 좌우 비율 5:4
- 모드 전환(TXT↔EPUB) 시 드롭존 텍스트/아이콘 갱신

### 진행 예정 — #8: Text Merger MD 출력

- 출력 포맷 라디오 버튼 (.txt / .md)
- 헤더 자동 추가 옵션 (체크박스, 헤더 레벨, 파일명 사용)
- 5개 언어 번역

### 진행 예정 — QA 체크리스트 v1.0.6

- `QA_CHECKLIST_v1.0.5.md` 포맷 참고하여 `QA_CHECKLIST_v1.0.6.md` 신설 예정
- Phase 2-a 티어 전수 / Phase 2-b 도움말 5개 언어 / 프리징 최적화 시나리오 포함

### 진행 예정 — 디버그 스크립트 실기 파일명 정리

- `docs/debug/diagnose_ilsig.py`: L2 docstring, L16 PATH 상수, L19 print 문구에 남은 초기 진단 대상 파일명 중립화. PATH는 `test_data/tier3_heavy.txt` 가데이터 경로로 치환 권장
- `docs/debug/make_tier_test_data.py`: L18 주석 중립화
- 원본 진단 대상 파일 삭제는 신용우님 재량

### 설계 결정 기록 (향후 참조용)

**Text Fixer vs Bulk Fixer 처리 철학 분리** — Phase 2-a 설계 논의 중 확정:

| 구분 | Text Fixer | Bulk Fixer |
|---|---|---|
| 처리 단위 | 단일 파일 | 대량 파일 |
| 사용자 존재 | 현장 상호작용 | 부재 (자동) |
| 리스크 전이 | 사용자 동의 (B, 등대) | 사후 투명성 |
| 경고 수단 | 다이얼로그 | 리포트 파일 |

- **사전 스캔 설계안 폐기**: 36GB 규모 실제 시나리오 고려 시 비현실적
- **심각 실패 스킵의 정당성**: 잘못된 인코딩 강제 처리는 원본보다 나쁜 결과 → 원본 보호가 우선
- **두 도구 역할 분담**: Bulk에서 스킵된 파일 → Text Fixer에서 개별 검토 권장

**지침서 대비 실제 구현 변경점** (Phase 2-a) — 상세는 `v1.0.6_Phase2_Completion_Record.md` §8 참조:

- `sig_done` Signal 3-param → 4-param (`fail` 카테고리 보존)
- `sig_file_done` `bool` → `str` 전체 전환 (카테고리 명확화)
- 완료 다이얼로그 **조건부 표시** (전부 정상이면 생략 — 기존 UX 유지)
- 번역 키 `bulk_done_fail` 추가로 4개
- 위치 추적 알고리즘 근본 재설계 (O(N×K) → O(N), 실기 QA 중 현실화된 성능 이슈 대응)

---

### 완료 — #7 Text Converter 구조 리팩토링 ⭐ NEW (2026-04-21 오후)

**배경**: Bulk Fixer 리팩토링 패턴을 Text Converter에도 복제하여 UI 일관성 확보. 하단 안내 박스 제거 + 레이아웃 5:4 재구성 + 드롭존 분리.

- **신규 클래스 `TextConverterDropZone`** 추가 (`L4763`, 109줄)
  - `BulkFixerDropZone` 복제 + `mode` 파라미터 (TXT/EPUB 전환 시 텍스트·아이콘 갱신)
  - 폴더 드롭은 미지원 (EPUB 생성 시 폴더 구조 보존 이슈 방지)
  - `files_dropped` 시그널 하나

- **`TextConverterFileList` 재구성** (`L4872`):
  - `InternalMove` → `DragDrop` 모드 (Qt 자동 소스 삭제 버그 회피)
  - `setSectionsClickable(True)` 명시 (v1.0.6 기존 헤더 정렬 버그 수정 패턴)
  - `startDrag` CopyAction 강제
  - `paintEvent` 빈 상태 렌더링 제거

- **`TextConverterPanel._build` 레이아웃 재구성**:
  - 좌 `stretch=5` / 우 `stretch=4` 비율 (왼쪽 확대)
  - 드롭존 상단 배치
  - 출력 폴더·변환 버튼·진행바·상태 레이블 모두 오른쪽 이동
  - 하단 안내 박스 제거

- **번역 키 정리**:
  - `conv_help` 5개 언어 제거 (하단 안내 박스 폐지)
  - 기존 죽은 `conv_file_list` 5개 언어 제거 (옵션 A 선택)
  - 새 `conv_file_list` 5개 언어 추가

- **`_switch`에 `_drop_zone.set_mode()` 추가**, `retranslate`·`refresh_btn_styles`에 드롭존 갱신

- **`MergeDragList` 데드 코드 제거** (57줄) — v1.0.3/1.0.4에서 `MergeFileTree`로 교체된 미사용 클래스. #7 작업과 동반 정리. (이전 인수인계 §7.1 "v1.0.7 후보" 해소)

- **지시서**: `v1.0.6_TextConverter_Refactor_Work_Instruction.md` v4 확정 (381줄)

- **실기 QA**: 9/9 전수 통과 (드롭존 양방향, 모드 전환, 내부 드래그, 헤더 클릭 정렬, 5:4 레이아웃, 5개 언어 회귀, 변환 E2E 양방향, toolTip 오염 회귀, 테마 전환 회귀 — IceCream Ebook Reader 외부 검증 포함)

### 완료 — 설정 다이얼로그 번체 중국어 잔재 버그 수정 (v1.0.5부터 존재한 기존 버그)

**배경**: 繁體 → 한국어 전환 시 단축키 리셋 버튼들에 `預設` / `重設` / `輸出資料夾` / `選擇資料夾` 등 번체 문자열 잔재. `SettingsDialog._retranslate_dialog`가 일부 위젯 텍스트 갱신을 누락한 것이 근본 원인.

- **§2.1 A — `_apply_theme_now`에 `_retranslate_dialog()` 호출 추가** (1줄)
  - 테마 카드 더블클릭 경로와 [적용] 버튼 경로의 일관성 확보

- **§2.2 B — 위젯 self 저장 보완** (9개)
  - `_sc_reset_btns` dict, `_sc_reset_all_btn` (단축키 리셋 버튼)
  - `_lang_frame`, `_odir_btn`, `_odir_reset_btn` (일반 설정 위젯)
  - `_ver_lbl` (사이드바 버전 라벨)
  - 기타 self 저장 누락분

- **§2.4 D — `_retranslate_dialog` 확장** (3블록)
  - **D-1**: 단축키 리셋 버튼들 텍스트 갱신 (`btn_reset` / `btn_reset_all`)
  - **D-2**: 일반 설정 출력 폴더 라벨/버튼 텍스트 갱신 (`settings_output_dir` / `conv_btn_pick` / `merge_path_reset`)
  - **D-3**: 라이선스 페이지 타이틀 갱신 (`settings_nav_license`)

- **§2.5 E — AppSuite 내 데드 코드 3개 메서드 74줄 완전 제거** ⭐
  - `_page_language` (40줄) + `_on_lang_selected` (2줄) + `_retranslate_dialog` (32줄)
  - 전수 grep 검증: 호출처 0건 + `_lang_radios` 초기화 없음으로 실행 시 `AttributeError` 확정
  - MergeDragList와 동일 유형 리팩토링 잔재 (SettingsDialog가 별도 QDialog로 분리되기 전 잔재 복제본)
  - `closeEvent`는 AppSuite의 정상 기능이므로 보존 (작업 중 패널 확인 + 종료 확인 팝업)

- **지시서**: `v1.0.6_SettingsDialog_RefreshRetranslate_Work_Instruction.md` v2 확정 (359줄)

- **실기 QA**: 繁體 → 한국어 전환 시 모든 탭(테마/일반 설정/단축키/라이선스) 잔재 해소 확인 (2026-04-21 오후)

### 완료 — APP_VERSION 및 외부 메타 파일 v1.0.6 갱신

- **`FileNexusSuite.py` L76**: `APP_VERSION = "1.0.5"` → `"1.0.6"`
  - 11개 표시 위치 자동 반영 (HelpDialog 5개 언어 타이틀 / SettingsDialog 사이드바 / AppSuite 메인 헤더 등)

- **`version_info.txt`**: `filevers`/`prodvers`/`FileVersion`/`ProductVersion` 4곳 `1.0.6.0`
  - Windows 파일 속성 대화상자 실측 확인 완료 (2026-04-21 오후)

- **`README.txt`**: 타이틀 v1.0.6

- **`README.md`**: version 뱃지 1.0.6 + 한글 이름 "신용우" 제거
  - L36 `[신용우(Hanrim)]` → `[Hanrim]`
  - L280 `**신용우 Yongwoo Shin (Hanrim)**` → `**Yongwoo Shin (Hanrim)**`
  - L38 영문 본문 및 L268 Copyright는 **공식 크레딧**으로 유지

- **`build.bat`**: 버전 표기 없음 확인 (수정 불요)

### 완료 — 자동 테스트 TestV106AppVersion 분리

- **기존 `TestV105Regression.test_app_version_source_is_105`** 및 `TestV105RegressionModule.test_app_version_is_105` 제거
- **§추가N 신설** — `TestV106AppVersion` + `TestV106AppVersionModule` 2개 클래스 (B-1 옵션)
  - v1.0.5 기타 회귀 테스트 클래스들은 그대로 유지 (v1.0.5 당시 상태 메시지·인코딩 드롭다운 등 계속 지켜봄)
- **실측**: 527/0/0/0 통과 (55 → **57 클래스**)
- **라인 수**: `test_file_nexus.py` 4,342 → 4,370 (+28줄)

### 작업 중 — v1.0.7 이월 항목

#### ⏭ 설정 다이얼로그 라벨/프레임 color 잔재 버그 (v1.0.5부터 존재)

**증상**: 테마 변경 [적용] 후 다른 탭 이동 시 **라이트→다크 방향에서만** 일부 위젯이 이전 테마 값으로 남음 (언어 프레임 배경, 타이틀 라벨 color, 출력 폴더 관련 위젯). 설정창 재오픈 시 정상 복귀.

**2026-04-21 오후 세션 처리 경과**:
- v1.0.5 빌드로 재현 확인 — v1.0.6에서 생긴 버그 아님
- 4가지 접근 시도: `QTimer` 지연 / `unpolish/polish` / `QApplication` 전역 재적용 / `findChildren().update()` — **모두 실패**
- 결국 **v1.0.5 원본 상태로 깨끗하게 원상복귀** + v1.0.7 이월 결정
- 유지된 v1.0.6 수정은 §2.1 A / §2.2 B / §2.4 D / §2.5 E만 (번체 잔재 + 데드 코드 관련)

**상세**: `Claude_Handover_FileNexusSuite_v1.0.6.md` §5.1 및 §7.8 참조 (재시도 금지 목록 포함).


## v1.0.5 (2026-04-18) — Text Merger 저장 인코딩 드롭다운 UI 사용성 개선

### 버그 수정 (릴리즈 QA 중 발견)

- **언어 전환 시 Text Merger 하단 상태 메시지가 한국어로 남는 문제** (`TextMergerPanel.retranslate`, `L9589~`)
  - 현상: 파일 추가 후 언어를 영어/일본어/중국어로 전환하면 "26개 파일 추가됨 (인코딩 자동 감지 완료)"가 한국어 그대로 표시됨
  - 범위 확장: 동일 구조의 다른 상태 메시지들도 모두 같은 버그 존재 — `merge_status_del`, `merge_status_clr`, `merge_reading`, `merge_save_done`, `merge_save_err`, `merge_path_set`, `merge_path_reset_done`, `bulk_scanning`
  - 원인: `retranslate()`가 `merge_status_ready` 상태일 때만 `_lbl_status`를 갱신하는 구조 (v1.0.4 이전부터 존재한 기존 버그, v1.0.5 빌드 후 실기 QA 중 신용우님이 3개 언어 스크린샷으로 발견)
  - 수정: `_retranslate_status()` 헬퍼 메서드 + `_match_status_template()` 정규식 매칭 유틸 신설
    - **정적 메시지** (플레이스홀더 없음, 5종): 단순 매핑 후 현재 언어로 재렌더
    - **복원 가능 동적 메시지** (2종): 원본 정보로 재구성
      - `merge_status_add` → `len(self.file_list)`로 `{n}` 복원
      - `merge_path_set` → `self.save_dir`로 `{path}` 복원 (save_dir 비어있으면 `ready` 폴백)
    - **복원 불가 메시지** (3종, 원본 정보 손실): `ready`로 리셋 + `_glog` 디버그 로그로 원인 추적 가능
  - 방어적 처리: 알려지지 않은 상태 텍스트는 변경하지 않음 (외부 확장 대응)

### 기능 개선 (UI)

- **저장 인코딩 드롭다운에 용도 설명 병기** (`L9152~9162`)
  - 기존: `UTF-8`, `Shift-JIS`, `GBK` 같은 기술명만 노출 → 비프로그래머가 8종 중 무엇을 고를지 판단이 어려움
  - 개선: 각 아이템에 연관 언어 병기 (예: `Shift-JIS (일본어)`, `GBK (중국어 간체)`)
  - 주관적 표현(`(추천)`, `(전용)`)은 배제하고 **사실 기반 수식어만** 사용
  - UTF-8 / UTF-16은 특정 언어에 종속되지 않으므로 수식어 없이 표기
  - 5개 지원 언어(한·영·일·중간·중번) 모두 해당 언어권 표준 표기 적용
  - 중국어 간체/번체에서 일본어는 `日文`으로 표기 (v1.0.4 tip 문구와 일관성)

- **저장 인코딩 콤보박스 아래 한 줄 도움말 추가** (`L9189~9193`)
  - 문구: "확실하지 않으면 UTF-8을 선택하세요" (5개 언어 번역)
  - 회색 작은 글씨(`MUTED`, `font-size:11px`)로 기존 도움말 톤과 통일
  - 목적: 콤보박스를 열기 전에도 권장 기본값을 시각적으로 안내

### 내부 구조 개선 (리팩토링)

- **표시 라벨과 내부 키 분리** (`TextMergerPanel._ENC_ITEMS` 클래스 상수 신설, `L9086~9099`)
  - 기존(v1.0.4): `addItems(["UTF-8", ...])` → `currentText()`로 저장값 획득 → 언어 전환 시 라벨이 바뀌면 내부 로직에 영향 가능
  - 개선(v1.0.5): `addItem(display, userData)` 패턴 — `userData`에 기존 내부 키 8종 보존
  - `_merge_files()` / `get_config()` → `currentText()` → `currentData()` 로 마이그레이션
  - `apply_config()` → `findData()` 우선, 실패 시 `findText()` 폴백 (v1.0.4 이하 설정 파일 호환 자동 유지)
  - 향후 라벨 스타일 변경 시 내부 codec 매핑 / 설정 저장 로직에 영향 없음

- **Text Merger의 `retranslate()` 갱신**  (`L9671~9677`)
  - 언어 전환 시 콤보박스 8개 아이템의 표시 라벨과 도움말 라벨을 모두 재번역
  - `_ENC_ITEMS` 상수 한 곳에서 매핑을 관리하여 초기화/재번역 양쪽에서 동기화 사고 위험 제거

### 번역 리소스 추가

- 5개 언어 × 9개 키 = **45개 번역 항목 신규 추가** (`merge_enc_utf8` ~ `merge_enc_big5` + `merge_enc_hint`)
- 키 이름은 기존 `merge_enc_warn_*` 패턴을 따라 `merge_enc_*` prefix로 통일
- 각 언어 사전의 `merge_enc_warn_msg` 바로 뒤에 논리적 그룹핑

### 기술 부채 해소 — 번역 사전 중복 키 정리

v1.0.2 인수인계에서 식별된 `zh_cn` 중복 이슈를 이번 버전에서 전체 언어 일괄 정리:

- **74개 중복 라인 삭제** (zh_cn 69 + ko 1 + en 1 + ja 2 + zh_tw 1)
- **모든 중복의 두 출현 값이 완전히 일치** 확인 후 삭제 (AST 파싱 기반 안전 검증)
- 각 중복 그룹의 첫 출현 보존, 나머지 삭제 원칙
- **동작 영향 0**: Python dict는 나중 값이 앞선 값을 덮어쓰지만, 값 동일이므로 결과 동일
- 주요 중복 패턴:
  - `merge_open_explorer` 키가 5개 언어 **모두**에서 중복 (dict 전체 재삽입 흔적)
  - `bulk_*` / `tf_*` 접두사 키들이 `zh_cn`에 대량 중복 (Bulk Fixer·Text Fixer 확장 시점의 의도치 않은 중복 삽입)
- 결과: 5개 언어 각 dict가 390~391키로 슬림화 (zh_cn 463줄 → 394줄)

### 테스트 자동화 강화

- **`TestV105Regression` (소스 검증 12개)**:
  - `_ENC_ITEMS` 상수 정의 + 8종 내부 키 + 8종 i18n 키 전수 검증
  - 콤보박스가 `addItem(display, userData)` 패턴 사용 확인 (v1.0.4 `addItems` 잔재 검출)
  - `_lbl_enc_hint` 도움말 라벨 생성 + retranslate 갱신 로직 존재
  - `retranslate()`에서 콤보박스 아이템 라벨 갱신 로직 존재
  - `_merge_files` / `get_config` / `apply_config`의 `currentData`·`findData` 마이그레이션
  - 5개 언어 사전 × 9개 키 = 45개 항목 존재 (정규식 기반 개수 검증)
  - 중국어 간체/번체에서 `日文` 표기 사용 + `日语`/`日語` 부재 검증 (v1.0.4 tip과 일관성)
  - APP_VERSION 소스값 `1.0.5` 검증

- **`TestV105RegressionModule` (런타임 검증 6개)**:
  - APP_VERSION 실제 런타임 값 `1.0.5` 검증
  - 5개 언어 딕셔너리에 9개 `merge_enc_*` 키가 실제 문자열 값으로 존재
  - 각 라벨이 대응 인코딩 키(예: `UTF-8`)를 포함함으로써 식별 가능성 보장
  - 중국어 간체/번체 `merge_enc_shiftjis` 값에 `日文` 포함 + `日语`/`日語` 부재
  - `TextMergerPanel._ENC_ITEMS` 내부 키 순서가 v1.0.4 콤보박스 순서와 동일 (설정 호환성 보장)
  - 도움말 문구에 `UTF-8` 안내가 모든 언어에 포함

- **v1.0.4 기존 테스트 2개 업데이트** (시그니처 변경 영향, 의도 유지):
  - `test_text_merger_combo_has_cjk_encodings`: `addItems` 정규식 → `_ENC_ITEMS` 상수 블록 검색으로 변경
  - `test_app_version_is_104` → `test_app_version_is_104_or_later`: 정확 일치 → 튜플 비교 (`≥ (1,0,4)`) 완화

- **`TestV105TranslationNoDuplicates` (중복 재발 방지 2개)**:
  - 5개 언어 사전의 중복 키가 전부 0개임을 AST 파싱 기반으로 검증
  - 언어별 키 개수 편차가 5 이내임을 검증 (번역 완결성 간접 보장)

- **`TestV105StatusRetranslate` (상태 메시지 재번역 10개)**:
  - 정적 메시지(ready/clr/save_err) 재렌더링 검증
  - 동적 메시지 `merge_status_add` — 언어 전환 시 현재 file_list 수로 재구성
  - 동적 메시지 `merge_path_set` — 현재 save_dir로 재구성, 빈 값이면 ready 폴백
  - 복원 불가 메시지(`del`, `save_done`) → ready 리셋 검증
  - 알려지지 않은 임의 텍스트는 변경하지 않는 방어적 처리 검증
  - `_match_status_template` 단위 테스트 (플레이스홀더 있는 템플릿 정규식 매칭 정확도)

**최종 결과: 502개 / 실패 0 / 오류 0 / 스킵 0 (로컬, Offscreen Qt 환경)**

### 호환성

- **v1.0.4 이하 사용자 설정 파일 자동 호환**:
  - v1.0.4까지 `combo_enc`는 표시 텍스트(`"Shift-JIS"` 등)로 저장됨
  - v1.0.5의 `apply_config()`은 `findData()` 1차 → `findText()` 2차 폴백 → 구버전 설정 그대로 로드 성공
  - 한 번 저장되면 v1.0.5 이후 형식(내부 키)으로 자동 마이그레이션
- **회귀 위험 최소화**: `TextMergerPanel` 외 다른 탭(Text Converter 등) 및 콤보박스 미변경. 설정 저장 스키마 키 이름(`combo_enc`) 그대로 유지.

---

## v1.0.4 (2026-04-18) — Text Merger 인코딩 종합 개선

### 버그 수정 (초판 피드백 반영)

- **경고 다이얼로그에 HTML 태그가 그대로 표시되던 문제** (`_build_dlg` / `_dlg_question`)
  - `_build_dlg`가 메시지 라벨에 `PlainText` 포맷을 강제 지정 → 신규 `merge_enc_warn_msg`의 `<b>`, `<br>`, `<code>` 태그가 텍스트로 보이던 문제
  - 수정: `_build_dlg`와 `_dlg_question`에 `rich_text: bool = False` 파라미터 추가 (기본값은 기존 동작 유지)
  - Text Merger 경고 호출부만 `rich_text=True`로 변경 → 다른 다이얼로그 동작 영향 0
  - 기본값이 False이므로 외부 다이얼로그 호출부는 변경 불필요

- **ASCII로 시작하는 Shift-JIS/GBK/Big5 파일을 cp949로 오판정하던 문제** (`alchemy_detect_encoding` 폴백)
  - chardet이 "영어 도입부 + CJK 본문" 파일을 `cp1006`(우르두어) 등 엉뚱한 인코딩으로 24% 정도 낮은 신뢰도로 감지 → 임계값 통과 못 함
  - 폴백 단계에서 `utf-8` 실패 시 곧바로 `cp949`를 반환해 실제 Shift-JIS 파일도 cp949로 잘못 분류되던 문제
  - 수정: `utf-8` 실패 시 `cp949 → shift_jis → gbk → big5` 순차로 strict 디코딩을 검증해 실제로 디코딩 가능한 인코딩을 찾음
  - 추가: Windows의 Shift-JIS 확장 인코딩(`cp932`, `windows-31j`)을 CJK 화이트리스트에 추가하고 `shift_jis`로 정규화 (chardet이 긴 일본어 콘텐츠를 `cp932`로 반환하는 케이스 대응)
  - 최후의 폴백은 `cp949` 유지 (v1.0.3 동작과 호환)
  - v1.0.4 Shift-JIS 저장 결과물을 다시 Text Merger에 드롭하는 자연스러운 시나리오에서 발견됨

- **경고 다이얼로그가 실제 파일 손실 규모를 축소 표현하던 문제** (`alchemy_check_encoding_compat` UX 개선)
  - 기존 표시: "깨질 문자: 약 N자" — 여기서 N은 "고유 문자 **종류 수**" (예: "한"이 50번 있어도 1로 카운트)
  - 사용자가 "N자만 ?로 대체될 것"으로 오해 → 실제로는 파일 대부분이 `?`가 되는 상황이 발생
  - 신용우님의 실기 테스트: 25개 다국어 파일을 Shift-JIS로 저장 시도 → 다이얼로그엔 "약 313자"로 표시됐으나 실제 ? 대체는 **3,023자** (10배 차이)
  - 수정: `alchemy_check_encoding_compat` 시그니처를 `(has_loss, bad_count, samples)` 3-tuple → `(has_loss, bad_kinds, bad_total, total_chars, samples)` 5-tuple로 확장
  - 다이얼로그 표시도 3단 구조로 개선: "깨질 문자 **종류**: N종 / 영향받는 **글자 수**: M자 (전체의 **P%**)"
  - 사용자는 이제 실제 손실 규모와 비율까지 인지한 상태에서 저장 여부 결정 가능
  - 5개 언어 메시지 모두 동일한 정보 구조로 통일

### 기능 추가

- **Text Merger 저장 인코딩에 Shift-JIS / GBK / Big5 추가** (`L9072`)
  - 기존 5종(UTF-8, UTF-8-BOM, EUC-KR, CP949, UTF-16) → 8종으로 확장
  - 5개 지원 언어(한·영·일·중간·중번)와 저장 인코딩 범위 일치
  - codec 매핑 4종으로 확장: `Shift-JIS`→`shift_jis`, `GBK`→`gbk`, `Big5`→`big5`
  - 기존 콤보박스 인덱스(0~4) 그대로 보존 → 저장된 설정값 호환

- **UnicodeEncodeError 사전 경고 다이얼로그** (`L9445~9456`)
  - 저장 직전 `alchemy_check_encoding_compat()`로 손실 검증
  - 한글→Shift-JIS 같은 호환 불가 조합에서 저장 실패 전 미리 경고
  - 다이얼로그에 깨질 문자 개수 + 샘플 5개 표시
  - 사용자 동의 시 `errors='replace'`로 저장 (`?`로 대체), 거부 시 저장 중단
  - 샘플 문자 HTML 이스케이프 처리로 다이얼로그 렌더링 안전성 확보
  - 5개 언어에 `merge_enc_warn_title` / `merge_enc_warn_msg` 키 추가

- **신뢰도 % 4단계 색상 코딩 + 툴팁** (`L6647~6665`, `L9328~9332`)
  - 기존 균일 회색 표시 → 4단계 의미별 색상 (인수인계 후보 #3)
    - ≥90%: `#4CAF50` 초록 (안전)
    - ≥70%: `#F1C40F` 노랑 (주의)
    - ≥50%: `#E67E22` 주황 (경고, alchemy CJK 임계값 0.5와 일치)
    - <50%: `#E74C3C` 빨강 (위험)
  - 신뢰도 <90%인 텍스트 파일은 툴팁에 안내 추가
    (chardet 원본 신뢰도가 낮아도 결과는 정확할 수 있음)
  - 5개 언어에 `merge_low_conf_hint` 키 추가

- **CJK 인코딩 배지 색상/라벨 추가** (`L6526~6552`)
  - v1.0.3 누락 보완 — alchemy가 감지한 `shift_jis/gbk/big5`가 보라색 fallback으로만 표시되던 문제
  - 새 색상: `shift_jis`=분홍(`#E91E63`), `gbk/gb18030/gb2312`=골드(`#F1C40F`), `big5`=시안(`#00BCD4`)
  - 배지 라벨 정규화: `Shift-JIS`, `GBK`, `Big5`

### 리팩토링

- **`alchemy_detect_encoding()` 시그니처 확장 + Text Merger `_detect_encoding` 통합** (`L3456`)
  - 반환 타입: `str` → `(str, float)` 튜플 (인코딩명 + 신뢰도)
  - Text Merger 패널의 자체 `_detect_encoding()` 메서드 제거 → alchemy로 통일
  - 읽는 바이트 8192 → 32768로 확대 (Text Merger 기존 동작 흡수)
  - 인수인계 후보 #4 "`_detect_encoding()` 통합 여부" 완료
  - 호출부 5곳 업데이트:
    1. `TxtEpubConvertWorker.run()` (L4307)
    2. `TextFixerPanel.load_file()` (L7274)
    3. `BulkFixerWorker.run()` (L8217)
    4. `BulkFixerPanel._on_file_selected()` (L8656)
    5. `MergePanel._add_files()` (L9319, 패턴 `enc, conf = alchemy_detect_encoding(path)`)
  - Text Merger 부수 효과: v1.0.3 alchemy 강화분(CJK 정규화·화이트리스트) 자동 흡수
  - Text Fixer/Bulk Fixer 부수 효과: 읽는 바이트 8192 → 32768로 CJK 감지 정확도 ↑

### 도움말·문서

- **Text Merger 도움말 5개 언어 갱신** (`L12162`, `L12299`, `L12436`, `L12573`, `L12710`)
  - 저장 인코딩 선택 기준에 Shift-JIS·GBK·Big5 설명 추가
  - 한국어·English·日本語·简体中文·繁體中文 모두 동일 분량으로 갱신

### 테스트 자동화 강화

- 신규 회귀 테스트 클래스 2개 추가
  - `TestV104Regression` — 소스 코드 검증 (14개 테스트)
    - D: alchemy 튜플 반환 + `_detect_encoding` 제거 + 호출부 언패킹
    - A: 콤보박스 + codec 매핑 + 델리게이트 색상/라벨
    - B: `alchemy_check_encoding_compat` 정의 + `_on_merge_done` 호출 + 다국어 키
    - C: 4단계 색상 분기 + 툴팁 다국어 키
    - 초판 피드백: `_dlg_question` rich_text 파라미터 + alchemy CJK 폴백 루프
  - `TestV104RegressionModule` — 모듈 로드 기반 (7개 테스트)
    - APP_VERSION 정확히 '1.0.4'
    - alchemy가 실제 `(str, float)` 튜플 반환
    - `alchemy_check_encoding_compat` 실제 동작 (5-tuple: 한글→Shift-JIS 손실 감지, UTF-8 통과, 샘플 5개 제한)
    - B 옵션 개선: 영향받는 총 글자 수가 실제 ? 대체 개수와 일치 (교차 검증)
    - 초판 피드백: ASCII로 시작하는 Shift-JIS 파일 감지 검증
- v1.0.3 기존 테스트 중 시그니처 변경 영향 11개 업데이트 (의도 유지)
  - `TestAlchemyDetectEncoding` 5개 (utf8_bom / utf16_le_bom / utf16_be_bom / pure_utf8 / returns_string) — 튜플 호환 헬퍼로 첫 요소 추출
  - `TestBulkFixerFileIO` 3개 (utf8_bom_roundtrip / utf16_le_roundtrip / utf16_be_roundtrip) — `enc = detected[0] if isinstance(...) else detected` 패턴 적용
  - `TestV103RegressionModule.test_app_version_is_103` — "정확히 1.0.3" → "1.0.3 이상"으로 완화 (V012/V100 패턴과 일관)
  - `test_alchemy_detect_encoding_utf16_le/be` — 튜플 반환 호환 패턴 적용

### 알려진 이슈 (미수정 — 동작에 영향 없음)

- `zh_cn` 사전이 두 블록으로 나뉘어 188개 키 중복 정의됨 (v1.0.2부터 식별)
  - 모든 중복 키가 같은 값으로 정의되어 있어 동작 정상
  - 향후 사전 정리 PR 별도 진행 (회귀 위험으로 v1.0.4 범위에서도 제외)

### 검증 범위

- **단위 테스트**: 472개 (전체), V104 신규 21개 포함 — 실패 0 / 오류 0
  - v1.0.3: 451개 → v1.0.4 초판: 467개 → v1.0.4 최종: 472개 (초판 피드백 + UX 개선 반영)
- **실기 검증**: 25개 인코딩 샘플 파일 드래그 감지, 한글→Shift-JIS 저장 경고 동작, 저장 결과물 재드롭 시나리오
- **구조적 안전성**:
  - 콤보박스 기존 인덱스 0~4 보존 → 설정 저장값 호환
  - `alchemy_detect_encoding` 호출부 4곳 모두 튜플 언패킹 적용 (누락 없음)
  - `_detect_encoding` 메서드 완전 제거 (잔재 0건)
  - 회귀 테스트로 위 구조 자동 검증

---

## v1.0.3 (2026-04-18) — 인코딩 감지 버그 수정

### 버그 수정

- **Text Fixer·Bulk Fixer의 UTF-16 / CJK 인코딩 처리 실패** (`L7253`, `L8193`, `L8628`)
  - UTF-16 LE/BE, Shift-JIS, GBK, Big5 인코딩 파일이 깨진 상태로 저장되던 문제
  - 원인: 3곳의 인코딩 감지 로직이 `('utf-8-sig', 'utf-8', 'cp949', 'euc-kr', 'latin-1')`만 시도
    - UTF-16 계열 누락 → BOM 검출 못하고 다른 인코딩으로 오해
    - 비-한국어 ANSI 누락 → Shift-JIS·GBK·Big5 파일 실패
    - `latin-1`이 폴백 → 모든 바이트를 무조건 "디코딩 성공"시켜 깨진 채 처리됨
  - 수정: 3곳 모두 기존 `alchemy_detect_encoding()` 함수를 재사용하도록 통일
    1. `TextFixerPanel.load_file()` (L7253) — 단일 파일 로드
    2. `BulkFixerWorker.run()` (L8193) — 일괄 처리
    3. `BulkFixerPanel._on_file_selected()` (L8628) — 미리보기 ⭐
  - `latin-1` 폴백 제거, `shift_jis`/`gbk`/`big5` 폴백 추가 (5개 언어 지원 일치)
  - 영향 범위: 5개 언어 × UTF-16 LE/BE + 일본어·중국어 간체·번체 ANSI = 12개 케이스

- **`alchemy_detect_encoding()`의 GBK/Big5/Shift-JIS 감지 실패** (`L3456`)
  - chardet이 CJK 인코딩에 대해 자주 0.5~0.7 신뢰도를 반환하는데,
    기존 임계값 0.7 엄격 기준 때문에 GBK/Big5 파일이 `cp949` 폴백으로 잘못 디코딩
  - 수정: CJK 인코딩 화이트리스트 추가, 이들은 0.5 이상이면 신뢰하도록 완화
    - `gb18030`, `gbk`, `gb2312`, `big5`, `shift_jis`, `shift-jis`, `euc-jp`
  - `gb18030`/`gb2312` → `gbk` 정규화, `shift-jis` → `shift_jis` 정규화 추가
  - 기타 인코딩은 기존 0.7 임계값 유지 (보수적 처리)
  - Text Converter(L4288)에도 함께 적용됨 — 모든 탭 일관 동작

### 테스트 자동화 강화

- `TestBulkFixerFileIO`에 인코딩 라운드트립 테스트 5개 추가
  - `test_utf8_bom_roundtrip`, `test_utf16_le_roundtrip`, `test_utf16_be_roundtrip`
  - `test_cp949_roundtrip`, `test_5_languages_utf8`
- 신규 회귀 테스트 클래스 2개 추가
  - `TestV103Regression` — 소스 코드에 `latin-1` 재등장 여부 검출 (7개 테스트)
  - `TestV103RegressionModule` — `alchemy_detect_encoding()` 동작 검증 (3개 테스트)
- 기존 v0.12.0 / v1.0.0 회귀 테스트의 APP_VERSION 하드코딩 체크를
  "v1.0.0 이상"으로 완화 (향후 버전 호환성 확보)
- **테스트 샘플 데이터를 완전 중립 텍스트(CC0)로 교체** — 저작권 분리
  - 기존: 실존 소설 텍스트를 테스트 입력으로 사용
  - 교체: 서사·캐릭터·세계관 요소가 없는 완전 중립 샘플
    (예: "테스트 샘플 [1] 섹션 A에서 섹션 B까지", "응답자/검사자" 같은 일반 역할만 등장)
  - `test_file_nexus.py` 상단에 `SAMPLE_KO_*` 상수 섹션 추가 (총 11개 상수)
  - 13곳의 테스트에서 상수 참조 방식으로 변경 → 저작권 이슈 없는 공개 가능한 구조

### 알려진 이슈 (미수정 — 동작에 영향 없음)

- `zh_cn` 사전이 두 블록(L2013~L2204, L2204~L2462)으로 나뉘어 188 개 키가 중복 정의되어 있음 (v1.0.2에서 식별됨)
  - 모든 중복 키가 같은 값으로 정의되어 있어 동작 정상
  - 향후 사전 정리 PR 별도 진행 권장 (회귀 위험으로 v1.0.3 범위에서도 제외)

### 검증 범위

- **입력**: 5개 언어 × 5개 인코딩 = 25개 테스트 파일 (수동 검증)
  - 한국어·English·日本語·简体中文·繁體中文
  - UTF-8 / UTF-8 BOM / UTF-16 LE / UTF-16 BE / ANSI(각 언어별)
- **수정 전 결과**: 13/25 (52%) — UTF-16 전체 + 일본어/중국어 ANSI 깨짐
- **수정 후 결과**: 25/25 (100%) ⭐
- **2종 프리셋** 모두에서 동일하게 100% 달성 (Normal, Novel)
- **정상 작동 확인된 탭** (수정 불필요)
  - Text Merger: 25/25 통과 (기존에 이미 `_detect_encoding()` 사용 중)
  - Text Converter: alchemy 개선으로 함께 혜택

---

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
