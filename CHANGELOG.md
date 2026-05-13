# Changelog

[English](./CHANGELOG_EN.md) | **한국어**

본 프로젝트의 주요 변경사항을 버전별로 기록합니다.

각 버전의 사용자 안내는 [GitHub Releases](https://github.com/MerciHanrim/FileNexusSuite/releases) 페이지를 참조하세요.
포맷은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/)를 따릅니다.

**v1.0.x ~ v1.1.0 이력:** [`docs/changelog/CHANGELOG_archive_KO.md`](docs/changelog/CHANGELOG_archive_KO.md)

---

## [1.1.1] — 2026-05-13

v1.1.0의 *모듈화와 디자인 폴리싱* 다음 자리에서 도움말 모듈이 Qt Linguist 런타임 양식으로 마지막 합류하고 본체에 남아있던 i18n 결함이 정리되는 자리. 두 묶음(도움말 모듈의 5개 언어 분기 제거와 인스턴스 메서드 재구성, 본체 6곳의 한글 하드코드 `self.tr()`/`QT_TR_NOOP`/`QCoreApplication.translate` 정리)으로 구성. 한림(@MerciHanrim)과 Claude Opus 4.7의 페어 프로그래밍 합작품으로 v1.0.5부터 누적된 운영 패턴을 그대로 살린다 — 도움말 모듈 전환은 한림이 짚어주신 *도움말 시스템도 본체와 같은 Qt Linguist 워크플로로 통합하자*는 방향에서 출발해 인스턴스 메서드 재구성으로 자리잡았고, 본체 i18n 결함 정리는 도움말 버튼 툴팁 한 곳의 발견에서 본체 전체의 AST 기반 전수 검사로 확장된 자연스러운 호흡을 따랐다.

### Changed
- **도움말 모듈의 Qt Linguist 전환 마무리 (v1.1.1 다국어 트랙 — 도움말 모듈 합류)** — `fns_help.py`의 `_build_help_html()`이 5개 언어(ko/en/ja/zh_cn/zh_tw) Python 분기 약 1,100줄을 직접 보유하던 양식에서, `HelpDialog`의 인스턴스 메서드 세 개 (`_get_intro()`, `_get_sections()`, `_render_section()`)로 재구성됨. 모든 사용자 가시 도움말 콘텐츠는 영문 base + `self.tr()` wrap 양식으로 통일되어, 런타임에 `QTranslator`를 통해 `help_*.qm`으로 해석. `_section_icons` 매핑이 다국어 번역된 section title을 key로 lookup하던 양식에서 section index 기반으로 단순화 (`_SECTION_ICONS` 클래스 상수 8개 항목 — 언어 변경 시 lookup이 깨지지 않는 안정성 확보). `_render_section()`은 기존 `_build_help_html()` 내부의 헬퍼 함수와 `HelpDialog._build` 내부 인라인 렌더 로직 두 군데에 중복 존재하던 HTML 렌더를 `HelpDialog._render_section(entry)` 인스턴스 메서드로 통합, 단일 렌더 경로로 응집. 동시에 `_build_help_html()`의 legacy full-page HTML 렌더 경로(약 180줄, `_data_only=False` 분기)가 본체와 `preview_ui` 양쪽에서 호출되지 않아 통째로 제거되었고, `_get_help_data()` 모듈 함수도 제거. `fns_help.py`는 약 1,486 → 829줄로 축소 (-657줄, -44%). v1.1.0에서 본체 UI 문자열에 적용되었던 Qt Linguist 워크플로가 도움말 콘텐츠까지 일관되게 확장됨.
- **`LicenseDialog` 클래스 신설 — `build_html()` static 메서드 패턴** — 기존 `_build_license_html()` 모듈 함수가 `LicenseDialog` 클래스의 `build_html()` static 메서드로 이전. License HTML 빌드 책임이 단일 클래스에 응집되어, `SettingsDialog`의 License 탭(`SettingsDialog._page_license()` 경유)과 독립 다이얼로그(`preview_ui.py._show_license()` 경유) 양쪽에서 동일 메서드를 재사용. 라이선스 페이지 상단의 summary banner 한 줄("Licensed under the MIT License · Free to use, modify, distribute, and sell · Copyright notice must be retained.")이 기존 `QCoreApplication.translate()` 호출에서 영문 하드코드로 전환 — MIT 라이선스 자체가 영문 표준 법률 문서이므로 summary 한 줄의 번역 가치가 낮고, 영문 표기가 라이선스 페이지의 사실상 표준. `preview_ui.py._show_license()`가 18줄의 인라인 다이얼로그 빌드에서 `LicenseDialog(self).exec()` 한 줄로 단축.
- **본체 i18n 결함 정리 (v1.1.1 i18n 위생 트랙)** — v1.0.x 시절 단일 한국어 코드의 잔재로 본체에 남아있던 한글 하드코드 6곳이 정리됨. AST 기반 전수 검사(`audit_hardcoded_korean.py`, 아래 Added 참고)로 발견된 결함을 처리 패턴별로 분류해 적절한 wrap 방식 적용. **Pattern A (메서드 안, `self.tr()` 직접 적용)** — `AppSuite`의 도움말 버튼 setToolTip과 시작 로그 메시지가 `self.tr()`로 wrap, 본체 언어 설정에 따라 정상 다국어 표시. **Pattern B (모듈 레벨 함수, `QCoreApplication.translate` 사용)** — `epub_to_text()` 모듈 함수의 EPUB 메타데이터 `'저자: '` 출력이 `QCoreApplication.translate('EpubConverter', 'Author: ')`로 wrap, self가 없는 모듈 함수에 적용되는 표준 패턴. **Pattern C (클래스 변수, `QT_TR_NOOP`으로 mark only)** — `SettingsDialog._SECTIONS` 클래스 변수의 4개 사이드바 라벨(`'테마'`, `'언어 설정'`, `'단축키'`, `'라이선스'`)이 `QT_TR_NOOP('Theme')`/`QT_TR_NOOP('Language')`/`QT_TR_NOOP('Shortcuts')`/`QT_TR_NOOP('License')`로 mark, 실제 번역은 `__init__`/`_build`에서 `self.tr(label)` 호출 시점에 처리. `audit_hardcoded_korean.py`는 AST 기반이라 false positive 패턴(`LANG_NATIVE_FALLBACK`의 native locale name, `_combo_lang`의 EPUB 메타데이터, CSS font-family의 한글 폰트 식별자 3건)을 그대로 다시 검출하지만, 재실행 시 보고서의 false positive 목록을 가이드로 활용.
- **코드 위생 정리** — 사용되지 않던 모듈 코드 -45줄 제거, `svg_html_img` 호출은 no-op stub로 전환. 외부 사용자 가시 변화 없음, 후속 작업 시 참조점 보존.

### Fixed
- **Debug Log 토글 시 Text Converter Book Info 패널 레이아웃 깨짐** — Text Converter 탭의 우측 Book Info 패널에서 Title / Author / Language / Chapter Split 4개 입력 필드의 라벨이 입력 박스에 가려지던 현상. Debug Log 패널 토글로 메인 윈도우 세로 공간이 줄어들 때 widgets가 충분한 height를 못 받아 spacing이 collapse되는 결함. 수정 방법: Book Info 패널을 `ScrollHintArea`로 wrap하여 세로 공간이 줄어도 입력 박스의 height와 spacing이 보장되도록 처리, 동시에 우측 사이드바의 다른 2개 패널도 `ScrollHintArea`로 선제 wrap하여 동일 결함의 잠재적 재발을 차단. v1.1.0부터 존재하던 문제.
- **`preview_ui.py`의 dead `_t` import** — `preview_ui.py` L24에서 `FileNexusSuite`로부터 `_t` 심볼을 import하던 라인이 ImportError를 일으키던 상태. 본체에서 이미 `_t` 심볼이 사라졌으나 `preview_ui.py`만 import 목록 갱신을 누락했음. preview UI 안에서 `_t`가 실제로 호출되는 곳은 없는 dead reference. 수정: import 목록에서 `_t,` 제거. `preview_ui.py` 라인 수 약 753 → 738줄 (-15줄, `_show_license()` 단축 포함).

### Added
- **`audit_hardcoded_korean.py` 검사 도구** — `FileNexusSuite.py`에서 `self.tr()`/`QT_TR_NOOP`/`QCoreApplication.translate` wrap이 누락된 한글 string literal을 AST 기반으로 전수 검사하는 신규 도구. docstring 제외, 번역 호출의 인자 자동 판별. 본 릴리즈 작업 중 6개 진짜 결함과 3개 false positive를 분류한 가이드로 사용됨. 본체 코드 변경 후 동일 검사를 재실행해 새로운 i18n 결함을 조기 발견하는 용도로 재사용 가능. 검사 도구 정착 과정에서 상대 경로 fix 후속 처리.

### Tests
- **513 → 512 passing (한림 환경, -1 변화)**, 0 failures / 0 errors / 5 intentional skips. `TestBuildHelpHtml`의 재작성(아래)으로 인한 net 변화.
- **`TestBuildHelpHtml` 재작성 — Qt Linguist 런타임 양식** — 기존 9개 테스트 메서드는 `_build_help_html(_data_only=False, _lang=...)` 시그니처에 의존했으나, `_lang` 파라미터가 제거되면서 통째로 재작성. 새 양식은 `QTranslator` install/remove 사이클로 언어별 도움말 표시를 검증.
- **i18n 결함 정리 검증 테스트 추가** — 본체 한글 하드코드 6곳이 모두 적절히 wrap되었는지 AST 기반 검증 (`audit_hardcoded_korean.py` 통합); `LicenseDialog.build_html()` static 메서드 호출 가능성 검증 (인스턴스 생성 없이 호출 가능).

---

> 이전 버전들의 변경 이력은 [`docs/changelog/CHANGELOG_archive_KO.md`](docs/changelog/CHANGELOG_archive_KO.md)에서 확인할 수 있습니다.
