import { useQuery } from '@apollo/client/react'
import { mockUserDetailsData } from '@mockData/mockUserDetails'
import { waitFor, screen } from '@testing-library/react'
import { axe } from 'jest-axe'
import { render } from 'wrappers/testUtil'
import UserDetailsPage from 'app/members/[memberKey]/page'

jest.mock('@apollo/client/react', () => ({
  useQuery: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(() => ({ push: jest.fn() })),
  useParams: jest.fn(() => ({ memberKey: 'test-user' })),
}))

jest.mock('components/Badges', () => {
  const MockBadges = ({
    name,
    cssClass,
    showTooltip,
  }: {
    name: string
    cssClass: string
    showTooltip?: boolean
  }) => (
    <div
      data-testid={`badge-${name.toLowerCase().replaceAll(/\s+/g, '-')}`}
      data-css-class={cssClass}
      data-show-tooltip={showTooltip}
    >
      <span data-testid={`icon-${cssClass.replace('fa-', '')}`} />
    </div>
  )
  MockBadges.displayName = 'MockBadges'
  return {
    __esModule: true,
    default: MockBadges,
  }
})

jest.mock('utils/helpers/githubHeatmap', () => ({
  fetchHeatmapData: jest.fn(),
  drawContributions: jest.fn(() => {}),
}))

describe('UserDetailsPage Accessibility', () => {
  it('should have no accessibility violations', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      loading: false,
      error: null,
    })

    const { container } = render(<UserDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Test User')).toBeInTheDocument()
    })

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
