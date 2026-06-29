import re
example2 = r'\Device\NPF_{12345678-1234-1234-1234-123456789012}'
escaped2 = re.escape(example2)
print('Escaped example2:', escaped2)
# Split by escaped hyphen
parts = escaped2.split('\\-')
print('Parts:', parts)
# Replace each part
parts[0] = parts[0].replace('12345678', '[0-9a-fA-F]{8}')
parts[1] = parts[1].replace('1234', '[0-9a-fA-F]{4}')
parts[2] = parts[2].replace('1234', '[0-9a-fA-F]{4}')
parts[3] = parts[3].replace('1234', '[0-9a-fA-F]{4}')
parts[4] = parts[4].replace('123456789012', '[0-9a-fA-F]{12}')
# Join back with escaped hyphen
pattern = '\\-'.join(parts)
print('Pattern after replacement:', pattern)
# Make underscore optional: replace '\_' with '_?'
pattern = pattern.replace('\\_', '_?')
print('Pattern after making underscore optional:', pattern)
# Compile and test
try:
    pat = re.compile(pattern)
    print('Pattern compiled')
    test_str = r'\Device\NPF_{12345678-1234-1234-1234-123456789012}'
    print('Test string:', repr(test_str))
    if pat.match(test_str):
        print('Match!')
    else:
        print('No match')
except Exception as e:
    print('Error:', e)