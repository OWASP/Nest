import L from 'leaflet'
import { useEffect, useRef } from 'react'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'
import 'leaflet.markercluster'

const ChapterMap = ({ geoLocData }) => {
  const mapRef = useRef<L.Map | null>(null)

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

    const markerClusterGroup = L.markerClusterGroup()

    const bounds: [number, number][] = []
    geoLocData.forEach((chapter) => {
      if (chapter._geoloc) {
        const marker = L.marker([chapter._geoloc.lat, chapter._geoloc.lng])
        marker.bindPopup(chapter.idx_name)
        markerClusterGroup.addLayer(marker)
        bounds.push([chapter._geoloc.lat, chapter._geoloc.lng])
      }
    })

    map.addLayer(markerClusterGroup)

    if (bounds.length > 0) {
      map.fitBounds(bounds as L.LatLngBoundsExpression)
    }
  }, [geoLocData])

  return <div id="chapter-map" className="rounded-2xl" style={{ height: '400px', width: '100%' }} />
}

export default ChapterMap
