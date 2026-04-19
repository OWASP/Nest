import { render, screen, fireEvent } from '@testing-library/react'
import type { Session } from 'next-auth'
import '@testing-library/jest-dom'
import CardDetailsHeader from 'components/CardDetailsPage/CardDetailsHeader'
import type { CardDetailsHeaderProps } from 'components/CardDetailsPage/CardDetailsHeader'

jest.mock('next-auth/react', () => ({
  useSession: jest.fn(() => ({
    data: null,
    status: 'unauthenticated',
  })),
}))

// eslint-disable-next-line @typescript-eslint/no-require-imports
const mockUseSession = jest.mocked(require('next-auth/react').useSession)

jest.mock('utils/scrollToAnchor', () => ({
  scrollToAnchor: jest.fn(),
}))

jest.mock('utils/env.client', () => ({
  IS_PROJECT_HEALTH_ENABLED: true,
}))

jest.mock('components/EntityActions', () => ({
  __esModule: true,
  default: ({
    type,
    programKey,
    moduleKey,
  }: {
    type: string
    programKey?: string
    moduleKey?: string
  }) => (
    <div data-testid="entity-actions">
      EntityActions: type={type}, programKey={programKey}, moduleKey={moduleKey}
    </div>
  ),
}))

jest.mock('components/StatusBadge', () => ({
  __esModule: true,
  default: ({ status }: { status: string }) => (
    <span data-testid={`status-badge-${status}`}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  ),
}))

jest.mock('components/MetricsScoreCircle', () => ({
  __esModule: true,
  default: ({
    score,
    clickable,
    onClick,
  }: {
    score: number
    clickable?: boolean
    onClick?: () => void
  }) =>
    clickable ? (
      <button data-testid="metrics-score-circle" onClick={onClick}>
        Score: {score}
      </button>
    ) : (
      <div data-testid="metrics-score-circle">Score: {score}</div>
    ),
}))

describe('CardDetailsHeader', () => {
  const defaultProps: CardDetailsHeaderProps = {
    title: 'Test Title',
  }

  it('renders title correctly', () => {
    render(<CardDetailsHeader {...defaultProps} />)
    expect(screen.getByText('Test Title')).toBeInTheDocument()
  })

  it('renders description when provided', () => {
    render(<CardDetailsHeader {...defaultProps} description="Test description" />)
    expect(screen.getByText('Test description')).toBeInTheDocument()
  })

  it('renders inactive badge when isActive is false', () => {
    render(<CardDetailsHeader {...defaultProps} isActive={false} />)
    expect(screen.getByTestId('status-badge-inactive')).toBeInTheDocument()
  })

  it('renders archived badge when isArchived is true', () => {
    render(<CardDetailsHeader {...defaultProps} isArchived={true} showArchivedBadge={true} />)
    expect(screen.getByTestId('status-badge-archived')).toBeInTheDocument()
  })

  it('does not render archived badge when showArchivedBadge is false', () => {
    render(<CardDetailsHeader {...defaultProps} isArchived={true} showArchivedBadge={false} />)
    expect(screen.queryByTestId('status-badge-archived')).not.toBeInTheDocument()
  })

  it('renders health metrics when conditions are met', () => {
    const healthMetricsData = [{ score: 85 }]
    render(
      <CardDetailsHeader
        {...defaultProps}
        healthMetricsData={healthMetricsData}
        showHealthMetrics={true}
      />
    )
    expect(screen.getByTestId('metrics-score-circle')).toBeInTheDocument()
  })

  it('does not render health metrics when score is undefined', () => {
    const healthMetricsData = [{ score: undefined }]
    render(
      <CardDetailsHeader
        {...defaultProps}
        healthMetricsData={healthMetricsData}
        showHealthMetrics={true}
      />
    )
    expect(screen.queryByTestId('metrics-score-circle')).not.toBeInTheDocument()
  })

  it('calls scrollToAnchor when health metrics button is clicked', () => {
    const { scrollToAnchor } = jest.requireMock('utils/scrollToAnchor')
    const healthMetricsData = [{ score: 85 }]

    render(
      <CardDetailsHeader
        {...defaultProps}
        healthMetricsData={healthMetricsData}
        showHealthMetrics={true}
      />
    )

    const button = screen.getByTestId('metrics-score-circle')
    fireEvent.click(button)

    expect(scrollToAnchor).toHaveBeenCalledWith('issues-trend')
  })

  describe('Module actions with admin and mentor logic', () => {
    afterEach(() => {
      mockUseSession.mockReturnValue({
        data: null,
        status: 'unauthenticated',
      } as { data: Session | null; status: string })
    })

    it('renders entity actions when showModuleActions is true and user is admin', () => {
      mockUseSession.mockReturnValueOnce({
        data: {
          user: {
            login: 'admin_user',
          },
        },
        status: 'authenticated',
      } as { data: Record<string, unknown>; status: string })

      const admins = [{ login: 'admin_user' }]

      render(
        <CardDetailsHeader
          {...defaultProps}
          programKey="test-program"
          moduleKey="test-module"
          accessLevel="admin"
          admins={admins}
          showModuleActions={true}
        />
      )

      expect(screen.getByTestId('entity-actions')).toBeInTheDocument()
      expect(screen.getByText(/EntityActions.*type=module/)).toBeInTheDocument()
    })

    it('renders entity actions when showModuleActions is true and user is mentor', () => {
      mockUseSession.mockReturnValueOnce({
        data: {
          user: {
            login: 'mentor_user',
          },
        },
        status: 'authenticated',
      } as { data: Record<string, unknown>; status: string })

      const mentors = [{ login: 'mentor_user' }]

      render(
        <CardDetailsHeader
          {...defaultProps}
          programKey="test-program"
          moduleKey="test-module"
          mentors={mentors}
          showModuleActions={true}
        />
      )

      expect(screen.getByTestId('entity-actions')).toBeInTheDocument()
    })

    it('does not render entity actions when showModuleActions is true but user is neither admin nor mentor', () => {
      mockUseSession.mockReturnValueOnce({
        data: {
          user: {
            login: 'regular_user',
          },
        },
        status: 'authenticated',
      } as { data: Record<string, unknown>; status: string })

      const admins = [{ login: 'admin_user' }]
      const mentors = [{ login: 'mentor_user' }]

      render(
        <CardDetailsHeader
          {...defaultProps}
          programKey="test-program"
          moduleKey="test-module"
          accessLevel="viewer"
          admins={admins}
          mentors={mentors}
          showModuleActions={true}
        />
      )

      expect(screen.queryByTestId('entity-actions')).not.toBeInTheDocument()
    })

    it('does not render entity actions when showModuleActions is true but programKey is missing', () => {
      mockUseSession.mockReturnValueOnce({
        data: {
          user: {
            login: 'admin_user',
          },
        },
        status: 'authenticated',
      } as { data: Record<string, unknown>; status: string })

      const admins = [{ login: 'admin_user' }]

      render(
        <CardDetailsHeader
          {...defaultProps}
          moduleKey="test-module"
          accessLevel="admin"
          admins={admins}
          showModuleActions={true}
        />
      )

      expect(screen.queryByTestId('entity-actions')).not.toBeInTheDocument()
    })

    it('does not render entity actions when showModuleActions is true but moduleKey is missing', () => {
      mockUseSession.mockReturnValueOnce({
        data: {
          user: {
            login: 'admin_user',
          },
        },
        status: 'authenticated',
      } as { data: Record<string, unknown>; status: string })

      const admins = [{ login: 'admin_user' }]

      render(
        <CardDetailsHeader
          {...defaultProps}
          programKey="test-program"
          moduleKey={undefined}
          accessLevel="admin"
          admins={admins}
          showModuleActions={true}
        />
      )

      expect(screen.queryByTestId('entity-actions')).not.toBeInTheDocument()
    })

    it('renders entity actions when user is both admin and mentor', () => {
      mockUseSession.mockReturnValueOnce({
        data: {
          user: {
            login: 'admin_mentor_user',
          },
        },
        status: 'authenticated',
      } as { data: Record<string, unknown>; status: string })

      const admins = [{ login: 'admin_mentor_user' }]
      const mentors = [{ login: 'admin_mentor_user' }]

      render(
        <CardDetailsHeader
          {...defaultProps}
          programKey="test-program"
          moduleKey="test-module"
          accessLevel="admin"
          admins={admins}
          mentors={mentors}
          showModuleActions={true}
        />
      )

      expect(screen.getByTestId('entity-actions')).toBeInTheDocument()
    })
  })

  describe('Program actions', () => {
    it('renders program EntityActions when showProgramActions, canUpdateStatus, and programKey are all set', () => {
      render(
        <CardDetailsHeader
          {...defaultProps}
          showProgramActions={true}
          canUpdateStatus={true}
          programKey="my-program"
          status="active"
        />
      )
      const actions = screen.getByTestId('entity-actions')
      expect(actions).toBeInTheDocument()
      expect(actions).toHaveTextContent('type=program')
      expect(actions).toHaveTextContent('programKey=my-program')
    })

    it('does not render program EntityActions when canUpdateStatus is false', () => {
      render(
        <CardDetailsHeader
          {...defaultProps}
          showProgramActions={true}
          canUpdateStatus={false}
          programKey="my-program"
        />
      )
      expect(screen.queryByTestId('entity-actions')).not.toBeInTheDocument()
    })

    it('does not render program EntityActions when programKey is missing', () => {
      render(
        <CardDetailsHeader {...defaultProps} showProgramActions={true} canUpdateStatus={true} />
      )
      expect(screen.queryByTestId('entity-actions')).not.toBeInTheDocument()
    })

    it('does not render program EntityActions when showProgramActions is false', () => {
      render(
        <CardDetailsHeader
          {...defaultProps}
          showProgramActions={false}
          canUpdateStatus={true}
          programKey="my-program"
        />
      )
      expect(screen.queryByTestId('entity-actions')).not.toBeInTheDocument()
    })
  })

  describe('Edge cases', () => {
    it('renders empty title when title prop is not provided', () => {
      render(<CardDetailsHeader />)
      expect(document.querySelector('h1')).toBeInTheDocument()
      expect(document.querySelector('h1')?.textContent).toBe('')
    })

    it('does not render description paragraph when description is not provided', () => {
      render(<CardDetailsHeader {...defaultProps} />)
      expect(screen.queryByText('Test description')).not.toBeInTheDocument()
    })

    it('does not render health metrics when healthMetricsData is an empty array', () => {
      render(
        <CardDetailsHeader {...defaultProps} showHealthMetrics={true} healthMetricsData={[]} />
      )
      expect(screen.queryByTestId('metrics-score-circle')).not.toBeInTheDocument()
    })

    it('does not render health metrics when showHealthMetrics is false', () => {
      render(
        <CardDetailsHeader
          {...defaultProps}
          showHealthMetrics={false}
          healthMetricsData={[{ score: 90 }]}
        />
      )
      expect(screen.queryByTestId('metrics-score-circle')).not.toBeInTheDocument()
    })

    it('does not render module EntityActions when showModuleActions is false', () => {
      render(
        <CardDetailsHeader
          {...defaultProps}
          showModuleActions={false}
          programKey="test-program"
          moduleKey="test-module"
          accessLevel="admin"
          admins={[{ login: 'admin_user' }]}
        />
      )
      expect(screen.queryByTestId('entity-actions')).not.toBeInTheDocument()
    })

    it('renders active component without inactive badge when isActive is true (default)', () => {
      render(<CardDetailsHeader {...defaultProps} isActive={true} />)
      expect(screen.queryByTestId('status-badge-inactive')).not.toBeInTheDocument()
    })

    it('does not render archived badge when isArchived is false (default)', () => {
      render(<CardDetailsHeader {...defaultProps} showArchivedBadge={true} isArchived={false} />)
      expect(screen.queryByTestId('status-badge-archived')).not.toBeInTheDocument()
    })
  })
})
