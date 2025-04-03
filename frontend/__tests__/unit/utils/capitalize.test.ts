import { capitalize } from 'utils/capitalize'

describe('capitalize function', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('capitalizes the first letter of a single lowercase word', () => {
    expect(capitalize('word')).toBe('Word')
  })

  test('does not change a single word that is already capitalized', () => {
    expect(capitalize('Word')).toBe('Word')
  })

  test('handles an empty string', () => {
    expect(capitalize('')).toBe('')
  })

  test('handles null', () => {
    expect(capitalize(null)).toBe(null)
  })

  test('handles undefined', () => {
    expect(capitalize(undefined)).toBe(undefined)
  })

  test('capitalizes a single letter', () => {
    expect(capitalize('a')).toBe('A')
  })

  test('capitalizes the first letter and keeps rest of the characters in the word', () => {
    expect(capitalize('wOrD')).toBe('WOrD')
  })

  test('handles strings with only uppercase letters', () => {
    expect(capitalize('WORD')).toBe('WORD')
  })
})
