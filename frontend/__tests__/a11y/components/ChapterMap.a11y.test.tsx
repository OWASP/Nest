import { mockChapterData } from '@mockData/mockChapterData'
import { screen, fireEvent, render, waitFor } from '@testing-library/react'
import { axe } from 'jest-axe'
import * as L from 'leaflet'
import { useTheme } from 'next-themes'
import React, { useEffect } from 'react'
import ChapterMap from 'components/ChapterMap'

const mockMap = {
  setView: jest.fn().mockReturnThis(),
  fitBounds: jest.fn().mockReturnThis(),
  scrollWheelZoom: {
    enable: jest.fn(),
    disable: jest.fn(),
  },
  dragging: {
    enable: jest.fn(),
    disable: jest.fn(),
  },
  touchZoom: {
    enable: jest.fn(),
    disable: jest.fn(),
  },
  doubleClickZoom: {
    enable: jest.fn(),
    disable: jest.fn(),
  },
  keyboard: {
    enable: jest.fn(),
    disable: jest.fn(),
  },
  getContainer: jest.fn(() => ({
    clientWidth: 800,
    clientHeight: 400,
  })),
  setMinZoom: jest.fn(),
}

const mockZoomControl = {
  addTo: jest.fn().mockReturnThis(),
  remove: jest.fn(),
}

/* eslint-disable @typescript-eslint/naming-convention */
jest.mock('leaflet', () => ({
  map: jest.fn(() => mockMap),
  tileLayer: jest.fn(() => ({
    addTo: jest.fn().mockReturnThis(),
  })),
  marker: jest.fn(() => ({
    bindPopup: jest.fn().mockReturnThis(),
  })),
  popup: jest.fn(() => ({
    setContent: jest.fn().mockReturnThis(),
  })),
  latLngBounds: jest.fn(() => ({})),
  Icon: jest.fn(() => ({})),
  divIcon: jest.fn(() => ({})),
  control: {
    zoom: jest.fn(() => mockZoomControl),
  },
}))
/* eslint-enable @typescript-eslint/naming-convention */

// Mock CSS imports
jest.mock('leaflet/dist/leaflet.css', () => ({}))
jest.mock('leaflet.markercluster/dist/MarkerCluster.css', () => ({}))
jest.mock('leaflet.markercluster/dist/MarkerCluster.Default.css', () => ({}))
jest.mock('leaflet.markercluster', () => ({}))

// Mock react-leaflet
jest.mock('react-leaflet', () => ({
  MapContainer: ({
    children,
    center,
    zoom,
    scrollWheelZoom,
    style,
    zoomControl,
    maxBounds,
    maxBoundsViscosity,
    className,
  }: {
    children: React.ReactNode
    center: L.LatLngExpression
    zoom: number
    scrollWheelZoom: boolean
    style: React.CSSProperties
    zoomControl: boolean
    maxBounds: L.LatLngBoundsExpression
    maxBoundsViscosity: number
    className: string
  }) => {
    useEffect(() => {
      L.map('chapter-map', {
        worldCopyJump: false,
        maxBounds,
        maxBoundsViscosity,
        scrollWheelZoom,
        zoomControl,
      }).setView(center, zoom)
    }, [center, zoom, scrollWheelZoom, zoomControl, maxBounds, maxBoundsViscosity])
    return (
      <div id="chapter-map" style={style} className={className}>
        {children}
      </div>
    )
  },
  TileLayer: ({
    attribution,
    url,
    className,
  }: {
    attribution: string
    url: string
    className: string
  }) => {
    useEffect(() => {
      L.tileLayer(url, { attribution, className }).addTo(mockMap as unknown as L.Map)
    }, [url, attribution, className])
    return null
  },
  Marker: ({
    children,
    position,
    icon,
  }: {
    children: React.ReactNode
    position: L.LatLngExpression
    icon: L.Icon
  }) => {
    useEffect(() => {
      const marker = L.marker(position, { icon })
      marker.bindPopup(L.popup().setContent('mock content'))
    }, [position, icon])
    return <div data-testid="marker">{children}</div>
  },
  Popup: ({ children }: { children: React.ReactNode }) => <div data-testid="popup">{children}</div>,
  useMap: () => mockMap as unknown as L.Map,
}))

// Mock react-leaflet-cluster
jest.mock('react-leaflet-cluster', () => ({
  __esModule: true,
  default: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="marker-cluster-group">{children}</div>
  ),
}))

const defaultProps = {
  geoLocData: mockChapterData.chapters,
  showLocal: false,
  style: { width: '100%', height: '400px' },
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('ChapterMap a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  it('should not have any accessibility violations in locked state', async () => {
    const { baseElement } = render(<ChapterMap {...defaultProps} />)

    const results = await axe(baseElement)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when map is unlocked', async () => {
    const { baseElement } = render(<ChapterMap {...defaultProps} onShareLocation={jest.fn()} />)

    const unlockButton = screen.getByLabelText('Unlock map')
    fireEvent.click(unlockButton)

    await waitFor(() => expect(screen.getByLabelText(/Share location/i)).toBeInTheDocument())

    const results = await axe(baseElement)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when user location is shared', async () => {
    const { baseElement } = render(
      <ChapterMap
        {...defaultProps}
        showLocal={true}
        userLocation={{ latitude: 10, longitude: 10 }}
      />
    )

    const results = await axe(baseElement)
    expect(results).toHaveNoViolations()
  })
})
