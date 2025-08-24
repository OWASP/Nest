const LHCI_BASE_URL = process.env.LHCI_BASE_URL || 'http://localhost:3000'
const LHCI_CHROME_FLAGS =
  process.env.LHCI_CHROME_FLAGS || '--disable-dev-shm-usage --headless --no-sandbox'

const ROUTES = ['/', '/about', '/chapters', '/projects']

const getUrls = () => {
  const baseUrl = LHCI_BASE_URL.endsWith('/') ? LHCI_BASE_URL.slice(0, -1) : LHCI_BASE_URL
  return ROUTES.map((route) => `${baseUrl}${route}`)
}

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
      url: getUrls(),
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
}
