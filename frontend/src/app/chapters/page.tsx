'use client'
import { useQuery } from '@apollo/client/react'
import { useSearchPage } from 'hooks/useSearchPage'
import { useRouter } from 'next/navigation'
import { useEffect, useMemo, useState } from 'react'
import { FaRightToBracket } from 'react-icons/fa6'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'
import { GetChapterCountriesDocument } from 'types/__generated__/chapterQueries.generated'
import type { AlgoliaResponse } from 'types/algolia'
import type { Chapter } from 'types/chapter'
import { sortOptionsChapter } from 'utils/sortingOptions'
import { getFilteredIcons, handleSocialUrls } from 'utils/utility'
import Card from 'components/Card'
import ChapterMapWrapper from 'components/ChapterMapWrapper'
import CountryFilter from 'components/CountryFilter'
import SearchPageLayout from 'components/SearchPageLayout'
import SortBy from 'components/SortBy'

const ChaptersPage = () => {
  const [geoLocData, setGeoLocData] = useState<Chapter[]>([])
  const [selectedCountry, setSelectedCountry] = useState<string>('')

  const { data: countriesData, loading: countriesLoading } = useQuery(GetChapterCountriesDocument)
  const countries = countriesData?.chapterCountries ?? []

  const facetFilters = useMemo(
    () => (selectedCountry ? [`idx_country:${selectedCountry}`] : []),
    [selectedCountry]
  )

  const {
    items: chapters,
    isLoaded,
    currentPage,
    totalPages,
    searchQuery,
    sortBy,
    order,
    handleSearch,
    handlePageChange,
    handleSortChange,
    handleOrderChange,
  } = useSearchPage<Chapter>({
    indexName: 'chapters',
    pageTitle: 'OWASP Chapters',
    defaultSortBy: 'default',
    defaultOrder: 'desc',
    facetFilters,
  })

  useEffect(() => {
    const fetchData = async () => {
      const searchParams = {
        indexName: 'chapters',
        query: '',
        currentPage,
        hitsPerPage: currentPage === 1 ? 1000 : 25,
      }
      const data: AlgoliaResponse<Chapter> = await fetchAlgoliaData(
        searchParams.indexName,
        searchParams.query,
        searchParams.currentPage,
        searchParams.hitsPerPage,
        selectedCountry ? [`idx_country:${selectedCountry}`] : []
      )
      setGeoLocData(data.hits)
    }
    fetchData()
  }, [currentPage, selectedCountry])

  const handleCountryChange = (country: string) => {
    setSelectedCountry(country)
  }

  const router = useRouter()
  const renderChapterCard = (chapter: Chapter) => {
    const params: string[] = ['updatedAt']
    const filteredIcons = getFilteredIcons(chapter, params)
    const formattedUrls = handleSocialUrls(chapter.relatedUrls ?? [])

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
        key={chapter.objectID ?? chapter.key}
        cardKey={chapter.objectID ?? chapter.key}
        title={chapter.name}
        url={`/chapters/${chapter.key}`}
        summary={chapter.summary ?? ''}
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
      filterChildren={
        <CountryFilter
          countries={countries}
          selectedCountry={selectedCountry}
          onCountryChange={handleCountryChange}
          isLoading={countriesLoading}
        />
      }
      inlineSort
      sortChildren={
        <SortBy
          onOrderChange={handleOrderChange}
          onSortChange={handleSortChange}
          selectedOrder={order}
          selectedSortOption={sortBy}
          sortOptions={sortOptionsChapter}
        />
      }
      totalPages={totalPages}
    >
      {chapters.length > 0 && (
        <ChapterMapWrapper
          geoLocData={searchQuery || selectedCountry ? chapters : geoLocData}
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
