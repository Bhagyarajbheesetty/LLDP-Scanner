"""
Low‑level LLDP helpers – pure functions, no I/O.
"""

import struct
from typing import Dict, Any, Optional

# ----------------------------------------------------------------------
# TLV constants (mirrored from lldp_scanner.py – keep them in one place)
# ----------------------------------------------------------------------
ETH_P_LLDP = 0x88CC

TLV_CHASSIS_ID   = 1
TLV_PORT_ID      = 2
TLV_TTL          = 3
TLV_PORT_DESCRIPTION = 4
TLV_SYSTEM_NAME  = 5
TLV_SYSTEM_DESCRIPTION = 6
TLV_SYSTEM_CAPABILITIES = 7
TLV_MANAGEMENT_ADDRESS = 8
TLV_END_OF_LLDPDU = 0

# ----------------------------------------------------------------------
# Subtype maps (also moved here)
# ----------------------------------------------------------------------
CHASSIS_SUBTYPE = {
    1: "chassis component",
    2: "interface alias",
    3: "port component",
    4: "mac address",
    5: "network address",
    6: "interface name",
    7: "local",
}
PORT_SUBTYPE = {
    1: "interface alias",
    2: "port component",
    3: "mac address",
    4: "network address",
    5: "interface name",
    6: "agent circuit id",
    7: "local",
}

# ----------------------------------------------------------------------
# System capabilities (bit → name) – names match original lldp_scanner.py
# ----------------------------------------------------------------------
CAP_OTHER = 0x0001
CAP_REPEATER = 0x0002
CAP_BRIDGE = 0x0004
CAP_WLAN_ACCESS_POINT = 0x0008
CAP_ROUTER = 0x0010
CAP_TELEPHONE = 0x0020
CAP_DOCSIS_CABLE_DEVICE = 0x0040
CAP_STATION_ONLY = 0x0080
CAP_RESERVED = 0x8000

CAPABILITY_NAMES = {
    CAP_OTHER: "Other",
    CAP_REPEATER: "Repeater",
    CAP_BRIDGE: "Bridge",
    CAP_WLAN_ACCESS_POINT: "WLAN Access Point",
    CAP_ROUTER: "Router",
    CAP_TELEPHONE: "Telephone",
    CAP_DOCSIS_CABLE_DEVICE: "DOCSIS Cable Device",
    CAP_STATION_ONLY: "Station only",
}

# ----------------------------------------------------------------------
# Core parsing
# ----------------------------------------------------------------------
def parse_tlv(data: bytes) -> Dict[int, bytes]:
    """
    Convert raw LLDP TLV block into a dict {type: value}.
    Mirrors the logic that lived inside lldp_scanner.parse_tlv.
    """
    i = 0
    tlvs: Dict[int, bytes] = {}
    n = len(data)
    while i + 2 <= n:
        tvinfo = struct.unpack('>H', data[i:i+2])[0]
        ttype = (tvinfo >> 9) & 0x7F          # 7‑bit type
        tlen  = tvinfo & 0x1FF                # 9‑bit length
        i += 2
        if tlen == 0:                         # End of LLDPDU
            break
        if i + tlen > n:
            break
        tlvs[ttype] = data[i:i+tlen]
        i += tlen
    return tlvs


# ----------------------------------------------------------------------
# Decoding helpers (all pure, return str or empty string)
# ----------------------------------------------------------------------
def _decode_mac(buf: bytes) -> str:
    return ':'.join(f'{b:02x}' for b in buf)

def decode_chassis_id(subtype: int, value: bytes) -> str:
    if subtype == 4:                     # MAC address
        return _decode_mac(value)
    if subtype in (2, 6, 7):             # string
        try:
            return value.decode('utf-8', errors='ignore')
        except Exception:
            return value.hex()
    if subtype == 5:                     # network address (IPv4)
        if len(value) >= 2 and value[0] == 1:
            return '.'.join(str(b) for b in value[1:5])
    return value.hex()

def decode_port_id(subtype: int, value: bytes) -> str:
    if subtype in (3, 4):                # MAC address
        return _decode_mac(value)
    if subtype in (1, 2, 5, 6, 7):       # string
        try:
            return value.decode('utf-8', errors='ignore')
        except Exception:
            return value.hex()
    if subtype == 5:                     # network address (IPv4)
        if len(value) >= 2 and value[0] == 1:
            return '.'.join(str(b) for b in value[1:5])
    return value.hex()

def decode_system_capabilities(value: bytes) -> str:
    if len(value) < 4:
        return ""
    caps = struct.unpack('>H', value[:2])[0]
    names = [name for bit, name in CAPABILITY_NAMES.items() if caps & bit]
    return ', '.join(names) if names else "None"

def decode_management_address(value: bytes) -> str:
    # The spec contains sub‑len, family, address, … – we just hex‑dump for simplicity.
    return value.hex()

def decode_lldp_packet(raw: bytes) -> Optional[Dict[str, Any]]:
    """
    High‑level helper: given the LLDP payload (after Ethernet header),
    return a dict with all decoded fields or None if mandatory TLVs missing.
    """
    tlvs = parse_tlv(raw)
    if not all(k in tlvs for k in (TLV_CHASSIS_ID, TLV_PORT_ID, TLV_TTL)):
        return None

    # Chassis ID
    chest = tlvs[TLV_CHASSIS_ID]
    if len(chest) < 2:
        return None
    chest_subtype = chest[0]
    chest_val = chest[1:]
    chassis_str = decode_chassis_id(chest_subtype, chest_val)

    # Port ID
    port = tlvs[TLV_PORT_ID]
    if len(port) < 2:
        return None
    port_subtype = port[0]
    port_val = port[1:]
    port_str = decode_port_id(port_subtype, port_val)

    # TTL
    ttl_tlv = tlvs[TLV_TTL]
    if len(ttl_tlv) < 2:
        return None
    ttl = struct.unpack('!H', ttl_tlv)[0]

    # Optional TLVs (graceful fallback to empty string)
    port_desc = ""
    if TLV_PORT_DESCRIPTION in tlvs:
        try:
            port_desc = tlvs[TLV_PORT_DESCRIPTION].decode('utf-8', errors='ignore')
        except Exception:
            pass

    sys_name = ""
    if TLV_SYSTEM_NAME in tlvs:
        try:
            sys_name = tlvs[TLV_SYSTEM_NAME].decode('utf-8', errors='ignore')
        except Exception:
            pass

    sys_desc = ""
    if TLV_SYSTEM_DESCRIPTION in tlvs:
        try:
            sys_desc = tlvs[TLV_SYSTEM_DESCRIPTION].decode('utf-8', errors='ignore')
        except Exception:
            pass

    sys_cap = ""
    if TLV_SYSTEM_CAPABILITIES in tlvs:
        sys_cap = decode_system_capabilities(tlvs[TLV_SYSTEM_CAPABILITIES])

    mgmt_addr = ""
    if TLV_MANAGEMENT_ADDRESS in tlvs:
        mgmt_addr = decode_management_address(tlvs[TLV_MANAGEMENT_ADDRESS])

    return {
        'chassis_id':      chassis_str,
        'chassis_subtype': chest_subtype,
        'port_id':         port_str,
        'port_subtype':    port_subtype,
        'ttl':             ttl,
        'port_desc':       port_desc,
        'sys_name':        sys_name,
        'sys_desc':        sys_desc,
        'sys_cap':         sys_cap,
        'mgmt_addr':       mgmt_addr,
    }