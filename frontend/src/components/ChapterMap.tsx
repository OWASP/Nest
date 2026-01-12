'use client'
import { Button } from '@heroui/button'
import { Tooltip } from '@heroui/tooltip'
import L from 'leaflet'
import { useRouter } from 'next/navigation'
import React, { useEffect, useRef, useState, useMemo } from 'react'
import { FaUnlock } from 'react-icons/fa'
import { FaLocationDot } from 'react-icons/fa6'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import MarkerClusterGroup from 'react-leaflet-cluster'
import type { Chapter } from 'types/chapter'
import type { UserLocation } from 'utils/geolocationUtils'
import 'leaflet.markercluster'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'

const MapZoomControl = ({ isMapActive }: { isMapActive: boolean }) => {
  const map = useMap()
  const zoomControlRef = useRef<L.Control.Zoom | null>(null)
  useEffect(() => {
    if (!map) return
    if (isMapActive) {
      map.scrollWheelZoom.enable()
      map.dragging.enable()
      map.touchZoom.enable()
      map.doubleClickZoom.enable()
      map.keyboard.enable()

      if (!zoomControlRef.current) {
        zoomControlRef.current = L.control.zoom({ position: 'topleft' })
        zoomControlRef.current.addTo(map)
      }
    } else {
      map.scrollWheelZoom.disable()
      map.dragging.disable()
      map.touchZoom.disable()
      map.doubleClickZoom.disable()
      map.keyboard.disable()

      if (zoomControlRef.current) {
        zoomControlRef.current.remove()
        zoomControlRef.current = null
      }
    }
  }, [isMapActive, map])

  useEffect(() => {
    return () => {
      if (!map) return
      map.scrollWheelZoom.disable()
      map.dragging.disable()
      map.touchZoom.disable()
      map.doubleClickZoom.disable()
      map.keyboard.disable()
      if (zoomControlRef.current) {
        zoomControlRef.current.remove()
        zoomControlRef.current = null
      }
    }
  }, [map])
  return null
}

const MapViewUpdater = ({
  validGeoLocData,
  userLocation,
  showLocal,
}: {
  validGeoLocData: Chapter[]
  userLocation?: UserLocation | null
  showLocal: boolean
}) => {
  const map = useMap()

  useEffect(() => {
    if (!map) return
    const container = map.getContainer()
    const width = container.clientWidth
    const height = container.clientHeight
    const aspectRatio = width / height

    const dynamicMinZoom = aspectRatio > 2 ? 1 : 2
    map.setMinZoom(dynamicMinZoom)

    if (userLocation && validGeoLocData.length > 0) {
      const maxNearestChapters = 5
      const localChapters = validGeoLocData.slice(0, maxNearestChapters)
      const locationsForBounds: L.LatLngExpression[] = [
        [userLocation.latitude, userLocation.longitude],
        ...localChapters.map(
          (chapter) =>
            [
              chapter._geoloc?.lat ?? chapter.geoLocation?.lat,
              chapter._geoloc?.lng ?? chapter.geoLocation?.lng,
            ] as L.LatLngExpression
        ),
      ]
      const localBounds = L.latLngBounds(locationsForBounds)
      const maxZoom = 12
      const padding = 50
      map.fitBounds(localBounds, { maxZoom: maxZoom, padding: [padding, padding] })
    } else if (showLocal && validGeoLocData.length > 0) {
      const maxNearestChapters = 5
      const localChapters = validGeoLocData.slice(0, maxNearestChapters - 1)
      const localBounds = L.latLngBounds(
        localChapters.map((chapter) => [
          chapter._geoloc?.lat ?? chapter.geoLocation?.lat,
          chapter._geoloc?.lng ?? chapter.geoLocation?.lng,
        ])
      )
      const maxZoom = 7
      const padding = 50
      const nearestChapter = validGeoLocData[0]
      map.setView(
        [
          nearestChapter._geoloc?.lat ?? nearestChapter.geoLocation?.lat,
          nearestChapter._geoloc?.lng ?? nearestChapter.geoLocation?.lng,
        ],
        maxZoom
      )
      map.fitBounds(localBounds, { maxZoom: maxZoom, padding: [padding, padding] })
    } else {
      map.setView([20, 0], Math.max(dynamicMinZoom, 2))
    }
  }, [userLocation, showLocal, validGeoLocData, map])

  return null
}

const ChapterMap = ({
  geoLocData,
  showLocal,
  style,
  userLocation,
  onShareLocation,
}: {
  geoLocData: Chapter[]
  showLocal: boolean
  style: React.CSSProperties
  userLocation?: UserLocation | null
  onShareLocation?: () => void
}) => {
  const router = useRouter()
  const [isMapActive, setIsMapActive] = useState(false)
  const validGeoLocData = useMemo(() => {
    return geoLocData.filter((chapter) => {
      const lat = chapter._geoloc?.lat ?? chapter.geoLocation?.lat
      const lng = chapter._geoloc?.lng ?? chapter.geoLocation?.lng
      return typeof lat === 'number' && typeof lng === 'number'
    })
  }, [geoLocData])

  const chapterIcon = useMemo(
    () =>
      new L.Icon({
        iconAnchor: [12, 41],
        iconRetinaUrl: '/img/marker-icon-2x.png',
        iconSize: [25, 41],
        iconUrl: '/img/marker-icon.png',
        popupAnchor: [1, -34],
        shadowSize: [41, 41],
        shadowUrl: '/img/marker-shadow.png',
      }),

    []
  )

  const userIcon = useMemo(
    () =>
      L.divIcon({
        html: ' <div aria-label="User location" role="img"><img src="/img/marker-icon.png" style="filter: hue-rotate(150deg) saturate(1.5) brightness(0.9); width: 25px; height: 41px;" alt="" aria-hidden="true" />  </div> ',
        className: 'user-location-marker',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
      }),
    []
  )

  return (
    <section
      aria-label="Chapter Map"
      className="relative"
      style={style}
      onMouseLeave={() => setIsMapActive(false)}
    >
      <MapContainer
        center={[20, 0]}
        zoom={2}
        scrollWheelZoom={isMapActive}
        style={{ height: '100%', width: '100%' }}
        zoomControl={false}
        minZoom={1}
        maxZoom={18}
        worldCopyJump={true}
        maxBounds={[
          [-85, -Infinity],
          [85, Infinity],
        ]}
        maxBoundsViscosity={0.5}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          className="map-tiles"
        />
        <MapViewUpdater
          validGeoLocData={validGeoLocData}
          userLocation={userLocation}
          showLocal={showLocal}
        />

        <MapZoomControl isMapActive={isMapActive} />

        <MarkerClusterGroup chunkedLoading>
          {useMemo(
            () =>
              validGeoLocData.map((chapter) => (
                <Marker
                  key={chapter.key}
                  position={[
                    chapter._geoloc?.lat ?? chapter.geoLocation?.lat,
                    chapter._geoloc?.lng ?? chapter.geoLocation?.lng,
                  ]}
                  icon={chapterIcon}
                >
                  <Popup>
                    <button
                      type="button"
                      className="cursor-pointer font-medium hover:text-blue-600"
                      onClick={() => router.push(`/chapters/${chapter.key}`)}
                    >
                      {chapter.name}
                    </button>
                  </Popup>
                </Marker>
              )),
            [validGeoLocData, chapterIcon, router]
          )}
        </MarkerClusterGroup>

        {userLocation && (
          <Marker
            position={[userLocation.latitude, userLocation.longitude]}
            icon={userIcon}
            title="Your location"
          >
            <Popup>Your Location</Popup>
          </Marker>
        )}
      </MapContainer>
      {!isMapActive && (
        <button
          type="button"
          tabIndex={0}
          className="pointer-events-none absolute inset-0 z-[500] flex cursor-pointer items-center justify-center rounded-[inherit] bg-black/10"
          onClick={() => {
            setIsMapActive(true)
          }}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault()
              setIsMapActive(true)
            }
          }}
          aria-label="Unlock map"
        >
          <p className="pointer-events-auto flex items-center gap-2 rounded-md bg-white/90 px-5 py-3 text-sm font-medium text-gray-700 shadow-lg transition-colors hover:bg-gray-200 hover:text-gray-900 dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600 dark:hover:text-white">
            <FaUnlock aria-hidden="true" />
            Unlock map
          </p>
        </button>
      )}
      {isMapActive && (
        <div className="absolute top-20 left-3 z-[999] w-fit">
          {onShareLocation && (
            <Tooltip
              showArrow
              content={
                userLocation
                  ? 'Reset location filter'
                  : 'Share your location to find nearby chapters'
              }
              placement="bottom-start"
            >
              <Button
                isIconOnly
                className="h-[30px] w-[30px] min-w-[30px] rounded-xs bg-white text-gray-700 shadow-lg outline-2 outline-gray-400 hover:bg-gray-100 dark:outline-gray-700"
                onPress={onShareLocation}
                aria-label={
                  userLocation ? 'Reset location filter' : 'Share location to find nearby chapters'
                }
              >
                <FaLocationDot size={14} />
              </Button>
            </Tooltip>
          )}
        </div>
      )}
    </section>
  )
}
export default ChapterMap
