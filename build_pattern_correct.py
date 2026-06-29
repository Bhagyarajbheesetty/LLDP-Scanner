import re

# Build pattern using re.escape on static parts
static_start = r'\Device\NPF{'  # This is what we want to match literally
static_end = '}'                # This is what we want to match literally

print("Static start:", repr(static_start))
print("Static end:", repr(static_end))

escaped_start = re.escape(static_start)
escaped_end = re.escape(static_end)

print("Escaped start:", repr(escaped_start))
print("Escaped end:", repr(escaped_end))

# The variable part in the middle: 8 hex, -, 4 hex, -, 4 hex, -, 4 hex, -, 12 hex
hex_pattern = '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'

# Combine: escaped_start + hex_pattern + escaped_end
pattern_without_anchors = escaped_start + hex_pattern + escaped_end
print("Pattern without anchors:", repr(pattern_without_anchors))

# Add anchors
pattern = '^' + pattern_without_anchors + '$'
print("Final pattern:", repr(pattern))

# Test
test_str1 = r'\Device\NPF_{12345678-1234-1234-1234-123456789012}'
test_str2 = r'\Device\NPF_{0EEA42E4-E899-4C20-BD51-C412CC78CDD8}'

print("\nTest strings:")
print("Test 1:", repr(test_str1))
print("Test 2:", repr(test_str2))

# Compile and test
pat = re.compile(pattern)
print("\nMatch results:")
print("Test 1 match:", bool(pat.match(test_str1)))
print("Test 2 match:", bool(pat.match(test_str2)))

# Let's also verify what the pattern looks like
print("\nPattern breakdown:")
print("Start anchor: ^")
print("Escaped start (should match \\Device\\NPF{):", repr(escaped_start))
print("Hex pattern:", hex_pattern)
print("Escaped end (should match }):", repr(escaped_end))
print("End anchor: $")