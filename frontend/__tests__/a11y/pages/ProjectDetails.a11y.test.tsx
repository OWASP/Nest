import { useQuery } from '@apollo/client/react'
import { mockProjectDetailsData } from '@mockData/mockProjectDetailsData'
import { waitFor, screen } from '@testing-library/react'
import { axe } from 'jest-axe'
import { render } from 'wrappers/testUtil'
import ProjectDetailsPage from 'app/projects/[projectKey]/page'

jest.mock('next/navigation', () => ({
  useParams: jest.fn(() => ({ projectKey: 'test-project' })),
  useRouter: jest.fn(() => ({ push: jest.fn() })),
}))

jest.mock('@apollo/client/react', () => ({
  useQuery: jest.fn(),
  useMutation: jest.fn(() => [jest.fn()]),
}))

jest.mock('react-apexcharts', () => {
  return {
    __esModule: true,
    default: () => {
      return <div data-testid="mock-apexcharts">Mock ApexChart</div>
    },
  }
})

describe('ProjectDetailsPage Accessibility', () => {
  it('should have no accessibility violations', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockProjectDetailsData,
      loading: false,
      error: null,
    })

    const { container } = render(<ProjectDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument()
    })

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
