import { faLocationDot } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Button } from '@heroui/button'
import dynamic from 'next/dynamic'
import React, { useState } from 'react'
import type { Chapter } from 'types/chapter'
import {
  getUserLocationFromBrowser,
  sortChaptersByDistance,
  type UserLocation,
} from 'utils/geolocationUtils'

const ChapterMap = dynamic(() => import('./ChapterMap'), { ssr: false })

interface ChapterMapWrapperProps {
  geoLocData: Chapter[]
  showLocal: boolean
  style: React.CSSProperties
  showLocationSharing?: boolean
}

const ChapterMapWrapper: React.FC<ChapterMapWrapperProps> = (props) => {
  const [userLocation, setUserLocation] = useState<UserLocation | null>(null)
  const [isLoadingLocation, setIsLoadingLocation] = useState(false)
  const [sortedData, setSortedData] = useState<Chapter[] | null>(null)

  const enableLocationSharing = props.showLocationSharing === true

  if (!enableLocationSharing) {
    return <ChapterMap {...props} />
  }

  const handleShareLocation = async () => {
    if (userLocation) {
      setUserLocation(null)
      setSortedData(null)
      return
    }

    setIsLoadingLocation(true)

    try {
      const location = await getUserLocationFromBrowser()

      if (location) {
        setUserLocation(location)
        const sorted = sortChaptersByDistance(props.geoLocData, location)
        setSortedData(sorted.map(({ _distance, ...chapter }) => chapter as unknown as Chapter))
      }
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Error detecting location:', error)
    } finally {
      setIsLoadingLocation(false)
    }
  }

  const mapData = sortedData ?? props.geoLocData

  return (
    <div className="space-y-4">
      <div className="mb-4 flex items-center gap-3 rounded-lg bg-gray-100 p-4 shadow-md dark:bg-gray-800">
        <Button
          isIconOnly
          className="bg-blue-500 text-white hover:bg-blue-600"
          onClick={handleShareLocation}
          isLoading={isLoadingLocation}
          disabled={isLoadingLocation}
          aria-label={
            userLocation ? 'Reset location filter' : 'Share location to find nearby chapters'
          }
          title={userLocation ? 'Reset location filter' : 'Share location to find nearby chapters'}
        >
          <FontAwesomeIcon icon={faLocationDot} size="lg" />
        </Button>

        <div className="text-sm text-gray-700 dark:text-gray-300">
          {userLocation ? (
            <>
              <div className="font-semibold text-blue-600 dark:text-blue-400">
                📍 Showing chapters near you
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400">
                Location: {userLocation.latitude.toFixed(2)}, {userLocation.longitude.toFixed(2)}
              </div>
            </>
          ) : (
            <>
              <div className="font-semibold text-gray-800 dark:text-gray-200">
                Find chapters near you
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400">
                Click the blue button to use your current location
              </div>
            </>
          )}
        </div>
      </div>

      <ChapterMap {...props} geoLocData={mapData} userLocation={userLocation} />
    </div>
  )
}

export default ChapterMapWrapper
