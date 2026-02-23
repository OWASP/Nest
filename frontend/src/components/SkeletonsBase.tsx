import { Skeleton } from '@heroui/skeleton'
import type { CardSkeletonProps } from 'types/skeleton'
import LoadingSpinner from 'components/LoadingSpinner'
import AboutSkeleton from 'components/skeletons/AboutSkeleton'
import CardSkeleton from 'components/skeletons/Card'
import MemberDetailsPageSkeleton from 'components/skeletons/MemberDetailsPageSkeleton'
import OrganizationDetailsPageSkeleton from 'components/skeletons/OrganizationDetailsPageSkeleton'
import SnapshotSkeleton from 'components/skeletons/SnapshotSkeleton'
import UserCardSkeleton from 'components/skeletons/UserCard'

// Use CardSkeleton directly; wrapper removed
function userCardRender() {
  const cardCount = 12
  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {Array.from({ length: cardCount }, (_, index) => (
        <UserCardSkeleton key={`user-skeleton-${index}`} />
      ))}
    </div>
  )
}

function snapshotCardRender() {
  const cardCount = 12
  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {Array.from({ length: cardCount }, (_, index) => (
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
  let componentProps: CardSkeletonProps = {}

  switch (indexName) {
    case 'chapters':
      componentProps = { showLevel: false, showIcons: false, showLink: false }
      break
    case 'issues':
      componentProps = {
        showLevel: false,
        showIcons: true,
        numIcons: 2,
        showContributors: false,
        showSocial: false,
      }
      break
    case 'projects':
      componentProps = { showLink: false, showSocial: false, showIcons: true, numIcons: 3 }
      break
    case 'committees':
      componentProps = { showLink: false, showLevel: false, showIcons: true, numIcons: 1 }
      break
    case 'users':
      return userCardRender()
    case 'organizations':
      return userCardRender()
    case 'snapshots':
      return snapshotCardRender()
    case 'about':
      return <AboutSkeleton />
    case 'member-details':
    case 'members':
      return <MemberDetailsPageSkeleton />
    case 'organizations-details':
      return <OrganizationDetailsPageSkeleton />
    default:
      return <LoadingSpinner imageUrl={loadingImageUrl} />
  }
  return (
    <div className="flex w-full flex-col items-center justify-center">
      {indexName == 'chapters' ? (
        <Skeleton className="mb-2 h-96 w-full max-w-6xl" />
      ) : (
        <CardSkeleton {...componentProps} />
      )}
      <CardSkeleton {...componentProps} />
      <CardSkeleton {...componentProps} />
      <CardSkeleton {...componentProps} />
    </div>
  )
}

export default SkeletonBase
