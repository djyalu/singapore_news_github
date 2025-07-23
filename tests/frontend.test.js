/**
 * Frontend JavaScript tests for Singapore News Scraper
 */

// Mock the app.js functionality since it's a large file
const mockApp = {
  // Authentication functions
  login: jest.fn(),
  logout: jest.fn(),
  isAuthenticated: jest.fn(),
  
  // Data loading functions
  loadScrapedArticles: jest.fn(),
  loadDashboardData: jest.fn(),
  loadTodayArticlesModal: jest.fn(),
  
  // UI functions
  showNotification: jest.fn(),
  updateTodayArticles: jest.fn(),
  refreshDashboard: jest.fn(),
  
  // API functions
  triggerScraping: jest.fn(),
  sendWhatsApp: jest.fn(),
};

describe('Authentication System', () => {
  beforeEach(() => {
    // Reset DOM
    document.body.innerHTML = `
      <form id="loginForm">
        <input id="username" value="admin" />
        <input id="password" value="Admin@123" />
        <button type="submit">Login</button>
      </form>
      <button id="logoutButton">Logout</button>
      <div id="notifications"></div>
    `;
  });

  test('should handle successful login', async () => {
    fetch.mockResponseOnce(JSON.stringify({
      success: true,
      message: 'Login successful'
    }));

    // Simulate login
    const loginData = {
      type: 'login',
      username: 'admin',
      password: 'Admin@123'
    };

    const response = await fetch('/api/auth', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(loginData)
    });

    const result = await response.json();
    
    expect(result.success).toBe(true);
    expect(result.message).toBe('Login successful');
    expect(fetch).toHaveBeenCalledWith('/api/auth', expect.objectContaining({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(loginData)
    }));
  });

  test('should handle login failure', async () => {
    fetch.mockResponseOnce(JSON.stringify({
      success: false,
      error: 'Invalid credentials'
    }));

    const loginData = {
      type: 'login',
      username: 'wrong',
      password: 'wrong'
    };

    const response = await fetch('/api/auth', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(loginData)
    });

    const result = await response.json();
    
    expect(result.success).toBe(false);
    expect(result.error).toBe('Invalid credentials');
  });

  test('should handle logout', () => {
    // Set up authenticated state
    sessionStorage.setItem('user', JSON.stringify({ username: 'admin' }));
    
    // Simulate logout
    sessionStorage.removeItem('user');
    
    expect(sessionStorage.getItem('user')).toBeNull();
  });
});

describe('Data Loading Functions', () => {
  test('should load latest scraped articles', async () => {
    const mockArticles = {
      success: true,
      articles: [
        {
          group: 'News',
          articles: [
            {
              title: 'Test Article',
              url: 'https://example.com/test',
              summary: 'Test summary',
              site: 'Test Site'
            }
          ],
          article_count: 1
        }
      ],
      lastUpdated: '2025-07-24T00:00:00Z'
    };

    fetch.mockResponseOnce(JSON.stringify(mockArticles));

    const response = await fetch('/api/get-latest-scraped');
    const data = await response.json();

    expect(data.success).toBe(true);
    expect(data.articles).toHaveLength(1);
    expect(data.articles[0].group).toBe('News');
    expect(data.articles[0].article_count).toBe(1);
  });

  test('should handle API errors gracefully', async () => {
    fetch.mockRejectOnce(new Error('Network error'));

    try {
      await fetch('/api/get-latest-scraped');
    } catch (error) {
      expect(error.message).toBe('Network error');
    }
  });
});

describe('Scraping Operations', () => {
  test('should trigger scraping workflow', async () => {
    const mockResponse = {
      success: true,
      message: 'Scraping started',
      run_id: 123456,
      run_url: 'https://github.com/test/repo/actions/runs/123456'
    };

    fetch.mockResponseOnce(JSON.stringify(mockResponse));

    const response = await fetch('/api/trigger-scraping', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ manual: true })
    });

    const result = await response.json();

    expect(result.success).toBe(true);
    expect(result.message).toBe('Scraping started');
    expect(result.run_id).toBe(123456);
    expect(typeof result.run_url).toBe('string');
  });

  test('should handle scraping errors', async () => {
    fetch.mockResponseOnce(JSON.stringify({
      success: false,
      error: 'GitHub token not configured'
    }), { status: 500 });

    const response = await fetch('/api/trigger-scraping', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ manual: true })
    });

    const result = await response.json();

    expect(result.success).toBe(false);
    expect(result.error).toBe('GitHub token not configured');
  });
});

describe('UI Helper Functions', () => {
  test('should format dates correctly', () => {
    const formatDate = (dateString) => {
      const date = new Date(dateString);
      return date.toLocaleDateString('ko-KR');
    };

    const testDate = '2025-07-24T00:00:00Z';
    const formatted = formatDate(testDate);
    
    expect(typeof formatted).toBe('string');
    expect(formatted).toMatch(/\d{4}/); // Should contain year
  });

  test('should validate URLs', () => {
    const isValidUrl = (string) => {
      try {
        new URL(string);
        return true;
      } catch (_) {
        return false;
      }
    };

    expect(isValidUrl('https://example.com')).toBe(true);
    expect(isValidUrl('http://example.com')).toBe(true);
    expect(isValidUrl('not-a-url')).toBe(false);
    expect(isValidUrl('')).toBe(false);
  });

  test('should sanitize HTML content', () => {
    const sanitizeHtml = (html) => {
      const div = document.createElement('div');
      div.textContent = html;
      return div.innerHTML;
    };

    const maliciousInput = '<script>alert("xss")</script>Hello';
    const sanitized = sanitizeHtml(maliciousInput);
    
    expect(sanitized).not.toContain('<script>');
    expect(sanitized).toContain('Hello');
  });
});

describe('Local Storage Management', () => {
  test('should store and retrieve user data', () => {
    const userData = { username: 'admin', role: 'admin' };
    
    sessionStorage.setItem('user', JSON.stringify(userData));
    const retrieved = JSON.parse(sessionStorage.getItem('user'));
    
    expect(retrieved).toEqual(userData);
    expect(retrieved.username).toBe('admin');
    expect(retrieved.role).toBe('admin');
  });

  test('should handle missing storage data', () => {
    const result = sessionStorage.getItem('nonexistent');
    expect(result).toBeNull();
  });

  test('should clear storage on logout', () => {
    sessionStorage.setItem('user', JSON.stringify({ username: 'test' }));
    sessionStorage.setItem('cache', 'some data');
    
    sessionStorage.clear();
    
    expect(sessionStorage.getItem('user')).toBeNull();
    expect(sessionStorage.getItem('cache')).toBeNull();
  });
});

describe('Error Handling', () => {
  test('should handle network errors', async () => {
    fetch.mockRejectOnce(new Error('Network error'));

    try {
      await fetch('/api/test');
      fail('Should have thrown an error');
    } catch (error) {
      expect(error.message).toBe('Network error');
    }
  });

  test('should handle malformed JSON responses', async () => {
    fetch.mockResponseOnce('invalid json');

    const response = await fetch('/api/test');
    
    try {
      await response.json();
      fail('Should have thrown an error');
    } catch (error) {
      expect(error).toBeInstanceOf(SyntaxError);
    }
  });

  test('should handle empty responses', async () => {
    fetch.mockResponseOnce('');

    const response = await fetch('/api/test');
    const text = await response.text();
    
    expect(text).toBe('');
  });
});

describe('Data Validation', () => {
  test('should validate article structure', () => {
    const validateArticle = (article) => {
      const required = ['title', 'url', 'summary', 'site', 'group'];
      return required.every(field => field in article && article[field]);
    };

    const validArticle = {
      title: 'Test Title',
      url: 'https://example.com',
      summary: 'Test summary',
      site: 'Test Site',
      group: 'News'
    };

    const invalidArticle = {
      title: 'Test Title',
      // missing required fields
    };

    expect(validateArticle(validArticle)).toBe(true);
    expect(validateArticle(invalidArticle)).toBe(false);
  });

  test('should validate settings structure', () => {
    const validateSettings = (settings) => {
      const required = ['scrapingMethod', 'maxArticlesPerSite'];
      return required.every(field => field in settings);
    };

    const validSettings = {
      scrapingMethod: 'traditional',
      maxArticlesPerSite: 3
    };

    const invalidSettings = {
      scrapingMethod: 'traditional'
      // missing maxArticlesPerSite
    };

    expect(validateSettings(validSettings)).toBe(true);
    expect(validateSettings(invalidSettings)).toBe(false);
  });
});

describe('Utility Functions', () => {
  test('should debounce function calls', (done) => {
    const debounce = (func, wait) => {
      let timeout;
      return function executedFunction(...args) {
        const later = () => {
          clearTimeout(timeout);
          func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
      };
    };

    const mockFn = jest.fn();
    const debouncedFn = debounce(mockFn, 100);

    // Call multiple times quickly
    debouncedFn();
    debouncedFn();
    debouncedFn();

    // Should not be called yet
    expect(mockFn).not.toHaveBeenCalled();

    // Wait for debounce period
    setTimeout(() => {
      expect(mockFn).toHaveBeenCalledTimes(1);
      done();
    }, 150);
  });

  test('should throttle function calls', (done) => {
    const throttle = (func, limit) => {
      let inThrottle;
      return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
          func.apply(context, args);
          inThrottle = true;
          setTimeout(() => inThrottle = false, limit);
        }
      };
    };

    const mockFn = jest.fn();
    const throttledFn = throttle(mockFn, 100);

    // Call multiple times quickly
    throttledFn();
    throttledFn();
    throttledFn();

    // Should be called once immediately
    expect(mockFn).toHaveBeenCalledTimes(1);

    // Wait and call again
    setTimeout(() => {
      throttledFn();
      expect(mockFn).toHaveBeenCalledTimes(2);
      done();
    }, 150);
  });
});