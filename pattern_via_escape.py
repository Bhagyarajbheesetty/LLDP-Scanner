import re

literal = r'\Device\NPF{'
print('Literal:', repr(literal))
escaped_literal = re.escape(literal)
print('Escaped literal:', escaped_literal)

# Pattern for the hex parts with hyphens
hex_pattern = '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
print('Hex pattern:', hex_pattern)

# Closing brace
closing_brace = '}'
escaped_closing = re.escape(closing_brace)
print('Escaped closing brace:', escaped_closing)

# Combine
pattern = '^' + escaped_literal + hex_pattern + escaped_closing + '$'
print('Full pattern:', pattern)
print('Pattern repr:', repr(pattern))

# Test
test_str1 = r'\Device\NPF_{12345678-1234-1234-1234-123456789012}'
test_str2 = r'\Device\NPF_{0EEA42E4-E899-4C20-BD51-C412CC78CDD8}'

print('Test1:', repr(test_str1))
print('Test2:', repr(test_str2))

pat = re.compile(pattern)
print('Match test1:', bool(pat.match(test_str1)))
print('Match test2:', bool(pat.match(test_str2)))

# Additional tests
test_short = r'\Device\NPF_{12345678-1234-1234-1234-12345678901}'  # 11 hex
print('Test short:', repr(test_short))
print('Match short:', bool(pat.match(test_short)))

test_long = r'\Device\NPF_{12345678-1234-1234-1234-1234567890123}'  # 13 hex
print('Test long:', repr(test_long))
print('Match long:', bool(pat.match(test_long)))

# Test with lowercase letters
test_lower = r'\Device\NPF_{abcdef12-3456-7890-abcd-ef1234567890}'
print('Test lower:', repr(test_lower))
print('Match lower:', bool(pat.match(test_lower)))