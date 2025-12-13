import { faCalendar, faCalendarPlus } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useState } from 'react'
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
      className={className}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {icon || (
        <FontAwesomeIcon icon={isHovered ? faCalendarPlus : faCalendar} className={iconClassName} />
      )}
      {showLabel && <span>{label}</span>}
    </a>
  )
}
