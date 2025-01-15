import { useSearchPage } from 'hooks/useSearchPage'
import { useNavigate } from 'react-router-dom'
import { CommitteeType } from 'types/committee'
import { getFilteredIcons, handleSocialUrls } from 'utils/utility'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import Card from 'components/Card'
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
  } = useSearchPage<CommitteeType>({
    indexName: 'committees',
    pageTitle: 'OWASP Committees',
  })
  const navigate = useNavigate()
  const renderCommitteeCard = (committee: CommitteeType, index: number) => {
    const params: string[] = ['idx_updated_at']
    const filteredIcons = getFilteredIcons(committee, params)
    const formattedUrls = handleSocialUrls(committee.idx_related_urls)
    const handleButtonClick = () => {
      navigate(`/committees/${committee.idx_key}`)
    }

    const SubmitButton = {
      label: 'View Details',
      icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
      onclick: handleButtonClick,
    }

    return (
      <Card
        key={committee.objectID || `committee-${index}`}
        title={committee.idx_name}
        url={`committees/${committee.idx_key}`}
        summary={committee.idx_summary}
        icons={filteredIcons}
        topContributors={committee.idx_top_contributors}
        button={SubmitButton}
        social={formattedUrls}
        tooltipLabel={`Learn more about ${committee.idx_name}`}
      />
    )
  }

  return (
    <SearchPageLayout
      isLoaded={isLoaded}
      indexName="committees"
      totalPages={totalPages}
      currentPage={currentPage}
      onSearch={handleSearch}
      searchQuery={searchQuery}
      onPageChange={handlePageChange}
      empty="No committees found"
      searchPlaceholder="Search for OWASP committees..."
    >
      {committees && committees.map(renderCommitteeCard)}
    </SearchPageLayout>
  )
}

export default CommitteesPage
