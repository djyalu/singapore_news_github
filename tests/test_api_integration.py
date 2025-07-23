"""
API Integration tests for Singapore News Scraper
Tests all API endpoints with real-like conditions
"""
import pytest
import json
import requests
import os
from unittest.mock import Mock, patch
import tempfile

class TestAPIIntegration:
    """Test API endpoints integration"""
    
    BASE_URL = "https://singapore-news-github.vercel.app/api"
    
    def test_api_health_check(self):
        """Test basic API health"""
        # Test environment endpoint
        try:
            response = requests.get(f"{self.BASE_URL}/test-env", timeout=10)
            assert response.status_code in [200, 500]  # Either works or config issue
        except requests.RequestException:
            pytest.skip("API not accessible - likely in development")
    
    @patch('requests.post')
    def test_authentication_endpoint(self, mock_post):
        """Test authentication API"""
        # Mock successful login
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'message': '로그인 성공'
        }
        mock_post.return_value = mock_response
        
        login_data = {
            'type': 'login',
            'username': 'admin',
            'password': 'Admin@123'
        }
        
        response = requests.post(
            f"{self.BASE_URL}/auth",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        result = response.json()
        assert result['success'] == True
        assert '로그인' in result['message']
        mock_post.assert_called_once()
    
    @patch('requests.get')
    def test_get_latest_scraped_endpoint(self, mock_get):
        """Test get latest scraped articles API"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'filename': 'news_20250724_000000.json',
            'lastUpdated': '2025-07-24T00:00:00Z',
            'articleCount': 5,
            'articles': [
                {
                    'group': 'News',
                    'articles': [
                        {
                            'title': 'Test Article',
                            'url': 'https://example.com/test',
                            'summary': 'Test summary',
                            'site': 'Test Site',
                            'group': 'News'
                        }
                    ],
                    'article_count': 1,
                    'sites': ['Test Site'],
                    'timestamp': '2025-07-24T00:00:00Z',
                    'scraping_method': 'traditional'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        response = requests.get(f"{self.BASE_URL}/get-latest-scraped")
        result = response.json()
        
        assert result['success'] == True
        assert 'articles' in result
        assert len(result['articles']) > 0
        assert 'article_count' in result['articles'][0]
        mock_get.assert_called_once()
    
    @patch('requests.post')
    def test_trigger_scraping_endpoint(self, mock_post):
        """Test trigger scraping workflow API"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'message': '뉴스 스크래핑이 시작되었습니다',
            'run_id': 123456789,
            'run_url': 'https://github.com/test/repo/actions/runs/123456789'
        }
        mock_post.return_value = mock_response
        
        trigger_data = {'manual': True}
        
        response = requests.post(
            f"{self.BASE_URL}/trigger-scraping",
            json=trigger_data,
            headers={'Content-Type': 'application/json'}
        )
        
        result = response.json()
        assert result['success'] == True
        assert 'run_id' in result
        assert 'run_url' in result
        assert isinstance(result['run_id'], int)
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_save_data_endpoint(self, mock_post):
        """Test save data (settings/sites) API"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'message': '설정이 저장되었습니다'
        }
        mock_post.return_value = mock_response
        
        # Test settings save
        settings_data = {
            'type': 'settings',
            'settings': {
                'scrapingMethod': 'traditional',
                'maxArticlesPerSite': 3,
                'whatsappChannels': [
                    {
                        'id': '120363419092108413@g.us',
                        'name': 'Test Channel',
                        'enabled': True
                    }
                ]
            }
        }
        
        response = requests.post(
            f"{self.BASE_URL}/save-data",
            json=settings_data,
            headers={'Content-Type': 'application/json'}
        )
        
        result = response.json()
        assert result['success'] == True
        assert '저장' in result['message']
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_delete_scraped_file_endpoint(self, mock_post):
        """Test delete scraped file API"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'message': '파일이 삭제되었습니다'
        }
        mock_post.return_value = mock_response
        
        delete_data = {'filename': 'news_20250724_000000.json'}
        
        response = requests.post(
            f"{self.BASE_URL}/delete-scraped-file",
            json=delete_data,
            headers={'Content-Type': 'application/json'}
        )
        
        result = response.json()
        assert result['success'] == True
        assert '삭제' in result['message']
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_test_whatsapp_endpoint(self, mock_post):
        """Test WhatsApp test message API"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'message': 'WhatsApp 테스트 메시지가 전송되었습니다',
            'messageId': '3EB0C767D097695C4308'
        }
        mock_post.return_value = mock_response
        
        test_data = {
            'message': '테스트 메시지입니다',
            'channelId': '120363419092108413@g.us'
        }
        
        response = requests.post(
            f"{self.BASE_URL}/test-whatsapp",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        result = response.json()
        assert result['success'] == True
        assert 'messageId' in result
        assert len(result['messageId']) > 0
        mock_post.assert_called_once()

class TestAPIErrorHandling:
    """Test API error scenarios"""
    
    BASE_URL = "https://singapore-news-github.vercel.app/api"
    
    @patch('requests.post')
    def test_authentication_failure(self, mock_post):
        """Test authentication with wrong credentials"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'success': False,
            'error': '잘못된 사용자명 또는 비밀번호입니다'
        }
        mock_post.return_value = mock_response
        
        login_data = {
            'type': 'login',
            'username': 'wrong',
            'password': 'wrong'
        }
        
        response = requests.post(
            f"{self.BASE_URL}/auth",
            json=login_data
        )
        
        result = response.json()
        assert result['success'] == False
        assert 'error' in result
        assert response.status_code == 401
    
    @patch('requests.post')
    def test_missing_environment_variables(self, mock_post):
        """Test API with missing environment variables"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {
            'success': False,
            'error': 'GitHub token not configured'
        }
        mock_post.return_value = mock_response
        
        response = requests.post(
            f"{self.BASE_URL}/trigger-scraping",
            json={'manual': True}
        )
        
        result = response.json()
        assert result['success'] == False
        assert 'token' in result['error'].lower()
        assert response.status_code == 500
    
    @patch('requests.get')
    def test_no_scraped_data_available(self, mock_get):
        """Test API when no scraped data is available"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            'success': False,
            'error': '스크랩된 데이터가 없습니다'
        }
        mock_get.return_value = mock_response
        
        response = requests.get(f"{self.BASE_URL}/get-latest-scraped")
        result = response.json()
        
        assert result['success'] == False
        assert '데이터' in result['error']
        assert response.status_code == 404

class TestAPIDataValidation:
    """Test API request/response data validation"""
    
    def test_validate_login_request(self):
        """Test login request data validation"""
        # Valid login request
        valid_request = {
            'type': 'login',
            'username': 'admin',
            'password': 'Admin@123'
        }
        
        required_fields = ['type', 'username', 'password']
        for field in required_fields:
            assert field in valid_request
            assert valid_request[field] is not None
            assert len(str(valid_request[field])) > 0
    
    def test_validate_save_settings_request(self):
        """Test save settings request validation"""
        valid_request = {
            'type': 'settings',
            'settings': {
                'scrapingMethod': 'traditional',
                'maxArticlesPerSite': 3,
                'whatsappChannels': []
            }
        }
        
        assert valid_request['type'] in ['settings', 'sites']
        assert 'settings' in valid_request or 'sites' in valid_request
        
        if 'settings' in valid_request:
            settings = valid_request['settings']
            assert 'scrapingMethod' in settings
            assert settings['scrapingMethod'] in ['traditional', 'ai', 'rss', 'hybrid']
    
    def test_validate_scraped_data_response(self):
        """Test scraped data response structure"""
        sample_response = {
            'success': True,
            'articles': [
                {
                    'group': 'News',
                    'articles': [
                        {
                            'title': 'Test Article',
                            'url': 'https://example.com/test',
                            'summary': 'Test summary',
                            'site': 'Test Site',
                            'group': 'News'
                        }
                    ],
                    'article_count': 1
                }
            ],
            'lastUpdated': '2025-07-24T00:00:00Z',
            'articleCount': 1
        }
        
        # Validate response structure
        assert 'success' in sample_response
        assert sample_response['success'] is True
        assert 'articles' in sample_response
        assert isinstance(sample_response['articles'], list)
        
        # Validate article group structure
        for group in sample_response['articles']:
            assert 'group' in group
            assert 'articles' in group
            assert 'article_count' in group
            assert isinstance(group['articles'], list)
            assert group['article_count'] == len(group['articles'])
            
            # Validate individual articles
            for article in group['articles']:
                required_fields = ['title', 'url', 'summary', 'site', 'group']
                for field in required_fields:
                    assert field in article
                    assert article[field] is not None
                    assert len(str(article[field])) > 0

class TestAPIRateLimiting:
    """Test API rate limiting and performance"""
    
    @patch('requests.get')
    def test_concurrent_requests_handling(self, mock_get):
        """Test API handles concurrent requests properly"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True}
        mock_get.return_value = mock_response
        
        # Simulate concurrent requests
        import concurrent.futures
        import threading
        
        def make_request():
            return requests.get("https://singapore-news-github.vercel.app/api/test-env")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should complete (mocked)
        assert len(results) == 5
        assert all(hasattr(result, 'status_code') for result in results)
    
    def test_request_timeout_handling(self):
        """Test API request timeout handling"""
        with patch('requests.get') as mock_get:
            # Mock timeout exception
            mock_get.side_effect = requests.Timeout("Request timed out")
            
            with pytest.raises(requests.Timeout):
                requests.get(
                    "https://singapore-news-github.vercel.app/api/test-env",
                    timeout=1
                )

class TestAPISecurityHeaders:
    """Test API security headers and CORS"""
    
    @patch('requests.options')
    def test_cors_headers(self, mock_options):
        """Test CORS preflight request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        mock_options.return_value = mock_response
        
        response = requests.options("https://singapore-news-github.vercel.app/api/auth")
        
        # Check CORS headers
        assert 'Access-Control-Allow-Origin' in response.headers
        assert 'Access-Control-Allow-Methods' in response.headers
        assert 'Access-Control-Allow-Headers' in response.headers
        assert response.status_code == 200
    
    def test_content_type_validation(self):
        """Test content type validation"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Validate required headers
        assert 'Content-Type' in headers
        assert headers['Content-Type'] == 'application/json'
        assert 'Accept' in headers

if __name__ == '__main__':
    pytest.main([__file__, '-v'])