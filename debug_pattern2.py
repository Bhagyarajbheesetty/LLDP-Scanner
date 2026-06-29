import re
pattern = r'^\\Device\\NPF_\{[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\}$'
print('Pattern:', repr(pattern))
test_str1 = r'\Device\NPF_{12345678-1234-1234-1234-123456789012}'
test_str2 = r'\Device\NPF_{0EEA42E4-E899-4C20-BD51-C412CC78CDD8}'
print('Test1:', repr(test_str1))
print('Test2:', repr(test_str2))
print('Length test1:', len(test_str1))
print('Length test2:', len(test_str2))
prefix = r'\Device\NPF{'
print('Prefix repr:', repr(prefix))
print('Test2 starts with prefix?', test_str2.startswith(prefix))
print('Test2 first 12 chars:', repr(test_str2[:12]))
print('Prefix first 12 chars:', repr(prefix[:12]))
# Let's break down test_str2
print('Breaking test_str2:')
# Remove the prefix and suffix manually
if test_str2.startswith('\\Device\\NPF{') and test_str2.endswith('}'):
    print('Starts and ends correctly')
    inner = test_str2[len('\\Device\\NPF{'):-1]
    print('Inside braces:', repr(inner))
    parts = inner.split('-')
    print('Parts:', parts)
    print('Lengths:', [len(p) for p in parts])
else:
    print('Does not start/end as expected')
    print('First 20 chars of test_str2:', repr(test_str2[:20]))
    print('Last 5 chars:', repr(test_str2[-5:]))
pat = re.compile(pattern)
print('Match test1:', bool(pat.match(test_str1)))
print('Match test2:', bool(pat.match(test_str2)))