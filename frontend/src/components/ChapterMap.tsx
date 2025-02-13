import L from 'leaflet'
import React, { useEffect, useRef } from 'react'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'
import 'leaflet.markercluster'
import { useTheme } from './ThemeProvider'

interface GeoLocData {
  _geoloc: {
    lat: number
    lng: number
  }
  name: string
  key: string
}

interface ChapterMapProps {
  geoLocData?: GeoLocData[]
  style?: React.CSSProperties
}

const ChapterMap: React.FC<ChapterMapProps> = ({ geoLocData = [], style }) => {
  const { dark } = useTheme()
  const mapRef = useRef<L.Map | null>(null)
  const tileLayerRef = useRef<L.TileLayer | null>(null)
  const markerClusterGroupRef = useRef<L.MarkerClusterGroup | null>(null)
  const mapContainerRef = useRef<HTMLDivElement | null>(null)

  //for reference: https://leafletjs.com/reference.html#map-example
  useEffect(() => {
    if (!mapContainerRef.current) return

    if (!mapRef.current) {
      mapRef.current = L.map(mapContainerRef.current, {
        center: [20, 0],
        zoom: 2,
        // minZoom: 2,
        maxZoom: 10,
      })
    }
  }, [])

  useEffect(() => {
    if (!mapRef.current) return
    const map = mapRef.current

    const tileLayerUrl = dark
      ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
      : 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'

    if (tileLayerRef.current) {
      map.removeLayer(tileLayerRef.current)
    }
    tileLayerRef.current = L.tileLayer(tileLayerUrl, {
      attribution: '© OpenStreetMap contributors',
    })
    tileLayerRef.current.addTo(map)
  }, [dark])

  useEffect(() => {
    if (!mapRef.current) return
    const map = mapRef.current

    if (markerClusterGroupRef.current) {
      map.removeLayer(markerClusterGroupRef.current)
    }

    const markerClusterGroup = L.markerClusterGroup()
    markerClusterGroupRef.current = markerClusterGroup

    let bounds: L.LatLngBounds | null = null
    let validMarkers = 0

    geoLocData.forEach((chapter) => {
      if (!chapter._geoloc || isNaN(chapter._geoloc.lat) || isNaN(chapter._geoloc.lng)) return
      const { lat, lng } = chapter._geoloc
      const marker = L.marker([lat, lng])
      marker.bindPopup(`<div>${chapter.name}</div>`)
      markerClusterGroup.addLayer(marker)

      if (!bounds) {
        bounds = L.latLngBounds([lat, lng], [lat, lng])
      } else {
        bounds.extend([lat, lng])
      }
      validMarkers++
    })

    map.addLayer(markerClusterGroup)

    if (bounds && validMarkers > 0) {
      map.fitBounds(bounds, { maxZoom: 10 })
    } else {
      map.setView([20, 0], 2) // Default view if no markers are present
    }
  }, [geoLocData])

  return (
    <div
      ref={mapContainerRef}
      id="chapter-map"
      className="rounded-2xl"
      style={{
        height: '500px',
        width: '100%',
        background: dark ? '#282d33' : '#F0F0F0', // Apply blue background only in dark mode
        ...style,
      }}
    ></div>
  )
}

export default ChapterMap
