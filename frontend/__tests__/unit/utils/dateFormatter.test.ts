import {
  formatCompactDateRange,
  formatDate,
  formatDateForInput,
  formatDateRange,
} from 'utils/dateFormatter'

describe('formatDate function', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('formats ISO date string correctly', () => {
    expect(formatDate('2021-09-01T00:00:00+00:00')).toBe('Sep 1, 2021')
  })

  test('formats dates with leading zeros correctly', () => {
    expect(formatDate('2023-01-05T00:00:00+00:00')).toBe('Jan 5, 2023')
  })

  test('handles different months', () => {
    expect(formatDate('2023-12-25T00:00:00+00:00')).toBe('Dec 25, 2023')
    expect(formatDate('2023-07-04T00:00:00+00:00')).toBe('Jul 4, 2023')
  })

  test('returns empty string for null', () => {
    expect(formatDate(null)).toBe('')
  })

  test('returns empty string for empty string', () => {
    expect(formatDate('')).toBe('')
  })

  test('returns empty string for invalid date string', () => {
    expect(formatDate('not-a-date')).toBe('')
  })
})

describe('formatDateRange function', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('formats date range in same month correctly', () => {
    expect(formatDateRange('2023-09-01T00:00:00+00:00', '2023-09-04T00:00:00+00:00')).toBe(
      'Sep 1 — 4, 2023'
    )
  })

  test('formats date range in different months but same year correctly', () => {
    expect(formatDateRange('2023-09-29T00:00:00+00:00', '2023-10-02T00:00:00+00:00')).toBe(
      'Sep 29 — Oct 2, 2023'
    )
  })

  test('formats date range in different years correctly', () => {
    expect(formatDateRange('2023-12-30T00:00:00+00:00', '2024-01-03T00:00:00+00:00')).toBe(
      'Dec 30, 2023 — Jan 3, 2024'
    )
  })

  test('formats ISO date string ranges correctly', () => {
    expect(formatDateRange('2021-09-01T00:00:00+00:00', '2021-09-04T00:00:00+00:00')).toBe(
      'Sep 1 — 4, 2021'
    )
  })

  test('handles month boundaries correctly', () => {
    expect(formatDateRange('2023-09-30T00:00:00+00:00', '2023-10-02T00:00:00+00:00')).toBe(
      'Sep 30 — Oct 2, 2023'
    )
  })

  test('handles year boundaries correctly', () => {
    expect(formatDateRange('2004-12-29T00:00:00+00:00', '2005-01-02T00:00:00+00:00')).toBe(
      'Dec 29, 2004 — Jan 2, 2005'
    )
  })

  test('handles single-day ranges correctly', () => {
    expect(formatDateRange('2023-09-01T00:00:00+00:00', '2023-09-01T00:00:00+00:00')).toBe(
      'Sep 1, 2023'
    )
  })

  test('treats epoch as a valid date', () => {
    expect(formatDateRange('1970-01-01T00:00:00+00:00', '1970-01-01T00:00:00+00:00')).toBe(
      'Jan 1, 1970'
    )
  })
})

describe('formatCompactDateRange function', () => {
  test('shows only the end year for ranges across years', () => {
    expect(formatCompactDateRange('2025-03-24', '2026-03-24')).toBe('Mar 24, 2025 — 2026')
  })

  test('shows only the end year when the end month and day differ', () => {
    expect(formatCompactDateRange('2023-12-30', '2024-01-03')).toBe('Dec 30, 2023 — 2024')
  })

  test.each([
    ['2023-09-01', '2023-09-04', 'Sep 1 — 4, 2023'],
    ['2023-09-29', '2023-10-02', 'Sep 29 — Oct 2, 2023'],
    ['2023-09-01', '2023-09-01', 'Sep 1, 2023'],
  ])('keeps the regular format for %s to %s in the same year', (start, end, expected) => {
    expect(formatCompactDateRange(start, end)).toBe(expected)
  })

  test.each([
    ['invalid-date', '2024-01-01'],
    ['2024-01-01', 'invalid-date'],
  ])('returns empty string for invalid range %s to %s', (start, end) => {
    expect(formatCompactDateRange(start, end)).toBe('')
  })
})

describe('formatDateForInput function', () => {
  test('formats ISO date string correctly for input fields', () => {
    expect(formatDateForInput('2021-09-01T00:00:00+00:00')).toBe('2021-09-01')
  })

  test('returns empty string for invalid input instead of throwing', () => {
    expect(formatDateForInput('invalid-date')).toBe('')
  })

  test('treats epoch as a valid date', () => {
    expect(formatDateForInput('1970-01-01T00:00:00+00:00')).toBe('1970-01-01')
  })
})
