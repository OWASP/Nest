import { useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { screen, waitFor } from '@testing-library/react'
import { render } from 'wrappers/testUtil'
import SponsorsPage from 'app/sponsors/page'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

const mockSponsors = [
  {
    id: 'sponsor-1',
    name: 'Diamond Corp',
    description: 'A leading security firm',
    imageUrl: 'https://example.com/diamond.png',
    url: 'https://diamondcorp.com',
    sponsorType: 'Diamond',
  },
  {
    id: 'sponsor-2',
    name: 'Platinum Inc',
    description: '',
    imageUrl: '',
    url: '',
    sponsorType: 'Platinum',
  },
  {
    id: 'sponsor-3',
    name: 'Gold Ltd',
    description: 'Gold level sponsor description',
    imageUrl: '',
    url: 'https://goldltd.com',
    sponsorType: 'Gold',
  },
  {
    id: 'sponsor-4',
    name: 'Supporter Co',
    description: '',
    imageUrl: '',
    url: '',
    sponsorType: 'Supporter',
  },
  {
    id: 'sponsor-5',
    name: 'Bronze Alliance',
    description: '',
    imageUrl: '',
    url: '',
    sponsorType: 'Bronze',
  },
  {
    id: 'sponsor-6',
    name: 'Excluded Corp',
    description: '',
    imageUrl: '',
    url: '',
    sponsorType: 'Not a Sponsor',
  },
]

describe('SponsorsPage', () => {
  const mockAddToast = addToast as jest.MockedFunction<typeof addToast>

  beforeEach(() => {
    jest.clearAllMocks()
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: { sponsors: mockSponsors },
      error: null,
      loading: false,
    })
  })

  test('renders loading spinner when loading is true', () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: null,
      error: null,
      loading: true,
    })
    render(<SponsorsPage />)
    expect(screen.getAllByAltText('Loading indicator').length).toBeGreaterThan(0)
  })

  test('shows "No Sponsors Yet" when sponsors list is empty', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: { sponsors: [] },
      error: null,
      loading: false,
    })
    render(<SponsorsPage />)
    await waitFor(() => {
      expect(screen.getByText('No Sponsors Yet')).toBeInTheDocument()
    })
    expect(screen.getByText('Be the first to support the OWASP Nest project!')).toBeInTheDocument()
  })

  test('shows "No Sponsors Yet" when data is null', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: null,
      error: null,
      loading: false,
    })
    render(<SponsorsPage />)
    await waitFor(() => {
      expect(screen.getByText('No Sponsors Yet')).toBeInTheDocument()
    })
  })

  test('calls addToast with danger color on GraphQL error', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: null,
      error: { message: 'GraphQL error' },
      loading: false,
    })
    render(<SponsorsPage />)
    await waitFor(() => {
      expect(mockAddToast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'GraphQL Request Failed',
          color: 'danger',
        })
      )
    })
  })

  test('renders error UI on GraphQL error instead of empty state', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: null,
      error: { message: 'GraphQL error' },
      loading: false,
    })
    render(<SponsorsPage />)
    await waitFor(() => {
      expect(screen.getByText('Unable to load sponsors')).toBeInTheDocument()
    })
    expect(screen.getByText(/Something went wrong while fetching sponsor data/)).toBeInTheDocument()
    expect(screen.queryByText('No Sponsors Yet')).not.toBeInTheDocument()
  })

  test('renders sponsor names when data is loaded', async () => {
    render(<SponsorsPage />)
    await waitFor(() => {
      expect(screen.getByText('Diamond Corp')).toBeInTheDocument()
    })
    expect(screen.getByText('Platinum Inc')).toBeInTheDocument()
    expect(screen.getByText('Gold Ltd')).toBeInTheDocument()
    expect(screen.getByText('Supporter Co')).toBeInTheDocument()
  })

  test('renders sponsor description when present', async () => {
    render(<SponsorsPage />)
    await waitFor(() => {
      expect(screen.getByText('A leading security firm')).toBeInTheDocument()
    })
    expect(screen.getByText('Gold level sponsor description')).toBeInTheDocument()
  })

  test('renders sponsor image when imageUrl is provided', async () => {
    render(<SponsorsPage />)
    await waitFor(() => {
      const image = screen.getByAltText('Diamond Corp logo')
      expect(image).toHaveAttribute('src', 'https://example.com/diamond.png')
    })
  })

  test('renders "Visit website" link when sponsor url is provided', async () => {
    render(<SponsorsPage />)
    await waitFor(() => {
      const visitLinks = screen.getAllByText('Visit website')
      expect(visitLinks.length).toBeGreaterThan(0)
    })
  })

  test('does not render "Visit website" when sponsor url is empty', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: {
        sponsors: [
          {
            id: 'no-url-sponsor',
            name: 'No URL Sponsor',
            description: '',
            imageUrl: '',
            url: '',
            sponsorType: 'Gold',
          },
        ],
      },
      error: null,
      loading: false,
    })
    render(<SponsorsPage />)
    await waitFor(() => {
      expect(screen.getByText('No URL Sponsor')).toBeInTheDocument()
    })
    expect(screen.queryByText('Visit website')).not.toBeInTheDocument()
  })

  test('puts sponsors with unknown tier into "Other" group', async () => {
    render(<SponsorsPage />)
    await waitFor(() => {
      expect(screen.getByText('Other Sponsors')).toBeInTheDocument()
    })
    expect(screen.getByText('Bronze Alliance')).toBeInTheDocument()
  })

  test('excludes sponsors with "Not a Sponsor" type', async () => {
    render(<SponsorsPage />)
    await waitFor(() => {
      expect(screen.getByText('Diamond Corp')).toBeInTheDocument()
    })
    expect(screen.queryByText('Excluded Corp')).not.toBeInTheDocument()
  })

  test('renders tier group badge counts', async () => {
    render(<SponsorsPage />)
    await waitFor(() => {
      expect(screen.getByText('Diamond Sponsors')).toBeInTheDocument()
    })
    expect(screen.getByText('Gold Sponsors')).toBeInTheDocument()
  })

  test('renders "Become a Sponsor" section with apply and donate links', async () => {
    render(<SponsorsPage />)
    await waitFor(() => {
      expect(screen.getByText('Apply to Sponsor')).toBeInTheDocument()
    })
    expect(screen.getByText('Donate via OWASP')).toBeInTheDocument()
  })

  test('renders "Become a Sponsor" link in empty state', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: { sponsors: [] },
      error: null,
      loading: false,
    })
    render(<SponsorsPage />)
    await waitFor(() => {
      expect(screen.getAllByText('Become a Sponsor').length).toBeGreaterThan(0)
    })
  })

  test('uses fallback style for unrecognised sponsorType', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: {
        sponsors: [
          {
            id: 'unknown-tier',
            name: 'Unrecognised Corp',
            description: '',
            imageUrl: '',
            url: '',
            sponsorType: 'Obscure',
          },
        ],
      },
      error: null,
      loading: false,
    })
    render(<SponsorsPage />)
    await waitFor(() => {
      expect(screen.getByText('Unrecognised Corp')).toBeInTheDocument()
    })
    expect(screen.getByText('Other Sponsors')).toBeInTheDocument()
  })

  test('renders sponsor sponsor type badge', async () => {
    render(<SponsorsPage />)
    await waitFor(() => {
      expect(screen.getByText('Diamond')).toBeInTheDocument()
    })
  })
})
