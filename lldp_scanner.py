#!/usr/bin/env python3
"""
LLDP Network Device Scanner (standalone executable)
Discovers network devices using LLDP and prints info in real-time.
Only requires Npcap installed in WinPcap-compatible mode.
"""

import sys
import struct
import threading
import time
from datetime import datetime
from ctypes import *
from ctypes.wintypes import *

# Import shared utilities
from lldp_utils.parsing import (
    ETH_P_LLDP,
    TLV_CHASSIS_ID, TLV_PORT_ID, TLV_TTL, TLV_PORT_DESCRIPTION,
    TLV_SYSTEM_NAME, TLV_SYSTEM_DESCRIPTION, TLV_SYSTEM_CAPABILITIES,
    TLV_MANAGEMENT_ADDRESS, TLV_END_OF_LLDPDU,
    CHASSIS_SUBTYPE, PORT_SUBTYPE,
    CAP_OTHER, CAP_REPEATER, CAP_BRIDGE, CAP_WLAN_ACCESS_POINT,
    CAP_ROUTER, CAP_TELEPHONE, CAP_DOCSIS_CABLE_DEVICE,
    CAP_STATION_ONLY, CAP_RESERVED, CAPABILITY_NAMES,
    parse_tlv, decode_chassis_id, decode_port_id,
    decode_system_capabilities, decode_management_address,
    decode_lldp_packet
)

from lldp_utils.interface import list_interfaces, is_valid_npf_name

# ---------- WinPcap/Npcap structures via ctypes ----------
try:
    wpcap = WinDLL("wpcap.dll")
except OSError:
    try:
        wpcap = WinDLL("Packet.dll")
    except OSError:
        import os
        possible_paths = [
            r"C:\Windows\System32\wpcap.dll",
            r"C:\Windows\SysWOW64\wpcap.dll",
            r"C:\Program Files\npcap\wpcap.dll",
            r"C:\Program Files (x86)\npcap\wpcap.dll"
        ]
        loaded = False
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    wpcap = WinDLL(path)
                    loaded = True
                    break
                except OSError:
                    continue
        if not loaded:
            print("Error: Unable to load the required network library. Ensure Npcap is installed in WinPcap-compatible mode.")
            sys.exit(1)

# Define structs needed for pcap API
class timeval(Structure):
    _fields_ = [("tv_sec", c_long),
                ("tv_usec", c_long)]

class pcap_pkthdr(Structure):
    _fields_ = [("ts", timeval),
                ("caplen", c_uint),
                ("len", c_uint)]

# Function prototypes
pcap_lookupdev = wpcap.pcap_lookupdev
pcap_lookupdev.argtypes = [c_char_p]
pcap_lookupdev.restype = c_char_p

pcap_open_live = wpcap.pcap_open_live
pcap_open_live.argtypes = [c_char_p, c_int, c_int, c_int, c_char_p]
pcap_open_live.restype = c_void_p

pcap_loop = wpcap.pcap_loop
pcap_loop.argtypes = [c_void_p, c_int, CFUNCTYPE(None, POINTER(c_ubyte), POINTER(pcap_pkthdr), POINTER(c_ubyte)), c_void_p]
pcap_loop.restype = c_int

pcap_datalink = wpcap.pcap_datalink
pcap_datalink.argtypes = [c_void_p]
pcap_datalink.restype = c_int

pcap_close = wpcap.pcap_close
pcap_close.argtypes = [c_void_p]
pcap_close.restype = None

pcap_geterr = wpcap.pcap_geterr
pcap_geterr.argtypes = [c_void_p]
pcap_geterr.restype = c_char_p

pcap_setnonblock = wpcap.pcap_setnonblock
pcap_setnonblock.argtypes = [c_void_p, c_int, c_char_p]
pcap_setnonblock.restype = c_int

pcap_breakloop = wpcap.pcap_breakloop
pcap_breakloop.argtypes = [c_void_p]
pcap_breakloop.restype = c_int

# pcap_findalldevs and pcap_freealldevs may exist
try:
    pcap_findalldevs = wpcap.pcap_findalldevs
    pcap_findalldevs.restype = c_int
except AttributeError:
    pcap_findalldevs = None

try:
    pcap_freealldevs = wpcap.pcap_freealldevs
    pcap_freealldevs.restype = None
except AttributeError:
    pcap_freealldevs = None

if pcap_findalldevs:
    # Define pcap_if structure
    class pcap_if(Structure):
        pass
    pcap_if._fields_ = [
        ("next", POINTER(pcap_if)),
        ("name", c_char_p),
        ("description", c_char_p),
        ("addresses", c_void_p),  # we ignore
        ("flags", c_uint)
    ]
    # Define pointer types
    pcap_if_ptr = POINTER(pcap_if)
    pcap_if_ptr_ptr = POINTER(pcap_if_ptr)
    pcap_findalldevs.argtypes = [pcap_if_ptr_ptr, c_char_p]
    pcap_freealldevs.argtypes = [pcap_if_ptr]

# ---------- Helper functions ----------
def errbuf_to_string(errbuf):
    return ctypes.c_char_p(errbuf).value.decode('mbcs', errors='ignore')

# ---------- LLDP Scanner Class ----------
class LLDPScanner:
    def __init__(self, interface_npf):
        self.interface_npf = interface_npf
        self.adhandle = None
        self.running = False
        self.thread = None
        self.callback = None
        self.user_data = None

    def set_callback(self, callback):
        self.callback = callback

    def _make_handler(self):
        def handler(user, header, pkt_data):
            if not self.running:
                return
            pkt_len = header.contents.len
            caplen = header.contents.caplen
            if pkt_len < 14:
                return
            raw = bytes((pkt_data[i] for i in range(min(pkt_len, caplen))))
            if len(raw) < 14:
                return
            ethertype = struct.unpack('!H', raw[12:14])[0]
            if ethertype != ETH_P_LLDP:
                return
            lldp_raw = raw[14:]
            info = decode_lldp_packet(lldp_raw)
            if not info:
                return
            if self.callback:
                self.callback(info, self.interface_npf)
        return handler

    def start(self):
        if self.running:
            return
        errbuf = create_string_buffer(256)
        self.adhandle = pcap_open_live(self.interface_npf.encode('mbcs'), 65535, 1, 1000, errbuf)
        if not self.adhandle:
            raise RuntimeError("Unable to open network adapter. Please check that the interface is available and you have sufficient permissions.")
        # Check link type (optional)
        linktype = pcap_datalink(self.adhandle)
        if linktype != 1:  # DLT_EN10MB
            print(f"Warning: Link-layer type {linktype} is not Ethernet (1). LLDP may not be captured correctly.")
        # Prepare callback
        handler_func = self._make_handler()
        cbfunc = CFUNCTYPE(None, POINTER(c_ubyte), POINTER(pcap_pkthdr), POINTER(c_ubyte))(handler_func)
        self.running = True
        def capture_loop():
            result = pcap_loop(self.adhandle, -1, cbfunc, self.user_data)
            if result == -1 and self.running:
                print("Error during packet capture. Please check your network adapter and try again.")
            self.stop()
        self.thread = threading.Thread(target=capture_loop, daemon=True)
        self.thread.start()

    def stop(self):
        if not self.running:
            return
        self.running = False
        if self.adhandle:
            pcap_breakloop(self.adhandle)
            pcap_close(self.adhandle)
            self.adhandle = None
        if self.thread:
            self.thread.join(timeout=2)
            self.thread = None

# ---------- Packet handler (for command-line version) ----------
def make_handler(ifname):
    seen = {}
    def handler(user, header, pkt_data):
        pkt_len = header.contents.len
        caplen = header.contents.caplen
        if pkt_len < 14:
            return
        raw = bytes((pkt_data[i] for i in range(min(pkt_len, caplen))))
        if len(raw) < 14:
            return
        ethertype = struct.unpack('!H', raw[12:14])[0]
        if ethertype != ETH_P_LLDP:
            return
        lldp_raw = raw[14:]
        info = decode_lldp_packet(lldp_raw)
        if not info:
            return
        key = (info['chassis_id'], info['port_id'])
        now = time.time()
        if key in seen:
            last_time, _ = seen[key]
            if now - last_time < 5:
                return
        seen[key] = (now, info)
        ts = datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{ts}] Interface: {ifname}")
        print(f"  Chassis ID: {info['chassis_id']} ({CHASSIS_SUBTYPE.get(info['chassis_subtype'], 'unknown')})")
        print(f"  Port ID:    {info['port_id']} ({PORT_SUBTYPE.get(info['port_subtype'], 'unknown')})")
        print(f"  TTL:        {info['ttl']} seconds")
        if info['port_desc']:
            print(f"  Port Description: {info['port_desc']}")
        if info['sys_name']:
            print(f"  System Name: {info['sys_name']}")
        if info['sys_desc']:
            print(f"  System Description: {info['sys_desc']}")
        if info['sys_cap']:
            print(f"  System Capabilities: {info['sys_cap']}")
        if info['mgmt_addr']:
            print(f"  Management Address: {info['mgmt_addr']}")
        print()
        sys.stdout.flush()
    return handler

# ---------- Main ----------
def main():
    print("LLDP Network Device Scanner")
    print("===========================")
    # List interfaces
    try:
        ifaces = list_interfaces()
    except Exception as e:
        print(f"Error listing interfaces: {e}")
        print("Make sure Npcap is installed in WinPcap-compatible mode.")
        sys.exit(1)

    if not ifaces:
        print("No network interfaces found.")
        sys.exit(0)

    print("\nAvailable network interfaces:")
    for idx, (friendly, npf) in enumerate(ifaces, 1):
        if friendly != npf:
            print(f"  {idx}. {friendly} [{npf}]")
        else:
            print(f"  {idx}. {npf}")

    # Select interface
    while True:
        try:
            choice = input("\nSelect interface number (or 'q' to quit): ").strip()
            if choice.lower() == 'q':
                return
            idx = int(choice) - 1
            if 0 <= idx < len(ifaces):
                _, iface_npf = ifaces[idx]
                if not is_valid_npf_name(iface_npf):
                    print(f"Invalid interface name: {iface_npf}. Please select a different interface.")
                    continue
                break
            else:
                print("Invalid number.")
        except ValueError:
            print("Please enter a number.")

    # Open device for capturing
    errbuf = create_string_buffer(256)
    adhandle = pcap_open_live(iface_npf.encode('mbcs'), 65535, 1, 1000, errbuf)
    if not adhandle:
        print("\nUnable to open network adapter. Please check that the interface is available and you have sufficient permissions.")
        sys.exit(1)

    # Check link type (optional)
    linktype = pcap_datalink(adhandle)
    if linktype != 1:  # DLT_EN10MB
        print(f"Warning: Link-layer type {linktype} is not Ethernet (1). LLDP may not be captured correctly.")
        # Continue anyway

    # Prepare callback
    user_data = None
    handler_func = make_handler(iface_npf)
    cbfunc = CFUNCTYPE(None, POINTER(c_ubyte), POINTER(pcap_pkthdr), POINTER(c_ubyte))(handler_func)

    print(f"\nListening for LLDP frames on {iface_npf}... Press Ctrl+C to stop.\n")
    sys.stdout.flush()

    def capture_loop():
        result = pcap_loop(adhandle, -1, cbfunc, user_data)
        if result == -1:
            err = pcap_geterr(adhandle)
            print("\nError during packet capture. Please check your network adapter and try again.")
        pcap_close(adhandle)

    t = threading.Thread(target=capture_loop, daemon=True)
    t.start()

    try:
        while t.is_alive():
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping...")
        pcap_breakloop(adhandle)
        t.join(timeout=2)
        print("Stopped.")
    finally:
        pcap_close(adhandle)

if __name__ == "__main__":
    main()