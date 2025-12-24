'use client'
import { Button } from '@heroui/button'
import { Tooltip } from '@heroui/tooltip'
import L, { MarkerClusterGroup } from 'leaflet'
import React, { useEffect, useRef, useState } from 'react'
import { FaUnlock } from 'react-icons/fa'
import { FaLocationDot } from 'react-icons/fa6'
import type { Chapter } from 'types/chapter'
import type { UserLocation } from 'utils/geolocationUtils'
import 'leaflet.markercluster'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'

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
  const userMarkerRef = useRef<L.Marker | null>(null)
  const zoomControlRef = useRef<L.Control.Zoom | null>(null)
  const initialViewRef = useRef<{ center: L.LatLngExpression; zoom: number } | null>(null)
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
        minZoom: 2.4,
        dragging: false,
        doubleClickZoom: false,
        touchZoom: false,
        boxZoom: false,
        keyboard: false,
        scrollWheelZoom: false,
        zoomControl: false,
      }).setView([20, 0], 2.4)

      initialViewRef.current = {
        center: mapRef.current.getCenter(),
        zoom: mapRef.current.getZoom(),
      }

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        className: 'map-tiles',
        noWrap: true,
      }).addTo(mapRef.current)



      mapRef.current.on('mouseout', (e: L.LeafletMouseEvent) => {
        const originalEvent = e.originalEvent as MouseEvent
        const relatedTarget = originalEvent.relatedTarget as Node | null
        const container = mapRef.current?.getContainer()
        const mapParent = container?.parentElement
        if (
          relatedTarget &&
          (container?.contains(relatedTarget) || mapParent?.contains(relatedTarget))
        )
          return

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

    if (userMarkerRef.current) {
      userMarkerRef.current.remove()
      userMarkerRef.current = null
    }

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
      userMarkerRef.current = userMarker
    }

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
    } else if (initialViewRef.current) {
      map.setView(initialViewRef.current.center, initialViewRef.current.zoom)
    }
  }, [geoLocData, showLocal, userLocation])

  useEffect(() => {
    const map = mapRef.current
    if (!map) return

    if (isMapActive) {
      map.dragging.enable()
      map.touchZoom.enable()
      map.doubleClickZoom.enable()
      map.scrollWheelZoom.enable()
      map.boxZoom.enable()
      map.keyboard.enable()

      if (!zoomControlRef.current) {
        zoomControlRef.current = L.control.zoom({ position: 'topleft' })
        zoomControlRef.current.addTo(map)
      }
    } else {
      map.dragging.disable()
      map.touchZoom.disable()
      map.doubleClickZoom.disable()
      map.scrollWheelZoom.disable()
      map.boxZoom.disable()
      map.keyboard.disable()

      if (zoomControlRef.current) {
        zoomControlRef.current.remove()
        zoomControlRef.current = null
      }
    }

    return () => {
      if (zoomControlRef.current) {
        zoomControlRef.current.remove()
        zoomControlRef.current = null
      }
    }
  }, [isMapActive])

  return (
    <div className="relative" style={style}>
      <div id="chapter-map" className="h-full w-full" />
      {!isMapActive && (
        <div
          className="absolute inset-0 z-[2000] flex items-center justify-center rounded-[inherit] bg-black/10"
        >
          <button
            type="button"
            className="flex cursor-pointer items-center gap-2 rounded-md bg-white/90 px-5 py-3 text-sm font-medium text-gray-700 shadow-lg transition-colors hover:bg-gray-200 hover:text-gray-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600 dark:hover:text-white"
            onClick={() => setIsMapActive(true)}
            aria-label="Unlock map"
          >
            <FaUnlock aria-hidden="true" />
            Unlock map
          </button>
        </div>
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
    </div>
  )
}
export default ChapterMap
