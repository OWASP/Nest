import { useQuery } from '@apollo/client'
import { useNavigate } from 'react-router-dom'
import { SnapshotDetailsProps, Snapshots } from 'types/snapshot'
import { METADATA_CONFIG } from 'utils/metadata'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import MetadataManager from 'components/MetadataManager'
import SearchPageLayout from 'components/SearchPageLayout'
import SnapshotCard from 'components/SnapshotCard' // A custom card component for Snapshot
import { GET_COMMUNITY_SNAPSHOTS } from 'api/queries/homeQueries'
import { useEffect, useState } from 'react'
import LoadingSpinner from 'components/LoadingSpinner'
import { toast } from 'hooks/useToast'

const SnapshotsPage = () => {
  const [snapshots, setSnapshots] = useState<Snapshots[] | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)

  const { data: graphQLData, error: graphQLRequestError } = useQuery(GET_COMMUNITY_SNAPSHOTS)

  useEffect(() => {
    if (graphQLData) {
      setSnapshots(graphQLData.snapshots)
      setIsLoading(false)
    }
    if (graphQLRequestError) {
      toast({
        description: 'Unable to complete the requested operation.',
        title: 'GraphQL Request Failed',
        variant: 'destructive',
      })
      setIsLoading(false)
    }
  }, [graphQLData, graphQLRequestError])

  const navigate = useNavigate()

  const handleButtonClick = (snapshot: Snapshots) => {
    navigate(`/community/snapshots/${snapshot.key}`)
  }

  const renderSnapshotCard = (snapshot: Snapshots) => {
    const SubmitButton = {
      label: 'View Details',
      icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
      onclick: () => handleButtonClick(snapshot),
    }

    return (
      <SnapshotCard
        title={snapshot.title}
        button={SubmitButton}
        startAt={snapshot.startAt}
        // endAt={snapshot.endAt}
      />
    )
  }

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner imageUrl="/img/owasp_icon_white_sm.png" />
      </div>
    )
  }

  return (
    <MetadataManager {...METADATA_CONFIG.snapshot}>
      <SearchPageLayout
        currentPage={1}
        empty="No Snapshots found"
        indexName="snapshots"
        isLoaded={!isLoading}
        onPageChange={() => {}}
        onSearch={() => {}}
        searchPlaceholder="Search for OWASP Snapshots..."
        searchQuery=""
        totalPages={1}
      >
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {snapshots &&
          snapshots.map((snapshot: Snapshots) => (
            <div key={snapshot.key}>{renderSnapshotCard(snapshot)}</div>
          ))}
      </div>
      </SearchPageLayout>
    </MetadataManager>
  )
}

export default SnapshotsPage
