@echo off
echo ========================================
echo   Installation Mail Sender
echo ========================================
echo.

REM Verifier si Python est installe
python --version >nul 2>&1
if errorlevel 1 (
    echo Python n'est pas installe sur ce PC.
    echo.
    echo ========================================
    echo   INSTRUCTIONS
    echo ========================================
    echo 1. Clique sur "Download Python 3.x.x"
    echo 2. Lance l'installateur
    echo 3. COCHE "Add Python to PATH" en bas !
    echo 4. Clique "Install Now"
    echo 5. Relance INSTALL.bat apres
    echo ========================================
    echo.
    pause
    start https://www.python.org/downloads/
    exit /b 0
)

echo [OK] Python detecte:
python --version
echo.

echo ----------------------------------------
echo   Installation des dependances
echo ----------------------------------------
echo.

echo [1/4] Mise a jour de pip...
python -m pip install --upgrade pip

echo.
echo [2/4] Installation de CustomTkinter...
python -m pip install customtkinter

echo.
echo [3/4] Installation de Pandas...
python -m pip install pandas

echo.
echo [4/4] Installation de Openpyxl ^(Excel^)...
python -m pip install openpyxl

echo.
echo ========================================
echo   Installation terminee !
echo ========================================
echo.
echo Tu peux maintenant:
echo   - run.bat     = Lancer l'app
echo   - build.bat   = Creer l'exe
echo.
pause
