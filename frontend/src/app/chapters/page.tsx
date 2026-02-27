'use client'
import { Select, SelectItem } from '@heroui/select'
import { useSearchPage } from 'hooks/useSearchPage'
import { useRouter } from 'next/navigation'
import { useCallback, useEffect, useState } from 'react'
import { FaRightToBracket } from 'react-icons/fa6'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'
import type { AlgoliaResponse } from 'types/algolia'
import type { Chapter } from 'types/chapter'
import { sortOptionsChapter } from 'utils/sortingOptions'
import { getFilteredIcons, handleSocialUrls } from 'utils/utility'
import Card from 'components/Card'
import ChapterMapWrapper from 'components/ChapterMapWrapper'
import SearchPageLayout from 'components/SearchPageLayout'
import SortBy from 'components/SortBy'

const ChaptersPage = () => {
  const [geoLocData, setGeoLocData] = useState<Chapter[]>([])
  const [allCountries, setAllCountries] = useState<string[]>([])
  const [selectedCountry, setSelectedCountry] = useState<string>('')
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
  })

  const handleCountryChange = useCallback(
    (country: string) => {
      setSelectedCountry(country)
      if (country) {
        handleFacetFilterChange([`idx_country:${country}`])
      } else {
        handleFacetFilterChange([])
      }
    },
    [handleFacetFilterChange]
  )

  useEffect(() => {
    const fetchAllCountries = async () => {
      const data: AlgoliaResponse<Chapter> = await fetchAlgoliaData('chapters', '', 1, 1000)
      const countrySet = new Set<string>()
      for (const chapter of data.hits) {
        if (chapter.country) {
          countrySet.add(chapter.country)
        }
      }
      setAllCountries(Array.from(countrySet).sort((a, b) => a.localeCompare(b)))
      setGeoLocData(data.hits)
    }
    fetchAllCountries()
  }, [])

  useEffect(() => {
    const fetchGeoData = async () => {
      const facetFilters: string[] = []
      if (selectedCountry) {
        facetFilters.push(`idx_country:${selectedCountry}`)
      }
      const data: AlgoliaResponse<Chapter> = await fetchAlgoliaData(
        'chapters',
        '',
        1,
        1000,
        facetFilters
      )
      setGeoLocData(data.hits)
    }
    if (selectedCountry) {
      fetchGeoData()
    }
  }, [selectedCountry])

  const countries = allCountries

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
      totalPages={totalPages}
      filterChildren={
        <div className="inline-flex h-12 items-center rounded-lg border border-gray-300 bg-gray-100 pl-3 shadow-sm transition-all duration-200 hover:shadow-md dark:border-gray-600 dark:bg-[#323232]">
          <Select
            aria-label="Filter by country"
            className=""
            labelPlacement="outside-left"
            size="md"
            label="Country :"
            placeholder="All Countries"
            classNames={{
              label: 'font-medium text-sm text-gray-700 dark:text-gray-300 w-auto select-none pe-0',
              trigger:
                'bg-transparent data-[hover=true]:bg-transparent focus:outline-none focus:underline border-none shadow-none text-nowrap w-40 min-h-8 h-8 text-sm font-medium text-gray-800 dark:text-gray-200 hover:text-gray-900 dark:hover:text-gray-100 transition-all duration-0',
              value: 'text-gray-800 dark:text-gray-200 font-medium',
              selectorIcon: 'text-gray-500 dark:text-gray-400 transition-transform duration-200',
              popoverContent:
                'bg-white dark:bg-[#2a2a2a] border border-gray-200 dark:border-gray-600 rounded-md shadow-lg min-w-36 p-1 focus:outline-none',
              listbox: 'p-0 focus:outline-none',
            }}
            selectedKeys={selectedCountry ? [selectedCountry] : []}
            onChange={(e) => handleCountryChange((e.target as HTMLSelectElement).value)}
          >
            {[
              { key: '', label: 'All Countries' },
              ...countries.map((c) => ({ key: c, label: c })),
            ].map((option) => (
              <SelectItem
                key={option.key}
                classNames={{
                  base: 'text-sm text-gray-700 dark:text-gray-300 hover:bg-transparent dark:hover:bg-transparent focus:bg-gray-100 dark:focus:bg-[#404040] focus:outline-none rounded-sm px-3 py-2 cursor-pointer data-[selected=true]:bg-blue-50 dark:data-[selected=true]:bg-blue-900/20 data-[selected=true]:text-blue-600 dark:data-[selected=true]:text-blue-400 data-[focus=true]:bg-gray-100 dark:data-[focus=true]:bg-[#404040]',
                }}
              >
                {option.label}
              </SelectItem>
            ))}
          </Select>
        </div>
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
