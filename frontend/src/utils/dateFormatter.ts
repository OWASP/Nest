const toISODateString = (input: string): string => {
  if (input.includes('/')) {
    const parts = input.split('/')
    // YYYY/MM/DD format
    if (parts[0].length === 4) {
      return `${parts[0]}-${parts[1]}-${parts[2]}`
    }
    // MM/DD/YYYY format
    return `${parts[2]}-${parts[0]}-${parts[1]}`
  }
  return input
}

/**
 * Formats a date value into a human-readable string (e.g., "Sep 1, 2023").
 *
 * @param input - A Unix timestamp in seconds or a date string (ISO 8601, MM/DD/YYYY, or YYYY/MM/DD).
 * @returns A formatted date string in "MMM D, YYYY" format, or an empty string if input is falsy.
 * @throws {TypeError} If the input cannot be parsed into a valid date.
 */
export const formatDate = (input: number | string) => {
  if (!input) {
    return ''
  }

  const date =
    typeof input === 'number'
      ? new Date(input * 1000) // Unix timestamp in seconds
      : new Date(toISODateString(input))

  if (Number.isNaN(date.getTime())) {
    throw new TypeError('Invalid date')
  }

  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    timeZone: 'UTC',
  })
}

/**
 * Formats a date range into a concise human-readable string.
 *
 * Produces compact output depending on whether dates share the same month, year, or neither:
 * - Same day: "Sep 1, 2025"
 * - Same month: "Sep 1 — 4, 2025"
 * - Same year: "Sep 29 — Oct 2, 2025"
 * - Different years: "Dec 30, 2025 — Jan 3, 2026"
 *
 * @param startDate - The range start as a Unix timestamp in seconds or a date string.
 * @param endDate - The range end as a Unix timestamp in seconds or a date string.
 * @returns A formatted date range string.
 * @throws {TypeError} If either date cannot be parsed into a valid date.
 */
export const formatDateRange = (startDate: number | string, endDate: number | string) => {
  const start = typeof startDate === 'number' ? new Date(startDate * 1000) : new Date(startDate)
  const end = typeof endDate === 'number' ? new Date(endDate * 1000) : new Date(endDate)

  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) {
    throw new TypeError('Invalid date')
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

/**
 * Formats a date value into an ISO date string suitable for HTML date inputs ("YYYY-MM-DD").
 *
 * @param dateStr - A Unix timestamp in seconds or a date string.
 * @returns A date string in "YYYY-MM-DD" format, or an empty string if input is falsy.
 * @throws {TypeError} If the input cannot be parsed into a valid date.
 */
export const formatDateForInput = (dateStr: string | number) => {
  if (!dateStr) return ''
  const date = typeof dateStr === 'number' ? new Date(dateStr * 1000) : new Date(dateStr)
  if (Number.isNaN(date.getTime())) {
    throw new TypeError('Invalid date')
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

/**
 * Calculates a date range by subtracting the specified duration from today's date.
 *
 * When only `years` is specified, the range is aligned to end on the nearest preceding
 * Saturday and span 364 days (52 full weeks).
 *
 * @param options - An object specifying the duration to subtract, with optional `years`, `months`, and `days` fields.
 * @returns An object containing `startDate` and `endDate` as ISO date strings ("YYYY-MM-DD").
 */
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
