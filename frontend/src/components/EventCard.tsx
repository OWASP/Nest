import React from 'react'
import { FaCalendar } from 'react-icons/fa'
import type { Event } from 'types/event'
import { formatDate } from 'utils/dateFormatter'

interface EventCardProps {
  event: Event
}

const EventCard: React.FC<EventCardProps> = ({ event }) => (
  <a
    href={event.url}
    target="_blank"
    rel="noopener noreferrer"
    className="block rounded-lg bg-gray-200 p-4 dark:bg-gray-700"
  >
    <div className="flex items-start justify-between">
      <div>
        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100">{event.name}</h3>
        {event.summary && (
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">{event.summary}</p>
        )}
        <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
          <span className="flex items-center gap-1">
            <FaCalendar className="h-3 w-3" />
            {formatDate(event.startDate)}
            {event.endDate && ` - ${formatDate(event.endDate)}`}
          </span>
          {event.suggestedLocation && <span>{event.suggestedLocation}</span>}
        </div>
      </div>
      {event.category && (
        <span className="rounded-full bg-blue-100 px-2 py-1 text-xs font-medium text-blue-800 dark:bg-blue-900 dark:text-blue-200">
          {event.category}
        </span>
      )}
    </div>
  </a>
)

export default EventCard
