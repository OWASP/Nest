const LHCI_CHROME_FLAGS =
  process.env.LHCI_CHROME_FLAGS || '--disable-dev-shm-usage --headless --no-sandbox'
const LHCI_URL = process.env.LHCI_URL || 'http://localhost:3000/'

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
        chromeFlags: LHCI_CHROME_FLAGS,
      },
      url: [LHCI_URL],
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
}
