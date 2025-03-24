import L from 'leaflet'
import React, { useEffect, useMemo, useRef, useCallback } from 'react'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'
import 'leaflet.markercluster'
import { GeoLocDataAlgolia, GeoLocDataGraphQL } from 'types/chapter'

const ChapterMap = ({
  geoLocData,
  showLocal,
  style,
  isDarkMode,
}: {
  geoLocData: GeoLocDataGraphQL[] | GeoLocDataAlgolia[]
  showLocal: boolean
  style: React.CSSProperties
  isDarkMode?: boolean
}) => {
  const mapRef = useRef<L.Map | null>(null)
  const markerClusterRef = useRef<L.MarkerClusterGroup | null>(null)

  const chapters = useMemo(() => {
    return geoLocData.map((chapter) => ({
      lat: '_geoloc' in chapter ? chapter._geoloc.lat : chapter.geoLocation.lat,
      lng: '_geoloc' in chapter ? chapter._geoloc.lng : chapter.geoLocation.lng,
      key: chapter.key,
      name: chapter.name,
    }))
  }, [geoLocData])

  useEffect(() => {
    if (!mapRef.current) {
      const map = L.map('chapter-map', {
        worldCopyJump: false,
        maxBounds: [
          [-90, -180],
          [90, 180],
        ],
        maxBoundsViscosity: 1.0,
        preferCanvas: true,
      }).setView([20, 0], 2)


      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        className: 'map-tiles',
        useCache: false,
      }).addTo(map)

      mapRef.current = map
    }
  }, [])

  const updateMarkers = useCallback(() => {
    if (!mapRef.current) return
    const map = mapRef.current

    if (!markerClusterRef.current) {
      markerClusterRef.current = L.markerClusterGroup()
    } else {
      markerClusterRef.current.clearLayers()
    }

    const markerClusterGroup = markerClusterRef.current
    const bounds: [number, number][] = []

    chapters.forEach((chapter) => {
      const markerIcon = new L.Icon({
        iconAnchor: [12, 41],
        iconRetinaUrl: '/img/marker-icon-2x.png',
        iconSize: [25, 41],
        iconUrl: '/img/marker-icon.png',
        popupAnchor: [1, -34],
        shadowSize: [41, 41],
        shadowUrl: '/img/marker-shadow.png',
      })

      const marker = L.marker([chapter.lat, chapter.lng], { icon: markerIcon })


      const popupContent = document.createElement('div')
      popupContent.className = 'popup-content'


      if (isDarkMode) {
        popupContent.style.backgroundColor = '#2b2b2b'
        popupContent.style.color = '#ffffff'
        popupContent.style.border = '1px solid #ffffff'
      } else {
        popupContent.style.backgroundColor = '#ffffff'
        popupContent.style.color = '#000000'
        popupContent.style.border = '1px solid #000000'
      }


      const chapterLink = document.createElement('a')
      chapterLink.href = `/chapters/${chapter.key}`
      chapterLink.textContent = chapter.name
      chapterLink.style.textDecoration = 'underline'
      chapterLink.style.cursor = 'pointer'

      popupContent.appendChild(chapterLink)
      marker.bindPopup(popupContent)

      markerClusterGroup.addLayer(marker)
      bounds.push([chapter.lat, chapter.lng])
    })

    map.addLayer(markerClusterGroup)

    if (showLocal && chapters.length > 0) {
      const maxNearestChapters = 5
      const localChapters = chapters.slice(0, maxNearestChapters)
      const localBounds = L.latLngBounds(localChapters.map((ch) => [ch.lat, ch.lng]))
      const nearestChapter = chapters[0]

      map.setView([nearestChapter.lat, nearestChapter.lng], 7)
      map.fitBounds(localBounds, { maxZoom: 7 }) // Restored maxZoom
    }
  }, [chapters, showLocal, isDarkMode])

  useEffect(() => {
    updateMarkers()
  }, [updateMarkers])

  return (
    <div
      id="chapter-map"
      style={{
        ...style,
        backgroundColor: isDarkMode ? '#1e1e1e' : '#ffffff',
        padding: '10px',
        borderRadius: '8px',
      }}
    />
  )
}

export default ChapterMap
