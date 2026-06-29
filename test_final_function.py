import re

def is_valid_npf_name(npname: str) -> bool:
    """
    Validate that the NPF name matches the expected pattern:
    \Device\NPF_{xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx}
    where x is a hexadecimal digit.
    """
    pattern = r'^\\Device\\\\NPF\\_\\{[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\\\}$'
    return bool(re.match(pattern, npname))

# Test it
test_cases = [
    (r'\Device\NPF_{12345678-1234-1234-1234-123456789012}', True),
    (r'\Device\NPF_{0EEA42E4-E899-4C20-BD51-C412CC78CDD8}', True),
    (r'\Device\NPF_{12345678-1234-1234-1234-12345678901}', False),
    (r'\Device\NPF_{12345678-1234-1234-1234-1234567890123}', False),
    (r'\Device\NPF_{12345678-1234-1234-1234-12345678901G}', False),
    (r'\Device\NPF{12345678-1234-1234-1234-123456789012}', False),  # missing underscore
]

print("Testing the function:")
all_pass = True
for test_input, expected in test_cases:
    result = is_valid_npf_name(test_input)
    status = "PASS" if result == expected else "FAIL"
    if result != expected:
        all_pass = False
    print(f"{status}: {repr(test_input)} -> {result} (expected {expected})")

print(f"\nOverall: {'ALL TESTS PASSED' if all_pass else 'SOME TESTS FAILED'}")