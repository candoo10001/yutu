#!/usr/bin/env python3
"""Comprehensive test for all subtitle text replacement fixes"""
import sys
sys.path.insert(0, 'src')

from src.video_composer import VideoComposer
from src.config import Config

# Create composer instance
config = Config.from_env()
composer = VideoComposer(config)

# Comprehensive test cases covering all issues
test_cases = [
    # 원 (won) currency fixes
    ('근원', '근원', '원 in other word - should NOT change'),
    ('100원', '100₩', '100 won - should change'),
    ('만원', '만₩', '10000 won - should change'),

    # 달러 (dollar) currency fixes
    ('달러구역', '달러구역', '달러 in other word - should NOT change'),
    ('100달러', '100$', '100 dollars - should change'),

    # Number + 억 fixes
    ('일천이백억', '일천이백억', '1200억 in Korean - should NOT change'),
    ('삼백억', '삼백억', '300억 in Korean - should NOT change'),
    ('백억', '100억', 'standalone 100억 - should change'),
    ('천억', '1000억', 'standalone 1000억 - should change'),

    # 분기 (quarter) fixes
    ('일 분기', '1분기', '1st quarter - should change'),
    ('작년일분기', '작년일분기', '분기 in compound - should NOT change'),

    # Combined realistic examples
    ('테슬라의 시가총액이 일천이백억 달러를 돌파했습니다',
     '테슬라의 시가총액이 일천이백억 달러를 돌파했습니다',
     'Complex sentence with 1200억 and 달러'),

    ('투자 규모는 백억 원입니다',
     '투자 규모는 100억 원입니다',
     'Sentence with 백억 and 원 (원 preserved to avoid false positives)'),
]

print('Comprehensive Subtitle Text Replacement Test')
print('=' * 100)
passed = 0
failed = 0

for test_input, expected, description in test_cases:
    result = composer._convert_tts_to_subtitle_format(test_input)
    status = '✓ PASS' if result == expected else '✗ FAIL'

    if result == expected:
        passed += 1
    else:
        failed += 1

    print(f'{status:8} | {description:50}')
    if result != expected:
        print(f'         Input:    {test_input}')
        print(f'         Expected: {expected}')
        print(f'         Got:      {result}')
    print()

print('=' * 100)
print(f'Final Results: {passed} passed, {failed} failed')

if failed == 0:
    print('✓ ALL TESTS PASSED! Subtitle replacements are working correctly.')
else:
    print(f'✗ {failed} tests failed. Please review the output above.')
    sys.exit(1)
