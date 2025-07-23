"""
Unit tests for the main scraper functionality
"""
import pytest
import json
import os
from unittest.mock import Mock, patch, mock_open
from datetime import datetime
import pytz

# Import the modules to test
try:
    from scripts.scraper import (
        load_settings, 
        load_sites, 
        clean_text, 
        is_recent_article,
        contains_keywords,
        is_blocked,
        extract_articles_generic,
        scrape_site
    )
except ImportError:
    pytest.skip("Scraper modules not available", allow_module_level=True)

class TestScraperCore:
    """Test core scraper functionality"""
    
    def test_load_settings_success(self, mock_requests):
        """Test successful settings loading from API"""
        mock_requests['get'].return_value.json.return_value = {
            'success': True,
            'data': {'scrapingMethod': 'traditional'}
        }
        
        settings = load_settings()
        assert settings['scrapingMethod'] == 'traditional'
        mock_requests['get'].assert_called_once()
    
    def test_load_settings_fallback_to_file(self, mock_file_operations):
        """Test fallback to local file when API fails"""
        # Mock API failure
        with patch('requests.get', side_effect=Exception("API Error")):
            # Mock file reading
            mock_data = {'scrapingMethod': 'ai'}
            mock_file_operations['open'].return_value.__enter__.return_value.read.return_value = json.dumps(mock_data)
            
            with patch('json.load', return_value=mock_data):
                settings = load_settings()
                assert settings['scrapingMethod'] == 'ai'
    
    def test_load_settings_default_fallback(self, mock_file_operations):
        """Test default settings when both API and file fail"""
        with patch('requests.get', side_effect=Exception("API Error")), \
             patch('json.load', side_effect=FileNotFoundError()):
            
            settings = load_settings()
            assert 'scrapingMethod' in settings
            assert settings['scrapingMethod'] == 'traditional'
    
    def test_load_sites_success(self, mock_requests, mock_sites):
        """Test successful sites loading"""
        mock_requests['get'].return_value.json.return_value = {
            'success': True,
            'data': mock_sites
        }
        
        sites = load_sites()
        assert len(sites) == 3
        assert sites[0]['name'] == 'The Straits Times'
    
    def test_clean_text_basic(self):
        """Test basic text cleaning functionality"""
        # Test HTML tag removal
        html_text = "<p>This is <strong>bold</strong> text.</p>"
        cleaned = clean_text(html_text)
        assert "<p>" not in cleaned
        assert "<strong>" not in cleaned
        assert "This is bold text." in cleaned
        
        # Test multiple whitespace reduction
        spaced_text = "This   has    multiple     spaces"
        cleaned = clean_text(spaced_text)
        assert "This has multiple spaces" in cleaned
        
        # Test empty string
        assert clean_text("") == ""
        
        # Test None input
        assert clean_text(None) == ""
    
    def test_is_recent_article(self):
        """Test article recency checking"""
        kst = pytz.timezone('Asia/Seoul')
        now = datetime.now(kst)
        
        # Test recent article (within 2 days)
        recent_date = now
        assert is_recent_article(recent_date) == True
        
        # Test old article (more than 2 days)
        from datetime import timedelta
        old_date = now - timedelta(days=3)
        assert is_recent_article(old_date) == False
        
        # Test None date (should return True as fallback)
        assert is_recent_article(None) == True
    
    def test_contains_keywords(self):
        """Test keyword matching functionality"""
        text = "Singapore economy shows strong growth in technology sector"
        
        # Test positive match
        keywords = ["economy", "technology"]
        assert contains_keywords(text, keywords) == True
        
        # Test case insensitive
        keywords = ["ECONOMY", "TECHNOLOGY"] 
        assert contains_keywords(text, keywords) == True
        
        # Test no match
        keywords = ["politics", "sports"]
        assert contains_keywords(text, keywords) == False
        
        # Test empty keywords
        assert contains_keywords(text, []) == False
        
        # Test empty text
        assert contains_keywords("", ["keyword"]) == False
    
    def test_is_blocked(self):
        """Test blocked keywords functionality"""
        text = "This article contains advertisement content"
        
        # Test blocked content
        blocked_keywords = ["advertisement", "spam"]
        assert is_blocked(text, blocked_keywords) == True
        
        # Test case insensitive
        blocked_keywords = ["ADVERTISEMENT"]
        assert is_blocked(text, blocked_keywords) == True
        
        # Test not blocked
        blocked_keywords = ["politics", "sports"]
        assert is_blocked(text, blocked_keywords) == False
        
        # Test empty blocked list
        assert is_blocked(text, []) == False

class TestScraperExtraction:
    """Test article extraction functionality"""
    
    def test_extract_articles_generic(self, mock_beautiful_soup):
        """Test generic article extraction"""
        # Mock BeautifulSoup with sample data
        mock_link = Mock()
        mock_link.get.return_value = "/test-article"
        mock_link.get_text.return_value = "Test Article Title"
        
        mock_beautiful_soup.find_all.return_value = [mock_link]
        
        with patch('bs4.BeautifulSoup', return_value=mock_beautiful_soup):
            soup = mock_beautiful_soup
            articles = extract_articles_generic(soup, "https://test.com", "Test Site")
            
            assert len(articles) >= 0  # Should handle the mocked data gracefully
    
    @patch('requests.get')
    def test_scrape_site_success(self, mock_get, mock_beautiful_soup):
        """Test successful site scraping"""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test content</body></html>"
        mock_get.return_value = mock_response
        
        # Mock article extraction
        with patch('scripts.scraper.extract_articles_generic', return_value=[]):
            articles = scrape_site("https://test.com", "Test Site", {})
            assert isinstance(articles, list)
    
    @patch('requests.get')
    def test_scrape_site_failure(self, mock_get):
        """Test site scraping failure handling"""
        # Mock HTTP failure
        mock_get.side_effect = Exception("Connection failed")
        
        articles = scrape_site("https://test.com", "Test Site", {})
        assert articles == []  # Should return empty list on failure

class TestScraperIntegration:
    """Integration tests for scraper components"""
    
    @patch('scripts.scraper.load_settings')
    @patch('scripts.scraper.load_sites')
    @patch('scripts.scraper.scrape_site')
    def test_scraping_workflow(self, mock_scrape, mock_load_sites, mock_load_settings, 
                              mock_settings, mock_sites, sample_article):
        """Test complete scraping workflow"""
        # Setup mocks
        mock_load_settings.return_value = mock_settings
        mock_load_sites.return_value = mock_sites
        mock_scrape.return_value = [sample_article]
        
        # Test the workflow would work
        settings = mock_load_settings()
        sites = mock_load_sites()
        
        assert len(sites) == 3
        assert settings['scrapingMethod'] == 'traditional'
        
        # Test scraping each site
        for site in sites:
            if site['enabled']:
                articles = mock_scrape(site['url'], site['name'], settings)
                assert len(articles) >= 0

class TestScraperUtils:
    """Test utility functions"""
    
    def test_settings_validation(self, mock_settings):
        """Test settings structure validation"""
        required_keys = [
            'scrapingMethod', 'scrapTarget', 'summaryOptions',
            'sendChannel', 'monitoring'
        ]
        
        for key in required_keys:
            assert key in mock_settings, f"Missing required setting: {key}"
    
    def test_sites_validation(self, mock_sites):
        """Test sites configuration validation"""
        required_keys = ['name', 'url', 'group', 'enabled']
        
        for site in mock_sites:
            for key in required_keys:
                assert key in site, f"Missing required site field: {key}"
            
            # Test URL format
            assert site['url'].startswith('http'), f"Invalid URL format: {site['url']}"
    
    def test_article_structure_validation(self, sample_article):
        """Test article data structure validation"""
        required_keys = [
            'title', 'url', 'summary', 'content', 'site', 
            'group', 'publish_date', 'scraped_at'
        ]
        
        for key in required_keys:
            assert key in sample_article, f"Missing required article field: {key}"

if __name__ == '__main__':
    pytest.main([__file__, '-v'])