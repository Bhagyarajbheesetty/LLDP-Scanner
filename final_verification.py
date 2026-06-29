from lldp_utils.interface import is_valid_npf_name
import re

# Test that we can import and that the function works
print("Testing import and basic functionality...")

# Test a known good value
good = r'\Device\NPF_{12345678-1234-1234-1234-123456789012}'
bad = r'\Device\NPF_{12345678-1234-1234-1234-12345678901}'

print(f"Good NPF name: {is_valid_npf_name(good)}")
print(f"Bad NPF name (too short): {is_valid_npf_name(bad)}")

# A truly too long example
test_cases = [
    (r'\Device\NPF_{00000000-0000-0000-0000-000000000000}', True, "All zeros"),
    (r'\Device\NPF_{ffffffff-ffff-ffff-ffff-ffffffffffff}', True, "All F's"),
    (r'\Device\NPF_{01234567-89AB-CDEF-0123-456789ABCDEF}', True, "Mixed hex"),
    (r'\Device\NPF_{01234567-89AB-CDEF-0123-456789ABCDEG}', False, "Invalid G at end"),
    (r'\Device\NPF_{01234567-89AB-CDEF-0123-456789ABCDEFF}', False, "Too long (33 chars in last group)"),
    (r'\Device\NPF_{012345678-89AB-CDEF-0123-456789ABCDEF}', False, "Too long (9 chars in first group)"),
]

print("\nDetailed test results:")
all_pass = True
for test_input, expected, desc in test_cases:
    result = is_valid_npf_name(test_input)
    status = "PASS" if result == expected else "FAIL"
    if result != expected:
        all_pass = False
    print(f"{status}: {desc} - {repr(test_input)} -> {result}")

print(f"\nFinal verification: {'PASSED' if all_pass else 'FAILED'}")