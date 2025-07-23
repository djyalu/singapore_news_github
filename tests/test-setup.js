/**
 * Jest test setup for Singapore News Scraper
 */
import '@testing-library/jest-dom';
import 'jest-fetch-mock';

// Enable fetch mocking
global.fetch = require('jest-fetch-mock');

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock sessionStorage
const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.sessionStorage = sessionStorageMock;

// Mock console methods to reduce noise in tests
global.console = {
  ...console,
  log: jest.fn(),
  debug: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
};

// Mock window.location
delete window.location;
window.location = {
  href: 'http://localhost',
  origin: 'http://localhost',
  protocol: 'http:',
  host: 'localhost',
  hostname: 'localhost',
  port: '',
  pathname: '/',
  search: '',
  hash: '',
  reload: jest.fn(),
  replace: jest.fn(),
  assign: jest.fn(),
};

// Mock Chart.js
global.Chart = {
  register: jest.fn(),
  Chart: jest.fn().mockImplementation(() => ({
    destroy: jest.fn(),
    update: jest.fn(),
    render: jest.fn(),
  })),
};

// Setup DOM
document.body.innerHTML = `
  <div id="app">
    <div id="todayArticles">0</div>
    <div id="articlesList"></div>
    <div id="latestScrapedArticles"></div>
    <div id="scrapedArticlesList"></div>
    <div id="historyList"></div>
    <div id="statusIndicator"></div>
    <div id="loadingSpinner" style="display: none;"></div>
    <button id="scrapButton">스크랩</button>
    <button id="sendButton">전송</button>
    <button id="loginButton">로그인</button>
    <button id="logoutButton">로그아웃</button>
    <form id="loginForm">
      <input id="username" type="text" />
      <input id="password" type="password" />
    </form>
    <div id="notifications"></div>
  </div>
`;

// Mock API responses
const mockApiResponses = {
  '/api/get-latest-scraped': {
    success: true,
    articles: [
      {
        group: 'News',
        articles: [
          {
            title: 'Test Article',
            url: 'https://example.com/test',
            summary: 'Test summary',
            site: 'Test Site',
            group: 'News',
          }
        ],
        article_count: 1,
      }
    ],
    lastUpdated: '2025-07-24T00:00:00Z',
    articleCount: 1,
  },
  '/api/auth': {
    success: true,
    message: 'Authentication successful',
  },
  '/api/trigger-scraping': {
    success: true,
    message: 'Scraping started',
    run_id: 123456,
  },
};

// Setup fetch mock defaults
beforeEach(() => {
  fetch.resetMocks();
  localStorage.clear();
  sessionStorage.clear();
  
  // Default fetch mock
  fetch.mockResponse((req) => {
    const url = new URL(req.url).pathname;
    const response = mockApiResponses[url];
    
    if (response) {
      return Promise.resolve(JSON.stringify(response));
    }
    
    return Promise.reject(new Error(`No mock response for ${url}`));
  });
});

// Cleanup after each test
afterEach(() => {
  jest.clearAllMocks();
  document.body.innerHTML = '';
});