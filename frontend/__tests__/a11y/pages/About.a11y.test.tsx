import { useQuery } from '@apollo/client/react'
import { mockAboutData } from '@mockData/mockAboutData'
import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import About from 'app/about/page'
import {
  GetProjectMetadataDocument,
  GetTopContributorsDocument,
} from 'types/__generated__/projectQueries.generated'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
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

jest.mock('components/MarkdownWrapper', () => ({
  __esModule: true,
  default: ({ content }) => <div data-testid="markdown-content">{content}</div>,
}))

const mockProjectData = {
  data: { project: mockAboutData.project },
  loading: false,
  error: null,
}

const mockTopContributorsData = {
  data: null,
  loading: false,
  error: null,
}

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

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('About Page Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  const mockUseQuery = useQuery as unknown as jest.Mock

  it('should have no accessibility violations', async () => {
    mockUseQuery.mockImplementation((query, options) => {
      const key = options?.variables?.key

      if (query === GetProjectMetadataDocument) {
        if (key === 'nest') {
          return mockProjectData
        }
      } else if (query === GetTopContributorsDocument) {
        if (key === 'nest') {
          return mockTopContributorsData
        }
      }

      return { loading: true }
    })

    const { container } = render(<About />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have no accessibility violations when loading', async () => {
    mockUseQuery.mockReturnValue({ loading: true })

    const { container } = render(<About />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have no accessibility violations when error occurs', async () => {
    mockUseQuery.mockReturnValue({
      data: null,
      loading: false,
      error: new Error('Test error'),
    })

    const { container } = render(<About />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
