import { isValidSearchQuery } from 'utils/helpers/searchHelpers'

describe('isValidSearchQuery', () => {
  test.each(['hello', 'hello world', 'my-project_1', 'a b c'])('accepts %j', (query) => {
    expect(isValidSearchQuery(query)).toBe(true)
  })

  test.each([
    ['tab', 'hello\tworld'],
    ['newline', 'hello\nworld'],
    ['non-breaking space', 'hello\u00a0world'],
    ['special characters', 'React.JS'],
    ['plus signs', 'C++'],
    ['empty string', ''],
  ])('rejects %s', (_label, query) => {
    expect(isValidSearchQuery(query)).toBe(false)
  })
})
