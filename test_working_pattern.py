# Let's test the exact pattern from fixed_pattern.py that we know worked

# From fixed_pattern.py, this is what we had:
pattern_from_working_test = r'^\\Device\\\\NPF\\_\\{[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\\\}$'
print("Pattern from working test:", repr(pattern_from_working_test))

# This should be the string that gets passed to re.compile
print("Pattern string (what re.compile sees):", repr(pattern_from_working_test))

# Test it
import re
test_str = r'\Device\NPF_{12345678-1234-1234-1234-123456789012}'
compiled = re.compile(pattern_from_working_test)
result = bool(compiled.match(test_str))
print(f"Test string: {repr(test_str)}")
print(f"Match result: {result}")

# Now, what source code do we need to produce this exact string?
# Since pattern_from_working_test is already a raw string literal,
# the source code to produce it is exactly what we see between the r'...'
# So the source should be: ^\\Device\\\\NPF\\_\\{[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\\\}$

# Let's verify by creating it explicitly
pattern_source = r'^\\Device\\\\NPF\\_\\{[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\\\}$'
print("\nExplicitly created pattern source:", repr(pattern_source))
print("Matches working test?", pattern_source == pattern_from_working_test)

# Test the explicitly created one
compiled2 = re.compile(pattern_source)
result2 = bool(compiled2.match(test_str))
print(f"Explicit pattern match result: {result2}")