# Test: what source do I need to get a string with exactly one backslash?
source = '\\'  # This is just one backslash in source
print(f"Source: {repr(source)}")
print(f"Length: {len(source)}")
print(f"Char 0: {repr(source[0])}")

# What about two backslashes in string?
source = '\\\\'  # This is two backslashes in source
print(f"\nSource: {repr(source)}")
print(f"Length: {len(source)}")
print(f"Char 0: {repr(source[0])}")
print(f"Char 1: {repr(source[1])}")

# What about three backslashes in string?
source = '\\\\\\'  # Three backslashes in source
print(f"\nSource: {repr(source)}")
print(f"Length: {len(source)}")
print(f"Char 0: {repr(source[0])}")
print(f"Char 1: {repr(source[1])}")
print(f"Char 2: {repr(source[2])}")

# What about four backslashes in string?
source = '\\\\\\\\'  # Four backslashes in source
print(f"\nSource: {repr(source)}")
print(f"Length: {len(source)}")
print(f"Char 0: {repr(source[0])}")
print(f"Char 1: {repr(source[1])}")
print(f"Char 2: {repr(source[2])}")
print(f"Char 3: {repr(source[3])}")