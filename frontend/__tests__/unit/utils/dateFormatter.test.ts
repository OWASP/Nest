import { formatDate, formatDateRange } from 'utils/dateFormatter'

describe('formatDate function', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('formats Unix timestamp correctly', () => {
    // time stamp convert and checked from https://www.epochconverter.com/
    // 1630454400 is Sep 1, 2021 in Unix timestamp (seconds)
    expect(formatDate(1630454400)).toBe('Sep 1, 2021')
  })

  test('formats dates with leading zeros correctly', () => {
    // 1672876800 is Jan 5, 2023 in Unix timestamp (seconds)
    expect(formatDate(1672876800)).toBe('Jan 5, 2023')
  })

  test('handles different months', () => {
    // 1703462400 is Dec 25, 2023 and 1688428800 is Jul 4, 2023
    expect(formatDate(1703462400)).toBe('Dec 25, 2023')
    expect(formatDate(1688428800)).toBe('Jul 4, 2023')
  })
})

describe('formatDateRange function', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('formats date range in same month correctly', () => {
    expect(formatDateRange(1693526400, 1693785600)).toBe('Sep 1 — 4, 2023')
  })

  test('formats date range in different months but same year correctly', () => {
    expect(formatDateRange(1695945600, 1696204800)).toBe('Sep 29 — Oct 2, 2023')
  })

  test('formats date range in different years correctly', () => {
    expect(formatDateRange(1703894400, 1704240000)).toBe('Dec 30, 2023 — Jan 3, 2024')
  })

  test('formats Unix timestamp date ranges correctly', () => {
    // Sept 1-4, 2021
    const startTimestamp = 1630454400
    const endTimestamp = 1630713600
    expect(formatDateRange(startTimestamp, endTimestamp)).toBe('Sep 1 — 4, 2021')
  })

  test('handles month boundaries correctly', () => {
    expect(formatDateRange(1696032000, 1696204800)).toBe('Sep 30 — Oct 2, 2023')
  })

  test('handles year boundaries correctly', () => {
    // 1104278400 is Dec 29, 2004
    expect(formatDateRange(1104278400, 1104624000)).toBe('Dec 29, 2004 — Jan 2, 2005')
  })

  test('handles single-day ranges correctly', () => {
    expect(formatDateRange(1693526400, 1693526400)).toBe('Sep 1, 2023')
  })
})
