if exist build rmdir /s /q build
if exist dist rmdir /s /q dist


pyinstaller --onefile --windowed main.py