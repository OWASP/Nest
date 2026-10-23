export const formatDate = (input: string | null) => {
  if (input === null || input === '') {
    return ''
  }

  const date = new Date(input)
  if (Number.isNaN(date.getTime())) return ''

  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    timeZone: 'UTC',
  })
}

export const formatDateRange = (startDate: string, endDate: string) => {
  const start = new Date(startDate)
  const end = new Date(endDate)

  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) {
    return ''
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

export const formatDateForInput = (input: string | null) => {
  if (!input) return ''

  const date = new Date(input)
  if (Number.isNaN(date.getTime())) return ''

  return date.toISOString().slice(0, 10)
}
