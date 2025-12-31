@echo off
REM Start local FastAPI app for testing

cd /d %~dp0
echo Starting FastAPI app locally...
venv\Scripts\python.exe app.py
