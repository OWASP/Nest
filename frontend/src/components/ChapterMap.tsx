import L from 'leaflet'
import { useEffect, useRef } from 'react'
import 'leaflet/dist/leaflet.css'

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
      if (layer instanceof L.Marker) {
        map.removeLayer(layer)
      }
    })

    const bounds: [number, number][] = []
    geoLocData.forEach((chapter) => {
      if (chapter._geoloc) {
        L.marker([chapter._geoloc.lat, chapter._geoloc.lng]).addTo(map).bindPopup(chapter.idx_name)
        bounds.push([chapter._geoloc.lat, chapter._geoloc.lng])
      }
    })

    if (bounds.length > 0) {
      map.fitBounds(bounds as L.LatLngBoundsExpression)
    }
  }, [geoLocData])

  return <div id="chapter-map" className="rounded-2xl" style={{ height: '400px', width: '100%' }} />
}

export default ChapterMap
