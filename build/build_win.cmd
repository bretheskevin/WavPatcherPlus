@ECHO OFF
rmdir /q /s __pycache__
rmdir /q /s build
rmdir /q /s dist
pyinstaller --onefile ..\build\win_main.spec
pause
