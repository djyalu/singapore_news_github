"""
Singapore News Scraper Test Suite

This package contains all tests for the Singapore News Scraper project.
"""

import os
import sys

# Add parent directory to Python path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'scripts'))

# Test suite version
__version__ = '1.0.0'

# Test categories
TEST_CATEGORIES = {
    'unit': 'Unit tests for individual components',
    'integration': 'Integration tests for API endpoints',
    'e2e': 'End-to-end tests for complete workflows',
    'performance': 'Performance and load tests',
    'security': 'Security vulnerability tests'
}