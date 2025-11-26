import { faEye } from '@fortawesome/free-regular-svg-icons'
import { faEdit } from '@fortawesome/free-solid-svg-icons'
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import React from 'react'
import { ProgramStatusEnum } from 'types/__generated__/graphql'
import type { Program } from 'types/mentorship'
import ProgramCard from 'components/ProgramCard'

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: ({ icon, className }: { icon: unknown; className?: string }) => {
    let iconName = 'unknown'

    if (icon === faEye) {
      iconName = 'eye'
    } else if (icon === faEdit) {
      iconName = 'edit'
    }

    return <span data-testid={`icon-${iconName}`} className={className} />
  },
}))

jest.mock('hooks/useUpdateProgramStatus', () => ({
  useUpdateProgramStatus: () => ({ updateProgramStatus: jest.fn() }),
}))

jest.mock('hooks/useUpdateProgramStatus', () => ({
  useUpdateProgramStatus: () => ({ updateProgramStatus: jest.fn() }),
}))

jest.mock('components/ActionButton', () => ({
  __esModule: true,
  default: ({ children, onClick }: { children: React.ReactNode; onClick: () => void }) => (
    <button onClick={onClick} data-testid="action-button">
      {children}
    </button>
  ),
}))

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({ children, content }: { children: React.ReactNode; content: string }) => (
    <div data-testid="tooltip" title={content}>
      {children}
    </div>
  ),
}))

jest.mock('components/EntityActions', () => jest.requireActual('components/EntityActions'))

jest.mock('next/link', () => {
  return ({ children, href }: { children: React.ReactNode; href: string }) => {
    return <a href={href}>{children}</a>
  }
})

describe('ProgramCard', () => {
  const mockPush = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    ;(useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
      back: jest.fn(),
      forward: jest.fn(),
      refresh: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
    })
  })

  const baseMockProgram: Program = {
    id: '1',
    key: 'test-program',
    name: 'Test Program',
    description: 'This is a test program description',
    status: ProgramStatusEnum.Published,
    startedAt: '2024-01-01T00:00:00Z',
    endedAt: '2024-12-31T23:59:59Z',
    userRole: 'admin',
  }

  describe('Basic Rendering', () => {
    it('renders program name correctly', () => {
      render(
        <ProgramCard
          isAdmin={false}
          program={baseMockProgram}
          href="/test/path"
          accessLevel="user"
        />
      )

      expect(screen.getByText('Test Program')).toBeInTheDocument()
    })

    it('renders program description correctly', () => {
      render(
        <ProgramCard
          isAdmin={false}
          program={baseMockProgram}
          href="/test/path"
          accessLevel="user"
        />
      )

      expect(screen.getByText('This is a test program description')).toBeInTheDocument()
    })
  })

  describe('Access Level - Admin', () => {
    it('shows user role badge when accessLevel is admin', () => {
      render(
        <ProgramCard
          program={baseMockProgram}
          href="/test/path"
          isAdmin={true}
          accessLevel="admin"
        />
      )

      expect(screen.getByText('admin')).toBeInTheDocument()
    })

    it('renders Link with correct href', () => {
      const { container } = render(
        <ProgramCard
          program={baseMockProgram}
          href="/my/mentorship/programs/test-program"
          isAdmin={true}
          accessLevel="admin"
        />
      )

      const link = container.querySelector('a[href="/my/mentorship/programs/test-program"]')
      expect(link).toBeInTheDocument()
    })

    it('navigates to edit page when Edit is clicked', async () => {
      render(
        <ProgramCard
          program={baseMockProgram}
          href="/my/mentorship/programs/test-program"
          isAdmin={true}
          accessLevel="admin"
        />
      )

      const actionsButton = screen.getByTestId('program-actions-button')

      await act(async () => {
        fireEvent.click(actionsButton)
      })

      const editButton = await waitFor(() => {
        return screen.getByText('Edit')
      })

      await act(async () => {
        fireEvent.click(editButton)
      })

      expect(mockPush).toHaveBeenCalledWith('/my/mentorship/programs/test-program/edit')
    })
  })

  describe('Access Level - User', () => {
    it('does not show user role badge when accessLevel is user', () => {
      render(
        <ProgramCard
          isAdmin={false}
          program={baseMockProgram}
          href="/test/path"
          accessLevel="user"
        />
      )

      expect(screen.queryByText('admin')).not.toBeInTheDocument()
    })

    it('shows clickable card for user access', () => {
      render(
        <ProgramCard
          isAdmin={false}
          program={baseMockProgram}
          href="/test/path"
          accessLevel="user"
        />
      )

      const link = document.querySelector('a[href="/test/path"]')
      expect(link).toBeInTheDocument()
      expect(screen.queryByText('Preview')).not.toBeInTheDocument()
      expect(screen.queryByText('Edit')).not.toBeInTheDocument()
      expect(screen.queryByText('View Details')).not.toBeInTheDocument()
    })

    it('renders Link with correct href', () => {
      const { container } = render(
        <ProgramCard
          isAdmin={false}
          program={baseMockProgram}
          href="/mentorship/programs/test-program"
          accessLevel="user"
        />
      )

      const link = container.querySelector('a[href="/mentorship/programs/test-program"]')
      expect(link).toBeInTheDocument()
    })
  })

  describe('User Role Badge Styling', () => {
    it('applies admin role styling', () => {
      const adminProgram = { ...baseMockProgram, userRole: 'admin' }
      render(
        <ProgramCard isAdmin={true} program={adminProgram} href="/test/path" accessLevel="admin" />
      )

      const badge = screen.getByText('admin')
      expect(badge).toHaveClass('bg-blue-100', 'text-blue-800')
    })

    it('applies mentor role styling', () => {
      const mentorProgram = { ...baseMockProgram, userRole: 'mentor' }
      render(
        <ProgramCard isAdmin={true} program={mentorProgram} href="/test/path" accessLevel="admin" />
      )

      const badge = screen.getByText('mentor')
      expect(badge).toHaveClass('bg-green-100', 'text-green-800')
    })

    it('applies default role styling for unknown role', () => {
      const unknownRoleProgram = { ...baseMockProgram, userRole: 'unknown' }
      render(
        <ProgramCard
          isAdmin={true}
          program={unknownRoleProgram}
          href="/test/path"
          accessLevel="admin"
        />
      )

      const badge = screen.getByText('unknown')
      expect(badge).toHaveClass('bg-gray-100', 'text-gray-800')
    })

    it('applies default styling when userRole is undefined', () => {
      const noRoleProgram = { ...baseMockProgram, userRole: undefined }
      render(
        <ProgramCard isAdmin={true} program={noRoleProgram} href="/test/path" accessLevel="admin" />
      )

      // Should not render badge when userRole is undefined
      expect(screen.queryByText(/bg-/)).not.toBeInTheDocument()
    })
  })

  describe('Description Handling', () => {
    it('renders long descriptions with line-clamp-8 CSS class', () => {
      const longDescription = 'A'.repeat(300) // Long enough to trigger line clamping
      const longDescProgram = { ...baseMockProgram, description: longDescription }

      render(
        <ProgramCard
          isAdmin={false}
          program={longDescProgram}
          href="/test/path"
          accessLevel="user"
        />
      )

      expect(screen.getByText(longDescription)).toBeInTheDocument()
      expect(screen.getByText(longDescription)).toBeInTheDocument()
      const descriptionElement = screen.getByText(longDescription)
      expect(descriptionElement).toHaveClass('line-clamp-8')
    })

    it('shows full description when short', () => {
      const shortDescription = 'Short description'
      const shortDescProgram = { ...baseMockProgram, description: shortDescription }

      render(
        <ProgramCard
          isAdmin={false}
          program={shortDescProgram}
          href="/test/path"
          accessLevel="user"
        />
      )

      expect(screen.getByText('Short description')).toBeInTheDocument()

      const descriptionElement = screen.getByText('Short description')
      expect(descriptionElement).toHaveClass('line-clamp-8')
    })

    it('shows fallback text when description is empty', () => {
      const emptyDescProgram = { ...baseMockProgram, description: '' }

      render(
        <ProgramCard
          isAdmin={false}
          program={emptyDescProgram}
          href="/test/path"
          accessLevel="user"
        />
      )

      expect(screen.getByText('No description available.')).toBeInTheDocument()
    })

    it('shows fallback text when description is undefined', () => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const noDescProgram = { ...baseMockProgram, description: undefined as any }

      render(
        <ProgramCard isAdmin={false} program={noDescProgram} href="/test/path" accessLevel="user" />
      )

      expect(screen.getByText('No description available.')).toBeInTheDocument()
    })
  })

  describe('Date Formatting', () => {
    it('shows date range when both startedAt and endedAt are provided', () => {
      render(
        <ProgramCard
          isAdmin={false}
          program={baseMockProgram}
          href="/test/path"
          accessLevel="user"
        />
      )

      expect(
        screen.getByText((t) => t.includes('Jan 1, 2024') && t.includes('Dec 31, 2024'))
      ).toBeInTheDocument()
    })

    it('shows only start date when endedAt is missing', () => {
      const startOnlyProgram = { ...baseMockProgram, endedAt: '' }
      render(
        <ProgramCard
          isAdmin={false}
          program={startOnlyProgram}
          href="/test/path"
          accessLevel="user"
        />
      )

      expect(screen.getByText('Started: Jan 1, 2024')).toBeInTheDocument()
    })

    it('shows fallback text when both dates are missing', () => {
      const noDatesProgram = { ...baseMockProgram, startedAt: '', endedAt: '' }

      render(
        <ProgramCard
          isAdmin={false}
          program={noDatesProgram}
          href="/test/path"
          accessLevel="user"
        />
      )

      expect(screen.getByText('No dates set')).toBeInTheDocument()
    })

    it('shows fallback text when startedAt is missing but endedAt exists', () => {
      const endOnlyProgram = { ...baseMockProgram, startedAt: '' }

      render(
        <ProgramCard
          isAdmin={false}
          program={endOnlyProgram}
          href="/test/path"
          accessLevel="user"
        />
      )

      expect(screen.getByText('No dates set')).toBeInTheDocument()
    })
  })

  describe('Icons', () => {
    it('renders actions button for admin menu', () => {
      render(
        <ProgramCard
          program={baseMockProgram}
          isAdmin={true}
          href="/test/path"
          accessLevel="admin"
        />
      )

      expect(screen.getByTestId('program-actions-button')).toBeInTheDocument()
    })
  })

  describe('Edge Cases', () => {
    it('shows actions button for admin access', () => {
      render(
        <ProgramCard
          isAdmin={true}
          program={baseMockProgram}
          href="/test/path"
          accessLevel="admin"
        />
      )

      expect(screen.getByTestId('program-actions-button')).toBeInTheDocument()
    })

    it('handles program with minimal data', () => {
      const minimalProgram: Program = {
        id: '2',
        key: 'minimal',
        name: 'Minimal Program',
        description: '',
        status: ProgramStatusEnum.Draft,
        startedAt: '',
        endedAt: '',
      }

      render(
        <ProgramCard
          isAdmin={false}
          program={minimalProgram}
          href="/test/path"
          accessLevel="user"
        />
      )

      expect(screen.getByText('Minimal Program')).toBeInTheDocument()
      expect(screen.getByText('No description available.')).toBeInTheDocument()
      expect(screen.getByText('No dates set')).toBeInTheDocument()
    })
  })
})
