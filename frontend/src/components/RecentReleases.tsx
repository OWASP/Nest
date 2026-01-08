import React from 'react'
import { FaTag } from 'react-icons/fa6'
import type { Release as ReleaseType } from 'types/release'
import AnchorTitle from 'components/AnchorTitle'
import Release from 'components/Release'
import SecondaryCard from 'components/SecondaryCard'

interface RecentReleasesProps {
  data: ReleaseType[]
  showAvatar?: boolean
  showSingleColumn?: boolean
}

const RecentReleases: React.FC<RecentReleasesProps> = ({
  data,
  showAvatar = true,
  showSingleColumn = false,
}) => {
  return (
    <SecondaryCard
      icon={FaTag}
      title={
        <div className="flex items-center gap-2">
          <AnchorTitle title="Recent Releases" className="flex items-center leading-none" />
        </div>
      }
    >
      {data && data.length > 0 ? (
        <div
          className={`grid ${showSingleColumn ? 'grid-cols-1' : 'gap-4 gap-y-0 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3'}`}
        >
          {data.map((item) => (
            <Release
              key={`${item.repositoryName}-${item.tagName}`}
              release={item}
              showAvatar={showAvatar}
            />
          ))}
        </div>
      ) : (
        <p>No recent releases.</p>
      )}
    </SecondaryCard>
  )
}

export default RecentReleases
