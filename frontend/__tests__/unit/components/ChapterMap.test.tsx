import { render, fireEvent } from '@testing-library/react'
import * as L from 'leaflet'
import { Chapter } from 'types/chapter'
import ChapterMap from 'components/ChapterMap'

const mockMap = {
  setView: jest.fn().mockReturnThis(),
  addLayer: jest.fn().mockReturnThis(),
  fitBounds: jest.fn().mockReturnThis(),
  on: jest.fn().mockReturnThis(),
  getCenter: jest.fn(() => ({ lat: 20, lng: 0 })),
  getZoom: jest.fn(() => 2),
  getContainer: jest.fn(() => document.getElementById('chapter-map')),
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
  scrollWheelZoom: {
    enable: jest.fn(),
    disable: jest.fn(),
  },
  boxZoom: {
    enable: jest.fn(),
    disable: jest.fn(),
  },
  keyboard: {
    enable: jest.fn(),
    disable: jest.fn(),
  },
}

const mockMarker = {
  bindPopup: jest.fn().mockReturnThis(),
}

const mockPopup = {
  setContent: jest.fn().mockReturnThis(),
}

const mockMarkerClusterGroup = {
  addLayers: jest.fn(),
  clearLayers: jest.fn(),
}

const mockTileLayer = {
  addTo: jest.fn().mockReturnThis(),
}

const mockLatLngBounds = {}

const mockIcon = {}

const mockZoomControl = {
  addTo: jest.fn().mockReturnThis(),
  remove: jest.fn(),
}

jest.mock('leaflet', () => ({
  map: jest.fn(() => mockMap),
  marker: jest.fn(() => mockMarker),
  popup: jest.fn(() => mockPopup),
  markerClusterGroup: jest.fn(() => mockMarkerClusterGroup),
  tileLayer: jest.fn(() => mockTileLayer),
  latLngBounds: jest.fn(() => mockLatLngBounds),
  // eslint-disable-next-line @typescript-eslint/naming-convention
  Icon: jest.fn(() => mockIcon),
  control: {
    zoom: jest.fn(() => mockZoomControl),
  },
}))

jest.mock('leaflet/dist/leaflet.css', () => ({}))
jest.mock('leaflet.markercluster/dist/MarkerCluster.css', () => ({}))
jest.mock('leaflet.markercluster/dist/MarkerCluster.Default.css', () => ({}))
jest.mock('leaflet.markercluster', () => ({}))

describe('ChapterMap', () => {
  const mockChapterData: Chapter[] = [
    {
      _geoloc: { lat: 40.7128, lng: -74.006 },
      createdAt: 1640995200000,
      geoLocation: { lat: 40.7128, lng: -74.006 },
      isActive: true,
      key: 'new-york',
      leaders: ['John Doe'],
      name: 'New York Chapter',
      objectID: 'ny-1',
      region: 'North America',
      relatedUrls: ['https://example.com'],
      suggestedLocation: 'New York, NY',
      summary: 'NYC OWASP Chapter',
      topContributors: [],
      updatedAt: 1640995200000,
      url: 'https://owasp.org/www-chapter-new-york/',
    },
    {
      _geoloc: { lat: 51.5074, lng: -0.1278 },
      createdAt: 1640995200000,
      geoLocation: { lat: 51.5074, lng: -0.1278 },
      isActive: true,
      key: 'london',
      leaders: ['Jane Smith'],
      name: 'London Chapter',
      objectID: 'london-1',
      region: 'Europe',
      relatedUrls: ['https://example.com'],
      suggestedLocation: 'London, UK',
      summary: 'London OWASP Chapter',
      topContributors: [],
      updatedAt: 1640995200000,
      url: 'https://owasp.org/www-chapter-london/',
    },
  ]

  const defaultProps = {
    geoLocData: mockChapterData,
    showLocal: false,
    style: { width: '100%', height: '400px' },
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('rendering', () => {
    it('renders the map container with correct id and style', () => {
      const { container } = render(<ChapterMap {...defaultProps} />)

      const mapContainer = document.getElementById('chapter-map')
      expect(mapContainer).toBeInTheDocument()
      expect(mapContainer).toHaveAttribute('id', 'chapter-map')
      expect(mapContainer).toHaveClass('h-full', 'w-full')

      // Check that the parent container has the correct styles applied
      const parentContainer = container.firstChild as HTMLElement
      expect(parentContainer).toHaveClass('relative')
    })

    it('renders with empty data without crashing', () => {
      render(<ChapterMap {...defaultProps} geoLocData={[]} />)

      const mapContainer = document.getElementById('chapter-map')
      expect(mapContainer).toBeInTheDocument()
    })
  })

  describe('Map initialization', () => {
    it('initializes leaflet map with correct configuration', () => {
      render(<ChapterMap {...defaultProps} />)
      expect(L.map).toHaveBeenCalledWith('chapter-map', {
        worldCopyJump: false,
        maxBounds: [
          [-90, -180],
          [90, 180],
        ],
        maxBoundsViscosity: 1.0,
        scrollWheelZoom: false,
        zoomControl: false,
      })
      expect(mockMap.setView).toHaveBeenCalledWith([20, 0], 2)
    })

    it('adds tile layer to the map', () => {
      render(<ChapterMap {...defaultProps} />)
      expect(L.tileLayer).toHaveBeenCalledWith(
        'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        {
          attribution: '© OpenStreetMap contributors',
          className: 'map-tiles',
        }
      )
      expect(mockTileLayer.addTo).toHaveBeenCalledWith(mockMap)
    })

    it('disables all interaction handlers on initialization', () => {
      render(<ChapterMap {...defaultProps} />)
      expect(mockMap.dragging.disable).toHaveBeenCalled()
      expect(mockMap.touchZoom.disable).toHaveBeenCalled()
      expect(mockMap.doubleClickZoom.disable).toHaveBeenCalled()
      expect(mockMap.scrollWheelZoom.disable).toHaveBeenCalled()
      expect(mockMap.boxZoom.disable).toHaveBeenCalled()
      expect(mockMap.keyboard.disable).toHaveBeenCalled()
    })

    it('creates and adds marker cluster group', () => {
      render(<ChapterMap {...defaultProps} />)
      expect(L.markerClusterGroup).toHaveBeenCalled()
      expect(mockMap.addLayer).toHaveBeenCalledWith(mockMarkerClusterGroup)
    })
  })

  describe('Markers', () => {
    it('creates markers for each chapter', () => {
      render(<ChapterMap {...defaultProps} />)
      expect(L.marker).toHaveBeenCalledTimes(2)
      expect(L.marker).toHaveBeenCalledWith([40.7128, -74.006], { icon: mockIcon })
      expect(L.marker).toHaveBeenCalledWith([51.5074, -0.1278], { icon: mockIcon })
    })

    it('filters out virtual chapters when latitude longitude undefined', () => {
      const virtualChapterData: Chapter[] = [
        mockChapterData[0],
        {
          // A virtual chapter with no location data
          ...mockChapterData[1],
          _geoloc: undefined,
          geoLocation: undefined,
        },
      ]

      render(<ChapterMap {...defaultProps} geoLocData={virtualChapterData} />)
      expect(L.marker).toHaveBeenCalledTimes(1)
      expect(L.marker).not.toHaveBeenCalledWith([undefined, undefined], { icon: mockIcon })
    })

    it('filters out virtual chapters when latitude longitude null', () => {
      const virtualChapterData: Chapter[] = [
        mockChapterData[0],
        {
          // A virtual chapter with no location data
          ...mockChapterData[1],
          _geoloc: null,
          geoLocation: null,
        },
      ]

      render(<ChapterMap {...defaultProps} geoLocData={virtualChapterData} />)
      expect(L.marker).toHaveBeenCalledTimes(1)
      expect(L.marker).not.toHaveBeenCalledWith([null, null], { icon: mockIcon })
    })

    it('creates marker icons with correct configuration', () => {
      render(<ChapterMap {...defaultProps} />)
      expect(L.Icon).toHaveBeenCalledWith({
        iconAnchor: [12, 41],
        iconRetinaUrl: '/img/marker-icon-2x.png',
        iconSize: [25, 41],
        iconUrl: '/img/marker-icon.png',
        popupAnchor: [1, -34],
        shadowSize: [41, 41],
        shadowUrl: '/img/marker-shadow.png',
      })
    })

    it('adds markers to cluster group', () => {
      render(<ChapterMap {...defaultProps} />)
      expect(mockMarkerClusterGroup.addLayers).toHaveBeenCalledWith([mockMarker, mockMarker])
    })

    it('handles chapters with missing _geoloc but present geolocation', () => {
      const chapterWithoutGeoloc: Chapter[] = [
        {
          ...mockChapterData[0],
          _geoloc: undefined,
          geoLocation: { lat: 35.6762, lng: 139.6503 },
        },
      ]

      render(<ChapterMap {...defaultProps} geoLocData={chapterWithoutGeoloc} />)
      expect(L.marker).toHaveBeenCalledWith([35.6762, 139.6503], { icon: mockIcon })
    })

    it('handles chapters with 0 coordinates correctly', () => {
      const chapterWithZeroCoords: Chapter[] = [
        {
          ...mockChapterData[0],
          _geoloc: { lat: 0, lng: 0 },
          geoLocation: { lat: 0, lng: 0 },
        },
      ]

      render(<ChapterMap {...defaultProps} geoLocData={chapterWithZeroCoords} />)
      expect(L.marker).toHaveBeenCalledTimes(1)
      expect(L.marker).toHaveBeenCalledWith([0, 0], { icon: mockIcon })
    })
  })

  describe('Popups', () => {
    it('creates popups for each marker', () => {
      render(<ChapterMap {...defaultProps} />)
      expect(L.popup).toHaveBeenCalledTimes(2)
      expect(mockMarker.bindPopup).toHaveBeenCalledTimes(2)
    })

    it('sets popup content with chapter name', () => {
      render(<ChapterMap {...defaultProps} />)
      expect(mockPopup.setContent).toHaveBeenCalledTimes(2)
    })

    it('navigates to chapter page when popup is clicked', () => {
      render(<ChapterMap {...defaultProps} />)
      expect(mockChapterData[0].key).toBe('new-york')
    })
  })

  describe('Interactive Overlay', () => {
    it('displays overlay with "Unlock map" message initially', () => {
      const { getByText } = render(<ChapterMap {...defaultProps} />)
      expect(getByText('Unlock map')).toBeInTheDocument()
    })

    it('removes overlay when unlock button is clicked', () => {
      const { getByText, queryByText } = render(<ChapterMap {...defaultProps} />)

      const button = getByText('Unlock map').closest('button')
      expect(button).not.toBeNull()
      fireEvent.click(button as HTMLElement)

      expect(queryByText('Unlock map')).not.toBeInTheDocument()
    })

    it('enables all interaction handlers when unlock button is clicked', () => {
      const { getByText } = render(<ChapterMap {...defaultProps} />)

      const button = getByText('Unlock map').closest('button')
      expect(button).not.toBeNull()
      fireEvent.click(button as HTMLElement)

      expect(mockMap.dragging.enable).toHaveBeenCalled()
      expect(mockMap.touchZoom.enable).toHaveBeenCalled()
      expect(mockMap.doubleClickZoom.enable).toHaveBeenCalled()
      expect(mockMap.scrollWheelZoom.enable).toHaveBeenCalled()
      expect(mockMap.boxZoom.enable).toHaveBeenCalled()
      expect(mockMap.keyboard.enable).toHaveBeenCalled()
    })

    it('has proper accessibility attributes', () => {
      const { getByText } = render(<ChapterMap {...defaultProps} />)

      const button = getByText('Unlock map').closest('button')
      expect(button).not.toBeNull()
      expect(button).toHaveAttribute('type', 'button')
      expect(button).toHaveAttribute('aria-label', 'Unlock map')
    })
  })

  describe('Local View', () => {
    it('sets local view when showLocal is true', () => {
      render(<ChapterMap {...defaultProps} showLocal={true} />)

      expect(mockMap.setView).toHaveBeenCalledWith([40.7128, -74.006], 7)
      expect(L.latLngBounds).toHaveBeenCalled()
      expect(mockMap.fitBounds).toHaveBeenCalledWith(mockLatLngBounds, { maxZoom: 7 })
    })

    it('does not set local view when showLocal is false', () => {
      render(<ChapterMap {...defaultProps} showLocal={false} />)

      expect(mockMap.setView).toHaveBeenCalledWith([20, 0], 2)
      expect(mockMap.fitBounds).not.toHaveBeenCalled()
    })

    it('handles showLocal with empty data', () => {
      render(<ChapterMap {...defaultProps} geoLocData={[]} showLocal={true} />)

      expect(mockMap.setView).toHaveBeenCalledWith([20, 0], 2)
      expect(mockMap.fitBounds).not.toHaveBeenCalled()
    })
  })

  describe('Component Updates', () => {
    it('clears existing markers when data changes', () => {
      const { rerender } = render(<ChapterMap {...defaultProps} />)

      const newData = [mockChapterData[0]]
      rerender(<ChapterMap {...defaultProps} geoLocData={newData} />)
      expect(mockMarkerClusterGroup.clearLayers).toHaveBeenCalled()
    })

    it('updates local view when showLocal prop changes', () => {
      const { rerender } = render(<ChapterMap {...defaultProps} showLocal={false} />)
      const initialCallCount = mockMap.setView.mock.calls.length

      rerender(<ChapterMap {...defaultProps} showLocal={true} />)

      expect(mockMap.setView.mock.calls.length).toBeGreaterThan(initialCallCount)
    })
  })

  describe('Edge Cases', () => {
    it('handles chapters with null/undefined geolocation gracefully', () => {
      const chapterWithNullGeo: Chapter[] = [
        {
          ...mockChapterData[0],
          _geoloc: undefined,
          geoLocation: undefined,
        },
      ]
      render(<ChapterMap {...defaultProps} geoLocData={chapterWithNullGeo} />)
      expect(document.getElementById('chapter-map')).toBeInTheDocument()
    })

    it('applies custom styles correctly', () => {
      const customStyle = { width: '800px', height: '600px', border: '1px solid red' }

      const { container } = render(<ChapterMap {...defaultProps} style={customStyle} />)

      // Custom styles should be applied to the parent container
      const parentContainer = container.firstChild as HTMLElement
      expect(parentContainer).toHaveStyle('width: 800px; height: 600px; border: 1px solid red;')

      // Map container should have Tailwind classes
      const mapContainer = document.getElementById('chapter-map')
      expect(mapContainer).toHaveClass('h-full', 'w-full')
    })
  })

  describe('Accessibility', () => {
    it('provides accessible map container', () => {
      render(<ChapterMap {...defaultProps} />)

      const mapContainer = document.getElementById('chapter-map')
      expect(mapContainer).toBeInTheDocument()
      expect(mapContainer).toHaveAttribute('id', 'chapter-map')
    })
  })

  describe('Zoom Control Visibility', () => {
    beforeEach(() => {
      jest.clearAllMocks()
    })

    it('does not show zoom control initially', () => {
      render(<ChapterMap {...defaultProps} />)
      expect(L.map).toHaveBeenCalledWith(
        'chapter-map',
        expect.objectContaining({
          zoomControl: false,
        })
      )
    })

    it('shows zoom control when unlock button is clicked', () => {
      const { getByText } = render(<ChapterMap {...defaultProps} />)

      const button = getByText('Unlock map').closest('button')
      expect(button).not.toBeNull()
      fireEvent.click(button as HTMLElement)

      expect(L.control.zoom).toHaveBeenCalledWith({ position: 'topleft' })
      expect(mockZoomControl.addTo).toHaveBeenCalledWith(mockMap)
    })
  })

  describe('Share Location Button Visibility', () => {
    const mockOnShareLocation = jest.fn()

    it('does not show share location button initially when map is not active', () => {
      const { queryByLabelText } = render(
        <ChapterMap {...defaultProps} onShareLocation={mockOnShareLocation} />
      )

      expect(queryByLabelText(/share location/i)).not.toBeInTheDocument()
    })

    it('shows share location button when map becomes active', () => {
      const { getByText, getByLabelText } = render(
        <ChapterMap {...defaultProps} onShareLocation={mockOnShareLocation} />
      )

      expect(getByText('Unlock map')).toBeInTheDocument()

      const overlay = getByText('Unlock map').closest('button')
      expect(overlay).not.toBeNull()
      fireEvent.click(overlay as HTMLElement)

      expect(getByLabelText(/share location to find nearby chapters/i)).toBeInTheDocument()
    })

    it('does not render share location button when onShareLocation is not provided', () => {
      const { getByText, queryByLabelText } = render(<ChapterMap {...defaultProps} />)

      const overlay = getByText('Unlock map').closest('button')
      expect(overlay).not.toBeNull()
      fireEvent.click(overlay as HTMLElement)

      expect(queryByLabelText(/share location/i)).not.toBeInTheDocument()
    })
  })

  describe('Escape Key Re-lock', () => {
    it('re-locks the map when Escape key is pressed', () => {
      const { getByText, queryByText } = render(<ChapterMap {...defaultProps} />)

      // First unlock the map
      const unlockButton = getByText('Unlock map').closest('button')
      expect(unlockButton).not.toBeNull()
      fireEvent.click(unlockButton as HTMLElement)

      // Verify map is unlocked
      expect(queryByText('Unlock map')).not.toBeInTheDocument()
      expect(mockMap.dragging.enable).toHaveBeenCalled()

      // Press Escape to re-lock
      globalThis.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))

      // Verify map is locked again
      expect(getByText('Unlock map')).toBeInTheDocument()
      expect(mockMap.dragging.disable).toHaveBeenCalled()
      expect(mockMap.scrollWheelZoom.disable).toHaveBeenCalled()
    })

    it('does nothing when Escape is pressed and map is already locked', () => {
      const { getByText } = render(<ChapterMap {...defaultProps} />)

      const disableCallsBefore = mockMap.dragging.disable.mock.calls.length

      // Press Escape while map is locked
      globalThis.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))

      // Should still show unlock button
      expect(getByText('Unlock map')).toBeInTheDocument()

      // Disable should not be called again
      expect(mockMap.dragging.disable.mock.calls.length).toBe(disableCallsBefore)
    })

    it('removes zoom control when Escape re-locks the map', () => {
      const { getByText } = render(<ChapterMap {...defaultProps} />)

      // Unlock the map
      const unlockButton = getByText('Unlock map')
      fireEvent.click(unlockButton)

      // Zoom control should be added
      expect(mockZoomControl.addTo).toHaveBeenCalled()

      // Press Escape to re-lock
      globalThis.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))

      // Zoom control should be removed
      expect(mockZoomControl.remove).toHaveBeenCalled()
    })

    it('cleans up Escape key listener on unmount', () => {
      const addEventListenerSpy = jest.spyOn(globalThis, 'addEventListener')
      const removeEventListenerSpy = jest.spyOn(globalThis, 'removeEventListener')

      const { unmount } = render(<ChapterMap {...defaultProps} />)

      // Find the Escape key handler that was registered
      const escapeHandler = addEventListenerSpy.mock.calls.find(
        ([event]) => event === 'keydown'
      )?.[1]

      unmount()

      expect(removeEventListenerSpy).toHaveBeenCalledWith('keydown', escapeHandler)

      addEventListenerSpy.mockRestore()
      removeEventListenerSpy.mockRestore()
    })
  })

  describe('Pointer Events Structure', () => {
    it('overlay wrapper has pointer-events-none class', () => {
      const { container } = render(<ChapterMap {...defaultProps} />)

      const overlay = container.querySelector('.pointer-events-none')
      expect(overlay).toBeInTheDocument()
      expect(overlay).toHaveClass('absolute', 'inset-0', 'z-[500]')
    })

    it('unlock button has pointer-events-auto class', () => {
      const { getByText } = render(<ChapterMap {...defaultProps} />)

      const button = getByText('Unlock map').closest('button')
      expect(button).not.toBeNull()
      expect(button).toHaveClass('pointer-events-auto')
    })
  })
})
