#!/usr/bin/env python3
import os
import sys
sys.path.append('scripts')

# Ensure no API key
if 'GOOGLE_GEMINI_API_KEY' in os.environ:
    del os.environ['GOOGLE_GEMINI_API_KEY']

# Import fresh
from importlib import reload
import ai_scraper as ai_module
reload(ai_module)
from ai_scraper import ai_scraper

print("=== Testing Fallback Mode (No AI) ===")
print(f"API Key present: {bool(ai_scraper.api_key)}")
print(f"Model initialized: {ai_scraper.model is not None}")

# Test scraping
test_url = "https://www.channelnewsasia.com/singapore"
print(f"\nTesting scrape_with_ai on: {test_url}")

try:
    result = ai_scraper.scrape_with_ai(test_url)
    print(f"\nResult type: {result.get('type')}")
    
    if result['type'] == 'link_page':
        links = result.get('links', [])
        print(f"Links found: {len(links)}")
        print("\nFirst 10 links:")
        for i, link in enumerate(links[:10]):
            print(f"  {i+1}. {link}")
            
        # Check what the fallback validation accepts
        print("\n\nChecking fallback URL validation patterns:")
        test_urls = [
            "https://www.channelnewsasia.com/singapore/news-article-test",
            "https://www.channelnewsasia.com/2024/12/25/test-article",
            "https://www.channelnewsasia.com/singapore",
            "https://www.channelnewsasia.com/search",
            "https://www.channelnewsasia.com/newsletters"
        ]
        
        for url in test_urls:
            valid = ai_scraper._fallback_url_validation(url)
            print(f"  {url} -> {valid}")
            
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()

# Now test the main scraper
print("\n\n=== Testing Main Scraper ===")
from scraper import scrape_news

result_file = scrape_news()
print(f"Result file: {result_file}")

# Check the result
import json
with open(result_file, 'r') as f:
    data = json.load(f)
    print(f"Number of groups: {len(data)}")
    total_articles = sum(len(group.get('articles', [])) for group in data)
    print(f"Total articles: {total_articles}")
    
    if data and data[0].get('articles'):
        print(f"\nFirst article:")
        article = data[0]['articles'][0]
        print(f"  Title: {article.get('title', 'NO TITLE')}")
        print(f"  URL: {article.get('url', 'NO URL')}")
        print(f"  Content length: {len(article.get('content', ''))}")