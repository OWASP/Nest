'use client'
import { useSearchPage } from 'hooks/useSearchPage'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'
import { AlgoliaResponseType } from 'types/algolia'
import { ChapterTypeAlgolia } from 'types/chapter'
import { getFilteredIcons, handleSocialUrls } from 'utils/utility'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import Card from 'components/Card'
import ChapterMapWrapper from 'components/ChapterMapWrapper'
import SearchPageLayout from 'components/SearchPageLayout'

const ChaptersPage = () => {
  const [geoLocData, setGeoLocData] = useState<ChapterTypeAlgolia[]>([])
  const {
    items: chapters,
    isLoaded,
    currentPage,
    totalPages,
    searchQuery,
    handleSearch,
    handlePageChange,
  } = useSearchPage<ChapterTypeAlgolia>({
    indexName: 'chapters',
    pageTitle: 'OWASP Chapters',
  })

  useEffect(() => {
    const fetchData = async () => {
      const searchParams = {
        indexName: 'chapters',
        query: '',
        currentPage,
        hitsPerPage: currentPage === 1 ? 1000 : 25,
      }
      const data: AlgoliaResponseType<ChapterTypeAlgolia> = await fetchAlgoliaData(
        searchParams.indexName,
        searchParams.query,
        searchParams.currentPage,
        searchParams.hitsPerPage
      )
      setGeoLocData(data.hits)
    }
    fetchData()
  }, [currentPage])

  const router = useRouter()
  const renderChapterCard = (chapter: ChapterTypeAlgolia) => {
    const params: string[] = ['updated_at']
    const filteredIcons = getFilteredIcons(chapter, params)
    const formattedUrls = handleSocialUrls(chapter.related_urls)

    const handleButtonClick = () => {
      router.push(`/chapters/${chapter.key}`)
    }

    const SubmitButton = {
      label: 'View Details',
      icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket " />,
      onclick: handleButtonClick,
    }

    return (
      <Card
        key={chapter.objectID}
        title={chapter.name}
        url={`/chapters/${chapter.key}`}
        summary={chapter.summary}
        icons={filteredIcons}
        topContributors={chapter.top_contributors}
        button={SubmitButton}
        social={formattedUrls}
      />
    )
  }

  return (
    <SearchPageLayout
      currentPage={currentPage}
      empty="No chapters found"
      indexName="chapters"
      isLoaded={isLoaded}
      onPageChange={handlePageChange}
      onSearch={handleSearch}
      searchPlaceholder="Search for OWASP chapters..."
      searchQuery={searchQuery}
      totalPages={totalPages}
    >
      {chapters.length > 0 && (
        <ChapterMapWrapper
          geoLocData={searchQuery ? chapters : geoLocData}
          showLocal={true}
          style={{
            height: '400px',
            width: '100%',
            zIndex: '0',
            borderRadius: '0.5rem',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          }}
        />
      )}
      {chapters && chapters.filter((chapter) => chapter.is_active).map(renderChapterCard)}
    </SearchPageLayout>
  )
}

export default ChaptersPage
