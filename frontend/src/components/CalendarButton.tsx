'use client'

import { faCalendar, faCalendarPlus } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useState } from 'react'
import type { CalendarButtonProps } from 'types/calendar'
import getIcsFileUrl from 'utils/getIcsFileUrl'

export default function CalendarButton(props: Readonly<CalendarButtonProps>) {
  const [isHovered, setIsHovered] = useState(false)
  const [isDownloading, setIsDownloading] = useState(false)
  const {
    event,
    className = '',
    iconClassName = 'h-4 w-4',
    icon,
    showLabel = false,
    label = 'Add to Calendar',
  } = props
  const safeTitle = event.title || 'event'
  const ariaLabel = `Add ${safeTitle} to Calendar`

  const handleDownload = async () => {
    let url: string | null = null
    let link: HTMLAnchorElement | null = null
    try {
      setIsDownloading(true)
      url = await getIcsFileUrl(event)
      link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'invite.ics')
      document.body.appendChild(link)
      link.click()
    } catch {
      alert('Could not download calendar file.')
    } finally {
      if (link) link.remove()
      if (url) URL.revokeObjectURL(url)
      setIsDownloading(false)
    }
  }

  return (
    <button
      type="button"
      onClick={handleDownload}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      disabled={isDownloading}
      aria-label={ariaLabel}
      title={ariaLabel}
      className={className}
    >
      {icon || (
        <FontAwesomeIcon icon={isHovered ? faCalendarPlus : faCalendar} className={iconClassName} />
      )}
      {showLabel && <span>{label}</span>}
    </button>
  )
}
