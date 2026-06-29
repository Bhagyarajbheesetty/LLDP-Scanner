import re

example2 = r'\Device\NPF_{12345678-1234-1234-1234-123456789012}'
escaped2 = re.escape(example2)
print('Escaped example2:', escaped2)
parts = escaped2.split('\\-')
print('Parts:', parts)
# Replace each part
parts[0] = parts[0].replace('12345678', '[0-9a-fA-F]{8}')
parts[1] = parts[1].replace('1234', '[0-9a-fA-F]{4}')
parts[2] = parts[2].replace('1234', '[0-9a-fA-F]{4}')
parts[3] = parts[3].replace('1234', '[0-9a-fA-F]{4}')
parts[4] = parts[4].replace('123456789012', '[0-9a-fA-F]{12}')
pattern = '\\-'.join(parts)
print('Pattern after replacement:', pattern)
# Make underscore optional: replace '\_' with '_?'
pattern = pattern.replace('\\_', '_?')
print('Pattern after underscore optional:', pattern)
# Add anchors
pattern = '^' + pattern + '$'
print('Pattern with anchors:', pattern)
# Now test
test_str1 = r'\Device\NPF_{12345678-1234-1234-1234-123456789012}'
test_str2 = r'\Device\NPF_{0EEA42E4-E899-4C20-BD51-C412CC78CDD8}'
print('Test string 1:', repr(test_str1))
print('Test string 2:', repr(test_str2))
pat = re.compile(pattern)
print('Does pattern match test_str1?', bool(pat.match(test_str1)))
print('Does pattern match test_str2?', bool(pat.match(test_str2)))
print('Pattern repr:', repr(pattern))