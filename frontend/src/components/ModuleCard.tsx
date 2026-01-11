import Link from 'next/link'
import Image from 'next/image'
import { usePathname } from 'next/navigation'
import type React from 'react'
import { useState } from 'react'
import { FaChevronDown, FaChevronUp, FaTurnUp, FaCalendar, FaHourglassHalf } from 'react-icons/fa6'
import type { Module } from 'types/mentorship'
import { formatDate } from 'utils/dateFormatter'
import { TextInfoItem } from 'components/InfoItem'
import { LabelList } from 'components/LabelList'
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
  const isAdmin = accessLevel === 'admin'

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
          return <ModuleItem key={module.key || module.id} module={module} isAdmin={isAdmin} />
        })}
      </div>
      {modules.length > 4 && (
        <div className="mt-6 flex items-center justify-center text-center">
          <button
            type="button"
            onClick={() => setShowAllModule(!showAllModule)}
            onKeyDown={handleKeyDown}
            className="mt-4 flex items-center justify-center text-blue-400 hover:underline focus:rounded focus:outline-2 focus:outline-offset-2 focus:outline-blue-500"
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

const ModuleItem = ({ module, isAdmin }: { module: Module; isAdmin: boolean }) => {
  const pathname = usePathname()

  const mentors = module.mentors || []
  const mentees = module.mentees || []

  const mentorsWithAvatars = mentors.filter((m) => m?.avatarUrl)
  const menteesWithAvatars = mentees.filter((m) => m?.avatarUrl)

  const hasContributors = mentorsWithAvatars.length > 0 || menteesWithAvatars.length > 0

  return (
    <div className="flex h-auto min-h-[12rem] w-full flex-col gap-3 rounded-lg border-1 border-gray-200 p-4 shadow-xs ease-in-out hover:shadow-md dark:border-gray-700 dark:bg-gray-800">
      <Link
        href={`${pathname}/modules/${module.key || module.id}`}
        className="text-start font-semibold text-blue-400 hover:underline"
      >
        <TruncatedText text={module?.name} />
      </Link>
      <TextInfoItem icon={FaTurnUp} label="Level" value={String(module.experienceLevel).toUpperCase()} />
      <TextInfoItem icon={FaCalendar} label="Start" value={formatDate(module.startedAt)} />
      <TextInfoItem
        icon={FaHourglassHalf}
        label="Duration"
        value={getSimpleDuration(module.startedAt, module.endedAt)}
      />

      {hasContributors && (
        <div className="mt-auto flex gap-4 w-full">
          {mentorsWithAvatars.length > 0 && (
            <div className="flex-1 flex flex-col gap-2">
              <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">Mentors</span>
              <div className="flex flex-wrap gap-1">
                {mentorsWithAvatars.slice(0, 4).map((contributor) => (
                  <Image
                    key={contributor.login}
                    alt={contributor.name || contributor.login}
                    className="rounded-full border-1 border-gray-200 dark:border-gray-700"
                    height={24}
                    src={`${contributor.avatarUrl}&s=60`}
                    title={contributor.name || contributor.login}
                    width={24}
                  />
                ))}
                {mentorsWithAvatars.length > 4 && (
                  <span className="text-xs font-medium text-gray-400 self-center">
                    +{mentorsWithAvatars.length - 4}
                  </span>
                )}
              </div>
            </div>
          )}
          {menteesWithAvatars.length > 0 && (
            <div className={`flex-1 flex flex-col gap-2 ${mentorsWithAvatars.length > 0 ? 'border-l-1 border-gray-100 pl-4 dark:border-gray-700' : ''}`}>
              <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">Mentees</span>
              <div className="flex flex-wrap gap-1">
                {menteesWithAvatars.slice(0, 4).map((contributor) => (
                  <Image
                    key={contributor.login}
                    alt={contributor.name || contributor.login}
                    className="rounded-full border-1 border-gray-200 dark:border-gray-700"
                    height={24}
                    src={`${contributor.avatarUrl}&s=60`}
                    title={contributor.name || contributor.login}
                    width={24}
                  />
                ))}
                {menteesWithAvatars.length > 4 && (
                  <span className="text-xs font-medium text-gray-400 self-center">
                    +{menteesWithAvatars.length - 4}
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {isAdmin && module.labels && module.labels.length > 0 && (
        <div className="mt-2">
          <LabelList labels={module.labels} maxVisible={3} />
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
