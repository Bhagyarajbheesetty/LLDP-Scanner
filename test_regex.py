import re
s = '^' + '\\\\' + 'Device' + '\\\\' + 'NPF' + '_?' + '\\' + '{' + '[0-9a-fA-F]{8}' + '-' + '[0-9a-fA-F]{4}' + '-' + '[0-9a-fA-F]{4}' + '-' + '[0-9a-fA-F]{4}' + '-' + '[0-9a-fA-F]{4}' + '-' + '[0-9a-fA-F]{12}' + '\\' + '}' + '$'
print('String:', repr(s))
print('String:', s)
# Now compile the pattern
try:
    pattern = re.compile(s)
    print('Pattern compiled')
    test_str = r'\\Device\\\\NPF_{0EEA42E4-E899-4C20-BD51-C412CC78CDD8}'
    print('Test string:', repr(test_str))
    if pattern.match(test_str):
        print('Match!')
    else:
        print('No match')
except Exception as e:
    print('Error:', e)