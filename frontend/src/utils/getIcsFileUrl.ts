import { createEvent, DateArray, EventAttributes } from 'ics'
import type { CalendarEvent } from 'types/calendar'

export default function getIcsFileUrl(event: CalendarEvent): Promise<string> {
  return new Promise((resolve, reject) => {
    if (globalThis.window === undefined) {
      reject(new Error('Window not defined (server-side generation not supported)'))
      return
    }
    const parseDate = (date: number): DateArray => {
      // Unix timestamp in seconds
      const d = new Date(date * 1000)
      return [d.getUTCFullYear(), d.getUTCMonth() + 1, d.getUTCDate()]
    }

    const getEndDate = (start: DateArray, end: DateArray): DateArray => {
      if (start.join('-') === end.join('-')) {
        const [y, m, d] = end
        const nextDay = new Date(y, m - 1, d + 1)
        return [nextDay.getFullYear(), nextDay.getMonth() + 1, nextDay.getDate()]
      }
      return end
    }

    const startArray = parseDate(event.startDate)
    const rawEndArray = parseDate(event.endDate ?? event.startDate)
    const finalEndArray = getEndDate(startArray, rawEndArray)

    const eventAttributes: EventAttributes = {
      start: startArray,
      end: finalEndArray,
      title: event.title,
      status: 'CONFIRMED',
      busyStatus: 'BUSY',
      ...(event.description && { description: event.description }),
      ...(event.location && { location: event.location }),
      ...(event.url && { url: event.url }),
    }

    createEvent(eventAttributes, (error, value) => {
      if (error) {
        reject(error)
        return
      }

      const blob = new Blob([value], { type: 'text/calendar;charset=utf-8' })
      resolve(globalThis.URL.createObjectURL(blob))
    })
  })
}
