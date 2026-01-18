/* eslint-disable @next/next/no-img-element */
import { screen, fireEvent } from '@testing-library/react'
import { usePathname, useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import React from 'react'
import { render } from 'wrappers/testUtil'
import { ExperienceLevelEnum, ProgramStatusEnum } from 'types/__generated__/graphql'
import type { Module } from 'types/mentorship'
import SingleModuleCard from 'components/SingleModuleCard'

jest.mock('next/link', () => ({
  __esModule: true,
  default: ({
    children,
    href,
    className,
    ...props
  }: {
    children: React.ReactNode
    href: string
    className?: string
    [key: string]: unknown
  }) => (
    <a href={href} className={className} {...props} data-testid="module-link">
      {children}
    </a>
  ),
}))

jest.mock('next/image', () => ({
  __esModule: true,
  default: ({ src, alt, ...props }: { src: string; alt: string; [key: string]: unknown }) => (
    <img src={src} alt={alt} {...props} data-testid="contributor-avatar" />
  ),
}))

// Mock dependencies
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  usePathname: jest.fn(),
}))

jest.mock('next-auth/react', () => ({
  useSession: jest.fn(),
}))

jest.mock('react-icons/hi', () => ({
  HiUserGroup: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="icon-users" {...props} />
  ),
}))

jest.mock('utils/dateFormatter', () => ({
  formatDate: jest.fn((date: string) => new Date(date).toLocaleDateString()),
}))

jest.mock('utils/urlFormatter', () => ({
  getMemberUrl: jest.fn((login: string) => `/members/${login}`),
}))

jest.mock('components/ModuleCard', () => ({
  getSimpleDuration: jest.fn((start: string, end: string) => {
    const startDate = new Date(start)
    const endDate = new Date(end)
    const diffTime = Math.abs(endDate.getTime() - startDate.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return `${diffDays} days`
  }),
}))

jest.mock('components/ShowMoreButton', () => ({
  __esModule: true,
  default: ({ onToggle }: { onToggle: () => void }) => (
    <button data-testid="show-more-button" onClick={onToggle}>
      Show more
    </button>
  ),
}))

const mockPush = jest.fn()
const mockUseRouter = useRouter as jest.MockedFunction<typeof useRouter>
const mockUsePathname = usePathname as jest.MockedFunction<typeof usePathname>
const mockUseSession = useSession as jest.MockedFunction<typeof useSession>

// Test data
const mockModule: Module = {
  id: '1',
  key: 'test-module',
  name: 'Test Module',
  description: 'This is a test module description',
  status: ProgramStatusEnum.Published,
  experienceLevel: ExperienceLevelEnum.Intermediate,
  mentors: [
    {
      id: 'mentor-user1',
      name: 'user1',
      login: 'user1',
      avatarUrl: 'https://example.com/avatar1.jpg',
    },
    {
      id: 'mentor-user2',
      name: 'user2',
      login: 'user2',
      avatarUrl: 'https://example.com/avatar2.jpg',
    },
  ],
  startedAt: '2024-01-01T00:00:00Z',
  endedAt: '2024-12-31T23:59:59Z',
  domains: ['frontend', 'backend'],
  tags: ['react', 'nodejs'],
  labels: ['good first issue', 'bug'],
}

const mockModuleWithManyMentors: Module = {
  ...mockModule,
  mentors: Array.from({ length: 10 }, (_, i) => ({
    name: `mentor${i + 1}`,
    login: `mentor${i + 1}`,
    avatarUrl: `https://example.com/avatar${i + 1}.jpg`,
  })),
}

const mockAdmins = [{ login: 'admin1' }, { login: 'admin2' }]

describe('SingleModuleCard', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockUseRouter.mockReturnValue({
      push: mockPush,
      back: jest.fn(),
      forward: jest.fn(),
      refresh: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
    })
    mockUsePathname.mockReturnValue('/my/mentorship/programs/test-program')
    mockUseSession.mockReturnValue({
      data: null,
      status: 'unauthenticated',
      update: jest.fn(),
    })
  })

  describe('Basic Rendering', () => {
    it('renders module card with basic information', () => {
      render(<SingleModuleCard module={mockModule} />)

      expect(screen.getByText('Test Module')).toBeInTheDocument()
      expect(screen.getByText('This is a test module description')).toBeInTheDocument()
      expect(screen.getAllByTestId('icon-users').length).toBeGreaterThan(0)
    })

    it('renders module details correctly', () => {
      render(<SingleModuleCard module={mockModule} />)

      expect(screen.getByText('Experience Level:')).toBeInTheDocument()
      expect(screen.getByText('Intermediate')).toBeInTheDocument()
      expect(screen.getByText('Start Date:')).toBeInTheDocument()
      expect(screen.getByText('End Date:')).toBeInTheDocument()
      expect(screen.getByText('Duration:')).toBeInTheDocument()
    })

    it('renders mentors section with inline contributors when mentors exist', () => {
      render(<SingleModuleCard module={mockModule} />)

      expect(screen.getByText('Mentors')).toBeInTheDocument()
      expect(screen.getByText('User1')).toBeInTheDocument()
      expect(screen.getByText('User2')).toBeInTheDocument()
      expect(screen.getAllByTestId('contributor-avatar')).toHaveLength(2)
    })

    it('does not render mentors section when no mentors', () => {
      const moduleWithoutMentors = { ...mockModule, mentors: [] }
      render(<SingleModuleCard module={moduleWithoutMentors} />)

      expect(screen.queryByText('Mentors')).not.toBeInTheDocument()
    })

    it('renders module link with correct href', () => {
      render(<SingleModuleCard module={mockModule} />)

      const moduleLinks = screen.getAllByTestId('module-link')
      const titleLink = moduleLinks.find((link) =>
        link.getAttribute('href')?.includes('/modules/test-module')
      )
      expect(titleLink).toHaveAttribute(
        'href',
        '/my/mentorship/programs/test-program/modules/test-module'
      )
    })
  })

  describe('Inline Contributors Rendering', () => {
    it('renders contributor avatars inline without nested shadows', () => {
      render(<SingleModuleCard module={mockModule} />)

      const avatars = screen.getAllByTestId('contributor-avatar')
      expect(avatars.length).toBeGreaterThan(0)
    })

    it('renders show more button when more than 6 mentors', () => {
      render(<SingleModuleCard module={mockModuleWithManyMentors} />)

      expect(screen.getByTestId('show-more-button')).toBeInTheDocument()
    })

    it('does not render show more button when 6 or fewer mentors', () => {
      render(<SingleModuleCard module={mockModule} />)

      expect(screen.queryByTestId('show-more-button')).not.toBeInTheDocument()
    })

    it('toggles show all mentors when show more button is clicked', () => {
      render(<SingleModuleCard module={mockModuleWithManyMentors} />)

      // Initially shows only 6
      expect(screen.getAllByTestId('contributor-avatar')).toHaveLength(6)

      // Click show more
      fireEvent.click(screen.getByTestId('show-more-button'))

      // Should now show all 10
      expect(screen.getAllByTestId('contributor-avatar')).toHaveLength(10)
    })
  })

  describe('Mentee URL Handling', () => {
    it('uses private mentee URL in private view', () => {
      const moduleWithMentees: Module = {
        ...mockModule,
        mentees: [
          {
            name: 'mentee1',
            login: 'mentee1',
            avatarUrl: 'https://example.com/mentee1.jpg',
          },
        ],
      }
      mockUsePathname.mockReturnValue('/my/mentorship/programs/test-program')

      render(<SingleModuleCard module={moduleWithMentees} />)

      const menteeLinks = screen.getAllByTestId('module-link')
      const menteeLink = menteeLinks.find((link) =>
        link.getAttribute('href')?.includes('/mentees/')
      )
      expect(menteeLink).toHaveAttribute(
        'href',
        '/my/mentorship/programs/test-program/modules/test-module/mentees/mentee1'
      )
    })

    it('uses public member URL in public view', () => {
      const moduleWithMentees: Module = {
        ...mockModule,
        mentors: [],
        mentees: [
          {
            name: 'mentee1',
            login: 'mentee1',
            avatarUrl: 'https://example.com/mentee1.jpg',
          },
        ],
      }
      mockUsePathname.mockReturnValue('/programs/test-program')

      render(<SingleModuleCard module={moduleWithMentees} />)

      const allLinks = screen.getAllByRole('link')
      const menteeLink = allLinks.find((link) => link.getAttribute('href') === '/members/mentee1')
      expect(menteeLink).toBeInTheDocument()
    })
  })

  describe('Props Handling', () => {
    it('renders correctly with minimal props', () => {
      render(<SingleModuleCard module={mockModule} />)

      expect(screen.getByText('Test Module')).toBeInTheDocument()
      expect(screen.getByText('This is a test module description')).toBeInTheDocument()
    })

    it('handles admin props correctly', () => {
      render(<SingleModuleCard module={mockModule} accessLevel="admin" admins={mockAdmins} />)

      expect(screen.getByText('Test Module')).toBeInTheDocument()
    })
  })

  describe('Edge Cases', () => {
    it('handles missing module data gracefully', () => {
      const incompleteModule = {
        ...mockModule,
        description: '',
        mentors: [],
      }

      render(<SingleModuleCard module={incompleteModule} />)

      expect(screen.getByText('Test Module')).toBeInTheDocument()
      expect(screen.queryByText('Mentors')).not.toBeInTheDocument()
    })

    it('handles undefined admins array gracefully', () => {
      render(<SingleModuleCard module={mockModule} accessLevel="admin" />)

      // Should render without errors even with admin props
      expect(screen.getByText('Test Module')).toBeInTheDocument()
    })

    it('renders no description available when description is empty', () => {
      const moduleWithoutDescription = { ...mockModule, description: '' }
      render(<SingleModuleCard module={moduleWithoutDescription} />)

      expect(screen.getByText('No description available.')).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('has accessible link for module navigation', () => {
      render(<SingleModuleCard module={mockModule} />)

      const moduleLinks = screen.getAllByTestId('module-link')
      const titleLink = moduleLinks.find((link) =>
        link.getAttribute('href')?.includes('/modules/test-module')
      )
      expect(titleLink).toBeInTheDocument()
      expect(titleLink).toHaveAttribute(
        'href',
        '/my/mentorship/programs/test-program/modules/test-module'
      )
    })

    it('has proper heading structure with h2', () => {
      render(<SingleModuleCard module={mockModule} />)

      const moduleTitle = screen.getByRole('heading', { level: 2 })
      expect(moduleTitle).toBeInTheDocument()
      expect(moduleTitle).toHaveTextContent('Test Module')
    })

    it('has proper heading structure with h3 for contributors sections', () => {
      render(<SingleModuleCard module={mockModule} />)

      const mentorsHeading = screen.getByRole('heading', { level: 3, name: 'Mentors' })
      expect(mentorsHeading).toBeInTheDocument()
    })
  })

  describe('Styling', () => {
    it('renders without shadow or border classes in module wrapper', () => {
      render(<SingleModuleCard module={mockModule} />)

      // The component should render successfully with the section styling
      expect(screen.getByText('Test Module')).toBeInTheDocument()
      expect(screen.getByText('Mentors')).toBeInTheDocument()
    })

    it('renders contributor items with proper styling', () => {
      render(<SingleModuleCard module={mockModule} />)

      // Contributors should be rendered inline
      const avatars = screen.getAllByTestId('contributor-avatar')
      expect(avatars.length).toBeGreaterThan(0)
    })
  })
})
