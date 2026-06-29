import re

def debug_is_valid_npf_name(npname: str) -> bool:
    """
    Debug version of is_valid_npf_name to see what pattern is being used.
    """
    pattern = r'^\\Device\\\\NPF\\_\\{[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\\\}$'
    print(f"Pattern: {repr(pattern)}")
    print(f"Input: {repr(npname)}")
    result = bool(re.match(pattern, npname))
    print(f"Match result: {result}")
    return result

# Test with a known good value
test_input = r'\Device\NPF_{12345678-1234-1234-1234-123456789012}'
print("Testing debug function:")
debug_is_valid_npf_name(test_input)