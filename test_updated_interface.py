from lldp_utils.interface import is_valid_npf_name

# Test cases
test_cases = [
    (r'\Device\NPF_{12345678-1234-1234-1234-123456789012}', True, "Valid NPF name"),
    (r'\Device\NPF_{0EEA42E4-E899-4C20-BD51-C412CC78CDD8}', True, "Another valid NPF name"),
    (r'\Device\NPF_{12345678-1234-1234-1234-12345678901}', False, "Too short at end (11 hex)"),
    (r'\Device\NPF_{12345678-1234-1234-1234-1234567890123}', False, "Too long at end (13 hex)"),
    (r'\Device\NPF_{12345678-1234-1234-1234-12345678901G}', False, "Invalid hex character (G)"),
    (r'\Device\NPF{12345678-1234-1234-1234-123456789012}', False, "Missing underscore"),
    (r'\Device\NPF-{12345678-1234-1234-1234-123456789012}', False, "Wrong separator (hyphen instead of underscore)"),
    (r'Device\NPF_{12345678-1234-1234-1234-123456789012}', False, "Missing leading backslash"),
    (r'\Device\NPF_{12345678-1234-1234-1234-123456789012}extra', False, "Extra characters at end"),
    (r'\Device\NPF_{12345678-1234-1234-1234-12345678901', False, "Missing closing brace"),
]

print("Testing is_valid_npf_name function:")
all_passed = True
for test_input, expected, description in test_cases:
    result = is_valid_npf_name(test_input)
    status = "PASS" if result == expected else "FAIL"
    if result != expected:
        all_passed = False
    print(f"{status}: {description}")
    print(f"  Input: {repr(test_input)}")
    print(f"  Expected: {expected}, Got: {result}")
    print()

print(f"Overall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")