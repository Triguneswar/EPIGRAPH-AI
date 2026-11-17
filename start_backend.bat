@echo off
echo Starting EPIGRAPH-AI Backend Server on port 8000...
cd /d "%~dp0backend"
"C:\Users\nagat\AppData\Local\Programs\Python\Python312\python.exe" -m uvicorn app.main:app --reload --port 8000
pause
