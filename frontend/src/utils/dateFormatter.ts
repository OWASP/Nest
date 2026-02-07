export const formatDate = (input: number) => {
  if (!input) {
    return ''
  }

  const date = new Date(input * 1000)

  if (Number.isNaN(date.getTime())) {
    throw new Error('Invalid date')
  }

  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    timeZone: 'UTC',
  })
}

export const formatDateRange = (startDate: number , endDate: number) => {
  const start = new Date(startDate * 1000)
  const end = new Date(endDate * 1000)

  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) {
    throw new Error('Invalid date')
  }

  if (
    start.getTime() === end.getTime() ||
    (start.getUTCFullYear() === end.getUTCFullYear() &&
      start.getUTCMonth() === end.getUTCMonth() &&
      start.getUTCDate() === end.getUTCDate())
  ) {
    return formatDate(startDate)
  }

  const sameMonth =
    start.getUTCMonth() === end.getUTCMonth() && start.getUTCFullYear() === end.getUTCFullYear()
  const sameYear = start.getUTCFullYear() === end.getUTCFullYear()

  if (sameMonth) {
    // Format as "Month Day — Day, Year" (e.g., "Sep 1 — 4, 2025")
    return (
      `${start.toLocaleDateString('en-US', { month: 'short', timeZone: 'UTC' })} ` +
      `${start.getUTCDate()} — ${end.getUTCDate()}, ${start.getUTCFullYear()}`
    )
  } else if (sameYear) {
    // Different months but same year (e.g., "Sep 29 — Oct 2, 2025")
    const startMonth = start.toLocaleDateString('en-US', { month: 'short', timeZone: 'UTC' })
    const endMonth = end.toLocaleDateString('en-US', { month: 'short', timeZone: 'UTC' })
    const startDay = start.getUTCDate()
    const endDay = end.getUTCDate()
    const year = start.getUTCFullYear()

    return `${startMonth} ${startDay} — ${endMonth} ${endDay}, ${year}`
  } else {
    // Different years (e.g., "Dec 30, 2025 — Jan 3, 2026")
    return `${formatDate(startDate)} — ${formatDate(endDate)}`
  }
}

export const formatDateForInput = (dateStr:number) => {
  if (!dateStr) return ''
  const date = new Date(dateStr * 1000)
  if (Number.isNaN(date.getTime())) {
    throw new Error('Invalid date')
  }
  return date.toISOString().slice(0, 10)
}

export interface DateRangeOptions {
  years?: number
  months?: number
  days?: number
}

export interface DateRangeResult {
  startDate: string
  endDate: string
}

function calculateDaysToSubtract(dayOfWeek: number): number {
  return dayOfWeek === 0 ? -1 : -(dayOfWeek + 1)
}

function adjustDateForYearOnly(today: Date, endDate: Date, startDate: Date): void {
  const todayDayOfWeek = today.getUTCDay()
  const daysToSubtract = calculateDaysToSubtract(todayDayOfWeek)

  endDate.setUTCDate(endDate.getUTCDate() + daysToSubtract)
  startDate.setTime(endDate.getTime())
  startDate.setUTCDate(startDate.getUTCDate() - 363) // 364 days including start day
}

function calculateStartDate(today: Date, years: number, months: number, days: number): Date {
  const startDate = new Date(today)
  startDate.setUTCFullYear(today.getUTCFullYear() - years)
  startDate.setUTCMonth(today.getUTCMonth() - months)
  startDate.setUTCDate(today.getUTCDate() - days)
  return startDate
}

export function getDateRange(options: DateRangeOptions = {}): DateRangeResult {
  const { years = 0, months = 0, days = 0 } = options

  const today = new Date()
  today.setUTCHours(0, 0, 0, 0)

  const endDate = new Date(today)
  const startDate = calculateStartDate(today, years, months, days)

  const isYearOnly = years > 0 && months === 0 && days === 0
  if (isYearOnly) {
    adjustDateForYearOnly(today, endDate, startDate)
  }

  return {
    startDate: startDate.toISOString().split('T')[0],
    endDate: endDate.toISOString().split('T')[0],
  }
}
