import re

pattern = r'^\\Device\\\\NPF\\_\\{[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\\\}$'
print('Pattern:', repr(pattern))

# Compile with debug to see what it looks like
try:
    pat = re.compile(pattern, re.DEBUG)
except Exception as e:
    print('Error:', e)

# Test string
test_str = r'\Device\NPF_{12345678-1234-1234-1234-123456789012}'
print('Test string:', repr(test_str))

# Let's also print the string as bytes to see the backslashes
print('Test string as bytes:', test_str.encode('utf-8'))

# Now let's manually construct what we think the pattern should be
# We want to match: backslash, D, e, v, i, c, e, backslash, N, P, F, underscore, {
# then 8 hex, -, 4 hex, -, 4 hex, -, 4 hex, -, 12 hex, then }
# In regex, to match a literal backslash we need \\.
# So: \\Device\\NPF\_\{
# Then the hex groups with hyphens
# Then \} for the closing brace
# So pattern: r'^\\Device\\\\NPF\\_\\{[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\\\}$'
# That's what we have.

# Let's try a simpler approach: use re.escape on the whole static part and then insert the regex for the variable parts.
# The static parts are: \Device\NPF_{ and }
# But the {} are not static because the content changes. However, the braces themselves are static.
# So we can do: re.escape(r'\Device\NPF{') + hex pattern + re.escape('}')

static_start = r'\Device\NPF{'
static_end = '}'
escaped_start = re.escape(static_start)
escaped_end = re.escape(static_end)
print('Escaped start:', repr(escaped_start))
print('Escaped end:', repr(escaped_end))

# Now the hex pattern in between
hex_pattern = '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
pattern2 = escaped_start + hex_pattern + escaped_end
print('Pattern2:', repr(pattern2))
# Add anchors
pattern2 = '^' + pattern2 + '$'
print('Pattern2 anchored:', repr(pattern2))

pat2 = re.compile(pattern2)
print('Match test1:', bool(pat2.match(test_str)))
# Test second
test_str2 = r'\Device\NPF_{0EEA42E4-E899-4C20-BD51-C412CC78CDD8}'
print('Match test2:', bool(pat2.match(test_str2)))