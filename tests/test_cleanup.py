"""
Unit tests for data cleanup functionality
"""
import pytest
import json
import os
from datetime import datetime, timedelta
import pytz
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the modules to test
try:
    from scripts.cleanup_old_data import (
        cleanup_old_scraped_files,
        get_file_age_days,
        format_file_size,
        should_delete_file
    )
except ImportError:
    pytest.skip("Cleanup modules not available", allow_module_level=True)

class TestCleanup:
    """Test data cleanup functionality"""
    
    @pytest.fixture
    def temp_scraped_dir(self, tmp_path):
        """Create temporary scraped directory with test files"""
        scraped_dir = tmp_path / "data" / "scraped"
        scraped_dir.mkdir(parents=True)
        
        # Create test files with different ages
        kst = pytz.timezone('Asia/Seoul')
        now = datetime.now(kst)
        
        # Old file (35 days)
        old_file = scraped_dir / "news_20250619_120000.json"
        old_file.write_text(json.dumps({
            "timestamp": (now - timedelta(days=35)).isoformat(),
            "articles": []
        }))
        
        # Recent file (5 days)
        recent_file = scraped_dir / "news_20250719_120000.json"
        recent_file.write_text(json.dumps({
            "timestamp": (now - timedelta(days=5)).isoformat(),
            "articles": []
        }))
        
        # Current file (today)
        current_file = scraped_dir / "news_20250724_120000.json"
        current_file.write_text(json.dumps({
            "timestamp": now.isoformat(),
            "articles": []
        }))
        
        return scraped_dir
    
    def test_get_file_age_days(self, temp_scraped_dir):
        """Test file age calculation"""
        # Create a file with known modification time
        test_file = temp_scraped_dir / "test.json"
        test_file.write_text("{}")
        
        # Get age
        age = get_file_age_days(str(test_file))
        
        # Should be 0 days (just created)
        assert age >= 0
        assert age < 1
    
    def test_format_file_size(self):
        """Test file size formatting"""
        assert format_file_size(0) == "0 B"
        assert format_file_size(1023) == "1023 B"
        assert format_file_size(1024) == "1.00 KB"
        assert format_file_size(1024 * 1024) == "1.00 MB"
        assert format_file_size(1024 * 1024 * 1024) == "1.00 GB"
        assert format_file_size(1536 * 1024) == "1.50 MB"
    
    def test_should_delete_file(self, temp_scraped_dir):
        """Test file deletion criteria"""
        # Old JSON file - should delete
        old_file = temp_scraped_dir / "news_20250619_120000.json"
        old_file.write_text("{}")
        
        # Mock file age
        with patch('scripts.cleanup_old_data.get_file_age_days') as mock_age:
            mock_age.return_value = 35
            assert should_delete_file(str(old_file), retention_days=30) is True
            
            mock_age.return_value = 25
            assert should_delete_file(str(old_file), retention_days=30) is False
        
        # Non-JSON file - should not delete
        other_file = temp_scraped_dir / "test.txt"
        other_file.write_text("test")
        assert should_delete_file(str(other_file), retention_days=30) is False
    
    def test_cleanup_old_scraped_files(self, temp_scraped_dir):
        """Test cleanup of old scraped files"""
        # Create files
        old_files = []
        for i in range(5):
            old_file = temp_scraped_dir / f"news_2025061{i}_120000.json"
            old_file.write_text(json.dumps({"articles": []}))
            old_files.append(old_file)
        
        recent_file = temp_scraped_dir / "news_20250723_120000.json"
        recent_file.write_text(json.dumps({"articles": []}))
        
        # Mock file ages
        with patch('scripts.cleanup_old_data.get_file_age_days') as mock_age:
            def age_side_effect(filepath):
                if "202506" in filepath:  # Old files
                    return 35
                return 1  # Recent file
            
            mock_age.side_effect = age_side_effect
            
            # Run cleanup
            stats = cleanup_old_scraped_files(
                str(temp_scraped_dir.parent),
                retention_days=30,
                dry_run=False
            )
            
            # Check results
            assert stats['deleted_count'] == 5
            assert stats['kept_count'] == 1
            assert stats['total_size_deleted'] > 0
            
            # Verify old files are deleted
            for old_file in old_files:
                assert not old_file.exists()
            
            # Verify recent file is kept
            assert recent_file.exists()
    
    def test_cleanup_dry_run(self, temp_scraped_dir):
        """Test cleanup in dry run mode"""
        # Create an old file
        old_file = temp_scraped_dir / "news_20250619_120000.json"
        old_file.write_text(json.dumps({"articles": []}))
        
        with patch('scripts.cleanup_old_data.get_file_age_days') as mock_age:
            mock_age.return_value = 35
            
            # Run cleanup in dry run mode
            stats = cleanup_old_scraped_files(
                str(temp_scraped_dir.parent),
                retention_days=30,
                dry_run=True
            )
            
            # Should report deletion but not actually delete
            assert stats['deleted_count'] == 1
            assert old_file.exists()  # File should still exist
    
    def test_cleanup_size_limit(self, temp_scraped_dir):
        """Test cleanup with size limit"""
        # Create multiple large files
        for i in range(10):
            large_file = temp_scraped_dir / f"news_2025061{i}_120000.json"
            # Create 5MB file
            large_content = {"data": "x" * (5 * 1024 * 1024)}
            large_file.write_text(json.dumps(large_content))
        
        with patch('scripts.cleanup_old_data.get_file_age_days') as mock_age:
            mock_age.return_value = 35
            
            # Run cleanup with 20MB limit
            stats = cleanup_old_scraped_files(
                str(temp_scraped_dir.parent),
                retention_days=30,
                max_size_mb=20,
                dry_run=False
            )
            
            # Should delete only up to size limit
            assert stats['total_size_deleted'] <= 20 * 1024 * 1024
            assert stats['deleted_count'] < 10  # Not all files deleted
    
    def test_cleanup_error_handling(self, temp_scraped_dir):
        """Test error handling during cleanup"""
        # Create a file
        test_file = temp_scraped_dir / "news_20250619_120000.json"
        test_file.write_text("{}")
        
        with patch('scripts.cleanup_old_data.get_file_age_days') as mock_age:
            mock_age.return_value = 35
            
            # Mock os.remove to raise exception
            with patch('os.remove') as mock_remove:
                mock_remove.side_effect = PermissionError("Access denied")
                
                # Should handle error gracefully
                stats = cleanup_old_scraped_files(
                    str(temp_scraped_dir.parent),
                    retention_days=30,
                    dry_run=False
                )
                
                # File should still exist due to error
                assert test_file.exists()
                assert stats['errors'] > 0
    
    def test_cleanup_latest_file_protection(self, temp_scraped_dir):
        """Test that latest.json is never deleted"""
        # Create latest.json file
        latest_file = temp_scraped_dir.parent / "latest.json"
        latest_file.write_text(json.dumps({
            "lastUpdated": "2025-06-01T00:00:00+09:00"  # Old timestamp
        }))
        
        with patch('scripts.cleanup_old_data.get_file_age_days') as mock_age:
            mock_age.return_value = 100  # Very old
            
            # Run cleanup
            cleanup_old_scraped_files(
                str(temp_scraped_dir.parent),
                retention_days=30,
                dry_run=False
            )
            
            # latest.json should never be deleted
            assert latest_file.exists()
    
    def test_cleanup_directory_structure(self, temp_scraped_dir):
        """Test cleanup preserves directory structure"""
        # Create subdirectories
        subdir = temp_scraped_dir / "2025" / "07"
        subdir.mkdir(parents=True)
        
        # Add files to subdirectory
        old_file = subdir / "news_20250619_120000.json"
        old_file.write_text("{}")
        
        with patch('scripts.cleanup_old_data.get_file_age_days') as mock_age:
            mock_age.return_value = 35
            
            # Run cleanup
            cleanup_old_scraped_files(
                str(temp_scraped_dir.parent),
                retention_days=30,
                dry_run=False
            )
            
            # Directory structure should remain
            assert subdir.exists()
            assert temp_scraped_dir.exists()