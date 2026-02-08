import { createEvent } from 'ics'
import getIcsFileUrl from 'utils/getIcsFileUrl'

describe('getIcsFileUrl', () => {
  const originalCreateObjectURL = globalThis.URL.createObjectURL

  const mockEvent = {
    title: 'Conference',
    description: 'Discuss Q4 goals',
    location: 'Conference Room A',
    url: 'https://meet.google.com/abc-defg-hij',
    startDate: 1735689600, // 2025-01-01 00:00:00 UTC
    endDate: 1735862400, // 2025-01-03 00:00:00 UTC
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
      ...mockEvent,
      startDate: 1735689600, // 2025-01-01 00:00:00 UTC
      endDate: 1735862400, // 2025-01-03 00:00:00 UTC
    }

    await getIcsFileUrl(eventWithTimestamps)

    expect(createEvent).toHaveBeenCalledWith(
      expect.objectContaining({
        start: [2025, 1, 1],
        end: [2025, 1, 3],
      }),
      expect.any(Function)
    )
  })

  it('should correctly format Unix timestamps into DateArray (UTC conversion)', async () => {
    ;(createEvent as jest.Mock).mockImplementation((attr, cb) => cb(null, 'val'))

    const eventWithTimestamps = {
      ...mockEvent,
      startDate: 1735689600, // 2025-01-01 00:00:00 UTC
      endDate: 1735862400, // 2025-01-03 00:00:00 UTC
    }

    await getIcsFileUrl(eventWithTimestamps)

    expect(createEvent).toHaveBeenCalledWith(
      expect.objectContaining({
        start: [2025, 1, 1],
        end: [2025, 1, 3],
      }),
      expect.any(Function)
    )
  })

  it('should automatically increment the end date by 1 day if start and end dates are the same', async () => {
    ;(createEvent as jest.Mock).mockImplementation((attr, cb) => cb(null, 'val'))

    const singleDayEvent = {
      ...mockEvent,
      startDate: 1735689600, // 2025-01-01 00:00:00 UTC
      endDate: 1735689600, // 2025-01-01 00:00:00 UTC (same day)
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
      {
        start: [2025, 1, 1],
        end: [2025, 1, 3],
        title: mockEvent.title,
        description: mockEvent.description,
        location: mockEvent.location,
        url: mockEvent.url,
        status: 'CONFIRMED',
        busyStatus: 'BUSY',
      },
      expect.any(Function)
    )
  })
})
