@echo off
title EPIGRAPH-AI Launcher
echo ============================================================
echo Starting EPIGRAPH-AI (Backend on port 8000 + Frontend on 5173)...
echo ============================================================

cd /d "%~dp0"
start "EPIGRAPH-AI Backend (Port 8000)" cmd /k "call start_backend.bat"
timeout /t 3 /nobreak >nul
start "EPIGRAPH-AI Frontend (Port 5173)" cmd /k "call start_frontend.bat"

echo.
echo Both servers are starting in separate windows.
echo Web UI will be available at: http://localhost:5173/analysis/new
echo.
pause
