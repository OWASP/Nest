import FontAwesomeIconWrapper from 'helpers/wrappers/FontAwesomeIconWrapper'
import { useSearchPage } from 'hooks/useSearchPage'
import { useNavigate } from 'react-router-dom'
import { ChapterType } from 'types/chapter'
import { getFilteredIcons, handleSocialUrls } from 'utils/utils'
import Card from 'components/Card'
import SearchPageLayout from 'components/SearchPageLayout'

const ChaptersPage = () => {
  const {
    items: chapters,
    isLoaded,
    currentPage,
    totalPages,
    searchQuery,
    handleSearch,
    handlePageChange,
  } = useSearchPage<ChapterType>({
    indexName: 'chapters',
    pageTitle: 'OWASP Chapters',
  })
  const navigate = useNavigate()
  const renderChapterCard = (chapter: ChapterType, index: number) => {
    const params: string[] = ['idx_updated_at']
    const filteredIcons = getFilteredIcons(chapter, params)
    const formattedUrls = handleSocialUrls(chapter.idx_related_urls)

    const handleButtonClick = () => {
      navigate(`/chapters/${chapter.idx_key}`)
    }

    const SubmitButton = {
      label: 'View Details',
      icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket " />,
      onclick: handleButtonClick,
    }

    return (
      <Card
        key={chapter.objectID || `chapter-${index}`}
        title={chapter.idx_name}
        url={`chapters/${chapter.idx_key}`}
        summary={chapter.idx_summary}
        icons={filteredIcons}
        leaders={chapter.idx_leaders}
        topContributors={chapter.idx_top_contributors}
        button={SubmitButton}
        social={formattedUrls}
      />
    )
  }

  return (
    <SearchPageLayout
      isLoaded={isLoaded}
      totalPages={totalPages}
      currentPage={currentPage}
      searchQuery={searchQuery}
      indexName="chapters"
      onSearch={handleSearch}
      onPageChange={handlePageChange}
      searchPlaceholder="Search for OWASP chapters..."
      empty="No chapters found"
    >
      {chapters && chapters.map(renderChapterCard)}
    </SearchPageLayout>
  )
}

export default ChaptersPage
