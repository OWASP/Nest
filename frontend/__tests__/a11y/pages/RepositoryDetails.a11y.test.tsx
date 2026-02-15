import { useQuery } from '@apollo/client/react'
import { mockRepositoryData } from '@mockData/mockRepositoryData'
import { waitFor, screen } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import { render } from 'wrappers/testUtil'
import RepositoryDetailsPage from 'app/organizations/[organizationKey]/repositories/[repositoryKey]/page'

jest.mock('@apollo/client/react', () => ({
  useQuery: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(() => ({ push: jest.fn() })),
  useParams: jest.fn(() => ({
    repositoryKey: 'test-repository',
    organizationKey: 'test-organization',
  })),
}))

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('RepositoryDetailsPage Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  it('should have no accessibility violations', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockRepositoryData,
      loading: false,
      error: null,
    })

    const { container } = render(<RepositoryDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Test Repo')).toBeInTheDocument()
    })

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
