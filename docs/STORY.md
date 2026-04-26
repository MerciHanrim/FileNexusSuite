# File Nexus Suite — Design & Story

> This document is the project narrative covering File Nexus Suite's origin, development method, and safety design philosophy.
> For general usage, see [../README.md](../README.md); for v1.0.6 changes, see [../RELEASE_NOTE_v1.0.6.md](../RELEASE_NOTE_v1.0.6.md).
>
> 이 문서는 File Nexus Suite의 시작 동기, 개발 방식, 안전 설계 철학을 담은 프로젝트 서사입니다.
> 일반 사용 안내는 [../README.md](../README.md), v1.0.6 변경 사항은 [../RELEASE_NOTE_v1.0.6.md](../RELEASE_NOTE_v1.0.6.md)를 참조하세요.

---

## 1. Origin · 시작 동기

It didn't begin as a unified tool. The text merger **Forest of Letters**, the e-book converter **Alchemy of Words**, the filename organizer **River of Names**, the **Folder & File Batch Renamer**, and the line-break corrector **Text Fixer** (Garden of Lines) — single-purpose tools the author built for personal use had quietly grown to five.

처음에는 통합 도구가 아니었습니다. 텍스트 병합 도구 **Forest of Letters (활자의 숲)**, 전자책 변환 도구 **Alchemy of Words (언어 연금술)**, 파일명 정리 도구 **River of Names (흐르는 이름의 강)**, 폴더·파일 일괄 이름 변경 도구 **Folder & File Batch Renamer**, 그리고 줄바꿈 교정 도구 **Text Fixer (Garden of Lines, 줄의 정원)** — 이런 식으로 제작자가 개인적으로 쓰던 단일 기능 도구들이 어느새 5개로 늘어 있었습니다.

Each tool had its own identity, theme, and versioning system and had settled into daily use, but the friction of opening a different window, remembering a different shortcut, and configuring a different output folder each time kept growing. The theme cards and color system first attempted while building Folder & File Batch Renamer also gave conviction that they could serve as the visual identity of a unified tool, and from the thought "what if I unified them into one?" File Nexus Suite was born.

각각의 도구는 독립적인 정체성·테마·버전 체계를 가지고 일상에 자리잡았지만, 매번 다른 창을 띄우고 다른 단축키를 외우고 다른 출력 폴더를 설정하는 번거로움이 점점 커졌습니다. Folder & File Batch Renamer를 만들면서 처음 시도한 테마 카드와 컬러 시스템이 통합 도구의 시각적 정체성으로 자리잡을 수 있겠다는 확신도 더해졌고, "하나로 통합하면 어떨까?" 라는 생각에서 File Nexus Suite가 시작되었습니다.

The verified core logic of each tool was brought under one roof, and modernization from PyQt5 to **PySide6** (a Python GUI framework based on Qt 6) was carried out.

검증된 각 도구의 코어 로직을 한 지붕 아래로 모으고, PyQt5에서 **PySide6**(Qt 6 기반의 Python GUI 프레임워크)로 현대화하는 작업이 진행되었습니다.

The unification also produced an unexpected side effect. Once Text Fixer came under the same roof as the other tools, the thought "what if this ran on folders rather than one file at a time?" arose naturally, and a new tab called **Bulk Fixer** was created within the unified tool. Unification turned out to be more than just gathering tools — it became soil where new features could grow.

통합 과정에서 예상하지 못한 부수 효과도 있었습니다. Text Fixer가 다른 도구들과 같은 지붕 아래 들어오자 "이걸 한 파일씩이 아니라 폴더 단위로 일괄 처리하면 어떨까?" 라는 생각이 자연스럽게 떠올랐고, 그렇게 **Bulk Fixer**라는 새 탭이 통합 도구 안에서 새로 만들어졌습니다. 통합이 단순히 도구를 모으는 것을 넘어, 새로운 기능이 자랄 수 있는 토양이 되어준 셈입니다.

Wishing to share this same value with others who faced the same workflow friction, and with users beyond Korean, the project is released in five languages.

같은 워크플로우의 불편을 겪던 다른 사용자, 그리고 한국어 외의 언어를 사용하는 사용자에게도 같은 가치를 전하고 싶어 5개 언어로 공개합니다.

### 1.1 The Five Standalone Programs Before Unification · 통합 이전의 5개 독립 프로그램

| Original Program | Unified Tab |
|:---|:---|
| ![Forest of Letters](images/forest_of_letters_v1.2.7.png)<br>**Forest of Letters** (활자의 숲) v1.2.7 | Text Merger |
| ![Alchemy of Words](images/alchemy_of_words_v2.0.10.png)<br>**Alchemy of Words** (언어 연금술) v2.0.10 | Text Converter |
| ![River of Names](images/river_of_names_v2.0.8.png)<br>**River of Names** (흐르는 이름의 강) v2.0.8 | Tag Editor |
| ![Folder & File Batch Renamer](images/batch_renamer_v2.1.0.png)<br>**Folder & File Batch Renamer** v2.1.0<br>(The first tool to introduce the theme cards and 9-color theme system later adopted by File Nexus Suite · File Nexus Suite의 테마 카드·9개 컬러 테마 시스템이 처음 시도된 도구) | Batch Renamer |
| ![Text Fixer](images/text_fixer_v0.1.0.png)<br>**Text Fixer** (Garden of Lines, 줄의 정원) v0.1.0 | Text Fixer |

Each program operated as a standalone PyQt5-based tool before being migrated to PySide6 and unified into File Nexus Suite. **Bulk Fixer** is a feature newly created during unification, in addition to the five standalone tools.

각 프로그램은 PyQt5 기반 독립 도구로 운영되다가 PySide6로 마이그레이션되며 File Nexus Suite로 통합되었습니다. **Bulk Fixer**는 5개 독립 도구에 더해 통합 과정에서 새로 만들어진 기능입니다.

---

## 2. Development Method · 개발 방식

This project was developed through **pair programming with Anthropic's Claude**. [Hanrim](https://github.com/MerciHanrim) handled planning, UX design, feature specification, and quality management, while code writing was carried out in collaboration with AI.

본 프로젝트는 **Anthropic의 Claude와 페어 프로그래밍**으로 개발되었습니다. [Hanrim](https://github.com/MerciHanrim)이 기획·UX 설계·기능 명세·품질 관리를 담당하고, 코드 작성은 AI와 협업하여 진행했습니다.

The role division is clear. The human takes direction, priorities, architectural decisions, and quality judgment; the AI takes analysis, implementation, debugging, and test generation. Every design decision is reviewed and approved by the human, and the full source code is published in this repository for anyone to verify.

역할 분담은 명확합니다. 사람은 방향·우선순위·아키텍처 결정·품질 판단을 맡고, AI는 분석·구현·디버깅·테스트 생성을 맡습니다. 모든 설계 결정 뒤에는 사람의 검토와 승인이 있으며, 전체 소스 코드는 본 저장소에 공개되어 누구나 검증할 수 있습니다.

---

## 3. Safety Philosophy · 안전 설계 철학

Tools that modify files inherently carry the risk of data loss. Recognizing this, File Nexus Suite consistently applies **two meta-principles** across all tabs.

파일을 변경하는 도구는 본질적으로 데이터 손실 리스크를 가집니다. File Nexus Suite는 이를 인식하고 **두 가지 메타 원칙**을 모든 탭에 일관되게 적용합니다.

### 3.1 Meta-Principles · 메타 원칙

- 🔍 **Preview First · 미리보기 우선** — All destructive operations let you verify changes before and after execution.  
  모든 파괴적 작업은 실행 전 변경 전후를 확인할 수 있습니다.
- ↩️ **Undo Required · 실행 취소 필수** — Undo is provided for file-modifying operations such as renaming, tag editing, and merging.  
  이름 변경, 태그 편집, 병합 등 파일 변경 작업에 실행 취소를 제공합니다.

### 3.2 Additional Safety Design for Conversion Tools · 변환 도구의 추가 안전 설계

Tools that **create new files** — such as Text Fixer, Bulk Fixer, and Text Converter — have an additional layer of protection:

Text Fixer / Bulk Fixer / Text Converter처럼 **새 파일을 생성하는 도구**는 추가 보호 계층을 가집니다:

- 🛡️ **Original Untouched · 원본 무손상** — When an output folder is specified, the original files are not modified. The "overwrite original" option was deliberately removed to strengthen safety.  
  출력 폴더 지정 시 원본 파일은 손대지 않습니다. 안전성 강화를 위해 원본 덮어쓰기 옵션은 의도적으로 제거되었습니다.
- 🏷️ **Result Identification · 결과물 식별** — Converted files are automatically marked with prefixes such as `[Fixed]` to indicate that they need review.  
  변환된 파일은 `[Fixed]` 등의 접두사로 자동 표시되어 검수해야 할 파일임을 알립니다.
- 📁 **Output Path Separation · 출력 경로 분리** — Results are gathered into the `Output/` folder, clearly separated from the originals.  
  `Output/` 폴더로 결과물을 모아 원본과 명확히 분리합니다.

### 3.3 Text Fixer ↔ Bulk Fixer Recommended Workflow · Text Fixer ↔ Bulk Fixer 권장 워크플로우

Batch processing carries the inherent risk that algorithmic flaws can spread across many files, so the following flow is recommended:

일괄 처리는 알고리즘 결함이 다수 파일로 확산될 수 있는 본질적 리스크가 있어, 다음 흐름을 권장합니다:

1. Verify the conversion result with a single file in **Text Fixer**
2. Apply **Bulk Fixer** with confidence using the same algorithm
3. Review the `[Fixed]` results in the Output folder
4. Bulk-remove the `[Fixed]` prefix in the **Tag Editor** tab to finalize

1. **Text Fixer**에서 단일 파일로 변환 결과를 충분히 검증
2. 동일 알고리즘으로 안심하고 **Bulk Fixer** 일괄 적용
3. Output 폴더의 `[Fixed]` 결과물 검수
4. **Tag Editor** 탭에서 `[Fixed]` 태그 일괄 제거하여 정리 완료

This flow naturally guides users to always pass through batch processing results once.

이 흐름은 사용자가 일괄 처리 결과를 항상 한 번 거쳐가도록 자연스럽게 유도합니다.

### 3.4 Three-Tier Automatic Handling for Partially Corrupted Files · 부분 손상 파일 자동 3-티어 처리

Bulk Fixer automatically classifies **partially corrupted encoded files** — files that open in Notepad but fail every strict decoding (a decoding mode that allows no encoding errors):

메모장에선 열리지만 엄격 디코딩(인코딩 오류를 일체 허용하지 않는 디코딩 모드)이 모두 실패하는 **부분 손상 인코딩 파일**을 Bulk Fixer가 자동 분류합니다:

- **Tier 1 (corruption ≤500 chars)** — Normal processing + report generated
- **Tier 2 (501~5000 chars)** — Normal processing + warning-level report
- **Tier 3 (5001+ chars)** — **Skip with original protection** + report only

- **Tier 1 (손상 ≤500자)** — 정상 처리 + 리포트 생성
- **Tier 2 (501~5000자)** — 정상 처리 + 경고 수위 리포트
- **Tier 3 (5001자+)** — **원본 보호 스킵** + 리포트만 생성

All outputs are accompanied by a `{original_filename}.encoding_report.txt` report so you can verify after the fact which bytes were corrected. Text Fixer (single file) operates on **user consent** (a warning dialog confirms with the user before processing), while Bulk Fixer (batch) operates on **post-hoc transparency** (the result is openly disclosed via a report after processing) — a role division matched to the risk level.

모든 출력물은 `{원본파일명}.encoding_report.txt` 리포트를 동반하여 어떤 바이트가 교정되었는지 사후에 확인할 수 있습니다. Text Fixer(단일 파일)는 **사용자 동의 기반**(처리 전 경고 다이얼로그로 사용자에게 확인받는 방식), Bulk Fixer(일괄)는 **사후 투명성 기반**(처리 후 리포트로 결과를 투명하게 공개하는 방식)으로 작동합니다 — 리스크 수준에 맞춘 역할 분담입니다.

### 3.5 Design Intent · 설계 의도

The philosophy of the unified tool is "do not compromise on either convenience or safety." It provides the convenience of moving between six features in a single window, but each feature is simultaneously protected by five layers of safety: preview, undo, original protection, result identification, and tiered automatic handling. The efficiency of batch processing easily becomes catastrophe when misused, so the workflow is designed so that users naturally pass through verification while taking the fast path.

통합 도구의 철학은 "편의성과 안전성 중 어느 것도 양보하지 않는다"는 것입니다. 단일 창에서 6개 기능을 오가는 편의성을 제공하되, 각 기능에는 미리보기·실행 취소·원본 보호·결과물 식별·티어드 자동 처리라는 다섯 겹의 안전장치를 동시에 적용합니다. 일괄 처리의 효율은 오용 시 재앙이 되기 쉬우므로, 사용자가 빠른 길로 가면서도 자연스럽게 검증 과정을 거치도록 워크플로우를 설계했습니다.

---

## Contact · 문의

Questions, suggestions, and technical discussions about the project are welcome through [GitHub Issues](https://github.com/MerciHanrim/FileNexusSuite/issues).

프로젝트에 대한 문의, 제안, 기술적 논의는 [GitHub Issues](https://github.com/MerciHanrim/FileNexusSuite/issues)를 통해 환영합니다.
