import Card from '@nest-frontend/components/Card'
import SearchPageLayout from '@nest-frontend/components/SearchPageLayout'
import FontAwesomeIconWrapper from '@nest-frontend/lib/FontAwesomeIconWrapper'
import { useSearchPage } from '@nest-frontend/lib/hooks/useSearchPage'
import { ChapterType } from '@nest-frontend/lib/types'
import { getFilteredIcons, handleSocialUrls } from '@nest-frontend/lib/utils'

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

  const renderChapterCard = (chapter: ChapterType, index: number) => {
    const params: string[] = ['idx_updated_at']
    const filteredIcons = getFilteredIcons(chapter, params)
    const formattedUrls = handleSocialUrls(chapter.idx_related_urls)

    const SubmitButton = {
      label: 'Join',
      icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
      url: chapter.idx_url,
    }
    return (
      <Card
        key={chapter.objectID || `chapter-${index}`}
        title={chapter.idx_name}
        url={chapter.idx_url}
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
