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

  it('preserves hyphens between consecutive numbers', () => {
    expect(formatBreadcrumbTitle('snapshots-2025-09')).toBe('Snapshots 2025-09')
  })

  it('preserves hyphens in number sequences', () => {
    expect(formatBreadcrumbTitle('report-1-2-3')).toBe('Report 1 2 3')
  })

  it('handles mixed words and date formats', () => {
    expect(formatBreadcrumbTitle('report-2024-12-summary')).toBe('Report 2024-12 Summary')
  })
})
