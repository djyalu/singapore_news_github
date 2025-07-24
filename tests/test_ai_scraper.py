"""
Unit tests for AI-enhanced scraper functionality
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import pytz

# Import the modules to test
try:
    from scripts.ai_scraper import (
        AIScraper,
        extract_article_with_ai,
        generate_korean_summary,
        process_links_with_ai,
        get_kst_now
    )
except ImportError:
    pytest.skip("AI scraper modules not available", allow_module_level=True)

class TestAIScraper:
    """Test AI scraper functionality"""
    
    @pytest.fixture
    def mock_gemini_model(self):
        """Mock Gemini AI model"""
        with patch('google.generativeai.GenerativeModel') as mock_model:
            mock_instance = Mock()
            mock_response = Mock()
            mock_response.text = json.dumps({
                "title": "Test Article Title",
                "content": "This is the main content of the article.",
                "summary": "이것은 테스트 기사 요약입니다.",
                "publish_date": "2025-07-24T10:00:00+09:00",
                "author": "Test Author",
                "category": "Technology"
            })
            mock_instance.generate_content.return_value = mock_response
            mock_model.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def ai_scraper(self, mock_gemini_model):
        """Create AIScraper instance with mocked AI model"""
        with patch('google.generativeai.configure'):
            scraper = AIScraper(api_key="test_api_key")
            scraper.model = mock_gemini_model
            return scraper
    
    def test_ai_scraper_initialization(self):
        """Test AIScraper initialization"""
        with patch('google.generativeai.configure') as mock_configure:
            with patch('google.generativeai.GenerativeModel') as mock_model:
                scraper = AIScraper(api_key="test_key")
                mock_configure.assert_called_once_with(api_key="test_key")
                assert scraper.api_key == "test_key"
                assert scraper.requests_this_minute == []
    
    def test_extract_article_with_ai_success(self, ai_scraper):
        """Test successful article extraction with AI"""
        url = "https://example.com/article/123"
        html_content = "<html><body><h1>Test Article</h1><p>Content</p></body></html>"
        
        result = ai_scraper.extract_article(url, html_content)
        
        assert result is not None
        assert result['title'] == "Test Article Title"
        assert result['content'] == "This is the main content of the article."
        assert result['summary'] == "이것은 테스트 기사 요약입니다."
        assert result['url'] == url
        assert result['extracted_by'] == 'ai'
    
    def test_extract_article_with_ai_failure(self, ai_scraper):
        """Test article extraction failure handling"""
        ai_scraper.model.generate_content.side_effect = Exception("AI Error")
        
        url = "https://example.com/article/123"
        html_content = "<html><body><h1>Test</h1></body></html>"
        
        result = ai_scraper.extract_article(url, html_content)
        assert result is None
    
    def test_rate_limiting(self, ai_scraper):
        """Test API rate limiting functionality"""
        # Simulate 15 requests in quick succession
        current_time = get_kst_now()
        ai_scraper.requests_this_minute = [current_time.timestamp()] * 14
        
        # Next request should wait
        with patch('time.sleep') as mock_sleep:
            ai_scraper._check_rate_limit()
            mock_sleep.assert_called()
    
    def test_generate_korean_summary(self, ai_scraper):
        """Test Korean summary generation"""
        text = "Singapore's economy grew by 4.5% in Q3 2025."
        
        summary = ai_scraper.generate_summary(text)
        
        assert summary == "이것은 테스트 기사 요약입니다."
        ai_scraper.model.generate_content.assert_called()
    
    def test_process_links_with_ai(self, ai_scraper):
        """Test processing multiple links with AI"""
        links = [
            {"url": "https://example.com/1", "title": "Article 1"},
            {"url": "https://example.com/2", "title": "Article 2"}
        ]
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = "<html><body>Content</body></html>"
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            results = ai_scraper.process_links(links, site_name="Test Site")
            
            assert len(results) > 0
            assert all(article.get('extracted_by') == 'ai' for article in results)
    
    def test_cache_functionality(self, ai_scraper):
        """Test URL and content caching"""
        url = "https://example.com/cached"
        html_content = "<html><body>Cached Content</body></html>"
        
        # First extraction
        result1 = ai_scraper.extract_article(url, html_content)
        
        # Second extraction (should use cache)
        result2 = ai_scraper.extract_article(url, html_content)
        
        # Should only call AI once due to caching
        assert ai_scraper.model.generate_content.call_count == 1
        assert result1 == result2
    
    def test_fallback_to_traditional(self, ai_scraper):
        """Test fallback to traditional extraction on AI failure"""
        ai_scraper.model.generate_content.side_effect = Exception("AI Error")
        
        with patch('scripts.scraper.extract_article_generic') as mock_traditional:
            mock_traditional.return_value = {
                'title': 'Traditional Title',
                'content': 'Traditional content',
                'extracted_by': 'traditional'
            }
            
            url = "https://example.com/fallback"
            html_content = "<html><body>Content</body></html>"
            
            # Should fallback to traditional method
            ai_scraper.fallback_to_traditional = True
            result = ai_scraper.extract_article_with_fallback(url, html_content)
            
            assert result is not None
            assert result['extracted_by'] == 'traditional'
    
    def test_priority_based_link_limits(self, ai_scraper):
        """Test priority-based link limitation"""
        from scripts.ai_scraper_optimized import get_max_links_for_site
        
        # High priority site
        assert get_max_links_for_site("The Straits Times", "ai") == 4
        assert get_max_links_for_site("Channel NewsAsia", "ai") == 4
        
        # Medium priority site
        assert get_max_links_for_site("Business Times", "ai") == 3
        
        # Low priority site
        assert get_max_links_for_site("Unknown Site", "ai") == 2
    
    def test_ai_response_parsing(self, ai_scraper):
        """Test parsing of various AI response formats"""
        # Test valid JSON response
        ai_scraper.model.generate_content.return_value.text = json.dumps({
            "title": "Valid Title",
            "content": "Valid content"
        })
        result = ai_scraper.extract_article("https://test.com", "<html></html>")
        assert result['title'] == "Valid Title"
        
        # Test invalid JSON response
        ai_scraper.model.generate_content.return_value.text = "Invalid JSON"
        result = ai_scraper.extract_article("https://test.com", "<html></html>")
        assert result is None
    
    def test_kst_timestamp_generation(self):
        """Test KST timestamp generation"""
        kst_now = get_kst_now()
        assert kst_now.tzinfo.zone == 'Asia/Seoul'
        
        iso_timestamp = get_kst_now().isoformat()
        assert '+09:00' in iso_timestamp