'use client'
import { faLocationDot } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Button } from '@heroui/button'
import { Tooltip } from '@heroui/tooltip'
import L, { MarkerClusterGroup } from 'leaflet'
import React, { useEffect, useRef, useState } from 'react'
import type { Chapter } from 'types/chapter'
import type { UserLocation } from 'utils/geolocationUtils'
import 'leaflet.markercluster'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'
import 'leaflet.markercluster'

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
  const mapRef = useRef<L.Map | null>(null)
  const markerClusterRef = useRef<MarkerClusterGroup | null>(null)
  const [isMapActive, setIsMapActive] = useState(false)

  useEffect(() => {
    if (!mapRef.current) {
      mapRef.current = L.map('chapter-map', {
        worldCopyJump: false,
        maxBounds: [
          [-90, -180],
          [90, 180],
        ],
        maxBoundsViscosity: 1.0,
        scrollWheelZoom: false,
      }).setView([20, 0], 2)

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        className: 'map-tiles',
      }).addTo(mapRef.current)

      mapRef.current.on('click', () => {
        mapRef.current?.scrollWheelZoom.enable()
        setIsMapActive(true)
      })

      mapRef.current.on('mouseout', (e: L.LeafletMouseEvent) => {
        const originalEvent = e.originalEvent as MouseEvent
        const relatedTarget = originalEvent.relatedTarget as Node | null
        const container = mapRef.current?.getContainer()
        if (relatedTarget && container?.contains(relatedTarget)) return

        mapRef.current?.scrollWheelZoom.disable()
        setIsMapActive(false)
      })
    }

    const map = mapRef.current

    if (!markerClusterRef.current) {
      markerClusterRef.current = L.markerClusterGroup()
      map.addLayer(markerClusterRef.current)
    } else {
      markerClusterRef.current.clearLayers()
    }

    const markerClusterGroup = markerClusterRef.current

    const validGeoLocData = geoLocData.filter((chapter) => {
      const lat = chapter._geoloc?.lat ?? chapter.geoLocation?.lat
      const lng = chapter._geoloc?.lng ?? chapter.geoLocation?.lng
      return typeof lat === 'number' && typeof lng === 'number'
    })

    const markers = validGeoLocData.map((chapter) => {
      const markerIcon = new L.Icon({
        iconAnchor: [12, 41],
        iconRetinaUrl: '/img/marker-icon-2x.png',
        iconSize: [25, 41],
        iconUrl: '/img/marker-icon.png',
        popupAnchor: [1, -34],
        shadowSize: [41, 41],
        shadowUrl: '/img/marker-shadow.png',
      })

      const marker = L.marker(
        [
          chapter._geoloc?.lat ?? chapter.geoLocation?.lat,
          chapter._geoloc?.lng ?? chapter.geoLocation?.lng,
        ],
        { icon: markerIcon }
      )
      const popup = L.popup()
      const popupContent = document.createElement('div')
      popupContent.className = 'popup-content'
      popupContent.textContent = chapter.name
      popupContent.addEventListener('click', () => {
        globalThis.location.href = `/chapters/${chapter.key}`
      })
      popup.setContent(popupContent)
      marker.bindPopup(popup)
      return marker
    })

    markerClusterGroup.addLayers(markers)

    // Add user location marker if available
    if (userLocation && map) {
      const iconHtml =
        '<img src="/img/marker-icon.png" style="filter: hue-rotate(150deg) saturate(1.5) brightness(0.9); width: 25px; height: 41px;" alt="User location" />'
      const userMarkerIcon = L.divIcon({
        html: iconHtml,
        className: 'user-location-marker',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
      })

      const userMarker = L.marker([userLocation.latitude, userLocation.longitude], {
        icon: userMarkerIcon,
      })
      const userPopup = L.popup()
      const userPopupContent = document.createElement('div')
      userPopupContent.textContent = 'Your Location'
      userPopup.setContent(userPopupContent)
      userMarker.bindPopup(userPopup)
      userMarker.addTo(map)
    }

    if (userLocation && validGeoLocData.length > 0) {
      const maxNearestChapters = 5
      const localChapters = validGeoLocData.slice(0, maxNearestChapters)
      const localBounds = L.latLngBounds(
        localChapters.map((chapter) => [
          chapter._geoloc?.lat ?? chapter.geoLocation?.lat,
          chapter._geoloc?.lng ?? chapter.geoLocation?.lng,
        ])
      )
      const maxZoom = 12
      const nearestChapter = validGeoLocData[0]
      map.setView(
        [
          nearestChapter._geoloc?.lat ?? nearestChapter.geoLocation?.lat,
          nearestChapter._geoloc?.lng ?? nearestChapter.geoLocation?.lng,
        ],
        maxZoom
      )
      map.fitBounds(localBounds, { maxZoom: maxZoom })
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
      const nearestChapter = validGeoLocData[0]
      map.setView(
        [
          nearestChapter._geoloc?.lat ?? nearestChapter.geoLocation?.lat,
          nearestChapter._geoloc?.lng ?? nearestChapter.geoLocation?.lng,
        ],
        maxZoom
      )
      map.fitBounds(localBounds, { maxZoom: maxZoom })
    }
  }, [geoLocData, showLocal, userLocation])

  return (
    <div className="relative" style={style}>
      <div id="chapter-map" className="h-full w-full" />
      {!isMapActive && (
        <button
          type="button"
          tabIndex={0}
          className="pointer-events-none absolute inset-0 z-[500] flex cursor-pointer items-center justify-center rounded-[inherit] bg-black/10"
          onClick={() => {
            mapRef.current?.scrollWheelZoom.enable()
            setIsMapActive(true)
          }}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault()
              mapRef.current?.scrollWheelZoom.enable()
              setIsMapActive(true)
            }
          }}
          aria-label="Click to interact with map"
        >
          <p className="pointer-events-auto rounded-md bg-white/90 px-5 py-3 text-sm font-medium text-gray-700 shadow-lg dark:bg-gray-700 dark:text-white">
            Click to interact with map
          </p>
        </button>
      )}
      <div className="absolute top-20 left-3 z-[999] w-fit">
        {onShareLocation && (
          <Tooltip
            showArrow
            content={
              userLocation ? 'Reset location filter' : 'Share your location to find nearby chapters'
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
              <FontAwesomeIcon icon={faLocationDot} size="sm" />
            </Button>
          </Tooltip>
        )}
      </div>
    </div>
  )
}

export default ChapterMap
