/**
 * Jest configuration for Singapore News Scraper
 */

module.exports = {
  // Test environment
  testEnvironment: 'jsdom',
  
  // Setup files
  setupFilesAfterEnv: ['<rootDir>/test-setup.js'],
  
  // Module directories
  moduleDirectories: ['node_modules', '../js'],
  
  // Root directory
  rootDir: '.',
  
  // Test match patterns
  testMatch: [
    '**/__tests__/**/*.js',
    '**/?(*.)+(spec|test).js'
  ],
  
  // Coverage configuration
  collectCoverage: false, // Enable with --coverage flag
  collectCoverageFrom: [
    '../js/**/*.js',
    '../api/**/*.js',
    '!../js/**/*.min.js',
    '!../api/test-*.js',
    '!**/node_modules/**',
    '!**/vendor/**'
  ],
  
  // Coverage thresholds
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 75,
      lines: 75,
      statements: 75
    }
  },
  
  // Coverage reporters
  coverageReporters: [
    'text',
    'text-summary',
    'lcov',
    'html',
    'json',
    'cobertura'
  ],
  
  // Coverage directory
  coverageDirectory: '<rootDir>/coverage/javascript',
  
  // Transform files
  transform: {
    '^.+\\.js$': '<rootDir>/jest-transform.js'
  },
  
  // Ignore patterns
  testPathIgnorePatterns: [
    '/node_modules/',
    '/e2e/',
    '/.git/',
    '/coverage/'
  ],
  
  // Module file extensions
  moduleFileExtensions: ['js', 'json'],
  
  // Verbose output
  verbose: true,
  
  // Clear mocks between tests
  clearMocks: true,
  resetMocks: true,
  restoreMocks: true,
  
  // Test timeout
  testTimeout: 10000,
  
  // Reporters
  reporters: [
    'default',
    ['jest-junit', {
      outputDirectory: '<rootDir>/reports',
      outputName: 'jest-results.xml',
      classNameTemplate: '{classname}',
      titleTemplate: '{title}',
      ancestorSeparator: ' › ',
      usePathForSuiteName: 'true'
    }]
  ],
  
  // Global variables
  globals: {
    'API_BASE_URL': 'https://singapore-news-scraper.vercel.app',
    'TESTING': true
  },
  
  // Module name mapper for aliases
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/../$1',
    '^@js/(.*)$': '<rootDir>/../js/$1',
    '^@api/(.*)$': '<rootDir>/../api/$1'
  },
  
  // Bail on first test failure
  bail: false,
  
  // Error on deprecated APIs
  errorOnDeprecated: true,
  
  // Notify on completion
  notify: false,
  
  // Watch plugins
  watchPlugins: [
    'jest-watch-typeahead/filename',
    'jest-watch-typeahead/testname'
  ]
};