import { contributionCount, getContributionDateRange } from 'utils/contributionDataUtils'

describe('getContributionDateRange', () => {
  test('uses valid daily date bounds for older reports without a saved period', () => {
    expect(
      getContributionDateRange(undefined, {
        '2026-10-20': 1,
        '2025-02-28': 2,
        '2025-02-30': 3,
        '2024-01': 4,
        '2024-01-01T00:00:00Z': 5,
        invalid: 6,
      })
    ).toEqual({ startDate: '2025-02-28', endDate: '2026-10-20' })
  })

  test('prefers the saved reporting period over dates with recorded activity', () => {
    expect(
      getContributionDateRange(
        {
          commits: 2,
          pullRequests: 0,
          issues: 0,
          total: 2,
          startAt: '2025-10-22T12:30:45.123456+00:00',
          endAt: '2026-10-22T12:30:45.123456+00:00',
        },
        { '2026-10-20': 2 }
      )
    ).toEqual({ startDate: '2025-10-22', endDate: '2026-10-22' })
  })

  test.each([
    {
      startAt: '2025-10-22T23:30:00-02:00',
      endAt: '2026-10-22T00:30:00+02:00',
      expected: { startDate: '2025-10-23', endDate: '2026-10-21' },
    },
    {
      startAt: '2024-02-29',
      endAt: '2024-02-29',
      expected: { startDate: '2024-02-29', endDate: '2024-02-29' },
    },
    {
      startAt: '2026-10-22T01:00:00Z',
      endAt: '2026-10-22T12:00:00Z',
      expected: { startDate: '2026-10-22', endDate: '2026-10-22' },
    },
  ])(
    'normalizes valid saved bounds to UTC dates ($startAt, $endAt)',
    ({ startAt, endAt, expected }) => {
      expect(
        getContributionDateRange({
          commits: 0,
          issues: 0,
          pullRequests: 0,
          total: 0,
          startAt,
          endAt,
        })
      ).toEqual(expected)
    }
  )

  test.each([
    { startAt: undefined, endAt: '2026-10-22' },
    { startAt: '2025-10-22', endAt: undefined },
    { startAt: '', endAt: '2026-10-22' },
    { startAt: 'invalid', endAt: '2026-10-22' },
    { startAt: '2025-10', endAt: '2026-10-22' },
    { startAt: '2025-02-29', endAt: '2026-10-22' },
    { startAt: '2025-02-30T12:00:00Z', endAt: '2026-10-22' },
    { startAt: '2025-13-01', endAt: '2026-10-22' },
    { startAt: '2026-10-23', endAt: '2026-10-22' },
    { startAt: '2026-10-22T12:00:00Z', endAt: '2026-10-22T01:00:00Z' },
    { startAt: '2025-10-22T12:00:00', endAt: '2026-10-22' },
    { startAt: '2025-10-22T12:00:00ZjunkZ', endAt: '2026-10-22' }, // cspell:ignore Zjunk
  ])('falls back when saved bounds are unusable ($startAt, $endAt)', ({ startAt, endAt }) => {
    expect(
      getContributionDateRange(
        { commits: 2, issues: 0, pullRequests: 0, total: 2, startAt, endAt },
        { '2024-03-01': 1, '2023-02-01': 1 }
      )
    ).toEqual({ startDate: '2023-02-01', endDate: '2024-03-01' })
  })

  const unusableDailyData: Array<Record<string, number> | undefined> = [
    undefined,
    {},
    { invalid: 1 },
    { '2024-02-30': 1 },
    { '2024-01': 1, '2024-01-01T00:00:00Z': 1 },
  ]
  test.each(unusableDailyData)('returns no period when no usable dates exist (%j)', (data) => {
    expect(
      getContributionDateRange({ commits: 2, issues: 0, pullRequests: 0, total: 2 }, data)
    ).toBeUndefined()
  })

  test('retains a recorded zero-activity day as a valid one-day range', () => {
    expect(getContributionDateRange(undefined, { '2024-02-29': 0 })).toEqual({
      startDate: '2024-02-29',
      endDate: '2024-02-29',
    })
  })
})

describe('contributionCount', () => {
  test('returns 0 when contributions are missing', () => {
    expect(contributionCount(undefined, 'london', 'www-chapter-')).toBe(0)
  })

  test('uses a bare chapter key when present', () => {
    expect(contributionCount({ london: 4 }, 'london', 'www-chapter-')).toBe(4)
  })

  test('falls back from a bare chapter key to the prefixed map key', () => {
    expect(contributionCount({ 'www-chapter-london': 7 }, 'london', 'www-chapter-')).toBe(7)
  })

  test('falls back from a prefixed chapter key to the bare map key', () => {
    expect(contributionCount({ london: 3 }, 'www-chapter-london', 'www-chapter-')).toBe(3)
  })

  test('uses a bare project key when present', () => {
    expect(contributionCount({ nest: 12 }, 'nest', 'www-project-')).toBe(12)
  })

  test('falls back from a bare project key to the prefixed map key', () => {
    expect(contributionCount({ 'www-project-nest': 9 }, 'nest', 'www-project-')).toBe(9)
  })

  test('falls back from a prefixed project key to the bare map key', () => {
    expect(contributionCount({ nest: 5 }, 'www-project-nest', 'www-project-')).toBe(5)
  })

  test('returns 0 when neither key form is present', () => {
    expect(contributionCount({ other: 1 }, 'nest', 'www-project-')).toBe(0)
  })

  test('prefers the exact key over the alternate form', () => {
    expect(contributionCount({ nest: 2, 'www-project-nest': 8 }, 'nest', 'www-project-')).toBe(2)
  })

  test('ignores inherited Object.prototype properties on the alternate key', () => {
    expect(contributionCount({}, 'www-project-toString', 'www-project-')).toBe(0)
  })
})
