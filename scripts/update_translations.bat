@echo off
REM ============================================================================
REM  FileNexusSuite - Qt Linguist translation update routine
REM
REM  Run from the project root or directly from scripts/. The script always
REM  resolves paths relative to the project root.
REM
REM  Folder layout:
REM    translations_ts\fns_*.ts     <- source files (Git tracked)
REM    translations\fns_*.qm        <- runtime files (Git tracked)
REM
REM  Steps:
REM    0) Delete stale .qm only - .ts files are kept (translations preserved)
REM    1) pyside6-lupdate           - extract self.tr() -> translations_ts\fns_*.ts
REM                                   (FileNexusSuite.py only)
REM                                   Existing translations are preserved across
REM                                   lupdate runs; new sources show up as
REM                                   unfinished, removed sources are marked
REM                                   vanished.
REM    2) add_ts_contexts.py        - assign each message to enclosing class,
REM                                   recover vanished/unfinished entries that
REM                                   have intact translation text
REM    3) pyside6-lrelease          - compile .ts -> translations\fns_*.qm directly
REM
REM  New translations: edit translations_ts\fns_*.ts directly with Qt Linguist.
REM ============================================================================
setlocal

REM Resolve project root (parent of scripts/ where this .bat lives)
cd /d "%~dp0.."

set TS_DIR=translations_ts
set QM_DIR=translations
set SCRIPTS_DIR=scripts

if not exist %TS_DIR% mkdir %TS_DIR%
if not exist %QM_DIR% mkdir %QM_DIR%

echo === 0) Delete stale .qm (keep .ts to preserve translations) ===
del /Q %QM_DIR%\fns_*.qm 2>nul

echo.
echo === 1) pyside6-lupdate - extract self.tr() ===
pyside6-lupdate FileNexusSuite.py -ts ^
    %TS_DIR%\fns_ko.ts ^
    %TS_DIR%\fns_en.ts ^
    %TS_DIR%\fns_ja.ts ^
    %TS_DIR%\fns_zh_cn.ts ^
    %TS_DIR%\fns_zh_tw.ts
if errorlevel 1 goto :error

echo.
echo === 2) add_ts_contexts.py - assign enclosing class contexts ===
python %SCRIPTS_DIR%\add_ts_contexts.py
if errorlevel 1 goto :error

echo.
echo === 3) pyside6-lrelease - compile .qm directly to translations\ ===
for %%L in (ko en ja zh_cn zh_tw) do (
    pyside6-lrelease %TS_DIR%\fns_%%L.ts -qm %QM_DIR%\fns_%%L.qm
    if errorlevel 1 goto :error
)

echo.
echo === Done ===
goto :end

:error
echo.
echo *** Failed ***
exit /b 1

:end
endlocal
