'use client'
import L, { MarkerClusterGroup } from 'leaflet'
import React, { useEffect, useRef, useState } from 'react'
import type { Chapter } from 'types/chapter'
import 'leaflet.markercluster'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'
import 'leaflet.markercluster'
import { FiUnlock } from 'react-icons/fi'


const ChapterMap = ({
  geoLocData,
  showLocal,
  style,
}: {
  geoLocData: Chapter[]
  showLocal: boolean
  style: React.CSSProperties
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

    if (showLocal && validGeoLocData.length > 0) {
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
  }, [geoLocData, showLocal])

  return (
    <div className="relative" style={style}>
      <div id="chapter-map" className="h-full w-full" />
      {!isMapActive && (
        <button
          type="button"
          tabIndex={0}
          className="absolute inset-0 z-[1000] flex cursor-pointer items-center justify-center rounded-[inherit] bg-black/10"
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
          aria-label="Unlock map"
        >
          <p className="flex items-center gap-2 rounded-md bg-white/90 px-5 py-3 text-sm font-medium text-gray-700 shadow-lg dark:bg-gray-700 dark:text-white">
            <FiUnlock size={16} />
            Unlock map
          </p>
        </button>
      )}
    </div>
  )
}

export default ChapterMap
