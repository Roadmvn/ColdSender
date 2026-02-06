@echo off
echo ========================================
echo   Build Mail Sender
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

echo ----------------------------------------
echo   [1/4] Installation des outils
echo ----------------------------------------
echo.

python -m pip install customtkinter pandas openpyxl Pillow sendgrid pyinstaller

echo.
echo ----------------------------------------
echo   [2/4] Creation de l'executable
echo ----------------------------------------
echo.
echo Cela peut prendre 2-3 minutes...
echo.

python -m PyInstaller --onefile --windowed --name "ColdSender" ^
    --hidden-import=customtkinter ^
    --hidden-import=pandas ^
    --hidden-import=openpyxl ^
    --hidden-import=PIL ^
    --hidden-import=PIL.Image ^
    --hidden-import=sendgrid ^
    --collect-all customtkinter ^
    --add-data "src;src" ^
    main.py

echo.
echo ----------------------------------------
echo   [3/4] Nettoyage
echo ----------------------------------------
rmdir /s /q build 2>nul
del ColdSender.spec 2>nul
echo OK

echo.
echo ========================================
echo   [4/4] BUILD TERMINE !
echo ========================================
echo.
echo L'executable se trouve ici:
echo   dist\ColdSender.exe
echo.
echo Tu peux envoyer ce fichier a ton pote !
echo.
pause
