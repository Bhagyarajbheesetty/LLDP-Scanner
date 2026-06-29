import re
s = r'\Device\NPF_\{[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\\}'
print('String:', repr(s))
print('String:', s)
try:
    pattern = re.compile(s)
    print('Pattern compiled')
    test_str = r'\Device\NPF_{12345678-1234-1234-1234-123456789012}'
    print('Test string:', repr(test_str))
    if pattern.match(test_str):
        print('Match!')
    else:
        print('No match')
except Exception as e:
    print('Error:', e)
