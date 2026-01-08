import { useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { screen, waitFor } from '@testing-library/react'
import { mockUserDetailsData } from '@unit/data/mockUserDetails'
import { render } from 'wrappers/testUtil'
import '@testing-library/jest-dom'
import UserDetailsPage from 'app/members/[memberKey]/page'
import { drawContributions, fetchHeatmapData } from 'utils/helpers/githubHeatmap'

// Mock Apollo Client
jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))

// Mock Badges component
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

const mockRouter = {
  push: jest.fn(),
}

const mockError = {
  error: new Error('GraphQL error'),
}

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(() => mockRouter),
  useParams: () => ({ memberKey: 'test-user' }),
}))

// Mock GitHub heatmap utilities
jest.mock('utils/helpers/githubHeatmap', () => ({
  fetchHeatmapData: jest.fn(),
  drawContributions: jest.fn(() => {}),
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

describe('UserDetailsPage', () => {
  beforeEach(() => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      loading: false,
      error: null,
    })
    ;(fetchHeatmapData as jest.Mock).mockResolvedValue({
      contributions: { years: [{ year: '2023' }] },
    })
    ;(drawContributions as jest.Mock).mockImplementation(() => {})
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  // Helper functions to reduce nesting depth
  const getBadgeElements = () => {
    return screen.getAllByTestId(/^badge-/)
  }

  const getBadgeTestIds = () => {
    const badgeElements = getBadgeElements()
    return badgeElements.map((element) => element.dataset.testid)
  }

  const expectBadgesInCorrectOrder = (expectedOrder: string[]) => {
    const badgeTestIds = getBadgeTestIds()
    expect(badgeTestIds).toEqual(expectedOrder)
  }

  test('renders loading state', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: null,
      loading: true,
      error: null,
    })

    render(<UserDetailsPage />)

    // Use semantic role query instead of CSS selectors for better stability
    await waitFor(() => {
      expect(screen.getByTestId('user-loading-skeleton')).toBeInTheDocument()
    })
  })

  test('renders user details', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: {
        ...mockUserDetailsData,
        user: { ...mockUserDetailsData.user, recentIssues: {} },
      },
      error: null,
      loading: false,
    })

    render(<UserDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Test User')).toBeInTheDocument()
    })

    expect(screen.getByText('Statistics')).toBeInTheDocument()
    expect(screen.getByText('Test Company')).toBeInTheDocument()
    expect(screen.getByText('Test Location')).toBeInTheDocument()
    expect(screen.getByText('10 Followers')).toBeInTheDocument()
    expect(screen.getByText('5 Followings')).toBeInTheDocument()
    expect(screen.getByText('3 Repositories')).toBeInTheDocument()
    expect(screen.getByText('100 Contributions')).toBeInTheDocument()
  })

  test('renders recent issues correctly', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      error: null,
      loading: false,
    })

    render(<UserDetailsPage />)

    await waitFor(() => {
      const recentIssuesTitle = screen.getByText('Recent Issues')
      expect(recentIssuesTitle).toBeInTheDocument()

      const issueTitle = screen.getByText('Test Issue')
      expect(issueTitle).toBeInTheDocument()

      const issueComments = screen.getByText('Test Repo')
      expect(issueComments).toBeInTheDocument()
    })
  })

  test('renders recent pull requests correctly', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      error: null,
      loading: false,
    })

    render(<UserDetailsPage />)

    await waitFor(() => {
      const pullRequestsTitle = screen.getByText('Recent Pull Requests')
      expect(pullRequestsTitle).toBeInTheDocument()

      const pullRequestTitle = screen.getByText('Test Pull Request')
      expect(pullRequestTitle).toBeInTheDocument()
    })
  })

  test('renders recent releases correctly', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      error: null,
      loading: false,
    })
    render(<UserDetailsPage />)
    await waitFor(() => {
      const releasesTitle = screen.getByText('Recent Releases')
      expect(releasesTitle).toBeInTheDocument()
      const releases = mockUserDetailsData.recentReleases
      for (const release of releases) {
        expect(screen.getByText(release.name)).toBeInTheDocument()
        expect(screen.getByText(release.repositoryName)).toBeInTheDocument()
      }
    })
  })

  test('renders recent milestones correctly', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      error: null,
      loading: false,
    })

    render(<UserDetailsPage />)

    await waitFor(() => {
      const milestonesTitle = screen.getByText('Recent Milestones')
      expect(milestonesTitle).toBeInTheDocument()
      const milestones = mockUserDetailsData.recentMilestones
      for (const milestone of milestones) {
        expect(screen.getByText(milestone.title)).toBeInTheDocument()
        expect(screen.getByText(milestone.repositoryName)).toBeInTheDocument()
        expect(screen.getByText(`${milestone.openIssuesCount} open`)).toBeInTheDocument()
        expect(screen.getByText(`${milestone.closedIssuesCount} closed`)).toBeInTheDocument()
      }
    })
  })

  test('renders repositories section correctly', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      error: null,
      loading: false,
    })

    render(<UserDetailsPage />)

    await waitFor(() => {
      const repositoriesTitle = screen.getByText('Repositories')
      expect(repositoriesTitle).toBeInTheDocument()

      const repositoryName = screen.getByText('Test Repo')
      expect(repositoryName).toBeInTheDocument()

      const starsCount = screen.getByText('10')
      expect(starsCount).toBeInTheDocument()

      const forksCount = screen.getByText('5')
      expect(forksCount).toBeInTheDocument()
    })
  })

  test('renders statistics section correctly', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      error: null,
      loading: false,
    })

    render(<UserDetailsPage />)

    await waitFor(() => {
      const statisticsTitle = screen.getByText('Statistics')
      expect(statisticsTitle).toBeInTheDocument()

      const followersCount = screen.getByText('10 Followers')
      expect(followersCount).toBeInTheDocument()

      const followingCount = screen.getByText('5 Followings')
      expect(followingCount).toBeInTheDocument()

      const repositoriesCount = screen.getByText('3 Repositories')
      expect(repositoriesCount).toBeInTheDocument()

      const contributionsCount = screen.getByText('100 Contributions')
      expect(contributionsCount).toBeInTheDocument()
    })
  })

  test('renders contribution heatmap correctly', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      error: null,
      loading: false,
    })
    ;(fetchHeatmapData as jest.Mock).mockResolvedValue({
      years: [{ year: '2023' }], // Provide years data to satisfy condition in component
    })

    render(<UserDetailsPage />)

    // Wait for useEffect to process the fetchHeatmapData result
    await waitFor(() => {
      const heatmapContainer = screen
        .getByAltText('Heatmap Background')
        .closest('div.hidden.lg\\:block')
      expect(heatmapContainer).toBeInTheDocument()
      expect(heatmapContainer).toHaveClass('hidden')
      expect(heatmapContainer).toHaveClass('lg:block')
    })
  })

  test('handles contribution heatmap loading error correctly', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      error: null,
    })
    ;(fetchHeatmapData as jest.Mock).mockResolvedValue(null)

    render(<UserDetailsPage />)

    await waitFor(() => {
      const heatmapTitle = screen.queryByText('Contribution Heatmap')
      expect(heatmapTitle).not.toBeInTheDocument()
    })
  })

  test('renders user summary section correctly', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      error: null,
    })

    render(<UserDetailsPage />)

    await waitFor(() => {
      const userName = screen.getByText('Test User')
      expect(userName).toBeInTheDocument()
      const avatar = screen.getByAltText('Test User')
      expect(avatar).toHaveClass('rounded-full')
      expect(avatar).toHaveClass('h-[200px]')
      expect(avatar).toHaveClass('w-[200px]')

      // Check for responsive classes
      const summaryContainer = avatar.closest('div.flex')
      expect(summaryContainer).toHaveClass('flex-col')
      expect(summaryContainer).toHaveClass('lg:flex-row')
    })
  })

  test('displays contact information elements', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      error: null,
    })

    render(<UserDetailsPage />)

    await waitFor(() => {
      const emailElement = screen.getByText('testuser@example.com')
      expect(emailElement).toBeInTheDocument()

      const companyElement = screen.getByText('Test Company')
      expect(companyElement).toBeInTheDocument()

      const locationElement = screen.getByText('Test Location')
      expect(locationElement).toBeInTheDocument()
    })
  })

  test('renders error message when GraphQL request fails', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: null,
      error: mockError,
      loading: false,
    })

    render(<UserDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('Error loading user')).toBeInTheDocument()
    })

    expect(addToast).toHaveBeenCalledWith({
      description: 'An unexpected server error occurred.',
      title: 'Server Error',
      timeout: 5000,
      shouldShowTimeoutProgress: true,
      color: 'danger',
      variant: 'solid',
    })
  })

  test('renders user summary with no bio', async () => {
    const noBioData = {
      ...mockUserDetailsData,
      user: { ...mockUserDetailsData.user, bio: '' },
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: noBioData,
      loading: false,
      error: null,
    })

    render(<UserDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Test User')).toBeInTheDocument()
      expect(screen.queryByText('Test @User')).not.toBeInTheDocument()
    })
  })

  test('renders bio with multiple GitHub mentions correctly', async () => {
    const multiMentionData = {
      ...mockUserDetailsData,
      user: { ...mockUserDetailsData.user, bio: 'Test @User1 and @User2!' },
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: multiMentionData,
      loading: false,
      error: null,
    })

    render(<UserDetailsPage />)
    await waitFor(() => {
      const user1Link = screen.getByText('@User1')
      const user2Link = screen.getByText('@User2')
      expect(user1Link).toHaveAttribute('href', 'https://github.com/User1')
      expect(user2Link).toHaveAttribute('href', 'https://github.com/User2')
    })
  })

  test('handles no recent issues gracefully', async () => {
    const noIssuesData = {
      user: { ...mockUserDetailsData.user, recentIssues: {} },
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: noIssuesData,
      loading: false,
      error: null,
    })

    render(<UserDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Recent Issues')).toBeInTheDocument()
      expect(screen.getByText('No recent releases.')).toBeInTheDocument()
    })
  })

  test('handles no recent pull requests gracefully', async () => {
    const noPullsData = {
      ...mockUserDetailsData,
      recentPullRequests: [],
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: noPullsData,
      loading: false,
      error: null,
    })

    render(<UserDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Recent Pull Requests')).toBeInTheDocument()
      expect(screen.queryByText('Test Pull Request')).not.toBeInTheDocument()
    })
  })

  test('handles no recent releases gracefully', async () => {
    const noReleasesData = {
      ...mockUserDetailsData,
      recentReleases: [],
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: noReleasesData,
      loading: false,
      error: null,
    })
    render(<UserDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Recent Releases')).toBeInTheDocument()
      expect(screen.queryByText('Test v1.0.0')).not.toBeInTheDocument()
    })
  })

  test('handles no recent milestones gracefully', async () => {
    const noMilestonesData = {
      ...mockUserDetailsData,
      recentMilestones: [],
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: noMilestonesData,
      loading: false,
      error: null,
    })
    render(<UserDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('Recent Milestones')).toBeInTheDocument()
      expect(screen.queryByText('v2.0.0 Release')).not.toBeInTheDocument()
    })
  })

  test('renders statistics with zero values correctly', async () => {
    const zeroStatsData = {
      ...mockUserDetailsData,
      user: {
        ...mockUserDetailsData.user,
        contributionsCount: 0,
        followersCount: 0,
        followingCount: 0,
        publicRepositoriesCount: 0,
      },
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: zeroStatsData,
      loading: false,
      error: null,
    })

    render(<UserDetailsPage />)
    await waitFor(() => {
      expect(screen.getByText('No Followers')).toBeInTheDocument()
      expect(screen.getByText('No Followings')).toBeInTheDocument()
      expect(screen.getByText('No Repositories')).toBeInTheDocument()
      expect(screen.getByText('No Contributions')).toBeInTheDocument()
    })
  })

  test('renders user details with missing optional fields', async () => {
    const minimalData = {
      ...mockUserDetailsData,
      user: {
        ...mockUserDetailsData.user,
        email: '',
        company: '',
        location: '',
      },
    }
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: minimalData,
      loading: false,
      error: null,
    })

    render(<UserDetailsPage />)
    await waitFor(() => {
      expect(screen.getAllByText('N/A').length).toBe(3)
      const bioContainer = screen.getByText('@testuser').closest('div')
      expect(bioContainer).toHaveClass('text-center')
      expect(bioContainer).toHaveClass('lg:text-left')
    })
  })

  test('does not render sponsor block', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockUserDetailsData,
      error: null,
    })
    render(<UserDetailsPage />)
    await waitFor(() => {
      expect(screen.queryByText('Want to become a sponsor?')).toBeNull()
    })
  })

  describe('Badge Display Tests', () => {
    test('renders badges section when user has badges', async () => {
      ;(useQuery as unknown as jest.Mock).mockReturnValue({
        data: mockUserDetailsData,
        loading: false,
        error: null,
      })

      render(<UserDetailsPage />)
      await waitFor(() => {
        expect(screen.getByTestId('badge-contributor')).toBeInTheDocument()
        expect(screen.getByTestId('badge-security-expert')).toBeInTheDocument()
      })
    })

    test('renders badges with correct props', async () => {
      ;(useQuery as unknown as jest.Mock).mockReturnValue({
        data: mockUserDetailsData,
        loading: false,
        error: null,
      })

      render(<UserDetailsPage />)
      await waitFor(() => {
        const contributorBadge = screen.getByTestId('badge-contributor')
        expect(contributorBadge).toHaveAttribute('data-css-class', 'fa-medal')
        expect(contributorBadge).toHaveAttribute('data-show-tooltip', 'true')

        const securityBadge = screen.getByTestId('badge-security-expert')
        expect(securityBadge).toHaveAttribute('data-css-class', 'fa-shield-alt')
        expect(securityBadge).toHaveAttribute('data-show-tooltip', 'true')
      })
    })

    test('does not render badges section when user has no badges', async () => {
      const dataWithoutBadges = {
        ...mockUserDetailsData,
        user: {
          ...mockUserDetailsData.user,
          badges: [],
          badgeCount: 0,
        },
      }

      ;(useQuery as unknown as jest.Mock).mockReturnValue({
        data: dataWithoutBadges,
        loading: false,
        error: null,
      })

      render(<UserDetailsPage />)
      await waitFor(() => {
        expect(screen.queryByTestId(/^badge-/)).not.toBeInTheDocument()
      })
    })

    test('does not render badges section when badges is undefined', async () => {
      const dataWithoutBadges = {
        ...mockUserDetailsData,
        user: {
          ...mockUserDetailsData.user,
          badges: undefined,
          badgeCount: 0,
        },
      }

      ;(useQuery as unknown as jest.Mock).mockReturnValue({
        data: dataWithoutBadges,
        loading: false,
        error: null,
      })

      render(<UserDetailsPage />)
      await waitFor(() => {
        expect(screen.queryByTestId(/^badge-/)).not.toBeInTheDocument()
      })
    })

    test('renders badges with fallback cssClass when not provided', async () => {
      const dataWithIncompleteBadges = {
        ...mockUserDetailsData,
        user: {
          ...mockUserDetailsData.user,
          badges: [
            {
              id: '1',
              name: 'Test Badge',
              cssClass: undefined,
              description: 'Test description',
              weight: 1,
            },
          ],
        },
      }

      ;(useQuery as unknown as jest.Mock).mockReturnValue({
        data: dataWithIncompleteBadges,
        loading: false,
        error: null,
      })

      render(<UserDetailsPage />)
      await waitFor(() => {
        const badge = screen.getByTestId('badge-test-badge')
        expect(badge).toHaveAttribute('data-css-class', 'medal')
      })
    })

    test('renders badges with empty cssClass fallback', async () => {
      const dataWithEmptyCssClass = {
        ...mockUserDetailsData,
        user: {
          ...mockUserDetailsData.user,
          badges: [
            {
              id: '1',
              name: 'Test Badge',
              cssClass: '',
              description: 'Test description',
              weight: 1,
            },
          ],
        },
      }

      ;(useQuery as unknown as jest.Mock).mockReturnValue({
        data: dataWithEmptyCssClass,
        loading: false,
        error: null,
      })

      render(<UserDetailsPage />)
      await waitFor(() => {
        const badge = screen.getByTestId('badge-test-badge')
        expect(badge).toHaveAttribute('data-css-class', 'medal')
      })
    })

    test('handles badges with special characters in names', async () => {
      const dataWithSpecialBadges = {
        ...mockUserDetailsData,
        user: {
          ...mockUserDetailsData.user,
          badges: [
            {
              id: '1',
              name: 'Badge & More!',
              cssClass: 'fa-star',
              description: 'Special badge',
              weight: 1,
            },
          ],
        },
      }
      ;(useQuery as unknown as jest.Mock).mockReturnValue({
        data: dataWithSpecialBadges,
        loading: false,
        error: null,
      })

      render(<UserDetailsPage />)
      await waitFor(() => {
        expect(screen.getByTestId('badge-badge-&-more!')).toBeInTheDocument()
      })
    })

    test('handles badges with long names', async () => {
      const dataWithLongNameBadge = {
        ...mockUserDetailsData,
        user: {
          ...mockUserDetailsData.user,
          badges: [
            {
              id: '1',
              name: 'Very Long Badge Name That Exceeds Normal Length',
              cssClass: 'fa-trophy',
              description: 'Long name badge',
              weight: 1,
            },
          ],
        },
      }

      ;(useQuery as unknown as jest.Mock).mockReturnValue({
        data: dataWithLongNameBadge,
        loading: false,
        error: null,
      })

      render(<UserDetailsPage />)
      await waitFor(() => {
        expect(
          screen.getByTestId('badge-very-long-badge-name-that-exceeds-normal-length')
        ).toBeInTheDocument()
      })
    })

    // eslint-disable-next-line jest/expect-expect
    test('renders badges in correct order as returned by backend (weight ASC then name ASC)', async () => {
      // Backend returns badges sorted by weight ASC, then name ASC
      // This test verifies the frontend preserves the backend ordering
      const dataWithOrderedBadges = {
        ...mockUserDetailsData,
        user: {
          ...mockUserDetailsData.user,
          badges: [
            // Backend returns badges in this order: weight ASC, then name ASC
            {
              id: '3',
              name: 'Alpha Badge',
              cssClass: 'fa-star',
              description: 'Alpha badge with weight 1',
              weight: 1,
            },
            {
              id: '4',
              name: 'Beta Badge',
              cssClass: 'fa-trophy',
              description: 'Beta badge with weight 1',
              weight: 1,
            },
            {
              id: '1',
              name: 'Contributor',
              cssClass: 'medal',
              description: 'Active contributor',
              weight: 1,
            },
            {
              id: '2',
              name: 'Security Expert',
              cssClass: 'fa-shield-alt',
              description: 'Security expertise',
              weight: 2,
            },
            {
              id: '5',
              name: 'Top Contributor',
              cssClass: 'fa-crown',
              description: 'Highest weight badge',
              weight: 3,
            },
          ],
          badgeCount: 5,
        },
      }

      ;(useQuery as unknown as jest.Mock).mockReturnValue({
        data: dataWithOrderedBadges,
        loading: false,
        error: null,
      })

      render(<UserDetailsPage />)
      await waitFor(() => {
        // Expected order matches backend contract: weight ASC (1, 1, 1, 2, 3), then name ASC for equal weights
        const expectedOrder = [
          'badge-alpha-badge', // weight 1, name ASC
          'badge-beta-badge', // weight 1, name ASC
          'badge-contributor', // weight 1, name ASC
          'badge-security-expert', // weight 2
          'badge-top-contributor', // weight 3
        ]
        expectBadgesInCorrectOrder(expectedOrder)
      })
    })
  })
})
