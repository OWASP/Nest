import { useQuery } from '@apollo/client/react'
import { mockCommunityGraphQLData } from '@mockData/mockCommunityData'
import { screen, waitFor } from '@testing-library/react'
import { axe } from 'jest-axe'
import { render } from 'wrappers/testUtil'
import CommunityPage from 'app/community/page'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(() => ({
    push: jest.fn(),
  })),
}))

describe('Community Page Accessibility', () => {
  afterAll(() => {
    jest.clearAllMocks()
  })

  it('should have no accessibility violations', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockCommunityGraphQLData,
      loading: false,
      error: null,
    })

    const { container } = render(<CommunityPage />)

    await waitFor(() => {
      expect(screen.getByText('OWASP Community')).toBeInTheDocument()
    })

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
