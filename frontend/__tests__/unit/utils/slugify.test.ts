import slugify from 'utils/slugify'

describe('slugify', () => {
  test.each([
    ['accents and diacritics', 'Héllo Wörld Cañón', 'hello-world-canon'],
    ['basic English text', 'Hello World', 'hello-world'],
    ['collapse multiple spaces and symbols', 'one    two    --    three', 'one-two-three'],
    ['empty string', '', ''],
    ['extra spaces', '   Hello   World   ', 'hello-world'],
    ['leading and trailing hyphens', '---Hello World---', 'hello-world'],
    ['lowercase all letters', 'This Should BE Lowercase', 'this-should-be-lowercase'],
    ['multiple special characters together', 'Hello---World___Test!!!', 'hello-world-test'],
    ['no multiple consecutive hyphens', 'Hello     ---   World', 'hello-world'],
    ['numbers correctly', 'Project 2025 Version 2.0', 'project-2025-version-2-0'],
    ['only accented characters', 'éàëîôû', 'eaeiou'],
    ['only symbols', '*** $$$ ###', ''],
    ['special characters', 'Hello @ World #2025!', 'hello-world-2025'],
  ])('should handle %s', (_description, input, expected) => {
    expect(slugify(input)).toBe(expected)
  })
})
