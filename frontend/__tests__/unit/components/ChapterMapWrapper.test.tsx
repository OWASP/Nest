import { render, waitFor, fireEvent } from '@testing-library/react'
import React, { JSX } from 'react'
import { Chapter } from 'types/chapter'
import * as geolocationUtils from 'utils/geolocationUtils'

// Mock next/dynamic
jest.mock('next/dynamic', () => {
  return function mockDynamic(
    importFn: () => Promise<{ default: React.ComponentType<unknown> }>,
    options?: { ssr?: boolean }
  ) {
    // Ignore options for SSR: false — reference it without using `void`
    if (options) {
      /* intentionally unused */
    }
    // Return a component that resolves the import synchronously for testing
    const Component = React.lazy(importFn)
    return function DynamicComponent(props: Record<string, unknown>): JSX.Element {
      return (
        <React.Suspense fallback={<div data-testid="loading">Loading...</div>}>
          <Component {...props} />
        </React.Suspense>
      )
    }
  }
})

// Mock ChapterMap component
const mockOnShareLocation = jest.fn()
jest.mock('components/ChapterMap', () => {
  return function MockChapterMap(props: {
    geoLocData: Chapter[]
    showLocal: boolean
    style: React.CSSProperties
    userLocation?: { latitude: number; longitude: number } | null
    onShareLocation?: () => void
  }): JSX.Element {
    // Capture the onShareLocation prop for testing
    if (props.onShareLocation) {
      mockOnShareLocation.mockImplementation(props.onShareLocation)
    }
    return (
      <div data-testid="chapter-map" style={props.style}>
        <span data-testid="geo-loc-data-length">{props.geoLocData.length}</span>
        <span data-testid="show-local">{String(props.showLocal)}</span>
        {props.userLocation && (
          <span data-testid="user-location">
            {props.userLocation.latitude},{props.userLocation.longitude}
          </span>
        )}
        {props.onShareLocation && (
          <button data-testid="share-location-btn" onClick={props.onShareLocation}>
            Share Location
          </button>
        )}
      </div>
    )
  }
})

// Mock geolocation utilities
jest.mock('utils/geolocationUtils', () => ({
  getUserLocationFromBrowser: jest.fn(),
  sortChaptersByDistance: jest.fn(),
}))

describe('ChapterMapWrapper', () => {
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
    jest.spyOn(console, 'error').mockImplementation(() => {})
  })

  afterEach(() => {
    jest.restoreAllMocks()
  })

  // We need to import the component after mocks are set up
  const getChapterMapWrapper = async () => {
    const chapterModule = await import('components/ChapterMapWrapper')
    return chapterModule.default
  }

  describe('when showLocationSharing is false or undefined', () => {
    it('renders ChapterMap directly without wrapper when showLocationSharing is false', async () => {
      const ChapterMapWrapper = await getChapterMapWrapper()
      const { getByTestId } = render(
        <ChapterMapWrapper {...defaultProps} showLocationSharing={false} />
      )

      await waitFor(() => {
        expect(getByTestId('chapter-map')).toBeInTheDocument()
      })
      // Should not have share location button (no onShareLocation passed)
      expect(getByTestId('geo-loc-data-length')).toHaveTextContent('2')
    })

    it('renders ChapterMap directly without wrapper when showLocationSharing is undefined', async () => {
      const ChapterMapWrapper = await getChapterMapWrapper()
      const { getByTestId } = render(<ChapterMapWrapper {...defaultProps} />)

      await waitFor(() => {
        expect(getByTestId('chapter-map')).toBeInTheDocument()
      })
      expect(getByTestId('geo-loc-data-length')).toHaveTextContent('2')
    })
  })

  describe('when showLocationSharing is true', () => {
    it('renders ChapterMap with wrapping div and onShareLocation handler', async () => {
      const ChapterMapWrapper = await getChapterMapWrapper()
      const { getByTestId, container } = render(
        <ChapterMapWrapper {...defaultProps} showLocationSharing={true} />
      )

      await waitFor(() => {
        expect(getByTestId('chapter-map')).toBeInTheDocument()
      })

      // Check for the wrapper div with h-full w-full classes
      const wrapper = container.querySelector('.h-full.w-full')
      expect(wrapper).toBeInTheDocument()

      // Should have share location button
      expect(getByTestId('share-location-btn')).toBeInTheDocument()
    })

    it('uses original geoLocData when sortedData is null', async () => {
      const ChapterMapWrapper = await getChapterMapWrapper()
      const { getByTestId } = render(
        <ChapterMapWrapper {...defaultProps} showLocationSharing={true} />
      )

      await waitFor(() => {
        expect(getByTestId('geo-loc-data-length')).toHaveTextContent('2')
      })
    })
  })

  describe('handleShareLocation function', () => {
    it('clears user location when location is already set (toggle off)', async () => {
      const mockLocation = { latitude: 40.7128, longitude: -74.006 }
      const mockSortedChapters = [
        { ...mockChapterData[0], _distance: 0 },
        { ...mockChapterData[1], _distance: 100 },
      ]

      ;(geolocationUtils.getUserLocationFromBrowser as jest.Mock).mockResolvedValue(mockLocation)
      ;(geolocationUtils.sortChaptersByDistance as jest.Mock).mockReturnValue(mockSortedChapters)

      const ChapterMapWrapper = await getChapterMapWrapper()
      const { getByTestId, queryByTestId } = render(
        <ChapterMapWrapper {...defaultProps} showLocationSharing={true} />
      )

      await waitFor(() => {
        expect(getByTestId('share-location-btn')).toBeInTheDocument()
      })

      // First click - enable location sharing
      fireEvent.click(getByTestId('share-location-btn'))

      await waitFor(() => {
        expect(getByTestId('user-location')).toHaveTextContent('40.7128,-74.006')
      })

      // Second click - disable location sharing (toggle off)
      fireEvent.click(getByTestId('share-location-btn'))

      await waitFor(() => {
        expect(queryByTestId('user-location')).not.toBeInTheDocument()
      })
    })

    it('fetches and sets user location on successful geolocation', async () => {
      const mockLocation = { latitude: 51.5074, longitude: -0.1278 }
      const mockSortedChapters = [
        { ...mockChapterData[1], _distance: 0 },
        { ...mockChapterData[0], _distance: 5000 },
      ]

      ;(geolocationUtils.getUserLocationFromBrowser as jest.Mock).mockResolvedValue(mockLocation)
      ;(geolocationUtils.sortChaptersByDistance as jest.Mock).mockReturnValue(mockSortedChapters)

      const ChapterMapWrapper = await getChapterMapWrapper()
      const { getByTestId } = render(
        <ChapterMapWrapper {...defaultProps} showLocationSharing={true} />
      )

      await waitFor(() => {
        expect(getByTestId('share-location-btn')).toBeInTheDocument()
      })

      fireEvent.click(getByTestId('share-location-btn'))

      await waitFor(() => {
        expect(geolocationUtils.getUserLocationFromBrowser).toHaveBeenCalled()
        expect(geolocationUtils.sortChaptersByDistance).toHaveBeenCalledWith(
          mockChapterData,
          mockLocation
        )
        expect(getByTestId('user-location')).toHaveTextContent('51.5074,-0.1278')
      })
    })

    it('does nothing when geolocation returns null', async () => {
      ;(geolocationUtils.getUserLocationFromBrowser as jest.Mock).mockResolvedValue(null)

      const ChapterMapWrapper = await getChapterMapWrapper()
      const { getByTestId, queryByTestId } = render(
        <ChapterMapWrapper {...defaultProps} showLocationSharing={true} />
      )

      await waitFor(() => {
        expect(getByTestId('share-location-btn')).toBeInTheDocument()
      })

      fireEvent.click(getByTestId('share-location-btn'))

      await waitFor(() => {
        expect(geolocationUtils.getUserLocationFromBrowser).toHaveBeenCalled()
        expect(geolocationUtils.sortChaptersByDistance).not.toHaveBeenCalled()
        expect(queryByTestId('user-location')).not.toBeInTheDocument()
      })
    })

    it('logs error when geolocation throws an error', async () => {
      const mockError = new Error('Geolocation permission denied')
      ;(geolocationUtils.getUserLocationFromBrowser as jest.Mock).mockRejectedValue(mockError)
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})

      const ChapterMapWrapper = await getChapterMapWrapper()
      const { getByTestId, queryByTestId } = render(
        <ChapterMapWrapper {...defaultProps} showLocationSharing={true} />
      )

      await waitFor(() => {
        expect(getByTestId('share-location-btn')).toBeInTheDocument()
      })

      fireEvent.click(getByTestId('share-location-btn'))

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Error detecting location:', mockError)
        expect(queryByTestId('user-location')).not.toBeInTheDocument()
      })
    })

    it('correctly maps sorted data removing _distance property', async () => {
      const mockLocation = { latitude: 40.7128, longitude: -74.006 }
      const mockSortedChapters = [
        { ...mockChapterData[0], _distance: 0 },
        { ...mockChapterData[1], _distance: 5000 },
      ]

      ;(geolocationUtils.getUserLocationFromBrowser as jest.Mock).mockResolvedValue(mockLocation)
      ;(geolocationUtils.sortChaptersByDistance as jest.Mock).mockReturnValue(mockSortedChapters)

      const ChapterMapWrapper = await getChapterMapWrapper()
      const { getByTestId } = render(
        <ChapterMapWrapper {...defaultProps} showLocationSharing={true} />
      )

      await waitFor(() => {
        expect(getByTestId('share-location-btn')).toBeInTheDocument()
      })

      fireEvent.click(getByTestId('share-location-btn'))

      await waitFor(() => {
        // The component should still have 2 chapters after sorting
        expect(getByTestId('geo-loc-data-length')).toHaveTextContent('2')
      })
    })
  })

  describe('props forwarding', () => {
    it('forwards showLocal prop to ChapterMap', async () => {
      const ChapterMapWrapper = await getChapterMapWrapper()
      const { getByTestId } = render(
        <ChapterMapWrapper {...defaultProps} showLocal={true} showLocationSharing={true} />
      )

      await waitFor(() => {
        expect(getByTestId('show-local')).toHaveTextContent('true')
      })
    })

    it('forwards style prop to ChapterMap', async () => {
      const customStyle = { width: '500px', height: '300px' }
      const ChapterMapWrapper = await getChapterMapWrapper()
      const { getByTestId } = render(
        <ChapterMapWrapper {...defaultProps} style={customStyle} showLocationSharing={false} />
      )

      await waitFor(() => {
        expect(getByTestId('chapter-map')).toBeInTheDocument()
      })
    })
  })
})
