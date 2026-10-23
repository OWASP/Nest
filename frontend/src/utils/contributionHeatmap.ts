export type ContributionHeatmapSeries = Array<{
  name: string
  data: Array<{ x: string; y: number | null; date: string }>
}>

const monthFormatter = new Intl.DateTimeFormat('en-US', { month: 'short', timeZone: 'UTC' })

const toUtcDay = (value: string | Date): Date => {
  const date = new Date(value)
  date.setUTCHours(0, 0, 0, 0)
  return date
}

export const buildContributionCalendar = (
  startDate: string,
  endDate: string,
  contributionData: Record<string, number>,
  now: Date
) => {
  let start = toUtcDay(startDate)
  let end = toUtcDay(endDate)

  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) {
    end = toUtcDay(now)
    start = new Date(end)
    start.setUTCFullYear(start.getUTCFullYear() - 1)
  }

  if (start > end) {
    ;[start, end] = [end, start]
  }

  const series: ContributionHeatmapSeries = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map(
    (name) => ({ name, data: [] })
  )
  const currentDate = new Date(start)
  currentDate.setUTCDate(currentDate.getUTCDate() - ((currentDate.getUTCDay() + 6) % 7))
  const normalizedStart = start.toISOString().split('T')[0]
  const monthLabels: Record<string, string> = {}
  let weeksCount = 0

  while (currentDate <= end) {
    weeksCount++
    const weekLabel = `W${weeksCount}`
    for (const day of series) {
      const date = currentDate.toISOString().split('T')[0]
      const isInRange = currentDate >= start && currentDate <= end
      if (isInRange && (date === normalizedStart || currentDate.getUTCDate() === 1)) {
        const month = monthFormatter.format(currentDate)
        monthLabels[weekLabel] = monthLabels[weekLabel]
          ? `${monthLabels[weekLabel]} / ${month}`
          : month
      }
      day.data.push({
        x: weekLabel,
        y: isInRange ? (contributionData[date] ?? 0) : null,
        date,
      })
      currentDate.setUTCDate(currentDate.getUTCDate() + 1)
    }
  }

  // Leave room for the first full month when the starting partial month is only one column wide.
  if (monthLabels.W1 && monthLabels.W2) delete monthLabels.W1

  return {
    heatmapSeries: series.reverse(),
    weeksCount,
    monthLabels,
    startDate: normalizedStart,
    endDate: end.toISOString().split('T')[0],
  }
}
