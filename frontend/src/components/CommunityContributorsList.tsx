import upperFirst from 'lodash/upperFirst'
import Image from 'next/image'
import Link from 'next/link'
import type { IconType } from 'react-icons'
import { twMerge } from 'tailwind-merge'
import type { Contributor } from 'types/contributor'
import AnchorTitle from 'components/AnchorTitle'
import SecondaryCard from 'components/SecondaryCard'

interface CommunityContributorsListProps {
  contributors: Contributor[]
  title?: string
  maxInitialDisplay?: number
  icon?: IconType
  getUrl: (login: string) => string
  className?: string
}

const CommunityContributorsList = ({
  contributors,
  title: label = 'Contributors',
  maxInitialDisplay = 12,
  icon,
  getUrl,
  className,
}: CommunityContributorsListProps) => {
  const displayContributors = contributors.slice(0, maxInitialDisplay)

  if (contributors.length === 0) {
    return null
  }

  return (
    <SecondaryCard
      icon={icon}
      title={
        <div className="flex items-center gap-2">
          <AnchorTitle title={label} />
        </div>
      }
      className={twMerge(className)}
    >
      <div className="grid grid-cols-1 gap-4">
        {displayContributors.map((item) => (
          <div
            key={item.login}
            className="overflow-hidden rounded-lg bg-white p-4 shadow-sm dark:bg-gray-700"
          >
            <div className="flex w-full items-center gap-2">
              <Image
                alt={item?.name ? `${item.name}'s avatar` : 'Contributor avatar'}
                className="rounded-full"
                height={24}
                src={`${item?.avatarUrl}${item?.avatarUrl?.includes('?') ? '&' : '?'}s=60`}
                title={item?.name || item?.login}
                width={24}
              />
              <Link
                className="cursor-pointer overflow-hidden font-semibold text-ellipsis whitespace-nowrap text-blue-400 hover:underline"
                href={getUrl(item?.login)}
                title={item?.name || item?.login}
              >
                {upperFirst(item.name) || upperFirst(item.login)}
              </Link>
            </div>
          </div>
        ))}
      </div>
    </SecondaryCard>
  )
}

export default CommunityContributorsList
