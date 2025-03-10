import L from 'leaflet'
import React, { useEffect, useMemo, useRef } from 'react'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'
import 'leaflet.markercluster'
import { GeoLocDataAlgolia, GeoLocDataGraphQL } from 'types/chapter'

const ChapterMap = ({
  geoLocData,
  style,
}: {
  geoLocData: GeoLocDataGraphQL[] | GeoLocDataAlgolia[]
  style: React.CSSProperties
}) => {
  const mapRef = useRef<L.Map | null>(null)
  const markerClusterRef = useRef<L.MarkerClusterGroup | null>(null)

  const normalizedData = useMemo(() => {
    return geoLocData.map((chapter) => ({
      lat: '_geoloc' in chapter ? chapter._geoloc.lat : chapter.geoLocation.lat,
      lng: '_geoloc' in chapter ? chapter._geoloc.lng : chapter.geoLocation.lng,
      key: chapter.key,
      name: chapter.name,
    }))
  }, [geoLocData])

  useEffect(() => {
    if (!mapRef.current) {
      mapRef.current = L.map('chapter-map', {
        worldCopyJump: false,
        maxBounds: [
          [-90, -180],
          [90, 180],
        ],
        maxBoundsViscosity: 1.0,
      }).setView([20, 0], 2)

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
      }).addTo(mapRef.current)
    }

    const map = mapRef.current

    map.eachLayer((layer) => {
      if (layer instanceof L.Marker || layer instanceof L.LayerGroup) {
        map.removeLayer(layer)
      }
    })

    // Create a new marker cluster group
    const markerClusterGroup = L.markerClusterGroup()
    const bounds: [number, number][] = []
    markerClusterRef.current = markerClusterGroup

    // Validate and filter out invalid coordinates
    const validChapters = normalizedData.filter(
      (chapter) =>
        chapter.lat !== null &&
        chapter.lng !== null &&
        !isNaN(chapter.lat) &&
        !isNaN(chapter.lng) &&
        chapter.lat >= -90 &&
        chapter.lat <= 90 &&
        chapter.lng >= -180 &&
        chapter.lng <= 180
    )

    // Create markers for all chapters
    validChapters.forEach((chapter) => {
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
      const popup = L.popup()
      const popupContent = document.createElement('div')
      popupContent.className = 'popup-content'
      popupContent.textContent = chapter.name
      popupContent.addEventListener('click', () => {
        window.location.href = `/chapters/${chapter.key}`
      })
      popup.setContent(popupContent)
      marker.bindPopup(popup)
      markerClusterGroup.addLayer(marker)
      bounds.push([chapter.lat, chapter.lng])
    })

    map.addLayer(markerClusterGroup)

    // Determine map view based on 6th index (index 5)
    try {
      if (validChapters.length >= 6) {
        // Specifically target the 6th chapter (index 5)
        const sixthChapter = validChapters[5]

        // Take the first 6 chapters for bounds
        const localChapters = validChapters.slice(0, 6)
        const temp = localChapters.map((ch) => [ch.lat, ch.lng])
        const localBounds = L.latLngBounds(temp)

        map.setView([sixthChapter.lat, sixthChapter.lng], 6)
        map.fitBounds(localBounds, { maxZoom: 10 })
      } else if (validChapters.length > 0) {
        // Fallback if fewer than 6 chapters
        const firstChapter = validChapters[0]
        map.setView([firstChapter.lat, firstChapter.lng], 6)
      } else if (bounds.length > 0) {
        map.fitBounds(bounds)
      } else {
        map.setView([20, 0], 2)
      }
    } catch {
      map.setView([20, 0], 2)
    }
  }, [normalizedData])

  return <div id="chapter-map" style={style} />
}

export default ChapterMap
