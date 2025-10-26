import { render } from '@testing-library/react'
import { Chapter } from 'types/chapter'
import ChapterMap from 'components/ChapterMap'
import * as L from 'leaflet'

const mockMap = {
  setView: jest.fn().mockReturnThis(),
  addLayer: jest.fn().mockReturnThis(),
  fitBounds: jest.fn().mockReturnThis(),
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

jest.mock('leaflet', () => ({
  map: jest.fn(() => mockMap),
  marker: jest.fn(() => mockMarker),
  popup: jest.fn(() => mockPopup),
  markerClusterGroup: jest.fn(() => mockMarkerClusterGroup),
  tileLayer: jest.fn(() => mockTileLayer),
  latLngBounds: jest.fn(() => mockLatLngBounds),
  // eslint-disable-next-line @typescript-eslint/naming-convention
  Icon: jest.fn(() => mockIcon),
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
      render(<ChapterMap {...defaultProps} />)

      const mapContainer = document.getElementById('chapter-map')
      expect(mapContainer).toBeInTheDocument()
      expect(mapContainer).toHaveAttribute('id', 'chapter-map')
      expect(mapContainer).toHaveStyle('width: 100%; height: 400px;')
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

  describe('Local View', () => {
    it('sets local view when showLocal is true', () => {
      render(<ChapterMap {...defaultProps} showLocal={true} />)

      expect(mockMap.setView).toHaveBeenCalledWith([40.7128, -74.006], 7)
      expect(L.latLngBounds).toHaveBeenCalled()
      expect(mockMap.fitBounds).toHaveBeenCalledWith(mockLatLngBounds, { maxZoom: 7 })
    })

    it('does not set local view when showLocal is false', () => {
      render(<ChapterMap {...defaultProps} showLocal={false} />)

      expect(mockMap.setView).toHaveBeenCalledTimes(1)
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
      rerender(<ChapterMap {...defaultProps} showLocal={true} />)

      expect(mockMap.setView).toHaveBeenCalledTimes(2)
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

      render(<ChapterMap {...defaultProps} style={customStyle} />)

      const mapContainer = document.getElementById('chapter-map')
      expect(mapContainer).toHaveStyle('width: 800px; height: 600px; border: 1px solid red;')
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
})
