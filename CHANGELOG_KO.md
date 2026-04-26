# Changelog

본 프로젝트의 주요 변경사항을 버전별로 기록합니다.

각 버전의 코드 변경 상세는 [`RELEASE_NOTE_vX.X.X.md`](./) 파일을 참조하세요.
포맷은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/)를 따릅니다.

---

## [Unreleased]

Post-v1.0.10 docs 정리 트랙 — **메인 코드 + 부속 문서 영문 기본 결 전환**으로 비한국어권 개발자의 접근성 결을 두텁게 차리고 SignPath OSS Sponsorship 검토 신뢰도 결을 보강. 본 트랙은 SignPath 승인 결과가 도달한 시점에 v1.0.11로 릴리즈될 결.

### Changed
- **메인 소스 코드 영문화** — `FileNexusSuite.py`의 한국어 주석·docstring·디버그 로그 1,133줄을 영문으로 변환. 사용자 노출 UI 문자열, 언어별 분기 도움말 본문, 사전 키/값(의도적 한국어 결)은 보호. 안전을 위해 두 commit으로 분리 봉인: Step 1+2 (506줄, `f54bc81`) + Step 3 final (627줄, `177598b`). 청크별 `ast.parse` 통과 + 작업 폴더·Git 폴더 양쪽 ×2에서 `test_file_nexus.py` 535/0/0/0 결로 검증 마감.
- **STORY.md를 이중언어 EN/KO 서사 결로 전환** (`c469f6b`) — 프로젝트 서사를 단락별로 영문 우선 + 한국어 병기 결로 차려, 영어 사용자와 한국어 사용자 양쪽 모두 접근 가능하게 결을 펴짐.
- **README.txt를 영문 기본 + 다국어 라벨 결로 전환** (`3922250`) — 배포 ZIP에 동봉되는 README를 영문 본문 + 비한국어 사용자를 위한 짧은 다국어 라벨 결로 정리.
- **빌드 메타데이터 영문화** (`7ca4f734`) — `version_info.txt`, `requirements.txt`, 빌드 스크립트의 한국어 결을 영문으로 전환. 한국어 사용자에게 의도적으로 노출되는 결만 남김.
- **README.md STORY.md 참조 결 정밀화** (`91f67b5`) — `*(Korean only)*` → `*(English & Korean)*`로 정정. `c469f6b`에서 도입된 STORY.md 이중언어 구조 결을 정확히 반영.

### Documentation
- **다중 라인 docstring 닫음 결 식별 패턴**을 Console Release Manual에 추가 (v1.2 §5.9) — Step 3a 시행착오에서 발견된 *`"""` 닫음 위치 결의 두 패턴* (줄 끝 닫음 vs 별도 줄 닫음) 자국. 미래 일괄 리팩토링 트랙에서 같은 함정을 회피하도록 사전 점검 결의 명령어까지 포함.

---

## [1.0.10] — 2026-04-25

v1.0.10 — MIT 전환과 OSS 결의 시작점. v1.0.x 시리즈가 *"개인 작업툴 → OSS 공개"* 결의 전환점에 도달하는 릴리즈. 라이선스 전환(Freeware → MIT) + LGPL 호환성 명시적 문서화 + SignPath OSS Sponsorship 신청 트랙의 묶음.

### Changed
- **라이선스 전환: Freeware (source available) → MIT License** — 저작권 고지 유지 시 사용·수정·재배포·판매 모두 자유롭게 허용. 한림이 *"개인 작업 도구로 시작했지만, 같은 작업을 하는 다른 분들에게도 도움이 되기를"*이라는 결로 v1.0.x 시리즈 누적의 결과를 OSS 커뮤니티로 개방.
  - `LICENSE` 파일 — 자체 작성 Freeware 형식에서 MIT 표준 텍스트로 전환 (GitHub Licensee gem 정확 탐지). 한국어 안내 + Test Data Exception (CC0) 부록 보존
  - 5언어 `license_summary` 키 — *"무단 재배포·재가공·판매 금지"* → *"사용·수정·재배포·판매 모두 허용"* 정반대 의미로 재작성 (en/ko/ja/zh_cn/zh_tw)
  - `_build_license_html()` 본 프로젝트 항목 — `Freeware — Free for Personal & Commercial Use` → `MIT License` + note 한/영 단락 재작성 ("이타심" 한 줄 신규 추가, AI 페어 프로그래밍 결 보존)
  - `README.md` / `README_EN.md` 라이선스 섹션 본문 + license 뱃지 + LICENSE 파일 링크
  - `README.txt` 푸터 `Freeware (Personal & Commercial)` → `MIT License`
- **`Copyright © 2026 Hanrim. All rights reserved.` → `Copyright © 2026 Hanrim`** — "All rights reserved" 표기 6곳 일괄 정리. 1910년 부에노스아이레스 협약 잔재로 현대 저작권법에 법적 의미 없음 + MIT 라이선스 의미와 결 일관성. 적용 위치: `version_info.txt` `LegalCopyright` / `FileNexusSuite.py` L1 헤더 / `FileNexusSuite.py` L14637 `_footer_copyright` / `FileNexusSuite.py` L14325 `_build_license_html()` 본 프로젝트 항목 / `README.md` / `README_EN.md`
- **README 뱃지 시각 체계 재정립** — *"v1.0.10이 v1.0.x 시리즈에서 OSS 도착점"*이라는 결을 색의 흐름으로 표현. 카테고리별 색상 정합:
  - 정체성 (`CC785C` Anthropic 구릿빛): AI pair Claude / Download CTA
  - OSS 활기 (`97CA00` 짙은 OSS 초록): tests / **license MIT** ← v1.0.10 신규 자리
  - 시작점 (`7B6FA3` 보라): version 1.0.10 (이전 license에서 재배치)
  - 브랜드 인용 (외부 표준 그대로): python / PySide6 / platform / CI badge

### Added
- **LGPL 호환성 명시적 문서화** — `_build_license_html()` PySide6 (LGPL-3.0) / chardet (LGPL-2.1) note 필드에 LGPL replacement 안내 1문장씩 추가. *"File Nexus Suite is built with PyInstaller. Users may replace this LGPL library by rebuilding from source — see the GitHub repository for build instructions."* PyInstaller `--onedir` 빌드 모드의 `_internal/` 폴더 분리 구조에서 사용자가 LGPL 라이브러리를 직접 교체 가능함을 명시. LGPL §3 의무를 암묵적 충족(GitHub source 공개)에서 명시적 충족으로 강화하여 회색지대 영구 차단
- **`README.txt` `_internal` 폴더 보호 안내** — `⚠ 같은 폴더의 _internal 폴더는 프로그램 실행에 필요한 파일들이 있는 곳입니다. 삭제하지 마세요.` 한/영 양쪽 추가. PyInstaller `--onedir` 빌드 모드에서 사용자가 `_internal/` 폴더를 *"필요 없어 보이는 데이터"*로 오해하여 삭제할 위험 차단. README.txt가 자체 정체성(*"포장지 안내 라벨"*)에서 *"`_internal` 보호 장치"*라는 진짜 결을 정확히 갖추는 의도-산출물 정합 작업
- **README "이타심" 한 줄** — `README.md` / `README_EN.md` 라이선스 섹션 + `_build_license_html()` 본 프로젝트 항목 note에 일관 추가. *"개인 작업 도구로 시작했지만, 같은 작업을 하는 다른 분들에게도 도움이 되기를 바라며 MIT 라이선스로 공개합니다."* GitHub README와 앱 내 라이선스 페이지가 같은 결의 메시지를 사용자에게 전달

### Deferred
- **SignPath OSS Sponsorship 신청** — v1.0.10 Release publish 직후 `signpath.org` 신청서 제출. v1.0.10이 *"Latest release: first MIT release"*로 신청서에 기록됨으로써 검토 신뢰도 강화. 승인은 외부 절차(평균 1주 검토)로 진행되며, **승인 후 CI 통합 + 첫 서명 산출물은 v1.0.11에서 별 트랙으로 진행**. 본 릴리즈는 OSS Sponsorship의 자격 조건(OSI-approved license, no malware, maintained, released, documented, verifiable build) 6개 모두 충족하는 기반 마련

### Tests
- **535 passing** (v1.0.9와 동일), 58개 클래스, 실패·오류·스킵 0 (한림 로컬 + Git 폴더 이중 검증)
- v1.0.10 변경 영역(라이선스 텍스트 5언어 + 라이브러리 note 2곳 + 푸터 "All rights reserved" 제거 + 버전 갱신)이 자동 테스트 invariant와 충돌 0 — v1.0.4 작업 시점에 도입된 정수 튜플 비교 패턴 (`parts = tuple(int(p) for p in ver.split('.'))`)이 `1.0.10` 같은 두 자릿수 패치 버전을 미리 대비해둔 결과로, 모든 버전 비교 invariant가 자연 통과
### Documentation
- `FileNexusSuite.py` `APP_VERSION` 상수 `1.0.9` → `1.0.10` 갱신 (L76). f-string으로 참조되는 도움말 창 타이틀 5개 언어 + 사이드바 버전 라벨이 자동 일관 갱신됨
- `version_info.txt` 4곳 `1.0.9`/`1.0.9.0` → `1.0.10`/`1.0.10.0` 갱신 (`filevers` / `prodvers` 튜플, `FileVersion` / `ProductVersion` 문자열)
- `README.md` / `README_EN.md` version 뱃지 1.0.9 → 1.0.10 동기화 (영혼의 반쪽 원칙 적용)
- `README.txt` 첫 줄 v1.0.9 → v1.0.10 갱신

### File Changes
- `FileNexusSuite.py`: 14,850 → 14,850 줄 (라인 수 변화 없음 — 6개 영역 모두 *줄 수 동일한 부분 교체*. `note` 필드의 `\n\n`은 한 줄 안의 긴 문자열이라 라인 수에 영향 없음)
- `LICENSE`: 76 → 68 줄 (-8: third-party libraries 목록 영/한 양쪽 제거 — 앱 내 `_build_license_html()` + README가 단일 진실 원천 책임)
- `version_info.txt`: 버전 4곳 + `LegalCopyright` 갱신만
- `README.md` / `README_EN.md`: 라이선스 섹션 본문 재작성 + 뱃지 3개 색상/텍스트 갱신 + Copyright + LICENSE 링크
- `README.txt`: v1.0.10 갱신 + `_internal` 보호 안내 한/영 + 푸터 MIT

### Post-Release Documentation

v1.0.10 Release publish 후 외부 OSS-facing 결의 정합 작업으로 4개 docs commit 추가 (버전 번호는 v1.0.10 그대로 유지, 본 카테고리는 v1.0.10 풀코스 마감 시점 이후 누적). SignPath 검토자·외부 OSS 검토자가 저장소 도착 시 영문 첫 화면 + 영문 정책 문서 도달 가능한 결.

- **`1c2c8e8`** — README에 SignPath 코드 서명 안내 추가 (OSS Sponsorship 신청 준비). v1.0.10 신청서 §9 Reputation에서 README가 SignPath 트랙 진행 결을 외부 검토자에게 도달 가능하도록 명시
- **`ceef147`** — README 영문 기본 결 전환 (rename `README.md` → `README_KO.md`, `README_EN.md` → `README.md`). Git rename 정확 인식 (3 files / +245 / −245). 저장소 첫 화면이 영문 README로 도달, 외부 OSS-facing 결의 시작점
- **`0a936f3`** — `TEST_MANAGEMENT_POLICY.md` 영문 기본 결 전환. 한국어 원문은 `TEST_MANAGEMENT_POLICY_KO.md`로 사본 보존, 영문 신규 작성하여 같은 파일명에 덮어쓴 결로 외부 기본을 영문 결로 전환. SignPath 신청서 §9 Reputation의 `TEST_MANAGEMENT_POLICY.md` 클릭 시 영문 도착
- **`723219c`** — `TEST_MANAGEMENT_POLICY_KO.md` 한국어 사본 GitHub 추가 commit. `0a936f3` 시점에는 untracked 상태로 빠져 있었으나 후속 보충으로 영문 + 한국어 양쪽 사본이 GitHub에 도달

→ 4개 commit 모두 SSH 서명 + GitHub Actions CI 통과. 본 결로 v1.0.10 docs 정리 트랙 마감 도달, SignPath 검토 결과 대기 + v1.0.11 새 기능 트랙 진입 가능 상태.

상세: `RELEASE_NOTE_v1.0.10.md` (작업 폴더 전용, v1.0.10 풀코스 마감 시점 본문 — post-release docs는 본 카테고리 직접 명시)

---

## [1.0.9] — 2026-04-25

v1.0.x 시리즈 마무리 — 사후 정리 / 데이터 청소 카테고리. v1.0.8 인수인계 §5.1의 ACDG 4개 작업을 묶은 릴리즈.

### Added
- `build_pyinstaller.py` `--strict` 모드 신설 — 버전 일관성 검증 단계를 빌드 전(step 5)으로 분리하여 mismatch 발견 시 빌드 즉시 중단. PyInstaller 수십 초 + UPX 압축이 시작 전에 차단되어 시간/디스크 절약, 기존 빌드 산출물 보존. 신규 함수 `check_version_consistency(strict)` 추가, step 시퀀스 7→8단계로 재정렬.
  - `build.bat` wrapper에 `%*` 인자 패스스루 추가하여 `build.bat --strict` 직접 호출 가능
- `_t()` / `_rt()` 함수에 zh_cn → zh_tw fallback chain 추가 — zh_cn 사전에 미정의 키는 zh_tw로 1차 fallback, 최종은 ko fallback. v1.0.5부터 fallback이 ko 단일이었던 한계 보완.
- `test_file_nexus.py` `test_zh_cn_fallback_to_zh_tw` 신규 invariant — `_t()`/`_rt()` 두 함수 모두에 fallback 패턴이 살아있고 검증 대상 키가 존재하는지 검증. fallback 메커니즘이 향후 누군가의 실수로 깨지면 CI에서 즉시 자동 감지

### Changed
- `zh_cn` 사전에서 zh_tw와 값이 100% 동일한 **40개 키 정리** — fallback chain 도입으로 사용자 동작 영향 0이 정의상 보장됨 (v1.0.8 인수인계 §5.1.G "188개" 명세는 데이터로 검증되지 않아 현실 데이터 47개 → invariant 보호 7개 제외 → 40개로 정직하게 재정의)
  - 정리 대상: 이모지/심볼 (▶, UTF-8/UTF-16 등 인코딩 라벨 일부), 짧은 단어 (取消/完成/字/行 등), 자릿수 표기 (最少2位/固定3位 등), 자리표시자 (例: jpg, png, gif 등), 테마명 (深色/蜂蜜/薰衣草 등)
  - invariant 보호로 제외된 7개: `dlg_yes`/`dlg_no`/`dlg_warning` (다이얼로그 공통), `conv_status_done`/`conv_sub_epub2txt`/`conv_sub_txt2epub` (변환 상태), `rename_cancel` (취소) — 핵심 UI 키는 5언어 직접 정의 유지
- `test_file_nexus.py` `test_all_langs_same_key_count` 재설계 — 대칭 강제(5언어 동일 키 수)에서 비대칭 허용(zh_cn은 zh_tw 부분집합 허용 + ko/en/ja/zh_tw만 동일 키 수)으로 전환. zh_cn fallback 메커니즘과 정합성 확보
- `test_file_nexus.py` `test_all_languages_have_similar_key_count` 갱신 — zh_cn은 fallback chain 사용을 명시하여 키 수 검증에서 제외, 다른 4언어만 ≤5 차이 강제 (v1.0.5 시절 의도 유지)
- `README.md` / `README_EN.md` Copyright 및 제작자 표기 — `Yongwoo Shin (Hanrim)` → `Hanrim` 단독 (4곳). v1.0.8 §4.36 매체별 표기 정책에 따른 GitHub-facing 자료 동기화. 외부 격식 매체(포트폴리오, 기획서)는 풀네임 유지

### Verified
- `HelpDialog` 점검 — v1.0.8 SettingsDialog의 옵션 C 패턴(페이지 lazy 재생성)과 같은 구조적 결함 잠재 가능성 진단. 호출 방식 비교 결과 두 다이얼로그가 본질적으로 다른 패턴(HelpDialog는 `exec()` 모달 + 시그널 연결 0개 vs SettingsDialog는 "창 유지" + 시그널 3개)임이 확인되어 옵션 C 적용 불요. 점검 자체가 v1.0.9 §5.1.D 산출물 (코드 변경 0줄, 잠재 결함 없음을 데이터로 명시)

### Tests
- **535 passing** (+1 vs v1.0.8), 58개 클래스, 실패·오류·스킵 0 (한림 로컬 + Git 폴더 이중 검증)
- 회귀 발견 → 수정 사이클: §5.1.G 1차 적용 후 v1.0.5 회귀 테스트 6개 FAIL 발견 (`merge_enc_utf8`/`utf16`/`shiftjis` invariant 보호 키 정리에서 누락) → 정리 대상 47→40개로 축소 + invariant 갱신 → 535/0/0/0 통과
- 자동 테스트 시뮬레이션 단계 통과 (PySide6 의존성 없는 invariant 모두 직접 검증)

### Documentation
- `FileNexusSuite.py` `APP_VERSION` 상수 `1.0.8` → `1.0.9` 갱신 (L76). f-string으로 참조되는 도움말 창 타이틀 5개 언어 + 사이드바 버전 라벨이 자동 일관 갱신됨
- `version_info.txt` 4곳 `1.0.8`/`1.0.8.0` → `1.0.9`/`1.0.9.0` 갱신 (`filevers` / `prodvers` 튜플, `FileVersion` / `ProductVersion` 문자열)
- `README.md` / `README_EN.md` version 뱃지 1.0.8 → 1.0.9, tests 뱃지 534 → 535 동기화
- `README.txt` 첫 줄 v1.0.8 → v1.0.9 갱신

### File Changes
- `FileNexusSuite.py`: 14,883 → 14,850 줄 (-33: zh_cn 40개 키 제거 -40 + `_t()`/`_rt()` fallback 보강 +6 + APP_VERSION 갱신 등)
- `test_file_nexus.py`: 4,553 → 4,589 줄 (+36: 새 invariant `test_zh_cn_fallback_to_zh_tw` +20 + 기존 invariant 2개 갱신 +16)
- `build_pyinstaller.py`: 262 → 284 줄 (+22: `check_version_consistency` 신규 함수 + `--strict` CLI 파싱 + step 시퀀스 재정렬)
- `build.bat`: `%*` 인자 패스스루 1글자 추가
- `README.md` / `README_EN.md`: 표기 4곳 + 뱃지 2곳 갱신
- `version_info.txt`, `README.txt`: 버전 갱신만

### Known Issues / Deferred to v1.1.x
- **`ko` 사전 1개 부족 단서** — fail_log 메시지에서 `'ko': 403` (다른 4언어는 404)로 1개 차이가 발견됨. v1.0.7 §추가 작업 후 어디선가 발생한 것으로 추정. `_count_keys_per_language` 정규식이 멀티라인 값에서 키 1개를 못 잡는 가능성도 있음. v1.0.9 §5.1.G 스코프 외이며 v1.1.x 후보로 이월
- **Claude Desktop 4/14 리디자인 부수 효과** (v1.0.9 외부 발견) — 클라이언트 단에서 메시지 입력의 마크다운 auto-linking이 더 적극적으로 켜진 것으로 추정. 운영상 백틱(`` ` ``) 감싸기 + 긴 출력은 파일 업로드 우회 패턴으로 대응

상세: `RELEASE_NOTE_v1.0.9.md` (작업 폴더 전용)

---

## [1.0.8] — 2026-04-25

### Fixed
- **설정 다이얼로그 라벨/프레임 color 잔재 버그** (v1.0.5부터 존재, 5개 릴리즈 살아남은 본과제) — 페이지 lazy 재생성 메커니즘 도입으로 **구조적 해결**. v1.0.7 §11.3에서 이월된 본과제로, v1.0.6 세션에서 시도한 4가지 접근(QTimer 지연 / unpolish-polish / QApplication 전역 재적용 / findChildren update) 모두 실패한 후 v1.0.8에서 사전 조사 → 코드 진단 → 옵션 재평가의 정직한 흐름으로 풀어냄.
  - 코드 진단 결과 §11.1의 "영향 위젯 3가지"가 실제로는 **22개 위젯 갱신 누락**의 빙산 일각이었음이 드러남 (페이지 내부 거의 모든 inline stylesheet 위젯이 생성 시점 테마로 영구 고정되는 구조적 문제)
  - 옵션 A(Targeted 갱신, ~60~80줄) 대신 옵션 C(페이지 재생성, +17줄)로 변경 — 코드 변경량 1/4, 누락 재발 영구 방지
  - 메커니즘: 워크어라운드(설정창 재오픈)와 동일한 패턴을 다이얼로그 내부에서 자동화. §11.3에서 한림이 사전 후보로 적어둔 방향과 일치
- (사이드 결함) `_ver_lbl` (사이드바 하단 버전 라벨) 테마 전환 갱신 누락 보완. v1.0.6에서 "갱신용 self 저장"이라 주석 달아놓고도 `_refresh_theme`에서 호출 누락된 결함이 옵션 C 작업 중 코드 진단으로 발견되어 동시 해결.
- (사이드 결함) 출력 폴더 버튼(`_odir_btn` / `_odir_reset_btn`) 텍스트가 언어 변경 시 갱신되지 않던 결함 해소. v1.0.6 D-2 작업에서 `_retranslate_dialog`은 `self._odir_btn`을 참조하는데 `_page_language`에서는 로컬 변수로만 만들어 `hasattr` 검사로 silently fail 하던 잔재. 페이지 재생성으로 자동 해결.

### Changed
- `SettingsDialog._refresh_theme` / `_retranslate_dialog` 책임 명확화 — 다이얼로그 외곽 위젯만 책임지도록 단순화. 페이지 내부 위젯의 stylesheet·텍스트 갱신은 신규 `_recreate_pages` 메서드가 일괄 처리.
  - `_refresh_theme`: 32줄 → 30줄 (페이지 내부 갱신 루프 제거 + `_ver_lbl` 갱신 추가 + `_recreate_pages()` 호출 추가 + 주석)
  - `_retranslate_dialog`: 48줄 → 16줄 (페이지 내부 텍스트 갱신 모두 `_recreate_pages`에 위임)
- `_apply_theme_now`에서 `for n, card in self._cards.items(): card.set_selected(...)` 1줄 제거. 페이지 재생성 시 새 카드들이 `selected=(name==self._chosen)`로 자동 생성되므로 불필요.

### Added
- `SettingsDialog._recreate_pages()` 신규 메서드 — 페이지 4개 destroy + recreate.
  - 7단계 안전 흐름: 단축키 캡처 안전 종료 → 출력 폴더 임시 입력값 보존 → 기존 페이지 위젯 제거(`removeWidget` + `deleteLater`) → 컨테이너 dict 초기화 → 새 페이지 생성 → 임시 입력값 복원 → 현재 페이지 전환
  - 워크어라운드(설정창 재오픈) 메커니즘의 명시적 자동화. 향후 페이지에 위젯 추가 시 `_refresh_theme` / `_retranslate_dialog`에 갱신 라인 누락될 위험 영구 방지
  - **옵션 C 신규 동작**: 출력 폴더 입력란에 사용자가 입력했지만 적용 안 한 텍스트도 페이지 재생성 시 보존됨 (v1.0.7 동작 대비 개선)
- `test_file_nexus.py` `TestSettingsDialogStructureInvariant` 클래스 (§추가Q, +72줄) — v1.0.8 옵션 C 메커니즘 구조 invariant 3개:
  - `test_settings_dialog_has_recreate_pages` — `_recreate_pages` 메서드 존재 검증
  - `test_refresh_theme_calls_recreate_pages` — `_refresh_theme` 본문에 `self._recreate_pages()` 호출 포함 검증 (`inspect.getsource` 기반)
  - `test_retranslate_dialog_simplified` — `_retranslate_dialog`이 페이지 내부 attribute 9개(`_theme_page_title`, `_lang_page_title` 등)를 직접 갱신하지 않음 검증
  - TEST_MANAGEMENT_POLICY §3 4번 원칙(신규 기능에 대한 자동 커버리지 명시) 적용. 향후 누군가의 실수로 옵션 C 메커니즘이 깨지면 CI에서 즉시 자동 감지

### Tests
- **534 passing** (+3 vs v1.0.7), 58개 클래스, 실패·오류·스킵 0 (한림 로컬 실측)
- 옵션 C 패치 직후 531/0/0/0 유지 → invariant 3개 추가 후 534/0/0/0
- 수동 QA: 라이트↔다크 양방향 정상 + 단축키 캡처 중 적용 안전 + 출력 폴더 임시 입력 보존 모두 통과 (한림 검증)

### Documentation
- `FileNexusSuite.py` `APP_VERSION` 상수 `1.0.7` → `1.0.8` 갱신 (L76). f-string으로 참조되는 도움말 창 타이틀 5개 언어 + 사이드바 버전 라벨이 자동 일관 갱신됨
- `version_info.txt` 4곳 `1.0.7`/`1.0.7.0` → `1.0.8`/`1.0.8.0` 갱신 (`filevers` / `prodvers` 튜플, `FileVersion` / `ProductVersion` 문자열). PyInstaller 빌드 시 Windows `.exe` 속성 창의 메타데이터 정합 확보
- `README.md` / `README_EN.md` version 뱃지 1.0.7 → 1.0.8, tests 뱃지 531 → 534 동기화
- `README.txt` 첫 줄 v1.0.7 → v1.0.8 갱신

### File Changes
- `FileNexusSuite.py`: 14,866 → 14,883 줄 (+17: `_recreate_pages` 신규 메서드 +35 + 외곽 단순화 -28 + 주석 +6 + APP_VERSION 갱신 등)
- `test_file_nexus.py`: 4,481 → 4,553 줄 (+72: `TestSettingsDialogStructureInvariant` 신규 클래스)
- `version_info.txt`, `README.md`, `README_EN.md`, `README.txt`: 버전 갱신만

상세: `RELEASE_NOTE_v1.0.8.md` (v1.0.8 릴리즈 준비 단계에서 작성 예정)

---

## [1.0.7] — 2026-04-22

### Fixed
- (세션 1) TextMergerPanel `_set_scan_ui` 데드 `or True` 조건 제거
- (세션 1) TextConverterPanel `ConvertWorker.sig_file_progress` disconnect 누락 보완 (5:5 대칭)
- (세션 1) TextFixerPanel `_run` 내부 워커 정리에 terminate 폴백 추가
- (CI 도입 준비) `test_file_nexus.py` 커스텀 러너 exit code 계약 보완 — 실패/오류 시 `sys.exit(1)`, CI 뱃지 정확성 보장 (기존에는 실패해도 exit 0 반환하여 CI가 거짓 초록불을 띄울 수 있었음)
- (CI 도입 준비) `requirements.txt`에 `python-hwpx>=2.9.0` 누락 보완 (v1.0.6 HWPX 입력 지원 의존성이 README·기술 스택에만 명시되고 requirements에서 빠져 있던 불일치 해소)
- (CI 도입 준비) `FileNexusSuite.py` L76 `APP_VERSION` 상수 `1.0.6` → `1.0.7` 갱신 (세션 3 당초 누락, 릴리즈 직전 한림의 `findstr` 검증으로 발견). f-string으로 참조되는 앱 타이틀·도움말 창 버전 표시가 자동 일관 갱신됨
- (CI 도입 준비) `version_info.txt` 4곳 `1.0.6`/`1.0.6.0` → `1.0.7`/`1.0.7.0` 갱신 (`filevers` / `prodvers` 튜플, `FileVersion` / `ProductVersion` 문자열). PyInstaller 빌드 시 Windows `.exe` 속성 창의 "파일 버전" / "제품 버전" 메타데이터가 v1.0.7로 표시되도록 정합 확보
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
  - 러너: `windows-latest` 단일 (한림 로컬 Windows 환경과 일치, 529/0/0/0 재현 최우선)
  - Python: 3.10 단일 (한림 로컬 Python 3.10.11과 일치)
  - 트리거: main 브랜치 push/PR + `workflow_dispatch`(수동)
  - 의존성: `pip install -r requirements.txt` 단일 진실 원천
- (CI 도입) `README.md` 뱃지 확장 — CI 상태 뱃지 + 529 tests passing 뱃지 추가, 설치 명령어를 `pip install -r requirements.txt`로 단순화, version 뱃지 1.0.6 → 1.0.7 갱신

### Audit Fixes (세션 3)
세션 2 말미의 전수 감사에서 17건 고아로 추정된 번역키 중 **2건이 β 프로토콜 조사 과정에서 실제로는 활성 키**임이 확인됨 — 감사가 동적 키 생성 패턴을 놓친 결과.
- `conv_sub_txt2epub` / `conv_sub_epub2txt` — `TextConverterPanel.retranslate()` L6560의 `_t('conv_sub_' + val)` 동적 디스패치로 정상 사용 중
- 원 감사 17건 → **실제 데드 15건**으로 수정
- 본 2건은 `test_all_langs_have_text_converter_keys` 대표 키로 편입되어 향후 동적 생성 패턴도 invariant로 보호

### Deferred to v1.0.8
- 설정 다이얼로그 라벨 color 버그 재도전 (Phase 2 Completion Record §11.3 가이드 보존)
- v1.0.7 원 본과제였으나 17건 고아 노이즈 상태에서 난제 접근 시 판단 오류 위험이 있어 스코프 분리 — 고아 정리·invariant 재구성 완료 후 깨끗한 기반에서 재도전

### Tests
- **529 passing** (+2 vs v1.0.6), 57개 클래스, 실패·오류·스킵 0 (한림 로컬 실측)
- 세션 1·2: 527 passing 유지 (한림 로컬 0/0/0/0)
- 세션 3: invariant 재구성으로 구 7개 제거 + 신규 9개 추가 (`bulk_fixer_keys` 확장 유지) → Net +2 메서드
- 샌드박스 `TestTranslationCompleteness` 선택 실행: 12 tests passing (failure 0, error 0)

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
