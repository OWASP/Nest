import { useQuery, useLazyQuery, useApolloClient } from '@apollo/client/react'
import { mockSnapshotDetailsData } from '@mockData/mockSnapshotData'
import { waitFor, screen } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import { render } from 'wrappers/testUtil'
import SnapshotDetailsPage from 'app/community/snapshots/[id]/page'
import { GetSnapshotFeedbackDocument } from 'types/__generated__/snapshotQueries.generated'

jest.mock('@apollo/client/react', () => ({
  useQuery: jest.fn(),
  useLazyQuery: jest.fn(),
  useApolloClient: jest.fn(),
  useMutation: jest.fn(() => [jest.fn(), { loading: false }]),
}))

jest.mock('hooks/useDjangoSession', () => ({
  useDjangoSession: jest.fn(() => ({
    isSyncing: false,
    session: { user: { name: 'testuser' } },
    status: 'authenticated',
  })),
}))

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(() => ({ push: jest.fn() })),
  useParams: jest.fn(() => ({ id: '2024-12' })),
  useSearchParams: jest.fn(() => new URLSearchParams()),
}))

jest.mock('@/components/MarkdownWrapper', () => {
  return jest.fn(({ content, className }) => (
    <div className={`md-wrapper ${className}`} dangerouslySetInnerHTML={{ __html: content }} />
  ))
})

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

const mockSnapshotFeedbackData = {
  data: {
    snapshot: {
      id: 'snapshot-1',
      averageRating: 5,
      feedbackCount: 1,
      myFeedback: feedbackEntry,
      feedback: [feedbackEntry],
    },
  },
  loading: false,
  error: null,
  refetch: jest.fn(),
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('SnapshotDetails Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
    ;(useLazyQuery as unknown as jest.Mock).mockReturnValue([
      jest.fn().mockResolvedValue({ data: {} }),
    ])
    ;(useApolloClient as jest.Mock).mockReturnValue({
      cache: {
        updateQuery: jest.fn(),
      },
    })
  })
  it('should have no accessibility violations', async () => {
    ;(useQuery as unknown as jest.Mock).mockImplementation((query) =>
      query === GetSnapshotFeedbackDocument
        ? mockSnapshotFeedbackData
        : { data: mockSnapshotDetailsData, loading: false, error: null }
    )

    const { container } = render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('New Snapshot')).toBeInTheDocument()
    })
    expect(screen.getByText('Community Feedback')).toBeInTheDocument()

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
