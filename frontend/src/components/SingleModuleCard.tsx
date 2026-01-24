'use client'

import { capitalize } from 'lodash'
import upperFirst from 'lodash/upperFirst'
import Image from 'next/image'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useSession } from 'next-auth/react'
import React, { useState } from 'react'
import { FaFolderOpen } from 'react-icons/fa'
import { HiUserGroup } from 'react-icons/hi'
import type { ExtendedSession } from 'types/auth'
import type { Contributor } from 'types/contributor'
import type { Module } from 'types/mentorship'
import { formatDate } from 'utils/dateFormatter'
import { getMemberUrl } from 'utils/urlFormatter'
import EntityActions from 'components/EntityActions'
import Markdown from 'components/MarkdownWrapper'
import { getSimpleDuration } from 'components/ModuleCard'
import ShowMoreButton from 'components/ShowMoreButton'

interface SingleModuleCardProps {
  module: Module
  accessLevel?: string
  admins?: {
    login: string
  }[]
}

const SingleModuleCard: React.FC<SingleModuleCardProps> = ({ module, accessLevel, admins }) => {
  const { data: sessionData } = useSession() as { data: ExtendedSession | null }
  const pathname = usePathname()
  const [showAllMentors, setShowAllMentors] = useState(false)
  const [showAllMentees, setShowAllMentees] = useState(false)

  const currentUserLogin = sessionData?.user?.login

  const isAdmin =
    accessLevel === 'admin' && admins?.some((admin) => admin.login === currentUserLogin)

  const isMentor = module.mentors?.some((mentor) => mentor.login === currentUserLogin)

  // Extract programKey from pathname (e.g., /my/mentorship/programs/[programKey])
  const programKey = pathname?.split('/programs/')[1]?.split('/')[0] || ''

  const moduleDetails = [
    { label: 'Experience Level', value: capitalize(module.experienceLevel) },
    { label: 'Start Date', value: formatDate(module.startedAt) },
    { label: 'End Date', value: formatDate(module.endedAt) },
    { label: 'Duration', value: getSimpleDuration(module.startedAt, module.endedAt) },
  ]

  const maxInitialDisplay = 6
  const displayMentors = showAllMentors
    ? module.mentors
    : module.mentors?.slice(0, maxInitialDisplay)
  const displayMentees = showAllMentees
    ? module.mentees
    : module.mentees?.slice(0, maxInitialDisplay)

  const isPrivateView = pathname?.startsWith('/my/mentorship')

  const renderContributors = (
    contributors: Contributor[] | undefined,
    displayContributors: Contributor[] | undefined,
    label: string,
    showAll: boolean,
    toggleShowAll: () => void,
    isMentee = false
  ) => {
    if (!contributors || contributors.length === 0) return null

    return (
      <div className="pt-4">
        <h3 className="mb-4 flex items-center gap-2 text-xl font-semibold">
          <HiUserGroup className="h-5 w-5" />
          {label}
        </h3>
        <div className="grid gap-4 sm:grid-cols-1 md:grid-cols-3 lg:grid-cols-4">
          {displayContributors?.map((contributor) => (
            <div
              key={contributor.login}
              className="overflow-hidden rounded-lg bg-gray-200 p-4 dark:bg-gray-700"
            >
              <div className="flex w-full items-center gap-2">
                <Image
                  alt={contributor?.name ? `${contributor.name}'s avatar` : `${label} avatar`}
                  className="rounded-full"
                  height={24}
                  src={`${contributor?.avatarUrl}&s=60`}
                  title={contributor?.name || contributor?.login}
                  width={24}
                />
                <Link
                  className="cursor-pointer overflow-hidden font-semibold text-ellipsis whitespace-nowrap text-blue-400 hover:underline"
                  href={
                    isMentee && isPrivateView
                      ? `/my/mentorship/programs/${programKey}/modules/${module.key}/mentees/${contributor.login}`
                      : getMemberUrl(contributor?.login)
                  }
                  title={contributor?.name || contributor?.login}
                >
                  {upperFirst(contributor.name) || upperFirst(contributor.login)}
                </Link>
              </div>
            </div>
          ))}
        </div>
        {contributors.length > maxInitialDisplay && <ShowMoreButton onToggle={toggleShowAll} />}
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-4 rounded-lg bg-gray-100 p-6 dark:bg-gray-800">
      <div className="flex items-center justify-between">
        <div className="flex cursor-pointer items-center gap-2">
          <FaFolderOpen className="h-5 w-5 text-gray-500 dark:text-gray-300" />
          <Link href={`${pathname}/modules/${module.key}`} className="flex-1">
            <h2 className="max-w-full text-2xl font-semibold break-words text-blue-400 transition-colors duration-300 hover:text-blue-600 sm:break-normal">
              {module.name}
            </h2>
          </Link>
        </div>

        {(isAdmin || isMentor) && (
          <EntityActions
            type="module"
            programKey={programKey}
            moduleKey={module.key}
            isAdmin={isAdmin}
          />
        )}
      </div>

      {/* Description */}
      <div>
        <Markdown content={module.description || 'No description available.'} />
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
      {renderContributors(module.mentors, displayMentors, 'Mentors', showAllMentors, () =>
        setShowAllMentors(!showAllMentors)
      )}

      {/* Mentees */}
      {renderContributors(
        module.mentees,
        displayMentees,
        'Mentees',
        showAllMentees,
        () => setShowAllMentees(!showAllMentees),
        true
      )}
    </div>
  )
}

export default SingleModuleCard
