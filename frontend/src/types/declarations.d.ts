declare module 'react-leaflet' {
  import * as L from 'leaflet'
  import * as React from 'react'

  type SafeProps = Record<string, unknown>

  export const MapContainer: React.FC<SafeProps>
  export const TileLayer: React.FC<SafeProps>
  export const Marker: React.FC<SafeProps>
  export const Popup: React.FC<SafeProps>
  export function useMap(): L.Map
}
