import re
example2 = r'\Device\NPF_{12345678-1234-1234-1234-123456789012}'
escaped2 = re.escape(example2)
parts = escaped2.split('\\-')
parts[0] = parts[0].replace('12345678', '[0-9a-fA-F]{8}')
parts[1] = parts[1].replace('1234', '[0-9a-fA-F]{4}')
parts[2] = parts[2].replace('1234', '[0-9a-fA-F]{4}')
parts[3] = parts[3].replace('1234', '[0-9a-fA-F]{4}')
parts[4] = parts[4].replace('123456789012', '[0-9a-fA-F]{12}')
pattern = '\\-'.join(parts)
pattern = pattern.replace('\\_', '_?')
print('Pattern:', pattern)
try:
    pat = re.compile(pattern)
    print('Pattern compiled')
    # Test with correct hex lengths
    test_str1 = r'\Device\NPF_{12345678-1234-1234-1234-123456789012}'
    print('Test string 1 (correct):', repr(test_str1))
    if pat.match(test_str1):
        print('Match! (correct)')
    else:
        print('No match (unexpected)')
    # Test with original example (incorrect hex lengths)
    test_str2 = r'\Device\NPF_{0EEA42E4-E899-4C20-BD51-C412CC78CDD8}'
    print('Test string 2 (original):', repr(test_str2))
    if pat.match(test_str2):
        print('Match! (unexpected)')
    else:
        print('No match (expected)')
except Exception as e:
    print('Error:', e)