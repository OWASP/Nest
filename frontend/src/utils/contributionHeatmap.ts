export type ContributionHeatmapSeries = Array<{
  name: string
  data: Array<{ x: string; y: number | null; date: string }>
}>

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
  let weeksCount = 0

  while (currentDate <= end) {
    weeksCount++
    for (const day of series) {
      const date = currentDate.toISOString().split('T')[0]
      const isInRange = currentDate >= start && currentDate <= end
      day.data.push({
        x: `W${weeksCount}`,
        y: isInRange ? (contributionData[date] ?? 0) : null,
        date,
      })
      currentDate.setUTCDate(currentDate.getUTCDate() + 1)
    }
  }

  return {
    heatmapSeries: series.reverse(),
    weeksCount,
    startDate: start.toISOString().split('T')[0],
    endDate: end.toISOString().split('T')[0],
  }
}
