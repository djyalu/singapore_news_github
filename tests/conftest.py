"""
Pytest configuration and fixtures for Singapore News Scraper tests
"""
import pytest
import os
import json
import tempfile
from datetime import datetime
from unittest.mock import Mock, patch
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'scripts'))

@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    return {
        "scrapTarget": "recent",
        "importantKeywords": "economy,politics,covid",
        "summaryOptions": {
            "headline": True,
            "keywords": True,
            "content": True
        },
        "sendChannel": "whatsapp",
        "whatsappChannel": "120363419092108413@g.us",
        "sendSchedule": {
            "period": "daily",
            "time": "08:00",
            "weekdays": [],
            "date": "1"
        },
        "blockedKeywords": "advertisement,spam",
        "scrapingMethod": "traditional",
        "scrapingMethodOptions": {
            "ai": {
                "provider": "gemini",
                "model": "gemini-1.5-flash",
                "fallbackToTraditional": True
            },
            "traditional": {
                "useEnhancedFiltering": True
            }
        },
        "monitoring": {
            "enabled": True
        }
    }

@pytest.fixture
def mock_sites():
    """Mock sites configuration for testing"""
    return [
        {
            "name": "The Straits Times",
            "url": "https://www.straitstimes.com",
            "group": "News",
            "enabled": True
        },
        {
            "name": "Channel NewsAsia",
            "url": "https://www.channelnewsasia.com",
            "group": "News", 
            "enabled": True
        },
        {
            "name": "Business Times",
            "url": "https://www.businesstimes.com.sg",
            "group": "Economy",
            "enabled": True
        }
    ]

@pytest.fixture
def sample_article():
    """Sample article data for testing"""
    return {
        "title": "Singapore economy shows strong growth",
        "url": "https://example.com/article/123",
        "summary": "Singapore's economy demonstrated robust growth in Q3...",
        "content": "The Singapore economy expanded by 4.5% year-on-year in the third quarter...",
        "site": "The Straits Times",
        "group": "Economy",
        "publish_date": "2025-07-24T00:00:00+09:00",
        "scraped_at": "2025-07-24T00:30:00+09:00"
    }

@pytest.fixture
def sample_scraped_data():
    """Sample scraped data structure"""
    return {
        "timestamp": "2025-07-24T00:30:00+09:00",
        "articles": [
            {
                "group": "News",
                "articles": [
                    {
                        "title": "Breaking News Story",
                        "url": "https://example.com/news/1",
                        "summary": "Important news summary",
                        "site": "The Straits Times",
                        "group": "News"
                    }
                ],
                "article_count": 1,
                "sites": ["The Straits Times"],
                "timestamp": "2025-07-24T00:30:00+09:00",
                "scraping_method": "traditional"
            }
        ],
        "stats": {
            "total": 1,
            "byGroup": {"News": 1}
        }
    }

@pytest.fixture
def temp_data_dir():
    """Create temporary data directory for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create subdirectories
        scraped_dir = os.path.join(temp_dir, "scraped")
        history_dir = os.path.join(temp_dir, "history")
        os.makedirs(scraped_dir)
        os.makedirs(history_dir)
        
        # Create sample files
        settings_file = os.path.join(temp_dir, "settings.json")
        sites_file = os.path.join(temp_dir, "sites.json")
        latest_file = os.path.join(temp_dir, "latest.json")
        
        with open(settings_file, 'w') as f:
            json.dump({
                "scrapingMethod": "traditional",
                "maxArticlesPerSite": 3
            }, f)
            
        with open(sites_file, 'w') as f:
            json.dump([{
                "name": "Test Site",
                "url": "https://test.com",
                "group": "News",
                "enabled": True
            }], f)
            
        with open(latest_file, 'w') as f:
            json.dump({
                "lastUpdated": "2025-07-24T00:00:00+09:00",
                "latestFile": "news_20250724_000000.json"
            }, f)
        
        yield temp_dir

@pytest.fixture
def mock_requests():
    """Mock requests for HTTP calls"""
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post:
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = "<html><body>Test content</body></html>"
        mock_response.json.return_value = {"success": True}
        
        mock_get.return_value = mock_response
        mock_post.return_value = mock_response
        
        yield {
            'get': mock_get,
            'post': mock_post,
            'response': mock_response
        }

@pytest.fixture
def mock_beautiful_soup():
    """Mock BeautifulSoup for HTML parsing"""
    with patch('bs4.BeautifulSoup') as mock_soup:
        mock_soup_instance = Mock()
        mock_soup_instance.find_all.return_value = []
        mock_soup_instance.find.return_value = None
        mock_soup_instance.get_text.return_value = "Sample text content"
        
        mock_soup.return_value = mock_soup_instance
        yield mock_soup_instance

@pytest.fixture
def mock_datetime():
    """Mock datetime for consistent testing"""
    test_datetime = datetime(2025, 7, 24, 0, 30, 0)
    with patch('datetime.datetime') as mock_dt:
        mock_dt.now.return_value = test_datetime
        mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
        yield test_datetime

@pytest.fixture
def mock_file_operations():
    """Mock file operations for testing"""
    with patch('builtins.open', create=True) as mock_open, \
         patch('os.path.exists') as mock_exists, \
         patch('os.makedirs') as mock_makedirs:
        
        mock_exists.return_value = True
        yield {
            'open': mock_open,
            'exists': mock_exists,
            'makedirs': mock_makedirs
        }

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables"""
    test_env = {
        'GITHUB_TOKEN': 'test_token',
        'GITHUB_OWNER': 'test_owner',
        'GITHUB_REPO': 'test_repo',
        'WHATSAPP_API_KEY': 'test_whatsapp_key',
        'GOOGLE_GEMINI_API_KEY': 'test_gemini_key'
    }
    
    with patch.dict(os.environ, test_env):
        yield test_env