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

  test('renders organization cards with fallback values for missing optional fields', async () => {
    const mockDataWithMissingFields = {
      hits: [
        {
          objectID: 'org-no-optional',
          avatarUrl: 'https://avatars.githubusercontent.com/u/999999?v=4',
          collaboratorsCount: 10,
          company: null,
          createdAt: 1596744799,
          description: 'Organization without optional fields',
          email: null,
          followersCount: 100,
          location: null,
          login: 'no-optional-org',
          name: 'No Optional Fields Org',
          publicRepositoriesCount: 50,
          updatedAt: 1727390473,
          url: 'https://github.com/no-optional-org',
        },
        {
          objectID: 'org-empty-strings',
          avatarUrl: 'https://avatars.githubusercontent.com/u/888888?v=4',
          collaboratorsCount: 20,
          company: '',
          createdAt: 1596744799,
          description: 'Organization with empty strings',
          email: '',
          followersCount: 200,
          location: '',
          login: 'empty-strings-org',
          name: 'Empty Strings Org',
          publicRepositoriesCount: 100,
          updatedAt: 1727390473,
          url: 'https://github.com/empty-strings-org',
        },
      ],
      totalPages: 1,
    }
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue(mockDataWithMissingFields)

    render(<Organization />)

    await waitFor(() => {
      expect(screen.getByText('No Optional Fields Org')).toBeInTheDocument()
      expect(screen.getByText('Empty Strings Org')).toBeInTheDocument()
    })

    // The fallback for location should show @login
    expect(screen.getByText('@no-optional-org')).toBeInTheDocument()
    expect(screen.getByText('@empty-strings-org')).toBeInTheDocument()
  })

  test('renders organization card with null avatarUrl using fallback', async () => {
    const mockDataWithNullAvatar = {
      hits: [
        {
          objectID: 'org-null-avatar',
          avatarUrl: null,
          collaboratorsCount: 5,
          company: 'Test Company',
          createdAt: 1596744799,
          description: 'Organization with null avatar',
          email: 'test@example.com',
          followersCount: 50,
          location: 'Test Location',
          login: 'null-avatar-org',
          name: 'Null Avatar Org',
          publicRepositoriesCount: 25,
          updatedAt: 1727390473,
          url: 'https://github.com/null-avatar-org',
        },
      ],
      totalPages: 1,
    }
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue(mockDataWithNullAvatar)

    render(<Organization />)

    await waitFor(() => {
      expect(screen.getByText('Null Avatar Org')).toBeInTheDocument()
      // Verify fallback is shown by confirming the actual image is NOT shown
      expect(screen.queryByAltText("Null Avatar Org's profile picture")).not.toBeInTheDocument()
    })
  })
})
