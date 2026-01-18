declare module 'react-leaflet-cluster' {
  import { MarkerClusterGroupOptions } from 'leaflet'
  import React, { Component } from 'react'
  import { LayerGroupProps } from 'react-leaflet'

  interface MarkerClusterGroupProps extends LayerGroupProps {
    children?: React.ReactNode
    options?: MarkerClusterGroupOptions
    chunkedLoading?: boolean
  }

  export default class MarkerClusterGroup extends Component<MarkerClusterGroupProps> {}
}
