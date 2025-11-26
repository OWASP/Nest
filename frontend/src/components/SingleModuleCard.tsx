'use client'

import { faUsers } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { capitalize } from 'lodash'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useSession } from 'next-auth/react'
import React from 'react'
import { ExtendedSession } from 'types/auth'
import type { Module } from 'types/mentorship'
import { formatDate } from 'utils/dateFormatter'
import EntityActions from 'components/EntityActions'
import { getSimpleDuration } from 'components/ModuleCard'
import TopContributorsList from 'components/TopContributorsList'

interface SingleModuleCardProps {
  module: Module
  accessLevel?: string
  admins?: {
    login: string
  }[]
}

const SingleModuleCard: React.FC<SingleModuleCardProps> = ({ module, accessLevel, admins }) => {
  const { data } = useSession()
  const pathname = usePathname()

  const isAdmin =
    accessLevel === 'admin' &&
    admins?.some((admin) => admin.login === ((data as ExtendedSession)?.user?.login as string))

  // Extract programKey from pathname (e.g., /my/mentorship/programs/[programKey])
  const programKey = pathname?.split('/programs/')[1]?.split('/')[0] || ''

  const moduleDetails = [
    { label: 'Experience Level', value: capitalize(module.experienceLevel) },
    { label: 'Start Date', value: formatDate(module.startedAt) },
    { label: 'End Date', value: formatDate(module.endedAt) },
    { label: 'Duration', value: getSimpleDuration(module.startedAt, module.endedAt) },
  ]

  return (
    <div className="flex flex-col gap-4 rounded-xl border border-gray-200 p-5 shadow-md dark:border-gray-700">
      <div className="flex items-center justify-between">
        <div className="flex cursor-pointer items-center gap-2">
          <FontAwesomeIcon icon={faUsers} className="text-gray-500 dark:text-gray-300" />
          <Link
            href={`${pathname}/modules/${module.key}`}
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

        {isAdmin && <EntityActions type="module" programKey={programKey} moduleKey={module.key} />}
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
