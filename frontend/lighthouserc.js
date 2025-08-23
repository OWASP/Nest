const LHCI_CHROME_FLAGS =
  process.env.LHCI_CHROME_FLAGS || '--disable-dev-shm-usage --headless --no-sandbox'
const LHCI_OUTPUT_DIR = process.env.LHCI_OUTPUT_DIR || '.lighthouseci/'
const LHCI_UPLOAD_TARGET = process.env.LHCI_UPLOAD_TARGET || 'filesystem'
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
      outputDir: LHCI_OUTPUT_DIR,
      reportFilenamePattern: '%%DATETIME%%-%%HOSTNAME%%%%PATHNAME%%.%%EXTENSION%%',
      target: LHCI_UPLOAD_TARGET,
    },
  },
}
