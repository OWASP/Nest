const LHCI_BASE_URL = process.env.LHCI_BASE_URL || 'http://localhost:3000'
const LHCI_CHROME_FLAGS =
  process.env.LHCI_CHROME_FLAGS || '--disable-dev-shm-usage --headless --no-sandbox'

const URL_PATHS = [
  '/',
  '/about',
  '/chapters',
  '/community/snapshots',
  '/contribute',
  '/members',
  '/organizations',
  '/projects',
]

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
      numberOfRuns: 1,
      settings: {
        chromeFlags: LHCI_CHROME_FLAGS,
      },
      url: URL_PATHS.map((url_path) => `${LHCI_BASE_URL}${url_path}`),
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
}
