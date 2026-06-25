import ctypes
from ctypes import *
import os

wpcap = WinDLL("wpcap.dll")
pcap_findalldevs = wpcap.pcap_findalldevs
pcap_findalldevs.restype = c_int

class pcap_if(Structure):
    pass
pcap_if._fields_ = [
    ("next", POINTER(pcap_if)),
    ("name", c_char_p),
    ("description", c_char_p),
    ("addresses", c_void_p),
    ("flags", c_uint)
]

pcap_if_ptr = POINTER(pcap_if)
pcap_if_ptr_ptr = POINTER(pcap_if_ptr)
pcap_findalldevs.argtypes = [pcap_if_ptr_ptr, c_char_p]

alldevs_ptr = pcap_if_ptr()
errbuf = create_string_buffer(256)
ret = pcap_findalldevs(byref(alldevs_ptr), errbuf)
print("ret:", ret)
if ret != 0:
    print("err:", errbuf.value)
else:
    dev = alldevs_ptr
    i = 0
    while dev:
        print(f"Device {i}: name={dev.contents.name}, desc={dev.contents.description}")
        dev = dev.contents.next
        i += 1
