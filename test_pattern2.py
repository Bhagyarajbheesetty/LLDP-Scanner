import re

# Let's build the pattern step by step
# We want to match: \Device\NPF_{xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx}
# where each x is hex digit.

# Literal parts:
# \Device\NPF\{
# In regex, to match a literal backslash we need \\.
# So: \\Device\\NPF\\{
# But the { is a literal curly brace, so we need to escape it: \{
# Thus: \\Device\\NPF\\\\{  Wait, let's think.

# Actually, we want the regex pattern to contain the characters: backslash, D, e, v, i, c, e, backslash, N, P, F, backslash, {
# So the pattern string (what we pass to re.compile) should have:
# For each literal backslash in the input, we need two backslashes in the pattern string.
# So for the first backslash: we need \\ in the pattern string.
# Then the letters D e v i c e.
# Then another backslash: need \\ in the pattern string.
# Then N P F.
# Then another backslash: need \\ in the pattern string.
# Then a literal curly brace: in regex, to match a literal { we need \{ (because { is special). So we need to put \{ in the pattern string.
# To get \{ in the pattern string, we need to escape the backslash: so we write \\{ (two backslashes then a brace).

# So far: r'\\Device\\\\NPF\\\\\\{'? This is getting messy.

# Let's instead use re.escape on the literal part and then add the regex for the variable part.
literal = r'\Device\NPF{'
escaped_literal = re.escape(literal)
print('Escaped literal:', escaped_literal)
# Now we want to replace the placeholder hex digits with patterns.
# But we don't have placeholders. Instead, we can build the pattern as:
# escaped_literal + '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}' + '\\}'
# But note: the escaped_literal already includes the escaping for the backslashes and the curly brace.
# Let's see what escaped_literal looks like.

# Actually, let's just write the pattern as a raw string and test.
pattern = r'^\\Device\\\\NPF\\\\\{[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\\\\}$'
print('Pattern:', pattern)
print('Pattern repr:', repr(pattern))

# Now compile and test
pat = re.compile(pattern)
test1 = r'\Device\NPF_{12345678-1234-1234-1234-123456789012}'
test2 = r'\Device\NPF_{0EEA42E4-E899-4C20-BD51-C412CC78CDD8}'
print('Test1:', repr(test1), '->', bool(pat.match(test1)))
print('Test2:', repr(test2), '->', bool(pat.match(test2)))