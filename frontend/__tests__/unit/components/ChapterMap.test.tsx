import { render, fireEvent, waitFor } from '@testing-library/react'
import * as L from 'leaflet'
import React, { useEffect } from 'react'
import { Chapter } from 'types/chapter'
import ChapterMap from 'components/ChapterMap'

// Mock Leaflet
let mockMapInstance: unknown = null

const mockMap = {
  setView: jest.fn().mockReturnThis(),
  fitBounds: jest.fn().mockReturnThis(),
  scrollWheelZoom: {
    enable: jest.fn(),
    disable: jest.fn(),
  },
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
  useMap: () => mockMapInstance,
}))

// Mock react-leaflet-cluster
jest.mock('react-leaflet-cluster', () => ({
  __esModule: true,
  default: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="marker-cluster-group">{children}</div>
  ),
}))

// Mock next/navigation
const mockPush = jest.fn()
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}))

describe('ChapterMap Refactored Tests', () => {
  const mockChapterData: Chapter[] = [
    {
      _geoloc: { lat: 40.7128, lng: -74.006 },
      key: 'new-york',
      name: 'New York Chapter',
    } as Chapter,
    {
      geoLocation: { lat: 51.5074, lng: -0.1278 },
      key: 'london',
      name: 'London Chapter',
    } as Chapter,
  ]

  const defaultProps = {
    geoLocData: mockChapterData,
    showLocal: false,
    style: { width: '100%', height: '400px' },
  }

  beforeEach(() => {
    jest.clearAllMocks()
    mockMapInstance = mockMap
  })

  describe('Rendering', () => {
    it('renders the map container and markers', () => {
      const { getByTestId, getAllByTestId } = render(<ChapterMap {...defaultProps} />)

      expect(document.getElementById('chapter-map')).toBeInTheDocument()
      expect(getByTestId('marker-cluster-group')).toBeInTheDocument()
      expect(getAllByTestId('marker')).toHaveLength(2)
    })

    it('renders user location marker when provided', () => {
      const userLocation = { latitude: 10, longitude: 10, accuracy: 10 }
      const { getAllByTestId } = render(
        <ChapterMap {...defaultProps} userLocation={userLocation} />
      )
      expect(getAllByTestId('marker')).toHaveLength(3)
    })
  })

  describe('Map Locking Logic', () => {
    it('shows "Unlock map" button initially', () => {
      const { getByText } = render(<ChapterMap {...defaultProps} />)
      expect(getByText('Unlock map')).toBeInTheDocument()
    })

    it('unlocks map and shows zoom controls on click', async () => {
      const { getByText, queryByText } = render(<ChapterMap {...defaultProps} />)

      const unlockButton = getByText('Unlock map').closest('button')
      fireEvent.click(unlockButton)

      expect(queryByText('Unlock map')).not.toBeInTheDocument()

      await waitFor(() => {
        expect(mockMap.scrollWheelZoom.enable).toHaveBeenCalled()
        expect(L.control.zoom).toHaveBeenCalled()
      })
    })

    it('locks map again on mouse leave', async () => {
      const { getByText, container } = render(<ChapterMap {...defaultProps} />)

      const unlockButton = getByText('Unlock map').closest('button')
      fireEvent.click(unlockButton)
      const wrapper = container.firstChild as HTMLElement
      fireEvent.mouseLeave(wrapper)

      await waitFor(() => {
        expect(mockMap.scrollWheelZoom.disable).toHaveBeenCalled()
        expect(mockZoomControl.remove).toHaveBeenCalled()
        expect(getByText('Unlock map')).toBeInTheDocument()
      })
    })
  })

  describe('MapViewUpdater Logic', () => {
    it('sets world view by default', async () => {
      render(<ChapterMap {...defaultProps} />)
      await waitFor(() => {
        expect(mockMap.setView).toHaveBeenCalledWith([20, 0], 2)
      })
    })

    it('sets local view when showLocal is true', async () => {
      render(<ChapterMap {...defaultProps} showLocal={true} />)
      await waitFor(() => {
        expect(mockMap.setView).toHaveBeenCalledWith([40.7128, -74.006], 7)
        expect(mockMap.fitBounds).toHaveBeenCalled()
      })
    })

    it('uses geoLocation fallback when _geoloc is not available', async () => {
      const geoLocationOnlyData: Chapter[] = [
        {
          geoLocation: { lat: 35.6762, lng: 139.6503 },
          key: 'tokyo',
          name: 'Tokyo Chapter',
        } as Chapter,
      ]

      render(<ChapterMap {...defaultProps} geoLocData={geoLocationOnlyData} showLocal={true} />)

      await waitFor(() => {
        expect(mockMap.setView).toHaveBeenCalledWith([35.6762, 139.6503], 7)
      })
    })
  })

  describe('Share Location Button', () => {
    it('is only visible when map is unlocked', () => {
      const onShareLocation = jest.fn()
      const { queryByLabelText, getByText } = render(
        <ChapterMap {...defaultProps} onShareLocation={onShareLocation} />
      )

      expect(queryByLabelText(/share location/i)).not.toBeInTheDocument()

      fireEvent.click(getByText('Unlock map').closest('button'))
      expect(queryByLabelText(/share location/i)).toBeInTheDocument()
    })

    it('shows "Reset location filter" tooltip when user location is provided', () => {
      const onShareLocation = jest.fn()
      const userLocation = { latitude: 10, longitude: 10, accuracy: 10 }

      const { getByText, getByLabelText } = render(
        <ChapterMap
          {...defaultProps}
          onShareLocation={onShareLocation}
          userLocation={userLocation}
        />
      )
      fireEvent.click(getByText('Unlock map').closest('button'))
      const locationButton = getByLabelText('Reset location filter')
      expect(locationButton).toBeInTheDocument()
    })
  })

  describe('Popup Interactions', () => {
    it('renders chapter name in popup', () => {
      const { getAllByTestId } = render(<ChapterMap {...defaultProps} />)

      const popups = getAllByTestId('popup')
      expect(popups[0]).toHaveTextContent('New York Chapter')
      expect(popups[1]).toHaveTextContent('London Chapter')
    })

    it('popup click handler is set up correctly', () => {
      const { getAllByTestId } = render(<ChapterMap {...defaultProps} />)

      const popups = getAllByTestId('popup')
      const clickableButton = popups[0].querySelector('button')

      expect(clickableButton).toBeInTheDocument()
      expect(clickableButton).toHaveClass('cursor-pointer')
    })

    it('navigates to chapter page when popup is clicked', () => {
      const { getAllByTestId } = render(<ChapterMap {...defaultProps} />)

      const popups = getAllByTestId('popup')
      const clickableButton = popups[0].querySelector('button')
      fireEvent.click(clickableButton)

      expect(mockPush).toHaveBeenCalledWith('/chapters/new-york')
    })
  })

  describe('Keyboard Accessibility', () => {
    it('unlocks map with Enter key', async () => {
      const { getByText, queryByText } = render(<ChapterMap {...defaultProps} />)

      const unlockButton = getByText('Unlock map').closest('button')
      fireEvent.keyDown(unlockButton, { key: 'Enter' })

      expect(queryByText('Unlock map')).not.toBeInTheDocument()

      await waitFor(() => {
        expect(mockMap.scrollWheelZoom.enable).toHaveBeenCalled()
      })
    })

    it('unlocks map with Space key', async () => {
      const { getByText, queryByText } = render(<ChapterMap {...defaultProps} />)

      const unlockButton = getByText('Unlock map').closest('button')
      fireEvent.keyDown(unlockButton, { key: ' ' })

      expect(queryByText('Unlock map')).not.toBeInTheDocument()

      await waitFor(() => {
        expect(mockMap.scrollWheelZoom.enable).toHaveBeenCalled()
      })
    })

    it('does not unlock map with other keys', () => {
      const { getByText } = render(<ChapterMap {...defaultProps} />)

      const unlockButton = getByText('Unlock map').closest('button')
      fireEvent.keyDown(unlockButton, { key: 'Tab' })

      expect(getByText('Unlock map')).toBeInTheDocument()
    })
  })

  describe('Edge Cases', () => {
    it('handles case when map is not ready yet', () => {
      mockMapInstance = null

      const { container, getByText } = render(<ChapterMap {...defaultProps} />)
      expect(container).toBeInTheDocument()

      fireEvent.click(getByText('Unlock map').closest('button'))

      expect(L.control.zoom).not.toHaveBeenCalled()
    })

    it('filters out chapters with invalid geolocation', () => {
      const dataWithInvalidChapter: Chapter[] = [
        {
          _geoloc: { lat: 40.7128, lng: -74.006 },
          key: 'valid-chapter',
          name: 'Valid Chapter',
        } as Chapter,
        {
          key: 'invalid-chapter',
          name: 'Invalid Chapter',
        } as Chapter,
      ]

      const { getAllByTestId } = render(
        <ChapterMap {...defaultProps} geoLocData={dataWithInvalidChapter} />
      )

      expect(getAllByTestId('marker')).toHaveLength(1)
    })
  })
})
