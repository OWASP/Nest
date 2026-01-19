import { useQuery } from '@apollo/client/react'
import { mockCommitteeDetailsData } from '@mockData/mockCommitteeDetailsData'
import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import CommitteeDetailsPage from 'app/committees/[committeeKey]/page'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(() => ({ push: jest.fn() })),
  useParams: () => ({ committeeKey: 'test-committee' }),
  usePathname: jest.fn(() => '/committees/test-committee'),
}))

describe('CommitteeDetailsPage Accessibility', () => {
  const mockUseQuery = useQuery as unknown as jest.Mock

  it('should have no accessibility violations', async () => {
    mockUseQuery.mockReturnValue({
      data: mockCommitteeDetailsData,
      loading: false,
      error: null,
    })

    const { container } = render(<CommitteeDetailsPage />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should have no accessibility violations when loading', async () => {
    mockUseQuery.mockReturnValue({
      data: null,
      loading: true,
      error: null,
    })

    const { container } = render(<CommitteeDetailsPage />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have no accessibility violations when error occurs', async () => {
    mockUseQuery.mockReturnValue({
      data: null,
      loading: false,
      error: new Error('test error'),
    })

    const { container } = render(<CommitteeDetailsPage />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have no accessibility violations when no data exists', async () => {
    mockUseQuery.mockReturnValue({
      data: null,
      loading: false,
      error: null,
    })

    const { container } = render(<CommitteeDetailsPage />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
