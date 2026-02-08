import type { ReactNode } from 'react'

export type CalendarEvent = {
  title: string
  description?: string
  location?: string
  startDate: number
  endDate?: number
  url?: string
}

export type CalendarButtonProps = Readonly<{
  event: CalendarEvent
  className?: string
  iconClassName?: string
  icon?: ReactNode
  showLabel?: boolean
  label?: string
}>
