import L from 'leaflet'
import React, { useEffect, useMemo, useRef } from 'react'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'
import 'leaflet.markercluster'
import { GeoLocDataAlgolia, GeoLocDataGraphQL } from 'types/chapter'
import { desktopViewMinWidth } from 'utils/constants'
import { Tooltip } from 'components/ui/tooltip'

interface ChapterMapProps {
  geoLocData: GeoLocDataGraphQL[] | GeoLocDataAlgolia[]
  showLocal: boolean
  style?: React.CSSProperties
}

const ChapterMap: React.FC<ChapterMapProps> = ({ geoLocData, showLocal, style }) => {
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
    map.eachLayer((layer) => {
      if (layer instanceof L.Marker || layer instanceof L.LayerGroup) {
        map.removeLayer(layer)
      }
    })

    const markerClusterGroup = L.markerClusterGroup()
    markerClusterRef.current = markerClusterGroup
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

    if (showLocal && chapters.length) {
      const maxNearestChapters = 5
      const localChapters = chapters.slice(0, maxNearestChapters - 1)
      const localBounds = L.latLngBounds(localChapters.map((ch) => [ch.lat, ch.lng]))
      const firstChapter = chapters[0]
      const maxZoom = 7

      map.setView([firstChapter.lat, firstChapter.lng], maxZoom)
      map.fitBounds(localBounds, { maxZoom })
    }

    const isDesktop = window.innerWidth >= desktopViewMinWidth
    if (isDesktop) {
      map.scrollWheelZoom.disable()

      const handleKeyDown = (e: KeyboardEvent) => {
        if (e.ctrlKey) {
          map.scrollWheelZoom.enable()
        }
      }

      const handleKeyUp = () => {
        map.scrollWheelZoom.disable()
      }

      window.addEventListener('keydown', handleKeyDown)
      window.addEventListener('keyup', handleKeyUp)

      return () => {
        window.removeEventListener('keydown', handleKeyDown)
        window.removeEventListener('keyup', handleKeyUp)
      }
    }
  }, [chapters, showLocal])

  return (
    <Tooltip
      content="Press Ctrl while scrolling to zoom"
      closeDelay={100}
      openDelay={100}
      showArrow
      positioning={{ placement: 'top' }}
      disabled={window.innerWidth < desktopViewMinWidth}
    >
      <div style={{ position: 'relative' }}>
        {/* Ensure the map container has a minimum height to avoid being hidden */}
        <div
          id="chapter-map"
          className="rounded-lg dark:bg-[#212529]"
          style={{
            minHeight: '400px', // set a minimum height
            width: '100%', // or a specific width if desired
            ...style,
          }}
        />
      </div>
    </Tooltip>
  )
}

export default ChapterMap
