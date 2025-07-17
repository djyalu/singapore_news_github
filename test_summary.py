import os
import sys
sys.path.append('/mnt/d/projects/singapore_news_github')

# Check if Gemini API key is available
api_key = os.environ.get('GOOGLE_GEMINI_API_KEY')
print(f"GOOGLE_GEMINI_API_KEY is set: {bool(api_key)}")

# Test the create_summary function directly
from scripts.scraper import create_summary

test_article = {
    'title': 'Singapore government announces new housing policy',
    'content': 'The Singapore government today announced a new policy aimed at making housing more affordable for young families. The policy includes increased grants and subsidies that will help first-time buyers purchase HDB flats. Minister Lawrence Wong said this initiative will benefit over 100,000 families in the next five years.'
}

settings = {
    'scrapTarget': 'all',
    'blockedKeywords': '',
    'importantKeywords': ''
}

print("\nTesting create_summary function:")
result = create_summary(test_article, settings)
print(f"Result:\n{result}")

# Test keyword summary directly
from scripts.scraper import create_keyword_summary
print("\n\nTesting create_keyword_summary function:")
keyword_result = create_keyword_summary(test_article['title'], test_article['content'])
print(f"Result:\n{keyword_result}")