@echo off
echo ========================================
echo   Mail Sender
echo ========================================
echo.

cd /d "%~dp0"

REM Verifier si Python est installe
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe.
    echo Lance d'abord INSTALL.bat
    pause
    exit /b 1
)

REM Verifier si les dependances sont installees
python -c "import customtkinter" 2>nul
if errorlevel 1 (
    echo Installation des dependances...
    python -m pip install customtkinter pandas openpyxl Pillow
    echo.
)

echo Lancement...
python main.py

if errorlevel 1 (
    echo.
    echo [ERREUR] L'application a crash
    pause
)
