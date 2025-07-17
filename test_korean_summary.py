#!/usr/bin/env python3
"""
한글 요약 테스트 스크립트
"""

import sys
import os
sys.path.append('/mnt/d/projects/singapore_news_github/scripts')

from ai_summary_free import get_free_summary

# 테스트 데이터
title = "ComfortDelGro to introduce new taxi cancellation, waiting fee policy"
content = """To help its customers ease into the changes, ComfortDelGro will implement a waiver period. PHOTO: COMFORTDELGRO. To help its customers ease into the changes, ComfortDelGro will implement a waiver period. PHOTO: COMFORTDELGRO. SINGAPORE - Singapore's largest taxi operator ComfortDelGro will introduce new cancellation and waiting fee policies from July 31. ComfortDelGro fixes commission it charges cabbies at 70 cents per ride for 3 months."""

print("=" * 50)
print("한글 요약 테스트")
print("=" * 50)

print(f"제목: {title}")
print(f"내용: {content[:100]}...")
print()

# 요약 테스트
summary = get_free_summary(title, content)

print("생성된 요약:")
print(summary)
print()
print("=" * 50)