import { screen, waitFor } from '@testing-library/react'

import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { CommitteeDetailsPage } from 'pages'
import { render } from 'wrappers/testUtil'

import { mockCommitteeData } from '@tests/data/mockCommitteeData'

jest.mock('api/fetchAlgoliaData', () => ({
  fetchAlgoliaData: jest.fn(),
}))
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: jest.fn(),
}))
jest.mock('components/Pagination', () =>
  jest.fn(({ currentPage, onPageChange, totalPages }) =>
    totalPages > 1 ? (
      <div>
        <button onClick={() => onPageChange(currentPage + 1)}>Next Page</button>
      </div>
    ) : null
  )
)

describe('Committees Component', () => {
  beforeEach(() => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: mockCommitteeData.committees,
      totalPages: 2,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders skeleton initially', async () => {
    render(<CommitteeDetailsPage />)
    await waitFor(() => {
      const skeletonLoaders = screen.getAllByTestId('skeleton-loader')
      expect(skeletonLoaders.length).toBeGreaterThan(0)
    })
  })

  test('renders committee data correctly', async () => {
    render(<CommitteeDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Committee 1')).toBeInTheDocument()
    })
    expect(screen.getByText('This is a summary of Committee 1.')).toBeInTheDocument()
    const viewButton = screen.getByText('Learn More')
    expect(viewButton).toBeInTheDocument()
  })

  test('displays "Committee not found" when there are no committees', async () => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: [],
      totalPages: 0,
    })
    render(<CommitteeDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Committee not found')).toBeInTheDocument()
    })
  })
})
