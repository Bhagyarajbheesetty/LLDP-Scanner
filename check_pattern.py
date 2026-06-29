with open(r'C:\Users\Bbheesetty\LLDP Scanner\lldp_utils\interface.py', 'r') as f:
    lines = f.readlines()

line19 = lines[18]  # 0-indexed, so line 19 is index 18
print("Line 19 raw:", repr(line19))
print("Line 19:", line19.rstrip())

# Also let's check the pattern by extracting it
import ast
# Find the line that contains the pattern assignment
for i, line in enumerate(lines):
    if 'pattern =' in line and 'r' in line and '^' in line:
        print(f"Line {i+1}: {repr(line.rstrip())}")
        # Try to evaluate the pattern string
        try:
            # Extract the string literal
            start = line.index("r'")
            end = line.rindex("'")
            pattern_str = line[start+2:end]  # Skip the r'
            print(f"  Pattern string: {repr(pattern_str)}")
            print(f"  Pattern string length: {len(pattern_str)}")
            # Show first few and last few chars
            print(f"  First 20 chars: {repr(pattern_str[:20])}")
            print(f"  Last 20 chars: {repr(pattern_str[-20:])}")
        except Exception as e:
            print(f"  Error extracting pattern: {e}")
        break