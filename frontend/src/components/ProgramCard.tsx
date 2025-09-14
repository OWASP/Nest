import { faEye } from '@fortawesome/free-regular-svg-icons'
import { faEdit } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Tooltip } from '@heroui/tooltip'
import type React from 'react'
import { Program } from 'types/mentorship'
import ActionButton from 'components/ActionButton'

interface ProgramCardProps {
  program: Program
  onEdit?: (key: string) => void
  onView: (key: string) => void
  accessLevel: 'admin' | 'user'
}

const ProgramCard: React.FC<ProgramCardProps> = ({ program, onEdit, onView, accessLevel }) => {
  const formatDate = (d: string) =>
    new Date(d).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })

  const roleClass = {
    admin: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    mentor: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    default: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200',
  }

  const description = program.description || 'No description available.'

  // computes a formatted date string for the program based on its start and end dates.
  const dateInfo = (() => {
    if (program.startedAt && program.endedAt) {
      return `${formatDate(program.startedAt)} – ${formatDate(program.endedAt)}`
    } else if (program.startedAt) {
      return `Started: ${formatDate(program.startedAt)}`
    } else {
      return 'No dates set'
    }
  })()

  return (
    <div className="h-72 w-72 rounded-lg border border-gray-400 bg-white p-6 text-left transition-transform duration-300 hover:scale-[1.02] hover:brightness-105 md:h-80 md:w-80 lg:h-80 lg:w-96 dark:border-gray-600 dark:bg-gray-800">
      <div className="flex h-full flex-col">
        <div className="flex flex-1 flex-col pb-8">
          <div className="mb-2 flex items-start justify-between">
            <Tooltip
              closeDelay={100}
              delay={100}
              showArrow
              content={program.name}
              placement="bottom"
              className="w-88"
              isDisabled={program.name.length > 50 ? false : true}
            >
              <h3 className="mr-1 line-clamp-2 h-12 overflow-hidden text-base font-semibold text-gray-600 dark:text-white">
                {program.name}
              </h3>
            </Tooltip>
            {accessLevel === 'admin' && (
              <span
                className={`rounded-full px-2 py-1 text-xs font-medium capitalize ${roleClass[program.userRole] ?? roleClass.default}`}
              >
                {program.userRole}
              </span>
            )}
          </div>
          <div className="mb-2 text-xs text-gray-600 dark:text-gray-400">{dateInfo}</div>
          <p className="mb-4 text-sm text-gray-700 dark:text-gray-300">{description}</p>
        </div>

        <div className="flex gap-2">
          {accessLevel === 'admin' ? (
            <>
              <ActionButton onClick={() => onView(program.key)}>
                <FontAwesomeIcon icon={faEye} className="mr-1" />
                Preview
              </ActionButton>
              <ActionButton onClick={() => onEdit(program.key)}>
                <FontAwesomeIcon icon={faEdit} className="mr-1" />
                Edit
              </ActionButton>
            </>
          ) : (
            <ActionButton onClick={() => onView(program.key)}>
              <FontAwesomeIcon icon={faEye} className="mr-1" />
              View Details
            </ActionButton>
          )}
        </div>
      </div>
    </div>
  )
}

export default ProgramCard
