import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import type { IssueRow } from 'components/IssuesTable'
import IssuesTable from 'components/IssuesTable'

const mockIssues: IssueRow[] = [
  {
    objectID: '1',
    number: 101,
    title: 'Fix accessibility violations',
    state: 'open',
    labels: ['bug', 'a11y'],
    assignees: [
      { avatarUrl: 'https://example.com/avatar.png', login: 'testuser', name: 'Test User' },
    ],
  },
  {
    objectID: '2',
    number: 102,
    title: 'Update documentation',
    state: 'closed',
    isMerged: true,
    labels: ['docs'],
    assignees: [
      { avatarUrl: 'https://example.com/avatar2.png', login: 'testuser2', name: 'Test User 2' },
    ],
  },
]

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('IssuesTable a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })
  it('should have no accessibility violations with issues', async () => {
    const { container } = render(
      <main>
        <IssuesTable issues={mockIssues} />
      </main>
    )

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have no accessibility violations with empty issues', async () => {
    const { container } = render(
      <main>
        <IssuesTable issues={[]} />
      </main>
    )

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
