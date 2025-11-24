export const formatDate = (input: number | string) => {
  if (!input) {
    return ''
  }

  let date: Date
  if (typeof input === 'number') {
    date = new Date(input * 1000)
  } else if (!isNaN(Number(input)) && !input.includes('-') && !input.includes(':')) {
    date = new Date(Number(input) * 1000)
  } else {
    date = new Date(input)
  }

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

export const formatDateRange = (startDate: number | string, endDate: number | string) => {
  const parseDate = (inp: number | string) => {
    if (typeof inp === 'number') return new Date(inp * 1000)
    if (!isNaN(Number(inp)) && !inp.includes('-') && !inp.includes(':')) return new Date(Number(inp) * 1000)
    return new Date(inp)
  }

  const start = parseDate(startDate)
  const end = parseDate(endDate)

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
    // Format as "Month Day - Day, Year" (e.g., "Sep 1 - 4, 2025")
    return (
      `${start.toLocaleDateString('en-US', { month: 'short', timeZone: 'UTC' })} ` +
      `${start.getUTCDate()} — ${end.getUTCDate()}, ${start.getUTCFullYear()}`
    )
  } else if (sameYear) {
    // Different months but same year (e.g., "Sep 29 - Oct 2, 2025")
    const startMonth = start.toLocaleDateString('en-US', { month: 'short', timeZone: 'UTC' })
    const endMonth = end.toLocaleDateString('en-US', { month: 'short', timeZone: 'UTC' })
    const startDay = start.getUTCDate()
    const endDay = end.getUTCDate()
    const year = start.getUTCFullYear()

    return `${startMonth} ${startDay} — ${endMonth} ${endDay}, ${year}`
  } else {
    // Different years (e.g., "Dec 30, 2025 - Jan 3, 2026")
    return `${formatDate(startDate)} — ${formatDate(endDate)}`
  }
}

export const formatDateForInput = (dateStr: string | number) => {
  if (!dateStr) return ''
  let date: Date
  if (typeof dateStr === 'number') {
    date = new Date(dateStr * 1000)
  } else if (!isNaN(Number(dateStr)) && !dateStr.includes('-') && !dateStr.includes(':')) {
    date = new Date(Number(dateStr) * 1000)
  } else {
    date = new Date(dateStr)
  }
  if (Number.isNaN(date.getTime())) {
    throw new Error('Invalid date')
  }
  return date.toISOString().slice(0, 10)
}
