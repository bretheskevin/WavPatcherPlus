@ECHO OFF
rmdir /q /s __pycache__
rmdir /q /s build
rmdir /q /s dist
pyinstaller --onefile win_main.spec
pause
