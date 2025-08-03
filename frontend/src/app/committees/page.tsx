'use client'
import { useSearchPage } from 'hooks/useSearchPage'
import { useRouter } from 'next/navigation'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import type { Committee } from 'types/committee'
import { getFilteredIcons, handleSocialUrls } from 'utils/utility'
import Card from 'components/Card'
import PageLayout from 'components/PageLayout'
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
  } = useSearchPage<Committee>({
    indexName: 'committees',
    pageTitle: 'OWASP Committees',
  })
  const router = useRouter()
  const renderCommitteeCard = (committee: Committee) => {
    const params: string[] = ['updatedAt']
    const filteredIcons = getFilteredIcons(committee, params)
    const formattedUrls = handleSocialUrls(committee.relatedUrls)
    const handleButtonClick = () => {
      router.push(`/committees/${committee.key}`)
    }

    const submitButton = {
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
        topContributors={committee.topContributors}
        button={submitButton}
        social={formattedUrls}
        tooltipLabel={`Learn more about ${committee.name}`}
      />
    )
  }

  return (
    <PageLayout>
      <SearchPageLayout
        currentPage={currentPage}
        empty="No committees found"
        indexName="committees"
        isLoaded={isLoaded}
        onPageChange={handlePageChange}
        onSearch={handleSearch}
        searchPlaceholder="Search for committees..."
        searchQuery={searchQuery}
        totalPages={totalPages}
      >
        {committees && committees.map(renderCommitteeCard)}
      </SearchPageLayout>
    </PageLayout>
  )
}

export default CommitteesPage
