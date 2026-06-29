import re

# Correct pattern with underscore
pattern = r'^\\Device\\\\NPF\\_\\{[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\\\}$'
print('Pattern:', repr(pattern))

test_str1 = r'\Device\NPF_{12345678-1234-1234-1234-123456789012}'
test_str2 = r'\Device\NPF_{0EEA42E4-E899-4C20-BD51-C412CC78CDD8}'

print('Test1:', repr(test_str1))
print('Test2:', repr(test_str2))

pat = re.compile(pattern)
print('Match test1:', bool(pat.match(test_str1)))
print('Match test2:', bool(pat.match(test_str2)))

# Also test that the underscore is required
test_no_underscore = r'\Device\NPF_{12345678-1234-1234-1234-123456789012}'  # actually has underscore? Wait, this string has underscore? Let's see: \Device\NPF_{...} -> there is an underscore between NPF and {. So to test without underscore we need to remove it.
test_no_underscore = r'\Device\NPF{12345678-1234-1234-1234-123456789012}'  # missing underscore
print('Test no underscore:', repr(test_no_underscore))
print('Match no underscore:', bool(pat.match(test_no_underscore)))