@echo off
echo Starting EPIGRAPH-AI Frontend Server on port 5173...
cd /d "%~dp0frontend"
call npm.cmd run dev
pause
