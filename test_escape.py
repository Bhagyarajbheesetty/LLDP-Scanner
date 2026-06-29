import re

# Test re.escape on a string containing backslashes
test_str = r'\Device\NPF{'
print('Test string:', repr(test_str))
escaped = re.escape(test_str)
print('Escaped:', repr(escaped))
# Now compile and see if it matches the original string
pattern = re.compile(escaped)
print('Does escaped pattern match original string?', bool(pattern.match(test_str)))
# Also test that it doesn't match if we change something
print('Does it match "\\\\Device\\\\NPF{"?', bool(pattern.match('\\\\Device\\\\NF{')))