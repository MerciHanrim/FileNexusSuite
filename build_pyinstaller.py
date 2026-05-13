"""
File Nexus Suite — PyInstaller Build Script
============================================
Usage:
    python build_pyinstaller.py

Requirements:
    pip install pyinstaller
"""

import subprocess, sys, os, base64, re, shutil
from pathlib import Path

# ══════════════════════════════════════════════════════════════════════
# Settings
# ══════════════════════════════════════════════════════════════════════
SCRIPT        = "FileNexusSuite.py"
OUTPUT_NAME   = "FileNexusSuite"
ICON_TMP      = "_build_icon_tmp.ico"
VERSION_FILE  = "version_info.txt"      # Windows file properties version info
README_FILE   = "README.txt"            # Auto-copied to dist root after build
DIST_DIR      = "dist"
BUILD_DIR     = "build"

# UPX path
UPX_DIR = r"C:\Work Space\Coding\3_Tools\upx-5.0.2-win64"


# ══════════════════════════════════════════════════════════════════════
# Build Steps
# ══════════════════════════════════════════════════════════════════════
def step(n, total, msg):
    print(f"\n[{n}/{total}] {msg}")
    print("─" * 50)


def extract_icon(script_path):
    with open(script_path, encoding="utf-8") as f:
        src = f.read()
    m = re.search(r'_APP_ICON_B64 = \(\n((?:    "[^"]*"\n)+)\)', src)
    if not m:
        print("  ⚠ _APP_ICON_B64 not found — building without icon.")
        return False
    raw_b64 = re.sub(r'[\s"]', "", m.group(1))
    try:
        ico_bytes = base64.b64decode(raw_b64)
        with open(ICON_TMP, "wb") as f:
            f.write(ico_bytes)
        print(f"  ✅ Icon extracted  ({len(ico_bytes):,} bytes) → {ICON_TMP}")
        return True
    except Exception as e:
        print(f"  ⚠ Icon extraction failed: {e}")
        return False


def check_version_file():
    vf = Path(VERSION_FILE)
    if vf.exists():
        print(f"  ✅ {VERSION_FILE} found")
        return True
    print(f"  ⚠ {VERSION_FILE} not found — Windows version info will be omitted.")
    return False


def check_version_consistency(strict=False):
    """Verify version consistency between README.txt and APP_VERSION.

    With strict=True, build aborts on mismatch (exit 1).
    With strict=False, prints warning only and continues.
    """
    try:
        py_src = Path(SCRIPT).read_text(encoding="utf-8")
        m = re.search(r'APP_VERSION\s*=\s*["\']([\d.]+)["\']', py_src)
        app_ver = m.group(1) if m else None

        readme = Path(README_FILE)
        readme_ver = None
        if readme.exists():
            rm = re.search(r'v(\d+\.\d+\.\d+)', readme.read_text(encoding="utf-8"))
            readme_ver = rm.group(1) if rm else None

        if app_ver and readme_ver and app_ver != readme_ver:
            print(f"  ⚠ Version mismatch — {README_FILE}: v{readme_ver}, APP_VERSION: v{app_ver}")
            print(f"    → Update {README_FILE} to v{app_ver} before release.")
            if strict:
                print(f"  ❌ --strict mode: aborting build.")
                sys.exit(1)
            return False
        if app_ver:
            print(f"  ✅ Version consistent  (v{app_ver})")
        return True
    except Exception as e:
        print(f"  ⚠ Version check failed: {e}")
        return False


def check_pyinstaller():
    try:
        r = subprocess.run(
            [sys.executable, "-m", "PyInstaller", "--version"],
            capture_output=True, text=True
        )
        print(f"  ✅ PyInstaller {r.stdout.strip()}")
        return True
    except Exception:
        print("  ❌ PyInstaller not installed  →  pip install pyinstaller")
        return False


def check_upx():
    upx_exe = Path(UPX_DIR) / "upx.exe"
    if upx_exe.exists():
        try:
            r = subprocess.run([str(upx_exe), "--version"],
                               capture_output=True, text=True)
            print(f"  ✅ {r.stdout.strip().splitlines()[0]}")
            return str(upx_exe)
        except Exception:
            pass
    print(f"  ⚠ UPX not found ({upx_exe}) — skipping compression.")
    return None


def run_pyinstaller(has_icon, has_version_file, upx_exe):
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--windowed",           # no console
        "--onedir",             # folder mode (includes _internal/)
        "--noconfirm",          # overwrite without asking
        f"--name={OUTPUT_NAME}",
        f"--distpath={DIST_DIR}",
        f"--workpath={BUILD_DIR}",
        "--clean",
    ]

    if has_icon and Path(ICON_TMP).exists():
        cmd += ["--icon", ICON_TMP]

    if has_version_file and Path(VERSION_FILE).exists():
        cmd += ["--version-file", VERSION_FILE]

    if upx_exe:
        cmd += [f"--upx-dir={UPX_DIR}"]
        # Exclude DLLs that fail UPX compression
        upx_excludes = [
            "python3.dll", "python310.dll", "python311.dll", "python312.dll",
            "vcruntime140.dll", "vcruntime140_1.dll",
            "ucrtbase.dll", "msvcp140.dll",
            "api-ms-win-*.dll",
            "_uuid.pyd", "_decimal.pyd", "_hashlib.pyd", "_ssl.pyd",
            "_ctypes.pyd", "_socket.pyd", "_bz2.pyd", "_lzma.pyd",
        ]
        for exc in upx_excludes:
            cmd += ["--upx-exclude", exc]

    # Bundled data files — translations (.qm), required for i18n at runtime.
    # Explicit wildcards: only ship compiled fns_*.qm and help_*.qm.
    # Excludes .ts source files and any other accidental contents of translations/.
    cmd += ["--add-data", "translations/fns_*.qm;translations"]
    cmd += ["--add-data", "translations/help_*.qm;translations"]

    # Hidden imports — runtime optional dependencies (handled with ImportError, but must be declared explicitly when packaging)
    hidden = [
        "chardet",          # Automatic encoding detection
        "docx",             # DOCX reading (python-docx)
        "pdfplumber",       # PDF text extraction
        "openpyxl",         # XLSX reading
        "PySide6.QtSvg",    # SVG icon rendering (optional, but required for icon display)
    ]
    for pkg in hidden:
        cmd += ["--hidden-import", pkg]

    # Exclude unused modules
    excludes = [
        "matplotlib", "numpy", "pandas", "scipy",
        "PIL", "tkinter", "unittest",
    ]
    for exc in excludes:
        cmd += ["--exclude-module", exc]

    cmd.append(SCRIPT)

    print("  Options:")
    print(f"    Mode           : onedir (folder + _internal/)")
    print(f"    Output         : {DIST_DIR}/{OUTPUT_NAME}/")
    print(f"    Icon           : {'✅' if has_icon else 'none'}")
    print(f"    Version file   : {'✅' if has_version_file else 'none'}")
    print(f"    UPX            : {'✅' if upx_exe else 'none'}")
    print(f"    Bundled data   : translations/fns_*.qm + help_*.qm")
    print(f"    Hidden imports : {', '.join(hidden)}")
    print()
    return subprocess.run(cmd).returncode == 0


def copy_readme_to_dist():
    """Copy README.txt to dist root after build + version consistency check.
    Automates what used to be a manual copy each time.
    """
    src = Path(README_FILE)
    if not src.exists():
        print(f"  (skipped — {README_FILE} not found in project root)")
        return False

    dst_dir = Path(DIST_DIR) / OUTPUT_NAME
    if not dst_dir.exists():
        print(f"  ⚠ {dst_dir}/ not found — build may have failed.")
        return False

    dst = dst_dir / README_FILE
    shutil.copy2(src, dst)
    print(f"  ✅ {README_FILE} copied  →  {dst}")
    return True


def cleanup():
    removed = []
    if Path(ICON_TMP).exists():
        os.remove(ICON_TMP); removed.append(ICON_TMP)
    if Path(BUILD_DIR).exists():
        shutil.rmtree(BUILD_DIR, ignore_errors=True)
        removed.append(f"{BUILD_DIR}/")
    spec = Path(f"{OUTPUT_NAME}.spec")
    if spec.exists():
        os.remove(spec); removed.append(str(spec))
    for r in removed:
        print(f"  🗑 {r}")
    if not removed:
        print("  (nothing to clean)")


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════
def main():
    TOTAL = 8
    STRICT = "--strict" in sys.argv
    print()
    print("╔══════════════════════════════════════════════╗")
    print("║  File Nexus Suite — PyInstaller Build Script ║")
    print("╚══════════════════════════════════════════════╝")
    if STRICT:
        print("  Mode: STRICT  (build will abort on version mismatch)")

    if not Path(SCRIPT).exists():
        print(f"\n❌ {SCRIPT} not found. Run from the same folder.")
        sys.exit(1)

    step(1, TOTAL, "PyInstaller check")
    if not check_pyinstaller():
        sys.exit(1)

    step(2, TOTAL, "UPX check")
    upx_exe = check_upx()

    step(3, TOTAL, "Version file check")
    has_version_file = check_version_file()

    step(4, TOTAL, "Icon extraction")
    has_icon = extract_icon(SCRIPT)

    step(5, TOTAL, "Version consistency check")
    check_version_consistency(strict=STRICT)

    step(6, TOTAL, "PyInstaller build")
    success = run_pyinstaller(has_icon, has_version_file, upx_exe)

    step(7, TOTAL, "Copy README.txt to dist")
    copy_readme_to_dist()

    step(8, TOTAL, "Cleanup")
    cleanup()

    print()
    print("╔══════════════════════════════════════════════╗")
    exe = Path(DIST_DIR) / OUTPUT_NAME / f"{OUTPUT_NAME}.exe"
    if success and exe.exists():
        dist_path = exe.parent
        total = sum(f.stat().st_size for f in dist_path.rglob("*") if f.is_file())
        print(f"║  ✅ Build successful!                        ║")
        print(f"║  📁 {str(dist_path):<38} ║")
        print(f"║     Total size: {total/1024/1024:.0f} MB                      ║")
    elif success:
        print(f"║  ✅ Build done — check {DIST_DIR}/{OUTPUT_NAME}/   ║")
    else:
        print(f"║  ❌ Build failed — check errors above        ║")
    print("╚══════════════════════════════════════════════╝")
    print()


if __name__ == "__main__":
    main()
