# LLDP Network Device Scanner – Project Brief

## Project Overview
The LLDP Network Device Scanner is a Windows‑based utility that captures and displays Link Layer Discovery Protocol (LLDP) packets in real time. The application provides a graphical user interface (built with Python Tkinter) for discovering directly‑connected network devices, visualizing their chassis/port information, management addresses, and capabilities, and exporting results for further analysis.

## Timeline
- **Start Date:** 2025‑09‑01 (initial concept and requirements gathering)
- **Development Phases:**
  - **Phase 1 (Sep 2025):** Core LLDP capture using Npcap/wpcap.dll, CLI prototype.
  - **Phase 2 (Oct‑Nov 2025):** Tkinter GUI implementation – interface selector, results treeview, start/stop controls.
  - **Phase 3 (Dec 2025‑Jan 2026):** Added features – column visibility, dark/light theme, persistent settings, CSV export, real‑time search.
  - **Phase 4 (Feb‑Mar 2026):** UI refinements – fixed‑width interface selector with scrollbars, relocated search box, removed results‑table scrollbar, theme‑aware widget styling.
  - **Phase 5 (Apr‑May 2026):** Stabilization, bug‑fixes, performance optimization, documentation.
- **End Date:** 2026‑06‑26 (final build, README update, and repository push)

## LLDP Features Implemented
| Feature | Description |
|---------|-------------|
| **LLDP Packet Capture** | Uses Npcap in WinPcap‑API compatible mode to sniff Ethernet frames with EtherType 0x88CC. |
| **TLV Parsing** | Decodes Chassis ID, Port ID, TTL, System Name, Port Description, System Capabilities, and Management Address TLVs. |
| **Management Address Handling** | Automatically extracts IPv4 addresses from LLDP MGMT Address TLV (subtype 1) and displays them in dotted‑decimal format; falls back to raw data for IPv6 or other subtypes. |
| **Real‑time Updates** | New LLDP frames are inserted at the top of the results table as they arrive. |
| **Result Limiting** | Table limited to the 100 most recent entries to bound memory usage. |
| **Export** | CSV export (UTF‑8) of all currently visible rows, with user‑chosen filename. |
| **Search / Filter** | Live filtering as the user types; matches any column (case‑insensitive). |
| **Column Visibility** | Users can show/hide any column via a check‑box menu; column widths and hidden state are persisted. |
| **Theme Support** | Light (Windows native) and dark themes; theme applies to Treeview, buttons, entry fields, listbox, and scrollbars. |
| **Persistent Settings** | Last selected interface, window size/position, column widths, hidden columns, theme, and search text are saved to `lldp_scanner_settings.json` and restored on launch. |
| **Interface Selector** | Lists only friendly network interface names (no `[NPF]` clutter); includes functional vertical and horizontal scrollbars for long lists. |
| **Toolbar Layout** | Buttons (Start/Stop/Export/Columns/Toggle Theme/Clear) left‑aligned; Search box right‑aligned on the same row for a clean UI. |
| **Single Executable** | Bundled with PyInstaller (`dist\LLDP‑scanner.exe`) for zero‑install distribution on Windows. |
| **Command‑Line Interface** | Original CLI (`python lldp_scanner.py`) retained for terminal‑only usage. |

## Application Notes
- **Administrator Required:** Raw socket access via Npcap necessitates running the executable (or script) with Administrator privileges.
- **Npcap Installation:** Must be installed in *WinPcap API‑compatible mode* (option checked during setup). Without this mode the capture will fail.
- **Link‑Local Scope:** LLDP is a Layer 2 protocol; the scanner only sees devices directly attached to the selected interface (no routing across subnets).
- **Idle Behaviour:** If no LLDP traffic is present on the chosen interface, the UI remains idle until a packet arrives or the user stops the scan.
- **Memory Management:** The internal `all_results` list is capped at 1000 entries; the visible table is capped at 100 rows.
- **Cross‑Platform Considerations:** The core capture logic relies on Windows‑specific Npcap/wpcap.dll; the GUI (Tkinter) is cross‑platform, but the capture component limits deployment to Windows.
- **Licensing:** The project is released under a permissive MIT‑style license (see LICENSE file) for educational and commercial reuse.

## Conclusion
The LLDP Network Device Scanner now delivers a polished, feature‑rich GUI that meets the original goals of real‑time LLDP discovery, intuitive interaction, and easy result export. All requested UI adjustments (search box relocation, fixed‑width interface selector with scrollbars, removal of the results‑table scrollbar) have been incorporated, documented, and the final build is available in the repository under `dist\LLDP‑scanner.exe`.

For future work, consider:
- Adding support for LLDP-MED extensions.
- Providing a 64‑bit only build to reduce size.
- Implementing a packet‑view window for raw LLDP payload inspection.
- Extending persistent settings to include UI font/size preferences.

---  
*Document generated on 2026‑06‑26 as part of project closure.*