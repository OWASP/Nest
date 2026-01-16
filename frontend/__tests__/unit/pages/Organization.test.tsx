import { mockOrganizationData } from '@mockData/mockOrganizationData'
import { fireEvent, screen, waitFor } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import { render } from 'wrappers/testUtil'
import Organization from 'app/organizations/page'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'

const mockRouter = {
  push: jest.fn(),
}

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(() => mockRouter),
  useParams: () => ({ organizationKey: 'test-org' }),
  useSearchParams: () => new URLSearchParams(),
}))

jest.mock('server/fetchAlgoliaData', () => ({
  fetchAlgoliaData: jest.fn(),
}))

jest.mock('components/Pagination', () =>
  jest.fn(({ currentPage, onPageChange }) => (
    <div>
      <button onClick={() => onPageChange(currentPage + 1)}>Next Page</button>
    </div>
  ))
)

describe('Organization', () => {
  let mockRouter: { push: jest.Mock }
  beforeEach(() => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: mockOrganizationData.hits,
      totalPages: 2,
    })
    mockRouter = { push: jest.fn() }
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders organization data correctly', async () => {
    render(<Organization />)

    await waitFor(() => {
      expect(screen.getByText('Test Organization')).toBeInTheDocument()
    })

    expect(screen.getByText('Another Organization')).toBeInTheDocument()
  })

  test('handles page change correctly', async () => {
    window.scrollTo = jest.fn()
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: mockOrganizationData.hits,
      totalPages: 2,
    })
    render(<Organization />)
    await waitFor(() => {
      const nextPageButton = screen.getByText('Next Page')
      fireEvent.click(nextPageButton)
    })
    expect(window.scrollTo).toHaveBeenCalledWith({
      top: 0,
      behavior: 'auto',
    })
  })

  test('navigates to organization details on View Details button click', async () => {
    render(<Organization />)

    await waitFor(() => {
      const viewDetailsButtons = screen.getAllByText('View Profile')
      expect(viewDetailsButtons[0]).toBeInTheDocument()
      fireEvent.click(viewDetailsButtons[0])
    })

    expect(mockRouter.push).toHaveBeenCalledWith('/organizations/test-org')

    jest.restoreAllMocks()
  })
})
