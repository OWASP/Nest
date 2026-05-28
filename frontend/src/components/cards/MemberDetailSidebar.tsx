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
    <div className="h-fit space-y-6 md:space-y-8">
      <div className="flex flex-col items-start text-left">
        <Image
          width={200}
          height={200}
          className="aspect-square h-auto w-full rounded-full border-2 border-white bg-white object-cover dark:border-gray-800 dark:bg-gray-600/60"
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
          <p className="mt-4 text-base leading-relaxed text-gray-600 dark:text-gray-400">{formattedBio}</p>
        </div>
      </div>

      <div className="space-y-3 border-t border-gray-200 py-5 dark:border-gray-700">
        <div className="space-y-4 text-base text-gray-600 dark:text-gray-300">
          {details.map((detail) => (
            <div key={detail.label} className="flex items-start gap-1">
              <strong className="text-gray-800 dark:text-gray-100">{detail.label} : </strong>
              <span>{detail.value}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="space-y-3 border-t border-gray-200 py-5 dark:border-gray-700">
        <div className="space-y-4 text-base text-gray-600 dark:text-gray-300">
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
