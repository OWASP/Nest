import { pluralize } from 'utils/pluralize'

describe('pluralize function', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('handles singular and plural forms correctly', () => {
    expect(pluralize(1, 'star')).toBe('star')
    expect(pluralize(2, 'star', 'stars')).toBe('stars')
    expect(pluralize(5, 'fork')).toBe('forks')
  })

  test('returns plural form when count is 0 or falsy', () => {
    expect(pluralize(0, 'issue', 'issues')).toBe('issues')
    expect(pluralize(null, 'count')).toBe('counts')
    expect(pluralize(undefined, 'issue', 'issues')).toBe('issues')
  })

  test('handles non-standard pluralization correctly', () => {
    expect(pluralize(1, 'person', 'people')).toBe('person')
    expect(pluralize(2, 'person', 'people')).toBe('people')
  })
})
