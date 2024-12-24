import Card from '@src/components/Card'
import SearchPageLayout from '@src/components/SearchPageLayout'
import FontAwesomeIconWrapper from '@src/lib/FontAwesomeIconWrapper'
import { useSearchPage } from '@src/lib/hooks/useSearchPage'
import { CommitteeType } from '@src/lib/types'
import { getFilteredIcons, handleSocialUrls } from '@src/lib/utils'

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

  const renderCommitteeCard = (committee: CommitteeType, index: number) => {
    const params: string[] = ['idx_updated_at']
    const filteredIcons = getFilteredIcons(committee, params)
    const formattedUrls = handleSocialUrls(committee.idx_related_urls)

    const SubmitButton = {
      label: 'Learn More',
      icon: <FontAwesomeIconWrapper icon="fa-solid fa-people-group" />,
      url: committee.idx_url,
    }

    return (
      <Card
        key={committee.objectID || `committee-${index}`}
        title={committee.idx_name}
        url={committee.idx_url}
        summary={committee.idx_summary}
        icons={filteredIcons}
        leaders={committee.idx_leaders}
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
