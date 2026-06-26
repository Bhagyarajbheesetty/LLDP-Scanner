@echo off
REM Build LLDP scanner executable using PyInstaller with Tkinter GUI
echo Installing dependencies...
pip install -r requirements.txt
echo Building executable...
pyinstaller --onefile --name LLDP-scanner lldp_gui.py
echo Build complete. Executable is in dist\LLDP-scanner.exe