import { faEye } from '@fortawesome/free-regular-svg-icons'
import { faEdit } from '@fortawesome/free-solid-svg-icons'
import { fireEvent, render, screen } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import React from 'react'
import type { Program } from 'types/mentorship'
import { ProgramStatusEnum } from 'types/mentorship'
import ProgramCard from 'components/ProgramCard'

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: ({ icon, className }: { icon: unknown; className?: string }) => (
    <span
      data-testid={`icon-${icon === faEye ? 'eye' : icon === faEdit ? 'edit' : 'unknown'}`}
      className={className}
    />
  ),
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

describe('ProgramCard', () => {
  const mockOnView = jest.fn()

  const baseMockProgram: Program = {
    id: '1',
    key: 'test-program',
    name: 'Test Program',
    description: 'This is a test program description',
    status: ProgramStatusEnum.PUBLISHED,
    startedAt: '2024-01-01T00:00:00Z',
    endedAt: '2024-12-31T23:59:59Z',
    userRole: 'admin',
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Basic Rendering', () => {
    it('renders program name correctly', () => {
      render(
        <ProgramCard
          isAdmin={false}
          program={baseMockProgram}
          onView={mockOnView}
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
          onView={mockOnView}
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
          onView={mockOnView}
          isAdmin={true}
          accessLevel="admin"
        />
      )

      expect(screen.getByText('admin')).toBeInTheDocument()
    })

    it('calls onView when Preview button is clicked', () => {
      render(
        <ProgramCard
          program={baseMockProgram}
          onView={mockOnView}
          isAdmin={true}
          accessLevel="admin"
        />
      )

      const previewButton = screen.getByText('Preview').closest('button')
      fireEvent.click(previewButton!)

      expect(mockOnView).toHaveBeenCalledWith('test-program')
    })

    it('navigates to edit page when Edit Program is clicked', () => {
      const router = useRouter()

      render(
        <ProgramCard
          program={baseMockProgram}
          onView={mockOnView}
          isAdmin={true}
          accessLevel="admin"
        />
      )

      fireEvent.click(screen.getByTestId('program-actions-button'))
      fireEvent.click(screen.getByText('Edit Program'))

      expect(router.push).toHaveBeenCalledWith('/my/mentorship/programs/test-program/edit')
    })
  })

  describe('Access Level - User', () => {
    it('does not show user role badge when accessLevel is user', () => {
      render(
        <ProgramCard
          isAdmin={false}
          program={baseMockProgram}
          onView={mockOnView}
          accessLevel="user"
        />
      )

      expect(screen.queryByText('admin')).not.toBeInTheDocument()
    })

    it('shows only View Details button for user access', () => {
      render(
        <ProgramCard
          isAdmin={false}
          program={baseMockProgram}
          onView={mockOnView}
          accessLevel="user"
        />
      )

      expect(screen.getByText('View Details')).toBeInTheDocument()
      expect(screen.queryByText('Preview')).not.toBeInTheDocument()
      expect(screen.queryByText('Edit')).not.toBeInTheDocument()
    })

    it('calls onView when View Details button is clicked', () => {
      render(
        <ProgramCard
          isAdmin={false}
          program={baseMockProgram}
          onView={mockOnView}
          accessLevel="user"
        />
      )

      const viewButton = screen.getByText('View Details').closest('button')
      fireEvent.click(viewButton!)

      expect(mockOnView).toHaveBeenCalledWith('test-program')
    })
  })

  describe('User Role Badge Styling', () => {
    it('applies admin role styling', () => {
      const adminProgram = { ...baseMockProgram, userRole: 'admin' }
      render(
        <ProgramCard
          isAdmin={true}
          program={adminProgram}
          onView={mockOnView}
          accessLevel="admin"
        />
      )

      const badge = screen.getByText('admin')
      expect(badge).toHaveClass('bg-blue-100', 'text-blue-800')
    })

    it('applies mentor role styling', () => {
      const mentorProgram = { ...baseMockProgram, userRole: 'mentor' }
      render(
        <ProgramCard
          isAdmin={true}
          program={mentorProgram}
          onView={mockOnView}
          accessLevel="admin"
        />
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
          onView={mockOnView}
          accessLevel="admin"
        />
      )

      const badge = screen.getByText('unknown')
      expect(badge).toHaveClass('bg-gray-100', 'text-gray-800')
    })

    it('applies default styling when userRole is undefined', () => {
      const noRoleProgram = { ...baseMockProgram, userRole: undefined }
      render(
        <ProgramCard
          isAdmin={true}
          program={noRoleProgram}
          onView={mockOnView}
          accessLevel="admin"
        />
      )

      // Should not render badge when userRole is undefined
      expect(screen.queryByText(/bg-/)).not.toBeInTheDocument()
    })
  })

  describe('Description Handling', () => {
    it('renders long descriptions with line-clamp-6 CSS class', () => {
      const longDescription = 'A'.repeat(300) // Long enough to trigger line clamping
      const longDescProgram = { ...baseMockProgram, description: longDescription }

      render(
        <ProgramCard
          isAdmin={false}
          program={longDescProgram}
          onView={mockOnView}
          accessLevel="user"
        />
      )

      // Check that the full description is rendered (CSS handles the visual truncation)
      expect(screen.getByText(longDescription)).toBeInTheDocument()

      // Check that the paragraph has the line-clamp-6 class
      const descriptionElement = screen.getByText(longDescription)
      expect(descriptionElement).toHaveClass('line-clamp-6')
    })

    it('shows full description when short', () => {
      const shortDescription = 'Short description'
      const shortDescProgram = { ...baseMockProgram, description: shortDescription }

      render(
        <ProgramCard
          isAdmin={false}
          program={shortDescProgram}
          onView={mockOnView}
          accessLevel="user"
        />
      )

      expect(screen.getByText('Short description')).toBeInTheDocument()

      // Check that it still has line-clamp-6 class for consistency
      const descriptionElement = screen.getByText('Short description')
      expect(descriptionElement).toHaveClass('line-clamp-6')
    })

    it('shows fallback text when description is empty', () => {
      const emptyDescProgram = { ...baseMockProgram, description: '' }

      render(
        <ProgramCard
          isAdmin={false}
          program={emptyDescProgram}
          onView={mockOnView}
          accessLevel="user"
        />
      )

      expect(screen.getByText('No description available.')).toBeInTheDocument()
    })

    it('shows fallback text when description is undefined', () => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const noDescProgram = { ...baseMockProgram, description: undefined as any }

      render(
        <ProgramCard
          isAdmin={false}
          program={noDescProgram}
          onView={mockOnView}
          accessLevel="user"
        />
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
          onView={mockOnView}
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
          onView={mockOnView}
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
          onView={mockOnView}
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
          onView={mockOnView}
          accessLevel="user"
        />
      )

      expect(screen.getByText('No dates set')).toBeInTheDocument()
    })
  })

  describe('Icons', () => {
    it('renders eye icon for Preview button', () => {
      render(
        <ProgramCard
          program={baseMockProgram}
          isAdmin={true}
          onView={mockOnView}
          accessLevel="admin"
        />
      )

      expect(screen.getByTestId('icon-eye')).toBeInTheDocument()
    })

    it('renders actions button for admin menu', () => {
      render(
        <ProgramCard
          program={baseMockProgram}
          isAdmin={true}
          onView={mockOnView}
          accessLevel="admin"
        />
      )

      expect(screen.getByTestId('program-actions-button')).toBeInTheDocument()
    })

    it('renders eye icon for View Details button', () => {
      render(
        <ProgramCard
          isAdmin={false}
          program={baseMockProgram}
          onView={mockOnView}
          accessLevel="user"
        />
      )

      expect(screen.getByTestId('icon-eye')).toBeInTheDocument()
    })
  })

  describe('Edge Cases', () => {
    it('shows Edit Program in actions menu for admin access', () => {
      render(
        <ProgramCard
          isAdmin={true}
          program={baseMockProgram}
          onView={mockOnView}
          accessLevel="admin"
        />
      )

      fireEvent.click(screen.getByTestId('program-actions-button'))
      expect(screen.getByText('Edit Program')).toBeInTheDocument()
    })

    it('handles program with minimal data', () => {
      const minimalProgram: Program = {
        id: '2',
        key: 'minimal',
        name: 'Minimal Program',
        description: '',
        status: ProgramStatusEnum.DRAFT,
        startedAt: '',
        endedAt: '',
      }

      render(
        <ProgramCard
          isAdmin={false}
          program={minimalProgram}
          onView={mockOnView}
          accessLevel="user"
        />
      )

      expect(screen.getByText('Minimal Program')).toBeInTheDocument()
      expect(screen.getByText('No description available.')).toBeInTheDocument()
      expect(screen.getByText('No dates set')).toBeInTheDocument()
    })
  })
})
