@echo off
REM Build LLDP scanner executable using PyInstaller with Tkinter GUI
echo Installing dependencies...
pip install -r requirements.txt
echo Building executable...
pyinstaller --onefile --name lldp_scanner lldp_gui.py
echo Build complete. Executable is in dist\lldp_scanner.exe
pause