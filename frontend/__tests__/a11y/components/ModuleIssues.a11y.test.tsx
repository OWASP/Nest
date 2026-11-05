import { useQuery } from '@apollo/client/react'
import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import ModuleIssues from 'components/cards/ModuleIssues'

jest.mock('@apollo/client/react', () => ({
  useQuery: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(() => ({ push: jest.fn(), replace: jest.fn() })),
  useSearchParams: jest.fn(() => new URLSearchParams()),
}))

const mockModuleData = {
  managementModule: {
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
      {
        id: '2',
        objectID: '2',
        number: 102,
        title: 'Second Issue Title',
        state: 'open',
        isMerged: false,
        labels: ['docs'],
        assignees: [],
        taskDeadline: '2099-01-30T00:00:00Z',
      },
    ],
    issuesCount: 2,
    availableLabels: ['bug', 'feature-request', 'documentation'],
  },
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('ModuleIssues Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  afterAll(() => {
    jest.clearAllMocks()
  })

  it('should have no accessibility violations', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockModuleData,
      loading: false,
      error: null,
    })

    const { container } = render(<ModuleIssues programKey="prog1" moduleKey="mod1" />)

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
