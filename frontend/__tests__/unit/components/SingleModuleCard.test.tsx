import { faUsers } from '@fortawesome/free-solid-svg-icons'
import { screen } from '@testing-library/react'
import { usePathname, useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import React from 'react'
import { render } from 'wrappers/testUtil'
import { ExperienceLevelEnum, ProgramStatusEnum } from 'types/__generated__/graphql'
import type { Module } from 'types/mentorship'
import SingleModuleCard from 'components/SingleModuleCard'

// Mock dependencies
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  usePathname: jest.fn(),
}))

jest.mock('next-auth/react', () => ({
  useSession: jest.fn(),
}))

jest.mock('next/link', () => ({
  __esModule: true,
  default: ({
    children,
    href,
    target,
    rel,
    className,
    ...props
  }: {
    children: React.ReactNode
    href: string
    target?: string
    rel?: string
    className?: string
    [key: string]: unknown
  }) => (
    <a
      href={href}
      target={target}
      rel={rel}
      className={className}
      {...props}
      data-testid="module-link"
    >
      {children}
    </a>
  ),
}))

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: ({ icon, className }: { icon: unknown; className?: string }) => (
    <span data-testid={`icon-${icon === faUsers ? 'users' : 'ellipsis'}`} className={className} />
  ),
}))

jest.mock('utils/dateFormatter', () => ({
  formatDate: jest.fn((date: string) => new Date(date).toLocaleDateString()),
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

jest.mock('components/TopContributorsList', () => ({
  __esModule: true,
  default: ({ contributors, label }: { contributors: unknown[]; label: string }) => (
    <div data-testid="top-contributors-list">
      <span>
        {label}: {contributors.length} contributors
      </span>
    </div>
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
      name: 'user1',
      login: 'user1',
      avatarUrl: 'https://example.com/avatar1.jpg',
    },
    {
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
      expect(screen.getByTestId('icon-users')).toBeInTheDocument()
    })

    it('renders module details correctly', () => {
      render(<SingleModuleCard module={mockModule} />)

      expect(screen.getByText('Experience Level:')).toBeInTheDocument()
      expect(screen.getByText('Intermediate')).toBeInTheDocument()
      expect(screen.getByText('Start Date:')).toBeInTheDocument()
      expect(screen.getByText('End Date:')).toBeInTheDocument()
      expect(screen.getByText('Duration:')).toBeInTheDocument()
    })

    it('renders mentors list when mentors exist', () => {
      render(<SingleModuleCard module={mockModule} />)

      expect(screen.getByTestId('top-contributors-list')).toBeInTheDocument()
      expect(screen.getByText('Mentors: 2 contributors')).toBeInTheDocument()
    })

    it('does not render mentors list when no mentors', () => {
      const moduleWithoutMentors = { ...mockModule, mentors: [] }
      render(<SingleModuleCard module={moduleWithoutMentors} />)

      expect(screen.queryByTestId('top-contributors-list')).not.toBeInTheDocument()
    })

    it('renders module link with correct href', () => {
      render(<SingleModuleCard module={mockModule} />)

      const moduleLink = screen.getByTestId('module-link')
      expect(moduleLink).toHaveAttribute(
        'href',
        '/my/mentorship/programs/test-program/modules/test-module'
      )
      expect(moduleLink).toHaveAttribute('target', '_blank')
      expect(moduleLink).toHaveAttribute('rel', 'noopener noreferrer')
    })
  })

  describe('Simplified Interface', () => {
    it('focuses on content display only', () => {
      render(<SingleModuleCard module={mockModule} />)

      // Should display core content
      expect(screen.getByText('Test Module')).toBeInTheDocument()
      expect(screen.getByText('This is a test module description')).toBeInTheDocument()
      expect(screen.getByText('Experience Level:')).toBeInTheDocument()

      // Should have clickable title for navigation
      const moduleLink = screen.getByTestId('module-link')
      expect(moduleLink).toHaveAttribute(
        'href',
        '/my/mentorship/programs/test-program/modules/test-module'
      )
    })
  })

  describe('Props Handling', () => {
    it('renders correctly with minimal props', () => {
      render(<SingleModuleCard module={mockModule} />)

      expect(screen.getByText('Test Module')).toBeInTheDocument()
      expect(screen.getByText('This is a test module description')).toBeInTheDocument()
    })

    it('ignores admin-related props since menu is removed', () => {
      // These props are now ignored but should not cause errors
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
      expect(screen.queryByTestId('top-contributors-list')).not.toBeInTheDocument()
    })

    it('handles undefined admins array gracefully', () => {
      render(<SingleModuleCard module={mockModule} accessLevel="admin" />)

      // Should render without errors even with admin props
      expect(screen.getByText('Test Module')).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('has accessible link for module navigation', () => {
      render(<SingleModuleCard module={mockModule} />)

      const moduleLink = screen.getByTestId('module-link')
      expect(moduleLink).toBeInTheDocument()
      expect(moduleLink).toHaveAttribute(
        'href',
        '/my/mentorship/programs/test-program/modules/test-module'
      )
      expect(moduleLink).toHaveAttribute('target', '_blank')
      expect(moduleLink).toHaveAttribute('rel', 'noopener noreferrer')
    })

    it('has proper heading structure', () => {
      render(<SingleModuleCard module={mockModule} />)

      const moduleTitle = screen.getByRole('heading', { level: 1 })
      expect(moduleTitle).toBeInTheDocument()
      expect(moduleTitle).toHaveTextContent('Test Module')
    })
  })

  describe('Responsive Design', () => {
    it('applies responsive classes correctly', () => {
      render(<SingleModuleCard module={mockModule} />)

      const moduleTitle = screen.getByText('Test Module')
      expect(moduleTitle).toHaveClass('sm:break-normal', 'sm:text-lg', 'lg:text-2xl')
    })
  })
})
