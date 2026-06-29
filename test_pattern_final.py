import re

literal = r'\Device\NPF{'
escaped_literal = re.escape(literal)
print('Escaped literal:', repr(escaped_literal))

# Now build pattern
pattern = escaped_literal + '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}' + '\\}'
print('Pattern:', repr(pattern))

# Test
test_str1 = r'\Device\NPF_{12345678-1234-1234-1234-123456789012}'
test_str2 = r'\Device\NPF_{0EEA42E4-E899-4C20-BD51-C412CC78CDD8}'

print('Test1:', repr(test_str1))
print('Test2:', repr(test_str2))

pat = re.compile(pattern)
print('Match test1:', bool(pat.match(test_str1)))
print('Match test2:', bool(pat.match(test_str2)))

# Add anchors
pattern_anchored = '^' + pattern + '$'
print('Pattern anchored:', repr(pattern_anchored))
pat2 = re.compile(pattern_anchored)
print('Match test1 anchored:', bool(pat2.match(test_str1)))
print('Match test2 anchored:', bool(pat2.match(test_str2)))