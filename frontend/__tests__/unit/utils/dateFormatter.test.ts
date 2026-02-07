import { formatDate, formatDateRange } from 'utils/dateFormatter'

describe('formatDate function', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('formats Unix timestamp correctly', () => {
    // 1630454400 is Sep 1, 2021 in Unix timestamp (seconds)
    expect(formatDate(1630454400)).toBe('Sep 1, 2021')
  })

  test('formats dates with leading zeros correctly', () => {
    // TODO: Replace with Unix timestamp for 2023-01-05
    expect(formatDate(1672876800)).toBe('Jan 5, 2023')
  })

  test('handles different months', () => {
    // TODO: Replace with Unix timestamps for 2023-12-25 and 2023-07-04
    expect(formatDate(1703462400)).toBe('Dec 25, 2023')
    expect(formatDate(1688428800)).toBe('Jul 4, 2023')
  })
})

describe('formatDateRange function', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('formats date range in same month correctly', () => {
    // TODO: Replace with Unix timestamps for 2023-09-01 and 2023-09-04
    expect(formatDateRange(1693526400, 1693785600)).toBe('Sep 1 — 4, 2023')
  })

  test('formats date range in different months but same year correctly', () => {
    // TODO: Replace with Unix timestamps for 2023-09-29 and 2023-10-02
    expect(formatDateRange(1695945600, 1696204800)).toBe('Sep 29 — Oct 2, 2023')
  })

  test('formats date range in different years correctly', () => {
    // TODO: Replace with Unix timestamps for 2023-12-30 and 2024-01-03
    expect(formatDateRange(1703894400, 1704240000)).toBe('Dec 30, 2023 — Jan 3, 2024')
  })

  test('formats Unix timestamp date ranges correctly', () => {
    // Sept 1-4, 2021
    const startTimestamp = 1630454400 // Sep 1, 2021
    const endTimestamp = 1630713600 // Sep 4, 2021
    expect(formatDateRange(startTimestamp, endTimestamp)).toBe('Sep 1 — 4, 2021')
  })

  test('handles month boundaries correctly', () => {
    // TODO: Replace with Unix timestamps for 2023-09-30 and 2023-10-02
    expect(formatDateRange(1696032000, 1696204800)).toBe('Sep 30 — Oct 2, 2023')
  })

  test('handles year boundaries correctly', () => {
    // TODO: Replace with Unix timestamps for 2023-12-29 and 2024-01-02
    expect(formatDateRange(1703808000, 1704153600)).toBe('Dec 29, 2023 — Jan 2, 2024')
  })

  test('handles single-day ranges correctly', () => {
    // TODO: Replace with Unix timestamp for 2023-09-01
    expect(formatDateRange(1693526400, 1693526400)).toBe('Sep 1, 2023')
  })
})
