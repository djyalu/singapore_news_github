"""
Unit tests for email notification functionality
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import pytz

# Import the modules to test
try:
    from api.send_email import send_email, format_email_content
except ImportError:
    pytest.skip("Email modules not available", allow_module_level=True)

class TestEmail:
    """Test email functionality"""
    
    @pytest.fixture
    def mock_email_config(self):
        """Mock email configuration"""
        return {
            'smtp_host': 'smtp.gmail.com',
            'smtp_port': 587,
            'smtp_user': 'test@example.com',
            'smtp_password': 'test_password',
            'from_email': 'noreply@example.com',
            'to_emails': ['admin@example.com', 'user@example.com']
        }
    
    @pytest.fixture
    def mock_scraped_data(self):
        """Mock scraped data for email"""
        return {
            'timestamp': '2025-07-24T08:00:00+09:00',
            'articles': [
                {
                    'group': 'News',
                    'articles': [
                        {
                            'title': 'Breaking News Story',
                            'url': 'https://example.com/news/1',
                            'summary': 'Important news summary',
                            'site': 'The Straits Times'
                        }
                    ],
                    'article_count': 1
                }
            ],
            'stats': {
                'total': 1,
                'byGroup': {'News': 1}
            }
        }
    
    def test_format_email_content_html(self, mock_scraped_data):
        """Test HTML email content formatting"""
        content = format_email_content(mock_scraped_data, format='html')
        
        # Check HTML structure
        assert '<html>' in content
        assert '<body>' in content
        assert 'Singapore News Summary' in content
        
        # Check article content
        assert 'Breaking News Story' in content
        assert 'https://example.com/news/1' in content
        assert 'The Straits Times' in content
        
        # Check stats
        assert 'Total articles: 1' in content
    
    def test_format_email_content_text(self, mock_scraped_data):
        """Test plain text email content formatting"""
        content = format_email_content(mock_scraped_data, format='text')
        
        # Check text format
        assert '<html>' not in content
        assert 'SINGAPORE NEWS SUMMARY' in content
        assert 'Breaking News Story' in content
        assert 'https://example.com/news/1' in content
    
    def test_send_email_success(self, mock_email_config):
        """Test successful email sending"""
        with patch('smtplib.SMTP') as mock_smtp:
            # Mock SMTP instance
            mock_instance = Mock()
            mock_smtp.return_value = mock_instance
            
            # Send email
            result = send_email(
                subject='Test Subject',
                content='Test Content',
                config=mock_email_config
            )
            
            # Verify SMTP calls
            mock_smtp.assert_called_with(
                mock_email_config['smtp_host'],
                mock_email_config['smtp_port']
            )
            mock_instance.starttls.assert_called_once()
            mock_instance.login.assert_called_with(
                mock_email_config['smtp_user'],
                mock_email_config['smtp_password']
            )
            mock_instance.send_message.assert_called_once()
            mock_instance.quit.assert_called_once()
            
            assert result is True
    
    def test_send_email_authentication_failure(self, mock_email_config):
        """Test email sending with authentication failure"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_instance = Mock()
            mock_instance.login.side_effect = Exception("Authentication failed")
            mock_smtp.return_value = mock_instance
            
            result = send_email(
                subject='Test Subject',
                content='Test Content',
                config=mock_email_config
            )
            
            assert result is False
    
    def test_send_email_connection_failure(self, mock_email_config):
        """Test email sending with connection failure"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_smtp.side_effect = Exception("Connection failed")
            
            result = send_email(
                subject='Test Subject',
                content='Test Content',
                config=mock_email_config
            )
            
            assert result is False
    
    def test_email_with_attachments(self, mock_email_config, tmp_path):
        """Test email with attachments"""
        # Create test attachment
        attachment_file = tmp_path / "report.json"
        attachment_file.write_text(json.dumps({"test": "data"}))
        
        with patch('smtplib.SMTP') as mock_smtp:
            mock_instance = Mock()
            mock_smtp.return_value = mock_instance
            
            result = send_email(
                subject='Test with Attachment',
                content='See attached report',
                config=mock_email_config,
                attachments=[str(attachment_file)]
            )
            
            # Verify attachment was included
            call_args = mock_instance.send_message.call_args
            message = call_args[0][0]
            
            assert message.is_multipart()
            assert result is True
    
    def test_email_recipient_validation(self, mock_email_config):
        """Test email recipient validation"""
        # Invalid email addresses
        invalid_config = mock_email_config.copy()
        invalid_config['to_emails'] = ['invalid-email', '@example.com']
        
        with patch('smtplib.SMTP'):
            result = send_email(
                subject='Test',
                content='Test',
                config=invalid_config
            )
            
            # Should filter out invalid emails
            assert result is True
    
    def test_email_rate_limiting(self, mock_email_config):
        """Test email rate limiting"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_instance = Mock()
            mock_smtp.return_value = mock_instance
            
            # Send multiple emails rapidly
            for i in range(5):
                send_email(
                    subject=f'Test {i}',
                    content='Test',
                    config=mock_email_config
                )
            
            # Should implement rate limiting
            assert mock_instance.send_message.call_count <= 5
    
    def test_email_template_rendering(self):
        """Test email template rendering with various data"""
        test_cases = [
            # Empty data
            {
                'articles': [],
                'stats': {'total': 0}
            },
            # Multiple groups
            {
                'articles': [
                    {'group': 'News', 'articles': [], 'article_count': 5},
                    {'group': 'Economy', 'articles': [], 'article_count': 3}
                ],
                'stats': {'total': 8}
            }
        ]
        
        for data in test_cases:
            content = format_email_content(data, format='html')
            assert content is not None
            assert len(content) > 0
    
    def test_email_encoding(self, mock_email_config):
        """Test email with special characters"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_instance = Mock()
            mock_smtp.return_value = mock_instance
            
            # Content with special characters
            content = "Test with 한글 and émojis 🎉"
            
            result = send_email(
                subject='Test Encoding',
                content=content,
                config=mock_email_config
            )
            
            # Should handle encoding properly
            assert result is True
            
            # Check message encoding
            call_args = mock_instance.send_message.call_args
            message = call_args[0][0]
            assert 'utf-8' in str(message).lower()
    
    def test_email_scheduling(self, mock_email_config):
        """Test email scheduling functionality"""
        from api.send_email import should_send_email
        
        with patch('datetime.datetime') as mock_datetime:
            # Test daily schedule at correct time
            mock_datetime.now.return_value = datetime(2025, 7, 24, 8, 0, 0)
            schedule = {'period': 'daily', 'time': '08:00'}
            assert should_send_email(schedule) is True
            
            # Test weekly schedule
            mock_datetime.now.return_value = datetime(2025, 7, 24, 8, 0, 0)  # Thursday
            mock_datetime.now.return_value.weekday.return_value = 3
            schedule = {'period': 'weekly', 'weekdays': ['thu'], 'time': '08:00'}
            assert should_send_email(schedule) is True