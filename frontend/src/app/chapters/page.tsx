'use client'

import { useEffect, useRef, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useSearchPage } from 'hooks/useSearchPage'

import { FaRightToBracket } from 'react-icons/fa6'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'
import type { AlgoliaResponse } from 'types/algolia'
import type { Chapter } from 'types/chapter'
import { getFilteredIcons, handleSocialUrls } from 'utils/utility'
import Card from 'components/Card'
import ChapterMapWrapper from 'components/ChapterMapWrapper'
import SearchPageLayout from 'components/SearchPageLayout'

const ChaptersPage = () => {
  const isMountedRef = useRef(true)
  const [geoLocData, setGeoLocData] = useState<Chapter[]>([])
  const {
    items: chapters,
    isLoaded,
    currentPage,
    totalPages,
    searchQuery,
    handleSearch,
    handlePageChange,
  } = useSearchPage<Chapter>({
    indexName: 'chapters',
    pageTitle: 'OWASP Chapters',
  })

  useEffect(() => {
    isMountedRef.current = true
  
    const fetchData = async () => {
      const searchParams = {
        indexName: 'chapters',
        query: '',
        currentPage,
        hitsPerPage: currentPage === 1 ? 1000 : 25,
      }
  
      const data: AlgoliaResponse<Chapter> =
        await fetchAlgoliaData(
          searchParams.indexName,
          searchParams.query,
          searchParams.currentPage,
          searchParams.hitsPerPage
        )
  
      if (isMountedRef.current) {
        setGeoLocData(data.hits)
      }
    }
  
    fetchData()
  
    return () => {
      isMountedRef.current = false
    }
  }, [currentPage])

  const router = useRouter()
  const renderChapterCard = (chapter: Chapter) => {
    const params: string[] = ['updatedAt']
    const filteredIcons = getFilteredIcons(chapter, params)
    const formattedUrls = handleSocialUrls(chapter.relatedUrls)

    const handleButtonClick = () => {
      router.push(`/chapters/${chapter.key}`)
    }

    const submitButton = {
      label: 'View Details',
      icon: <FaRightToBracket className="h-4 w-4" />,
      onclick: handleButtonClick,
    }

    return (
      <Card
        key={chapter.objectID}
        cardKey={chapter.objectID}
        title={chapter.name}
        url={`/chapters/${chapter.key}`}
        summary={chapter.summary}
        icons={filteredIcons}
        topContributors={chapter.topContributors}
        button={submitButton}
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
      searchPlaceholder="Search for chapters..."
      searchQuery={searchQuery}
      totalPages={totalPages}
    >
      {chapters.length > 0 && (
        <ChapterMapWrapper
          geoLocData={searchQuery ? chapters : geoLocData}
          showLocal={true}
          showLocationSharing={true}
          style={{
            height: '400px',
            width: '100%',
            zIndex: '0',
            borderRadius: '0.5rem',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          }}
        />
      )}
      {chapters?.filter((chapter) => chapter.isActive).map(renderChapterCard)}
    </SearchPageLayout>
  )
}

export default ChaptersPage
