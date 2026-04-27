<div align="center">

# File Nexus Suite

**통합 파일 관리 도구**

텍스트 병합 · EPUB 변환 · 파일명 태그 편집 · 일괄 이름 변경 · 줄바꿈 교정

<br>

![version](https://img.shields.io/badge/version-1.0.10-7B6FA3?style=flat-square)
![python](https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-Qt_6-41CD52?style=flat-square&logo=qt&logoColor=white)
![platform](https://img.shields.io/badge/platform-Windows_10_%7C_11-0078D4?style=flat-square&logo=windows&logoColor=white)
[![CI](https://github.com/MerciHanrim/FileNexusSuite/actions/workflows/ci.yml/badge.svg)](https://github.com/MerciHanrim/FileNexusSuite/actions/workflows/ci.yml)
![tests](https://img.shields.io/badge/tests-535%20passing-97CA00?style=flat-square)
![license](https://img.shields.io/badge/license-MIT-97CA00?style=flat-square)
![AI](https://img.shields.io/badge/AI_pair_programming-Claude-CC785C?style=flat-square)

<br>

[English](./README.md) | **Korean**

<br>

[![Download Latest Release](https://img.shields.io/badge/⬇%20Download%20Latest%20Release-CC785C?style=for-the-badge&logoColor=white)](https://github.com/MerciHanrim/FileNexusSuite/releases/latest)

[Report Bug](https://github.com/MerciHanrim/FileNexusSuite/issues) · [Request Feature](https://github.com/MerciHanrim/FileNexusSuite/issues)

</div>

---

## 프로젝트 소개

File Nexus Suite는 일상적인 파일 작업을 하나의 데스크톱 애플리케이션에 통합한 Windows용 도구입니다. 텍스트 파일 병합, EPUB/TXT 상호 변환, 파일명 태그 편집, 폴더·파일 일괄 이름 변경, 텍스트 줄바꿈 교정까지 — **6개의 핵심 기능을 일관된 UI로 제공**합니다.

본 프로젝트는 **AI 페어 프로그래밍(Claude)으로 개발**되었습니다. 전체 소스 코드는 본 저장소에 공개되어 있어 자유롭게 검토·학습할 수 있습니다.

> 📖 프로젝트의 시작 동기, 설계 철학, 안전 설계 상세는 [docs/STORY.md](docs/STORY.md)를 참조하세요.

---

## 주요 특징

- 🗂️ **6 Integrated Tabs** — 한 창에서 6개 핵심 도구 일관 UI로 운영
- 🛡️ **Safe by Design** — 미리보기·실행취소 + 부분 손상 파일 자동 3-티어 처리
- 🌐 **5 Languages** — 한국어 · English · 日本語 · 简体中文 · 繁體中文 (OS 자동 감지)
- 📄 **HWPX 지원** — 한국 문서 표준 포맷을 Text Merger에서 직접 읽기

---

## 탭별 기능

### 📋 Text Merger
여러 파일(TXT, MD, CSV, JSON, DOCX, PDF, XLSX, **HWPX**)을 하나의 텍스트 파일로 병합합니다. 파일 구분선 삽입 옵션, 인코딩 자동 감지, 저장 인코딩 자동 추천을 지원합니다.

### 🔄 Text Converter
TXT와 EPUB 형식을 상호 변환합니다. 텍스트 원고로 전자책을 만들거나, EPUB에서 텍스트를 추출해 편집 가능한 형태로 꺼낼 수 있습니다.

### 🏷️ Tag Editor
파일명의 `[태그]` 패턴을 일괄 추가·제거합니다. 파일명 앞자리 0 제거 모드도 지원합니다.

### 📁 Batch Renamer
폴더와 파일 이름을 일괄 변경합니다. 숫자 자동 추출(스마트 추출)과 순차 번호 부여 두 방식을 지원합니다.

### ✦ Text Fixer
OCR이나 전자책에서 추출한 텍스트의 잘못된 줄바꿈을 교정합니다. 한국어·영어 모드를 지원하며, 변경 위치를 시각적으로 확인할 수 있습니다.

### ✦ Bulk Fixer
Text Fixer의 로직을 여러 파일에 한 번에 적용합니다. 폴더 구조 유지 옵션을 지원합니다.

---

## 🎨 스크린샷

<div align="center">

| Text Merger | Text Fixer | Bulk Fixer |
|:---:|:---:|:---:|
| ![Text Merger](https://github.com/user-attachments/assets/f4792f57-6162-470a-8a1a-6137225ede5c) | ![Text Fixer](https://github.com/user-attachments/assets/16c2b9c2-e7b3-4343-86dc-691a8007d0c9) | ![Bulk Fixer](https://github.com/user-attachments/assets/00e042fd-9703-4fa7-b6ea-53fc7efc38d1) |

</div>

---

## 설치 및 실행

### 실행 파일 다운로드 (일반 사용자)

[**Releases 페이지**](https://github.com/MerciHanrim/FileNexusSuite/releases)에서 최신 Windows 실행 파일을 다운로드하세요.

### 소스에서 실행 (개발자)

```bash
# 저장소 클론
git clone https://github.com/MerciHanrim/FileNexusSuite.git
cd FileNexusSuite

# 의존성 설치 (requirements.txt 사용 권장)
pip install -r requirements.txt

# 실행
python FileNexusSuite.py
```

---

## 기술 스택

| Category | Technology |
|---|---|
| Language | Python 3.10+ |
| GUI Framework | PySide6 (Qt 6) |
| File Format Support | chardet, python-docx, pdfplumber, openpyxl, python-hwpx |
| Build | PyInstaller (Windows executable) |
| AI Collaboration | Anthropic Claude |

---

## 테마 & 언어

<details>
<summary><strong>🎨 9 Themes + Auto Mode</strong></summary>

<br>

| Theme | Mood |
|---|---|
| **Light** | 깔끔한 밝은 모드 |
| **Dark** | 차분한 어두운 모드 |
| **Sakura** | 벚꽃 느낌 |
| **Choco** | 앤티크 브론즈 |
| **Mint** | 상쾌한 자연 톤 |
| **Ocean** | 시원한 바다 톤 |
| **Sand** | 사막 톤 |
| **Honey** | 따뜻한 꿀 톤 |
| **Lavender** | 부드러운 라벤더 톤 |
| **Auto** | OS 다크모드 자동 감지 |

</details>

<details>
<summary><strong>🌐 5 Supported Languages</strong></summary>

<br>

- 🇰🇷 한국어 (Korean)
- 🇺🇸 English
- 🇯🇵 日本語 (Japanese)
- 🇨🇳 简体中文 (Simplified Chinese)
- 🇹🇼 繁體中文 (Traditional Chinese)

앱 최초 실행 시 OS 언어를 자동 감지하며, 설정에서 언제든 변경할 수 있습니다.

</details>

---

## 라이선스

본 소프트웨어는 **MIT 라이선스**로 배포됩니다. 저작권 고지를 유지하는 조건으로 사용·수정·재배포·판매가 모두 자유롭게 허용됩니다.

개인 작업 도구로 시작했지만, 같은 작업을 하는 다른 분들에게도 도움이 되기를 바라며 MIT 라이선스로 공개합니다.

사용된 오픈소스 라이브러리:
- Python (PSF License 2.0)
- PySide6 (LGPL-3.0)
- chardet (LGPL-2.1)
- python-docx, pdfplumber, openpyxl, python-hwpx (MIT)

전체 라이선스 정보는 앱 내 **[설정 → 라이선스]** 에서 확인할 수 있으며, 저장소 루트의 [`LICENSE`](./LICENSE) 파일에서도 확인 가능합니다.

Copyright © 2026 Hanrim

---

## 코드 서명

본 프로젝트는 [SignPath Foundation](https://signpath.org)의 무료 코드 서명을 신청 중이며, 승인 후 v1.0.11부터 배포되는 `.exe`에 SignPath Foundation 서명이 적용될 예정입니다.

---

## 피드백

Issues, feedback, and feature requests are welcome in any of the 5 supported languages. 한국어 / English / 日本語 / 中文 (简体·繁體) 모두 환영합니다.

---

## 제작자

**Hanrim** — [@MerciHanrim](https://github.com/MerciHanrim)

제품 기획 · UX 설계 · 품질 관리 · AI 디렉팅 · 릴리즈 관리
