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

  const normalizedData = useMemo(() => {
    return geoLocData.map((chapter) => ({
      lat: '_geoloc' in chapter ? chapter._geoloc.lat : chapter.geoLocation.lat,
      lng: '_geoloc' in chapter ? chapter._geoloc.lng : chapter.geoLocation.lng,
      key: chapter.key,
      name: chapter.name,
    }))
  }, [geoLocData])

  //for reference: https://leafletjs.com/reference.html#map-example
  useEffect(() => {
    if (!mapRef.current) {
      mapRef.current = L.map('chapter-map', {
        worldCopyJump: false, // Prevents the map from wrapping around the world
        maxBounds: [
          [-90, -180], // Southwest corner of the map bounds (latitude, longitude)
          [90, 180], // Northeast corner of the map bounds (latitude, longitude)
        ],
        maxBoundsViscosity: 1.0,
      }).setView([20, 0], 2)

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        className: 'map-tiles',
      }).addTo(mapRef.current)
    }

    const map = mapRef.current

    // Remove previous markers
    map.eachLayer((layer) => {
      if (layer instanceof L.Marker || layer instanceof L.LayerGroup) {
        map.removeLayer(layer)
      }
    })

    const markerClusterGroup = L.markerClusterGroup()
    const bounds: [number, number][] = []
    normalizedData.forEach((chapter) => {
      const markerIcon = new L.Icon({
        iconAnchor: [12, 41], // Anchor point
        iconRetinaUrl: '/img/marker-icon-2x.png',
        iconSize: [25, 41], // Default size for Leaflet markers
        iconUrl: '/img/marker-icon.png',
        popupAnchor: [1, -34], // Popup position relative to marker
        shadowSize: [41, 41], // Shadow size
        shadowUrl: '/img/marker-shadow.png',
      })
      const marker = L.marker([chapter.lat, chapter.lng], {
        icon: markerIcon,
      })
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

    if (bounds.length > 0) {
      map.fitBounds(bounds as L.LatLngBoundsExpression, { maxZoom: 10 })
    }
  }, [normalizedData])

  return <div id="chapter-map" className="rounded-2xl dark:bg-[#212529] rounded-lg" style={style} />
}

export default ChapterMap
