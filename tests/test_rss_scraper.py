"""
Unit tests for RSS feed scraper functionality
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import pytz
import feedparser

# Import the modules to test
try:
    from scripts.scraper_rss import (
        RSSFeedScraper,
        parse_rss_feed,
        extract_article_from_feed_entry,
        get_feed_urls
    )
except ImportError:
    pytest.skip("RSS scraper modules not available", allow_module_level=True)

class TestRSSScraper:
    """Test RSS feed scraper functionality"""
    
    @pytest.fixture
    def mock_feed_data(self):
        """Mock RSS feed data"""
        return {
            'feed': {
                'title': 'Test News Feed',
                'link': 'https://example.com',
                'description': 'Test news feed description'
            },
            'entries': [
                {
                    'title': 'First Article Title',
                    'link': 'https://example.com/article1',
                    'summary': 'This is the summary of the first article.',
                    'published_parsed': (2025, 7, 24, 10, 0, 0, 0, 0, 0),
                    'author': 'Test Author',
                    'tags': [{'term': 'Technology'}, {'term': 'Singapore'}]
                },
                {
                    'title': 'Second Article Title',
                    'link': 'https://example.com/article2',
                    'description': 'Description of the second article.',
                    'published_parsed': (2025, 7, 24, 9, 0, 0, 0, 0, 0),
                    'categories': [{'term': 'Business'}]
                }
            ]
        }
    
    @pytest.fixture
    def rss_scraper(self):
        """Create RSSFeedScraper instance"""
        scraper = RSSFeedScraper()
        return scraper
    
    def test_rss_scraper_initialization(self, rss_scraper):
        """Test RSSFeedScraper initialization"""
        assert rss_scraper.feed_urls is not None
        assert isinstance(rss_scraper.feed_urls, dict)
        assert rss_scraper.max_articles_per_feed == 5
    
    def test_parse_rss_feed_success(self, rss_scraper, mock_feed_data):
        """Test successful RSS feed parsing"""
        with patch('feedparser.parse') as mock_parse:
            mock_parse.return_value = mock_feed_data
            
            articles = rss_scraper.parse_feed("https://example.com/feed")
            
            assert len(articles) == 2
            assert articles[0]['title'] == 'First Article Title'
            assert articles[0]['url'] == 'https://example.com/article1'
            assert articles[0]['extracted_by'] == 'rss'
    
    def test_parse_rss_feed_with_limit(self, rss_scraper, mock_feed_data):
        """Test RSS feed parsing with article limit"""
        with patch('feedparser.parse') as mock_parse:
            mock_parse.return_value = mock_feed_data
            
            rss_scraper.max_articles_per_feed = 1
            articles = rss_scraper.parse_feed("https://example.com/feed")
            
            assert len(articles) == 1
            assert articles[0]['title'] == 'First Article Title'
    
    def test_parse_rss_feed_failure(self, rss_scraper):
        """Test RSS feed parsing failure handling"""
        with patch('feedparser.parse') as mock_parse:
            mock_parse.side_effect = Exception("Feed parse error")
            
            articles = rss_scraper.parse_feed("https://example.com/feed")
            
            assert articles == []
    
    def test_extract_article_from_feed_entry(self, rss_scraper):
        """Test article extraction from feed entry"""
        entry = {
            'title': 'Test Article',
            'link': 'https://example.com/test',
            'summary': 'Test summary content',
            'published_parsed': (2025, 7, 24, 10, 0, 0, 0, 0, 0),
            'author': 'John Doe',
            'tags': [{'term': 'Tech'}, {'term': 'News'}]
        }
        
        article = rss_scraper.extract_article_from_entry(entry, "Test Site", "Technology")
        
        assert article['title'] == 'Test Article'
        assert article['url'] == 'https://example.com/test'
        assert article['summary'] == 'Test summary content'
        assert article['site'] == 'Test Site'
        assert article['group'] == 'Technology'
        assert article['author'] == 'John Doe'
        assert 'Tech' in article['tags']
    
    def test_get_feed_urls(self, rss_scraper):
        """Test getting feed URLs for sites"""
        # Test known site
        feed_url = rss_scraper.get_feed_url("Mothership")
        assert feed_url == "https://mothership.sg/feed/"
        
        # Test unknown site
        feed_url = rss_scraper.get_feed_url("Unknown Site")
        assert feed_url is None
    
    def test_date_parsing(self, rss_scraper):
        """Test various date format parsing"""
        # Test with published_parsed
        entry1 = {
            'title': 'Article 1',
            'link': 'https://test.com/1',
            'published_parsed': (2025, 7, 24, 10, 0, 0, 0, 0, 0)
        }
        article1 = rss_scraper.extract_article_from_entry(entry1, "Test", "News")
        assert '2025-07-24' in article1['publish_date']
        
        # Test with published string
        entry2 = {
            'title': 'Article 2',
            'link': 'https://test.com/2',
            'published': 'Wed, 24 Jul 2025 10:00:00 +0900'
        }
        article2 = rss_scraper.extract_article_from_entry(entry2, "Test", "News")
        assert article2['publish_date'] is not None
        
        # Test with no date
        entry3 = {
            'title': 'Article 3',
            'link': 'https://test.com/3'
        }
        article3 = rss_scraper.extract_article_from_entry(entry3, "Test", "News")
        assert article3['publish_date'] is not None  # Should use current time
    
    def test_content_extraction_priority(self, rss_scraper):
        """Test content extraction with different field priorities"""
        # Entry with both summary and description
        entry = {
            'title': 'Test Article',
            'link': 'https://test.com',
            'summary': 'This is the summary',
            'description': 'This is the description',
            'content': [{'value': 'This is the full content'}]
        }
        
        article = rss_scraper.extract_article_from_entry(entry, "Test", "News")
        
        # Should prioritize content over summary/description
        assert 'full content' in article['content']
    
    def test_scrape_all_feeds(self, rss_scraper):
        """Test scraping all configured feeds"""
        with patch.object(rss_scraper, 'parse_feed') as mock_parse:
            mock_parse.return_value = [
                {
                    'title': 'Article from feed',
                    'url': 'https://example.com/article',
                    'group': 'News'
                }
            ]
            
            all_articles = rss_scraper.scrape_all_feeds()
            
            assert len(all_articles) > 0
            assert all(article.get('extracted_by') == 'rss' for article in all_articles)
    
    def test_feed_validation(self, rss_scraper):
        """Test feed validation and error handling"""
        invalid_feeds = [
            {},  # Empty feed
            {'entries': []},  # No entries
            {'entries': [{'no_title': 'test'}]},  # Entry without required fields
        ]
        
        with patch('feedparser.parse') as mock_parse:
            for invalid_feed in invalid_feeds:
                mock_parse.return_value = invalid_feed
                articles = rss_scraper.parse_feed("https://test.com/feed")
                assert isinstance(articles, list)  # Should return empty list, not crash
    
    def test_duplicate_url_handling(self, rss_scraper):
        """Test handling of duplicate URLs in feed"""
        feed_data = {
            'entries': [
                {'title': 'Article 1', 'link': 'https://example.com/same-url'},
                {'title': 'Article 2', 'link': 'https://example.com/same-url'},
                {'title': 'Article 3', 'link': 'https://example.com/different-url'}
            ]
        }
        
        with patch('feedparser.parse') as mock_parse:
            mock_parse.return_value = feed_data
            
            articles = rss_scraper.parse_feed("https://test.com/feed")
            
            # Should handle duplicates appropriately
            urls = [article['url'] for article in articles]
            assert len(urls) == len(set(urls))  # No duplicate URLs