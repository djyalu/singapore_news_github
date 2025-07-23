# Singapore News Scraper Test Suite

Comprehensive testing framework for the Singapore News Scraper project.

## 📋 Overview

This test suite provides complete coverage for all components of the Singapore News Scraper:

- **Python Unit Tests**: Core scraping logic and utilities
- **JavaScript Tests**: Frontend functionality and UI components
- **API Integration Tests**: All Vercel serverless functions
- **E2E Tests**: Complete user workflows with Playwright
- **Security Tests**: Vulnerability scanning and code analysis
- **Performance Tests**: Basic performance and optimization checks

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Run All Tests

```bash
# Using the comprehensive test runner
cd tests
python run-tests.py

# Or using the shell script (Linux/macOS)
./run-tests.sh
```

### Run Specific Test Types

```bash
# Python tests only
python run-tests.py --python

# JavaScript tests only
python run-tests.py --javascript

# API integration tests
python run-tests.py --api

# E2E tests
python run-tests.py --e2e

# Security tests
python run-tests.py --security

# Performance tests
python run-tests.py --performance
```

## 📁 Directory Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest configuration and fixtures
├── requirements.txt            # Python test dependencies
├── package.json               # Node.js test dependencies
├── test-setup.js              # Jest configuration
├── playwright.config.js       # Playwright E2E configuration
├── run-tests.sh               # Shell test runner (Linux/macOS)
├── run-tests.py               # Python test runner (cross-platform)
├── README.md                  # This file
├── test_scraper.py            # Python unit tests for scraper
├── test_api_integration.py    # API integration tests
├── frontend.test.js           # JavaScript/Frontend tests
├── e2e/                       # End-to-end tests
│   ├── auth.spec.js           # Authentication flow tests
│   ├── dashboard.spec.js      # Dashboard functionality tests
│   └── scraping-workflow.spec.js # Complete workflow tests
├── reports/                   # Test result reports
├── coverage/                  # Coverage reports
│   ├── python/               # Python coverage
│   └── javascript/           # JavaScript coverage
└── test-results/             # Playwright test results
```

## 🧪 Test Categories

### 1. Python Unit Tests (`test_scraper.py`)

Tests the core Python functionality:

- **Settings and configuration loading**
- **Text processing and cleaning**
- **Article extraction and validation**
- **Date and keyword filtering**
- **Error handling and fallbacks**

```bash
# Run Python tests with coverage
python -m pytest test_scraper.py -v --cov=../scripts --cov-report=html
```

### 2. JavaScript Frontend Tests (`frontend.test.js`)

Tests client-side functionality:

- **Authentication system**
- **Data loading and caching**
- **UI interactions**
- **Error handling**
- **Local storage management**

```bash
# Run JavaScript tests
cd tests
npm test
```

### 3. API Integration Tests (`test_api_integration.py`)

Tests all Vercel API endpoints:

- **`/api/auth`** - Authentication
- **`/api/trigger-scraping`** - Workflow triggers
- **`/api/get-latest-scraped`** - Data retrieval
- **`/api/save-data`** - Configuration saving
- **`/api/test-whatsapp`** - WhatsApp testing
- **Error scenarios and edge cases**

```bash
# Run API tests
python -m pytest test_api_integration.py -v
```

### 4. E2E Tests (Playwright)

Tests complete user workflows:

- **Authentication flow** (`auth.spec.js`)
- **Dashboard functionality** (`dashboard.spec.js`)
- **Complete scraping workflow** (`scraping-workflow.spec.js`)

```bash
# Run E2E tests
npx playwright test
```

### 5. Security Tests

Automated security analysis:

- **Hardcoded secret detection**
- **Input validation checks**
- **CORS policy validation**
- **Authentication bypass attempts**

### 6. Performance Tests

Basic performance analysis:

- **Large file detection**
- **Blocking operation detection**
- **Memory usage patterns**
- **API response times**

## 📊 Test Reports and Coverage

### Coverage Reports

After running tests, coverage reports are generated:

- **Python**: `tests/coverage/python/index.html`
- **JavaScript**: `tests/coverage/javascript/lcov-report/index.html`

### Test Results

- **JUnit XML**: `tests/reports/*.xml`
- **HTML Reports**: `tests/reports/*.html` 
- **JSON Summary**: `tests/reports/test-summary-*.json`

### Viewing Reports

```bash
# Open Python coverage report
open tests/coverage/python/index.html

# Open JavaScript coverage report
open tests/coverage/javascript/lcov-report/index.html

# Open Playwright test report
npx playwright show-report
```

## 🔧 Configuration

### Pytest Configuration (`conftest.py`)

Provides fixtures for:
- Mock settings and sites
- Sample article data
- Temporary directories
- HTTP request mocking
- Environment setup

### Jest Configuration (`test-setup.js`)

Configures:
- JSDOM environment
- Fetch mocking
- LocalStorage/SessionStorage mocking
- Console mocking for cleaner output

### Playwright Configuration (`playwright.config.js`)

Configures:
- Multiple browser testing (Chrome, Firefox, Safari)
- Mobile device testing
- Screenshot/video capture on failure
- Parallel test execution

## 🚀 CI/CD Integration

### GitHub Actions (`.github/workflows/test.yml`)

The test suite integrates with GitHub Actions for:

- **Multi-version testing**: Python 3.8-3.11, Node.js 16-20
- **Parallel execution**: All test types run in parallel
- **Artifact collection**: Test reports and coverage data
- **PR comments**: Automated test result summaries
- **Security scanning**: Integrated with Bandit and Semgrep

### Workflow Triggers

- **Push to main/develop**: Full test suite
- **Pull requests**: Full test suite with PR comments
- **Manual trigger**: On-demand testing
- **Nightly**: Comprehensive test suite

## 🛠️ Development Workflow

### Adding New Tests

1. **Python tests**: Add to `test_scraper.py` or create new `test_*.py` files
2. **JavaScript tests**: Add to `frontend.test.js` or create `*.test.js` files
3. **API tests**: Add to `test_api_integration.py`
4. **E2E tests**: Add to `e2e/*.spec.js`

### Test Data and Fixtures

Use the provided fixtures in `conftest.py`:

```python
def test_article_processing(sample_article, mock_settings):
    # Your test code here
    assert sample_article['title']
    assert mock_settings['scrapingMethod']
```

### Mocking External Services

```python
# Mock HTTP requests
@patch('requests.get')
def test_api_call(mock_get):
    mock_get.return_value.json.return_value = {'success': True}
    # Test code
```

```javascript
// Mock fetch in JavaScript
fetch.mockResponseOnce(JSON.stringify({ success: true }));
```

## 📈 Test Metrics and Quality Gates

### Coverage Targets

- **Python**: 80% line coverage
- **JavaScript**: 75% line coverage
- **API Integration**: 90% endpoint coverage

### Quality Gates

Tests must pass the following criteria:

- All unit tests pass
- Coverage meets minimum thresholds
- No security vulnerabilities detected
- E2E tests pass on Chrome and Firefox
- API integration tests pass
- Code quality checks pass (linting, formatting)

## 🐛 Troubleshooting

### Common Issues

1. **Python import errors**:
   ```bash
   export PYTHONPATH="$PWD:$PWD/scripts:$PYTHONPATH"
   ```

2. **Node.js dependency issues**:
   ```bash
   cd tests
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Playwright browser issues**:
   ```bash
   npx playwright install --with-deps
   ```

4. **Permission denied on scripts**:
   ```bash
   chmod +x run-tests.sh run-tests.py
   ```

### Debug Mode

Enable verbose output:

```bash
# Python tests with debug output
python -m pytest -v -s --tb=long

# JavaScript tests with debug output
npm test -- --verbose

# E2E tests with debug output
npx playwright test --debug
```

## 📞 Support

For issues or questions about the test suite:

1. Check this documentation
2. Review test logs and error messages
3. Check [GitHub Actions](https://github.com/djyalu/singapore_news_github/actions) for CI failures
4. Create an issue on the GitHub repository

## 🤝 Contributing

When contributing to the test suite:

1. Add tests for new functionality
2. Maintain or improve coverage
3. Update documentation
4. Ensure all tests pass locally before submitting PR
5. Follow the existing test patterns and conventions