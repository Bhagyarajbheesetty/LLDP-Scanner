"""
Wrapper around the Npcap/WinPcap calls that returns a list of
(user‑friendly name, NPF name) tuples.
"""

import sys
import os
from ctypes import *
from ctypes.wintypes import *

# Re‑use the same wpcap loading logic from lldp_scanner.py
try:
    wpcap = WinDLL("wpcap.dll")
except OSError:
    try:
        wpcap = WinDLL("Packet.dll")
    except OSError:
        possible_paths = [
            r"C:\Windows\System32\wpcap.dll",
            r"C:\Windows\SysWOW64\wpcap.dll",
            r"C:\Program Files\npcap\wpcap.dll",
            r"C:\Program Files (x86)\npcap\wpcap.dll",
        ]
        for p in possible_paths:
            if os.path.exists(p):
                wpcap = WinDLL(p)
                break
        else:
            raise OSError("Unable to load wpcap.dll or Packet.dll. "
                          "Install Npcap in WinPcap‑compatible mode.")

# Function prototypes (same as before)
pcap_findalldevs = wpcap.pcap_findalldevs
pcap_findalldevs.restype = c_int
pcap_freealldevs = wpcap.pcap_freealldevs
pcap_freealldevs.restype = None
pcap_lookupdev = wpcap.pcap_lookupdev
pcap_lookupdev.argtypes = [c_char_p]
pcap_lookupdev.restype = c_char_p

class pcap_if(Structure):
    pass
pcap_if._fields_ = [
    ("next", POINTER(pcap_if)),
    ("name", c_char_p),
    ("description", c_char_p),
    ("addresses", c_void_p),
    ("flags", c_uint),
]

pcap_if_ptr      = POINTER(pcap_if)
pcap_if_ptr_ptr  = POINTER(pcap_if_ptr)

pcap_findalldevs.argtypes = [pcap_if_ptr_ptr, c_char_p]
pcap_freealldevs.argtypes = [pcap_if_ptr]

def _errbuf_to_string(errbuf):
    return ctypes.c_char_p(errbuf).value.decode('mbcs', errors='ignore')

def _friendly_from_guid(guid: str):
    """Extract the human‑readable description from the registry (same as before)."""
    try:
        try:
            import _winreg as winreg
        except ImportError:
            import winreg
        key_path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            i = 0
            while True:
                try:
                    sub = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, sub) as sk:
                        try:
                            inst, _ = winreg.QueryValueEx(sk, "NetCfgInstanceId")
                            if isinstance(inst, str) and inst.lower() == "{" + guid.lower() + "}":
                                try:
                                    return winreg.QueryValueEx(sk, "DriverDesc")[0]
                                except FileNotFoundError:
                                    pass
                        except FileNotFoundError:
                            pass
                    i += 1
                except OSError:
                    break
    except Exception:
        pass
    return None

def list_interfaces():
    """
    Return a list of tuples: (friendly_name, npf_name).
    If no friendly name can be obtained, the NPF name is used for both entries.
    """
    ifaces = []
    if pcap_findalldevs:
        alldevs_ptr = POINTER(pcap_if)()
        errbuf = create_string_buffer(256)
        ret = pcap_findalldevs(byref(alldevs_ptr), errbuf)
        if ret != 0:
            raise RuntimeError(_errbuf_to_string(errbuf))
        dev = alldevs_ptr
        while dev:
            name = dev.contents.name.decode('mbcs', errors='ignore')
            desc = dev.contents.description
            friendly = None
            if desc:
                desc = desc.decode('mbcs', errors='ignore')
                if desc.strip():
                    friendly = desc
            # If we didn't get a friendly name from description, try to get it from the registry via the GUID
            if not friendly:
                # Try to extract GUID from NPF name pattern: \Device\NPF_{<guid>}
                if name.startswith(r'\Device\NPF{') and name.endswith('}'):
                    guid = name[len(r'\Device\NPF{'):-1]  # extract the GUID without braces
                    friendly = _friendly_from_guid(guid)
            # If still no friendly name, fallback to the NPF name
            if not friendly:
                friendly = name
            ifaces.append((friendly, name))
            dev = dev.contents.next
        if alldevs_ptr:
            pcap_freealldevs(alldevs_ptr)
    else:
        # Fallback: just use default device
        errbuf = create_string_buffer(256)
        dev = pcap_lookupdev(errbuf)
        if not dev:
            raise RuntimeError(_errbuf_to_string(errbuf))
        name = dev.decode('mbcs', errors='ignore')
        friendly = None
        # Try to get the friendly name from the registry via the GUID.
        # Extract GUID from NPF name pattern: \Device\NPF_{<guid>}
        if name.startswith(r'\Device\NPF{') and name.endswith('}'):
            guid = name[len(r'\Device\NPF{'):-1]  # extract the GUID without braces
            friendly = _friendly_from_guid(guid)
        # If still no friendly name, fallback to the NPF name
        if not friendly:
            friendly = name
        ifaces.append((friendly, name))
    return ifaces