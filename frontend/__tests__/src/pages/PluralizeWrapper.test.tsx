import { pluralize } from 'utils/pluralize'

describe('pluralize function', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('returns empty string for count = 1 with default "s"', () => {
    expect(pluralize(1)).toBe('')
  })

  test('returns "s" for count > 1 or count = 0  with default "s"', () => {
    expect(pluralize(0)).toBe('s')
    expect(pluralize(2)).toBe('s')
    expect(pluralize(5)).toBe('s')
  })

  test('handles singular and plural forms correctly', () => {
    expect(pluralize(1, 'star,stars')).toBe('star')
    expect(pluralize(2, 'star,stars')).toBe('stars')
    expect(pluralize(5, 'fork,forks')).toBe('forks')
  })

  test('returns plural form when count is 0 or falsy', () => {
    expect(pluralize(0, 'issue,issues')).toBe('issues')
    expect(pluralize(null, 'count,counts')).toBe('counts')
    expect(pluralize(undefined, 'issue,issues')).toBe('issues')
  })

  test('handles non-standard pluralization correctly', () => {
    expect(pluralize(1, 'person,people')).toBe('person')
    expect(pluralize(2, 'person,people')).toBe('people')
  })

  test('handles incorrect inputs gracefully', () => {
    expect(pluralize(1, '')).toBe('')
    expect(pluralize(1, ',')).toBe('')
    expect(pluralize(2, ',')).toBe('')
    expect(pluralize(1, 'word')).toBe('')
    expect(pluralize(2, 'word')).toBe('word')
  })
})
