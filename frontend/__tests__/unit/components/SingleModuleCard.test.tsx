import { faUsers } from '@fortawesome/free-solid-svg-icons'
import { fireEvent, screen, waitFor } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import React from 'react'
import { render } from 'wrappers/testUtil'
import { ExperienceLevelEnum, ProgramStatusEnum } from 'types/__generated__/graphql'
import type { ExtendedSession } from 'types/auth'
import type { Module } from 'types/mentorship'
import SingleModuleCard from 'components/SingleModuleCard'

// Mock dependencies
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
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
}

const mockAdmins = [{ login: 'admin1' }, { login: 'admin2' }]

const mockSessionData: ExtendedSession = {
  user: {
    login: 'admin1',
    isLeader: true,
    email: 'admin@example.com',
    image: 'https://example.com/admin-avatar.jpg',
  },
  expires: '2024-12-31T23:59:59Z',
}

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
      expect(screen.getByTestId('icon-ellipsis')).toBeInTheDocument()
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
      expect(moduleLink).toHaveAttribute('href', '//modules/test-module')
      expect(moduleLink).toHaveAttribute('target', '_blank')
      expect(moduleLink).toHaveAttribute('rel', 'noopener noreferrer')
    })
  })

  describe('Dropdown Menu', () => {
    it('opens dropdown when ellipsis button is clicked', () => {
      render(<SingleModuleCard module={mockModule} />)

      const ellipsisButton = screen.getByRole('button')
      fireEvent.click(ellipsisButton)

      expect(screen.getByText('View Module')).toBeInTheDocument()
    })

    it('closes dropdown when clicking outside', async () => {
      render(<SingleModuleCard module={mockModule} />)

      const ellipsisButton = screen.getByRole('button')
      fireEvent.click(ellipsisButton)

      expect(screen.getByText('View Module')).toBeInTheDocument()

      // Click outside the dropdown
      fireEvent.mouseDown(document.body)

      await waitFor(() => {
        expect(screen.queryByText('View Module')).not.toBeInTheDocument()
      })
    })

    it('navigates to view module when View Module is clicked', () => {
      render(<SingleModuleCard module={mockModule} />)

      const ellipsisButton = screen.getByRole('button')
      fireEvent.click(ellipsisButton)

      const viewButton = screen.getByText('View Module')
      fireEvent.click(viewButton)

      expect(mockPush).toHaveBeenCalledWith('//modules/test-module')
    })

    it('shows only View Module option for non-admin users', () => {
      render(
        <SingleModuleCard
          module={mockModule}
          showEdit={true}
          accessLevel="user"
          admins={mockAdmins}
        />
      )

      const ellipsisButton = screen.getByRole('button')
      fireEvent.click(ellipsisButton)

      expect(screen.getByText('View Module')).toBeInTheDocument()
      expect(screen.queryByText('Edit Module')).not.toBeInTheDocument()
      expect(screen.queryByText('Create Module')).not.toBeInTheDocument()
    })
  })

  describe('Admin Functionality', () => {
    beforeEach(() => {
      mockUseSession.mockReturnValue({
        data: mockSessionData,
        status: 'authenticated',
        update: jest.fn(),
      })
    })

    it('shows Edit Module option for admin users when showEdit is true', () => {
      render(
        <SingleModuleCard
          module={mockModule}
          showEdit={true}
          accessLevel="admin"
          admins={mockAdmins}
        />
      )

      const ellipsisButton = screen.getByRole('button')
      fireEvent.click(ellipsisButton)

      expect(screen.getByText('View Module')).toBeInTheDocument()
      expect(screen.getByText('Edit Module')).toBeInTheDocument()
      expect(screen.getByText('Create Module')).toBeInTheDocument()
    })

    it('does not show Edit Module option when showEdit is false', () => {
      render(
        <SingleModuleCard
          module={mockModule}
          showEdit={false}
          accessLevel="admin"
          admins={mockAdmins}
        />
      )

      const ellipsisButton = screen.getByRole('button')
      fireEvent.click(ellipsisButton)

      expect(screen.getByText('View Module')).toBeInTheDocument()
      expect(screen.queryByText('Edit Module')).not.toBeInTheDocument()
      expect(screen.getByText('Create Module')).toBeInTheDocument()
    })

    it('navigates to edit module when Edit Module is clicked', () => {
      render(
        <SingleModuleCard
          module={mockModule}
          showEdit={true}
          accessLevel="admin"
          admins={mockAdmins}
        />
      )

      const ellipsisButton = screen.getByRole('button')
      fireEvent.click(ellipsisButton)

      const editButton = screen.getByText('Edit Module')
      fireEvent.click(editButton)

      expect(mockPush).toHaveBeenCalledWith('//modules/test-module/edit')
    })

    it('navigates to create module when Create Module is clicked', () => {
      render(
        <SingleModuleCard
          module={mockModule}
          showEdit={true}
          accessLevel="admin"
          admins={mockAdmins}
        />
      )

      const ellipsisButton = screen.getByRole('button')
      fireEvent.click(ellipsisButton)

      const createButton = screen.getByText('Create Module')
      fireEvent.click(createButton)

      expect(mockPush).toHaveBeenCalledWith('//modules/create')
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

    it('handles undefined admins array', () => {
      render(<SingleModuleCard module={mockModule} showEdit={true} accessLevel="admin" />)

      const ellipsisButton = screen.getByRole('button')
      fireEvent.click(ellipsisButton)

      expect(screen.getByText('View Module')).toBeInTheDocument()
      expect(screen.queryByText('Edit Module')).not.toBeInTheDocument()
    })

    it('handles null session data', () => {
      mockUseSession.mockReturnValue({
        data: null,
        status: 'unauthenticated',
        update: jest.fn(),
      })

      render(
        <SingleModuleCard
          module={mockModule}
          showEdit={true}
          accessLevel="admin"
          admins={mockAdmins}
        />
      )

      const ellipsisButton = screen.getByRole('button')
      fireEvent.click(ellipsisButton)

      expect(screen.getByText('View Module')).toBeInTheDocument()
      expect(screen.queryByText('Edit Module')).not.toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('has proper button roles and interactions', () => {
      render(<SingleModuleCard module={mockModule} />)

      const ellipsisButton = screen.getByRole('button')
      expect(ellipsisButton).toBeInTheDocument()

      fireEvent.click(ellipsisButton)

      const viewButton = screen.getByText('View Module')
      expect(viewButton.closest('button')).toBeInTheDocument()
    })

    it('supports keyboard navigation', () => {
      render(<SingleModuleCard module={mockModule} />)

      const ellipsisButton = screen.getByRole('button')

      // Focus the button
      ellipsisButton.focus()
      expect(ellipsisButton).toHaveFocus()

      // Press Enter to open dropdown
      fireEvent.keyDown(ellipsisButton, { key: 'Enter', code: 'Enter' })
      fireEvent.click(ellipsisButton) // Simulate the click that would happen

      expect(screen.getByText('View Module')).toBeInTheDocument()
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
