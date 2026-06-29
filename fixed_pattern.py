import re

# Build pattern using re.escape on static parts INCLUDING the underscore
static_start = r'\Device\NPF_{'  # NOTE: includes the underscore
static_end = '}'                # closing brace

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

# Additional tests
test_short = r'\Device\NPF_{12345678-1234-1234-1234-12345678901}'  # 11 hex at end
print("\nTest short (11 hex):", repr(test_short))
print("Match:", bool(pat.match(test_short)))

test_long = r'\Device\NPF_{12345678-1234-1234-1234-1234567890123}'  # 13 hex at end
print("Test long (13 hex):", repr(test_long))
print("Match:", bool(pat.match(test_long)))

test_bad_chars = r'\Device\NPF_{12345678-1234-1234-1234-12345678901G}'  # G is not hex
print("Test bad char (G):", repr(test_bad_chars))
print("Match:", bool(pat.match(test_bad_chars)))

# Test that underscore is required
test_no_underscore = r'\Device\NPF{12345678-1234-1234-1234-123456789012}'  # missing underscore
print("\nTest no underscore:", repr(test_no_underscore))
print("Match:", bool(pat.match(test_no_underscore)))