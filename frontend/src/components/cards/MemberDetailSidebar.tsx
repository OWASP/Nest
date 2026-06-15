import Image from 'next/image'
import Link from 'next/link'
import React from 'react'
import { FaCodeMerge, FaFolderOpen, FaPersonWalkingArrowRight, FaUserPlus } from 'react-icons/fa6'

import { User } from 'types/user'
import { formatDate } from 'utils/dateFormatter'
import InfoBlock from 'components/InfoBlock'

type Detail = {
  label: string
  value: string
}

type Stat = {
  icon: typeof FaCodeMerge
  pluralizedName?: string
  unit: string
  value: number
}

interface MemberDetailSidebarProps {
  user: User
  formattedBio: React.ReactNode
}

const MemberDetailSidebar = ({ user, formattedBio }: MemberDetailSidebarProps) => {
  const details: Detail[] = [
    { label: 'Joined', value: user.createdAt ? formatDate(user.createdAt) : 'Not available' },
    { label: 'Email', value: user.email || 'N/A' },
    { label: 'Company', value: user.company || 'N/A' },
    { label: 'Location', value: user.location || 'N/A' },
  ]

  const stats: Stat[] = [
    { icon: FaPersonWalkingArrowRight, value: user.followersCount || 0, unit: 'Follower' },
    { icon: FaUserPlus, value: user.followingCount || 0, unit: 'Following' },
    {
      icon: FaFolderOpen,
      pluralizedName: 'Repositories',
      unit: 'Repository',
      value: user.publicRepositoriesCount ?? 0,
    },
    { icon: FaCodeMerge, value: user.contributionsCount || 0, unit: 'Contribution' },
  ]

  return (
    <div className="h-fit flex flex-col sm:flex-row xl:flex-col gap-6 sm:gap-8">
      <div className="flex min-w-0 flex-col items-start gap-0 text-left sm:flex-1 xl:flex-col xl:items-start">
        <Image
          width={200}
          height={200}
          className="aspect-square size-32 shrink-0 rounded-full border-2 border-white bg-white object-cover sm:size-40 xl:h-auto xl:w-full dark:border-gray-800 dark:bg-gray-600/60"
          src={user.avatarUrl || '/placeholder.svg'}
          alt={user.name || user.login || 'User Avatar'}
        />
        <div className="mt-6 mb-2 w-full overflow-x-auto text-left">
          <h2 className="text-3xl font-semibold text-gray-900 dark:text-gray-100">
            {user.name || user.login}
          </h2>
          <Link
            href={user.url || '#'}
            className="text-base text-gray-500 hover:underline dark:text-gray-400"
          >
            @{user.login}
          </Link>
          <div className="mt-4 text-base leading-relaxed wrap-break-word whitespace-pre-wrap text-gray-600 dark:text-gray-400">
            {formattedBio}
          </div>
        </div>
      </div>

      <div className="flex flex-col gap-0 sm:w-72 sm:shrink-0 sm:gap-6 xl:w-full xl:gap-0">
        <div className="space-y-4 border-t border-gray-200 py-5 text-base text-gray-600 dark:border-gray-700 dark:text-gray-300 sm:rounded-lg sm:border-t-0 sm:bg-gray-100 sm:p-6 sm:shadow-md sm:dark:bg-gray-800 xl:rounded-none xl:border-t xl:bg-transparent xl:px-0 xl:py-5 xl:shadow-none xl:dark:bg-transparent">
          {details.map((detail) => (
            <div key={detail.label} className="flex items-start gap-1">
              <strong className="text-gray-800 dark:text-gray-100">{detail.label} : </strong>
              <span>{detail.value}</span>
            </div>
          ))}
        </div>

        <div className="space-y-4 border-t border-gray-200 py-5 text-base text-gray-600 dark:border-gray-700 dark:text-gray-300 sm:rounded-lg sm:border-t-0 sm:bg-gray-100 sm:p-6 sm:shadow-md sm:dark:bg-gray-800 xl:rounded-none xl:border-t xl:bg-transparent xl:px-0 xl:py-5 xl:shadow-none xl:dark:bg-transparent">
          {stats.map((stat) => (
            <InfoBlock
              key={`${stat.unit}-${stat.value}`}
              icon={stat.icon}
              label={stat.pluralizedName ?? stat.unit}
              pluralizedName={stat.pluralizedName}
              unit={stat.unit}
              value={stat.value}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

export default MemberDetailSidebar
