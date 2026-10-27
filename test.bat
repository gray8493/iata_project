@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

echo ============================================================
echo  AITA - AUTOMATION TEST RUNNER
echo  Chay 5 level test cua tests\ (unit+integration, system,
echo  acceptance, e2e, performance) + bo test desktop-client.
echo  Xuat bao cao JUnit + coverage vao thu muc reports\.
echo ============================================================

set "PYTHON_CMD=python"
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    where py >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set "PYTHON_CMD=py"
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
        set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    )
)

set "PYTHONPATH=%~dp0apps\desktop-client\src"
set "QT_QPA_PLATFORM=offscreen"
if not exist "reports" mkdir "reports"

rem Coverage chi bat khi may da cai pytest-cov (CI luon cai san)
"%PYTHON_CMD%" -c "import pytest_cov" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "COV_FLAGS=--cov=apps/desktop-client/src --cov-report=term-missing --cov-report=xml:reports/coverage.xml"
) else (
    set "COV_FLAGS="
)

set "FAILED=0"

call :run_level "1/6 UNIT + INTEGRATION"         "tests\unit tests\integration"         junit-1-unit-integration.xml
call :run_level "2/6 SYSTEM (Qt offscreen)"      "tests\system"                         junit-2-system.xml
call :run_level "3/6 ACCEPTANCE"                 "tests\acceptance"                     junit-3-acceptance.xml
call :run_level "4/6 E2E (toolchain that)"       "tests\e2e"                            junit-4-e2e.xml
call :run_level "5/6 PERFORMANCE"                "tests\performance"                    junit-5-performance.xml
call :run_level "6/6 DESKTOP-CLIENT + COVERAGE"  "apps\desktop-client\tests"            junit-6-desktop-client.xml

echo.
echo ============================================================
if "%FAILED%"=="1" (
    echo [KET QUA] CO LEVEL TEST BI LOI - xem chi tiet phia tren.
    echo Bao cao: reports\*.xml
    pause
    endlocal
    exit /b 1
)
echo [KET QUA] TAT CA CAC LEVEL TEST DEU PASS.
echo Bao cao: reports\*.xml
pause
endlocal
exit /b 0

:run_level
echo.
echo ============================================================
echo  %~1
echo ============================================================
"%PYTHON_CMD%" -m pytest %~2 -v --durations=10 --junitxml="reports\%~3" !COV_FLAGS!
if errorlevel 1 set "FAILED=1"
exit /b 0
