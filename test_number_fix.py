#!/usr/bin/env python3
"""Test number replacement fixes"""
import re

def convert_tts_to_subtitle_format(text):
    replacements = [
        # Common number + 억 patterns - only match standalone
        (r'(?<!일|이|삼|사|오|육|칠|팔|구|십|백|천)십억', '10억'),
        (r'(?<!일|이|삼|사|오|육|칠|팔|구|십|백|천)백억', '100억'),
        (r'(?<!일|이|삼|사|오|육|칠|팔|구|십|백|천)천억', '1000억'),
        (r'(?<!일|이|삼|사|오|육|칠|팔|구|십|백|천)일조', '1조'),
    ]

    result = text
    for pattern, replacement in replacements:
        result = re.sub(pattern, replacement, result)
    return result

# Test cases for number formatting
test_cases = [
    # Standalone numbers (should change)
    ('십억', '10억', '✓ Should change - standalone'),
    ('백억', '100억', '✓ Should change - standalone'),
    ('천억', '1000억', '✓ Should change - standalone'),
    ('일조', '1조', '✓ Should change - standalone'),

    # Part of larger numbers (should NOT change)
    ('일천이백억', '일천이백억', '✓ Should NOT change - 1200억'),
    ('삼백억', '삼백억', '✓ Should NOT change - 300억'),
    ('오십억', '오십억', '✓ Should NOT change - 50억'),
    ('이천억', '이천억', '✓ Should NOT change - 2000억'),
    ('삼천오백억', '삼천오백억', '✓ Should NOT change - 3500억'),

    # In sentences (standalone should change)
    ('투자 규모는 백억 원입니다', '투자 규모는 100억 원입니다', '✓ Should change in sentence'),
    ('약 천억 정도', '약 1000억 정도', '✓ Should change in sentence'),
]

print('Testing number replacement fixes:')
print('=' * 100)
passed = 0
failed = 0
for test_input, expected, description in test_cases:
    result = convert_tts_to_subtitle_format(test_input)
    status = '✓ PASS' if result == expected else '✗ FAIL'
    if result == expected:
        passed += 1
    else:
        failed += 1
    indicator = '    ' if result == expected else ' ❌ '
    print(f'{status:8}{indicator}{test_input:30} → {result:30} | {description}')
print('=' * 100)
print(f'Results: {passed} passed, {failed} failed')
