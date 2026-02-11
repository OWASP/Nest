'use client'
import Link from 'next/link'
import { FaCalendar, FaMapMarkerAlt } from 'react-icons/fa'
import { HiUserGroup } from 'react-icons/hi'
import { formatDate } from 'utils/dateFormatter'
import LeadersList from 'components/LeadersList'
import { TruncatedText } from 'components/TruncatedText'

interface ChapterCardProps {
  chapterKey: string
  name: string
  createdAt: number
  suggestedLocation: string | null
  leaders: string[]
}

const ChapterCard = ({
  chapterKey,
  name,
  createdAt,
  suggestedLocation,
  leaders,
}: ChapterCardProps) => (
  <div className="rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
    <h3 className="mb-2 text-lg font-semibold">
      <Link href={`/chapters/${chapterKey}`} className="text-blue-400 hover:underline">
        <TruncatedText text={name} />
      </Link>
    </h3>
    <div className="flex flex-wrap items-center text-sm text-gray-600 dark:text-gray-400">
      <div className="mr-4 flex items-center">
        <FaCalendar className="mr-2 h-4 w-4" />
        <span>{formatDate(createdAt)}</span>
      </div>
      {suggestedLocation && (
        <div className="flex flex-1 items-center overflow-hidden">
          <FaMapMarkerAlt className="mr-2 h-4 w-4 shrink-0" />
          <TruncatedText text={suggestedLocation} />
        </div>
      )}
    </div>
    {leaders.length > 0 && (
      <div className="mt-1 flex items-center gap-x-2 text-sm text-gray-600 dark:text-gray-400">
        <HiUserGroup className="h-4 w-4 shrink-0" />
        <LeadersList entityKey={`${chapterKey}-leaders`} leaders={String(leaders)} />
      </div>
    )}
  </div>
)

export default ChapterCard
