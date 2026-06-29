import re
from lldp_utils.interface import is_valid_npf_name

# Test cases
test_cases = [
    r'\Device\NPF_{12345678-1234-1234-1234-123456789012}',  # valid
    r'\Device\NPF_{0EEA42E4-E899-4C20-BD51-C412CC78CDD8}',  # invalid: last group too short
    r'\Device\NPF_{0EEA42E4-E899-4C20-BD51-C412CC78CDD8}',  # same as above
    r'\Device\NPF_{0EEA42E4-E899-4C20-BD51-C412CC78CDD89AB}', # extra chars
    r'\Device\NPF_{0EEA42E4-E899-4C20-BD51-C412CC78CDD}',   # too short
    r'\Device\NPF_{0EEA42E4-E899-4C20-BD51-C412CC78CDD8}',   # 8-4-4-4-8-4? Actually, let's count:
]

for ip in test_cases:
    print(f"Input: {repr(ip)}")
    print(f"Valid: {is_valid_npf_name(ip)}")
    print()