import { createEvent } from 'ics'
import getIcsFileUrl from 'utils/getIcsFileUrl'

describe('getIcsFileUrl', () => {
  const originalCreateObjectURL = globalThis.URL.createObjectURL

  const mockEvent = {
    title: 'Conference',
    description: 'Discuss Q4 goals',
    location: 'Conference Room A',
    startDate: '2025-01-01T00:00:00Z',
    endDate: '2025-01-03T00:00:00Z',
  }

  beforeAll(() => {
    globalThis.URL.createObjectURL = jest.fn(() => 'blob:http://localhost/mock-uuid')
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  afterAll(() => {
    globalThis.URL.createObjectURL = originalCreateObjectURL
  })

  it('should generate a blob URL when event creation is successful', async () => {
    ;(createEvent as jest.Mock).mockImplementation((attributes, callback) => {
      callback(null, 'BEGIN:VCALENDAR...')
    })

    const result = await getIcsFileUrl(mockEvent)

    expect(result).toBe('blob:http://localhost/mock-uuid')
    expect(createEvent).toHaveBeenCalledTimes(1)
    expect(globalThis.URL.createObjectURL).toHaveBeenCalledWith(expect.any(Blob))
  })

  it('should correctly format Unix timestamps into DateArray', async () => {
    ;(createEvent as jest.Mock).mockImplementation((attr, cb) => cb(null, 'val'))

    const eventWithTimestamps = {
      title: 'Multi-day',
      startDate: '2025-01-01T00:00:00Z',
      endDate: '2025-01-03T00:00:00Z',
    }

    await getIcsFileUrl(eventWithTimestamps)

    expect(createEvent).toHaveBeenCalledWith(
      expect.objectContaining({
        start: [2025, 1, 1],
        end: [2025, 1, 4],
      }),
      expect.any(Function)
    )
  })

  it('should correctly format Unix timestamps into DateArray (UTC conversion)', async () => {
    ;(createEvent as jest.Mock).mockImplementation((attr, cb) => cb(null, 'val'))

    const eventWithTimestamps = {
      title: 'Multi-day UTC',
      startDate: '2025-01-01T00:00:00Z',
      endDate: '2025-01-03T00:00:00Z',
    }

    await getIcsFileUrl(eventWithTimestamps)

    expect(createEvent).toHaveBeenCalledWith(
      expect.objectContaining({
        start: [2025, 1, 1],
        end: [2025, 1, 4],
      }),
      expect.any(Function)
    )
  })

  it('should automatically increment the end date by 1 day if start and end dates are the same', async () => {
    ;(createEvent as jest.Mock).mockImplementation((attr, cb) => cb(null, 'val'))

    const singleDayEvent = {
      title: 'Single day',
      startDate: '2025-01-01T00:00:00Z',
      endDate: '2025-01-01T00:00:00Z',
    }

    await getIcsFileUrl(singleDayEvent)

    expect(createEvent).toHaveBeenCalledWith(
      expect.objectContaining({
        start: [2025, 1, 1],
        end: [2025, 1, 2],
      }),
      expect.any(Function)
    )
  })

  it('should reject the promise if createEvent returns an error', async () => {
    const mockError = new Error('ICS generation failed')

    ;(createEvent as jest.Mock).mockImplementation((attr, callback) => {
      callback(mockError, null)
    })

    await expect(getIcsFileUrl(mockEvent)).rejects.toThrow('ICS generation failed')
  })

  it('should pass all event attributes correctly to createEvent', async () => {
    ;(createEvent as jest.Mock).mockImplementation((attr, cb) => cb(null, 'val'))

    await getIcsFileUrl(mockEvent)

    expect(createEvent).toHaveBeenCalledWith(
      expect.objectContaining({
        start: [2025, 1, 1],
        end: [2025, 1, 4],
        title: mockEvent.title,
        description: mockEvent.description,
        location: mockEvent.location,
        status: 'CONFIRMED',
        busyStatus: 'BUSY',
      }),
      expect.any(Function)
    )
  })

  describe('generated calendar dates', () => {
    beforeEach(() => {
      ;(createEvent as jest.Mock).mockImplementation(
        jest.requireActual<typeof import('ics')>('ics').createEvent
      )
    })

    it.each<[string, string, string | undefined, string, string]>([
      ['single-day', '2026-10-27', '2026-10-27', '20261027', '20261028'],
      ['missing end date', '2026-10-27', undefined, '20261027', '20261028'],
      ['multi-day', '2026-10-27', '2026-10-30', '20261027', '20261031'],
      ['month boundary', '2026-10-30', '2026-11-02', '20261030', '20261103'],
      ['year boundary', '2026-12-30', '2027-01-02', '20261230', '20270103'],
      ['leap day', '2028-02-28', '2028-02-29', '20280228', '20280301'],
    ])(
      'includes the final day of a %s event',
      async (_description, startDate, endDate, expectedStart, expectedEnd) => {
        await getIcsFileUrl({ title: 'Conference', startDate, endDate })

        const blob = (globalThis.URL.createObjectURL as jest.Mock).mock.calls[0][0] as Blob
        const content = await new Promise<string>((resolve, reject) => {
          const reader = new FileReader()
          reader.onload = () => resolve(reader.result as string)
          reader.onerror = () => reject(reader.error)
          reader.readAsText(blob)
        })

        expect(content).toContain(`DTSTART;VALUE=DATE:${expectedStart}`)
        expect(content).toContain(`DTEND;VALUE=DATE:${expectedEnd}`)
      }
    )
  })
})
