import slugify from 'utils/slugify'

describe('slugify', () => {
  test('should convert basic English text to a slug', () => {
    expect(slugify('Hello World')).toBe('hello-world')
  })

  test('should handle extra spaces', () => {
    expect(slugify('   Hello   World   ')).toBe('hello-world')
  })

  test('should replace special characters with hyphens', () => {
    expect(slugify('Hello @ World #2025!')).toBe('hello-world-2025')
  })

  test('should handle multiple special characters together', () => {
    expect(slugify('Hello---World___Test!!!')).toBe('hello-world-test')
  })

  test('should remove accents and diacritics', () => {
    expect(slugify('Héllo Wörld Cañón')).toBe('hello-world-canon')
  })

  test('should trim leading and trailing hyphens', () => {
    expect(slugify('---Hello World---')).toBe('hello-world')
  })

  test('should handle numbers correctly', () => {
    expect(slugify('Project 2025 Version 2.0')).toBe('project-2025-version-2-0')
  })

  test('should collapse multiple spaces and symbols into one hyphen', () => {
    expect(slugify('one    two    --    three')).toBe('one-two-three')
  })

  test('should return an empty string when given only symbols', () => {
    expect(slugify('*** $$$ ###')).toBe('')
  })

  test('should return an empty string when given an empty string', () => {
    expect(slugify('')).toBe('')
  })

  test('should lowercase all letters', () => {
    expect(slugify('This Should BE Lowercase')).toBe('this-should-be-lowercase')
  })

  test('should handle strings with only accented characters', () => {
    expect(slugify('éàëîôû')).toBe('eaeiou')
  })

  test('should not have multiple consecutive hyphens', () => {
    expect(slugify('Hello     ---   World')).toBe('hello-world')
  })
})
