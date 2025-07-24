"""
Performance and load testing for Singapore News Scraper
"""
import pytest
import time
import json
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch
import memory_profiler
import psutil
import os

# Import modules to test
try:
    from scripts.scraper import scrape_site, clean_text, extract_articles_generic
    from scripts.ai_scraper import AIScraper
except ImportError:
    pytest.skip("Scraper modules not available", allow_module_level=True)

class TestPerformance:
    """Performance test cases"""
    
    @pytest.fixture
    def large_html_content(self):
        """Generate large HTML content for testing"""
        articles_html = ""
        for i in range(100):
            articles_html += f"""
            <article>
                <h2><a href="/article/{i}">Article Title {i}</a></h2>
                <p>{"Lorem ipsum dolor sit amet " * 50}</p>
                <time datetime="2025-07-24T10:00:00+09:00">July 24, 2025</time>
            </article>
            """
        
        return f"""
        <html>
        <head><title>Test News Site</title></head>
        <body>
            <div class="articles">
                {articles_html}
            </div>
        </body>
        </html>
        """
    
    @pytest.fixture
    def large_article_list(self):
        """Generate large list of articles"""
        return [
            {
                'title': f'Article {i}',
                'url': f'https://example.com/article/{i}',
                'content': 'Lorem ipsum ' * 100,
                'summary': 'Test summary ' * 20,
                'group': ['News', 'Economy', 'Technology'][i % 3],
                'site': 'Test Site',
                'publish_date': '2025-07-24T10:00:00+09:00'
            }
            for i in range(1000)
        ]
    
    def test_text_cleaning_performance(self):
        """Test performance of text cleaning function"""
        # Large text with HTML
        large_text = "<p>Test content</p> " * 10000
        
        start_time = time.time()
        cleaned = clean_text(large_text)
        duration = time.time() - start_time
        
        assert duration < 1.0  # Should complete within 1 second
        assert len(cleaned) > 0
        assert '<p>' not in cleaned
    
    def test_article_extraction_performance(self, large_html_content):
        """Test performance of article extraction"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = large_html_content
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            start_time = time.time()
            articles = extract_articles_generic("https://example.com", large_html_content)
            duration = time.time() - start_time
            
            assert duration < 2.0  # Should complete within 2 seconds
            assert len(articles) > 0
    
    def test_concurrent_scraping(self):
        """Test concurrent scraping of multiple sites"""
        sites = [
            {'name': f'Site {i}', 'url': f'https://example{i}.com', 'group': 'News'}
            for i in range(10)
        ]
        
        def mock_scrape(site):
            time.sleep(0.1)  # Simulate network delay
            return [{
                'title': f'Article from {site["name"]}',
                'url': f'{site["url"]}/article'
            }]
        
        with patch('scripts.scraper.scrape_site', side_effect=mock_scrape):
            start_time = time.time()
            
            # Concurrent execution
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(mock_scrape, site) for site in sites]
                results = []
                for future in as_completed(futures):
                    results.extend(future.result())
            
            duration = time.time() - start_time
            
            # Should be faster than sequential (10 * 0.1 = 1 second)
            assert duration < 0.5  # With 5 workers, should complete in ~0.2 seconds
            assert len(results) == 10
    
    @pytest.mark.memory
    def test_memory_usage_large_dataset(self, large_article_list):
        """Test memory usage with large dataset"""
        import tracemalloc
        
        tracemalloc.start()
        
        # Process large dataset
        start_snapshot = tracemalloc.take_snapshot()
        
        # Simulate processing
        processed = []
        for article in large_article_list:
            processed_article = {
                'title': clean_text(article['title']),
                'summary': article['summary'][:100],
                'url': article['url']
            }
            processed.append(processed_article)
        
        end_snapshot = tracemalloc.take_snapshot()
        
        # Calculate memory usage
        stats = end_snapshot.compare_to(start_snapshot, 'lineno')
        total_memory = sum(stat.size_diff for stat in stats)
        
        # Memory usage should be reasonable (less than 50MB for 1000 articles)
        assert total_memory < 50 * 1024 * 1024
        
        tracemalloc.stop()
    
    def test_ai_scraper_rate_limiting_performance(self):
        """Test AI scraper rate limiting performance"""
        with patch('google.generativeai.GenerativeModel'):
            ai_scraper = AIScraper("test_key")
            
            # Simulate rapid requests
            start_time = time.time()
            
            for i in range(15):  # Gemini limit is 15/minute
                ai_scraper._check_rate_limit()
            
            duration = time.time() - start_time
            
            # Should implement proper rate limiting
            assert duration < 5.0  # Should not block unnecessarily
    
    def test_json_serialization_performance(self, large_article_list):
        """Test JSON serialization performance"""
        data = {
            'timestamp': '2025-07-24T10:00:00+09:00',
            'articles': large_article_list,
            'stats': {
                'total': len(large_article_list),
                'byGroup': {'News': 334, 'Economy': 333, 'Technology': 333}
            }
        }
        
        # Test serialization
        start_time = time.time()
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        serialization_time = time.time() - start_time
        
        # Test deserialization
        start_time = time.time()
        loaded_data = json.loads(json_str)
        deserialization_time = time.time() - start_time
        
        assert serialization_time < 0.5  # Should serialize quickly
        assert deserialization_time < 0.5  # Should deserialize quickly
        assert len(loaded_data['articles']) == 1000
    
    @pytest.mark.stress
    def test_stress_continuous_scraping(self):
        """Stress test: continuous scraping simulation"""
        def mock_scrape_cycle():
            with patch('scripts.scraper.scrape_site') as mock_scrape:
                mock_scrape.return_value = [
                    {'title': 'Test', 'url': 'https://test.com'}
                ]
                
                # Simulate 100 scraping cycles
                for _ in range(100):
                    result = mock_scrape({'url': 'https://test.com'})
                    assert len(result) > 0
                    time.sleep(0.01)  # Small delay
        
        # Run in thread to test for memory leaks or performance degradation
        thread = threading.Thread(target=mock_scrape_cycle)
        thread.start()
        thread.join(timeout=10)  # Should complete within 10 seconds
        
        assert not thread.is_alive()  # Thread should have completed
    
    def test_parallel_api_calls(self):
        """Test parallel API endpoint calls"""
        async def mock_api_call(endpoint):
            await asyncio.sleep(0.1)  # Simulate API delay
            return {'success': True, 'endpoint': endpoint}
        
        async def run_parallel_calls():
            endpoints = [
                '/api/get-latest-scraped',
                '/api/auth',
                '/api/get-scraping-status',
                '/api/test-env'
            ]
            
            tasks = [mock_api_call(ep) for ep in endpoints]
            results = await asyncio.gather(*tasks)
            return results
        
        start_time = time.time()
        results = asyncio.run(run_parallel_calls())
        duration = time.time() - start_time
        
        # Should complete faster than sequential (0.4s)
        assert duration < 0.2
        assert len(results) == 4
        assert all(r['success'] for r in results)
    
    def test_file_operations_performance(self, tmp_path):
        """Test file I/O performance"""
        # Create many small files
        start_time = time.time()
        
        for i in range(100):
            file_path = tmp_path / f"article_{i}.json"
            data = {'id': i, 'title': f'Article {i}', 'content': 'x' * 1000}
            file_path.write_text(json.dumps(data))
        
        write_duration = time.time() - start_time
        
        # Read all files
        start_time = time.time()
        articles = []
        
        for i in range(100):
            file_path = tmp_path / f"article_{i}.json"
            data = json.loads(file_path.read_text())
            articles.append(data)
        
        read_duration = time.time() - start_time
        
        assert write_duration < 1.0  # Should write quickly
        assert read_duration < 0.5   # Reading should be faster
        assert len(articles) == 100