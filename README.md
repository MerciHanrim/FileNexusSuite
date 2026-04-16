<div align="center">

# File Nexus Suite

**통합 파일 관리 도구 · Integrated File Utility**

텍스트 병합 · EPUB 변환 · 파일명 태그 편집 · 일괄 이름 변경 · 줄바꿈 교정

<br>

![version](https://img.shields.io/badge/version-1.0.1-CC785C?style=flat-square)
![python](https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-Qt_6-41CD52?style=flat-square&logo=qt&logoColor=white)
![platform](https://img.shields.io/badge/platform-Windows_10_%7C_11-0078D4?style=flat-square&logo=windows&logoColor=white)
![license](https://img.shields.io/badge/license-Freeware_(source_available)-7B6FA3?style=flat-square)
![AI](https://img.shields.io/badge/AI_pair_programming-Claude-CC785C?style=flat-square)

[**Download**](https://github.com/MerciHanrim/FileNexusSuite/releases) · [**Report Bug**](https://github.com/MerciHanrim/FileNexusSuite/issues) · [**Request Feature**](https://github.com/MerciHanrim/FileNexusSuite/issues)

</div>

---

## 프로젝트 소개 · About

File Nexus Suite는 일상적인 파일 작업을 하나의 데스크톱 애플리케이션에 통합한 Windows용 도구입니다. 텍스트 파일 병합, EPUB/TXT 상호 변환, 파일명 태그 편집, 폴더·파일 일괄 이름 변경, 텍스트 줄바꿈 교정까지 — **6개의 핵심 기능을 일관된 UI로 제공**합니다.

> File Nexus Suite integrates everyday file tasks into a single Windows desktop application — text merging, EPUB conversion, filename tag editing, batch renaming, and line-break correction — all with a consistent UI.

### 개발 방식 · Development Approach

본 프로젝트는 **AI 페어 프로그래밍(Claude)으로 개발**되었습니다. [Hanrim](https://github.com/MerciHanrim)이 기획·UX 설계·기능 명세·품질 관리를 담당하고, 코드 작성은 AI와 협업하여 진행했습니다. 전체 소스 코드는 본 저장소에 공개되어 있어 자유롭게 검토·학습할 수 있습니다.

> This project was developed with **AI pair programming (Claude)**. Planning, UX design, feature specification, and quality management were done by Hanrim, with code written in collaboration with AI. The full source code is published in this repository for open review and study.

---

## 주요 특징 · Highlights

- 🗂️ **6 Integrated Tabs** — Text Merger, Text Converter, Tag Editor, Batch Renamer, Text Fixer, Bulk Fixer
- 🎨 **9 Themes + Auto Mode** — Light, Dark, Sakura, Choco, Mint, Ocean, Sand, Honey, Lavender (+ OS dark mode detection)
- 🌐 **5 Languages** — 한국어 · English · 日本語 · 简体中文 · 繁體中文 (auto-detected from OS)
- ↩️ **Undo Support** — Every destructive action (renames, merges, tag edits) can be reverted
- 👁️ **Preview Before Apply** — All batch operations show a preview before execution
- 🔋 **Sleep Prevention** — Windows sleep mode is blocked during long operations
- 🎯 **Drag & Drop Everywhere** — Every tab accepts file/folder drag & drop
- 💾 **Smart Encoding** — Auto-detect with chardet, supports UTF-8 / UTF-8-BOM / EUC-KR / CP949 / UTF-16

---

## 탭별 기능 · Features

### 📋 Text Merger
여러 파일(TXT, MD, CSV, JSON, DOCX, PDF, XLSX 등)을 하나의 텍스트 파일로 병합합니다. 파일 구분선 삽입 옵션과 인코딩 자동 감지를 지원합니다.

> Merge multiple files (TXT, MD, CSV, JSON, DOCX, PDF, XLSX, etc.) into a single text file with customizable separators and auto encoding detection.

### 🔄 Text Converter
TXT와 EPUB 형식을 상호 변환합니다. 텍스트 원고로 전자책을 만들거나, EPUB에서 텍스트를 추출해 편집 가능한 형태로 꺼낼 수 있습니다.

> Convert between TXT and EPUB formats. Create e-books from text files or extract text from EPUBs.

### 🏷️ Tag Editor
파일명의 `[태그]` 패턴을 일괄 추가·제거합니다. 파일명 앞자리 0 제거 모드도 지원합니다.

> Batch add/remove `[tag]` patterns from filenames. Includes a leading-zero removal mode.

### 📁 Batch Renamer
폴더와 파일 이름을 일괄 변경합니다. 숫자 자동 추출(스마트 추출)과 순차 번호 부여 두 방식을 지원합니다.

> Rename folders and files in bulk using smart number extraction or sequential numbering.

### ✦ Text Fixer
OCR이나 전자책에서 추출한 텍스트의 잘못된 줄바꿈을 교정합니다. 한국어·영어 모드를 지원하며, 변경 위치를 시각적으로 확인할 수 있습니다.

> Fix broken line breaks in OCR'd or extracted text. Intelligent paragraph reconstruction with Korean/English mode and visual diff highlighting.

### ✦ Bulk Fixer
Text Fixer의 로직을 여러 파일에 한 번에 적용합니다. 폴더 구조 유지 옵션을 지원합니다.

> Apply Text Fixer's logic to multiple files at once. Preserves folder structure option.

---

## 설치 및 실행 · Installation

### 실행 파일 다운로드 (일반 사용자) · Download Executable

[**Releases 페이지**](https://github.com/MerciHanrim/FileNexusSuite/releases)에서 최신 Windows 실행 파일을 다운로드하세요.

> Download the latest Windows executable from the [Releases](https://github.com/MerciHanrim/FileNexusSuite/releases) page.

### 소스에서 실행 (개발자) · Run from Source

```bash
# 저장소 클론
git clone https://github.com/MerciHanrim/FileNexusSuite.git
cd FileNexusSuite

# 의존성 설치
pip install PySide6 chardet python-docx pdfplumber openpyxl

# 실행
python FileNexusSuite.py
```

---

## 기술 스택 · Tech Stack

| Category | Technology |
|---|---|
| Language | Python 3.10+ |
| GUI Framework | PySide6 (Qt 6) |
| File Format Support | chardet, python-docx, pdfplumber, openpyxl |
| Build | PyInstaller (Windows executable) |
| AI Collaboration | Anthropic Claude |

---

## 테마 & 언어 · Themes & Languages

<details>
<summary><strong>🎨 9 Themes + Auto Mode</strong></summary>

<br>

| Theme | Mood |
|---|---|
| **Light** | 깔끔한 밝은 모드 · Clean, bright |
| **Dark** | 차분한 어두운 모드 · Deep, focused |
| **Sakura** | 벚꽃 느낌 · Cherry blossom |
| **Choco** | 앤티크 브론즈 · Warm cacao |
| **Mint** | 상쾌한 자연 톤 · Fresh, natural |
| **Ocean** | 시원한 바다 톤 · Cool blue |
| **Sand** | 사막 톤 · Desert warm |
| **Honey** | 따뜻한 꿀 톤 · Golden amber |
| **Lavender** | 부드러운 라벤더 톤 · Soft purple |
| **Auto** | OS 다크모드 자동 감지 · Follows OS dark mode |

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

> Language is auto-detected from OS settings on first launch and can be changed anytime in Settings.

</details>

---

## 라이선스 · License

본 소프트웨어는 **프리웨어(소스 공개)** 입니다. 개인 및 상업적 사용이 자유롭게 허용되며, 무단 재배포·재가공·판매는 금지됩니다.

> This software is **freeware (source available)**. Free for personal and commercial use. Unauthorized redistribution, repackaging, or resale is prohibited.

사용된 오픈소스 라이브러리:
- Python (PSF License 2.0)
- PySide6 (LGPL-3.0)
- chardet (LGPL-2.1)
- python-docx, pdfplumber, openpyxl (MIT)

전체 라이선스 정보는 앱 내 **[설정 → 라이선스]** 에서 확인할 수 있습니다.

Copyright © 2026 Hanrim. All rights reserved.

---

## 제작자 · Author

**신용우 (Hanrim)** — [@MerciHanrim](https://github.com/MerciHanrim)

제품 기획 · UX 설계 · 품질 관리 · AI 디렉팅 · 릴리즈 관리

> Product planning · UX design · Quality management · AI direction · Release management

---

## Acknowledgments

Built with the assistance of [Claude](https://claude.ai) by Anthropic, acting as a pair programming partner throughout the development process.

프로젝트의 모든 코드는 Anthropic의 [Claude](https://claude.ai)와 페어 프로그래밍으로 작성되었습니다.
