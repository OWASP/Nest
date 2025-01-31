import L from 'leaflet'
import { useEffect, useRef } from 'react'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'
import 'leaflet.markercluster'

const ChapterMap = ({ geoLocData }) => {
  const mapRef = useRef<L.Map | null>(null)
  //for reference: https://leafletjs.com/reference.html#map-example
  useEffect(() => {
    if (!mapRef.current) {
      mapRef.current = L.map('chapter-map', {
        worldCopyJump: false, // Prevents the map from wrapping around the world
        maxBounds: [
          [-90, -180], // Southwest corner of the map bounds (latitude, longitude)
          [90, 180], // Northeast corner of the map bounds (latitude, longitude)
        ],
        maxBoundsViscosity: 1.0, // How smoothly the map bounces back when the user tries to pan outside the max bounds
      }).setView([20, 0], 2) // Initial view of the map: [latitude, longitude], zoom level
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        className: 'map-tiles',
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
        const markerIcon = new L.Icon({
          iconAnchor: [12, 41], // Anchor point
          iconRetinaUrl: '/img/marker-icon-2x.png',
          iconSize: [25, 41], // Default size for Leaflet markers
          iconUrl: '/img/marker-icon.png',
          popupAnchor: [1, -34], // Popup position relative to marker
          shadowSize: [41, 41], // Shadow size
          shadowUrl: '/img/marker-shadow.png',
        })
        const marker = L.marker([chapter._geoloc.lat, chapter._geoloc.lng], { icon: markerIcon })
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
        bounds.push([chapter._geoloc.lat, chapter._geoloc.lng])
      }
    })

    map.addLayer(markerClusterGroup)

    if (bounds.length > 0) {
      map.fitBounds(bounds as L.LatLngBoundsExpression, { maxZoom: 10 })
    }
  }, [geoLocData])

  return (
    <div
      id="chapter-map"
      className="rounded-2xl"
      style={{ height: '400px', width: '100%', zIndex: '0' }}
    />
  )
}

export default ChapterMap
