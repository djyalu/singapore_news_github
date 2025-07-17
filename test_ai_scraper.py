#!/usr/bin/env python3
import os
import sys
sys.path.append('scripts')

from ai_scraper import ai_scraper

# Test environment
print("=== AI Scraper Test ===")
print(f"API Key present: {bool(ai_scraper.api_key)}")
print(f"API Key length: {len(ai_scraper.api_key) if ai_scraper.api_key else 0}")
print(f"Model initialized: {ai_scraper.model is not None}")

# Test URL validation
test_url = "https://www.channelnewsasia.com/singapore/singapore-news-test-article-123456"
print(f"\nTesting URL validation for: {test_url}")

# Test with fallback (no AI)
result = ai_scraper._fallback_url_validation(test_url)
print(f"Fallback validation result: {result}")

# Test obvious article URL
obvious_result = ai_scraper._is_obvious_article_url(test_url)
print(f"Obvious article URL: {obvious_result}")

# Test scraping
print(f"\nTesting scrape_with_ai...")
try:
    scrape_result = ai_scraper.scrape_with_ai("https://www.channelnewsasia.com/singapore")
    print(f"Scrape result type: {scrape_result.get('type')}")
    if scrape_result['type'] == 'link_page':
        print(f"Links found: {len(scrape_result.get('links', []))}")
        for i, link in enumerate(scrape_result.get('links', [])[:5]):
            print(f"  {i+1}. {link}")
    elif scrape_result['type'] == 'error':
        print(f"Error: {scrape_result.get('error')}")
except Exception as e:
    print(f"Exception during scraping: {e}")
    import traceback
    traceback.print_exc()