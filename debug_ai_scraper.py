#!/usr/bin/env python3
import os
import sys
sys.path.append('scripts')

# Set a fake API key to test AI mode
os.environ['GOOGLE_GEMINI_API_KEY'] = 'fake-key-for-testing'

# Re-import to get new instance with API key
from importlib import reload
import ai_scraper as ai_module
reload(ai_module)
from ai_scraper import ai_scraper

print("=== AI Scraper Debug ===")
print(f"API Key present: {bool(ai_scraper.api_key)}")
print(f"Model initialized: {ai_scraper.model is not None}")

# Test scraping a news site
test_url = "https://www.channelnewsasia.com/singapore"
print(f"\nTesting scrape_with_ai on: {test_url}")

try:
    result = ai_scraper.scrape_with_ai(test_url)
    print(f"\nResult type: {result.get('type')}")
    
    if result['type'] == 'link_page':
        links = result.get('links', [])
        print(f"Links found: {len(links)}")
        print("\nFirst 5 links:")
        for i, link in enumerate(links[:5]):
            print(f"  {i+1}. {link}")
            
        # Test scraping the first article link
        if links:
            print(f"\nTesting first article link: {links[0]}")
            article_result = ai_scraper.scrape_with_ai(links[0])
            print(f"Article result type: {article_result.get('type')}")
            if article_result['type'] == 'article':
                print(f"Title: {article_result.get('title', 'NO TITLE')}")
                print(f"Content length: {len(article_result.get('content', ''))}")
                print(f"Extracted by: {article_result.get('extracted_by', 'unknown')}")
            
    elif result['type'] == 'error':
        print(f"Error: {result.get('error')}")
        
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()

# Test the scrape_news_ai function from scraper.py
print("\n\n=== Testing scrape_news_ai ===")
from scraper import scrape_news_ai, load_settings, load_sites

settings = load_settings()
sites = load_sites()
print(f"Number of sites: {len(sites)}")
print(f"Scrap target: {settings.get('scrapTarget')}")
print(f"Important keywords: {settings.get('importantKeywords')}")
print(f"Blocked keywords: {settings.get('blockedKeywords')}")

# Test with just one site
if sites:
    test_site = sites[0]
    print(f"\nTesting site: {test_site['name']} - {test_site['url']}")
    
    # Mock run the AI scraper logic
    site_result = ai_scraper.scrape_with_ai(test_site['url'])
    print(f"Site result type: {site_result['type']}")
    
    if site_result['type'] == 'link_page':
        links = site_result.get('links', [])
        print(f"Links found: {len(links)}")
        
        # Check if links pass the validation in scraper.py
        if links:
            print("\nChecking first link processing...")
            article_url = links[0]
            article_result = ai_scraper.scrape_with_ai(article_url)
            
            print(f"Article type: {article_result['type']}")
            print(f"Title: {article_result.get('title', 'NO TITLE')}")
            print(f"Content: {article_result.get('content', 'NO CONTENT')[:200]}...")
            
            # Check validation conditions
            has_title = bool(article_result.get('title'))
            has_content = bool(article_result.get('content'))
            content_length = len(article_result.get('content', ''))
            
            print(f"\nValidation checks:")
            print(f"Has title: {has_title}")
            print(f"Has content: {has_content}")
            print(f"Content length: {content_length} (min: 50)")
            print(f"Would pass validation: {has_title and has_content and content_length >= 50}")