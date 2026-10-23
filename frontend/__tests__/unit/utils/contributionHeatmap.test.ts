import { buildContributionCalendar } from 'utils/contributionHeatmap'

const now = new Date('2026-10-22T12:00:00Z')

describe('buildContributionCalendar', () => {
  it('labels months from reporting days rather than leading padding', () => {
    const calendar = buildContributionCalendar('2024-03-01', '2024-04-02', {}, now)
    expect(calendar.monthLabels).toEqual({ W1: 'Mar', W6: 'Apr' })
  })

  it('keeps both month names when a partial period crosses months in one week', () => {
    const calendar = buildContributionCalendar('2024-01-31', '2024-02-02', {}, now)
    expect(calendar.monthLabels).toEqual({ W1: 'Jan / Feb' })
  })

  it('leaves space for the next month after a one-column partial month', () => {
    const calendar = buildContributionCalendar('2025-03-24', '2025-05-31', {}, now)
    expect(calendar.monthLabels).toEqual({ W2: 'Apr', W6: 'May' })
  })

  it('preserves month labels when the period crosses into another year', () => {
    const calendar = buildContributionCalendar('2024-01-01', '2025-01-01', {}, now)
    const labels = Object.values(calendar.monthLabels)
    expect(labels).toHaveLength(13)
    expect(labels.filter((label) => label === 'Jan')).toHaveLength(2)
  })

  it('labels months even when there is no activity', () => {
    const calendar = buildContributionCalendar('2024-01-01', '2024-03-31', {}, now)
    expect(Object.values(calendar.monthLabels)).toEqual(['Jan', 'Feb', 'Mar'])
  })

  it('aligns partial weeks into seven equally sized weekday rows', () => {
    const calendar = buildContributionCalendar('2024-01-03', '2024-01-10', {}, now)

    expect(calendar.weeksCount).toBe(2)
    expect(calendar.heatmapSeries.map((day) => day.name)).toEqual([
      'Sun',
      'Sat',
      'Fri',
      'Thu',
      'Wed',
      'Tue',
      'Mon',
    ])
    expect(calendar.heatmapSeries.map((day) => day.data.length)).toEqual([2, 2, 2, 2, 2, 2, 2])
    const monday = calendar.heatmapSeries.find((day) => day.name === 'Mon')
    const sunday = calendar.heatmapSeries.find((day) => day.name === 'Sun')
    expect(monday?.data.map(({ date, y }) => ({ date, y }))).toEqual([
      { y: null, date: '2024-01-01' },
      { y: 0, date: '2024-01-08' },
    ])
    expect(sunday?.data.map(({ date, y }) => ({ date, y }))).toEqual([
      { y: 0, date: '2024-01-07' },
      { y: null, date: '2024-01-14' },
    ])
    expect(monday?.data.map((point) => point.x)).toEqual(sunday?.data.map((point) => point.x))
  })

  it('distinguishes blank padding from zero activity and excludes out-of-period counts', () => {
    const { heatmapSeries } = buildContributionCalendar(
      '2024-01-03',
      '2024-01-10',
      { '2024-01-01': 99, '2024-01-03': 5, '2024-01-10': 2, '2024-01-14': 99 },
      now
    )
    const cells = heatmapSeries.flatMap((day) => day.data)

    expect(cells.find((point) => point.date === '2024-01-01')?.y).toBeNull()
    expect(cells.find((point) => point.date === '2024-01-14')?.y).toBeNull()
    expect(cells.find((point) => point.date === '2024-01-04')?.y).toBe(0)
    expect(cells.find((point) => point.date === '2024-01-03')?.y).toBe(5)
    expect(cells.find((point) => point.date === '2024-01-10')?.y).toBe(2)
    expect(cells.reduce((sum, point) => sum + (point.y ?? 0), 0)).toBe(7)
  })

  it('normalizes timestamp bounds to their UTC calendar dates', () => {
    const calendar = buildContributionCalendar(
      '2024-01-02T00:30:00+05:30',
      '2024-01-02T23:30:00-02:00',
      { '2024-01-01': 1, '2024-01-02': 2, '2024-01-03': 3 },
      now
    )

    expect(calendar.startDate).toBe('2024-01-01')
    expect(calendar.endDate).toBe('2024-01-03')
    expect(
      calendar.heatmapSeries
        .flatMap((day) => day.data)
        .filter((point) => point.y !== null)
        .sort((a, b) => a.date.localeCompare(b.date))
        .map(({ date, y }) => ({ date, y }))
    ).toEqual([
      { date: '2024-01-01', y: 1 },
      { date: '2024-01-02', y: 2 },
      { date: '2024-01-03', y: 3 },
    ])
  })

  it.each([
    { start: '2024-02-28', end: '2024-03-01', dates: ['2024-02-28', '2024-02-29', '2024-03-01'] },
    { start: '2023-12-31', end: '2024-01-01', dates: ['2023-12-31', '2024-01-01'] },
    { start: '2024-02-29', end: '2024-02-29', dates: ['2024-02-29'] },
  ])('includes every reporting day from $start through $end', ({ start, end, dates }) => {
    const { heatmapSeries } = buildContributionCalendar(start, end, {}, now)
    expect(
      heatmapSeries
        .flatMap((day) => day.data)
        .filter((point) => point.y !== null)
        .map((point) => point.date)
        .sort()
    ).toEqual(dates)
  })

  it('swaps reversed bounds without losing contribution values', () => {
    const calendar = buildContributionCalendar('2024-01-10', '2024-01-03', { '2024-01-03': 5 }, now)

    expect(calendar.startDate).toBe('2024-01-03')
    expect(calendar.endDate).toBe('2024-01-10')
    expect(calendar.heatmapSeries.flatMap((day) => day.data)).toContainEqual(
      expect.objectContaining({ date: '2024-01-03', y: 5 })
    )
  })

  it.each([
    { start: '', end: '2024-01-31' },
    { start: '2024-01-01', end: '' },
    { start: 'invalid-date', end: '2024-01-31' },
    { start: '2024-01-01', end: 'invalid-date' },
  ])('uses the supplied clock for invalid bounds ($start, $end)', ({ start, end }) => {
    const calendar = buildContributionCalendar(start, end, {}, now)
    expect(calendar.startDate).toBe('2025-10-22')
    expect(calendar.endDate).toBe('2026-10-22')
  })

  it('does not mutate the supplied clock or contribution data', () => {
    const clock = new Date(now)
    const data = Object.freeze({ '2026-10-22': 4 })

    const { heatmapSeries } = buildContributionCalendar('', '', data, clock)

    expect(clock.toISOString()).toBe('2026-10-22T12:00:00.000Z')
    expect(data).toEqual({ '2026-10-22': 4 })
    expect(heatmapSeries.flatMap((day) => day.data)).toContainEqual(
      expect.objectContaining({ date: '2026-10-22', y: 4 })
    )
  })
})
