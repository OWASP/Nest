import { useQuery } from '@apollo/client'
import { fireEvent, screen, waitFor, within } from '@testing-library/react'
import { mockAboutData } from '@unit/data/mockAboutData'
import { render } from 'wrappers/testUtil'
import About from 'pages/About'

jest.mock('@apollo/client', () => ({
  ...jest.requireActual('@apollo/client'),
  useQuery: jest.fn(),
}))

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: () => <span data-testid="mock-icon" />,
}))

jest.mock('utils/aboutData', () => ({
  aboutText: [
    'This is a test paragraph about the project.',
    'This is another paragraph about the project history.',
  ],
  roadmap: [
    { title: 'Feature 1', issueLink: 'https://github.com/owasp/test/issues/1' },
    { title: 'Feature 2', issueLink: 'https://github.com/owasp/test/issues/2' },
    { title: 'Feature 3', issueLink: 'https://github.com/owasp/test/issues/3' },
  ],
  technologies: [
    {
      section: 'Backend',
      tools: {
        Python: {
          icon: 'devicon-python-plain',
          url: 'https://www.python.org/',
        },
      },
    },
    {
      section: 'Frontend',
      tools: {
        React: {
          icon: 'devicon-react-original',
          url: 'https://reactjs.org/',
        },
      },
    },
    {
      section: 'Tests',
      tools: {
        Jest: {
          icon: 'devicon-jest-plain',
          url: 'https://jestjs.io/',
        },
        Pytest: {
          icon: 'devicon-pytest-plain',
          url: 'https://docs.pytest.org/',
        },
      },
    },
    {
      section: 'Tools',
      tools: {
        Ansible: {
          icon: 'devicon-ansible-plain',
          url: 'https://www.ansible.com/',
        },
        GitHub: {
          icon: 'devicon-github-original',
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

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: jest.fn(),
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

const mockError = {
  error: new Error('GraphQL error'),
}

describe('About Component', () => {
  beforeEach(() => {
    ;(useQuery as jest.Mock).mockImplementation((query, options) => {
      if (options?.variables?.key === 'nest') {
        return mockProjectData
      } else if (options?.variables?.key === 'arkid15r') {
        return mockUserData('arkid15r')
      } else if (options?.variables?.key === 'kasya') {
        return mockUserData('kasya')
      } else if (options?.variables?.key === 'mamicidal') {
        return mockUserData('mamicidal')
      }
      return { loading: true }
    })
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
      expect(screen.getByText('Kate Golovanova')).toBeInTheDocument()
      expect(screen.getByText('Starr Brown')).toBeInTheDocument()
    })
  })

  test('handles leader data loading error gracefully', async () => {
    ;(useQuery as jest.Mock).mockImplementation((query, options) => {
      if (options?.variables?.key === 'nest') {
        return mockProjectData
      } else if (options?.variables?.key === 'arkid15r') {
        return { data: null, loading: false, error: mockError }
      } else if (options?.variables?.key === 'kasya') {
        return mockUserData('kasya')
      } else if (options?.variables?.key === 'mamicidal') {
        return mockUserData('mamicidal')
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
      expect(screen.queryByText('Contributor 7')).not.toBeInTheDocument()
    })
  })

  test('toggles contributors list when show more/less is clicked', async () => {
    render(<About />)
    await waitFor(() => {
      expect(screen.getByText('Contributor 6')).toBeInTheDocument()
      expect(screen.queryByText('Contributor 7')).not.toBeInTheDocument()
    })

    const contributorsSection = screen
      .getByRole('heading', { name: /Top Contributors/i })
      .closest('div')
    const showMoreButton = within(contributorsSection!).getByRole('button', { name: /Show more/i })
    fireEvent.click(showMoreButton)

    await waitFor(() => {
      expect(screen.getByText('Contributor 7')).toBeInTheDocument()
      expect(screen.getByText('Contributor 8')).toBeInTheDocument()
    })

    const showLessButton = within(contributorsSection!).getByRole('button', { name: /Show less/i })
    fireEvent.click(showLessButton)

    await waitFor(() => {
      expect(screen.queryByText('Contributor 7')).not.toBeInTheDocument()
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
    expect(screen.getByText('React')).toBeInTheDocument()

    const ansibleLink = screen.getByText('Ansible').closest('a')
    expect(ansibleLink).toHaveAttribute('href', 'https://www.ansible.com/')

    const githubLink = screen.getByText('GitHub').closest('a')
    expect(githubLink).toHaveAttribute('href', 'https://www.github.com/')

    const reactLink = screen.getByText('React').closest('a')
    expect(reactLink).toHaveAttribute('href', 'https://reactjs.org/')

    const ansibleIcon = screen.getByText('Ansible').previousSibling
    expect(ansibleIcon).toHaveClass('devicon-ansible-plain')

    const githubIcon = screen.getByText('GitHub').previousSibling
    expect(githubIcon).toHaveClass('devicon-github-original')

    const reactIcon = screen.getByText('React').previousSibling
    expect(reactIcon).toHaveClass('devicon-react-original')
  })

  test('renders roadmap correctly', async () => {
    render(<About />)

    const roadmapSection = screen.getByText('Roadmap').closest('div')
    expect(roadmapSection).toBeInTheDocument()

    const roadmapItems = within(roadmapSection).getAllByRole('listitem')
    expect(roadmapItems).toHaveLength(3)

    expect(screen.getByText('Feature 1')).toBeInTheDocument()
    expect(screen.getByText('Feature 2')).toBeInTheDocument()
    expect(screen.getByText('Feature 3')).toBeInTheDocument()

    const links = within(roadmapSection).getAllByRole('link')
    expect(links[0].getAttribute('href')).toBe('https://github.com/owasp/test/issues/1')
  })

  test('renders project stats cards correctly', async () => {
    render(<About />)

    await waitFor(() => {
      expect(screen.getByText('Contributors')).toBeInTheDocument()
      expect(screen.getByText('Issues')).toBeInTheDocument()
      expect(screen.getByText('Forks')).toBeInTheDocument()
      expect(screen.getByText('Stars')).toBeInTheDocument()
    })
  })

  test('leader card buttons open external links', async () => {
    const windowOpenSpy = jest.spyOn(window, 'open').mockImplementation(() => null)

    render(<About />)

    await waitFor(() => {
      expect(screen.getAllByText('View Profile')).toHaveLength(3)
    })

    const viewProfileButtons = screen.getAllByText('View Profile')
    fireEvent.click(viewProfileButtons[0])

    expect(windowOpenSpy).toHaveBeenCalledWith(
      '/community/users/arkid15r',
      '_blank',
      'noopener,noreferrer'
    )

    windowOpenSpy.mockRestore()
  })
})
