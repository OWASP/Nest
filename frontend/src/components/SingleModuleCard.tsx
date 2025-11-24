import { faUsers, faEllipsisV } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { capitalize } from 'lodash'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import React, { useState, useRef, useEffect } from 'react'
import { ExtendedSession } from 'types/auth'
import type { Module } from 'types/mentorship'
import { formatDate } from 'utils/dateFormatter'
import { getSimpleDuration } from 'components/ModuleCard'
import TopContributorsList from 'components/TopContributorsList'

interface SingleModuleCardProps {
  module: Module
  showEdit?: boolean
  accessLevel?: string
  admins?: {
    login: string
  }[]
}

const SingleModuleCard: React.FC<SingleModuleCardProps> = ({
  module,
  showEdit,
  accessLevel,
  admins,
}) => {
  const router = useRouter()
  const { data } = useSession()
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const isAdmin =
    accessLevel === 'admin' &&
    admins?.some((admin) => admin.login === ((data as ExtendedSession)?.user?.login as string))

  const handleEdit = () => {
    setDropdownOpen(false)
    router.push(`${globalThis.location.pathname}/modules/${module.key}/edit`)
  }

  const handleCreate = () => {
    setDropdownOpen(false)
    router.push(`${globalThis.location.pathname}/modules/create`)
  }

  const handleIssue = () => {
    setDropdownOpen(false)
    router.push(`${globalThis.location.pathname}/modules/${module.key}/issues`)
  }

  const moduleDetails = [
    { label: 'Experience Level', value: capitalize(module.experienceLevel) },
    { label: 'Start Date', value: formatDate(module.startedAt) },
    { label: 'End Date', value: formatDate(module.endedAt) },
    { label: 'Duration', value: getSimpleDuration(module.startedAt, module.endedAt) },
  ]

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div className="flex flex-col gap-4 rounded-xl border border-gray-200 p-5 shadow-md dark:border-gray-700">
      <div className="flex items-center justify-between">
        <div className="flex cursor-pointer items-center gap-2">
          <FontAwesomeIcon icon={faUsers} className="text-gray-500 dark:text-gray-300" />
          <Link
            href={`${globalThis.location.pathname}/modules/${module.key}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1"
          >
            <h1
              className="max-w-full text-base font-semibold break-words text-blue-400 hover:text-blue-600 sm:text-lg sm:break-normal lg:text-2xl"
              style={{
                transition: 'color 0.3s ease',
              }}
            >
              {module.name}
            </h1>
          </Link>
        </div>

        {isAdmin && (
          <div className="relative" ref={dropdownRef}>
            <button
              type="button"
              onClick={() => setDropdownOpen((prev) => !prev)}
              className="rounded px-4 py-2 hover:bg-gray-200 dark:hover:bg-gray-700"
            >
              <FontAwesomeIcon icon={faEllipsisV} />
            </button>

            {dropdownOpen && (
              <div className="absolute right-0 z-20 mt-2 w-40 rounded-md border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-800">
                {showEdit && isAdmin && (
                  <button
                    type="button"
                    onClick={handleEdit}
                    className="block w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    Edit Module
                  </button>
                )}
                {isAdmin && (
                  <button
                    type="button"
                    onClick={handleCreate}
                    className="block w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    Create Module
                  </button>
                )}
                {isAdmin && (
                  <button
                    type="button"
                    onClick={handleIssue}
                    className="block w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    View Issues
                  </button>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Description */}
      <div>
        <p>{module.description}</p>
      </div>

      {/* Details */}
      <div className="pt-4">
        {moduleDetails.map((detail) => (
          <div key={detail.label} className="pt-1">
            <strong>{detail.label}:</strong> {detail.value || 'Unknown'}
          </div>
        ))}
      </div>

      {/* Mentors */}
      {module.mentors?.length > 0 && (
        <TopContributorsList
          icon={faUsers}
          contributors={module.mentors}
          maxInitialDisplay={6}
          label="Mentors"
        />
      )}
    </div>
  )
}

export default SingleModuleCard
