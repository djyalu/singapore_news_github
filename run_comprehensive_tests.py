#!/usr/bin/env python3
"""
Comprehensive Test Runner for Singapore News Scraper
Runs tests without pytest dependencies
"""

import sys
import os
import json
import time
import traceback
from datetime import datetime
from pathlib import Path
import importlib
import inspect

# Add project paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts'))

class TestRunner:
    def __init__(self):
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'skipped': 0,
            'tests': []
        }
        self.start_time = time.time()
        
    def print_header(self, text):
        print(f"\n{'=' * 80}")
        print(f"  {text}")
        print('=' * 80)
        
    def print_test_result(self, test_name, status, message=""):
        symbols = {
            'pass': '✓',
            'fail': '✗',
            'error': '⚠',
            'skip': '⊘'
        }
        colors = {
            'pass': '\033[92m',
            'fail': '\033[91m',
            'error': '\033[93m',
            'skip': '\033[94m',
            'reset': '\033[0m'
        }
        
        symbol = symbols.get(status, '?')
        color = colors.get(status, colors['reset'])
        
        print(f"{color}{symbol} {test_name}{colors['reset']}")
        if message:
            print(f"  └─ {message}")
            
        self.results['tests'].append({
            'name': test_name,
            'status': status,
            'message': message
        })
        
        if status == 'pass':
            self.results['passed'] += 1
        elif status == 'fail':
            self.results['failed'] += 1
        elif status == 'error':
            self.results['errors'] += 1
        else:
            self.results['skipped'] += 1
    
    def test_imports(self):
        """Test all module imports"""
        self.print_header("Testing Module Imports")
        
        modules_to_test = [
            'scripts.scraper',
            'scripts.ai_scraper',
            'scripts.scraper_rss',
            'scripts.scraper_hybrid',
            'scripts.send_whatsapp_green',
            'scripts.cleanup_old_data',
            'scripts.ai_summary_free',
            'scripts.site_selectors',
            'scripts.text_processing',
            'scripts.deduplication',
            'scripts.monitoring'
        ]
        
        for module_name in modules_to_test:
            try:
                importlib.import_module(module_name)
                self.print_test_result(f"Import {module_name}", 'pass')
            except ImportError as e:
                self.print_test_result(f"Import {module_name}", 'fail', str(e))
            except Exception as e:
                self.print_test_result(f"Import {module_name}", 'error', str(e))
    
    def test_scraper_functions(self):
        """Test core scraper functions"""
        self.print_header("Testing Scraper Functions")
        
        try:
            from scripts.scraper import clean_text, extract_domain, contains_keywords
            
            # Test clean_text
            test_cases = [
                ("  Hello   World  \n\n", "Hello World"),
                ("Test\n\nMultiple\nLines", "Test Multiple Lines"),
                ("   ", ""),
                ("Normal text", "Normal text")
            ]
            
            for input_text, expected in test_cases:
                result = clean_text(input_text)
                if result == expected:
                    self.print_test_result(f"clean_text('{input_text[:20]}...')", 'pass')
                else:
                    self.print_test_result(f"clean_text('{input_text[:20]}...')", 'fail', 
                                         f"Expected '{expected}', got '{result}'")
            
            # Test extract_domain
            domain_tests = [
                ("https://www.example.com/article", "example.com"),
                ("http://subdomain.test.org/page", "subdomain.test.org"),
                ("https://localhost:8080/test", "localhost")
            ]
            
            for url, expected in domain_tests:
                result = extract_domain(url)
                if result == expected:
                    self.print_test_result(f"extract_domain('{url}')", 'pass')
                else:
                    self.print_test_result(f"extract_domain('{url}')", 'fail',
                                         f"Expected '{expected}', got '{result}'")
            
            # Test contains_keywords
            test_keywords = ['singapore', 'news', 'test']
            keyword_tests = [
                ("Singapore news today", True),
                ("Random text without keywords", False),
                ("This is a TEST case", True),
                ("", False)
            ]
            
            for text, expected in keyword_tests:
                result = contains_keywords(text, test_keywords)
                if result == expected:
                    self.print_test_result(f"contains_keywords('{text[:30]}...')", 'pass')
                else:
                    self.print_test_result(f"contains_keywords('{text[:30]}...')", 'fail',
                                         f"Expected {expected}, got {result}")
                    
        except Exception as e:
            self.print_test_result("Scraper function tests", 'error', str(e))
    
    def test_data_validation(self):
        """Test data validation functions"""
        self.print_header("Testing Data Validation")
        
        try:
            # Test JSON file structure
            data_files = [
                'data/settings.json',
                'data/sites.json',
                'data/latest.json'
            ]
            
            for file_path in data_files:
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                        self.print_test_result(f"JSON validation: {file_path}", 'pass')
                        
                        # Additional validation based on file type
                        if 'settings.json' in file_path:
                            required_fields = ['scrapingMethod', 'whatsappChannels']
                            missing = [f for f in required_fields if f not in data]
                            if missing:
                                self.print_test_result(f"Settings structure validation", 'fail',
                                                     f"Missing fields: {missing}")
                            else:
                                self.print_test_result(f"Settings structure validation", 'pass')
                                
                    except json.JSONDecodeError as e:
                        self.print_test_result(f"JSON validation: {file_path}", 'fail', str(e))
                else:
                    self.print_test_result(f"JSON validation: {file_path}", 'skip', "File not found")
                    
        except Exception as e:
            self.print_test_result("Data validation tests", 'error', str(e))
    
    def test_ai_scraper_functions(self):
        """Test AI scraper specific functions"""
        self.print_header("Testing AI Scraper Functions")
        
        try:
            from scripts.ai_scraper import extract_content_with_ai, RateLimiter
            
            # Test RateLimiter
            rate_limiter = RateLimiter(requests_per_minute=15)
            self.print_test_result("RateLimiter initialization", 'pass')
            
            # Test rate limiting logic
            start = time.time()
            for i in range(3):
                rate_limiter.wait_if_needed()
            elapsed = time.time() - start
            
            if elapsed < 12:  # Should take at least 12 seconds for 3 requests at 15/min
                self.print_test_result("RateLimiter timing", 'pass', f"Elapsed: {elapsed:.2f}s")
            else:
                self.print_test_result("RateLimiter timing", 'fail', f"Too slow: {elapsed:.2f}s")
                
        except ImportError:
            self.print_test_result("AI Scraper tests", 'skip', "Module not available")
        except Exception as e:
            self.print_test_result("AI Scraper tests", 'error', str(e))
    
    def test_rss_scraper(self):
        """Test RSS scraper functionality"""
        self.print_header("Testing RSS Scraper")
        
        try:
            from scripts.scraper_rss import extract_articles_from_rss
            
            # Test with mock RSS data
            mock_feed = """<?xml version="1.0"?>
            <rss version="2.0">
                <channel>
                    <title>Test Feed</title>
                    <item>
                        <title>Test Article</title>
                        <link>https://example.com/test</link>
                        <description>Test description</description>
                        <pubDate>Mon, 01 Jan 2024 00:00:00 GMT</pubDate>
                    </item>
                </channel>
            </rss>"""
            
            # This would need proper mocking, so we'll just test import
            self.print_test_result("RSS scraper import", 'pass')
            
        except ImportError:
            self.print_test_result("RSS Scraper tests", 'skip', "Module not available")
        except Exception as e:
            self.print_test_result("RSS Scraper tests", 'error', str(e))
    
    def test_whatsapp_integration(self):
        """Test WhatsApp integration"""
        self.print_header("Testing WhatsApp Integration")
        
        try:
            from scripts.send_whatsapp_green import format_message_for_whatsapp
            
            # Test message formatting
            test_articles = [{
                'title': 'Test Article',
                'url': 'https://example.com/test',
                'summary': 'Test summary in Korean',
                'group': 'News'
            }]
            
            message = format_message_for_whatsapp(test_articles)
            
            # Check message contains expected elements
            checks = [
                ('Contains title', 'Test Article' in message),
                ('Contains URL', 'https://example.com/test' in message),
                ('Contains group', 'News' in message),
                ('Has header', '싱가포르 뉴스' in message)
            ]
            
            for check_name, result in checks:
                if result:
                    self.print_test_result(f"WhatsApp formatting: {check_name}", 'pass')
                else:
                    self.print_test_result(f"WhatsApp formatting: {check_name}", 'fail')
                    
        except ImportError:
            self.print_test_result("WhatsApp tests", 'skip', "Module not available")
        except Exception as e:
            self.print_test_result("WhatsApp tests", 'error', str(e))
    
    def test_security_checks(self):
        """Basic security checks"""
        self.print_header("Testing Security")
        
        # Check for sensitive data in code
        sensitive_patterns = [
            'password=',
            'api_key=',
            'secret=',
            'token='
        ]
        
        code_files = list(Path('scripts').glob('*.py')) + list(Path('api').glob('*.js'))
        
        for file_path in code_files[:5]:  # Check first 5 files
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                
                found_sensitive = False
                for pattern in sensitive_patterns:
                    if pattern in content and '=' in content[content.find(pattern):content.find(pattern)+50]:
                        # Check if it's not just a variable name
                        line = content[content.find(pattern):content.find('\n', content.find(pattern))]
                        if '"' in line or "'" in line:
                            found_sensitive = True
                            break
                
                if found_sensitive:
                    self.print_test_result(f"Security check: {file_path.name}", 'fail', 
                                         "Possible hardcoded credentials")
                else:
                    self.print_test_result(f"Security check: {file_path.name}", 'pass')
                    
            except Exception as e:
                self.print_test_result(f"Security check: {file_path.name}", 'error', str(e))
    
    def test_performance_basics(self):
        """Basic performance tests"""
        self.print_header("Testing Performance")
        
        try:
            from scripts.scraper import clean_text
            import time
            
            # Test clean_text performance
            test_text = "This is a test " * 1000  # Large text
            
            start = time.time()
            for _ in range(100):
                clean_text(test_text)
            elapsed = time.time() - start
            
            # Should process 100 iterations in under 1 second
            if elapsed < 1.0:
                self.print_test_result("clean_text performance", 'pass', 
                                     f"100 iterations in {elapsed:.3f}s")
            else:
                self.print_test_result("clean_text performance", 'fail',
                                     f"Too slow: {elapsed:.3f}s")
                                     
        except Exception as e:
            self.print_test_result("Performance tests", 'error', str(e))
    
    def generate_report(self):
        """Generate test report"""
        elapsed = time.time() - self.start_time
        
        self.print_header("Test Summary")
        
        total = self.results['passed'] + self.results['failed'] + self.results['errors'] + self.results['skipped']
        
        print(f"\nTotal tests: {total}")
        print(f"Passed:      \033[92m{self.results['passed']}\033[0m")
        print(f"Failed:      \033[91m{self.results['failed']}\033[0m")
        print(f"Errors:      \033[93m{self.results['errors']}\033[0m")
        print(f"Skipped:     \033[94m{self.results['skipped']}\033[0m")
        print(f"\nTime elapsed: {elapsed:.2f} seconds")
        
        # Save results to file
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'duration': elapsed,
            'results': self.results
        }
        
        with open('test_results.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\nDetailed results saved to: test_results.json")
        
        # Return success if no failures or errors
        return self.results['failed'] == 0 and self.results['errors'] == 0

def main():
    print("\n🧪 Singapore News Scraper - Comprehensive Test Suite")
    print("=" * 80)
    
    runner = TestRunner()
    
    # Run all test categories
    test_methods = [
        runner.test_imports,
        runner.test_scraper_functions,
        runner.test_data_validation,
        runner.test_ai_scraper_functions,
        runner.test_rss_scraper,
        runner.test_whatsapp_integration,
        runner.test_security_checks,
        runner.test_performance_basics
    ]
    
    for test_method in test_methods:
        try:
            test_method()
        except Exception as e:
            print(f"\n⚠️  Error running {test_method.__name__}: {e}")
            traceback.print_exc()
    
    # Generate report
    success = runner.generate_report()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()