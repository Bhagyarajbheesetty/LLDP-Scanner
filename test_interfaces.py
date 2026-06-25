import sys
sys.path.insert(0, '.')
from lldp_utils.interface import list_interfaces
try:
    ifaces = list_interfaces()
    print("Interfaces found:", len(ifaces))
    for friendly, npf in ifaces:
        print(f"  {friendly} [{npf}]")
except Exception as e:
    print("Error:", e)
    traceback.print_exc()