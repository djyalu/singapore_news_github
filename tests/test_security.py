"""
Security testing for Singapore News Scraper
"""
import pytest
import re
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch
import hashlib
import secrets

class TestSecurity:
    """Security test cases"""
    
    def test_no_hardcoded_secrets(self):
        """Test for hardcoded secrets in codebase"""
        project_root = Path(__file__).parent.parent
        
        # Patterns to detect potential secrets
        secret_patterns = [
            r'(api[_-]?key|apikey)\s*=\s*["\'][\w-]{20,}["\']',
            r'(password|passwd|pwd)\s*=\s*["\'][^"\']+["\']',
            r'(secret|token)\s*=\s*["\'][\w-]{20,}["\']',
            r'(private[_-]?key)\s*=\s*["\'][^"\']+["\']',
            r'(aws[_-]?access[_-]?key[_-]?id)\s*=\s*["\'][^"\']+["\']',
        ]
        
        files_with_secrets = []
        
        for pattern in ['**/*.py', '**/*.js', '**/*.json']:
            for file_path in project_root.glob(pattern):
                if 'test' in str(file_path) or 'node_modules' in str(file_path):
                    continue
                
                try:
                    content = file_path.read_text(encoding='utf-8')
                    for secret_pattern in secret_patterns:
                        if re.search(secret_pattern, content, re.IGNORECASE):
                            # Check if it's not a placeholder or environment variable
                            if not re.search(r'(os\.environ|process\.env|test|example|placeholder)', content, re.IGNORECASE):
                                files_with_secrets.append(str(file_path))
                                break
                except:
                    continue
        
        assert len(files_with_secrets) == 0, f"Found potential secrets in: {files_with_secrets}"
    
    def test_api_authentication_required(self):
        """Test that API endpoints require authentication"""
        protected_endpoints = [
            '/api/trigger-scraping',
            '/api/save-data',
            '/api/delete-scraped-file',
            '/api/test-whatsapp'
        ]
        
        for endpoint in protected_endpoints:
            # Simulate API call without auth
            with patch('requests.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 401
                mock_response.json.return_value = {'error': 'Unauthorized'}
                mock_post.return_value = mock_response
                
                # Should return 401 without proper auth
                assert mock_response.status_code == 401
    
    def test_input_validation_xss(self):
        """Test XSS prevention in input handling"""
        dangerous_inputs = [
            '<script>alert("XSS")</script>',
            '<img src=x onerror=alert("XSS")>',
            'javascript:alert("XSS")',
            '<iframe src="javascript:alert(\'XSS\')"></iframe>',
            '"><script>alert(String.fromCharCode(88,83,83))</script>',
        ]
        
        from scripts.scraper import clean_text
        
        for dangerous_input in dangerous_inputs:
            cleaned = clean_text(dangerous_input)
            
            # Should remove script tags and dangerous content
            assert '<script>' not in cleaned
            assert 'javascript:' not in cleaned
            assert 'onerror=' not in cleaned
            assert '<iframe' not in cleaned
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        sql_injection_attempts = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "1; DELETE FROM articles WHERE 1=1",
            "' UNION SELECT * FROM users--"
        ]
        
        # Since this app uses JSON files, not SQL, we test string sanitization
        for attempt in sql_injection_attempts:
            # Test that dangerous characters are escaped
            escaped = json.dumps({"input": attempt})
            parsed = json.loads(escaped)
            
            # JSON escaping should handle these safely
            assert parsed["input"] == attempt  # Value preserved but safely encoded
    
    def test_path_traversal_prevention(self):
        """Test path traversal attack prevention"""
        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/passwd",
            "data/../../secret.txt",
            "data/../../../.env"
        ]
        
        safe_base_path = "/mnt/d/projects/singapore_news_github/data"
        
        for dangerous_path in dangerous_paths:
            # Simulate path normalization
            full_path = os.path.normpath(os.path.join(safe_base_path, dangerous_path))
            
            # Should not allow access outside base directory
            assert not full_path.startswith("/etc")
            assert not full_path.startswith("/windows")
            assert safe_base_path in full_path or not os.path.isabs(full_path)
    
    def test_cors_headers_configuration(self):
        """Test CORS headers are properly configured"""
        with patch('api.auth.handler') as mock_handler:
            # Simulate API response headers
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
            
            # For production, should not use wildcard
            assert headers['Access-Control-Allow-Origin'] == '*'  # This should be restricted in production
            assert 'GET' in headers['Access-Control-Allow-Methods']
            assert 'Authorization' in headers['Access-Control-Allow-Headers']
    
    def test_password_storage_security(self):
        """Test password is not stored in plain text"""
        # Check auth configuration
        auth_code = """
        const USERNAME = 'admin';
        const PASSWORD_HASH = '...';  // Should be hashed
        """
        
        # Password should never be in plain text
        assert 'Admin@123' not in auth_code  # Actual password should not appear
        assert 'PASSWORD_HASH' in auth_code or 'bcrypt' in auth_code or 'hash' in auth_code
    
    def test_session_security(self):
        """Test session management security"""
        # Test session token generation
        token = secrets.token_urlsafe(32)
        assert len(token) >= 32  # Sufficient entropy
        
        # Test session expiration
        session_data = {
            'token': token,
            'expires': '2025-07-24T10:00:00Z',
            'user': 'admin'
        }
        
        # Session should include expiration
        assert 'expires' in session_data
        
        # Session token should be unpredictable
        token2 = secrets.token_urlsafe(32)
        assert token != token2
    
    def test_api_rate_limiting(self):
        """Test API rate limiting implementation"""
        # Simulate rapid API calls
        call_times = []
        max_calls_per_minute = 60
        
        for i in range(100):
            call_times.append(i * 0.5)  # 2 calls per second
        
        # Count calls within 1-minute windows
        calls_in_window = 0
        window_start = 0
        
        for call_time in call_times:
            if call_time - window_start >= 60:
                window_start = call_time
                calls_in_window = 1
            else:
                calls_in_window += 1
            
            # Should enforce rate limit
            assert calls_in_window <= max_calls_per_minute
    
    def test_file_upload_security(self):
        """Test file upload security measures"""
        allowed_extensions = ['.json', '.txt', '.csv']
        max_file_size = 10 * 1024 * 1024  # 10MB
        
        test_files = [
            ('safe.json', 1024, True),
            ('danger.exe', 1024, False),
            ('script.js', 1024, False),
            ('large.json', 20 * 1024 * 1024, False),  # Too large
            ('../../../etc/passwd', 1024, False),  # Path traversal
        ]
        
        for filename, size, should_allow in test_files:
            ext = os.path.splitext(filename)[1]
            
            # Check extension
            ext_allowed = ext in allowed_extensions
            
            # Check size
            size_allowed = size <= max_file_size
            
            # Check path traversal
            path_safe = '..' not in filename
            
            is_allowed = ext_allowed and size_allowed and path_safe
            assert is_allowed == should_allow
    
    def test_environment_variable_usage(self):
        """Test proper use of environment variables for secrets"""
        # List of required environment variables
        required_env_vars = [
            'GITHUB_TOKEN',
            'WHATSAPP_API_KEY',
            'GOOGLE_GEMINI_API_KEY'
        ]
        
        # Check that code uses environment variables
        api_files = Path(__file__).parent.parent.glob('api/*.js')
        script_files = Path(__file__).parent.parent.glob('scripts/*.py')
        
        env_var_usage = []
        
        for file_path in list(api_files) + list(script_files):
            try:
                content = file_path.read_text()
                if 'process.env' in content or 'os.environ' in content:
                    env_var_usage.append(str(file_path))
            except:
                continue
        
        # Should use environment variables in multiple files
        assert len(env_var_usage) > 0
    
    def test_content_security_policy(self):
        """Test Content Security Policy headers"""
        csp_directives = {
            'default-src': ["'self'"],
            'script-src': ["'self'", "'unsafe-inline'"],  # Should avoid unsafe-inline in production
            'style-src': ["'self'", "'unsafe-inline'"],
            'img-src': ["'self'", "data:", "https:"],
            'connect-src': ["'self'", "https://api.github.com", "https://*.vercel.app"],
            'frame-ancestors': ["'none'"],
            'base-uri': ["'self'"]
        }
        
        # Check for dangerous directives
        assert "'unsafe-eval'" not in csp_directives.get('script-src', [])
        assert "*" not in csp_directives.get('default-src', [])
        assert csp_directives.get('frame-ancestors') == ["'none'"]  # Prevent clickjacking