import re

# Simple test: does re.escape work for matching a literal backslash string?
simple_test = r'\Device\NPF{'
print("Simple test string:", repr(simple_test))

escaped_simple = re.escape(simple_test)
print("Escaped:", repr(escaped_simple))

# Compile the escaped pattern
pattern_simple = re.compile(escaped_simple)
print("Does escaped pattern match original?", bool(pattern_simple.match(simple_test)))

# Now let's build the full pattern step by step and debug what's happening
static_start = r'\Device\NPF{'
static_end = '}'

print("\n--- Building the full pattern ---")
print("Static start:", repr(static_start))
print("Static end:", repr(static_end))

escaped_start = re.escape(static_start)
escaped_end = re.escape(static_end)

print("Escaped start:", repr(escaped_start))
print("Escaped end:", repr(escaped_end))

# Let's verify these work individually
print("\n--- Testing components ---")
print("Does escaped start match static start?", bool(re.compile(escaped_start).match(static_start)))
print("Does escaped end match static end?", bool(re.compile(escaped_end).match(static_end)))

# Now the middle part
hex_part = '12345678-1234-1234-1234-123456789012'
hex_pattern = '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'

print("\nHex part to match:", repr(hex_part))
print("Hex pattern:", repr(hex_pattern))
print("Does hex pattern match hex part?", bool(re.compile(hex_pattern).fullmatch(hex_part)))

# Now combine
combined = escaped_start + hex_pattern + escaped_end
print("\nCombined (no anchors):", repr(combined))

# Test the combined pattern on the full string without braces
full_string_without_braces = static_start + hex_part + static_end
print("Full string without extra braces:", repr(full_string_without_braces))
print("Does combined pattern match full string?", bool(re.compile(combined).match(full_string_without_braces)))

# Now add anchors
final_pattern = '^' + combined + '$'
print("\nFinal pattern:", repr(final_pattern))
print("Does final pattern match full string?", bool(re.compile(final_pattern).match(full_string_without_braces)))

# Test with the actual test strings
print("\n--- Testing with actual test strings ---")
test1 = r'\Device\NPF_{12345678-1234-1234-1234-123456789012}'
test2 = r'\Device\NPF_{0EEA42E4-E899-4C20-BD51-C412CC78CDD8}'

print("Test 1:", repr(test1))
print("Test 2:", repr(test2))

print("Test 1 matches:", bool(re.compile(final_pattern).match(test1)))
print("Test 2 matches:", bool(re.compile(final_pattern).match(test2)))

# Let's also check what the actual difference is by looking at the strings character by character
print("\n--- Character-by-character analysis ---")
print("Test 1 chars:")
for i, c in enumerate(test1):
    print(f"  [{i:2}] {repr(c)} (ord={ord(c)})")

print("\nWhat the pattern expects:")
# Let's manually construct what the pattern should match
expected = ''
expected += chr(92)  # \
expected += 'Device'
expected += chr(92)  # \
expected += 'NPF'
expected += '_'
expected += chr(123) # {
expected += '12345678'
expected += '-'
expected += '1234'
expected += '-'
expected += '1234'
expected += '-'
expected += '1234'
expected += '-'
expected += '123456789012'
expected += chr(125) # }
print("Expected:", repr(expected))
print("Match?", test1 == expected)