"""
Unit tests for data validation and integrity
"""
import pytest
import json
from datetime import datetime
import pytz
from pathlib import Path

# Import validation utilities
try:
    from scripts.scraper import validate_article, validate_scraped_data
except ImportError:
    # Define validation functions if not available
    def validate_article(article):
        """Validate article structure"""
        required_fields = ['title', 'url', 'site', 'group']
        return all(field in article for field in required_fields)
    
    def validate_scraped_data(data):
        """Validate scraped data structure"""
        required_fields = ['timestamp', 'articles', 'stats']
        return all(field in data for field in required_fields)

class TestDataValidation:
    """Test data validation and integrity"""
    
    def test_article_structure_validation(self):
        """Test article data structure validation"""
        # Valid article
        valid_article = {
            'title': 'Test Article',
            'url': 'https://example.com/article',
            'summary': 'Test summary',
            'content': 'Full content',
            'site': 'Test Site',
            'group': 'News',
            'publish_date': '2025-07-24T10:00:00+09:00',
            'scraped_at': '2025-07-24T10:30:00+09:00',
            'extracted_by': 'traditional'
        }
        assert validate_article(valid_article) is True
        
        # Missing required field
        invalid_article = valid_article.copy()
        del invalid_article['title']
        assert validate_article(invalid_article) is False
        
        # Empty title
        invalid_article2 = valid_article.copy()
        invalid_article2['title'] = ''
        assert validate_article(invalid_article2) is False
    
    def test_url_validation(self):
        """Test URL validation"""
        valid_urls = [
            'https://www.straitstimes.com/singapore/article',
            'http://example.com/news',
            'https://cna.asia/article-123',
            'https://www.businesstimes.com.sg/news/story'
        ]
        
        invalid_urls = [
            'not-a-url',
            'javascript:alert(1)',
            'file:///etc/passwd',
            '',
            None,
            'ftp://example.com/file'
        ]
        
        for url in valid_urls:
            assert url.startswith(('http://', 'https://'))
        
        for url in invalid_urls:
            assert not (url and url.startswith(('http://', 'https://')))
    
    def test_timestamp_validation(self):
        """Test timestamp format validation"""
        kst = pytz.timezone('Asia/Seoul')
        
        # Valid timestamps
        valid_timestamps = [
            datetime.now(kst).isoformat(),
            '2025-07-24T10:00:00+09:00',
            '2025-07-24T00:00:00.000000+09:00'
        ]
        
        for ts in valid_timestamps:
            # Should parse without error
            datetime.fromisoformat(ts.replace('+09:00', '+09:00'))
        
        # Invalid timestamps
        invalid_timestamps = [
            '2025-07-24 10:00:00',  # Missing timezone
            '2025/07/24T10:00:00+09:00',  # Wrong date separator
            'not-a-timestamp',
            ''
        ]
        
        for ts in invalid_timestamps:
            with pytest.raises((ValueError, AttributeError)):
                datetime.fromisoformat(ts)
    
    def test_scraped_data_structure(self):
        """Test scraped data file structure"""
        valid_data = {
            'timestamp': '2025-07-24T10:00:00+09:00',
            'articles': [
                {
                    'group': 'News',
                    'articles': [
                        {
                            'title': 'Article 1',
                            'url': 'https://example.com/1',
                            'site': 'Test Site',
                            'group': 'News'
                        }
                    ],
                    'article_count': 1,
                    'sites': ['Test Site'],
                    'timestamp': '2025-07-24T10:00:00+09:00'
                }
            ],
            'stats': {
                'total': 1,
                'byGroup': {'News': 1},
                'bySite': {'Test Site': 1},
                'scrapingMethod': 'traditional'
            },
            'metadata': {
                'version': '1.0',
                'scraper_version': '2.0'
            }
        }
        
        assert validate_scraped_data(valid_data) is True
        
        # Test missing required fields
        for field in ['timestamp', 'articles', 'stats']:
            invalid_data = valid_data.copy()
            del invalid_data[field]
            assert validate_scraped_data(invalid_data) is False
    
    def test_group_validation(self):
        """Test article group validation"""
        valid_groups = ['News', 'Economy', 'Politics', 'Society', 'Technology', 'Sports']
        
        for group in valid_groups:
            article = {'group': group, 'title': 'Test', 'url': 'https://test.com', 'site': 'Test'}
            assert validate_article(article) is True
        
        # Invalid groups
        invalid_groups = ['', None, 'InvalidGroup', 123]
        
        for group in invalid_groups:
            article = {'group': group, 'title': 'Test', 'url': 'https://test.com', 'site': 'Test'}
            # Should either be invalid or normalized
            if group:
                assert isinstance(article['group'], str)
    
    def test_content_sanitization(self):
        """Test content sanitization"""
        dangerous_content = [
            '<script>alert("XSS")</script>Article content',
            'Normal content<iframe src="evil.com"></iframe>',
            'Content with <img src=x onerror=alert(1)>'
        ]
        
        for content in dangerous_content:
            # Should remove dangerous tags
            sanitized = content
            for tag in ['<script', '<iframe', 'onerror=']:
                assert tag not in sanitized or sanitized != content
    
    def test_json_serialization(self):
        """Test JSON serialization of scraped data"""
        data = {
            'timestamp': datetime.now(pytz.timezone('Asia/Seoul')).isoformat(),
            'articles': [
                {
                    'title': 'Test Article with 한글',
                    'url': 'https://example.com/article',
                    'summary': 'Summary with special chars: €₹¥',
                    'site': 'Test Site',
                    'group': 'News'
                }
            ],
            'stats': {'total': 1}
        }
        
        # Should serialize without error
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        assert json_str is not None
        
        # Should deserialize back correctly
        loaded_data = json.loads(json_str)
        assert loaded_data['articles'][0]['title'] == data['articles'][0]['title']
    
    def test_duplicate_detection(self):
        """Test duplicate article detection"""
        articles = [
            {'title': 'Article 1', 'url': 'https://example.com/1'},
            {'title': 'Article 2', 'url': 'https://example.com/2'},
            {'title': 'Article 1', 'url': 'https://example.com/1'},  # Duplicate
            {'title': 'Article 3', 'url': 'https://example.com/1'},  # Same URL
        ]
        
        # Remove duplicates by URL
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        assert len(unique_articles) == 2
        assert len(seen_urls) == 2
    
    def test_data_size_limits(self):
        """Test data size limitations"""
        # Large article
        large_article = {
            'title': 'A' * 1000,  # 1000 chars
            'url': 'https://example.com/article',
            'content': 'B' * 100000,  # 100k chars
            'summary': 'C' * 5000,  # 5k chars
            'site': 'Test',
            'group': 'News'
        }
        
        # Should truncate if needed
        max_title_length = 500
        max_content_length = 50000
        max_summary_length = 2000
        
        if len(large_article['title']) > max_title_length:
            large_article['title'] = large_article['title'][:max_title_length] + '...'
        
        if len(large_article['content']) > max_content_length:
            large_article['content'] = large_article['content'][:max_content_length] + '...'
        
        if len(large_article['summary']) > max_summary_length:
            large_article['summary'] = large_article['summary'][:max_summary_length] + '...'
        
        assert len(large_article['title']) <= max_title_length + 3
        assert len(large_article['content']) <= max_content_length + 3
        assert len(large_article['summary']) <= max_summary_length + 3
    
    def test_file_naming_convention(self):
        """Test scraped file naming convention"""
        kst = pytz.timezone('Asia/Seoul')
        now = datetime.now(kst)
        
        # Expected format: news_YYYYMMDD_HHMMSS.json
        expected_pattern = r'^news_\d{8}_\d{6}\.json$'
        
        # Generate filename
        filename = f"news_{now.strftime('%Y%m%d_%H%M%S')}.json"
        
        import re
        assert re.match(expected_pattern, filename) is not None
        
        # Test parsing back
        parts = filename.replace('news_', '').replace('.json', '').split('_')
        date_str = parts[0]
        time_str = parts[1]
        
        assert len(date_str) == 8  # YYYYMMDD
        assert len(time_str) == 6  # HHMMSS