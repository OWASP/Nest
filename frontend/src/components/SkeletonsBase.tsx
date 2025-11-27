import { Skeleton } from '@heroui/skeleton'
import LoadingSpinner from 'components/LoadingSpinner'
import CardSkeleton from 'components/skeletons/Card'
import SnapshotSkeleton from 'components/skeletons/SnapshotSkeleton'
import UserCardSkeleton from 'components/skeletons/UserCard'

function userCardRender() {
  const cardCount = 12
  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {Array.from({ length: cardCount }).map((_, index) => (
        <UserCardSkeleton key={`user-skeleton-${index}`} />
      ))}
    </div>
  )
}

function snapshotCardRender() {
  const cardCount = 12
  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {Array.from({ length: cardCount }).map((_, index) => (
        <SnapshotSkeleton key={`snapshot-skeleton-${index}`} />
      ))}
    </div>
  )
}


const SkeletonBase = ({
  indexName,
  loadingImageUrl,
}: {
  indexName: string
  loadingImageUrl: string
}) => {
  let Component
  switch (indexName) {
    case 'chapters':
      Component = () => <CardSkeleton showLevel={false} showIcons={false} showLink={false} />
      break
    case 'issues':
      Component = () => (
        <CardSkeleton
          showLevel={false}
          showIcons={true}
          numIcons={2}
          showContributors={false}
          showSocial={false}
        />
      )
      break
    case 'projects':
      Component = () => (
        <CardSkeleton showLink={false} showSocial={false} showIcons={true} numIcons={3} />
      )
      break
    case 'committees':
      Component = () => (
        <CardSkeleton showLink={false} showLevel={false} showIcons={true} numIcons={1} />
      )
      break
    case 'users':
      return userCardRender()

    case 'organizations':
      return userCardRender()
    case 'snapshots':
      return snapshotCardRender()

    default:
      return <LoadingSpinner imageUrl={loadingImageUrl} />
  }
  return (
    <div className="flex w-full flex-col items-center justify-center">
      {indexName == 'chapters' ? (
        <Skeleton className="mb-2 h-96 w-full max-w-6xl" />
      ) : (
        <Component />
      )}
      <Component />
      <Component />
      <Component />
    </div>
  )
}

export default SkeletonBase
