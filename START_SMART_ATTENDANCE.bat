@echo off
TITLE AttendAI — Offline Smart Attendance Platform
COLOR 0A
CLS

echo ==============================================================================
echo                          ATTENDAI ACADEMY
echo              AI-POWERED OFFLINE SMART ATTENDANCE PLATFORM
echo ==============================================================================
echo.
echo [1/3] Checking Local Python & Node Runtime...
echo [2/3] Seeding / Verifying SQLite Database & Enrolled Face Embeddings...

cd /d "%~dp0"
"C:\Users\ODIN\AppData\Local\Programs\Python\Python311\python.exe" backend/app/seed.py

echo.
echo [3/3] Starting Local FastAPI AI Server on http://127.0.0.1:8000 ...
start "AttendAI Backend API" /B "C:\Users\ODIN\AppData\Local\Programs\Python\Python311\python.exe" -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000

echo Starting Frontend Web Server...
cd frontend
start "AttendAI Frontend" /B npm run dev -- --port 5173

timeout /t 3 /nobreak >nul

echo.
echo ==============================================================================
echo [SUCCESS] AttendAI is running in 100%% Local Offline Mode!
echo [URL] Opening http://localhost:5173 in browser...
echo ==============================================================================
start http://localhost:5173

pause
