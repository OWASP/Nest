import type { Release as ReleaseType } from 'types/release'
import { MAX_RELEASES_TO_SHOW } from 'utils/constants'
import Release from 'components/Release'
import ShowMoreButton from 'components/ShowMoreButton'

type ReleasesSectionProps = {
  releases: ReleaseType[]
  showAll: boolean
  onToggle: () => void
}

export const ReleasesSection = ({ releases, showAll, onToggle }: ReleasesSectionProps) => {
  const visibleReleases = showAll ? releases : releases.slice(0, MAX_RELEASES_TO_SHOW)
  return (
    <>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {visibleReleases.map((release, index) => {
          return (
            <Release
              key={
                release.id || `${release.tagName}-${release.repositoryName ?? 'unknown'}-${index}`
              }
              release={release}
              showAvatar={true}
              index={index}
            />
          )
        })}
      </div>
      {releases.length > MAX_RELEASES_TO_SHOW && <ShowMoreButton onToggle={onToggle} />}
    </>
  )
}
