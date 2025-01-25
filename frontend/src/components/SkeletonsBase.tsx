import LoadingSpinner from 'components/LoadingSpinner'
import CardSkeleton from 'components/skeletons/Card'
import UserCardSkeleton from 'components/skeletons/UserCard'
import { Skeleton } from 'components/ui/skeleton'

function userCardRender() {
  const cardCount = 12
  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {Array.from({ length: cardCount }).map((_, index) => (
        <UserCardSkeleton key={index} />
      ))}
    </div>
  )
}

const SkeletonBase = ({ indexName, loadingImageUrl }) => {
  let Component
  switch (indexName) {
    case 'chapters':
      Component = () => <CardSkeleton showLevel={false} showIcons={1} showLink={false} />
      break
    case 'issues':
      Component = () => (
        <CardSkeleton showLevel={false} showIcons={2} showContributors={false} showSocial={false} />
      )
      break
    case 'projects':
      Component = () => <CardSkeleton showLink={false} showSocial={false} />
      break
    case 'committees':
      Component = () => <CardSkeleton showLink={false} showLevel={false} showIcons={1} />
      break
    case 'users':
      return userCardRender()
    default:
      return <LoadingSpinner imageUrl={loadingImageUrl} />
  }
  return (
    <div className="flex w-full flex-col items-center justify-center">
      {indexName == 'chapters' ? (
        <Skeleton className="mb-2 w-full max-w-6xl" h={400} />
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
