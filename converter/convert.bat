@echo off
rem Command-line conversion without the web app.
rem Usage: convert.bat C:\path\to\old-project.zip
rem    or: drag a .zip file onto this file.
if "%~1"=="" (
  echo Usage: convert.bat C:\path\to\old-project.zip
  pause
  exit /b 1
)
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" converter.py "%~1"
) else (
  python converter.py "%~1"
)
pause
