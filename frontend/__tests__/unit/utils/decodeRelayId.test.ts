import { decodeRelayId } from 'utils/decodeRelayId'

describe('decodeRelayId', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('parses plain integer strings directly', () => {
    expect(decodeRelayId('42')).toBe(42)
    expect(decodeRelayId('100')).toBe(100)
    expect(decodeRelayId('0')).toBe(0)
  })

  test('decodes base64-encoded Relay global IDs', () => {
    const projectGlobalId = btoa('ProjectType:42')
    expect(decodeRelayId(projectGlobalId)).toBe(42)

    const chapterGlobalId = btoa('ChapterType:789')
    expect(decodeRelayId(chapterGlobalId)).toBe(789)
  })

  test('extracts numbers via fallback regex when string is not valid base64 but has digits', () => {
    expect(decodeRelayId('invalid-id-999!!!')).toBe(999)
  })

  test('returns 0 when string contains no digits and cannot be decoded', () => {
    expect(decodeRelayId('no-digits-here!')).toBe(0)
    expect(decodeRelayId('')).toBe(0)
  })
})
