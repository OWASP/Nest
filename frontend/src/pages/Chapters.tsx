import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { useSearchPage } from 'hooks/useSearchPage'
import { useEffect, useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { AlgoliaResponseType } from 'types/algolia'
import { ChapterTypeAlgolia } from 'types/chapter'
import { METADATA_CONFIG } from 'utils/metadata'
import { getFilteredIcons, handleSocialUrls } from 'utils/utility'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import Card from 'components/Card'
import ChapterMap from 'components/ChapterMap'
import MetadataManager from 'components/MetadataManager'
import SearchPageLayout from 'components/SearchPageLayout'

const ChaptersPage = () => {
  const [geoLocData, setGeoLocData] = useState<ChapterTypeAlgolia[]>([])
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null)

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

  // Fetch chapter data and user location
  useEffect(() => {
    const fetchData = async () => {
      const searchParams = {
        indexName: 'chapters',
        query: '',
        currentPage: 1,
        hitsPerPage: 1000,
      }
      const data: AlgoliaResponseType<ChapterTypeAlgolia> = await fetchAlgoliaData(
        searchParams.indexName,
        searchParams.query,
        searchParams.currentPage,
        searchParams.hitsPerPage
      )
      setGeoLocData(data.hits)
    }

    const fetchUserLocation = () => {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            setUserLocation({
              lat: position.coords.latitude,
              lng: position.coords.longitude,
            })
          },
          () => {

          }
        )
      }
    }

    fetchData()
    fetchUserLocation()
  }, [])

  const navigate = useNavigate()

  const renderChapterCard = (chapter: ChapterTypeAlgolia) => {
    const params: string[] = ['updated_at']
    const filteredIcons = getFilteredIcons(chapter, params)
    const formattedUrls = handleSocialUrls(chapter.related_urls)

    const handleButtonClick = () => {
      navigate(`/chapters/${chapter.key}`)
    }

    const SubmitButton = {
      label: 'View Details',
      icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
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

  // Determine which data to use for the map
  const mapData = useMemo(() => {
    return searchQuery ? chapters : geoLocData
  }, [searchQuery, chapters, geoLocData])

  return (
    <MetadataManager {...METADATA_CONFIG.chapters}>
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
        {mapData.length > 0 && (
          <ChapterMap
            geoLocData={mapData}
            userLocation={userLocation}
            style={{ height: '400px', width: '100%', zIndex: '0' }}
          />
        )}
        {chapters && chapters.filter((chapter) => chapter.is_active).map(renderChapterCard)}
      </SearchPageLayout>
    </MetadataManager>
  )
}

export default ChaptersPage
