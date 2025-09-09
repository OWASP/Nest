import { faEye } from '@fortawesome/free-regular-svg-icons'
import { faEdit } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Tooltip } from '@heroui/tooltip'
import type React from 'react'
import { useState, useEffect } from 'react'
import { Program } from 'types/mentorship'
import ActionButton from 'components/ActionButton'

interface ProgramCardProps {
  program: Program
  onEdit?: (key: string) => void
  onView: (key: string) => void
  accessLevel: 'admin' | 'user'
}

const ProgramCard: React.FC<ProgramCardProps> = ({ program, onEdit, onView, accessLevel }) => {
  const [screenSize, setScreenSize] = useState<'sm' | 'md' | 'lg'>('md')

  useEffect(() => {
    const updateScreenSize = () => {
      const width = window.innerWidth
      if (width < 768) {
        setScreenSize('sm')
      } else if (width < 1024) {
        setScreenSize('md')
      } else {
        setScreenSize('lg')
      }
    }

    updateScreenSize()
    window.addEventListener('resize', updateScreenSize)
    return () => window.removeEventListener('resize', updateScreenSize)
  }, [])

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

  const titleThresholds = { sm: 40, md: 60, lg: 80 }
  const descriptionThresholds = { sm: 150, md: 200, lg: 250 }

  const isTitleLong = program.name.length > titleThresholds[screenSize]
  const isDescriptionLong = description.length > descriptionThresholds[screenSize]

  return (
    <div className="h-64 w-80 rounded-[5px] border border-gray-400 bg-white p-6 text-left transition-transform duration-300 hover:scale-[1.02] hover:brightness-105 dark:border-gray-600 dark:bg-gray-800">
      <div className="flex h-full flex-col">
        <div className="flex flex-1 flex-col">
          <div className="mb-2 flex items-start justify-between">
            {isTitleLong ? (
              <Tooltip content={program.name} placement="top" className="w-64">
                <h3 className="line-clamp-2 h-12 overflow-hidden text-base font-semibold text-gray-600 dark:text-white">
                  {program.name}
                </h3>
              </Tooltip>
            ) : (
              <h3 className="line-clamp-2 h-12 overflow-hidden text-base font-semibold text-gray-600 dark:text-white">
                {program.name}
              </h3>
            )}
            {accessLevel === 'admin' && (
              <span
                className={`rounded-full px-2 py-1 text-xs font-medium capitalize ${roleClass[program.userRole] ?? roleClass.default}`}
              >
                {program.userRole}
              </span>
            )}
          </div>
          <div className="mb-2 text-sm text-gray-600 dark:text-gray-400">
            {program.startedAt && program.endedAt
              ? `${formatDate(program.startedAt)} – ${formatDate(program.endedAt)}`
              : program.startedAt
                ? `Started: ${formatDate(program.startedAt)}`
                : 'No dates set'}
          </div>
          <div className="flex flex-1 flex-col justify-start">
            {isDescriptionLong ? (
              <Tooltip content={description} placement="bottom" className="w-88">
                <p className="line-clamp-4 overflow-hidden text-sm text-gray-700 dark:text-gray-300">
                  {description}
                </p>
              </Tooltip>
            ) : (
              <p className="line-clamp-4 overflow-hidden text-sm text-gray-700 dark:text-gray-300">
                {description}
              </p>
            )}
          </div>
        </div>

        <div className="mt-auto flex gap-2">
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
