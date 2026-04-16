<div align="center">

# 📁 File Nexus Suite

**텍스트·전자책·미디어 파일 작업에 특화된 통합 파일 도구**
*An integrated file utility for text, e-book, and media file management*

[![Version](https://img.shields.io/github/v/release/MerciHanrim/FileNexusSuite?color=CC785C&label=version)](https://github.com/MerciHanrim/FileNexusSuite/releases)
[![Downloads](https://img.shields.io/github/downloads/MerciHanrim/FileNexusSuite/total?color=CC785C)](https://github.com/MerciHanrim/FileNexusSuite/releases)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![PySide6](https://img.shields.io/badge/PySide6-Qt%206-41CD52?logo=qt&logoColor=white)](https://doc.qt.io/qtforpython-6/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6?logo=windows&logoColor=white)]()
[![License](https://img.shields.io/badge/License-Freeware-green)]()

[**📥 Download**](https://github.com/MerciHanrim/FileNexusSuite/releases/latest) ·
[**📖 Features**](#-주요-기능--features) ·
[**🎨 Screenshots**](#-스크린샷--screenshots) ·
[**⚙️ Tech Stack**](#️-기술-스택--tech-stack)

</div>

---

## 💡 프로젝트 소개 / About

File Nexus Suite는 일상적인 파일 정리 작업—텍스트 병합, 포맷 변환, 이름 변경, 줄바꿈 교정—을 하나의 데스크톱 애플리케이션에 통합한 도구입니다. 개별적으로 개발했던 5개의 독립 프로그램을 하나의 탭 기반 인터페이스로 통합하고, PyQt5에서 PySide6(Qt 6)로 마이그레이션하며 완성한 프로젝트입니다.

> File Nexus Suite combines five originally standalone programs—text merger, EPUB/TXT converter, tag editor, batch renamer, and line-break fixer—into one tab-based desktop application. Migrated from PyQt5 to PySide6 (Qt 6) for consistent modern UI across all features.

---

## 📥 Download / 다운로드

가장 최신 버전을 다운로드하세요. 별도 설치가 필요 없습니다.
*Download the latest version. No installation required.*

| Platform | Download |
|----------|----------|
| 🪟 Windows 10/11 (64-bit) | [**FileNexusSuite v1.0.1**](https://github.com/MerciHanrim/FileNexusSuite/releases/latest) |

**사용법 / How to use**
1. zip 압축 해제 / Extract the zip file
2. `FileNexusSuite.exe` 실행 / Run `FileNexusSuite.exe`
3. 앱 내 우측 상단 [?] 도움말 참고 / See in-app `[?]` Help (top-right)

---

## 🛠 주요 기능 / Features

| Tab | 기능 / Feature |
| :-- | :-- |
| **Text Merger** | 여러 파일을 하나의 텍스트로 병합 *(TXT, MD, CSV, DOCX, PDF, XLSX 등)* <br>*Merge multiple files into one text file* |
| **Text Converter** | TXT ↔ EPUB 형식 일괄 변환 <br>*Batch convert between TXT and EPUB* |
| **Tag Editor** | 파일명 태그 일괄 추가·제거, 0패딩 제거 <br>*Batch add/remove filename tags, strip zero-padding* |
| **Batch Renamer** | 폴더·파일 일괄 이름 변경 (접두사·번호·치환·정규식) <br>*Batch rename folders/files with prefix, numbering, find & replace, regex* |
| **Text Fixer** | 단일 파일 줄바꿈 교정 — 단락 병합·빈 줄 정리 <br>*Fix line breaks in a single file* |
| **Bulk Fixer** | 여러 파일에 Text Fixer 일괄 적용 <br>*Apply Text Fixer to multiple TXT files at once* |

---

## 🎨 스크린샷 / Screenshots

<div align="center">

| Text Merger | Text Fixer | Bulk Fixer |
|:---:|:---:|:---:|
| ![Text Merger](https://github.com/user-attachments/assets/f4792f57-6162-470a-8a1a-6137225ede5c) | ![Text Fixer](https://github.com/user-attachments/assets/16c2b9c2-e7b3-4343-86dc-691a8007d0c9) | ![Bulk Fixer](https://github.com/user-attachments/assets/00e042fd-9703-4fa7-b6ea-53fc7efc38d1) |

</div>

---

## ✨ 주요 특징 / Highlights

- 🌏 **5개 언어 지원** — 한국어 · English · 日本語 · 中文简体 · 中文繁體
- 🎨 **9개 테마 + OS 자동 감지** — Light · Dark · Sakura · Ocean · Mint · Sand · Honey · Lavender · Choco
- ⌨️ **단축키 커스터마이징** — 모든 탭 단축키 사용자 지정 가능
- 📁 **전역 출력 폴더** — 저장 후 자동 열기 옵션
- 🔍 **Ctrl+F 검색** — Text Fixer 내장 검색
- ↩️ **실행 취소(Undo)** — 모든 파일 변경 작업 되돌리기 가능
- 🖱️ **드래그 앤 드롭** — 모든 탭에서 파일·폴더 드래그 입력 지원
- 💾 **설정 영속화** — JSON 기반 환경설정 자동 저장

---

## ⚙️ 기술 스택 / Tech Stack

| 구분 | 기술 |
|:--|:--|
| **언어 / Language** | Python 3.x |
| **GUI 프레임워크** | PySide6 (Qt 6) — LGPL-3.0 |
| **인코딩 감지** | chardet *(optional)* |
| **문서 처리** | python-docx · pdfplumber · openpyxl *(optional)* |
| **전자책 처리** | ebooklib + BeautifulSoup *(optional)* |
| **아이콘 시스템** | 자체 SVG 벡터 아이콘 (line/filled 듀얼 스타일) |
| **빌드 / Build** | PyInstaller (단일 실행 파일 / single-file executable) |

> 모든 외부 라이브러리는 `try/except`로 임포트되어 미설치 환경에서도 핵심 기능이 동작합니다.
> *All external libraries are loaded with `try/except` — core features work even without optional dependencies.*

---

## 💻 시스템 요구사항 / Requirements

- **OS:** Windows 10 / 11 (64-bit)
- **설치 / Installation:** 별도 설치 불필요 — exe 실행만 하면 됩니다 / *No installation required*

---

## 📜 라이선스 / License

이 소프트웨어는 **프리웨어**입니다.
*This software is **freeware**.*

- ✅ 개인 및 상업적 사용 자유 / Free for personal & commercial use
- ❌ 무단 재배포·재가공·판매 금지 / No redistribution, repackaging, or resale

Copyright © 2026 Hanrim. All rights reserved.

자세한 오픈소스 라이선스 고지는 앱 내 **설정 → 라이선스** 메뉴에서 확인하실 수 있습니다.
*See in-app **Settings → License** for full open-source attribution.*

---

## 👤 Author

**Hanrim** — [@MerciHanrim](https://github.com/MerciHanrim)

문제 보고 및 제안은 [Issues](https://github.com/MerciHanrim/FileNexusSuite/issues)에 남겨주세요.
*Bug reports and suggestions welcome via [Issues](https://github.com/MerciHanrim/FileNexusSuite/issues).*

---

<div align="center">

⭐ 이 프로젝트가 마음에 드신다면 Star를 눌러주세요!
*If you find this project useful, please consider giving it a star!*

</div>
