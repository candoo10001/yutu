#!/usr/bin/env python3
"""Test the 원 currency replacement fix"""
import re

def convert_tts_to_subtitle_format(text):
    replacements = [
        (r'퍼센트', '%'),
        (r'달러', '$'),
        (r'(\d+)\s*원(?=\s|[,.]|$)', r'\1₩'),  # 100원, 천원 etc (after numbers)
        (r'(억|만|천|백)\s*원(?=\s|[,.]|$)', r'\1₩'),  # 억원, 만원, 천원 (after number words)
    ]

    result = text
    for pattern, replacement in replacements:
        result = re.sub(pattern, replacement, result)
    return result

# Test cases
test_cases = [
    '근원',  # Should stay as is
    '원인',  # Should stay as is
    '병원',  # Should stay as is
    '100원',  # Should become 100₩
    '만원',  # Should become 만₩
    '천원',  # Should become 천₩
    '100원입니다',  # Should stay (no space/punctuation after)
    '100원 입니다',  # Should become 100₩ 입니다
    '근원적인',  # Should stay as is
    '5억원',  # Should become 5억₩
    '1만원',  # Should become 1만₩
]

print('Testing 원 replacement fix:')
print('=' * 70)
for test in test_cases:
    result = convert_tts_to_subtitle_format(test)
    changed = '✓ CHANGED' if test != result else '  (unchanged)'
    print(f'{test:20} → {result:20} {changed}')
print('=' * 70)
