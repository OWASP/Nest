import FontAwesomeIconWrapper from 'lib/FontAwesomeIconWrapper'
import { useSearchPage } from 'lib/hooks/useSearchPage'
import { ChapterType } from 'lib/types'
import { getFilteredIcons, handleSocialUrls } from 'lib/utils'

import Card from 'components/Card'
import { ErrorDisplay } from 'components/ErrorDisplay'
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
    error,
    retry,
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
    if (error) {
      return <ErrorDisplay error={error} onRetry={error.action === 'retry' ? retry : undefined} />
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
