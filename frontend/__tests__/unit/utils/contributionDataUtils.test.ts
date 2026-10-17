import { contributionCount } from 'utils/contributionDataUtils'

describe('contributionCount', () => {
  test('returns 0 when contributions are missing', () => {
    expect(contributionCount(undefined, 'london', 'www-chapter-')).toBe(0)
  })

  test('uses a bare chapter key when present', () => {
    expect(contributionCount({ london: 4 }, 'london', 'www-chapter-')).toBe(4)
  })

  test('falls back from a bare chapter key to the prefixed map key', () => {
    expect(contributionCount({ 'www-chapter-london': 7 }, 'london', 'www-chapter-')).toBe(7)
  })

  test('falls back from a prefixed chapter key to the bare map key', () => {
    expect(contributionCount({ london: 3 }, 'www-chapter-london', 'www-chapter-')).toBe(3)
  })

  test('uses a bare project key when present', () => {
    expect(contributionCount({ nest: 12 }, 'nest', 'www-project-')).toBe(12)
  })

  test('falls back from a bare project key to the prefixed map key', () => {
    expect(contributionCount({ 'www-project-nest': 9 }, 'nest', 'www-project-')).toBe(9)
  })

  test('falls back from a prefixed project key to the bare map key', () => {
    expect(contributionCount({ nest: 5 }, 'www-project-nest', 'www-project-')).toBe(5)
  })

  test('returns 0 when neither key form is present', () => {
    expect(contributionCount({ other: 1 }, 'nest', 'www-project-')).toBe(0)
  })

  test('prefers the exact key over the alternate form', () => {
    expect(contributionCount({ nest: 2, 'www-project-nest': 8 }, 'nest', 'www-project-')).toBe(2)
  })

  test('ignores inherited Object.prototype properties on the alternate key', () => {
    expect(contributionCount({}, 'www-project-toString', 'www-project-')).toBe(0)
  })
})
