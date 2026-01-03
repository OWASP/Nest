import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { ReactNode } from 'react'
import { Milestone } from 'types/milestone'
import { User } from 'types/user'
import Milestones from 'components/Milestones'

expect.extend(toHaveNoViolations)

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(),
}))

jest.mock('components/ItemCardList', () => {
  const MockItemCardList = ({
    title,
    data,
    showAvatar,
    icon,
    showSingleColumn,
    renderDetails,
  }: {
    title: ReactNode
    data: Milestone[]
    showAvatar: boolean
    icon: unknown
    showSingleColumn: boolean
    renderDetails: (item: Milestone) => ReactNode
  }) => {
    const getIconLabel = (iconProp: unknown): string => {
      if (!iconProp) return 'no-icon'
      if (typeof iconProp === 'function' && iconProp.name) return iconProp.name
      if (typeof iconProp === 'string') return iconProp
      return typeof iconProp
    }

    return (
      <div data-testid="item-card-list">
        <div data-testid="title">{title}</div>
        <div data-testid="show-avatar">{showAvatar.toString()}</div>
        <div data-testid="show-single-column">{showSingleColumn.toString()}</div>
        <div data-testid="icon">{getIconLabel(icon)}</div>
        {data.map((item, index) => {
          // Avoid nested template literals by constructing fallback separately
          const fallbackKey = [
            item.organizationName || 'org',
            item.repositoryName || 'repo',
            item.title || 'milestone',
          ].join('-')

          const uniqueKey = `milestone-${index}-${item.url || fallbackKey}`

          return (
            <div key={uniqueKey} data-testid={`milestone-${index}`}>
              {renderDetails(item)}
            </div>
          )
        })}
      </div>
    )
  }

  return {
    __esModule: true,
    default: MockItemCardList,
  }
})

const createMockUser = (): User => ({
  login: 'testuser',
  name: 'Test User',
  avatarUrl: 'https://github.com/testuser.png',
  url: 'https://github.com/testuser',
  key: 'testuser',
  followersCount: 10,
  followingCount: 5,
  publicRepositoriesCount: 20,
  contributionsCount: 50,
  createdAt: 1640995200000,
  updatedAt: 1640995200000,
})

const createMockMilestone = (overrides: Partial<Milestone> = {}): Milestone => ({
  author: createMockUser(),
  body: 'Test milestone description',
  closedIssuesCount: 5,
  createdAt: '2023-01-01T00:00:00Z',
  openIssuesCount: 3,
  organizationName: 'test-org',
  progress: 75,
  repositoryName: 'test-repo',
  state: 'open',
  title: 'Test Milestone',
  url: 'https://github.com/test-org/test-repo/milestone/1',
  ...overrides,
})

describe('Milestones a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<Milestones data={[createMockMilestone()]} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
