import type { JSX } from 'react'

export type CalendarEvent = {
  title: string
  description?: string
  location?: string
  startDate: string | Date
  endDate?: string | Date
}

export type CalendarButtonProps = {
  event: CalendarEvent
  className?: string
  iconClassName?: string
  icon?: JSX.Element
  showLabel?: boolean
  label?: string
}
