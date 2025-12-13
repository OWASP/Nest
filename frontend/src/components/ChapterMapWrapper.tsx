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
    }
  }

  const mapData = sortedData ?? props.geoLocData

  return (
    <div className="space-y-4">
      <ChapterMap
        {...props}
        geoLocData={mapData}
        userLocation={userLocation}
        onShareLocation={handleShareLocation}
      />
    </div>
  )
}

export default ChapterMapWrapper
