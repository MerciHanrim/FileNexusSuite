<div align="center">

# File Nexus Suite

**Integrated File Utility**

Text merging · EPUB conversion · Filename tag editing · Batch renaming · Line-break correction

<br>

![version](https://img.shields.io/badge/version-1.0.10-7B6FA3?style=flat-square)
![python](https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-Qt_6-41CD52?style=flat-square&logo=qt&logoColor=white)
![platform](https://img.shields.io/badge/platform-Windows_10_%7C_11-0078D4?style=flat-square&logo=windows&logoColor=white)
[![CI](https://github.com/MerciHanrim/FileNexusSuite/actions/workflows/ci.yml/badge.svg?event=push)](https://github.com/MerciHanrim/FileNexusSuite/actions/workflows/ci.yml)
[![Build](https://github.com/MerciHanrim/FileNexusSuite/actions/workflows/build.yml/badge.svg?event=push)](https://github.com/MerciHanrim/FileNexusSuite/actions/workflows/build.yml)
![tests](https://img.shields.io/badge/tests-589%20passing-97CA00?style=flat-square)
![license](https://img.shields.io/badge/license-MIT-97CA00?style=flat-square)
![AI](https://img.shields.io/badge/AI_pair_programming-Claude-CC785C?style=flat-square)

<br>

**English** | [Korean](./README_KO.md)

<br>

[![Download Latest Release](https://img.shields.io/badge/⬇%20Download%20Latest%20Release-CC785C?style=for-the-badge&logoColor=white)](https://github.com/MerciHanrim/FileNexusSuite/releases/latest)

[Report Bug](https://github.com/MerciHanrim/FileNexusSuite/issues) · [Request Feature](https://github.com/MerciHanrim/FileNexusSuite/issues)

</div>

---

## About

File Nexus Suite integrates everyday file tasks into a single Windows desktop application — text merging, EPUB conversion, filename tag editing, batch renaming, and line-break correction — **six core features with a consistent UI**.

This project was developed with **AI pair programming (Claude)**. The full source code is published in this repository for open review and study.

> 📖 For project origin, design philosophy, and safety architecture, see [docs/STORY.md](docs/STORY.md) *(English & Korean)*.

---

## Highlights

- 🗂️ **6 Integrated Tabs** — Six core tools in one window with a consistent UI
- 🛡️ **Safe by Design** — Preview + undo + automatic tiered handling of partially corrupted files
- 🌐 **5 Languages** — 한국어 · English · 日本語 · 简体中文 · 繁體中文 (auto-detected from OS)
- 📄 **HWPX Support** — Read Korea's standard document format directly in Text Merger

---

## Features

### 📋 Text Merger
Merge multiple files (TXT, MD, CSV, JSON, DOCX, PDF, XLSX, **HWPX**) into a single text file. Supports customizable separators, auto encoding detection, and smart save-encoding recommendation.

### 🔄 Text Converter
Convert between TXT and EPUB formats. Create e-books from text manuscripts or extract text from EPUBs for editing.

### 🏷️ Tag Editor
Batch add/remove `[tag]` patterns from filenames. Includes a leading-zero removal mode.

### 📁 Batch Renamer
Rename folders and files in bulk using smart number extraction or sequential numbering.

### ✦ Text Fixer
Fix broken line breaks in OCR'd or extracted text. Intelligent paragraph reconstruction with Korean/English mode and visual diff highlighting.

### ✦ Bulk Fixer
Apply Text Fixer's logic to multiple files at once. Preserves folder structure option.

---

## 🎨 Screenshots

<div align="center">

| Text Merger | Text Fixer | Bulk Fixer |
|:---:|:---:|:---:|
| ![Text Merger](https://github.com/user-attachments/assets/f4792f57-6162-470a-8a1a-6137225ede5c) | ![Text Fixer](https://github.com/user-attachments/assets/16c2b9c2-e7b3-4343-86dc-691a8007d0c9) | ![Bulk Fixer](https://github.com/user-attachments/assets/00e042fd-9703-4fa7-b6ea-53fc7efc38d1) |

</div>

---

## Installation

### Download Executable (End Users)

Download the latest Windows executable from the [**Releases**](https://github.com/MerciHanrim/FileNexusSuite/releases) page.

### Run from Source (Developers)

```bash
# Clone the repository
git clone https://github.com/MerciHanrim/FileNexusSuite.git
cd FileNexusSuite

# Install dependencies (requirements.txt recommended)
pip install -r requirements.txt

# Run
python FileNexusSuite.py
```

### Uninstallation

This is a fully portable application — no installer, no registry entries, no system file modifications.

Delete the `FileNexusSuite` folder. All settings (`FileNexusSuite.json`), output files (`Output/`), and application data are stored in the same folder.

---

## Tech Stack

| Category | Technology |
|---|---|
| Language | Python 3.10+ |
| GUI Framework | PySide6 (Qt 6) |
| File Format Support | chardet, python-docx, pdfplumber, openpyxl, python-hwpx |
| Build | PyInstaller (Windows executable) |
| AI Collaboration | Anthropic Claude |

---

## Themes & Languages

<details>
<summary><strong>🎨 9 Themes + Auto Mode</strong></summary>

<br>

| Theme | Mood |
|---|---|
| **Light** | Clean, bright |
| **Dark** | Deep, focused |
| **Sakura** | Cherry blossom |
| **Choco** | Warm cacao, antique bronze |
| **Mint** | Fresh, natural |
| **Ocean** | Cool blue |
| **Sand** | Desert warm |
| **Honey** | Golden amber |
| **Lavender** | Soft purple |
| **Auto** | Follows OS dark mode |

</details>

<details>
<summary><strong>🌐 5 Supported Languages</strong></summary>

<br>

- 🇰🇷 한국어 (Korean)
- 🇺🇸 English
- 🇯🇵 日本語 (Japanese)
- 🇨🇳 简体中文 (Simplified Chinese)
- 🇹🇼 繁體中文 (Traditional Chinese)

Language is auto-detected from OS settings on first launch and can be changed anytime in Settings.

</details>

---

## License

This software is distributed under the **MIT License**. Free to use, modify, redistribute, and sell, provided that the copyright notice is retained.

Originally built as a personal tool, now released under MIT in the hope it may help others with similar workflows.

Open-source libraries used:
- Python (PSF License 2.0)
- PySide6 (LGPL-3.0)
- chardet (LGPL-2.1)
- python-docx, pdfplumber, openpyxl, python-hwpx (MIT)

Full license information is available in the app at **[Settings → License]**, and also in the [`LICENSE`](./LICENSE) file in the repository root.

Copyright © 2026 Hanrim

---

## Feedback

Issues, feedback, and feature requests are welcome in any of the 5 supported languages — 한국어 / English / 日本語 / 中文 (简体·繁體).

---

## Author

**Hanrim** — [@MerciHanrim](https://github.com/MerciHanrim)

Product planning · UX design · Quality management · AI direction · Release management
