import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import type { Issue } from 'types/issue'
import MenteeIssues from 'components/MenteeIssues'

const mockOpenIssues: Issue[] = [
  {
    objectID: '1',
    title: 'Open issue',
    url: 'https://github.com/test/repo/issues/1',
    createdAt: '2025-01-01',
    state: 'open',
    number: 1,
    labels: ['bug'],
  },
]

const mockClosedIssues: Issue[] = [
  {
    objectID: '2',
    title: 'Closed issue',
    url: 'https://github.com/test/repo/issues/2',
    createdAt: '2025-01-01',
    updatedAt: '2025-02-01',
    state: 'closed',
    number: 2,
    labels: ['enhancement'],
  },
]

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('MenteeIssues a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should have no accessibility violations', async () => {
    const { container } = render(
      <MenteeIssues
        openIssues={mockOpenIssues}
        closedIssues={mockClosedIssues}
        menteeHandle="test-mentee"
      />
    )

    const results = await axe(container, {
      rules: {
        'heading-order': { enabled: false },
      },
    })
    expect(results).toHaveNoViolations()
  })
})
