@echo off
setlocal
cd /d "%~dp0"

echo Starting AITA Desktop Client...

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

"%PYTHON_CMD%" apps\desktop-client\main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Application exited with error code: %ERRORLEVEL%
    pause
)
endlocal
