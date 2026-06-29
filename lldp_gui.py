#!/usr/bin/env python3
"""
LLDP Network Device Scanner - Tkinter GUI Version
A simple graphical interface for the LLDP scanner.
"""

import sys
import tkinter as tk
from tkinter import ttk, filedialog, Menu
import threading
import time
from datetime import datetime
import json
import os

from lldp_scanner import LLDPScanner
from lldp_utils.interface import list_interfaces, is_valid_npf_name


class LLDPScannerGUI:
    def __init__(self, root):
        self.root = root
        self._setup_window()
        self.scanner = None
        self.scanning = False
        self.selected_iface_npf = None  # store the NPF name of selected item
        self.all_results = []  # store all results for filtering
        self.current_filter = tk.StringVar()
        self.current_filter.trace_add("write", self.on_search_change)
        self.settings_file = os.path.join(os.path.dirname(__file__), 'lldp_scanner_settings.json')
        # Theme handling
        self.dark_mode = False
        self.style = ttk.Style()
        # Column visibility
        self.column_widths = {}  # store original widths for hidden columns
        self.hidden_columns = set()
        self._column_vars = {}  # store BooleanVars for column menu checkbuttons

        self.create_widgets()
        self.load_interfaces()
        self.load_settings()
        self.apply_settings()
        self.apply_theme()  # apply initial theme (light)

    def _setup_window(self):
        """Configure the main window properties."""
        self.root.title("LLDP Network Device Scanner")
        self.root.update_idletasks()
        self.root.geometry("800x600")
        # Make window resizable
        self.root.resizable(True, True)
        # Start maximized/full screen
        self.root.state('zoomed')  # Start maximized on Windows

    # --------------------------------------------------------------------- #
    # Widget creation
    # --------------------------------------------------------------------- #
    def create_widgets(self):
        # ---- main frame ----------------------------------------------------
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # ---- configure grid layout -----------------------------------------
        self._configure_grid_weights(main_frame)

        # ---- create left pane (interface selector) -------------------------
        self.left_frame = ttk.Frame(main_frame)
        self.left_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))
        self.left_frame.rowconfigure(0, weight=0)   # label fixed height
        self.left_frame.rowconfigure(1, weight=1)   # list area expands
        self.left_frame.columnconfigure(0, weight=1) # single column expands
        self._create_interface_selector(self.left_frame)

        # ---- create right pane (controls + results) ------------------------
        self.right_frame = ttk.Frame(main_frame)
        self.right_frame.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.W, tk.E))
        # row 0: button frame + search frame (horizontal)
        # row 1: label for results (fixed height)
        # row 2: treeview (expandable)
        self.right_frame.rowconfigure(0, weight=0)   # button/search row
        self.right_frame.rowconfigure(1, weight=0)   # results label
        self.right_frame.rowconfigure(2, weight=1)   # treeview expands
        self.right_frame.columnconfigure(0, weight=0) # left side (buttons) fixed width
        self.right_frame.columnconfigure(1, weight=1) # spacer expands
        self.right_frame.columnconfigure(2, weight=0) # right side (search) fixed width

        # button frame (left side of row 0)
        button_frame = ttk.Frame(self.right_frame)
        button_frame.grid(row=0, column=0, sticky=tk.W, padx=(0,5), pady=(0,10))
        self._create_button_frame_contents(button_frame)

        # search frame (right side of row 0)
        self._create_search_frame(self.right_frame, row=0, column=2, padx=(5,0), pady=(0,10), sticky=tk.E)

        # results label and treeview (spanning all three columns, rows 1-2)
        self._create_results_area(self.right_frame, row=1, column=0, columnspan=3)

    def _create_button_frame_contents(self, parent):
        """Create the button frame with start/stop controls (to be placed inside a given parent)."""
        self.start_btn = ttk.Button(parent, text="Start Scan",
                                    command=self.start_scanning, state="disabled")
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.stop_btn = ttk.Button(parent, text="Stop Scan",
                                   command=self.stop_scanning, state="disabled")
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # Add Export button
        self.export_btn = ttk.Button(parent, text="Export Results",
                                     command=self.export_results, state="disabled")
        self.export_btn.pack(side=tk.LEFT, padx=5)

        # Add Columns button
        self.columns_btn = ttk.Button(parent, text="Columns",
                                      command=self.show_column_menu)
        self.columns_btn.pack(side=tk.LEFT, padx=5)

        # Add Toggle Theme button
        self.theme_btn = ttk.Button(parent, text="Toggle Theme",
                                    command=self.toggle_theme)
        self.theme_btn.pack(side=tk.LEFT, padx=5)

        self.status_var = tk.StringVar(value="Ready")
        self.clear_btn = ttk.Button(parent, text="Clear Results",
                                    command=self.clear_results)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        ttk.Label(parent, textvariable=self.status_var).pack(
            side=tk.LEFT, padx=(20, 0)
        )

    def _configure_grid_weights(self, main_frame):
        """Configure grid weights for resizing behavior."""
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        # Two columns: list area (fixed width) and controls/results area (expands)
        main_frame.columnconfigure(0, weight=0)   # list area fixed width
        main_frame.columnconfigure(1, weight=1)   # controls+results area expands
        # Single row that expands vertically
        main_frame.rowconfigure(0, weight=1)

    def _create_interface_selector(self, parent):
        """Create the network interface selector widgets."""
        ttk.Label(parent, text="Network Interface:").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )

        # Frame that holds the listbox + scrollbars
        list_frame = ttk.Frame(parent)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S),
                        pady=(0, 5))

        # Container for listbox and vertical scrollbar (will expand to fill available space)
        list_container = ttk.Frame(list_frame)
        list_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # ----- listbox -------------------------------------------------------
        self.interface_listbox = tk.Listbox(
            list_container,
            height=10,                     # visible items
            width=25,                      # fixed width in characters (reduced)
            exportselection=False,
            relief='sunken',
            borderwidth=2,
            bg='white',
            fg='black',
            selectbackground='#0078d7',
            selectforeground='white',
            activestyle='none'
        )
        self.interface_listbox.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        self.interface_listbox.bind('<<ListboxSelect>>', self.on_interface_select)

        # ----- vertical scrollbar --------------------------------------------
        self.interface_v_scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL)
        self.interface_v_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.interface_listbox.configure(yscrollcommand=self.interface_v_scrollbar.set)
        self.interface_v_scrollbar.configure(command=self.interface_listbox.yview)

        # ----- horizontal scrollbar ------------------------------------------
        self.interface_h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL)
        self.interface_h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.interface_listbox.configure(xscrollcommand=self.interface_h_scrollbar.set)
        self.interface_h_scrollbar.configure(command=self.interface_listbox.xview)

    def _create_button_frame(self, parent, row=0):
        """Create the button frame with start/stop controls."""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.start_btn = ttk.Button(button_frame, text="Start Scan",
                                    command=self.start_scanning, state="disabled")
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.stop_btn = ttk.Button(button_frame, text="Stop Scan",
                                   command=self.stop_scanning, state="disabled")
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # Add Export button
        self.export_btn = ttk.Button(button_frame, text="Export Results",
                                     command=self.export_results, state="disabled")
        self.export_btn.pack(side=tk.LEFT, padx=5)

        # Add Columns button
        self.columns_btn = ttk.Button(button_frame, text="Columns",
                                      command=self.show_column_menu)
        self.columns_btn.pack(side=tk.LEFT, padx=5)

        # Add Toggle Theme button
        self.theme_btn = ttk.Button(button_frame, text="Toggle Theme",
                                    command=self.toggle_theme)
        self.theme_btn.pack(side=tk.LEFT, padx=5)

        self.status_var = tk.StringVar(value="Ready")
        self.clear_btn = ttk.Button(button_frame, text="Clear Results",
                                    command=self.clear_results)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        ttk.Label(button_frame, textvariable=self.status_var).pack(
            side=tk.LEFT, padx=(20, 0)
        )

    def _create_search_frame(self, parent, row=0, column=0, **kwargs):
        """Create the search frame for the results."""
        # Default grid options
        default_options = {'sticky': (tk.W, tk.E), 'pady': (0, 5)}
        default_options.update(kwargs)
        search_frame = ttk.Frame(parent)
        search_frame.grid(row=row, column=column, **default_options)
        # Configure two columns: label (fixed width) and entry (expanding)
        search_frame.columnconfigure(0, weight=0)   # label column
        search_frame.columnconfigure(1, weight=1)   # entry column

        ttk.Label(search_frame, text="Search:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 5)
        )
        self.search_entry = ttk.Entry(search_frame, textvariable=self.current_filter)
        self.search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        # Bind Enter key to trigger search (though trace already does it)
        self.search_entry.bind('<Return>', lambda e: self.on_search_change(None, None, None))

    def _create_results_area(self, parent, row=0, column=0, columnspan=1):
        """Create the results display area (treeview)."""
        ttk.Label(parent, text="Discovered Devices:").grid(
            row=row, column=column, columnspan=columnspan, sticky=tk.W, pady=(0, 5)
        )

        columns = ('timestamp', 'interface', 'chassis_id', 'port_id', 'ttl',
                   'sys_name', 'port_desc', 'sys_cap', 'mgmt_addr')
        self.tree = ttk.Treeview(parent, columns=columns,
                                 show='headings', height=15)

        # headings
        self.tree.heading('timestamp', text='Time')
        self.tree.heading('interface', text='Interface')
        self.tree.heading('chassis_id', text='Chassis ID')
        self.tree.heading('port_id', text='Port ID')
        self.tree.heading('ttl', text='TTL (s)')
        self.tree.heading('sys_name', text='System Name')
        self.tree.heading('port_desc', text='Port Description')
        self.tree.heading('sys_cap', text='Capabilities')
        self.tree.heading('mgmt_addr', text='Mgmt Address')

        # column widths
        self.tree.column('timestamp', width=150)
        self.tree.column('interface', width=150)
        self.tree.column('chassis_id', width=120)
        self.tree.column('port_id', width=120)
        self.tree.column('ttl', width=60)
        self.tree.column('sys_name', width=150)
        self.tree.column('port_desc', width=150)
        self.tree.column('sys_cap', width=150)
        self.tree.column('mgmt_addr', width=120)

        self.tree.grid(row=row+1, column=column, columnspan=columnspan, sticky=(tk.W, tk.E, tk.N, tk.S))

        # ---- resize weights for results ------------------------------------
        for col_idx in range(column, column + columnspan):
            parent.columnconfigure(col_idx, weight=1)
        parent.rowconfigure(row+1, weight=1)

        # Bind heading clicks for column menu
        self.tree.bind('<Button-2>', self.show_column_menu)  # Right-click
        self.tree.bind('<Button-3>', self.show_column_menu)  # Right-click (alternative)
        for col in columns:
            self.tree.heading(col, command=lambda c=col: self.show_column_menu(None, c))

    def show_column_menu(self, event=None, column=None):
        """Show a menu to toggle column visibility."""
        # Create menu if not exists
        if not hasattr(self, '_column_menu'):
            self._column_menu = Menu(self.root, tearoff=0)
            self._column_menu_entries = {}
            columns = ('timestamp', 'interface', 'chassis_id', 'port_id', 'ttl',
                       'sys_name', 'port_desc', 'sys_cap', 'mgmt_addr')
            for col in columns:
                var = tk.BooleanVar(value=True)  # Initially visible
                self._column_vars[col] = var
                self._column_menu_entries[col] = self._column_menu.add_checkbutton(
                    label=col.replace('_', ' ').title(),
                    variable=var,
                    command=lambda c=col: self.toggle_column(c)
                )
        # Post menu at mouse position or widget
        if event:
            self._column_menu.tk_popup(event.x_root, event.y_root)
        else:
            # If called from heading, approximate position
            self._column_menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())

    def toggle_column(self, column):
        """Toggle visibility of a column."""
        if column in self._column_vars:
            visible = self._column_vars[column].get()
            if visible:
                self.hidden_columns.discard(column)
                # Restore width if we have it stored
                if column in self.column_widths:
                    self.tree.column(column, width=self.column_widths[column])
                else:
                    # Use default width
                    self.tree.column(column, width=tk.Font().measure(column.replace('_', ' ').title()) + 20)
            else:
                # Store current width before hiding
                current_width = self.tree.column(column, 'width')
                if current_width != 0:
                    self.column_widths[column] = current_width
                self.hidden_columns.add(column)
                self.tree.column(column, width=0)
            self.save_settings()

    def _apply_column_visibility(self):
        """Apply stored column widths and hide/show columns."""
        for col, width in self.column_widths.items():
            self.tree.column(col, width=width)
        for col in self.hidden_columns:
            self.tree.column(col, width=0)

    def on_search_change(self, *args):
        """Filter results based on search text."""
        search_text = self.current_filter.get().lower()
        # Limit the length of search_text to prevent DoS via overly long strings
        if len(search_text) > 100:
            search_text = search_text[:100]
        # Clear current view
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Re-add filtered results from all_results
        for result in self.all_results:
            # Check if any field contains the search text
            match = False
            for value in result.values():
                if search_text in str(value).lower():
                    match = True
                    break
            if match:
                self.tree.insert('', tk.END, values=tuple(result.values()))

    # --------------------------------------------------------------------- #
    # Interface loading
    # --------------------------------------------------------------------- #
    def load_interfaces(self):
        """Fill the listbox with the interfaces returned by the scanner."""
        try:
            ifaces = list_interfaces()

            # Store raw data for later use
            self.interface_data = ifaces

            # Clear and repopulate the listbox
            self.interface_listbox.delete(0, tk.END)
            for friendly, npf in ifaces:
                # Show friendly name only; fallback to NPF if friendly empty
                display = friendly if friendly else npf
                self.interface_listbox.insert(tk.END, display)

            if ifaces:
                # Select the first item by default
                self.interface_listbox.selection_set(0)
                self.interface_listbox.see(0)          # scroll to top
                self.on_interface_select(None)         # trigger handler
            else:
                self.status_var.set("No interfaces found")

        except Exception as e:
            self.status_var.set("Error loading network interfaces. Please check your network configuration.")
            print("ERROR loading interfaces", flush=True)

    # --------------------------------------------------------------------- #
    # Selection handler
    # --------------------------------------------------------------------- #
    def on_interface_select(self, event):
        """Called when the user picks an interface from the listbox."""
        selection = self.interface_listbox.curselection()
        if selection:
            idx = int(selection[0])
            if hasattr(self, 'interface_data') and idx < len(self.interface_data):
                friendly, iface_npf = self.interface_data[idx]
                if not is_valid_npf_name(iface_npf):
                    self.selected_iface_npf = None
                    self.start_btn.config(state="disabled")
                    self.status_var.set(f"Invalid interface: {friendly}")
                else:
                    self.selected_iface_npf = iface_npf
                    self.start_btn.config(state="normal")
                    self.status_var.set(f"Selected: {friendly}")
            else:
                self.start_btn.config(state="disabled")
        else:
            self.start_btn.config(state="disabled")

    # --------------------------------------------------------------------- #
    # Scanning control
    # --------------------------------------------------------------------- #
    def start_scanning(self):
        """Start LLDP scanning on selected interface"""
        if self.scanning:
            return
        if self.selected_iface_npf is None:
            self.status_var.set("Please select an interface")
            return

        try:
            self.scanner = LLDPScanner(self.selected_iface_npf)

            def lldp_callback(info, ifname):
                # This runs in the scanner thread, so we need to schedule GUI update
                self.root.after(0, self.add_result, info, ifname)

            # Clear previous results when starting a new scan
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.scanner.set_callback(lldp_callback)
            self.scanner.start()

            self.scanning = True
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.status_var.set(f"Scanning on {self.selected_iface_npf}")
            # Enable export button when scanning starts (will have results soon)
            if hasattr(self, 'export_btn'):
                self.export_btn.config(state="normal")

        except Exception as e:
            self.status_var.set("Error starting scan. Please check your network adapter and permissions.")
            print("ERROR starting scan", flush=True)

    def stop_scanning(self):
        """Stop LLDP scanning"""
        if not self.scanning:
            return

        if self.scanner:
            self.scanner.stop()
            self.scanner = None

        self.scanning = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_var.set("Scan stopped")

    def clear_results(self):
        """Clear all results from the treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.status_var.set("Results cleared")

    def export_results(self):
        """Export scan results to a CSV file"""
        if not self.tree.get_children():
            self.status_var.set("No results to export")
            return

        from tkinter import filedialog
        import csv
        import datetime

        # Ask user for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Scan Results"
        )

        if not filename:  # User cancelled
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                # Define CSV headers matching treeview columns
                fieldnames = ['timestamp', 'interface', 'chassis_id', 'port_id', 'ttl',
                             'sys_name', 'port_desc', 'sys_cap', 'mgmt_addr']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # Write header
                writer.writeheader()

                # Write all rows from treeview
                for item_id in self.tree.get_children():
                    values = self.tree.item(item_id)['values']
                    row = dict(zip(fieldnames, values))
                    writer.writerow(row)

            self.status_var.set(f"Results exported to {filename}")
        except Exception as e:
            self.status_var.set(f"Export failed: {str(e)}")
            print(f"ERROR exporting results: {e}")

    # --------------------------------------------------------------------- #
    # Result display (called from main thread via after)
    # --------------------------------------------------------------------- #
    def add_result(self, info, ifname):
        """Add a LLDP result to the treeview (called from main thread)"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Format management address as IPv4 if needed
        mgmt_addr = info.get('mgmt_addr', '')
        if mgmt_addr:
            # Handle common LLDP MGMT address formats
            # Try to extract IPv4 address from various possible formats
            formatted_addr = None

            if isinstance(mgmt_addr, bytes) and len(mgmt_addr) >= 2:
                # Check if it follows LLDP MGMT Address format: subtype + address
                subtype = mgmt_addr[0]
                if subtype == 1 and len(mgmt_addr) >= 5:  # IPv4 subtype
                    # Extract 4 bytes following the subtype
                    ip_bytes = mgmt_addr[1:5]
                    formatted_addr = '.'.join(str(b) for b in ip_bytes)
                elif subtype == 2 and len(mgmt_addr) >= 17:  # IPv6 subtype
                    # For IPv6, we'll leave it as-is for now or convert if needed
                    try:
                        formatted_addr = mgmt_addr[1:17].decode('utf-8', errors='ignore')
                    except:
                        formatted_addr = str(mgmt_addr[1:17])
                else:
                    # Unknown subtype or insufficient data, try to decode as string
                    try:
                        formatted_addr = mgmt_addr.decode('utf-8', errors='ignore')
                    except:
                        formatted_addr = str(mgmt_addr)
            elif isinstance(mgmt_addr, str):
                # Already a string, check if it looks like hex or needs cleaning
                cleaned = mgmt_addr.strip()
                # Remove any whitespace or common separators
                cleaned = cleaned.replace(' ', '').replace('-', '').replace(':', '')

                # Check if it's a hex string that might contain an IPv4 address
                if all(c in '0123456789abcdefABCDEF' for c in cleaned) and len(cleaned) >= 2:
                    # Try to find IPv4 address patterns in the hex string
                    # LLDP MGMT Address format often: [length][subtype=1][ipv4_bytes][optional_interface_info]
                    # IPv4 hex is 8 characters (4 bytes), preceded by subtype byte (2 hex chars)

                    # Scan through the string looking for subtype 1 followed by 4 bytes
                    found_ipv4 = False
                    for i in range(0, len(cleaned) - 10, 2):  # Need at least subtype(2) + ipv4(8) = 10 hex chars
                        if cleaned[i:i+2].lower() == '01':  # Subtype 1 = IPv4
                            try:
                                ip_hex = cleaned[i+2:i+10]  # Next 4 bytes = 8 hex chars
                                if len(ip_hex) == 8:
                                    ip_parts = [str(int(ip_hex[j:j+2], 16)) for j in range(0, 8, 2)]
                                    # Validate each part is 0-255
                                    if all(0 <= int(part) <= 255 for part in ip_parts):
                                        formatted_addr = '.'.join(ip_parts)
                                        found_ipv4 = True
                                        break
                            except (ValueError, IndexError):
                                continue  # Keep looking

                    # If we didn't find a structured IPv4, try simple conversions
                    if not found_ipv4:
                        if len(cleaned) == 8:
                            # Might be direct hex representation of IPv4 (e.g., "C0A80101" for 192.168.1.1)
                            try:
                                formatted_addr = '.'.join(str(int(cleaned[i:i+2], 16)) for i in range(0, 8, 2))
                            except:
                                formatted_addr = cleaned  # Keep original if conversion fails
                        elif '.' in cleaned and len(cleaned.split('.')) == 4:
                            # Already looks like an IPv4 address
                            parts = cleaned.split('.')
                            if all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
                                formatted_addr = cleaned
                            else:
                                formatted_addr = cleaned  # Keep as-is if not valid IP
                        else:
                            formatted_addr = cleaned  # Keep original string
                    # If we found IPv4, formatted_addr is already set
                elif '.' in cleaned and len(cleaned.split('.')) == 4:
                    # Already looks like an IPv4 address (decimal format)
                    parts = cleaned.split('.')
                    if all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
                        formatted_addr = cleaned
                    else:
                        formatted_addr = cleaned  # Keep as-is if not valid IP
                else:
                    formatted_addr = cleaned  # Keep original string
            else:
                # Other types, convert to string
                formatted_addr = str(mgmt_addr)

            # Use the formatted address if we successfully formatted it, otherwise keep original
            if formatted_addr is not None:
                mgmt_addr = formatted_addr

        # Insert at the top (newest first)
        self.tree.insert('', 0, values=(
            timestamp,
            ifname,
            info.get('chassis_id', ''),
            info.get('port_id', ''),
            info.get('ttl', ''),
            info.get('sys_name', ''),
            info.get('port_desc', ''),
            info.get('sys_cap', ''),
            mgmt_addr
        ))

        # Also store in all_results for filtering
        result_dict = {
            'timestamp': timestamp,
            'interface': ifname,
            'chassis_id': info.get('chassis_id', ''),
            'port_id': info.get('port_id', ''),
            'ttl': info.get('ttl', ''),
            'sys_name': info.get('sys_name', ''),
            'port_desc': info.get('port_desc', ''),
            'sys_cap': info.get('sys_cap', ''),
            'mgmt_addr': mgmt_addr
        }
        self.all_results.append(result_dict)
        # Limit all_results to prevent memory issues (keep last 1000)
        if len(self.all_results) > 1000:
            self.all_results = self.all_results[-1000:]

        # Limit to 100 rows to prevent memory issues
        children = self.tree.get_children()
        if len(children) > 100:
            self.tree.delete(children[-1])  # Remove oldest

    # --------------------------------------------------------------------- #
    # Window closing
    # --------------------------------------------------------------------- #
    def on_closing(self):
        """Handle window closing"""
        if self.scanning:
            self.stop_scanning()
        self.save_settings()
        self.root.destroy()

    # --------------------------------------------------------------------- #
    # Theme handling
    # --------------------------------------------------------------------- #
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):
        """Apply the current theme (light or dark) to ttk widgets."""
        if self.dark_mode:
            # Dark theme colors
            bg_color = '#2d2d2d'
            fg_color = '#ffffff'
            entry_bg = '#3c3f41'
            select_bg = '#0078d7'
            # Configure styles
            self.style.theme_use('default')  # Start with default to override
            self.style.configure('.', background=bg_color, foreground=fg_color)
            self.style.configure('TFrame', background=bg_color)
            self.style.configure('TLabel', background=bg_color, foreground=fg_color)
            self.style.configure('TButton', background=bg_color, foreground=fg_color)
            self.style.map('TButton',
                           background=[('active', '#3c3f41'), ('pressed', '#1f1f1f')],
                           foreground=[('disabled', '#a0a0a0')])
            self.style.configure('TEntry', fieldbackground=entry_bg, foreground=fg_color)
            self.style.configure('Treeview',
                                 background=bg_color,
                                 foreground=fg_color,
                                 fieldbackground=bg_color)
            self.style.map('Treeview',
                           background=[('selected', select_bg)])
            self.style.configure('TMenubutton', background=bg_color, foreground=fg_color)
            # Configure listbox and scrollbars (tk widgets)
            listbox_bg = '#1e1e1e'
            listbox_fg = '#ffffff'
            select_bg_listbox = '#0078d7'
            select_fg_listbox = '#ffffff'
            self.interface_listbox.configure(background=listbox_bg,
                                             foreground=listbox_fg,
                                             selectbackground=select_bg_listbox,
                                             selectforeground=select_fg_listbox)
            # ttk scrollbars will pick up style from above
        else:
            # Light theme (use system default)
            self.style.theme_use('vista')  # Windows native look
            # Ensure ttk uses default settings
            self.style.configure('.')  # Reset to theme defaults
            # Reset listbox to system defaults
            self.interface_listbox.configure(background='white',
                                             foreground='black',
                                             selectbackground='#0078d7',
                                             selectforeground='white')

    # --------------------------------------------------------------------- #
    # Settings handling
    # --------------------------------------------------------------------- #
    def load_settings(self):
        """Load settings from JSON file."""
        try:
            if os.path.isfile(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                # Apply settings
                self.dark_mode = settings.get('dark_mode', False)
                self.column_widths = settings.get('column_widths', {})
                self.hidden_columns = set(settings.get('hidden_columns', []))
                # Apply column visibility settings
                self._apply_column_visibility()
                self.current_filter.set(settings.get('search_text', ''))
            else:
                # Default settings
                self.dark_mode = False
                self.column_widths = {}
                self.hidden_columns = set()
                self.current_filter.set('')
        except Exception as e:
            print(f"ERROR loading settings: {e}")

    def save_settings(self):
        """Save settings to JSON file."""
        try:
            settings = {
                'dark_mode': self.dark_mode,
                'column_widths': self.column_widths,
                'hidden_columns': list(self.hidden_columns),
                'search_text': self.current_filter.get()
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"ERROR saving settings: {e}")

    def apply_settings(self):
        """Apply loaded settings to GUI."""
        # Apply theme
        self.apply_theme()
        # Apply column visibility and widths
        self._apply_column_visibility()
        # Apply search text
        self.current_filter.set(self.current_filter.get())


def main():
    root = tk.Tk()
    app = LLDPScannerGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    # Force window to front and give focus
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(lambda: root.attributes('-topmost', False))
    try:
        root.mainloop()
    except Exception as e:
        print(f"ERROR in mainloop: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()