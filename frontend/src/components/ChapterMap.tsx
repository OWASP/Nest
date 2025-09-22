'use client'
import L, { MarkerClusterGroup } from 'leaflet'
import React, { useEffect, useRef } from 'react'
import type { Chapter } from 'types/chapter'
import 'leaflet.markercluster'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'
import 'leaflet.markercluster'

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
        className: 'map-tiles',
      }).addTo(mapRef.current)
    }

    const map = mapRef.current

    if (!markerClusterRef.current) {
      markerClusterRef.current = L.markerClusterGroup()
      map.addLayer(markerClusterRef.current)
    } else {
      markerClusterRef.current.clearLayers()
    }

    const markerClusterGroup = markerClusterRef.current

    const markers = geoLocData.map((chapter) => {
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
          chapter._geoloc?.lat || chapter.geoLocation?.lat,
          chapter._geoloc?.lng || chapter.geoLocation?.lng,
        ],
        { icon: markerIcon }
      )
      const popup = L.popup()
      const popupContent = document.createElement('div')
      popupContent.className = 'popup-content'
      popupContent.textContent = chapter.name
      popupContent.addEventListener('click', () => {
        window.location.href = `/chapters/${chapter.key}`
      })
      popup.setContent(popupContent)
      marker.bindPopup(popup)
      return marker
    })

    markerClusterGroup.addLayers(markers)

    if (showLocal && geoLocData.length > 0) {
      const maxNearestChapters = 5
      const localChapters = geoLocData.slice(0, maxNearestChapters - 1)
      const localBounds = L.latLngBounds(
        localChapters.map((chapter) => [
          chapter._geoloc?.lat || chapter.geoLocation?.lat,
          chapter._geoloc?.lng || chapter.geoLocation?.lng,
        ])
      )
      const maxZoom = 7
      const nearestChapter = geoLocData[0]
      map.setView(
        [
          nearestChapter._geoloc?.lat || nearestChapter.geoLocation?.lat,
          nearestChapter._geoloc?.lng || nearestChapter.geoLocation?.lng,
        ],
        maxZoom
      )
      map.fitBounds(localBounds, { maxZoom: maxZoom })
    }
  }, [geoLocData, showLocal])

  return <div id="chapter-map" style={style} />
}

export default ChapterMap
