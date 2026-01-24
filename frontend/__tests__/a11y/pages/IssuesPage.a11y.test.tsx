import { useQuery } from '@apollo/client/react'
import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import IssuesPage from 'app/my/mentorship/programs/[programKey]/modules/[moduleKey]/issues/page'

jest.mock('@apollo/client/react', () => ({
  useQuery: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  useParams: jest.fn(() => ({ programKey: 'prog1', moduleKey: 'mod1' })),
  useRouter: jest.fn(),
  useSearchParams: jest.fn(() => new URLSearchParams()),
}))

const mockModuleData = {
  getModule: {
    name: 'Test Module',
    issues: [
      {
        id: '1',
        objectID: '1',
        number: 101,
        title: 'First Issue Title',
        state: 'open',
        isMerged: false,
        labels: ['bug'],
        assignees: [
          {
            avatarUrl: 'http://example.com/avatar.png',
            login: 'user1',
            name: 'User One',
          },
        ],
      },
    ],
    issuesCount: 1,
    availableLabels: ['bug', 'feature-request', 'documentation'],
  },
}

describe('IssuesPage Accessibility', () => {
  afterAll(() => {
    jest.clearAllMocks()
  })

  it('should have no accessibility violations', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockModuleData,
      loading: false,
      error: null,
    })

    const { container } = render(<IssuesPage />)

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
