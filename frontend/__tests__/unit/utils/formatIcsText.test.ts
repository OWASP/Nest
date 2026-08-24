import formatIcsText from 'utils/formatIcsText'

describe('formatIcsText', () => {
  it('escapes ICS special characters in event titles', () => {
    expect(formatIcsText('OWASP Global AppSec EU 2026 - Vienna, Austria')).toBe(
      'OWASP Global AppSec EU 2026 - Vienna\\, Austria'
    )
    expect(formatIcsText('Event; with special, chars\\and\nnewlines')).toBe(
      'Event\\; with special\\, chars\\\\and\\nnewlines'
    )
  })
})
