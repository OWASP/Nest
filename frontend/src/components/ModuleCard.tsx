import {
  faChevronDown,
  faChevronUp,
  faLevelUpAlt,
  faCalendarAlt,
  faHourglassHalf,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { capitalize } from 'lodash'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
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
    return (
      <SingleModuleCard
        module={modules[0]}
        showEdit={!!accessLevel && accessLevel === 'admin'}
        accessLevel={accessLevel}
        admins={admins}
      />
    )
  }

  const displayedModule = showAllModule ? modules : modules.slice(0, 4)

  return (
    <div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
        {displayedModule.map((module) => {
          return <ModuleItem key={module.key || module.id} details={module} />
        })}
      </div>
      {modules.length > 4 && (
        <div className="mt-6 flex items-center justify-center text-center">
          <button
            type="button"
            onClick={() => setShowAllModule(!showAllModule)}
            className="mt-4 flex items-center justify-center text-blue-400 hover:underline"
          >
            {showAllModule ? (
              <>
                Show less <FontAwesomeIcon icon={faChevronUp} className="ml-1" />
              </>
            ) : (
              <>
                Show more <FontAwesomeIcon icon={faChevronDown} className="ml-1" />
              </>
            )}
          </button>
        </div>
      )}
    </div>
  )
}

const ModuleItem = ({ details }: { details: Module }) => {
  const router = useRouter()
  const handleClick = () => {
    router.push(`${globalThis.location.pathname}/modules/${details.key}`)
  }

  return (
    <div className="flex h-46 w-full flex-col gap-3 rounded-lg border-1 border-gray-200 p-4 shadow-xs ease-in-out hover:shadow-md dark:border-gray-700 dark:bg-gray-800">
      <button
        type="button"
        onClick={handleClick}
        className="text-start font-semibold text-blue-400 hover:underline"
      >
        <TruncatedText text={details?.name} />
      </button>
      <TextInfoItem icon={faLevelUpAlt} label="Level" value={capitalize(details.experienceLevel)} />
      <TextInfoItem icon={faCalendarAlt} label="Start" value={formatDate(details.startedAt)} />
      <TextInfoItem
        icon={faHourglassHalf}
        label="Duration"
        value={getSimpleDuration(details.startedAt, details.endedAt)}
      />
    </div>
  )
}

export default ModuleCard

export const getSimpleDuration = (start: string, end: string): string => {
  const startDate = new Date(start)
  const endDate = new Date(end)
  if (Number.isNaN(startDate.getTime()) || Number.isNaN(endDate.getTime())) {
    return 'Invalid duration'
  }

  const ms = endDate.getTime() - startDate.getTime()
  const days = Math.floor(ms / (1000 * 60 * 60 * 24))

  const weeks = Math.ceil(days / 7)
  return `${weeks} week${weeks !== 1 ? 's' : ''}`
}
