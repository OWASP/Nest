declare module 'react-leaflet' {
  import * as L from 'leaflet'
  import * as React from 'react'

  interface MapContainerProps {
    center?: L.LatLngExpression
    zoom?: number
    scrollWheelZoom?: boolean
    style?: React.CSSProperties
    zoomControl?: boolean
    minZoom?: number
    maxZoom?: number
    worldCopyJump?: boolean
    maxBounds?: L.LatLngBoundsExpression
    maxBoundsViscosity?: number
    children?: React.ReactNode
  }

  interface TileLayerProps {
    attribution?: string
    url: string
    className?: string
  }

  interface MarkerProps {
    position: L.LatLngExpression
    icon?: L.Icon | L.DivIcon
    title?: string
    children?: React.ReactNode
  }

  interface PopupProps {
    children?: React.ReactNode
  }

  export const MapContainer: React.FC<MapContainerProps>
  export const TileLayer: React.FC<TileLayerProps>
  export const Marker: React.FC<MarkerProps>
  export const Popup: React.FC<PopupProps>
  export function useMap(): L.Map
}
