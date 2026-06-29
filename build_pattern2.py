import re

# Build pattern step by step
parts = []
parts.append('^')
parts.append('\\\\')  # backslash
parts.append('Device')
parts.append('\\\\')  # backslash
parts.append('NPF')
parts.append('_')     # underscore
parts.append('\\\\')  # backslash for escaping {
parts.append('{')
parts.append('[0-9a-fA-F]{8}')
parts.append('-')
parts.append('[0-9a-fA-F]{4}')
parts.append('-')
parts.append('[0-9a-fA-F]{4}')
parts.append('-')
parts.append('[0-9a-fA-F]{4}')
parts.append('-')
parts.append('[0-9a-fA-F]{12}')
parts.append('\\\\')  # backslash for escaping }
parts.append('}')
parts.append('$')

pattern = ''.join(parts)
print('Pattern:', repr(pattern))

# Test
test_str1 = r'\Device\NPF_{12345678-1234-1234-1234-123456789012}'
test_str2 = r'\Device\NPF_{0EEA42E4-E899-4C20-BD51-C412CC78CDD8}'

print('Test1:', repr(test_str1))
print('Test2:', repr(test_str2))

pat = re.compile(pattern)
print('Match test1:', bool(pat.match(test_str1)))
print('Match test2:', bool(pat.match(test_str2)))

# Also test a few more
test_short = r'\Device\NPF_{12345678-1234-1234-1234-12345678901}'  # 11 hex at end
print('Test short:', repr(test_short))
print('Match short:', bool(pat.match(test_short)))

test_long = r'\Device\NPF_{12345678-1234-1234-1234-1234567890123}'  # 13 hex at end
print('Test long:', repr(test_long))
print('Match long:', bool(pat.match(test_long)))

# Let's also print what the pattern looks like when printed
print('Pattern string:')
print(pattern)