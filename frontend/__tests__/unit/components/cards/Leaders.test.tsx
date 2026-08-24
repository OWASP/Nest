import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import type { Leader } from 'types/leader'
import Leaders from 'components/cards/Leaders'

jest.mock('components/Leaders', () => ({
  __esModule: true,
  default: ({ users }: { users: Leader[] }) => (
    <div data-testid="leaders-component">
      Leaders: {users.map((u) => u.member?.login ?? u.memberName).join(', ')}
    </div>
  ),
}))

const createMockLeader = (login: string, name: string): Leader => ({
  description: 'Leader',
  memberName: name,
  member: {
    login,
    name,
    avatarUrl: `https://example.com/${login}.jpg`,
  },
})

describe('Leaders', () => {
  const mockLeader = createMockLeader('user1', 'User One')

  it('renders nothing when entityLeaders is undefined', () => {
    const { container } = render(<Leaders entityLeaders={undefined} />)
    expect(container.firstChild).toBeNull()
  })

  it('renders nothing when entityLeaders is null', () => {
    const { container } = render(<Leaders entityLeaders={null} />)
    expect(container.firstChild).toBeNull()
  })

  it('renders nothing when entityLeaders is empty array', () => {
    const { container } = render(<Leaders entityLeaders={[]} />)
    expect(container.firstChild).toBeNull()
  })

  it('renders Leaders component when entityLeaders has data', () => {
    render(<Leaders entityLeaders={[mockLeader]} />)
    expect(screen.getByTestId('leaders-component')).toBeInTheDocument()
    expect(screen.getByText(/user1/)).toBeInTheDocument()
  })

  it('renders div with mb-8 class when entityLeaders has data', () => {
    const { container } = render(<Leaders entityLeaders={[mockLeader]} />)
    const div = container.querySelector('div.mb-8')
    expect(div).toBeInTheDocument()
  })

  it('passes all leaders to Leaders component', () => {
    const leaders: Leader[] = [
      createMockLeader('leader1', 'Leader One'),
      createMockLeader('leader2', 'Leader Two'),
      createMockLeader('leader3', 'Leader Three'),
    ]

    render(<Leaders entityLeaders={leaders} />)
    expect(screen.getByTestId('leaders-component')).toBeInTheDocument()
    expect(screen.getByText(/leader1.*leader2.*leader3/)).toBeInTheDocument()
  })

  it('renders with single leader', () => {
    render(<Leaders entityLeaders={[mockLeader]} />)
    expect(screen.getByTestId('leaders-component')).toBeInTheDocument()
    expect(screen.getByText('Leaders: user1')).toBeInTheDocument()
  })

  it('renders Leaders component nested inside mb-8 div', () => {
    const { container } = render(<Leaders entityLeaders={[mockLeader]} />)
    const mbDiv = container.querySelector('div.mb-8')
    const leadersComponent = screen.getByTestId('leaders-component')
    expect(mbDiv?.contains(leadersComponent)).toBe(true)
  })
})
