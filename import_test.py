# Test that the modules can still import and the function is accessible
print("Testing imports...")

try:
    from lldp_utils.interface import is_valid_npf_name, list_interfaces
    print("[PASS] Successfully imported from lldp_utils.interface")
except Exception as e:
    print(f"[FAIL] Failed to import from lldp_utils.interface: {e}")

try:
    import lldp_scanner
    print("[PASS] Successfully imported lldp_scanner")
except Exception as e:
    print(f"[FAIL] Failed to import lldp_scanner: {e}")

try:
    import lldp_gui
    print("[PASS] Successfully imported lldp_gui")
except Exception as e:
    print(f"[FAIL] Failed to import lldp_gui: {e}")

# Test the function with a few values
print("\nTesting function accessibility:")
try:
    result = is_valid_npf_name(r'\Device\NPF_{12345678-1234-1234-1234-123456789012}')
    print(f"[PASS] Function call successful: {result}")
except Exception as e:
    print(f"[FAIL] Function call failed: {e}")

print("\nImport test completed.")