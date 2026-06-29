@echo off
REM Build LLDP scanner executable using PyInstaller with Tkinter GUI
echo Installing dependencies...
py -m pip install -r requirements.txt
echo Building executable...
py -m PyInstaller --onefile --name LLDP-scanner --hidden-import=winreg lldp_gui.py
echo Build complete. Executable is in dist\LLDP-scanner.exe