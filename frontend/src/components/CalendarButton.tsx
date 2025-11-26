import { faCalendarPlus } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import type { CalendarButtonProps } from 'types/calendar'
import getGoogleCalendarUrl from 'utils/getGoogleCalendarUrl'

export default function CalendarButton({
  event,
  className = '',
  iconClassName = '',
  icon,
  showLabel = false,
  label = 'Add to Google Calendar',
}: CalendarButtonProps) {
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
    >
      {icon || <FontAwesomeIcon icon={faCalendarPlus} className={iconClassName} />}
      {showLabel && <span>{label}</span>}
    </a>
  )
}
