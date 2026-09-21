import { useMutation, useQuery } from '@apollo/client/react'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import { render } from 'wrappers/testUtil'
import SnapshotFeedback from 'components/SnapshotFeedback'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
  useMutation: jest.fn(),
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

jest.mock('next-auth/react', () => ({
  signIn: jest.fn(),
}))

jest.mock('hooks/useDjangoSession', () => ({
  useDjangoSession: jest.fn(),
}))

const feedbackEntry = {
  id: 'feedback-1',
  avatarUrl: 'https://avatars.githubusercontent.com/u/1?v=4',
  comment: 'Really useful digest.',
  createdAt: '2025-01-15T10:00:00.000Z',
  login: 'alice',
  rating: 5,
  updatedAt: '2025-01-15T10:00:00.000Z',
  username: 'alice',
}

const setupMocks = (session: string, myFeedback: typeof feedbackEntry | null) => {
  ;(useDjangoSession as jest.Mock).mockReturnValue({
    isSyncing: false,
    session: { user: { name: 'testuser' } },
    status: session,
  })
  ;(useQuery as unknown as jest.Mock).mockReturnValue({
    data: {
      snapshot: {
        id: 'snapshot-1',
        averageRating: 4.5,
        feedbackCount: 2,
        myFeedback,
        feedback: [feedbackEntry],
      },
    },
    loading: false,
    error: null,
    refetch: jest.fn(),
  })
  ;(useMutation as unknown as jest.Mock).mockReturnValue([jest.fn(), { loading: false }])
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('SnapshotFeedback a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    jest.clearAllMocks()
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })

  it('should not have any accessibility violations when rating for the first time', async () => {
    setupMocks('authenticated', null)

    const { container } = render(<SnapshotFeedback snapshotKey="2024-12" />)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should not have any accessibility violations when editing saved feedback', async () => {
    setupMocks('authenticated', feedbackEntry)

    const { container } = render(<SnapshotFeedback snapshotKey="2024-12" />)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should not have any accessibility violations for anonymous visitors', async () => {
    setupMocks('unauthenticated', null)

    const { container } = render(<SnapshotFeedback snapshotKey="2024-12" />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
