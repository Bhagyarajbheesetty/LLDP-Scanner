# LLDP Network Device Scanner (with GUI)

A lightweight Windows application that discovers network devices using the Link Layer Discovery Protocol (LLDP) and displays their information in real-time via a graphical user interface.

## Features

- **Modern, Responsive GUI**: Built with Tkinter; window opens maximized on startup but remains fully resizable.
- **Two‑Pane Layout**:
  - *Left Pane*: Network Interface Selector – shows only friendly interface names (no `[NPF]` clutter), expands vertically, and automatically selects the first available interface.
  - *Right Pane*: Controls (Start/Stop Scan, Export Results, Clear Results) and a live results table showing the latest LLDP neighbors.
- **Real‑time LLDP Discovery**: Displays Chassis ID, Port ID, TTL, System Name, Port Description, System Capabilities, and Management Address.
- **Intelligent Management Address Handling**:
  - Automatically parses LLDP Management Address TLVs.
  - Extracts and displays IPv4 addresses in dotted‑decimal format (e.g., `192.168.1.1`).
  - Gracefully falls back to raw data for IPv6 or other address types.
- **Result Export**: Click **Export Results** during or after a scan to save the entire table to a CSV file (UTF‑8 encoded) with a user‑chosen filename.
- **Result Filtering**: Type in the **Search** box above the results table to filter rows in real‑time by any column (interface, chassis ID, system name, etc.). The search box is now positioned on the right side of the toolbar for a cleaner layout.
- **Fixed Interface Selector Scrollbars**: The network interface listbox now includes functional vertical and horizontal scrollbars for smooth navigation when many interfaces are present.
- **Column Visibility Control**: Click the **Columns** button (or right‑click any column header) to show/hide columns via a check‑box menu; visibility and column widths are persisted across sessions.
- **Dark / Light Theme Toggle**: Use the **Toggle Theme** button to switch between a light (native Windows) and a dark theme; preference is saved and restored.
- **Persistent Settings**: The application remembers your last‑selected interface, window size/position, column widths, hidden columns, theme choice, and search text, restoring them on the next launch.
- **Memory‑Efficient**: Limits the displayed table to the 100 most recent entries to avoid unbounded growth.
- **Plug‑and‑Play**: Requires only Npcap installed in WinPcap‑API compatible mode.
- **Single Executable**: Can be bundled with PyInstaller for easy distribution.
- **Command‑Line Interface**: The original CLI (`python lldp_scanner.py`) remains available for users who prefer a terminal.

## Prerequisites

- **Windows 10/11**
- **Npcap** installed in *WinPcap API‑compatible mode*  
  (Download from https://nmap.org/npcap/ and ensure the option **"Install Npcap in WinPcap API-compatible Mode"** is checked)
- The application must be run **as Administrator** to access raw network sockets.

## Build Instructions

1. Clone or copy this repository to a Windows machine.
2. Open a Command Prompt **as Administrator** and navigate to the project folder.
3. Install Python dependencies:
   ```bat
   pip install -r requirements.txt
   ```
4. Build the executable:
   ```bat
   build_exe.bat
   ```
   This creates `dist\LLDP-scanner.exe` (the GUI version).

## Usage

### Using the GUI (Recommended)

1. Run `dist\LLDP-scanner.exe` as Administrator.  
   The window starts maximized but you can resize it freely.
2. The left pane lists all available network interfaces (friendly names only). The first item is pre‑selected.
3. Click **Start Scan** to begin capturing LLDP packets on the chosen interface.
   - The button grays out, **Stop Scan** becomes active, and the status bar shows `Scanning on <interface>`.
4. Discovered devices appear in the table on the right, with the newest entries at the top.
   - The **Management Address** column shows a readable IP address when available (e.g., `192.168.1.1`).
5. Use the **Search** box above the table to filter results instantly by any column. The search box is now located on the right side of the toolbar.
6. Click the **Columns** button (or right‑click any column header) to show or hide columns; your visibility choices and column widths are remembered.
7. Click **Toggle Theme** to switch between a light and a dark appearance; your preference is saved.
8. To stop capturing, click **Stop Scan**. Controls return to their initial state.
9. While scanning or after stopping (if results exist), click **Export Results** to save the table to a CSV file of your choice.
10. Click **Clear Results** to remove all displayed entries.
11. Close the window to exit the application.

### Using the Command‑Line Interface

The original command‑line interface is still available:

1. Ensure Python 3.8+ is installed.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the script: `python lldp_scanner.py`
4. Follow the prompts to select an interface and view LLDP information in the console.

## How It Works

The application uses the Npcap/wpcap.dll library (via Python's `ctypes`) to capture Ethernet frames with EtherType `0x88CC` (LLDP). It parses the LLDPDU (Link Layer Discovery Protocol Data Unit) to extract device information.

The GUI version runs a simple Tkinter interface that updates in real‑time as LLDP frames are received.

## Notes

- LLDP is a link‑layer protocol; you will only see devices directly connected to the selected interface (not across routers).
- If no LLDP traffic is detected, the application will appear idle until a frame arrives or you stop the scan.
- The executable bundles the Python interpreter and required libraries; a separate Python installation is not required on the target machine (provided Ncpap is present).

## License

This project is provided as‑is for educational purposes. Feel free to modify and redistribute.

---

*Built with Python, Tkinter, and PyInstaller.*