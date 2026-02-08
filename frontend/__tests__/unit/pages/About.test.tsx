import { useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { mockAboutData } from '@mockData/mockAboutData'
import { fireEvent, screen, waitFor, within } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import React, { act } from 'react'
import { render } from 'wrappers/testUtil'
import About from 'app/about/page'
import { GetAboutPageDataDocument } from 'types/__generated__/aboutQueries.generated'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))

const mockRouter = {
  push: jest.fn(),
}

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(() => mockRouter),
}))

jest.mock('react-icons/fa', () => ({
  FaMapSigns: () => <span data-testid="mock-icon" />,
  FaTools: () => <span data-testid="mock-icon" />,
}))

jest.mock('react-icons/fa6', () => ({
  FaCircleCheck: () => <span data-testid="mock-icon" />,
  FaClock: () => <span data-testid="mock-icon" />,
  FaScroll: () => <span data-testid="mock-icon" />,
  FaBullseye: () => <span data-testid="mock-icon" />,
  FaUser: () => <span data-testid="mock-icon" />,
  FaUsersGear: () => <span data-testid="mock-icon" />,
  FaLink: () => <span data-testid="mock-icon" />,
  FaChevronRight: () => <span data-testid="mock-icon" />,
  FaFolderOpen: () => <span data-testid="mock-icon" />,
  FaMedal: () => <span data-testid="mock-icon" />,
}))

jest.mock('react-icons/hi', () => ({
  HiUserGroup: () => <span data-testid="mock-icon" />,
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

jest.mock('utils/aboutData', () => ({
  missionContent: {
    mission: 'Test mission statement',
    whoItsFor: 'Test target audience description',
  },
  keyFeatures: [
    { title: 'Feature 1', description: 'Feature 1 description' },
    { title: 'Feature 2', description: 'Feature 2 description' },
  ],
  getInvolvedContent: {
    description: 'Get involved description',
    ways: ['Way 1', 'Way 2'],
    callToAction: 'Test call to action',
  },
  projectStory: ['Test story paragraph 1', 'Test story paragraph 2'],
  projectTimeline: [
    { title: 'Timeline Event 1', description: 'Timeline description 1', year: '2023' },
    { title: 'Timeline Event 2', description: 'Timeline description 2', year: '2024' },
    { title: 'Timeline Event 3', description: 'Timeline description 3', year: '2025' },
    { title: 'Timeline Event 4', description: 'Timeline description 4', year: '2026' },
    { title: 'Timeline Event 5', description: 'Timeline description 5', year: '2027' },
    { title: 'Timeline Event 6', description: 'Timeline description 6', year: '2028' },
    { title: 'Timeline Event 7', description: 'Timeline description 7', year: '2029' },
  ],
  technologies: [
    {
      section: 'Backend',
      tools: {
        python: {
          icon: '/images/icons/python.svg',
          url: 'https://www.python.org/',
        },
      },
    },
    {
      section: 'Frontend',
      tools: {
        'Next.js': {
          icon: '/images/icons/nextjs.svg',
          url: 'https://nextjs.org/',
        },
      },
    },
    {
      section: 'Tests',
      tools: {
        jest: {
          icon: '/images/icons/jest.svg',
          url: 'https://jestjs.io/',
        },
        pytest: {
          icon: '/images/icons/pytest.svg',
          url: 'https://docs.pytest.org/',
        },
      },
    },
    {
      section: 'Tools',
      tools: {
        ansible: {
          icon: '/images/icons/ansible.svg',
          url: 'https://www.ansible.com/',
        },
        gitHub: {
          icon: '/images/icons/github.svg',
          url: 'https://www.github.com/',
        },
      },
    },
  ],
}))

jest.mock('components/MarkdownWrapper', () => ({
  __esModule: true,
  default: ({ content }) => <div data-testid="markdown-content">{content}</div>,
}))

jest.mock('components/AnchorTitle', () => ({
  __esModule: true,
  default: ({ title }: { title: string }) => <span data-testid="anchor-title">{title}</span>,
}))

jest.mock('components/UserCard', () => ({
  __esModule: true,
  default: ({
    name,
    credentials,
    description,
    button,
  }: {
    name?: string
    credentials?: string
    description?: string
    button?: { label?: string; onclick?: () => void }
  }) => (
    <div data-testid="user-card">
      {name && <span>{name}</span>}
      {credentials && <span>{credentials}</span>}
      {description && <span>{description}</span>}
      {button?.label && (
        <button
          onClick={() => {
            button.onclick?.()
          }}
        >
          {button.label}
        </button>
      )}
    </div>
  ),
}))

jest.mock('components/ShowMoreButton', () => ({
  __esModule: true,
  default: function ShowMoreButtonMock({ onToggle }: { onToggle: () => void }) {
    const [isExpanded, setIsExpanded] = React.useState(false)

    const handleClick = () => {
      setIsExpanded(!isExpanded)
      onToggle()
    }

    return (
      <div className="mt-4 flex justify-start">
        <button
          onClick={handleClick}
          className="flex items-center bg-transparent px-0 text-blue-400"
        >
          {isExpanded ? (
            <>
              Show less{' '}
              <span data-testid="icon-chevron-up" aria-hidden="true">
                chevron-up
              </span>
            </>
          ) : (
            <>
              Show more{' '}
              <span data-testid="icon-chevron-down" aria-hidden="true">
                chevron-down
              </span>
            </>
          )}
        </button>
      </div>
    )
  },
}))

describe('About Component', () => {
  let mockRouter: { push: jest.Mock }
  beforeEach(() => {
    ;(useQuery as unknown as jest.Mock).mockImplementation((query) => {
      if (query === GetAboutPageDataDocument) {
        return {
          data: {
            project: mockAboutData.project,
            topContributors: mockAboutData.topContributors,
            leader1: mockAboutData.users['arkid15r'],
            leader2: mockAboutData.users['kasya'],
            leader3: mockAboutData.users['mamicidal'],
          },
          loading: false,
          error: null,
        }
      }
      return { loading: true }
    })
    mockRouter = { push: jest.fn() }
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders mission and who its for sections correctly', async () => {
    await act(async () => {
      render(<About />)
    })

    const missionSection = screen.getByText('Our Mission').closest('div')
    expect(missionSection).toBeInTheDocument()
    expect(screen.getByText('Test mission statement')).toBeInTheDocument()

    const whoItsForSection = screen.getByText("Who It's For").closest('div')
    expect(whoItsForSection).toBeInTheDocument()
    expect(screen.getByText('Test target audience description')).toBeInTheDocument()
  })

  test('renders mission section', async () => {
    await act(async () => {
      render(<About />)
    })
    expect(screen.getByText('Our Mission')).toBeInTheDocument()
    expect(screen.getByText('Test mission statement')).toBeInTheDocument()
  })

  test("renders 'Who It's For' section", async () => {
    await act(async () => {
      render(<About />)
    })
    expect(screen.getByText("Who It's For")).toBeInTheDocument()
    expect(screen.getByText(/Test target audience description/)).toBeInTheDocument()
  })

  test('renders key features section correctly', async () => {
    await act(async () => {
      render(<About />)
    })

    const keyFeaturesSection = screen.getByText('Key Features').closest('div')
    expect(keyFeaturesSection).toBeInTheDocument()

    expect(screen.getByText('Feature 1')).toBeInTheDocument()
    expect(screen.getByText('Feature 2')).toBeInTheDocument()
    expect(screen.getByText('Feature 1 description')).toBeInTheDocument()
    expect(screen.getByText('Feature 2 description')).toBeInTheDocument()
  })

  test('renders get involved section correctly', async () => {
    await act(async () => {
      render(<About />)
    })

    const getInvolvedSection = screen.getByText('Get Involved').closest('div')
    expect(getInvolvedSection).toBeInTheDocument()

    expect(screen.getByText('Get involved description')).toBeInTheDocument()
    expect(screen.getByText('Way 1')).toBeInTheDocument()
    expect(screen.getByText('Way 2')).toBeInTheDocument()
    expect(screen.getByText('Test call to action')).toBeInTheDocument()
  })

  test('renders project history timeline correctly', async () => {
    await act(async () => {
      render(<About />)
    })

    expect(screen.getByText('Project Timeline')).toBeInTheDocument()
    expect(screen.getByText('Timeline Event 7')).toBeInTheDocument()
    expect(screen.getByText('Timeline Event 2')).toBeInTheDocument()
    expect(screen.queryByText('Timeline Event 1')).not.toBeInTheDocument()
    expect(screen.getByText('2029')).toBeInTheDocument()
    expect(screen.queryByText('2023')).not.toBeInTheDocument()
    expect(screen.getByText('2024')).toBeInTheDocument()

    expect(screen.getByText('Timeline Event 7')).toBeInTheDocument()
    expect(screen.queryByText('Timeline Event 1')).not.toBeInTheDocument()

    const timelineSection = screen.getByText('Project Timeline').closest('h2')?.parentElement
    if (!timelineSection) throw new Error('Could not find Timeline section')

    const showMoreButton = within(timelineSection).getByRole('button', { name: /Show more/i })
    fireEvent.click(showMoreButton)

    await waitFor(() => {
      expect(screen.getByText('Timeline Event 1')).toBeInTheDocument()
    })

    const showLessButton = within(timelineSection).getByRole('button', { name: /Show less/i })
    fireEvent.click(showLessButton)

    await waitFor(() => {
      expect(screen.queryByText('Timeline Event 1')).not.toBeInTheDocument()
    })
  })

  test('renders leaders section with three leaders', async () => {
    await act(async () => {
      render(<About />)
    })

    const leadersSection = screen.getByText('Leaders').closest('div')
    expect(leadersSection).toBeInTheDocument()

    await waitFor(() => {
      expect(screen.getByText('Arkadii Yakovets')).toBeInTheDocument()
      expect(screen.getByText('CCSP, CISSP, CSSLP')).toBeInTheDocument()
      expect(screen.getByText('Kate Golovanova')).toBeInTheDocument()
      expect(screen.getByText('CC')).toBeInTheDocument()
      expect(screen.getByText('CISSP')).toBeInTheDocument()
    })
  })

  test('renders top contributors section correctly', async () => {
    await act(async () => {
      render(<About />)
    })

    await waitFor(() => {
      expect(screen.getByText('Wall of Fame')).toBeInTheDocument()
      expect(screen.getByText('Contributor 1')).toBeInTheDocument()
      expect(screen.getByText('Contributor 6')).toBeInTheDocument()
      expect(screen.getByText('Contributor 10')).toBeInTheDocument()
      expect(screen.getByText('Contributor 12')).toBeInTheDocument()
      expect(screen.queryByText('Contributor 13')).not.toBeInTheDocument()
    })
  })

  test('toggles contributors list when show more/less is clicked', async () => {
    await act(async () => {
      render(<About />)
    })
    await waitFor(() => {
      expect(screen.getByText('Contributor 12')).toBeInTheDocument()
      expect(screen.queryByText('Contributor 13')).not.toBeInTheDocument()
    })

    const wallOfFameSection = screen.getByText('Wall of Fame').closest('h2')?.parentElement
    if (!wallOfFameSection) throw new Error('Could not find Wall of Fame section')

    const showMoreButton = within(wallOfFameSection).getByRole('button', { name: /Show more/i })
    fireEvent.click(showMoreButton)

    await waitFor(() => {
      expect(screen.getByText('Contributor 13')).toBeInTheDocument()
      expect(screen.getByText('Contributor 14')).toBeInTheDocument()
      expect(screen.getByText('Contributor 15')).toBeInTheDocument()
    })

    const showLessButton = within(wallOfFameSection).getByRole('button', { name: /Show less/i })
    fireEvent.click(showLessButton)

    await waitFor(() => {
      expect(screen.queryByText('Contributor 13')).not.toBeInTheDocument()
    })
  })

  test('renders technologies section correctly', async () => {
    await act(async () => {
      render(<About />)
    })

    const technologiesSection = screen.getByText('Technologies & Tools').closest('div')
    expect(technologiesSection).toBeInTheDocument()

    expect(screen.getByText('Backend')).toBeInTheDocument()
    expect(screen.getByText('Frontend')).toBeInTheDocument()
    expect(screen.getByText('Tests')).toBeInTheDocument()
    expect(screen.getByText('Tools')).toBeInTheDocument()

    expect(screen.getByText('Ansible')).toBeInTheDocument()
    expect(screen.getByText('GitHub')).toBeInTheDocument()
    expect(screen.getByText('Next.js')).toBeInTheDocument()

    const ansibleLink = screen.getByText('Ansible').closest('a')
    expect(ansibleLink).toHaveAttribute('href', 'https://www.ansible.com/')

    const githubLink = screen.getByText('GitHub').closest('a')
    expect(githubLink).toHaveAttribute('href', 'https://www.github.com/')

    const reactLink = screen.getByText('Next.js').closest('a')
    expect(reactLink).toHaveAttribute('href', 'https://nextjs.org/')

    const ansibleIconContainer = screen.getByText('Ansible').previousSibling
    expect(ansibleIconContainer).toBeInTheDocument()

    const githubIconContainer = screen.getByText('GitHub').previousSibling
    expect(githubIconContainer).toBeInTheDocument()

    const reactIconContainer = screen.getByText('Next.js').previousSibling
    expect(reactIconContainer).toBeInTheDocument()
  })

  test('renders roadmap correctly', async () => {
    await act(async () => {
      render(<About />)
    })

    const roadmapSection = screen.getByRole('heading', { name: /Roadmap/ }).closest('div')
    expect(roadmapSection).toBeInTheDocument()
    const roadmapData = [...mockAboutData.project.recentMilestones].sort((a, b) =>
      a.title > b.title ? 1 : -1
    )

    expect(screen.getByText(roadmapData[0].title)).toBeInTheDocument()
    expect(screen.getByText(roadmapData[1].title)).toBeInTheDocument()
    expect(screen.getByText(roadmapData[2].title)).toBeInTheDocument()
    expect(screen.queryByText(roadmapData[3].title)).not.toBeInTheDocument()

    const showMoreButtonRef = within(roadmapSection).getByRole('button', { name: /Show more/i })
    fireEvent.click(showMoreButtonRef)

    await waitFor(() => {
      expect(screen.getByText(roadmapData[3].title)).toBeInTheDocument()
    })

    const showLessButtonRef = within(roadmapSection).getByRole('button', { name: /Show less/i })
    fireEvent.click(showLessButtonRef)

    await waitFor(() => {
      expect(screen.queryByText(roadmapData[3].title)).not.toBeInTheDocument()
    })
  })

  test('renders project stats cards correctly', async () => {
    await act(async () => {
      render(<About />)
    })

    await waitFor(() => {
      expect(screen.getByText('Contributors')).toBeInTheDocument()
      expect(screen.getByText('Open Issues')).toBeInTheDocument()
      expect(screen.getByText('Forks')).toBeInTheDocument()
      expect(screen.getByText('Stars')).toBeInTheDocument()
    })
  })

  test('handles null project in data response gracefully', async () => {
    ;(useQuery as unknown as jest.Mock).mockImplementation((query) => {
      if (query === GetAboutPageDataDocument) {
        return {
          data: {
            project: null,
            topContributors: mockAboutData.topContributors,
            leader1: mockAboutData.users['arkid15r'],
            leader2: mockAboutData.users['kasya'],
            leader3: mockAboutData.users['mamicidal'],
          },
          loading: false,
          error: null,
        }
      }
      return { loading: true }
    })

    await act(async () => {
      render(<About />)
    })

    await waitFor(() => {
      expect(screen.getByText('Data not found')).toBeInTheDocument()
      expect(
        screen.getByText("Sorry, the page you're looking for doesn't exist")
      ).toBeInTheDocument()
    })
  })

  test('navigates to user details on View Profile button click', async () => {
    await act(async () => {
      render(<About />)
    })

    await waitFor(() => {
      const viewDetailsButtons = screen.getAllByText('View Profile')
      expect(viewDetailsButtons[0]).toBeInTheDocument()
      fireEvent.click(viewDetailsButtons[0])
    })

    expect(mockRouter.push).toHaveBeenCalledWith('/members/arkid15r')
  })

  test('handles partial user data in leader response', async () => {
    ;(useQuery as unknown as jest.Mock).mockImplementation((query) => {
      if (query === GetAboutPageDataDocument) {
        return {
          data: {
            project: mockAboutData.project,
            topContributors: mockAboutData.topContributors,
            leader1: {
              avatarUrl: 'https://avatars.githubusercontent.com/u/2201626?v=4',
              company: 'OWASP',
              // name is missing
              login: 'arkid15r',
              url: '/members/arkid15r',
            },
            leader2: mockAboutData.users['kasya'],
            leader3: mockAboutData.users['mamicidal'],
          },
          loading: false,
          error: null,
        }
      }
      return { loading: true }
    })

    await act(async () => {
      render(<About />)
    })

    await waitFor(() => {
      expect(screen.getByText('arkid15r')).toBeInTheDocument()
      expect(screen.getByText('Kate Golovanova')).toBeInTheDocument()
      expect(screen.getByText('Starr Brown')).toBeInTheDocument()
    })
  })

  test('renders LoadingSpinner when project data is loading', async () => {
    ;(useQuery as unknown as jest.Mock).mockImplementation(() => {
      return { loading: true, data: null, error: null }
    })

    await act(async () => {
      render(<About />)
    })
    await waitFor(() => {
      // Check for skeleton loading state by looking for skeleton containers
      const skeletonContainers = document.querySelectorAll(
        String.raw`.bg-gray-100.dark\:bg-gray-800`
      )
      expect(skeletonContainers.length).toBeGreaterThan(0)
    })
  })

  test('renders ErrorDisplay when project is null', async () => {
    ;(useQuery as unknown as jest.Mock).mockImplementation((query) => {
      if (query === GetAboutPageDataDocument) {
        return {
          loading: false,
          data: {
            project: null,
            topContributors: mockAboutData.topContributors,
            leader1: mockAboutData.users['arkid15r'],
            leader2: mockAboutData.users['kasya'],
            leader3: mockAboutData.users['mamicidal'],
          },
          error: null,
        }
      }
      return { loading: true }
    })
    await act(async () => {
      render(<About />)
    })
    await waitFor(() => {
      expect(screen.getByText(/Data not found/)).toBeInTheDocument()
      expect(
        screen.getByText(/Sorry, the page you're looking for doesn't exist/)
      ).toBeInTheDocument()
    })
  })

  test('triggers toaster error when GraphQL request fails', async () => {
    ;(useQuery as unknown as jest.Mock).mockImplementation((query) => {
      if (query === GetAboutPageDataDocument) {
        return { loading: false, data: null, error: new Error('GraphQL error') }
      }
      return { loading: true }
    })
    await act(async () => {
      render(<About />)
    })
    await waitFor(() => {
      expect(addToast).toHaveBeenCalledWith({
        color: 'danger',
        description: 'GraphQL error',
        shouldShowTimeoutProgress: true,
        timeout: 5000,
        title: 'Server Error',
        variant: 'solid',
      })
    })
  })

  test('renders milestone with progress 0 - Not Started', async () => {
    ;(useQuery as unknown as jest.Mock).mockImplementation((query) => {
      if (query === GetAboutPageDataDocument) {
        return {
          loading: false,
          data: {
            ...mockAboutData,
            project: {
              ...mockAboutData.project,
              recentMilestones: [
                {
                  ...mockAboutData.project.recentMilestones[0],
                  progress: 0,
                  title: 'Not Started',
                },
              ],
            },
          },
          error: null,
        }
      }
      return { loading: true }
    })
    await act(async () => {
      render(<About />)
    })
    await waitFor(() => {
      expect(screen.getByText('Not Started')).toBeInTheDocument()
    })
  })

  test('renders milestone with progress 50 - In Progress', async () => {
    ;(useQuery as unknown as jest.Mock).mockImplementation((query) => {
      if (query === GetAboutPageDataDocument) {
        return {
          loading: false,
          data: {
            ...mockAboutData,
            project: {
              ...mockAboutData.project,
              recentMilestones: [
                {
                  ...mockAboutData.project.recentMilestones[0],
                  progress: 50,
                  title: 'In Progress Milestone',
                },
              ],
            },
          },
          error: null,
        }
      }
      return { loading: true }
    })
    await act(async () => {
      render(<About />)
    })
    await waitFor(() => {
      expect(screen.getByText('In Progress Milestone')).toBeInTheDocument()
    })
  })

  test('renders milestone with progress 100 - Completed', async () => {
    ;(useQuery as unknown as jest.Mock).mockImplementation((query) => {
      if (query === GetAboutPageDataDocument) {
        return {
          loading: false,
          data: {
            ...mockAboutData,
            project: {
              ...mockAboutData.project,
              recentMilestones: [
                {
                  ...mockAboutData.project.recentMilestones[0],
                  progress: 100,
                  title: 'Completed',
                },
              ],
            },
          },
          error: null,
        }
      }
      return { loading: true }
    })
    await act(async () => {
      render(<About />)
    })
    await waitFor(() => {
      expect(screen.getByText('Completed')).toBeInTheDocument()
    })
  })
})
