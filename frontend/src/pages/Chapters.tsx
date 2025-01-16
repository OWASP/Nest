import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { useSearchPage } from 'hooks/useSearchPage'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AlgoliaResponseType } from 'types/algolia'
import { ChapterType } from 'types/chapter'
import { getFilteredIcons, handleSocialUrls } from 'utils/utility'
import { AppError } from 'wrappers/ErrorWrapper'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import Card from 'components/Card'
import ChapterMap from 'components/ChapterMap'
import SearchPageLayout from 'components/SearchPageLayout'

const ChaptersPage = () => {
  const [geoLocData, setGeoLocData] = useState<ChapterType[]>([])
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

  useEffect(() => {
    const fetchData = async () => {
      try {
        const searchParams = {
          indexName: 'chapters',
          query: '',
          currentPage: 1,
          filterKey: '',
          hitsPerPage: 1000,
        }
        const data: AlgoliaResponseType<ChapterType> = await fetchAlgoliaData(
          searchParams.indexName,
          searchParams.query,
          searchParams.currentPage,
          searchParams.filterKey,
          searchParams.hitsPerPage
        )
        setGeoLocData(data.hits)
      } catch (error) {
        if (error instanceof AppError) {
          throw error
        }
      }
    }
    fetchData()
  }, [])

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
      {geoLocData && <ChapterMap geoLocData={geoLocData} />}
      {chapters && chapters.map(renderChapterCard)}
    </SearchPageLayout>
  )
}

export default ChaptersPage
