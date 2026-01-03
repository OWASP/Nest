import { screen, fireEvent, render, waitFor } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { Chapter } from 'types/chapter'
import ChapterMap from 'components/ChapterMap'

expect.extend(toHaveNoViolations)

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
]

const defaultProps = {
  geoLocData: mockChapterData,
  showLocal: false,
  style: { width: '100%', height: '400px' },
}

describe('ChapterMap a11y', () => {
  it('should not have any accessibility violations in locked state', async () => {
    const { container } = render(<ChapterMap {...defaultProps} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when map is unlocked', async () => {
    const { container } = render(<ChapterMap {...defaultProps} onShareLocation={jest.fn()} />)

    const unlockButton = screen.getByLabelText('Unlock map')
    fireEvent.click(unlockButton)

    await waitFor(() => expect(screen.getByLabelText(/Share location/i)).toBeInTheDocument())

    const results = await axe(container)

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
