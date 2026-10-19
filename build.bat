@echo off
rem ===========================================================================
rem  AITA Desktop Client - release build (onedir exe + bundled toolchains).
rem
rem  Usage : double-click this file, or run build.bat from a terminal.
rem  Output: dist\AITA_Grader_v1\AITA_Grader_v1.exe   portable folder
rem          dist\AITA_Grader_v1_portable.zip         release package
rem
rem  Notes :
rem  - Messages are ASCII on purpose; cmd codepage cannot be trusted for UTF-8.
rem  - Toolchains are NOT downloaded here. Create them once with:
rem        python apps\desktop-client\scripts\build_toolchains.py --help
rem    The repo already keeps apps\desktop-client\toolchains\ ready to bundle.
rem ===========================================================================
setlocal EnableExtensions
cd /d "%~dp0"

set "ROOT=%~dp0"
set "APP_DIR=%ROOT%apps\desktop-client"
set "SPEC=%APP_DIR%\AITA_Grader_v1.spec"
set "TOOLCHAINS=%APP_DIR%\toolchains"
set "DIST=%ROOT%dist"
set "WORK=%ROOT%build"
set "BUNDLE=%DIST%\AITA_Grader_v1"
set "EXE=%BUNDLE%\AITA_Grader_v1.exe"
set "REPORT=%BUNDLE%\aita_selftest.txt"
set "ZIP=%DIST%\AITA_Grader_v1_portable.zip"

echo ======================================================================
echo   AITA Grader - release build
echo ======================================================================
echo.

rem --- 1/6 Python interpreter ------------------------------------------------
set "PYTHON_CMD=python"
where python >nul 2>&1
if not errorlevel 1 goto :have_python
where py >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py"
    goto :have_python
)
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    goto :have_python
)
echo [ERROR] Python 3.11+ not found on PATH.
echo         Install Python 3.11+ (tick "Add python.exe to PATH") and retry.
goto :fail

:have_python
for /f "delims=" %%v in ('%PYTHON_CMD% -V 2^>^&1') do set "PYVER=%%v"
echo [1/6] Python      : %PYTHON_CMD%   %PYVER%

rem --- 2/6 PyInstaller -------------------------------------------------------
"%PYTHON_CMD%" -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PyInstaller is not installed for this interpreter.
    echo         Fix with:  "%PYTHON_CMD%" -m pip install pyinstaller
    goto :fail
)
for /f "delims=" %%v in ('"%PYTHON_CMD%" -m PyInstaller --version 2^>^&1') do set "PIVER=%%v"
echo [2/6] PyInstaller : %PIVER%

rem --- 3/6 Spec + toolchains -------------------------------------------------
if not exist "%SPEC%" (
    echo [ERROR] Missing spec: %SPEC%
    goto :fail
)
if not exist "%TOOLCHAINS%" (
    echo [WARN ] No %TOOLCHAINS% - the exe will need GCC/JDK/Python on the target PC.
    echo         Create it first with scripts\build_toolchains.py if you want a portable build.
    echo         Press any key to continue anyway, or Ctrl+C to abort.
    pause >nul
) else (
    call :probe_tool "mingw64\bin\gcc.exe"    "gcc"
    call :probe_tool "jdk\bin\javac.exe"      "javac"
    call :probe_tool "jdk\bin\java.exe"       "java"
    call :probe_tool "python\python.exe"      "python"
)
echo [3/6] Toolchains  : %TOOLCHAINS%

rem --- 4/6 Build -------------------------------------------------------------
echo [4/6] Building with PyInstaller (about 2 minutes, please wait)...
"%PYTHON_CMD%" -m PyInstaller "%SPEC%" --noconfirm --clean --distpath "%DIST%" --workpath "%WORK%"
if errorlevel 1 (
    echo [ERROR] PyInstaller failed. Read the log above for the cause.
    goto :fail
)
if not exist "%EXE%" (
    echo [ERROR] Build finished but %EXE% is missing.
    goto :fail
)

rem --- 5/6 Selftest (real GCC + JDK + Python run inside the bundle) ----------
echo [5/6] Selftest: compiling and running 3+4 with the bundled toolchains...
if exist "%REPORT%" del "%REPORT%" >nul 2>&1
rem console=False -> the exe is a GUI app, so "start /wait" is required here.
start "" /wait "%EXE%" --selftest
set "SELFTEST_OK=0"
if exist "%REPORT%" (
    findstr /C:"OK (3+4=7)" "%REPORT%" >nul 2>&1
    if not errorlevel 1 set "SELFTEST_OK=1"
)
if "%SELFTEST_OK%"=="1" (
    echo [ OK ] GCC + JDK + Python all work inside the bundle.
) else (
    echo [WARN] Selftest not fully OK. Open this file to see why:
    echo        %REPORT%
    echo        ^(missing toolchains^? run scripts\build_toolchains.py, then build again^)
)

rem --- 6/6 Package -----------------------------------------------------------
echo [6/6] Packing %ZIP% ...
if exist "%ZIP%" del "%ZIP%" >nul 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -LiteralPath '%BUNDLE%' -DestinationPath '%ZIP%' -CompressionLevel Optimal -Force"
if not exist "%ZIP%" (
    echo [ERROR] Could not create the zip package.
    goto :fail
)

echo.
echo ======================================================================
echo   BUILD OK
echo ======================================================================
echo   Exe folder : %BUNDLE%
echo   Launcher   : %EXE%
echo   Release zip: %ZIP%
echo   Version    :
findstr /b "APP_VERSION" "%APP_DIR%\src\core\version.py"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$z=Get-Item -LiteralPath '%ZIP%'; '   Zip size   : ' + $z.Length + ' bytes (' + [math]::Round($z.Length/1MB,1) + ' MB)'; '   SHA-256    : ' + (Get-FileHash -LiteralPath $z.FullName -Algorithm SHA256).Hash.ToLower()"
echo.
echo   To ship an update, upload the zip to a GitHub Release and set on the
echo   backend (Render -^> Environment):
echo     APP_LATEST_VERSION        = the new version, e.g. 1.1.0
echo     APP_MIN_SUPPORTED_VERSION = e.g. 1.0.0
echo     APP_UPDATE_ARTIFACT_TYPE  = zip
echo     APP_UPDATE_ENTRYPOINT     = AITA_Grader_v1.exe
echo     APP_UPDATE_URL_WINDOWS    = https://github.com/.../AITA_Grader_v1_portable.zip
echo     APP_UPDATE_SHA256_WINDOWS = the SHA-256 printed above
echo     APP_UPDATE_SIZE_WINDOWS   = the byte size printed above
echo.
pause
endlocal
exit /b 0

:probe_tool
rem %1 = path relative to toolchains\, %2 = display name
if exist "%TOOLCHAINS%\%~1" (
    echo        toolchain  : %~2 OK
) else (
    echo        toolchain  : %~2 MISSING  ^(%TOOLCHAINS%\%~1^)
)
goto :eof

:fail
echo.
echo [FAILED] Build stopped. Fix the cause above, then run build.bat again.
pause
endlocal
exit /b 1
