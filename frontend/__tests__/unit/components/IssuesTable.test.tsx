import { render, screen, fireEvent, within } from '@testing-library/react'
import '@testing-library/jest-dom'
import React from 'react'
import IssuesTable, { type IssueRow } from 'components/IssuesTable'
import { LabelList } from 'components/LabelList'

const mockPush = jest.fn()

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}))

jest.mock('next/image', () => {
  return function MockImage({
    src,
    alt,
    style,
    fill,
  }: {
    src: string
    alt: string
    style?: React.CSSProperties
    fill?: boolean
  }) {
    // eslint-disable-next-line @next/next/no-img-element
    return <img src={src} alt={alt} style={style} data-testid="sponsor-image" data-fill={fill} />
  }
})

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({
    children,
    content,
    isDisabled,
  }: {
    children: React.ReactNode
    content: string
    isDisabled?: boolean
  }) => {
    if (isDisabled) {
      return <>{children}</>
    }
    return (
      <div data-testid="tooltip" data-content={content}>
        {children}
      </div>
    )
  },
}))

interface MockLabelListProps {
  entityKey: string
  labels: string[]
  maxVisible?: number
  className?: string
}

const MockLabelList = (props: MockLabelListProps) => {
  const { entityKey, labels, maxVisible = 5, className } = props
  if (!labels || labels.length === 0) return null
  const visibleLabels = labels.slice(0, maxVisible)
  const remainingCount = labels.length - maxVisible
  return (
    <div data-testid="label-list" className={className}>
      {visibleLabels.map((label) => (
        <span key={`${entityKey}-${label}`} data-testid="label">
          {label}
        </span>
      ))}
      {remainingCount > 0 && <span data-testid="label-more">+{remainingCount} more</span>}
    </div>
  )
}

jest.mock('components/LabelList', () => ({
  // Must match the module export name for the mock to be used by IssuesTable
  // eslint-disable-next-line @typescript-eslint/naming-convention -- component export name
  LabelList: jest.fn((props: MockLabelListProps) => <MockLabelList {...props} />),
}))

const mockIssues: IssueRow[] = [
  {
    objectID: '1',
    number: 123,
    title: 'Test Issue 1',
    state: 'open',
    isMerged: false,
    labels: ['bug', 'enhancement'],
    assignees: [
      {
        avatarUrl: 'https://example.com/avatar1.jpg',
        login: 'user1',
        name: 'User One',
      },
    ],
    url: 'https://github.com/test/repo/issues/123',
  },
  {
    objectID: '2',
    number: 124,
    title: 'Test Issue 2',
    state: 'closed',
    isMerged: false,
    labels: ['documentation'],
    assignees: [],
    url: 'https://github.com/test/repo/issues/124',
  },
  {
    objectID: '3',
    number: 125,
    title: 'Test Issue 3',
    state: 'closed',
    isMerged: true,
    labels: [],
    assignees: [
      {
        avatarUrl: 'https://example.com/avatar2.jpg',
        login: 'user2',
        name: 'User Two',
      },
      {
        avatarUrl: 'https://example.com/avatar3.jpg',
        login: 'user3',
        name: 'User Three',
      },
    ],
    url: 'https://github.com/test/repo/issues/125',
  },
]

describe('<IssuesTable />', () => {
  const defaultProps = {
    issues: mockIssues,
  }

  beforeEach(() => {
    jest.mocked(LabelList).mockClear()
  })

  describe('Rendering', () => {
    it('renders table view', () => {
      render(<IssuesTable {...defaultProps} />)
      const table = screen.getByRole('table')
      expect(table).toBeInTheDocument()
    })

    it('renders all issue rows', () => {
      render(<IssuesTable {...defaultProps} />)
      const issue1Buttons = screen.getAllByRole('button', { name: /Test Issue 1/i })
      const issue2Buttons = screen.getAllByRole('button', { name: /Test Issue 2/i })
      const issue3Buttons = screen.getAllByRole('button', { name: /Test Issue 3/i })
      expect(issue1Buttons.length).toBeGreaterThan(0)
      expect(issue2Buttons.length).toBeGreaterThan(0)
      expect(issue3Buttons.length).toBeGreaterThan(0)
    })

    it('renders table headers correctly', () => {
      render(<IssuesTable {...defaultProps} />)
      expect(screen.getByText('Title')).toBeInTheDocument()
      expect(screen.getByText('Status')).toBeInTheDocument()
      expect(screen.getByText('Labels')).toBeInTheDocument()
      expect(screen.getByText('Assignee')).toBeInTheDocument()
    })
  })

  describe('Status Badge', () => {
    it('renders Open status badge correctly', () => {
      render(<IssuesTable issues={[mockIssues[0]]} />)
      const openBadges = screen.getAllByText('Open')
      expect(openBadges.length).toBeGreaterThan(0)
    })

    it('renders Closed status badge correctly', () => {
      render(<IssuesTable issues={[mockIssues[1]]} />)
      const closedBadges = screen.getAllByText('Closed')
      expect(closedBadges.length).toBeGreaterThan(0)
    })

    it('renders Merged status badge when isMerged is true', () => {
      render(<IssuesTable issues={[mockIssues[2]]} />)
      // Merged issues display with "Closed" text (purple badge)
      const closedBadges = screen.getAllByText('Closed')
      expect(closedBadges.length).toBeGreaterThan(0)
    })

    it('defaults to Closed status for unknown states', () => {
      const unknownIssue: IssueRow = {
        objectID: '4',
        number: 126,
        title: 'Unknown State Issue',
        state: 'unknown',
        labels: [],
      }
      render(<IssuesTable issues={[unknownIssue]} />)
      const closedBadges = screen.getAllByText('Closed')
      expect(closedBadges.length).toBeGreaterThan(0)
    })
  })

  describe('Labels', () => {
    it('renders labels correctly', () => {
      render(<IssuesTable issues={[mockIssues[0]]} />)
      const bugLabels = screen.getAllByText('bug')
      const enhancementLabels = screen.getAllByText('enhancement')
      expect(bugLabels.length).toBeGreaterThan(0)
      expect(enhancementLabels.length).toBeGreaterThan(0)
    })

    it('renders "+X more" when labels exceed maxVisibleLabels', () => {
      const manyLabelsIssue: IssueRow = {
        objectID: '5',
        number: 127,
        title: 'Many Labels Issue',
        state: 'open',
        labels: ['label1', 'label2', 'label3', 'label4', 'label5', 'label6', 'label7'],
      }
      render(<IssuesTable issues={[manyLabelsIssue]} maxVisibleLabels={5} />)
      expect(screen.getByText('+2 more')).toBeInTheDocument()
    })

    it('does not render labels section when labels array is empty', () => {
      render(<IssuesTable issues={[mockIssues[2]]} />)
      const issueTitles = screen.getAllByText('Test Issue 3')
      const labelsCell = issueTitles[0].closest('tr')?.querySelector('td:nth-child(3)')
      expect(labelsCell?.textContent).toBe('')
    })

    it('respects maxVisibleLabels prop', () => {
      const manyLabelsIssue: IssueRow = {
        objectID: '6',
        number: 128,
        title: 'Many Labels Issue',
        state: 'open',
        labels: ['label1', 'label2', 'label3', 'label4', 'label5'],
      }
      render(<IssuesTable issues={[manyLabelsIssue]} maxVisibleLabels={3} />)
      expect(screen.getByText('+2 more')).toBeInTheDocument()
    })

    it('uses LabelList with entityKey derived from issue objectID', () => {
      render(<IssuesTable issues={[mockIssues[0]]} />)
      expect(LabelList).toHaveBeenCalledTimes(1)
      expect(LabelList).toHaveBeenCalledWith(
        expect.objectContaining({
          entityKey: 'issue-1',
          labels: ['bug', 'enhancement'],
          maxVisible: 5,
        }),
        undefined
      )
    })

    it('passes maxVisibleLabels to LabelList as maxVisible', () => {
      render(<IssuesTable issues={[mockIssues[0]]} maxVisibleLabels={3} />)
      expect(LabelList).toHaveBeenCalledTimes(1)
      expect(LabelList).toHaveBeenCalledWith(
        expect.objectContaining({
          entityKey: 'issue-1',
          labels: ['bug', 'enhancement'],
          maxVisible: 3,
        }),
        undefined
      )
    })

    it('passes empty array to LabelList when issue has no labels', () => {
      render(<IssuesTable issues={[mockIssues[2]]} />)
      expect(LabelList).toHaveBeenCalledTimes(1)
      expect(LabelList).toHaveBeenCalledWith(
        expect.objectContaining({
          entityKey: 'issue-3',
          labels: [],
          maxVisible: 5,
        }),
        undefined
      )
    })

    it('passes empty array to LabelList when issue.labels is undefined', () => {
      const issueWithUndefinedLabels = {
        ...mockIssues[0],
        objectID: 'undefined-labels',
        labels: undefined,
      } as IssueRow
      render(<IssuesTable issues={[issueWithUndefinedLabels]} />)
      expect(LabelList).toHaveBeenCalledTimes(1)
      expect(LabelList).toHaveBeenCalledWith(
        expect.objectContaining({
          entityKey: 'issue-undefined-labels',
          labels: [],
          maxVisible: 5,
        }),
        undefined
      )
    })

    it('calls LabelList once per issue row with correct labels', () => {
      render(<IssuesTable issues={mockIssues} />)
      expect(LabelList).toHaveBeenCalledTimes(3)
      expect(LabelList).toHaveBeenNthCalledWith(
        1,
        expect.objectContaining({ entityKey: 'issue-1', labels: ['bug', 'enhancement'] }),
        undefined
      )
      expect(LabelList).toHaveBeenNthCalledWith(
        2,
        expect.objectContaining({ entityKey: 'issue-2', labels: ['documentation'] }),
        undefined
      )
      expect(LabelList).toHaveBeenNthCalledWith(
        3,
        expect.objectContaining({ entityKey: 'issue-3', labels: [] }),
        undefined
      )
    })
  })

  describe('Assignee Column', () => {
    it('renders assignee column when showAssignee is true (default)', () => {
      render(<IssuesTable {...defaultProps} />)
      expect(screen.getByText('Assignee')).toBeInTheDocument()
    })

    it('hides assignee column when showAssignee is false', () => {
      render(<IssuesTable {...defaultProps} showAssignee={false} />)
      expect(screen.queryByText('Assignee')).not.toBeInTheDocument()
    })

    it('renders assignee avatar and name', () => {
      render(<IssuesTable issues={[mockIssues[0]]} />)
      const userContainer = screen.getByText('user1').closest('div')
      const avatar = within(userContainer).getByRole('presentation', { hidden: true })
      const user1Texts = screen.getAllByText('user1')
      expect(avatar).toBeInTheDocument()
      expect(user1Texts.length).toBeGreaterThan(0)
    })

    it('shows "+X" indicator when multiple assignees', () => {
      render(<IssuesTable issues={[mockIssues[2]]} />)
      const plusOneElements = screen.getAllByText(/\+1/)
      expect(plusOneElements.length).toBeGreaterThan(0)
    })

    it('does not render assignee section when no assignees', () => {
      render(<IssuesTable issues={[mockIssues[1]]} />)
      const issueTitles = screen.getAllByText('Test Issue 2')
      const assigneeCell = issueTitles[0].closest('tr')?.querySelector('td:nth-child(4)')
      expect(assigneeCell?.textContent).toBe('')
    })

    it('uses login when name is not available', () => {
      const issueWithoutName: IssueRow = {
        objectID: '7',
        number: 129,
        title: 'Issue Without Name',
        state: 'open',
        labels: [],
        assignees: [
          {
            avatarUrl: 'https://example.com/avatar4.jpg',
            login: 'user4',
            name: '',
          },
        ],
      }
      render(<IssuesTable issues={[issueWithoutName]} />)
      const user4Texts = screen.getAllByText('user4')
      expect(user4Texts.length).toBeGreaterThan(0)
    })

    it('uses name when login is not available', () => {
      const issueWithoutLogin: IssueRow = {
        objectID: '8-no-login',
        number: 133,
        title: 'Issue Without Login',
        state: 'open',
        labels: [],
        assignees: [
          {
            avatarUrl: 'https://example.com/avatar5.jpg',
            login: '',
            name: 'User Five',
          },
        ],
      }
      render(<IssuesTable issues={[issueWithoutLogin]} />)
      const user5Texts = screen.getAllByText('User Five')
      expect(user5Texts.length).toBeGreaterThan(0)
    })
  })

  describe('Click Handlers', () => {
    it('calls onIssueClick when provided', () => {
      const onIssueClick = jest.fn()
      render(<IssuesTable {...defaultProps} onIssueClick={onIssueClick} />)
      const issueButtons = screen.getAllByRole('button', { name: /Test Issue 1/i })
      expect(issueButtons.length).toBeGreaterThan(0)
      fireEvent.click(issueButtons[0])
      expect(onIssueClick).toHaveBeenCalledWith(123)
    })

    it('navigates to issue URL when onIssueClick is not provided', () => {
      const issueUrl = (num: number) => `/issues/${num}`
      render(<IssuesTable {...defaultProps} onIssueClick={undefined} issueUrl={issueUrl} />)
      const issueButtons = screen.getAllByRole('button', { name: /Test Issue 1/i })
      expect(issueButtons.length).toBeGreaterThan(0)
      fireEvent.click(issueButtons[0])
      expect(mockPush).toHaveBeenCalledWith('/issues/123')
    })

    it('does nothing when onIssueClick and issueUrl are not provided', () => {
      mockPush.mockClear()
      render(<IssuesTable {...defaultProps} onIssueClick={undefined} issueUrl={undefined} />)
      const issueButtons = screen.getAllByRole('button', { name: /Test Issue 1/i })
      expect(issueButtons.length).toBeGreaterThan(0)
      fireEvent.click(issueButtons[0])
      expect(mockPush).not.toHaveBeenCalled()
    })
  })

  describe('Empty State', () => {
    it('renders empty message when no issues', () => {
      render(<IssuesTable issues={[]} />)
      const emptyMessages = screen.getAllByText('No issues found.')
      expect(emptyMessages.length).toBeGreaterThan(0)
    })

    it('renders custom empty message', () => {
      const customMessage = 'No issues found for the selected filter.'
      render(<IssuesTable issues={[]} emptyMessage={customMessage} />)
      const customMessages = screen.getAllByText(customMessage)
      expect(customMessages.length).toBeGreaterThan(0)
    })

    it('renders empty state in desktop table', () => {
      render(<IssuesTable issues={[]} />)
      const table = screen.getByRole('table')
      const emptyRow = within(table).getByText('No issues found.')
      expect(emptyRow).toBeInTheDocument()
    })

    it('renders empty state in mobile view', () => {
      render(<IssuesTable issues={[]} />)
      const emptyMessages = screen.getAllByText('No issues found.')
      expect(emptyMessages.length).toBeGreaterThan(0)
    })
  })

  describe('Tooltip', () => {
    it('shows tooltip for long titles', () => {
      const longTitleIssue: IssueRow = {
        objectID: '8',
        number: 130,
        title: 'This is a very long issue title that exceeds fifty characters in length',
        state: 'open',
        labels: [],
      }
      render(<IssuesTable issues={[longTitleIssue]} />)
      const tooltips = screen.getAllByTestId('tooltip')
      const longTitleTooltip = tooltips.find(
        (tooltip) => tooltip.dataset.content === longTitleIssue.title
      )
      expect(longTitleTooltip).toBeInTheDocument()
      expect(longTitleTooltip?.dataset.content).toBe(longTitleIssue.title)
    })

    it('disables tooltip for short titles', () => {
      render(<IssuesTable issues={[mockIssues[0]]} />)
      const buttons = screen.getAllByRole('button', { name: /Test Issue 1/i })
      expect(buttons.length).toBeGreaterThan(0)
      const tooltips = screen.queryAllByTestId('tooltip')
      const shortTitleTooltip = tooltips.find(
        (tooltip) => tooltip.dataset.content === mockIssues[0].title
      )
      expect(shortTitleTooltip).toBeUndefined()
    })
  })

  describe('Mobile View', () => {
    it('renders status badge in mobile view', () => {
      render(<IssuesTable issues={[mockIssues[0]]} />)
      const openBadges = screen.getAllByText('Open')
      expect(openBadges.length).toBeGreaterThan(0)
    })

    it('renders labels in mobile view (limited to 3)', () => {
      const manyLabelsIssue: IssueRow = {
        objectID: '9',
        number: 131,
        title: 'Many Labels Issue',
        state: 'open',
        labels: ['label1', 'label2', 'label3', 'label4', 'label5'],
      }
      render(<IssuesTable issues={[manyLabelsIssue]} />)
      const label1Elements = screen.getAllByText('label1')
      expect(label1Elements.length).toBeGreaterThan(0)
    })

    it('renders assignee in mobile view when showAssignee is true', () => {
      render(<IssuesTable issues={[mockIssues[0]]} />)
      const user1Elements = screen.getAllByText('user1')
      expect(user1Elements.length).toBeGreaterThan(0)
    })

    it('does not render assignee in mobile view when showAssignee is false', () => {
      render(<IssuesTable issues={[mockIssues[0]]} showAssignee={false} />)
      const assigneeImages = screen.queryAllByAltText('user1')
      expect(assigneeImages.length).toBe(0)
    })
  })

  describe('Column Count', () => {
    it('calculates correct column count with assignee column', () => {
      render(<IssuesTable issues={[]} showAssignee={true} />)
      const table = screen.getByRole('table')
      const headers = within(table).getAllByRole('columnheader')
      expect(headers).toHaveLength(4)
    })

    it('calculates correct column count without assignee column', () => {
      render(<IssuesTable issues={[]} showAssignee={false} />)
      const table = screen.getByRole('table')
      const headers = within(table).getAllByRole('columnheader')
      expect(headers).toHaveLength(3)
    })
  })

  describe('Default Props', () => {
    it('uses default showAssignee value (true)', () => {
      render(<IssuesTable issues={mockIssues} />)
      expect(screen.getByText('Assignee')).toBeInTheDocument()
    })

    it('uses default emptyMessage', () => {
      render(<IssuesTable issues={[]} />)
      const emptyMessages = screen.getAllByText('No issues found.')
      expect(emptyMessages.length).toBeGreaterThan(0)
    })

    it('uses default maxVisibleLabels (5)', () => {
      const manyLabelsIssue: IssueRow = {
        objectID: '10',
        number: 132,
        title: 'Many Labels Issue',
        state: 'open',
        labels: ['label1', 'label2', 'label3', 'label4', 'label5', 'label6'],
      }
      render(<IssuesTable issues={[manyLabelsIssue]} />)
      expect(screen.getByText('+1 more')).toBeInTheDocument()
    })
  })
})
