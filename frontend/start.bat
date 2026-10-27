
@echo off
set "ROOT=%~dp0.."
for %%I in ("%ROOT%") do set "ROOT=%%~fI"

cd /d "%ROOT%"

if not exist ".venv\Scripts\python.exe" (
    echo Python virtual environment not found.
    pause
    exit /b 1
)

if not exist "backend\requirements.txt" (
    echo Backend requirements file not found.
    pause
    exit /b 1
)

if not exist "frontend\node_modules" (
    pushd "frontend"
    call npm install
    if errorlevel 1 (
        echo Frontend installation failed.
        popd
        pause
        exit /b 1
    )
    popd
)

start "EcoSort API" cmd /k "cd /d ""%ROOT%\backend"" && ""%ROOT%\.venv\Scripts\python.exe"" -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

start "EcoSort UI" cmd /k "cd /d ""%ROOT%\frontend"" && npm run dev -- --host 127.0.0.1"

timeout /t 5 /nobreak >nul
start " " "http://localhost:5173"
exit /b 0
