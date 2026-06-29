from lldp_utils.interface import is_valid_npf_name

# Test the function directly
test_input = r'\Device\NPF_{12345678-1234-1234-1234-123456789012}'
result = is_valid_npf_name(test_input)
print(f"Input: {repr(test_input)}")
print(f"Result: {result}")

# Let's also test what the pattern looks like
import re
pattern = r'^\\Device\\\\NPF\\_\\{[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\\\}$'
print(f"Pattern: {repr(pattern)}")
compiled = re.compile(pattern)
print(f"Compiled pattern: {compiled}")
print(f"Direct match: {bool(compiled.match(test_input))}")