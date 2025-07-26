import { render, screen } from '@testing-library/react'
import InfoItem from 'components/InfoItem'
import { faUser } from '@fortawesome/free-solid-svg-icons'
import millify from 'millify'

// ✅ Mocks
jest.mock('millify', () => jest.fn())
jest.mock('utils/pluralize', () => ({
  pluralize: jest.fn(),
}))
import { pluralize } from 'utils/pluralize'
const mockPluralize = pluralize as jest.Mock
const mockMillify = millify as jest.Mock

describe('InfoItem', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders successfully with required props', () => {
    mockMillify.mockReturnValue('1k')
    mockPluralize.mockReturnValue('1 user')

    render(<InfoItem icon={faUser} unit="user" value={1000} />)

    expect(screen.getByText('1k')).toBeInTheDocument()
    expect(screen.getByText('1 user')).toBeInTheDocument()
    expect(screen.getByRole('img', { hidden: true })).toBeInTheDocument()
  })

  it('uses pluralizedName if provided', () => {
    mockMillify.mockReturnValue('2k')
    mockPluralize.mockReturnValue('2 contributors')

    render(
      <InfoItem
        icon={faUser}
        unit="contributor"
        value={2000}
        pluralizedName="contributors"
      />
    )

    expect(mockPluralize).toHaveBeenCalledWith(2000, 'contributor', 'contributors')
    expect(screen.getByText('2 contributors')).toBeInTheDocument()
  })

  it('respects precision prop when formatting value', () => {
    render(<InfoItem icon={faUser} unit="view" value={15430} precision={3} />)
    expect(mockMillify).toHaveBeenCalledWith(15430, { precision: 3 })
  })

  it('handles value = 0 properly', () => {
    mockMillify.mockReturnValue('0')
    mockPluralize.mockReturnValue('0 views')

    render(<InfoItem icon={faUser} unit="view" value={0} />)

    expect(screen.getByText('0')).toBeInTheDocument()
    expect(screen.getByText('0 views')).toBeInTheDocument()
  })

  it('applies correct DOM structure and classes', () => {
    mockMillify.mockReturnValue('5')
    mockPluralize.mockReturnValue('5 likes')

    render(<InfoItem icon={faUser} unit="like" value={5} />)

    const container = screen.getByText('5').closest('div')
    expect(container).toHaveClass('flex items-center justify-between')

    const label = screen.getByText(/like/i).closest('span')
    expect(label).toHaveClass('flex items-center')

    const icon = screen.getByRole('img', { hidden: true })
    expect(icon).toHaveClass('mr-2 h-4 w-4')
  })

  it('uses default precision = 1 when not provided', () => {
    render(<InfoItem icon={faUser} unit="star" value={1010} />)
    expect(mockMillify).toHaveBeenCalledWith(1010, { precision: 1 })
  })

  it('renders both text and number correctly', () => {
    mockMillify.mockReturnValue('7.5k')
    mockPluralize.mockReturnValue('7.5 stars')

    render(<InfoItem icon={faUser} unit="star" value={7500} />)

    expect(screen.getByText('7.5k')).toBeInTheDocument()
    expect(screen.getByText('7.5 stars')).toBeInTheDocument()
  })
})
