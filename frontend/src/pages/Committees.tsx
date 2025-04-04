import { useSearchPage } from 'hooks/useSearchPage'
import { useNavigate } from 'react-router-dom'
import { CommitteeTypeAlgolia } from 'types/committee'
import { METADATA_CONFIG } from 'utils/metadata'
import { getFilteredIcons, handleSocialUrls } from 'utils/utility'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import Card from 'components/Card'
import MetadataManager from 'components/MetadataManager'
import SearchPageLayout from 'components/SearchPageLayout'

const CommitteesPage = () => {
  const {
    items: committees,
    isLoaded,
    currentPage,
    totalPages,
    searchQuery,
    handleSearch,
    handlePageChange,
  } = useSearchPage<CommitteeTypeAlgolia>({
    indexName: 'committee',
    pageTitle: 'OWASP Committees',
  })
  const navigate = useNavigate()
  const renderCommitteeCard = (committee: CommitteeTypeAlgolia) => {
    const params: string[] = ['updated_at']
    const filteredIcons = getFilteredIcons(committee, params)
    const formattedUrls = handleSocialUrls(committee.related_urls)
    const handleButtonClick = () => {
      navigate(`/committees/${committee.key}`)
    }

    const SubmitButton = {
      label: 'View Details',
      icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
      onclick: handleButtonClick,
    }

    return (
      <Card
        key={committee.objectID}
        title={committee.name}
        url={`/committees/${committee.key}`}
        summary={committee.summary}
        icons={filteredIcons}
        topContributors={committee.top_contributors}
        button={SubmitButton}
        social={formattedUrls}
        tooltipLabel={`Learn more about ${committee.name}`}
      />
    )
  }

  return (
    <MetadataManager {...METADATA_CONFIG.committees}>
      <SearchPageLayout
        currentPage={currentPage}
        empty="No committees found"
        indexName="committees"
        isLoaded={isLoaded}
        onPageChange={handlePageChange}
        onSearch={handleSearch}
        searchPlaceholder="Search for OWASP committees..."
        searchQuery={searchQuery}
        totalPages={totalPages}
      >
        {committees && committees.map(renderCommitteeCard)}
      </SearchPageLayout>
    </MetadataManager>
  )
}

export default CommitteesPage
