'use client'
import { Button } from '@heroui/button'
import { Tooltip } from '@heroui/tooltip'
import L from 'leaflet'
import { useRouter } from 'next/navigation'
import React, { useEffect, useMemo, useRef, useState } from 'react'
import { FaUnlock } from 'react-icons/fa'
import { FaLocationDot } from 'react-icons/fa6'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import MarkerClusterGroup from 'react-leaflet-cluster'
import type { Chapter } from 'types/chapter'
import type { UserLocation } from 'utils/geolocationUtils'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'

const MapZoomControl = ({ isMapActive }: { isMapActive: boolean }) => {
  const map = useMap()
  const zoomControlRef = useRef<L.Control.Zoom | null>(null)

  useEffect(() => {
    if (!map?.getContainer()) return

    if (isMapActive) {
      map.scrollWheelZoom.enable()
      map.dragging.enable()
      map.touchZoom.enable()
      map.doubleClickZoom.enable()
      map.keyboard.enable()

      zoomControlRef.current?.remove()
      zoomControlRef.current = L.control.zoom({ position: 'topleft' })
      zoomControlRef.current.addTo(map)
    } else {
      map.scrollWheelZoom.disable()
      map.dragging.disable()
      map.touchZoom.disable()
      map.doubleClickZoom.disable()
      map.keyboard.disable()

      zoomControlRef.current?.remove()
      zoomControlRef.current = null
    }
  }, [isMapActive, map])

  return null
}

const ChapterMap = ({
  geoLocData,
  showLocal,
  style,
  userLocation,
  onShareLocation,
}: {
  geoLocData: Chapter[]
  showLocal: boolean
  style: React.CSSProperties
  userLocation?: UserLocation | null
  onShareLocation?: () => void
}) => {
  const router = useRouter()
  const [isMapActive, setIsMapActive] = useState(false)

  const handlePointerLeave = (e: React.PointerEvent<HTMLElement>) => {
    if (!isMapActive) return

    const rect = e.currentTarget.getBoundingClientRect()
    const inside =
      e.clientX >= rect.left &&
      e.clientX <= rect.right &&
      e.clientY >= rect.top &&
      e.clientY <= rect.bottom

    if (!inside) setIsMapActive(false)
  }

  const validGeoLocData = useMemo(
    () =>
      geoLocData.filter((c) => {
        const lat = c._geoloc?.lat ?? c.geoLocation?.lat
        const lng = c._geoloc?.lng ?? c.geoLocation?.lng
        return typeof lat === 'number' && typeof lng === 'number'
      }),
    [geoLocData]
  )

  const chapterIcon = useMemo(
    () =>
      new L.Icon({
        iconUrl: '/img/marker-icon.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
      }),
    []
  )

  return (
    <section
      aria-label="Chapter Map"
      className="relative isolate z-0 overflow-hidden rounded-lg bg-slate-200 dark:bg-[#1a1a1a] cursor-default" // ✅ FIX
      style={style}
      onPointerLeave={handlePointerLeave}
    >
      <MapContainer
        center={[20, 0]}
        zoom={2}
        scrollWheelZoom={isMapActive}
        style={{
          height: '100%',
          width: '100%',
          outline: 'none',
          background: 'transparent',
          cursor: 'default', // ✅ FIX
        }}
        zoomControl={false}
      >
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

        <MapZoomControl isMapActive={isMapActive} />

        <MarkerClusterGroup>
          {validGeoLocData.map((chapter) => (
            <Marker
              key={chapter.key}
              position={[
                chapter._geoloc?.lat ?? chapter.geoLocation?.lat,
                chapter._geoloc?.lng ?? chapter.geoLocation?.lng,
              ]}
              icon={chapterIcon}
            >
              <Popup>
                <button
                  type="button"
                  className="cursor-pointer font-medium hover:text-blue-600"
                  onClick={() => router.push(`/chapters/${chapter.key}`)}
                >
                  {chapter.name}
                </button>
              </Popup>
            </Marker>
          ))}
        </MarkerClusterGroup>
      </MapContainer>

      {!isMapActive && (
        <div className="absolute inset-0 flex items-center justify-center">
          <button
            className="cursor-pointer"
            onClick={() => setIsMapActive(true)}
          >
            <FaUnlock /> Unlock map
          </button>
        </div>
      )}
    </section>
  )
}

export default ChapterMap