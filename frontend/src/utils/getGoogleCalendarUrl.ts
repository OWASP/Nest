import type { CalendarEvent } from 'types/calendar'

export type { CalendarEvent }

const pad = (n: number, width = 2) => String(n).padStart(width, '0')

function formatLocalDate(date: Date) {
  const year = date.getFullYear()
  const month = pad(date.getMonth() + 1)
  const day = pad(date.getDate())
  return `${year}${month}${day}`
}

function formatUTCDateTime(date: Date) {
  const year = date.getUTCFullYear()
  const month = pad(date.getUTCMonth() + 1)
  const day = pad(date.getUTCDate())
  const hours = pad(date.getUTCHours())
  const minutes = pad(date.getUTCMinutes())
  const seconds = pad(date.getUTCSeconds())
  return `${year}${month}${day}T${hours}${minutes}${seconds}Z`
}

function detectIsAllDay(dateInput: string | Date): boolean {
  if (dateInput instanceof Date) return false
  return !dateInput.includes('T') && !dateInput.includes(':')
}

export default function getGoogleCalendarUrl(event: CalendarEvent): string {
  if (!event || !event.startDate || !event.title) {
    throw new Error('getGoogleCalendarUrl: event, startDate and title are required')
  }

  const base = 'https://calendar.google.com/calendar/render?action=TEMPLATE'

  const start = new Date(event.startDate)
  if (Number.isNaN(start.getTime())) throw new Error('Invalid startDate')

  const end = event.endDate ? new Date(event.endDate) : new Date(start.getTime() + 60 * 60 * 1000)
  if (Number.isNaN(end.getTime())) throw new Error('Invalid endDate')

  const isAllDay = detectIsAllDay(event.startDate)

  let datesParam: string
  if (isAllDay) {
    const s = formatLocalDate(start)
    const e = formatLocalDate(end)
    datesParam = `${s}/${e}`
  } else {
    const s = formatUTCDateTime(start)
    const e = formatUTCDateTime(end)
    datesParam = `${s}/${e}`
  }

  const params = new URLSearchParams()
  params.set('text', event.title)
  if (event.description) params.set('details', event.description)
  if (event.location) params.set('location', event.location)

  const other = params.toString()
  return other ? `${base}&${other}&dates=${datesParam}` : `${base}&dates=${datesParam}`
}
