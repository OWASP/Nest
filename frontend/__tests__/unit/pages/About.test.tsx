import { useQuery } from '@apollo/client'
import { addToast } from '@heroui/toast'
import { fireEvent, screen, waitFor, within } from '@testing-library/react'
import { mockAboutData } from '@unit/data/mockAboutData'
import { useRouter } from 'next/navigation'
import { render } from 'wrappers/testUtil'
import About from 'app/about/page'
import { GET_PROJECT_METADATA, GET_TOP_CONTRIBUTORS } from 'server/queries/projectQueries'
import { GET_LEADER_DATA } from 'server/queries/userQueries'

jest.mock('@apollo/client', () => ({
  ...jest.requireActual('@apollo/client'),
  useQuery: jest.fn(),
}))

const mockRouter = {
  push: jest.fn(),
}
jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(() => mockRouter),
}))

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: () => <span data-testid="mock-icon" />,
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

jest.mock('utils/aboutData', () => ({
  aboutText: [
    'This is a test paragraph about the project.',
    'This is another paragraph about the project history.',
  ],
  technologies: [
    {
      section: 'Backend',
      tools: {
        Python: {
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
        Jest: {
          icon: '/images/icons/jest.svg',
          url: 'https://jestjs.io/',
        },
        Pytest: {
          icon: '/images/icons/pytest.svg',
          url: 'https://docs.pytest.org/',
        },
      },
    },
    {
      section: 'Tools',
      tools: {
        Ansible: {
          icon: '/images/icons/ansible.svg',
          url: 'https://www.ansible.com/',
        },
        GitHub: {
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

const mockUserData = (username) => ({
  data: { user: mockAboutData.users[username] },
  loading: false,
  error: null,
})

const mockProjectData = {
  data: { project: mockAboutData.project },
  loading: false,
  error: null,
}

const mockTopContributorsData = {
  data: { topContributors: mockAboutData.topContributors },
  loading: false,
  error: null,
}

const mockError = {
  error: new Error('GraphQL error'),
}

describe('About Component', () => {
  let mockRouter: { push: jest.Mock }
  beforeEach(() => {
    ;(useQuery as jest.Mock).mockImplementation((query, options) => {
      const key = options?.variables?.key

      if (query === GET_PROJECT_METADATA) {
        if (key === 'nest') {
          return mockProjectData
        }
      } else if (query === GET_TOP_CONTRIBUTORS) {
        if (key === 'nest') {
          return mockTopContributorsData
        }
      } else if (query === GET_LEADER_DATA) {
        return mockUserData(key)
      }

      return { loading: true }
    })
    mockRouter = { push: jest.fn() }
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders project history correctly', async () => {
    render(<About />)

    const historySection = screen.getByText('History').closest('div')
    expect(historySection).toBeInTheDocument()

    const markdownContents = await screen.findAllByTestId('markdown-content')
    expect(markdownContents.length).toBe(2)
    expect(markdownContents[0].textContent).toBe('This is a test paragraph about the project.')
    expect(markdownContents[1].textContent).toBe(
      'This is another paragraph about the project history.'
    )
  })

  test('renders leaders section with three leaders', async () => {
    render(<About />)

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

  test('handles leader data loading error gracefully', async () => {
    ;(useQuery as jest.Mock).mockImplementation((query, options) => {
      if (options?.variables?.key === 'nest') {
        return mockProjectData
      } else if (options?.variables?.key === 'arkid15r') {
        return { data: null, loading: false, error: mockError }
      } else if (options?.variables?.key === 'kasya' || options?.variables?.key === 'mamicidal') {
        return mockUserData(options?.variables?.key)
      }
      return { loading: true }
    })

    render(<About />)

    await waitFor(() => {
      expect(screen.getByText("Error loading arkid15r's data")).toBeInTheDocument()
      expect(screen.getByText('Kate Golovanova')).toBeInTheDocument()
      expect(screen.getByText('Starr Brown')).toBeInTheDocument()
    })
  })

  test('renders top contributors section correctly', async () => {
    render(<About />)

    await waitFor(() => {
      expect(screen.getByText('Top Contributors')).toBeInTheDocument()
      expect(screen.getByText('Contributor 1')).toBeInTheDocument()
      expect(screen.getByText('Contributor 6')).toBeInTheDocument()
      expect(screen.queryByText('Contributor 10')).not.toBeInTheDocument()
    })
  })

  test('toggles contributors list when show more/less is clicked', async () => {
    render(<About />)
    await waitFor(() => {
      expect(screen.getByText('Contributor 6')).toBeInTheDocument()
      expect(screen.queryByText('Contributor 10')).not.toBeInTheDocument()
    })

    const showMoreButton = screen.getByRole('button', { name: /Show more/i })
    fireEvent.click(showMoreButton)

    await waitFor(() => {
      expect(screen.getByText('Contributor 7')).toBeInTheDocument()
      expect(screen.getByText('Contributor 8')).toBeInTheDocument()
    })

    const showLessButton = screen.getByRole('button', { name: /Show less/i })
    fireEvent.click(showLessButton)

    await waitFor(() => {
      expect(screen.queryByText('Contributor 10')).not.toBeInTheDocument()
    })
  })

  test('renders technologies section correctly', async () => {
    render(<About />)

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
    render(<About />)

    const roadmapSection = screen.getByRole('heading', { name: 'Roadmap' }).closest('div')
    expect(roadmapSection).toBeInTheDocument()
    const roadmapData = mockAboutData.project.recentMilestones
    const links = within(roadmapSection)
      .getAllByRole('link')
      .filter((link) => link.getAttribute('href') !== '#roadmap')

    for (let i = 0; i < roadmapData.length; i++) {
      const milestone = roadmapData[i]
      expect(screen.getByText(milestone.title)).toBeInTheDocument()
      expect(screen.getByText(milestone.body)).toBeInTheDocument()
      expect(links[i].getAttribute('href')).toBe(milestone.url)
    }
  })

  test('renders project stats cards correctly', async () => {
    render(<About />)

    await waitFor(() => {
      expect(screen.getByText('Contributors')).toBeInTheDocument()
      expect(screen.getByText('Open Issues')).toBeInTheDocument()
      expect(screen.getByText('Forks')).toBeInTheDocument()
      expect(screen.getByText('Stars')).toBeInTheDocument()
    })
  })

  test('LeaderData component shows loading state correctly', async () => {
    ;(useQuery as jest.Mock).mockImplementation((query, options) => {
      if (options?.variables?.key === 'nest') {
        return mockProjectData
      } else if (options?.variables?.key === 'arkid15r') {
        return { data: null, loading: true, error: null }
      } else if (options?.variables?.key === 'kasya') {
        return mockUserData('kasya')
      } else if (options?.variables?.key === 'mamicidal') {
        return mockUserData('mamicidal')
      }
      return { loading: true }
    })

    render(<About />)

    await waitFor(() => {
      expect(screen.getByText('Loading arkid15r...')).toBeInTheDocument()
    })

    await waitFor(() => {
      expect(screen.getByText('Kate Golovanova')).toBeInTheDocument()
      expect(screen.getByText('Starr Brown')).toBeInTheDocument()
    })

    const loadingMessages = screen.getAllByText(/Loading .+\.\.\./)
    expect(loadingMessages).toHaveLength(1)
  })

  test('LeaderData component handles null user data correctly', async () => {
    ;(useQuery as jest.Mock).mockImplementation((query, options) => {
      if (options?.variables?.key === 'nest') {
        return mockProjectData
      } else if (options?.variables?.key === 'arkid15r') {
        return { data: { user: null }, loading: false, error: null }
      } else if (options?.variables?.key === 'kasya') {
        return mockUserData('kasya')
      } else if (options?.variables?.key === 'mamicidal') {
        return mockUserData('mamicidal')
      }
      return { loading: true }
    })

    render(<About />)

    await waitFor(() => {
      expect(screen.getByText('No data available for arkid15r')).toBeInTheDocument()
    })

    await waitFor(() => {
      expect(screen.getByText('Kate Golovanova')).toBeInTheDocument()
      expect(screen.getByText('Starr Brown')).toBeInTheDocument()
    })

    const noDataMessages = screen.getAllByText(/No data available for .+/)
    expect(noDataMessages).toHaveLength(1)
  })

  test('handles null project in data response gracefully', async () => {
    ;(useQuery as jest.Mock).mockImplementation((query, options) => {
      if (options?.variables?.key === 'nest') {
        return { data: { project: null }, loading: false, error: null }
      } else if (['arkid15r', 'kasya', 'mamicidal'].includes(options?.variables?.key)) {
        return mockUserData(options?.variables?.key)
      }
      return { loading: true }
    })

    render(<About />)

    await waitFor(() => {
      expect(screen.getByText('Data not found')).toBeInTheDocument()
      expect(
        screen.getByText("Sorry, the page you're looking for doesn't exist")
      ).toBeInTheDocument()
    })
  })

  test('handles undefined user data in leader response', async () => {
    ;(useQuery as jest.Mock).mockImplementation((query, options) => {
      if (options?.variables?.key === 'nest') {
        return mockProjectData
      } else if (options?.variables?.key === 'arkid15r') {
        return { data: undefined, loading: false, error: null }
      } else if (options?.variables?.key === 'kasya' || options?.variables?.key === 'mamicidal') {
        return mockUserData(options?.variables?.key)
      }
      return { loading: true }
    })

    render(<About />)

    await waitFor(() => {
      expect(screen.getByText('No data available for arkid15r')).toBeInTheDocument()
      expect(screen.getByText('Kate Golovanova')).toBeInTheDocument()
      expect(screen.getByText('Starr Brown')).toBeInTheDocument()
    })
  })

  test('navigates to user details on View Profile button click', async () => {
    render(<About />)

    await waitFor(() => {
      const viewDetailsButtons = screen.getAllByText('View Profile')
      expect(viewDetailsButtons[0]).toBeInTheDocument()
      fireEvent.click(viewDetailsButtons[0])
    })

    expect(mockRouter.push).toHaveBeenCalledWith('/members/arkid15r')
  })

  test('handles partial user data in leader response', async () => {
    const partialUserData = {
      data: {
        user: {
          avatarUrl: 'https://avatars.githubusercontent.com/u/2201626?v=4',
          company: 'OWASP',
          // name is missing
          url: '/members/arkid15r',
        },
      },
      loading: false,
      error: null,
    }

    ;(useQuery as jest.Mock).mockImplementation((query, options) => {
      if (options?.variables?.key === 'nest') {
        return mockProjectData
      } else if (options?.variables?.key === 'arkid15r') {
        return partialUserData
      } else if (options?.variables?.key === 'kasya' || options?.variables?.key === 'mamicidal') {
        return mockUserData(options?.variables?.key)
      }
      return { loading: true }
    })

    render(<About />)

    await waitFor(() => {
      expect(screen.getByText('arkid15r')).toBeInTheDocument()
      expect(screen.getByText('Kate Golovanova')).toBeInTheDocument()
      expect(screen.getByText('Starr Brown')).toBeInTheDocument()
    })
  })

  test('shows fallback when user data is missing', async () => {
    ;(useQuery as jest.Mock).mockImplementation((query, options) => {
      if (options?.variables?.key === 'nest') {
        return mockProjectData
      } else if (options?.variables?.key === 'arkid15r') {
        return { data: null, loading: false, error: false }
      } else if (options?.variables?.key === 'kasya') {
        return mockUserData('kasya')
      } else if (options?.variables?.key === 'mamicidal') {
        return mockUserData('mamicidal')
      }
      return { loading: true }
    })

    render(<About />)

    await waitFor(() => {
      expect(screen.getByText(/No data available for arkid15r/i)).toBeInTheDocument()
    })
  })

  test('renders LoadingSpinner when project data is loading', async () => {
    ;(useQuery as jest.Mock).mockImplementation((query, options) => {
      if (options?.variables?.key === 'nest') {
        return { loading: true, data: null, error: null }
      }
      return {
        loading: false,
        data: { user: { avatarUrl: '', company: '', name: 'Dummy', location: '' } },
        error: null,
      }
    })

    render(<About />)
    await waitFor(() => {
      // Look for the element with alt text "Loading indicator"
      const spinner = screen.getAllByAltText('Loading indicator')
      expect(spinner.length).toBeGreaterThan(0)
    })
  })

  test('renders ErrorDisplay when project is null', async () => {
    ;(useQuery as jest.Mock).mockImplementation((query, options) => {
      if (options?.variables?.key === 'nest') {
        return { loading: false, data: { project: null }, error: null }
      }
      return {
        loading: false,
        data: { user: { avatarUrl: '', company: '', name: 'Dummy', location: '' } },
        error: null,
      }
    })
    render(<About />)
    await waitFor(() => {
      expect(screen.getByText(/Data not found/)).toBeInTheDocument()
      expect(
        screen.getByText(/Sorry, the page you're looking for doesn't exist/)
      ).toBeInTheDocument()
    })
  })

  test('triggers toaster error when GraphQL request fails for project', async () => {
    ;(useQuery as jest.Mock).mockImplementation((query, options) => {
      if (query === GET_PROJECT_METADATA && options?.variables?.key === 'nest') {
        return { loading: false, data: null, error: new Error('GraphQL error') }
      }
      return {
        loading: false,
        data: { user: { avatarUrl: '', company: '', name: 'Dummy', location: '' } },
        error: null,
      }
    })
    render(<About />)
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

  test('triggers toaster error when GraphQL request fails for topContributors', async () => {
    ;(useQuery as jest.Mock).mockImplementation((query, options) => {
      if (query === GET_TOP_CONTRIBUTORS && options?.variables?.key === 'nest') {
        return { loading: false, data: null, error: new Error('GraphQL error') }
      }
      return {
        loading: false,
        data: { user: { avatarUrl: '', company: '', name: 'Dummy', location: '' } },
        error: null,
      }
    })
    render(<About />)
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
})
