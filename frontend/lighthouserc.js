module.exports = {
  ci: {
    assert: {
      assertions: {
        'categories:accessibility': ['warn', { minScore: 0.9 }],
        'categories:best-practices': ['warn', { minScore: 0.9 }],
        'categories:performance': ['warn', { minScore: 0.9 }],
        'categories:seo': ['warn', { minScore: 0.9 }],
      },
    },
    collect: {
      numberOfRuns: 3,
      settings: {
        chromeFlags: '--disable-dev-shm-usage --headless --no-sandbox',
      },
      url: ['http://localhost:3000/'],
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
}
