import getGoogleCalendarUrl from 'utils/getGoogleCalendarUrl'

describe('getGoogleCalendarUrl', () => {
  describe('date format detection', () => {
    it('detects all-day event from midnight timestamp', () => {
      const url = getGoogleCalendarUrl({
        title: 'Conference',
        startDate: 1764547200, // 2025-12-01T00:00:00Z
        endDate: 1764720000, // 2025-12-03T00:00:00Z
      })
      expect(url).toContain('dates=20251201/20251204')
      expect(url).not.toMatch(/dates=\d{8}T/)
    })

    it('detects timed event from non-midnight timestamp', () => {
      const url = getGoogleCalendarUrl({
        title: 'Meeting',
        startDate: 1764583200, // 2025-12-01T10:00:00Z
        endDate: 1764586800, // 2025-12-01T11:00:00Z
      })
      expect(url).toContain('T')
      expect(url).toContain('Z')
    })
  })

  describe('timestamp handling', () => {
    it('handles Unix timestamps correctly', () => {
      const url = getGoogleCalendarUrl({
        title: 'Event',
        startDate: 1764547200, // 2025-12-01T00:00:00Z
      })
      expect(url).toContain('text=Event')
      expect(url).toContain('dates=')
    })

    it('handles midnight timestamp as all-day', () => {
      const url = getGoogleCalendarUrl({
        title: 'All Day Event',
        startDate: 1766880000, // 2025-12-28T00:00:00Z
      })
      // All-day events get +1 day for end
      expect(url).toContain('dates=20251228/20251229')
    })
  })

  describe('default endDate behavior', () => {
    it('defaults endDate to 1 hour after startDate for timed events', () => {
      const url = getGoogleCalendarUrl({
        title: 'Quick Meeting',
        startDate: 1764583200, // 2025-12-01T10:00:00Z
      })
      expect(url).toContain('dates=20251201T100000Z/20251201T110000Z')
    })

    it('uses provided endDate when available', () => {
      const url = getGoogleCalendarUrl({
        title: 'Long Meeting',
        startDate: 1764583200, // 2025-12-01T10:00:00Z
        endDate: 1764597600, // 2025-12-01T14:00:00Z
      })
      expect(url).toContain('dates=20251201T100000Z/20251201T140000Z')
    })
  })

  describe('parameter encoding', () => {
    it('encodes title with special characters', () => {
      const url = getGoogleCalendarUrl({
        title: 'Meeting & Discussion: Q4 Review',
        startDate: 1764547200, // 2025-12-01T00:00:00Z
      })
      expect(url).toContain('text=Meeting')
      expect(url).toContain('%26')
      expect(url).toContain('%3A')
    })

    it('encodes description', () => {
      const url = getGoogleCalendarUrl({
        title: 'Event',
        startDate: 1764547200, // 2025-12-01T00:00:00Z
        description: 'Join us at https://example.com?id=123',
      })
      expect(url).toContain('details=')
      expect(url).toContain('example.com')
    })

    it('encodes location with special characters', () => {
      const url = getGoogleCalendarUrl({
        title: 'Event',
        startDate: 1764547200, // 2025-12-01T00:00:00Z
        location: '123 Main St, New York, NY 10001',
      })
      expect(url).toContain('location=')
    })
  })

  describe('URL structure', () => {
    it('generates correct base URL', () => {
      const url = getGoogleCalendarUrl({
        title: 'Event',
        startDate: 1764547200, // 2025-12-01T00:00:00Z
      })
      expect(url.startsWith('https://calendar.google.com/calendar/render?action=TEMPLATE')).toBe(
        true
      )
    })

    it('includes all provided parameters', () => {
      const url = getGoogleCalendarUrl({
        title: 'OWASP Conference',
        description: 'Annual security conference',
        location: 'Belgium',
        startDate: 1764633600, // 2025-12-02T00:00:00Z
        endDate: 1764720000, // 2025-12-03T00:00:00Z
      })
      expect(url).toContain('text=OWASP')
      expect(url).toContain('details=')
      expect(url).toContain('location=Belgium')
      expect(url).toContain('dates=')
    })

    it('omits empty optional parameters', () => {
      const url = getGoogleCalendarUrl({
        title: 'Simple Event',
        startDate: 1764547200, // 2025-12-01T00:00:00Z
      })
      expect(url).not.toContain('details=')
      expect(url).not.toContain('location=')
    })
  })

  describe('error handling', () => {
    it('throws error for missing title', () => {
      expect(() =>
        getGoogleCalendarUrl({
          title: '',
          startDate: 1764547200,
        })
      ).toThrow()
    })

    it('throws error for missing startDate', () => {
      expect(() =>
        getGoogleCalendarUrl({
          title: 'Event',
          startDate: 0,
        })
      ).toThrow()
    })
  })

  describe('real-world scenarios', () => {
    it('handles conference event', () => {
      const url = getGoogleCalendarUrl({
        title: 'Security Conference 2025',
        description: 'Annual security conference',
        location: 'Belgium',
        startDate: 1764633600, // 2025-12-02T00:00:00Z
        endDate: 1764720000, // 2025-12-03T00:00:00Z
      })
      expect(url).toContain('text=Security')
      expect(url).toContain('dates=20251202/20251204')
    })

    it('handles workshop with specific time', () => {
      const url = getGoogleCalendarUrl({
        title: 'Security Workshop',
        description: 'Hands-on security training',
        location: 'Virtual - Zoom',
        startDate: 1765789200, // 2025-12-15T09:00:00Z
        endDate: 1765818000, // 2025-12-15T17:00:00Z
      })
      expect(url).toContain('text=Security')
      expect(url).toContain('T')
    })

    it('handles multi-day conference', () => {
      const url = getGoogleCalendarUrl({
        title: 'Tech Conference 2026',
        location: 'Austin, USA',
        startDate: 1793059200, // 2026-10-27T00:00:00Z
        endDate: 1793318400, // 2026-10-30T00:00:00Z
      })
      expect(url).toContain('dates=20261027/20261031')
    })
  })
})
