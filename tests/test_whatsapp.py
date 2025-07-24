"""
Unit tests for WhatsApp messaging functionality
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import pytz

# Import the modules to test
try:
    from scripts.send_whatsapp_green import (
        WhatsAppSender,
        format_message,
        send_to_whatsapp,
        load_scraped_data,
        should_send_message
    )
except ImportError:
    pytest.skip("WhatsApp modules not available", allow_module_level=True)

class TestWhatsAppSender:
    """Test WhatsApp sender functionality"""
    
    @pytest.fixture
    def mock_settings(self):
        """Mock WhatsApp settings"""
        return {
            'whatsappChannel': '120363419092108413@g.us',
            'whatsappApiUrl': 'https://api.green-api.com',
            'sendSchedule': {
                'period': 'daily',
                'time': '08:00'
            },
            'messageFormat': {
                'includeEmoji': True,
                'includeLinks': True,
                'maxMessageLength': 4096
            }
        }
    
    @pytest.fixture
    def mock_scraped_data(self):
        """Mock scraped data for testing"""
        return {
            'timestamp': '2025-07-24T08:00:00+09:00',
            'articles': [
                {
                    'group': 'News',
                    'articles': [
                        {
                            'title': 'Breaking News: Singapore Economy Grows',
                            'url': 'https://example.com/news/1',
                            'summary': '싱가포르 경제가 성장했습니다.',
                            'site': 'The Straits Times'
                        },
                        {
                            'title': 'New Policy Announced',
                            'url': 'https://example.com/news/2',
                            'summary': '새로운 정책이 발표되었습니다.',
                            'site': 'Channel NewsAsia'
                        }
                    ],
                    'article_count': 2
                },
                {
                    'group': 'Economy',
                    'articles': [
                        {
                            'title': 'Stock Market Update',
                            'url': 'https://example.com/economy/1',
                            'summary': '주식 시장 업데이트입니다.',
                            'site': 'Business Times'
                        }
                    ],
                    'article_count': 1
                }
            ],
            'stats': {
                'total': 3,
                'byGroup': {'News': 2, 'Economy': 1}
            }
        }
    
    @pytest.fixture
    def whatsapp_sender(self, mock_settings):
        """Create WhatsAppSender instance"""
        with patch.dict('os.environ', {'WHATSAPP_API_KEY': 'test_api_key'}):
            sender = WhatsAppSender(mock_settings)
            return sender
    
    def test_whatsapp_sender_initialization(self, mock_settings):
        """Test WhatsAppSender initialization"""
        with patch.dict('os.environ', {'WHATSAPP_API_KEY': 'test_key'}):
            sender = WhatsAppSender(mock_settings)
            assert sender.api_key == 'test_key'
            assert sender.channel_id == '120363419092108413@g.us'
            assert sender.api_url == 'https://api.green-api.com'
    
    def test_format_message_basic(self, whatsapp_sender, mock_scraped_data):
        """Test basic message formatting"""
        message = whatsapp_sender.format_message(mock_scraped_data)
        
        assert '싱가포르 뉴스 요약' in message
        assert 'News (2건)' in message
        assert 'Economy (1건)' in message
        assert '총 3개 기사' in message
        
        # Check article content
        assert 'Breaking News: Singapore Economy Grows' in message
        assert '싱가포르 경제가 성장했습니다.' in message
        assert 'https://example.com/news/1' in message
    
    def test_format_message_with_emoji(self, whatsapp_sender, mock_scraped_data):
        """Test message formatting with emoji"""
        whatsapp_sender.settings['messageFormat']['includeEmoji'] = True
        message = whatsapp_sender.format_message(mock_scraped_data)
        
        assert '📰' in message  # News emoji
        assert '💼' in message  # Economy emoji
        assert '🔗' in message  # Link emoji
    
    def test_format_message_without_links(self, whatsapp_sender, mock_scraped_data):
        """Test message formatting without links"""
        whatsapp_sender.settings['messageFormat']['includeLinks'] = False
        message = whatsapp_sender.format_message(mock_scraped_data)
        
        assert 'https://example.com' not in message
        assert '싱가포르 경제가 성장했습니다.' in message  # Summary still included
    
    def test_message_length_limit(self, whatsapp_sender):
        """Test message length limiting"""
        # Create data with many articles
        large_data = {
            'articles': [
                {
                    'group': 'News',
                    'articles': [
                        {
                            'title': f'Very Long Article Title {i}' * 10,
                            'summary': f'Very long summary content {i}' * 20,
                            'url': f'https://example.com/{i}',
                            'site': 'Test Site'
                        } for i in range(20)
                    ]
                }
            ],
            'stats': {'total': 20}
        }
        
        message = whatsapp_sender.format_message(large_data)
        
        # Should be truncated to max length
        assert len(message) <= 4096
        assert '...' in message  # Truncation indicator
    
    def test_send_to_whatsapp_success(self, whatsapp_sender):
        """Test successful WhatsApp message sending"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'sent': True, 'id': '12345'}
            mock_post.return_value = mock_response
            
            result = whatsapp_sender.send_message("Test message")
            
            assert result is True
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert 'sendMessage' in call_args[0][0]
            assert 'Test message' in str(call_args)
    
    def test_send_to_whatsapp_failure(self, whatsapp_sender):
        """Test WhatsApp message sending failure"""
        with patch('requests.post') as mock_post:
            mock_post.side_effect = Exception("Network error")
            
            result = whatsapp_sender.send_message("Test message")
            
            assert result is False
    
    def test_load_scraped_data(self, whatsapp_sender, tmp_path):
        """Test loading scraped data from file"""
        # Create test file
        test_file = tmp_path / "test_data.json"
        test_data = {'articles': [], 'stats': {'total': 0}}
        test_file.write_text(json.dumps(test_data))
        
        loaded_data = whatsapp_sender.load_scraped_data(str(test_file))
        
        assert loaded_data == test_data
    
    def test_should_send_message(self, whatsapp_sender):
        """Test message sending schedule logic"""
        with patch('datetime.datetime') as mock_datetime:
            # Test daily schedule at correct time
            mock_datetime.now.return_value = datetime(2025, 7, 24, 8, 0, 0)
            whatsapp_sender.settings['sendSchedule'] = {
                'period': 'daily',
                'time': '08:00'
            }
            assert whatsapp_sender.should_send_now() is True
            
            # Test daily schedule at wrong time
            mock_datetime.now.return_value = datetime(2025, 7, 24, 9, 0, 0)
            assert whatsapp_sender.should_send_now() is False
            
            # Test weekly schedule
            mock_datetime.now.return_value = datetime(2025, 7, 24, 8, 0, 0)  # Thursday
            mock_datetime.now.return_value.weekday.return_value = 3
            whatsapp_sender.settings['sendSchedule'] = {
                'period': 'weekly',
                'weekdays': ['mon', 'thu'],
                'time': '08:00'
            }
            assert whatsapp_sender.should_send_now() is True
    
    def test_history_tracking(self, whatsapp_sender, tmp_path):
        """Test message history tracking"""
        history_file = tmp_path / "history.json"
        
        # Send message and track
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {'sent': True}
            
            whatsapp_sender.history_file = str(history_file)
            whatsapp_sender.send_and_track("Test message", {'stats': {'total': 5}})
        
        # Check history was saved
        assert history_file.exists()
        history = json.loads(history_file.read_text())
        assert len(history) == 1
        assert history[0]['message'] == "Test message"
        assert history[0]['articles_count'] == 5
        assert history[0]['status'] == 'success'
    
    def test_duplicate_prevention(self, whatsapp_sender):
        """Test prevention of duplicate message sending"""
        with patch.object(whatsapp_sender, 'get_last_sent_timestamp') as mock_last_sent:
            # Same timestamp - should not send
            mock_last_sent.return_value = '2025-07-24T08:00:00+09:00'
            data = {'timestamp': '2025-07-24T08:00:00+09:00'}
            
            assert whatsapp_sender.should_send_data(data) is False
            
            # Different timestamp - should send
            mock_last_sent.return_value = '2025-07-24T07:00:00+09:00'
            assert whatsapp_sender.should_send_data(data) is True
    
    def test_group_emoji_mapping(self, whatsapp_sender):
        """Test emoji mapping for different groups"""
        emoji_map = whatsapp_sender.get_group_emoji()
        
        assert emoji_map['News'] == '📰'
        assert emoji_map['Economy'] == '💼'
        assert emoji_map['Technology'] == '💻'
        assert emoji_map['Politics'] == '🏛️'
        assert emoji_map['Society'] == '👥'
        assert emoji_map['Sports'] == '⚽'
        
        # Default emoji for unknown group
        assert emoji_map.get('Unknown', '📌') == '📌'
    
    def test_error_recovery(self, whatsapp_sender):
        """Test error recovery mechanisms"""
        with patch('requests.post') as mock_post:
            # First attempt fails, second succeeds
            mock_post.side_effect = [
                Exception("Network error"),
                Mock(status_code=200, json=Mock(return_value={'sent': True}))
            ]
            
            # Should retry and succeed
            result = whatsapp_sender.send_with_retry("Test message", max_retries=2)
            
            assert result is True
            assert mock_post.call_count == 2