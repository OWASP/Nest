'use client'
import { useQuery } from '@apollo/client/react'
import { useSearchPage } from 'hooks/useSearchPage'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
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

  const router = useRouter()
  const [selectedCountry, setSelectedCountry] = useState<string>('')

  const { data: countriesData } = useQuery(GetChapterCountriesDocument)
  const countries = countriesData?.chapterCountries ?? []

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
    handleFacetFilterChange,
  } = useSearchPage<Chapter>({
    indexName: 'chapters',
    pageTitle: 'OWASP Chapters',
    defaultSortBy: 'default',
    defaultOrder: 'desc',
    facetFilters: [],
  })

  const handleCountryChange = (country: string) => {
    setSelectedCountry(country)
    if (country) {
      handleFacetFilterChange([`idx_country:${country}`])
    } else {
      handleFacetFilterChange([])
    }
  }

  useEffect(() => {
    const fetchGeoData = async () => {
      const data: AlgoliaResponse<Chapter> = await fetchAlgoliaData(
        'chapters',
        '',
        1,
        1000,
        selectedCountry ? [`idx_country:${selectedCountry}`] : []
      )
      setGeoLocData(data.hits)
    }
    fetchGeoData()
  }, [selectedCountry])

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
      totalPages={totalPages}
      filterChildren={
        <CountryFilter
          countries={countries}
          selectedCountry={selectedCountry}
          onCountryChange={handleCountryChange}
        />
      }
      sortChildren={
        <SortBy
          onOrderChange={handleOrderChange}
          onSortChange={handleSortChange}
          selectedOrder={order}
          selectedSortOption={sortBy}
          sortOptions={sortOptionsChapter}
        />
      }
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
