import getGoogleCalendarUrl from 'utils/getGoogleCalendarUrl'

describe('getGoogleCalendarUrl', () => {
  describe('date format detection', () => {
    it('detects all-day event from date-only string (YYYY-MM-DD)', () => {
      const url = getGoogleCalendarUrl({
        title: 'Conference',
        startDate: '2025-12-01',
        endDate: '2025-12-03',
      })
      expect(url).toContain('dates=20251201/20251203')
      expect(url).not.toMatch(/dates=\d{8}T/)
    })

    it('detects timed event from ISO string with T', () => {
      const url = getGoogleCalendarUrl({
        title: 'Meeting',
        startDate: '2025-12-01T10:00:00',
        endDate: '2025-12-01T11:00:00',
      })
      expect(url).toContain('T')
      expect(url).toContain('Z')
    })

    it('detects timed event from string with colon', () => {
      const url = getGoogleCalendarUrl({
        title: 'Meeting',
        startDate: '2025-12-01 10:00:00',
        endDate: '2025-12-01 11:00:00',
      })
      expect(url).toContain('T')
      expect(url).toContain('Z')
    })

    it('treats Date object as timed event', () => {
      const url = getGoogleCalendarUrl({
        title: 'Meeting',
        startDate: new Date('2025-12-01T10:00:00'),
        endDate: new Date('2025-12-01T11:00:00'),
      })
      expect(url).toContain('T')
      expect(url).toContain('Z')
    })
  })

  describe('diverse date formats', () => {
    it('handles ISO 8601 format', () => {
      const url = getGoogleCalendarUrl({
        title: 'Event',
        startDate: '2025-12-01T14:30:00.000Z',
      })
      expect(url).toContain('text=Event')
      expect(url).toContain('dates=')
    })

    it('handles date-only format', () => {
      const url = getGoogleCalendarUrl({
        title: 'All Day Event',
        startDate: '2025-12-25',
      })
      expect(url).toContain('dates=20251225')
    })

    it('handles Date object', () => {
      const url = getGoogleCalendarUrl({
        title: 'Event',
        startDate: new Date(2025, 11, 1, 10, 0, 0),
      })
      expect(url).toContain('text=Event')
    })

    it('handles timestamp-like ISO string', () => {
      const url = getGoogleCalendarUrl({
        title: 'Event',
        startDate: '2025-12-01T00:00:00Z',
      })
      expect(url).toContain('dates=')
    })
  })

  describe('default endDate behavior', () => {
    it('defaults endDate to 1 hour after startDate for timed events', () => {
      const url = getGoogleCalendarUrl({
        title: 'Quick Meeting',
        startDate: '2025-12-01T10:00:00Z',
      })
      expect(url).toContain('dates=20251201T100000Z/20251201T110000Z')
    })

    it('uses provided endDate when available', () => {
      const url = getGoogleCalendarUrl({
        title: 'Long Meeting',
        startDate: '2025-12-01T10:00:00Z',
        endDate: '2025-12-01T14:00:00Z',
      })
      expect(url).toContain('dates=20251201T100000Z/20251201T140000Z')
    })
  })

  describe('parameter encoding', () => {
    it('encodes title with special characters', () => {
      const url = getGoogleCalendarUrl({
        title: 'Meeting & Discussion: Q4 Review',
        startDate: '2025-12-01',
      })
      expect(url).toContain('text=Meeting')
      expect(url).toContain('%26')
      expect(url).toContain('%3A')
    })

    it('encodes description', () => {
      const url = getGoogleCalendarUrl({
        title: 'Event',
        startDate: '2025-12-01',
        description: 'Join us at https://example.com?id=123',
      })
      expect(url).toContain('details=')
      expect(url).toContain('example.com')
    })

    it('encodes location with special characters', () => {
      const url = getGoogleCalendarUrl({
        title: 'Event',
        startDate: '2025-12-01',
        location: '123 Main St, New York, NY 10001',
      })
      expect(url).toContain('location=')
    })
  })

  describe('URL structure', () => {
    it('generates correct base URL', () => {
      const url = getGoogleCalendarUrl({
        title: 'Event',
        startDate: '2025-12-01',
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
        startDate: '2025-12-02',
        endDate: '2025-12-03',
      })
      expect(url).toContain('text=OWASP')
      expect(url).toContain('details=')
      expect(url).toContain('location=Belgium')
      expect(url).toContain('dates=')
    })

    it('omits empty optional parameters', () => {
      const url = getGoogleCalendarUrl({
        title: 'Simple Event',
        startDate: '2025-12-01',
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
          startDate: '2025-12-01',
        })
      ).toThrow()
    })

    it('throws error for missing startDate', () => {
      expect(() =>
        getGoogleCalendarUrl({
          title: 'Event',
          startDate: '',
        })
      ).toThrow()
    })

    it('throws error for invalid startDate', () => {
      expect(() =>
        getGoogleCalendarUrl({
          title: 'Event',
          startDate: 'invalid-date',
        })
      ).toThrow('Invalid startDate')
    })

    it('throws error for invalid endDate', () => {
      expect(() =>
        getGoogleCalendarUrl({
          title: 'Event',
          startDate: '2025-12-01',
          endDate: 'invalid-date',
        })
      ).toThrow('Invalid endDate')
    })
  })

  describe('real-world scenarios', () => {
    it('handles conference event', () => {
      const url = getGoogleCalendarUrl({
        title: 'Security Conference 2025',
        description: 'Annual security conference',
        location: 'Belgium',
        startDate: '2025-12-02',
        endDate: '2025-12-03',
      })
      expect(url).toContain('text=Security')
      expect(url).toContain('dates=20251202/20251203')
    })

    it('handles workshop with specific time', () => {
      const url = getGoogleCalendarUrl({
        title: 'Security Workshop',
        description: 'Hands-on security training',
        location: 'Virtual - Zoom',
        startDate: '2025-12-15T09:00:00',
        endDate: '2025-12-15T17:00:00',
      })
      expect(url).toContain('text=Security')
      expect(url).toContain('T')
    })

    it('handles multi-day conference', () => {
      const url = getGoogleCalendarUrl({
        title: 'Tech Conference 2026',
        location: 'Austin, USA',
        startDate: '2026-10-27',
        endDate: '2026-10-30',
      })
      expect(url).toContain('dates=20261027/20261030')
    })
  })
})
