import { Tooltip } from '@heroui/tooltip'
import { useUpdateProgramStatus } from 'hooks/useUpdateProgramStatus'
import Link from 'next/link'
import type React from 'react'
import { GetProgramAndModulesDocument } from 'types/__generated__/programsQueries.generated'
import { Program } from 'types/mentorship'
import EntityActions from 'components/EntityActions'

interface ProgramCardProps {
  program: Program
  href: string
  accessLevel: 'admin' | 'user'
  isAdmin: boolean
}

const ProgramCard: React.FC<ProgramCardProps> = ({ program, href, accessLevel, isAdmin }) => {
  const formatDate = (d: string | number) => {
    const date = typeof d === 'number' ? new Date(d * 1000) : new Date(d)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }
  const { updateProgramStatus } = useUpdateProgramStatus({
    programKey: program.key,
    programName: program.name,
    isAdmin,
    refetchQueries: [
      {
        query: GetProgramAndModulesDocument,
        variables: { programKey: program.key },
      },
    ],
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
    <Link
      href={href}
      className="group block h-72 w-72 rounded-lg border border-gray-400 bg-white p-6 text-left transition-transform duration-300 hover:scale-[1.02] hover:brightness-105 md:h-80 md:w-80 lg:h-80 lg:w-96 dark:border-gray-600 dark:bg-gray-800"
    >
      <div className="flex h-full flex-col">
        <div className="flex flex-1 flex-col">
          <div className="mb-2 flex items-start justify-between">
            <Tooltip
              closeDelay={100}
              delay={100}
              showArrow
              content={program.name}
              placement="bottom"
              isDisabled={program.name.length > 50 ? false : true}
            >
              <h3 className="mr-1 line-clamp-2 h-12 overflow-hidden text-base font-semibold text-gray-600 dark:text-white">
                {program.name}
              </h3>
            </Tooltip>
            {accessLevel === 'admin' && isAdmin && (
              <div role="none" onMouseDown={(e) => e.stopPropagation()}>
                <EntityActions
                  type="program"
                  programKey={program.key}
                  status={program.status}
                  setStatus={updateProgramStatus}
                />
              </div>
            )}
          </div>
          <div className="mb-2 text-sm text-gray-600 dark:text-gray-400">
            <span>{dateInfo}</span>
            {accessLevel === 'admin' && program.userRole && (
              <span
                className={`ml-2 rounded-full px-2 py-1 text-xs font-medium capitalize ${
                  roleClass[program.userRole] ?? roleClass.default
                }`}
              >
                {program.userRole}
              </span>
            )}
          </div>
          <p className="line-clamp-8 text-sm text-gray-700 dark:text-gray-300">{description}</p>
        </div>
      </div>
    </Link>
  )
}

export default ProgramCard
