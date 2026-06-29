import re

# Correct pattern for NPF name validation
pattern = r'^\\Device\\\\NPF\\_\\{[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\\\}$'
print('Pattern:', repr(pattern))

# Test cases
test_cases = [
    (r'\Device\NPF_{12345678-1234-1234-1234-123456789012}', True, "Valid NPF name"),
    (r'\Device\NPF_{0EEA42E4-E899-4C20-BD51-C412CC78CDD8}', True, "Another valid NPF name"),
    (r'\Device\NPF_{12345678-1234-1234-1234-12345678901}', False, "Too short at end (11 hex)"),
    (r'\Device\NPF_{12345678-1234-1234-1234-1234567890123}', False, "Too long at end (13 hex)"),
    (r'\Device\NPF_{12345678-1234-1234-1234-123456789012}', False, "Missing underscore"),
    (r'\Device\NPF-{12345678-1234-1234-1234-123456789012}', False, "Wrong separator"),
    (r'\Device\NPF_{12345678-1234-1234-1234-123456789012}', False, "Missing closing brace"),
    (r'Device\NPF_{12345678-1234-1234-1234-123456789012}', False, "Missing leading backslash"),
    (r'\Device\NPF_{12345678-1234-1234-1234-123456789012}extra', False, "Extra characters at end"),
]

print("\nTest results:")
all_passed = True
for test_input, expected, description in test_cases:
    # Special case for the missing underscore test
    if test_input == r'\Device\NPF_{12345678-1234-1234-1234-123456789012}' and "[missing underscore]" in description:
        test_input = r'\Device\NPF{12345678-1234-1234-1234-123456789012}'  # Remove underscore

    # Special case for wrong separator
    if test_input == r'\Device\NPF_{12345678-1234-1234-1234-123456789012}' and "[Wrong separator]" in description:
        test_input = r'\Device\NPF-{12345678-1234-1234-1234-123456789012}'  # Replace _ with -

    # Special case for missing closing brace
    if test_input == r'\Device\NPF_{12345678-1234-1234-1234-123456789012}' and "[Missing closing brace]" in description:
        test_input = r'\Device\NPF_{12345678-1234-1234-1234-123456789012'  # Remove }

    result = bool(re.match(pattern, test_input))
    status = "PASS" if result == expected else "FAIL"
    if result != expected:
        all_passed = False
    print(f"{status}: {description}")
    print(f"  Input:    {repr(test_input)}")
    print(f"  Expected: {expected}, Got: {result}")
    print()

print(f"Overall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")