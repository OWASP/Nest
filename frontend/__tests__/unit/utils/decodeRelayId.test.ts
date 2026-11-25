import { decodeRelayId, tryDecodeRelayId } from 'utils/decodeRelayId'

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

  test('throws when the string is not valid base64, even if it contains digits', () => {
    expect(() => decodeRelayId('invalid-id-999!!!')).toThrow('Invalid Relay ID')
    expect(() => decodeRelayId('42abc')).toThrow('Invalid Relay ID')
  })

  test('throws when the string contains no digits and cannot be decoded', () => {
    expect(() => decodeRelayId('no-digits-here!')).toThrow('Invalid Relay ID')
    expect(() => decodeRelayId('')).toThrow('Invalid Relay ID')
  })

  test('throws for a valid base64 Relay ID with a non-numeric payload', () => {
    expect(() => decodeRelayId(btoa('ProjectType:abc'))).toThrow('Invalid Relay ID')
  })

  test('throws for valid base64 that is not in Type:id format', () => {
    expect(() => decodeRelayId(btoa('1234'))).toThrow('Invalid Relay ID')
  })
})

describe('tryDecodeRelayId', () => {
  test('returns the decoded ID for valid input', () => {
    expect(tryDecodeRelayId('7')).toBe(7)
    expect(tryDecodeRelayId(btoa('SnapshotSubscriptionNode:12'))).toBe(12)
  })

  test('returns null instead of throwing for invalid input', () => {
    expect(tryDecodeRelayId('invalid-id-999!!!')).toBeNull()
    expect(tryDecodeRelayId(btoa('ProjectType:abc'))).toBeNull()
    expect(tryDecodeRelayId('')).toBeNull()
  })
})
