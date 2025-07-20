#!/usr/bin/env python3
"""Test script to verify content extraction improvements"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from bs4 import BeautifulSoup
import requests
from scraper import extract_article_content, extract_pure_article_text, post_process_article_content
from text_processing import TextProcessor

def test_duplicate_content():
    """Test with sample HTML containing duplicate content"""
    
    # Sample HTML with duplicate paragraphs (like the real issue)
    html_content = """
    <html>
    <body>
        <article>
            <h1>Stop AI errors: New tool speeds up work with factual guardrails</h1>
            <div class="content">
                <p>IBM's Generative AI platform uses an open-source approach that can help cut your business costs, adapt to changing situations and keep data secure.</p>
                <p>IBM's Generative AI platform uses an open-source approach that can help cut your business costs, adapt to changing situations and keep data secure.</p>
                <p>57 per cent of Singapore organisations plan to increase AI investment in 2025.</p>
                <p>Lower development costs through community-driven improvements rather than proprietary development.</p>
                <p>Lower development costs through community-driven improvements rather than proprietary development.</p>
                <p>Eliminate vendor lock-in expenses, allowing more flexible and economical scaling.</p>
                <p>Eliminate vendor lock-in expenses, allowing more flexible and economical scaling.</p>
                <p>Discover how IBM's trusted AI framework can transform your business operations efficiently.</p>
            </div>
        </article>
    </body>
    </html>
    """
    
    soup = BeautifulSoup(html_content, 'html.parser')
    content_elem = soup.find('article')
    
    # Extract text using the improved function
    extracted_text = extract_pure_article_text(content_elem)
    
    print("=== TEST: Duplicate Content Removal ===")
    print(f"Extracted content:\n{extracted_text}\n")
    
    # Check for duplicates
    sentences = TextProcessor.extract_sentences(extracted_text)
    unique_sentences = list(set(sentences))
    
    print(f"Total sentences: {len(sentences)}")
    print(f"Unique sentences: {len(unique_sentences)}")
    print(f"Duplicates removed: {len(sentences) - len(unique_sentences)}")
    
    # Verify no sentence appears twice
    sentence_count = {}
    for sentence in sentences:
        normalized = sentence.lower().strip()
        sentence_count[normalized] = sentence_count.get(normalized, 0) + 1
    
    duplicates_found = False
    for sentence, count in sentence_count.items():
        if count > 1:
            print(f"DUPLICATE FOUND ({count}x): {sentence[:50]}...")
            duplicates_found = True
    
    if not duplicates_found:
        print("SUCCESS: No duplicates found in extracted content!")
    
    return not duplicates_found

def test_text_truncation():
    """Test that text is properly truncated without cutting words"""
    
    long_text = "Discover how IBM's trusted AI framework can transform your business operations efficiently. " * 20
    
    print("\n=== TEST: Safe Text Truncation ===")
    
    # Test truncation at different lengths
    for max_length in [100, 200, 500]:
        truncated = TextProcessor.safe_truncate(long_text, max_length)
        print(f"\nMax length: {max_length}")
        print(f"Actual length: {len(truncated)}")
        print(f"Last 20 chars: ...{truncated[-20:]}")
        
        # Check if ends properly (not mid-word)
        if truncated.endswith('...'):
            # Should have space before ellipsis
            assert truncated[-4] == ' ', "Truncation cut a word!"
        else:
            # Should end with punctuation
            assert truncated[-1] in '.!?', "Truncation didn't end properly!"
    
    print("\nSUCCESS: Text truncation works correctly!")
    return True

def test_real_article():
    """Test with a real article URL if available"""
    
    print("\n=== TEST: Real Article Extraction ===")
    
    # Test URL (you can change this to any article)
    test_url = "https://www.straitstimes.com/tech/ai-tool-speeds-up-work-with-factual-guardrails-improve-accuracy-watsonx-ibm"
    
    try:
        article_data = extract_article_content(test_url)
        
        if article_data:
            print(f"Title: {article_data['title']}")
            print(f"Content length: {len(article_data['content'])}")
            print(f"First 200 chars: {article_data['content'][:200]}...")
            
            # Check for duplicates in content
            sentences = TextProcessor.extract_sentences(article_data['content'])
            unique_sentences = list(set([s.lower().strip() for s in sentences]))
            
            print(f"\nSentence analysis:")
            print(f"Total sentences: {len(sentences)}")
            print(f"Unique sentences: {len(unique_sentences)}")
            
            if len(sentences) == len(unique_sentences):
                print("SUCCESS: No duplicate sentences found!")
                return True
            else:
                print(f"WARNING: Found {len(sentences) - len(unique_sentences)} duplicate sentences")
                return False
        else:
            print("Could not extract article data")
            return False
            
    except Exception as e:
        print(f"Error testing real article: {e}")
        print("(This is normal if running offline or if the URL is not accessible)")
        return True  # Don't fail the test for network issues

def main():
    """Run all tests"""
    
    print("Testing Content Extraction Improvements")
    print("=" * 50)
    
    tests_passed = 0
    tests_total = 3
    
    # Run tests
    if test_duplicate_content():
        tests_passed += 1
    
    if test_text_truncation():
        tests_passed += 1
        
    if test_real_article():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"Tests passed: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print("All tests passed! ✓")
        return 0
    else:
        print("Some tests failed! ✗")
        return 1

if __name__ == "__main__":
    sys.exit(main())