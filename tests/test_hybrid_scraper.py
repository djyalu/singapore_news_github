"""
Unit tests for hybrid scraper functionality
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import pytz

# Import the modules to test
try:
    from scripts.scraper_hybrid import (
        HybridScraper,
        scrape_with_hybrid,
        combine_results
    )
except ImportError:
    pytest.skip("Hybrid scraper modules not available", allow_module_level=True)

class TestHybridScraper:
    """Test hybrid scraper functionality"""
    
    @pytest.fixture
    def mock_traditional_scraper(self):
        """Mock traditional scraper"""
        with patch('scripts.scraper.scrape_site') as mock_scrape:
            mock_scrape.return_value = [
                {
                    'title': 'Traditional Article 1',
                    'url': 'https://example.com/trad1',
                    'summary': 'Traditional summary 1',
                    'extracted_by': 'traditional'
                },
                {
                    'title': 'Traditional Article 2',
                    'url': 'https://example.com/trad2',
                    'summary': 'Traditional summary 2',
                    'extracted_by': 'traditional'
                }
            ]
            yield mock_scrape
    
    @pytest.fixture
    def mock_ai_scraper(self):
        """Mock AI scraper"""
        with patch('scripts.ai_scraper.AIScraper') as mock_ai:
            mock_instance = Mock()
            mock_instance.generate_summary.return_value = "이것은 AI가 생성한 한국어 요약입니다."
            mock_instance.extract_article.return_value = {
                'title': 'AI Enhanced Article',
                'content': 'Enhanced content with AI',
                'summary': '향상된 AI 요약',
                'extracted_by': 'ai'
            }
            mock_ai.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def hybrid_scraper(self, mock_traditional_scraper, mock_ai_scraper):
        """Create HybridScraper instance"""
        with patch('scripts.scraper_hybrid.load_settings') as mock_settings:
            mock_settings.return_value = {
                'scrapingMethod': 'hybrid_ai',
                'maxArticlesPerSite': 3
            }
            scraper = HybridScraper()
            scraper.ai_scraper = mock_ai_scraper
            return scraper
    
    def test_hybrid_scraper_initialization(self):
        """Test HybridScraper initialization"""
        with patch('scripts.scraper_hybrid.load_settings') as mock_settings:
            mock_settings.return_value = {'scrapingMethod': 'hybrid_ai'}
            
            # With AI key
            with patch.dict('os.environ', {'GOOGLE_GEMINI_API_KEY': 'test_key'}):
                scraper = HybridScraper()
                assert scraper.ai_available is True
            
            # Without AI key
            with patch.dict('os.environ', {}, clear=True):
                scraper = HybridScraper()
                assert scraper.ai_available is False
    
    def test_phase1_traditional_scraping(self, hybrid_scraper, mock_traditional_scraper):
        """Test Phase 1: Traditional link collection"""
        site = {
            'name': 'Test Site',
            'url': 'https://example.com',
            'group': 'News'
        }
        
        articles = hybrid_scraper.scrape_site_phase1(site)
        
        assert len(articles) == 2
        assert all(a['extracted_by'] == 'traditional' for a in articles)
        mock_traditional_scraper.assert_called_once()
    
    def test_phase2_ai_enhancement(self, hybrid_scraper):
        """Test Phase 2: AI enhancement of articles"""
        articles = [
            {
                'title': 'Test Article',
                'url': 'https://example.com/test',
                'content': 'Original content',
                'summary': 'Original summary'
            }
        ]
        
        enhanced = hybrid_scraper.enhance_with_ai(articles)
        
        assert len(enhanced) == 1
        assert enhanced[0]['summary'] == "이것은 AI가 생성한 한국어 요약입니다."
        assert enhanced[0]['extracted_by'] == 'hybrid_ai'
    
    def test_ai_enhancement_fallback(self, hybrid_scraper):
        """Test AI enhancement with fallback on failure"""
        hybrid_scraper.ai_scraper.generate_summary.side_effect = Exception("AI Error")
        
        articles = [
            {
                'title': 'Test Article',
                'content': 'Test content',
                'summary': 'Original summary'
            }
        ]
        
        enhanced = hybrid_scraper.enhance_with_ai(articles)
        
        # Should keep original summary on AI failure
        assert enhanced[0]['summary'] == 'Original summary'
        assert enhanced[0]['extracted_by'] == 'hybrid_fallback'
    
    def test_combine_results(self, hybrid_scraper):
        """Test combining results from multiple sources"""
        traditional_articles = [
            {'title': 'Trad 1', 'group': 'News'},
            {'title': 'Trad 2', 'group': 'News'}
        ]
        
        ai_articles = [
            {'title': 'AI 1', 'group': 'Economy'},
            {'title': 'AI 2', 'group': 'Economy'}
        ]
        
        combined = hybrid_scraper.combine_results([traditional_articles, ai_articles])
        
        assert len(combined) == 4
        assert len([a for a in combined if a['group'] == 'News']) == 2
        assert len([a for a in combined if a['group'] == 'Economy']) == 2
    
    def test_full_hybrid_workflow(self, hybrid_scraper):
        """Test complete hybrid scraping workflow"""
        sites = [
            {'name': 'Site 1', 'url': 'https://site1.com', 'group': 'News'},
            {'name': 'Site 2', 'url': 'https://site2.com', 'group': 'Economy'}
        ]
        
        with patch.object(hybrid_scraper, 'scrape_site_phase1') as mock_phase1:
            mock_phase1.return_value = [
                {
                    'title': 'Article',
                    'url': 'https://example.com/article',
                    'content': 'Content',
                    'summary': 'Summary'
                }
            ]
            
            results = hybrid_scraper.scrape_all_sites(sites)
            
            assert len(results) > 0
            assert all('extracted_by' in article for article in results)
    
    def test_priority_based_selection(self, hybrid_scraper):
        """Test priority-based article selection"""
        # Many articles from same group
        articles = [
            {'title': f'Article {i}', 'group': 'News', 'score': i}
            for i in range(10)
        ]
        
        # Should limit articles per group
        selected = hybrid_scraper.select_best_articles(articles, max_per_group=3)
        
        assert len(selected) <= 3
        # Should select highest scoring articles
        assert all(article['score'] >= 7 for article in selected)
    
    def test_error_handling(self, hybrid_scraper):
        """Test error handling in hybrid scraping"""
        with patch.object(hybrid_scraper, 'scrape_site_phase1') as mock_phase1:
            mock_phase1.side_effect = Exception("Scraping error")
            
            site = {'name': 'Error Site', 'url': 'https://error.com'}
            
            # Should handle error gracefully
            articles = hybrid_scraper.scrape_site_safe(site)
            assert articles == []
    
    def test_performance_optimization(self, hybrid_scraper):
        """Test performance optimizations"""
        # Test caching
        url = "https://example.com/cached"
        content = "Cached content"
        
        # First call
        result1 = hybrid_scraper.get_cached_or_fetch(url, content)
        
        # Second call (should use cache)
        result2 = hybrid_scraper.get_cached_or_fetch(url, content)
        
        assert result1 == result2
        assert hybrid_scraper.cache_hits == 1
    
    def test_scraping_method_detection(self):
        """Test detection of scraping method"""
        with patch('scripts.scraper_hybrid.load_settings') as mock_settings:
            # Hybrid AI method
            mock_settings.return_value = {'scrapingMethod': 'hybrid_ai'}
            scraper = HybridScraper()
            assert scraper.method == 'hybrid_ai'
            
            # Fallback for legacy hybrid
            mock_settings.return_value = {'scrapingMethod': 'hybrid'}
            scraper = HybridScraper()
            assert scraper.method == 'hybrid_ai'
    
    def test_group_balancing(self, hybrid_scraper):
        """Test balanced article selection across groups"""
        articles = [
            {'title': f'News {i}', 'group': 'News'} for i in range(10)
        ] + [
            {'title': f'Econ {i}', 'group': 'Economy'} for i in range(5)
        ] + [
            {'title': f'Tech {i}', 'group': 'Technology'} for i in range(3)
        ]
        
        balanced = hybrid_scraper.balance_by_group(articles, max_total=9)
        
        # Should have articles from all groups
        groups = set(a['group'] for a in balanced)
        assert len(groups) == 3
        
        # Should not exceed max per group
        for group in groups:
            group_articles = [a for a in balanced if a['group'] == group]
            assert len(group_articles) <= 3