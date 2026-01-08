import { render, screen, fireEvent } from '@testing-library/react'
import { mockProjectDetailsData } from '@unit/data/mockProjectDetailsData'
import { useRouter } from 'next/navigation'
import Leaders from 'components/Leaders'

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

jest.mock('components/AnchorTitle', () => ({
  __esModule: true,
  default: ({ title }: { title: string }) => <span>{title}</span>,
}))

jest.mock('wrappers/IconWrapper', () => ({
  IconWrapper: ({ icon: IconComponent, className, ...props }) => {
    return IconComponent ? (
      <IconComponent className={className} data-testid="icon" {...props} />
    ) : (
      <i className="icon" />
    )
  },
}))

describe('Leaders Component', () => {
  const push = jest.fn()
  beforeEach(() => {
    ;(useRouter as jest.Mock).mockReturnValue({ push })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders a list of leaders', () => {
    render(<Leaders users={mockProjectDetailsData.project.entityLeaders} />)

    expect(screen.getByText('Leaders')).toBeInTheDocument()
    expect(screen.getByText('Alice')).toBeInTheDocument()
    expect(screen.getByText('Project Leader')).toBeInTheDocument()
  })

  it('renders the section title even with no leaders', () => {
    render(<Leaders users={[]} />)
    expect(screen.getByText('Leaders')).toBeInTheDocument()
    expect(screen.queryByText('Alice')).not.toBeInTheDocument()
  })

  it('navigates to the correct page on button click', () => {
    render(<Leaders users={mockProjectDetailsData.project.entityLeaders} />)

    const viewProfileButton = screen.getByText('View Profile')
    fireEvent.click(viewProfileButton)

    expect(push).toHaveBeenCalledWith('/members/alice')
  })
})
