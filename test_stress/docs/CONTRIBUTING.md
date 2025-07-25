# Contributing Guide / 기여 가이드

## Table of Contents / 목차
1. [Welcome / 환영합니다](#welcome--환영합니다)
2. [Code of Conduct / 행동 강령](#code-of-conduct--행동-강령)
3. [Getting Started / 시작하기](#getting-started--시작하기)
4. [Development Setup / 개발 환경 설정](#development-setup--개발-환경-설정)
5. [How to Contribute / 기여 방법](#how-to-contribute--기여-방법)
6. [Coding Standards / 코딩 표준](#coding-standards--코딩-표준)
7. [Testing Guidelines / 테스트 가이드라인](#testing-guidelines--테스트-가이드라인)
8. [Documentation / 문서화](#documentation--문서화)
9. [Pull Request Process / PR 프로세스](#pull-request-process--pr-프로세스)
10. [Community / 커뮤니티](#community--커뮤니티)

## Welcome / 환영합니다

Thank you for considering contributing to Singapore News Scraper! We welcome contributions from everyone, regardless of experience level. This guide will help you get started.

싱가포르 뉴스 스크래퍼에 기여를 고려해 주셔서 감사합니다! 경험 수준에 관계없이 모든 사람의 기여를 환영합니다. 이 가이드가 시작하는 데 도움이 될 것입니다.

### Why Contribute? / 왜 기여하나요?
- 🌟 Improve news accessibility for Korean speakers
- 🚀 Learn new technologies and best practices
- 🤝 Join a welcoming community
- 📈 Build your portfolio

## Code of Conduct / 행동 강령

### Our Pledge / 우리의 약속
We pledge to make participation in our project a harassment-free experience for everyone, regardless of:
- Age / 나이
- Body size / 체형
- Disability / 장애
- Ethnicity / 민족성
- Gender identity / 성 정체성
- Experience level / 경험 수준
- Nationality / 국적
- Personal appearance / 외모
- Race / 인종
- Religion / 종교
- Sexual identity and orientation / 성적 정체성과 지향

### Expected Behavior / 기대되는 행동
- 🤝 Be respectful and inclusive
- 💬 Use welcoming language
- 🎯 Focus on constructive criticism
- 👂 Listen to different viewpoints
- 🙏 Show empathy towards others

### Unacceptable Behavior / 용납되지 않는 행동
- ❌ Harassment or discrimination
- ❌ Trolling or insulting comments
- ❌ Personal or political attacks
- ❌ Public or private harassment
- ❌ Publishing others' private information

## Getting Started / 시작하기

### Prerequisites / 사전 요구사항
```bash
# Required tools
git --version      # Git 2.30+
node --version     # Node.js 16+
python --version   # Python 3.8+
npm --version      # npm 7+

# Recommended tools
code --version     # VS Code
gh --version       # GitHub CLI
```

### First Steps / 첫 단계
1. **Read the documentation** / 문서 읽기
   - [README.md](../README.md)
   - [ARCHITECTURE.md](ARCHITECTURE.md)
   - [API_REFERENCE.md](API_REFERENCE.md)

2. **Explore the codebase** / 코드베이스 탐색
   ```bash
   # Clone the repository
   git clone https://github.com/djyalu/singapore_news_github.git
   cd singapore_news_github
   
   # Explore structure
   tree -L 2 -I 'node_modules|cache|logs'
   ```

3. **Find an issue to work on** / 작업할 이슈 찾기
   - Check [Issues](https://github.com/djyalu/singapore_news_github/issues)
   - Look for `good first issue` labels
   - Ask in discussions if unsure

## Development Setup / 개발 환경 설정

### 1. Fork and Clone / 포크 및 클론
```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR_USERNAME/singapore_news_github.git
cd singapore_news_github

# Add upstream remote
git remote add upstream https://github.com/djyalu/singapore_news_github.git
git fetch upstream
```

### 2. Install Dependencies / 의존성 설치
```bash
# Python dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Node.js dependencies (if needed for local development)
npm install
```

### 3. Environment Setup / 환경 설정
```bash
# Create .env file for local development
cp .env.example .env

# Edit .env with your test credentials
# DO NOT use production credentials
```

### 4. Local Development Server / 로컬 개발 서버
```bash
# For frontend development
python -m http.server 8000
# Visit http://localhost:8000

# For API development (using Vercel CLI)
npm install -g vercel
vercel dev
```

### 5. VS Code Setup / VS Code 설정
```json
// .vscode/settings.json
{
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.fixAll.eslint": true
    },
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "[python]": {
        "editor.rulers": [88]
    },
    "[javascript]": {
        "editor.rulers": [100]
    }
}
```

## How to Contribute / 기여 방법

### Types of Contributions / 기여 유형

#### 1. Bug Reports / 버그 신고
```markdown
<!-- Bug report template -->
## Description
Clear description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Windows 11]
- Browser: [e.g., Chrome 120]
- Version: [e.g., 1.5.0]

## Screenshots
If applicable
```

#### 2. Feature Requests / 기능 요청
```markdown
<!-- Feature request template -->
## Problem Statement
What problem does this solve?

## Proposed Solution
How would you solve it?

## Alternatives Considered
Other solutions you've thought about

## Additional Context
Any other information
```

#### 3. Code Contributions / 코드 기여
- 🐛 Bug fixes
- ✨ New features
- 🎨 UI improvements
- ⚡ Performance optimizations
- 📝 Documentation updates
- 🧪 Test additions

#### 4. Translations / 번역
Help translate the UI or documentation to other languages

#### 5. Design Contributions / 디자인 기여
- UI/UX improvements
- Icons and graphics
- Color schemes
- Accessibility enhancements

### Contribution Workflow / 기여 워크플로우
```
1. Find/Create Issue
      │
      ▼
2. Fork Repository
      │
      ▼
3. Create Branch
      │
      ▼
4. Make Changes
      │
      ▼
5. Test Thoroughly
      │
      ▼
6. Commit Changes
      │
      ▼
7. Push to Fork
      │
      ▼
8. Create Pull Request
      │
      ▼
9. Code Review
      │
      ▼
10. Merge
```

## Coding Standards / 코딩 표준

### JavaScript Standards
```javascript
// ✅ Good
const processArticles = async (articles) => {
    // Use const/let, not var
    const processed = [];
    
    // Use meaningful variable names
    for (const article of articles) {
        // Handle errors properly
        try {
            const result = await processArticle(article);
            processed.push(result);
        } catch (error) {
            console.error(`Failed to process article: ${article.id}`, error);
        }
    }
    
    return processed;
};

// ❌ Bad
function process(a) {
    var p = [];
    for (var i = 0; i < a.length; i++) {
        p.push(processArticle(a[i]));
    }
    return p;
}
```

### Python Standards
```python
# ✅ Good
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class NewsScraper:
    """Scrapes news from Singapore websites."""
    
    def __init__(self, config: Dict[str, any]) -> None:
        """Initialize scraper with configuration.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self._session = None
    
    def scrape_site(self, site_url: str) -> List[Dict[str, str]]:
        """Scrape articles from a single site.
        
        Args:
            site_url: URL of the news site
            
        Returns:
            List of article dictionaries
            
        Raises:
            ScrapingError: If scraping fails
        """
        try:
            # Implementation here
            pass
        except Exception as e:
            logger.error(f"Failed to scrape {site_url}: {e}")
            raise ScrapingError(f"Scraping failed: {e}") from e

# ❌ Bad
def scrape(url):
    # no docstring
    # no type hints
    # poor error handling
    try:
        # scrape stuff
        pass
    except:
        print("error")
```

### CSS Standards
```css
/* ✅ Good */
/* Component: Article Card */
.article-card {
    /* Layout */
    display: flex;
    flex-direction: column;
    
    /* Spacing */
    padding: 1rem;
    margin-bottom: 1rem;
    
    /* Visual */
    background-color: var(--card-bg);
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    
    /* Animation */
    transition: transform 0.2s ease;
}

.article-card:hover {
    transform: translateY(-2px);
}

/* ❌ Bad */
.card {
    display: flex; padding: 10px; background: white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.card:hover { transform: translateY(-2px) }
```

### Git Commit Standards
```bash
# ✅ Good commit messages
feat: add RSS feed support for Mothership
fix: resolve timezone display issue in dashboard
docs: update API documentation for v1.5.0
style: format code according to Black
refactor: extract scraping logic into separate module
test: add unit tests for article validation
chore: update dependencies to latest versions

# ❌ Bad commit messages
fixed stuff
WIP
update
changes
```

### Branch Naming
```bash
# ✅ Good branch names
feature/add-telegram-support
fix/whatsapp-encoding-issue
docs/update-api-reference
refactor/scraping-engine
chore/update-dependencies

# ❌ Bad branch names
patch-1
myfeature
test
fix
```

## Testing Guidelines / 테스트 가이드라인

### Unit Tests / 단위 테스트
```python
# tests/test_scraper.py
import pytest
from scripts.scraper import extract_article_content

class TestScraper:
    """Test cases for scraper module."""
    
    def test_extract_article_content_valid_html(self):
        """Test extraction with valid HTML."""
        html = '<article><h1>Title</h1><p>Content</p></article>'
        result = extract_article_content(html)
        
        assert result['title'] == 'Title'
        assert result['content'] == 'Content'
    
    def test_extract_article_content_missing_title(self):
        """Test extraction with missing title."""
        html = '<article><p>Content only</p></article>'
        
        with pytest.raises(ValueError, match="Title not found"):
            extract_article_content(html)
    
    @pytest.mark.parametrize("html,expected", [
        ('<h1>Test</h1>', {'title': 'Test', 'content': ''}),
        ('<p>Test</p>', {'title': '', 'content': 'Test'}),
    ])
    def test_extract_various_formats(self, html, expected):
        """Test extraction with various HTML formats."""
        result = extract_article_content(html)
        assert result == expected
```

### Integration Tests / 통합 테스트
```javascript
// tests/api.test.js
const assert = require('assert');
const fetch = require('node-fetch');

describe('API Integration Tests', () => {
    const API_BASE = process.env.TEST_API_URL || 'http://localhost:3000';
    
    describe('GET /api/get-latest-scraped', () => {
        it('should return scraped articles', async () => {
            const response = await fetch(`${API_BASE}/api/get-latest-scraped`);
            const data = await response.json();
            
            assert.strictEqual(response.status, 200);
            assert.strictEqual(data.success, true);
            assert(Array.isArray(data.data.articles));
        });
        
        it('should filter by group', async () => {
            const response = await fetch(`${API_BASE}/api/get-latest-scraped?group=tech`);
            const data = await response.json();
            
            assert.strictEqual(response.status, 200);
            data.data.articles.forEach(article => {
                assert.strictEqual(article.group, 'tech');
            });
        });
    });
});
```

### End-to-End Tests / E2E 테스트
```javascript
// tests/e2e/dashboard.spec.js
describe('Dashboard E2E Tests', () => {
    beforeEach(() => {
        cy.visit('/');
    });
    
    it('should display login form', () => {
        cy.get('#login-form').should('be.visible');
        cy.get('#username').should('exist');
        cy.get('#password').should('exist');
    });
    
    it('should login successfully', () => {
        cy.get('#username').type('admin');
        cy.get('#password').type('Admin@123');
        cy.get('#login-button').click();
        
        cy.get('#dashboard').should('be.visible');
        cy.get('#login-form').should('not.exist');
    });
    
    it('should display articles after login', () => {
        // Login first
        cy.login('admin', 'Admin@123');
        
        // Check articles
        cy.get('.article-card').should('have.length.greaterThan', 0);
        cy.get('.article-card').first().within(() => {
            cy.get('.article-title').should('exist');
            cy.get('.article-summary').should('exist');
        });
    });
});
```

### Test Coverage Requirements / 테스트 커버리지 요구사항
```yaml
Minimum Coverage:
  - Statements: 80%
  - Branches: 70%
  - Functions: 80%
  - Lines: 80%

Critical Paths (100% coverage required):
  - Authentication
  - API endpoints
  - Data validation
  - Error handling
```

## Documentation / 문서화

### Code Documentation / 코드 문서화
```javascript
/**
 * Processes scraped articles and generates summaries.
 * 
 * @async
 * @function processArticles
 * @param {Article[]} articles - Array of article objects
 * @param {Object} options - Processing options
 * @param {string} options.method - Processing method ('ai' | 'traditional')
 * @param {number} options.maxLength - Maximum summary length
 * @returns {Promise<ProcessedArticle[]>} Processed articles with summaries
 * @throws {ProcessingError} If processing fails
 * 
 * @example
 * const processed = await processArticles(articles, {
 *     method: 'ai',
 *     maxLength: 200
 * });
 */
async function processArticles(articles, options = {}) {
    // Implementation
}
```

### API Documentation / API 문서화
```yaml
# OpenAPI 3.0 specification
/api/trigger-scraping:
  post:
    summary: Trigger news scraping workflow
    description: |
      Initiates the scraping process for all enabled news sites.
      This endpoint triggers a GitHub Action workflow.
    tags:
      - Scraping
    requestBody:
      required: false
      content:
        application/json:
          schema:
            type: object
            properties:
              method:
                type: string
                enum: [traditional, ai, hybrid_ai]
                default: hybrid_ai
              sites:
                type: array
                items:
                  type: string
    responses:
      '200':
        description: Scraping initiated successfully
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SuccessResponse'
```

### README Updates / README 업데이트
When adding new features, update:
1. Feature list
2. Installation steps (if needed)
3. Configuration options
4. Usage examples
5. API endpoints (if applicable)

## Pull Request Process / PR 프로세스

### 1. Before Creating PR / PR 생성 전
```bash
# Update from upstream
git fetch upstream
git rebase upstream/main

# Run tests
npm test
python -m pytest

# Check code style
npm run lint
black scripts/
pylint scripts/

# Build project
npm run build
```

### 2. PR Template / PR 템플릿
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change
- [ ] Documentation update

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added/updated
- [ ] All tests passing

## Screenshots (if applicable)
Before | After

## Related Issues
Fixes #123
```

### 3. Code Review Process / 코드 리뷰 프로세스
```
1. Automated checks run
   - Tests
   - Linting
   - Security scan
   
2. Peer review
   - At least 1 approver required
   - Address all comments
   
3. Final checks
   - Merge conflicts resolved
   - CI/CD passing
   
4. Merge
   - Squash and merge for features
   - Merge commit for large changes
```

### 4. After Merge / 머지 후
- Delete your feature branch
- Update your local main branch
- Close related issues
- Update documentation if needed

## Community / 커뮤니티

### Communication Channels / 소통 채널
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Requests**: Code contributions
- **Email**: admin@example.com (for sensitive matters)

### Getting Help / 도움 받기
```markdown
When asking for help:
1. Search existing issues/discussions
2. Provide context and error messages
3. Share relevant code snippets
4. Describe what you've tried
5. Be patient and respectful
```

### Recognition / 인정
We value all contributions! Contributors are:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Given credit in commit messages
- Eligible for contributor badges

### Meetups and Events / 모임 및 이벤트
- Monthly virtual contributor meetup
- Annual hackathon
- Conference talks and workshops

## Resources / 자료

### Learning Resources / 학습 자료
- [Python Best Practices](https://docs.python-guide.org/)
- [JavaScript MDN Docs](https://developer.mozilla.org/)
- [Git Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)

### Project-Specific Resources / 프로젝트 특정 자료
- [Architecture Overview](ARCHITECTURE.md)
- [API Documentation](API_REFERENCE.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Security Guidelines](SECURITY_GUIDE.md)

### Tools and Extensions / 도구 및 확장
```json
// Recommended VS Code extensions
{
    "recommendations": [
        "dbaeumer.vscode-eslint",
        "ms-python.python",
        "ms-python.vscode-pylance",
        "esbenp.prettier-vscode",
        "eamodio.gitlens",
        "github.copilot",
        "ms-azuretools.vscode-docker"
    ]
}
```

---
*Thank you for contributing to Singapore News Scraper!*

*싱가포르 뉴스 스크래퍼에 기여해 주셔서 감사합니다!*

*Last Updated: January 25, 2025*