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
}: {
  geoLocData: GeoLocDataGraphQL[] | GeoLocDataAlgolia[]
  showLocal: boolean
  style: React.CSSProperties
}) => {
  const mapRef = useRef<L.Map | null>(null)
  const markerClusterRef = useRef<L.MarkerClusterGroup | null>(null)

  // Memoize processed chapter data
  const chapters = useMemo(() => {
    return geoLocData.map((chapter) => ({
      lat: '_geoloc' in chapter ? chapter._geoloc.lat : chapter.geoLocation.lat,
      lng: '_geoloc' in chapter ? chapter._geoloc.lng : chapter.geoLocation.lng,
      key: chapter.key,
      name: chapter.name,
    }))
  }, [geoLocData])

  // Function to initialize map (runs once)
  useEffect(() => {
    if (!mapRef.current) {
      const map = L.map('chapter-map', {
        worldCopyJump: false,
        maxBounds: [
          [-90, -180],
          [90, 180],
        ],
        maxBoundsViscosity: 1.0,
      }).setView([20, 0], 2)

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        className: 'map-tiles',
      }).addTo(map)

      mapRef.current = map
    }
  }, [])

  // Function to update markers efficiently
  const updateMarkers = useCallback(() => {
    if (!mapRef.current) return
    const map = mapRef.current

    // Clear existing markers if needed
    if (markerClusterRef.current) {
      markerClusterRef.current.clearLayers()
    } else {
      markerClusterRef.current = L.markerClusterGroup()
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

      const marker = L.marker([chapter.lat, chapter.lng], { icon: markerIcon }).bindPopup(
        `<div class="popup-content">${chapter.name}</div>`
      )

      marker.on('click', () => {
        window.location.href = `/chapters/${chapter.key}`
      })

      markerClusterGroup.addLayer(marker)
      bounds.push([chapter.lat, chapter.lng])
    })

    map.addLayer(markerClusterGroup)

    // Zoom to local area if enabled
    if (showLocal && chapters.length > 0) {
      const maxNearestChapters = 5
      const localChapters = chapters.slice(0, maxNearestChapters)
      const localBounds = L.latLngBounds(localChapters.map((ch) => [ch.lat, ch.lng]))
      const maxZoom = 7

      map.fitBounds(localBounds, { maxZoom })
    }
  }, [chapters, showLocal])

  // Update markers when geoLocData changes
  useEffect(() => {
    updateMarkers()
  }, [updateMarkers])

  return <div id="chapter-map" style={style} />
}

export default ChapterMap
