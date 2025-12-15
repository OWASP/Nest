import { useState } from 'react'
import { FaCalendar, FaCalendarPlus } from 'react-icons/fa6'
import type { CalendarButtonProps } from 'types/calendar'
import getGoogleCalendarUrl from 'utils/getGoogleCalendarUrl'

export default function CalendarButton(props: Readonly<CalendarButtonProps>) {
  const [isHovered, setIsHovered] = useState(false)
  const {
    event,
    className = '',
    iconClassName = 'h-4 w-4',
    icon,
    showLabel = false,
    label = 'Add to Google Calendar',
  } = props
  const href = getGoogleCalendarUrl(event)
  const safeTitle = event.title || 'event'
  const ariaLabel = `Add ${safeTitle} to Google Calendar`

  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      aria-label={ariaLabel}
      title={ariaLabel}
      className={`flex items-center ${className}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {icon || (
        isHovered
          ? <FaCalendarPlus className={iconClassName} />
          : <FaCalendar className={iconClassName} />
      )}
      {showLabel && <span>{label}</span>}
    </a>
  )
}
