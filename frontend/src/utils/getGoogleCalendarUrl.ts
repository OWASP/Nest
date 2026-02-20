export type { CalendarEvent } from 'types/calendar'
import type { CalendarEvent } from 'types/calendar'

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

// All-day events have timestamps at midnight UTC (divisible by 86400 seconds)
const isAllDayEvent = (timestamp: number) => timestamp % 86400 === 0

export default function getGoogleCalendarUrl(event: CalendarEvent): string {
  if (!event?.startDate || !event.title) {
    throw new Error('getGoogleCalendarUrl: event, startDate and title are required')
  }

  const base = 'https://calendar.google.com/calendar/render?action=TEMPLATE'

  const start = new Date(event.startDate * 1000)
  if (Number.isNaN(start.getTime())) throw new Error('Invalid startDate')

  const end = event.endDate
    ? new Date(event.endDate * 1000)
    : new Date(start.getTime() + 60 * 60 * 1000)
  if (Number.isNaN(end.getTime())) throw new Error('Invalid endDate')

  const isAllDay = isAllDayEvent(event.startDate)

  let datesParam: string
  if (isAllDay) {
    const s = formatLocalDate(start)
    const endExclusive = new Date(end.getTime() + 24 * 60 * 60 * 1000)
    const e = formatLocalDate(endExclusive)
    datesParam = `${s}/${e}`
  } else {
    const s = formatUTCDateTime(start)
    const e = formatUTCDateTime(end)
    datesParam = `${s}/${e}`
  }

  const params = new URLSearchParams()
  params.set('text', event.title)

  let details = event.description || ''
  if (event.url) {
    details = details ? `${details}\n\n${event.url}` : event.url
  }
  if (details) params.set('details', details)

  if (event.location) params.set('location', event.location)

  const other = params.toString()
  return other ? `${base}&${other}&dates=${datesParam}` : `${base}&dates=${datesParam}`
}
