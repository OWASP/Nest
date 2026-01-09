export const formatDate = (input: number | string) => {
  if (!input) {
    return ''
  }

  const date =
    typeof input === 'number'
      ? new Date(input * 1000) // Unix timestamp in seconds
      : new Date(input) // ISO date string

  if (Number.isNaN(date.getTime())) {
    throw new Error('Invalid date')
  }

  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

export const formatDateRange = (startDate: number | string, endDate: number | string) => {
  const start = typeof startDate === 'number' ? new Date(startDate * 1000) : new Date(startDate)
  const end = typeof endDate === 'number' ? new Date(endDate * 1000) : new Date(endDate)

  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) {
    throw new Error('Invalid date')
  }

  if (
    start.getTime() === end.getTime() ||
    (start.getFullYear() === end.getFullYear() &&
      start.getMonth() === end.getMonth() &&
      start.getDate() === end.getDate())
  ) {
    return formatDate(startDate)
  }

  const sameMonth = start.getMonth() === end.getMonth() && start.getFullYear() === end.getFullYear()
  const sameYear = start.getFullYear() === end.getFullYear()

  if (sameMonth) {
    // Format as "Month Day - Day, Year" (e.g., "Sep 1 - 4, 2025")
    return (
      `${start.toLocaleDateString('en-US', { month: 'short' })} ` +
      `${start.getDate()} — ${end.getDate()}, ${start.getFullYear()}`
    )
  } else if (sameYear) {
    // Different months but same year (e.g., "Sep 29 - Oct 2, 2025")
    const startMonth = start.toLocaleDateString('en-US', { month: 'short' })
    const endMonth = end.toLocaleDateString('en-US', { month: 'short' })
    const startDay = start.getDate()
    const endDay = end.getDate()
    const year = start.getFullYear()

    return `${startMonth} ${startDay} — ${endMonth} ${endDay}, ${year}`
  } else {
    // Different years (e.g., "Dec 30, 2025 - Jan 3, 2026")
    return `${formatDate(startDate)} — ${formatDate(endDate)}`
  }
}

export const formatDateForInput = (dateStr: string | number) => {
  if (!dateStr) return ''
  const date = typeof dateStr === 'number' ? new Date(dateStr * 1000) : new Date(dateStr)
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
  const todayDayOfWeek = today.getDay()
  const daysToSubtract = calculateDaysToSubtract(todayDayOfWeek)

  endDate.setDate(endDate.getDate() + daysToSubtract)
  startDate.setTime(endDate.getTime())
  startDate.setDate(startDate.getDate() - 363) // 364 days including start day
}

function calculateStartDate(today: Date, years: number, months: number, days: number): Date {
  const startDate = new Date(today)
  startDate.setFullYear(today.getFullYear() - years)
  startDate.setMonth(today.getMonth() - months)
  startDate.setDate(today.getDate() - days)
  return startDate
}

export function getDateRange(options: DateRangeOptions = {}): DateRangeResult {
  const { years = 0, months = 0, days = 0 } = options

  const today = new Date()
  today.setHours(0, 0, 0, 0)

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
