cd %~dp0venv\Scripts 
pyinstaller.exe --onefile --windowed --clean --icon=icon.ico %~dp0\main2.py

pause


