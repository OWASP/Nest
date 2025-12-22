'use client'

import { addToast } from '@heroui/toast'
import { useState } from 'react'
import { FaCalendar, FaCalendarPlus } from 'react-icons/fa6'
import type { CalendarButtonProps } from 'types/calendar'
import getIcsFileUrl from 'utils/getIcsFileUrl'
import slugify from 'utils/slugify'

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
      link.setAttribute('download', `${slugify(event.title)}.ics`)
      document.body.appendChild(link)
      link.click()
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('Failed to download ICS file:', err)
      addToast({
        description: 'Failed to download ICS file',
        title: 'Download Failed',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'danger',
        variant: 'solid',
      })
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
      disabled={isDownloading}
      aria-label={ariaLabel}
      title={ariaLabel}
      className={`${className} flex items-center`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {icon ||
        (isHovered ? (
          <FaCalendarPlus className={iconClassName} />
        ) : (
          <FaCalendar className={iconClassName} />
        ))}
      {showLabel && <span>{label}</span>}
    </button>
  )
}
