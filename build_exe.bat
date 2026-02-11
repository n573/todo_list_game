@echo off
echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Building executable...
pyinstaller --onefile --windowed --name "Island Todo Quest" --icon=NONE main.py

echo.
echo Done! Your executable is in the 'dist' folder.
pause
