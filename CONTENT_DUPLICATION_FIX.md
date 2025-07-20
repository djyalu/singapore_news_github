# Content Duplication Fix for Singapore News Scraper

## Problem Identified

The scraper was producing articles with:
1. **Duplicate sentences** - Same sentences appearing 2-5 times in the content
2. **Text truncation** - Content being cut off mid-word (e.g., "busines" instead of "business")

### Example of the issue:
```
"IBM's Generative AI platform uses an open-source approach..." (appears 2 times)
"Among the low-cost airlines that have flown into..." (appears 5 times)
"Discover how IBM's trusted AI framework can transform your busines" (truncated)
```

## Root Cause

The `extract_pure_article_text` function in `scraper.py` was:
1. Extracting text from both `<p>` and `<div>` elements, causing duplicates when divs contained the same paragraphs
2. Using simple string slicing `[:1000]` which could cut words in half
3. Not deduplicating sentences within the same article

## Solution Implemented

### 1. Modified `scraper.py` to:
- Import the existing `TextProcessor` and `ArticleDeduplicator` modules
- Extract sentences individually and deduplicate them
- Use `TextProcessor.merge_paragraphs()` for safe text truncation
- Prioritize `<p>` tags over `<div>` tags to avoid duplicate extraction

### 2. Key changes in `extract_pure_article_text()`:
```python
# Extract paragraphs - p tags first, div only if no p tags
paragraphs = content_elem.find_all('p')
if not paragraphs:
    paragraphs = content_elem.find_all('div')

# Collect sentences and remove duplicates
all_sentences = []
seen_sentences = set()

for p in paragraphs:
    text = clean_text(p.get_text())
    
    # Extract sentences
    sentences = TextProcessor.extract_sentences(text)
    
    for sentence in sentences:
        # Normalize for duplicate check
        normalized = sentence.lower().strip()
        if normalized not in seen_sentences and len(sentence) > 20:
            seen_sentences.add(normalized)
            all_sentences.append(sentence)

# Merge with safe truncation
merged_content = TextProcessor.merge_paragraphs(all_sentences, max_length=1000)
```

### 3. Improved `post_process_article_content()`:
- Uses `TextProcessor.extract_sentences()` for clean sentence extraction
- Implements proper deduplication with normalized comparison
- Uses `TextProcessor.merge_paragraphs()` for safe content merging

### 4. Fixed `TextProcessor.safe_truncate()`:
- Ensures text ends at sentence boundaries when possible
- Falls back to word boundaries to avoid mid-word cuts
- Always ends with proper punctuation or ellipsis

## Testing

Created comprehensive tests in `test_content_extraction.py`:
1. **Duplicate Content Test** - Verifies duplicates are removed
2. **Text Truncation Test** - Ensures no mid-word cuts
3. **Real Article Test** - Tests with actual article URLs

All tests pass successfully!

## Results

Using `fix_scraped_data.py` on the problematic data:
- **Before**: Articles had 2-5x duplicate sentences, truncated text
- **After**: Clean, deduplicated content with proper sentence boundaries
- **Example**: First article reduced from 9 to 7 sentences (removed 2 duplicates)

## Future Improvements

1. Consider implementing fuzzy matching for near-duplicate sentences
2. Add language-specific sentence splitting for better Korean/Chinese support
3. Implement content quality scoring to filter low-quality extractions
4. Add monitoring to track duplicate rates over time

## Files Modified

1. `/scripts/scraper.py` - Main scraper with deduplication logic
2. `/scripts/text_processing.py` - Fixed safe truncation method
3. `/test_content_extraction.py` - Comprehensive test suite
4. `/fix_scraped_data.py` - Utility to fix existing scraped data

## How to Use

1. **New scraping** - The fix is automatically applied to all new scraping runs
2. **Fix existing data** - Run `python3 fix_scraped_data.py` to process existing files
3. **Test the fix** - Run `python3 test_content_extraction.py` to verify everything works

The scraper now produces clean, deduplicated content with proper text boundaries!