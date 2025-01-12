@echo off
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

python -m PyInstaller --clean ^
    --onefile ^
    --windowed ^
    --add-data "lib;lib" ^
    --add-data "config.ini;." ^
    --name "wow_finger" ^
    app.py

if errorlevel 1 (
    echo Compilation failed!
    pause
    exit /b 1
)

echo Compilation successful!
pause