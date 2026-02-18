import { formatDate, formatDateRange, formatDateForInput } from 'utils/dateFormatter'

describe('formatDate function', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('formats ISO date string correctly', () => {
    expect(formatDate('2023-09-01')).toBe('Sep 1, 2023')
  })

  test('formats Unix timestamp correctly', () => {
    // 1630454400 is Sep 1, 2021 in Unix timestamp (seconds)
    expect(formatDate(1630454400)).toBe('Sep 1, 2021')
  })

  test('throws error for invalid date', () => {
    expect(() => formatDate('invalid-date')).toThrow(TypeError)
    expect(() => formatDate('invalid-date')).toThrow('Invalid date')
  })

  test('handles different date formats', () => {
    expect(formatDate('2023/09/01')).toBe('Sep 1, 2023')
    expect(formatDate('09/01/2023')).toBe('Sep 1, 2023')
  })

  test('formats dates with leading zeros correctly', () => {
    expect(formatDate('2023-01-05')).toBe('Jan 5, 2023')
  })

  test('handles different months', () => {
    expect(formatDate('2023-12-25')).toBe('Dec 25, 2023')
    expect(formatDate('2023-07-04')).toBe('Jul 4, 2023')
  })
})

describe('formatDateRange function', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('formats date range in same month correctly', () => {
    expect(formatDateRange('2023-09-01', '2023-09-04')).toBe('Sep 1 — 4, 2023')
  })

  test('formats date range in different months but same year correctly', () => {
    expect(formatDateRange('2023-09-29', '2023-10-02')).toBe('Sep 29 — Oct 2, 2023')
  })

  test('formats date range in different years correctly', () => {
    expect(formatDateRange('2023-12-30', '2024-01-03')).toBe('Dec 30, 2023 — Jan 3, 2024')
  })

  test('formats Unix timestamp date ranges correctly', () => {
    // Sept 1-4, 2021
    const startTimestamp = 1630454400 // Sep 1, 2021
    const endTimestamp = 1630713600 // Sep 4, 2021
    expect(formatDateRange(startTimestamp, endTimestamp)).toBe('Sep 1 — 4, 2021')
  })

  test('throws error when start date is invalid', () => {
    expect(() => formatDateRange('invalid-date', '2023-09-04')).toThrow(TypeError)
    expect(() => formatDateRange('invalid-date', '2023-09-04')).toThrow('Invalid date')
  })

  test('throws error when end date is invalid', () => {
    expect(() => formatDateRange('2023-09-01', 'invalid-date')).toThrow(TypeError)
    expect(() => formatDateRange('2023-09-01', 'invalid-date')).toThrow('Invalid date')
  })

  test('handles month boundaries correctly', () => {
    expect(formatDateRange('2023-09-30', '2023-10-02')).toBe('Sep 30 — Oct 2, 2023')
  })

  test('handles year boundaries correctly', () => {
    expect(formatDateRange('2023-12-29', '2024-01-02')).toBe('Dec 29, 2023 — Jan 2, 2024')
  })

  test('handles single-day ranges correctly', () => {
    expect(formatDateRange('2023-09-01', '2023-09-01')).toBe('Sep 1, 2023')
  })

  test('handles mixed input types correctly', () => {
    // Sep 1, 2021 as Unix timestamp and ISO string
    expect(formatDateRange(1630454400, '2021-09-04')).toBe('Sep 1 — 4, 2021')
  })
})

describe('formatDateForInput function', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('formats ISO date string correctly', () => {
    expect(formatDateForInput('2023-09-01')).toBe('2023-09-01')
  })

  test('formats Unix timestamp correctly', () => {
    expect(formatDateForInput(1630454400)).toBe('2021-09-01')
  })

  test('throws TypeError for invalid date', () => {
    expect(() => formatDateForInput('invalid-date')).toThrow(TypeError)
    expect(() => formatDateForInput('invalid-date')).toThrow('Invalid date')
  })
})
