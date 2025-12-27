#!/usr/bin/env python3
"""Test all replacements for potential issues"""
import re

def convert_tts_to_subtitle_format(text):
    replacements = [
        # Percentages
        (r'퍼센트', '%'),

        # Currency - only replace when it's clearly a currency unit
        (r'(\d+)\s*달러(?=\s|[,.]|$)', r'\1$'),
        (r'(\d+)\s*원(?=\s|[,.]|$)', r'\1₩'),
        (r'(억|만|천|백)\s*원(?=\s|[,.]|$)', r'\1₩'),

        # Common fractions and decimals (context-aware)
        (r'일점오', '1.5'),
        (r'이점오', '2.5'),

        # Large numbers
        (r'(\d+)\s*억', r'\1억'),
        (r'(\d+)\s*만', r'\1만'),

        # Quarter references (분기) - only at word boundaries
        (r'(?<!\S)일\s*분기', '1분기'),
        (r'(?<!\S)이\s*분기', '2분기'),
        (r'(?<!\S)삼\s*분기', '3분기'),
        (r'(?<!\S)사\s*분기', '4분기'),

        # Common number + 억 patterns
        (r'십억', '10억'),
        (r'백억', '100억'),
    ]

    result = text
    for pattern, replacement in replacements:
        result = re.sub(pattern, replacement, result)
    return result

# Comprehensive test cases
test_cases = [
    # 원 tests (should be fixed)
    ('근원', '근원', '✓ Should NOT change'),
    ('원인', '원인', '✓ Should NOT change'),
    ('병원', '병원', '✓ Should NOT change'),
    ('100원', '100₩', '✓ Should change'),
    ('만원', '만₩', '✓ Should change'),
    ('5억원', '5억₩', '✓ Should change'),

    # 달러 tests (should be fixed)
    ('달러', '달러', '✓ Should NOT change (no number)'),
    ('100달러', '100$', '✓ Should change'),
    ('달러구역', '달러구역', '✓ Should NOT change'),
    ('50달러 입니다', '50$ 입니다', '✓ Should change'),

    # 퍼센트 tests (should be OK)
    ('퍼센트', '%', '✓ Should change'),
    ('50퍼센트', '50%', '✓ Should change'),

    # 분기 tests (should be fixed)
    ('일 분기', '1분기', '✓ Should change (at start)'),
    ('일분기', '1분기', '✓ Should change'),
    ('특별한 일 분기', '특별한 1분기', '✓ Should change (after space)'),
    ('작년일분기', '작년일분기', '✓ Should NOT change (no word boundary)'),
]

print('Testing all replacement fixes:')
print('=' * 90)
passed = 0
failed = 0
for test_input, expected, description in test_cases:
    result = convert_tts_to_subtitle_format(test_input)
    status = '✓ PASS' if result == expected else '✗ FAIL'
    if result == expected:
        passed += 1
    else:
        failed += 1
    print(f'{status:8} {test_input:25} → {result:25} | {description}')
print('=' * 90)
print(f'Results: {passed} passed, {failed} failed')
