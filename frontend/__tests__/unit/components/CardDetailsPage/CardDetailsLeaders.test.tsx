import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { Leader } from 'types/leader'
import CardDetailsLeaders from 'components/CardDetailsPage/CardDetailsLeaders'

jest.mock('components/Leaders', () => ({
  __esModule: true,
  default: ({ users }: { users: Leader[] }) => (
    <div data-testid="leaders-component">Leaders: {users.map((u) => u.login).join(', ')}</div>
  ),
}))

describe('CardDetailsLeaders', () => {
  const mockLeader: Leader = {
    id: '1',
    login: 'user1',
    name: 'User One',
    avatarUrl: 'https://example.com/avatar1.jpg',
  }

  it('renders nothing when entityLeaders is undefined', () => {
    const { container } = render(<CardDetailsLeaders entityLeaders={undefined} />)
    expect(container.firstChild).toBeNull()
  })

  it('renders nothing when entityLeaders is null', () => {
    const { container } = render(<CardDetailsLeaders entityLeaders={null} />)
    expect(container.firstChild).toBeNull()
  })

  it('renders nothing when entityLeaders is empty array', () => {
    const { container } = render(<CardDetailsLeaders entityLeaders={[]} />)
    expect(container.firstChild).toBeNull()
  })

  it('renders Leaders component when entityLeaders has data', () => {
    render(<CardDetailsLeaders entityLeaders={[mockLeader]} />)
    expect(screen.getByTestId('leaders-component')).toBeInTheDocument()
    expect(screen.getByText(/user1/)).toBeInTheDocument()
  })

  it('renders div with mb-8 class when entityLeaders has data', () => {
    const { container } = render(<CardDetailsLeaders entityLeaders={[mockLeader]} />)
    const div = container.querySelector('div.mb-8')
    expect(div).toBeInTheDocument()
  })

  it('passes all leaders to Leaders component', () => {
    const leaders: Leader[] = [
      {
        id: '1',
        login: 'leader1',
        name: 'Leader One',
        avatarUrl: 'https://example.com/avatar1.jpg',
      },
      {
        id: '2',
        login: 'leader2',
        name: 'Leader Two',
        avatarUrl: 'https://example.com/avatar2.jpg',
      },
      {
        id: '3',
        login: 'leader3',
        name: 'Leader Three',
        avatarUrl: 'https://example.com/avatar3.jpg',
      },
    ]

    render(<CardDetailsLeaders entityLeaders={leaders} />)
    expect(screen.getByTestId('leaders-component')).toBeInTheDocument()
    expect(screen.getByText(/leader1.*leader2.*leader3/)).toBeInTheDocument()
  })

  it('renders with single leader', () => {
    render(<CardDetailsLeaders entityLeaders={[mockLeader]} />)
    expect(screen.getByTestId('leaders-component')).toBeInTheDocument()
    expect(screen.getByText('Leaders: user1')).toBeInTheDocument()
  })

  it('renders Leaders component nested inside mb-8 div', () => {
    const { container } = render(<CardDetailsLeaders entityLeaders={[mockLeader]} />)
    const mbDiv = container.querySelector('div.mb-8')
    const leadersComponent = screen.getByTestId('leaders-component')
    expect(mbDiv?.contains(leadersComponent)).toBe(true)
  })
})
