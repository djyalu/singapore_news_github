#!/usr/bin/env python3
"""
Script to demonstrate the fix by re-processing scraped data with duplicate content
"""

import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from text_processing import TextProcessor
from datetime import datetime

def fix_article_content(content):
    """Fix duplicate sentences in article content"""
    if not content:
        return content
    
    # Extract sentences
    sentences = TextProcessor.extract_sentences(content, min_length=15)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_sentences = []
    
    for sentence in sentences:
        normalized = sentence.lower().strip()
        if normalized not in seen:
            seen.add(normalized)
            unique_sentences.append(sentence)
    
    # Merge back with safe truncation
    fixed_content = TextProcessor.merge_paragraphs(unique_sentences, max_length=1000)
    
    return fixed_content

def process_scraped_file(input_file, output_file):
    """Process a scraped news file to fix duplicate content"""
    
    print(f"Processing: {input_file}")
    
    # Load the data
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total_articles = 0
    fixed_articles = 0
    
    # Process each group
    for group in data:
        for article in group.get('articles', []):
            total_articles += 1
            
            original_content = article.get('content', '')
            if not original_content:
                continue
            
            # Fix the content
            fixed_content = fix_article_content(original_content)
            
            # Check if content was actually fixed
            if fixed_content != original_content:
                fixed_articles += 1
                print(f"\nFixed article: {article['title'][:60]}...")
                print(f"Original length: {len(original_content)}")
                print(f"Fixed length: {len(fixed_content)}")
                
                # Count duplicate sentences removed
                orig_sentences = original_content.split('. ')
                fixed_sentences = fixed_content.split('. ')
                print(f"Sentences: {len(orig_sentences)} -> {len(fixed_sentences)}")
                
                # Update the article
                article['content'] = fixed_content
                article['content_fixed'] = True
                article['fix_timestamp'] = datetime.now().isoformat()
    
    # Save the fixed data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Total articles processed: {total_articles}")
    print(f"Articles with duplicates fixed: {fixed_articles}")
    print(f"Output saved to: {output_file}")
    
    return fixed_articles > 0

def main():
    """Main function"""
    
    # Example: Fix the problematic file
    input_file = 'data/scraped/news_20250719_135747.json'
    output_file = 'data/scraped/news_20250719_135747_fixed.json'
    
    if os.path.exists(input_file):
        print("Fixing duplicate content in scraped news data...")
        print("="*60)
        
        if process_scraped_file(input_file, output_file):
            print("\nDuplicates were found and fixed!")
            
            # Show a sample of the fixed content
            with open(output_file, 'r', encoding='utf-8') as f:
                fixed_data = json.load(f)
                
            print("\nSample of fixed content:")
            print("-"*60)
            
            # Show first article's content
            if fixed_data and fixed_data[0]['articles']:
                first_article = fixed_data[0]['articles'][0]
                print(f"Title: {first_article['title']}")
                print(f"Content (first 300 chars):\n{first_article['content'][:300]}...")
        else:
            print("\nNo duplicates found - content was already clean!")
    else:
        print(f"Error: File not found: {input_file}")
        print("\nUsage: python3 fix_scraped_data.py")
        print("This will process the problematic scraped file and create a fixed version.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())