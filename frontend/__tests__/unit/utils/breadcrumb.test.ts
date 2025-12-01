import { formatBreadcrumbTitle } from 'utils/breadcrumb'

describe('formatBreadcrumbTitle', () => {
  it('capitalizes single word', () => {
    expect(formatBreadcrumbTitle('projects')).toBe('Projects')
  })

  it('splits hyphenated slug and capitalizes each word', () => {
    expect(formatBreadcrumbTitle('test-org-repo')).toBe('Test Org Repo')
  })

  it('handles multiple hyphens', () => {
    expect(formatBreadcrumbTitle('test-multi-word-slug-example')).toBe(
      'Test Multi Word Slug Example'
    )
  })

  it('preserves uppercase words', () => {
    expect(formatBreadcrumbTitle('OWASP-ZAP')).toBe('OWASP ZAP')
  })

  it('returns empty string for empty input', () => {
    expect(formatBreadcrumbTitle('')).toBe('')
  })

  it('handles single character segments', () => {
    expect(formatBreadcrumbTitle('a-b-c')).toBe('A B C')
  })

  it('handles numbers in slug', () => {
    expect(formatBreadcrumbTitle('top-10-2021')).toBe('Top 10 2021')
  })

  it('handles trailing/leading hyphens', () => {
    expect(formatBreadcrumbTitle('-test-')).toBe(' Test ')
  })
})
