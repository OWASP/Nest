import { capitalize } from 'lodash'
import Image from 'next/image'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import type React from 'react'
import { useState } from 'react'
import { FaChevronDown, FaChevronUp, FaTurnUp, FaCalendar, FaHourglassHalf } from 'react-icons/fa6'
import type { Module } from 'types/mentorship'
import { formatDate } from 'utils/dateFormatter'
import { TextInfoItem } from 'components/InfoItem'
import SingleModuleCard from 'components/SingleModuleCard'
import { TruncatedText } from 'components/TruncatedText'

interface ModuleCardProps {
  modules: Module[]
  accessLevel?: string
  admins?: { login: string }[]
}

const ModuleCard = ({ modules, accessLevel, admins }: ModuleCardProps) => {
  const [showAllModule, setShowAllModule] = useState(false)

  if (modules.length === 1) {
    return <SingleModuleCard module={modules[0]} accessLevel={accessLevel} admins={admins} />
  }

  const displayedModule = showAllModule ? modules : modules.slice(0, 4)

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      setShowAllModule(!showAllModule)
    }
  }

  return (
    <div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3">
        {displayedModule.map((module) => {
          return <ModuleItem key={module.key || module.id} module={module} />
        })}
      </div>
      {modules.length > 4 && (
        <div className="mt-6 flex items-center justify-center text-center">
          <button
            type="button"
            onClick={() => setShowAllModule(!showAllModule)}
            onKeyDown={handleKeyDown}
            className="mt-4 flex items-center justify-center text-blue-600 hover:underline focus:rounded focus:outline-2 focus:outline-offset-2 focus:outline-blue-500 dark:text-blue-300"
          >
            {showAllModule ? (
              <>
                Show less <FaChevronUp className="ml-1" />
              </>
            ) : (
              <>
                Show more <FaChevronDown className="ml-1" />
              </>
            )}
          </button>
        </div>
      )}
    </div>
  )
}

const ModuleItem = ({ module }: { module: Module }) => {
  const pathname = usePathname()

  const mentors = module.mentors || []
  const mentees = module.mentees || []

  const mentorsWithAvatars = mentors.filter((m) => m?.avatarUrl)
  const menteesWithAvatars = mentees.filter((m) => m?.avatarUrl)

  const programKey = pathname?.split('/programs/')[1]?.split('/')[0] || ''
  const moduleKey = module.key || module.id

  const getMenteeUrl = (login: string) => {
    if (pathname?.startsWith('/my/mentorship')) {
      return `/my/mentorship/programs/${programKey}/modules/${moduleKey}/mentees/${login}`
    }
    return `/members/${login}`
  }

  const getAvatarUrlWithSize = (avatarUrl: string): string => {
    try {
      const url = new URL(avatarUrl)
      url.searchParams.set('s', '60')
      return url.toString()
    } catch {
      const separator = avatarUrl.includes('?') ? '&' : '?'
      return `${avatarUrl}${separator}s=60`
    }
  }

  return (
    <div className="flex h-auto min-h-[12rem] w-full flex-col gap-3 rounded-lg border-1 border-gray-200 p-4 text-gray-800 shadow-xs ease-in-out hover:shadow-md dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300">
      <Link
        href={`${pathname}/modules/${module.key}`}
        className="text-start font-semibold text-gray-800 hover:underline dark:text-gray-300"
      >
        <TruncatedText text={module?.name} />
      </Link>
      <TextInfoItem icon={FaTurnUp} label="Level" value={capitalize(module.experienceLevel)} />
      <TextInfoItem icon={FaCalendar} label="Start" value={formatDate(module.startedAt)} />
      <TextInfoItem
        icon={FaHourglassHalf}
        label="Duration"
        value={getSimpleDuration(module.startedAt, module.endedAt)}
      />

      {(mentorsWithAvatars.length > 0 || menteesWithAvatars.length > 0) && (
        <div className="mt-auto flex w-full gap-4">
          {mentorsWithAvatars.length > 0 && (
            <div className="flex flex-1 flex-col gap-2">
              <span className="text-xs font-bold tracking-wider text-gray-800 uppercase dark:text-gray-300">
                Mentors
              </span>
              <div className="flex flex-wrap gap-1">
                {mentorsWithAvatars.slice(0, 4).map((contributor) => (
                  <Link
                    key={contributor.login}
                    href={`/members/${contributor.login}`}
                    className="transition-opacity hover:opacity-80"
                  >
                    <Image
                      alt={contributor.name || contributor.login}
                      className="rounded-full border-1 border-gray-200 dark:border-gray-700"
                      height={24}
                      src={getAvatarUrlWithSize(contributor.avatarUrl)}
                      title={contributor.name || contributor.login}
                      width={24}
                    />
                  </Link>
                ))}
                {mentorsWithAvatars.length > 4 && (
                  <span className="self-center text-xs font-medium text-gray-800 dark:text-gray-300">
                    +{mentorsWithAvatars.length - 4}
                  </span>
                )}
              </div>
            </div>
          )}
          {menteesWithAvatars.length > 0 && (
            <div
              className={`flex flex-1 flex-col gap-2 ${mentorsWithAvatars.length > 0 ? 'border-l-1 border-gray-100 pl-4 dark:border-gray-700' : ''}`}
            >
              <span className="text-xs font-bold tracking-wider text-gray-800 uppercase dark:text-gray-300">
                Mentees
              </span>
              <div className="flex flex-wrap gap-1">
                {menteesWithAvatars.slice(0, 4).map((contributor) => (
                  <Link
                    key={contributor.login}
                    href={getMenteeUrl(contributor.login)}
                    className="transition-opacity hover:opacity-80"
                  >
                    <Image
                      alt={contributor.name || contributor.login}
                      className="rounded-full border-1 border-gray-200 dark:border-gray-700"
                      height={24}
                      src={getAvatarUrlWithSize(contributor.avatarUrl)}
                      title={contributor.name || contributor.login}
                      width={24}
                    />
                  </Link>
                ))}
                {menteesWithAvatars.length > 4 && (
                  <span className="self-center text-xs font-medium text-gray-800 dark:text-gray-300">
                    +{menteesWithAvatars.length - 4}
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ModuleCard

export const getSimpleDuration = (start: string | number, end: string | number): string => {
  if (!start || !end) return 'N/A'

  const startDate = typeof start === 'number' ? new Date(start * 1000) : new Date(start)
  const endDate = typeof end === 'number' ? new Date(end * 1000) : new Date(end)

  if (Number.isNaN(startDate.getTime()) || Number.isNaN(endDate.getTime())) {
    return 'Invalid duration'
  }

  const ms = endDate.getTime() - startDate.getTime()
  const days = Math.floor(ms / (1000 * 60 * 60 * 24))
  const weeks = Math.ceil(days / 7)

  return `${weeks} week${weeks === 1 ? '' : 's'}`
}
