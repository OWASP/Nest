import { render, screen } from '@testing-library/react'
import millify from 'millify'
import React from 'react'
import { FaUser } from 'react-icons/fa'
import { pluralize } from 'utils/pluralize'
import InfoItem, { TextInfoItem } from 'components/InfoItem'

jest.mock('millify', () => jest.fn())
jest.mock('utils/pluralize', () => ({
  pluralize: jest.fn(),
}))

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({ children, content }: { children: React.ReactNode; content: string }) => (
    <span data-testid="tooltip" title={content}>
      {children}
    </span>
  ),
}))

const mockMillify = millify as jest.Mock
const mockPluralize = pluralize as jest.Mock

describe('InfoItem', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders successfully with required props', () => {
    mockMillify.mockReturnValue('1k')
    mockPluralize.mockReturnValue('1 user')

    render(<InfoItem icon={FaUser} unit="user" value={1000} />)

    expect(screen.getByText('1k')).toBeInTheDocument()
    expect(screen.getByText('1 user')).toBeInTheDocument()
    expect(document.querySelector('svg')).toBeInTheDocument()
  })

  it('uses pluralizedName if provided', () => {
    mockMillify.mockReturnValue('2k')
    mockPluralize.mockReturnValue('2 contributors')

    render(<InfoItem icon={FaUser} unit="contributor" value={2000} pluralizedName="contributors" />)

    expect(mockPluralize).toHaveBeenCalledWith(2000, 'contributor', 'contributors')
    expect(screen.getByText('2 contributors')).toBeInTheDocument()
  })

  it('respects precision prop when formatting value', () => {
    mockMillify.mockReturnValue('15.4k')
    mockPluralize.mockReturnValue('15430 views')

    render(<InfoItem icon={FaUser} unit="view" value={15430} precision={3} />)

    expect(mockMillify).toHaveBeenCalledWith(15430, { precision: 3 })
    expect(screen.getByText('15.4k')).toBeInTheDocument()
  })

  it('handles value = 0 properly', () => {
    mockMillify.mockReturnValue('0')
    mockPluralize.mockReturnValue('0 views')

    render(<InfoItem icon={FaUser} unit="view" value={0} />)

    expect(screen.getByText('0')).toBeInTheDocument()
    expect(screen.getByText('0 views')).toBeInTheDocument()
  })

  it('applies correct DOM structure and classes', () => {
    mockMillify.mockReturnValue('5')
    mockPluralize.mockReturnValue('5 likes')

    render(<InfoItem icon={FaUser} unit="like" value={5} />)

    const container = screen.getByText('5 likes').closest('div')
    expect(container).toHaveClass('flex', 'items-center', 'justify-between')

    const nameSpan = screen.getByText('5 likes').closest('span')
    expect(nameSpan).toHaveClass('flex', 'items-center')

    const icon = document.querySelector('svg')
    expect(icon).toBeInTheDocument()
    expect(icon).toHaveClass('mr-2', 'h-4', 'w-4')

    const valueSpan = screen.getByText('5').closest('span')
    expect(valueSpan).toHaveClass('font-medium')
  })

  it('uses default precision = 1 when not provided', () => {
    mockMillify.mockReturnValue('1k')
    mockPluralize.mockReturnValue('1010 stars')

    render(<InfoItem icon={FaUser} unit="star" value={1010} />)

    expect(mockMillify).toHaveBeenCalledWith(1010, { precision: 1 })
  })

  it('creates tooltip with correct content', () => {
    mockMillify.mockReturnValue('7.5k')
    mockPluralize.mockReturnValue('7.5k stars')

    render(<InfoItem icon={FaUser} unit="star" value={7500} />)

    const tooltip = screen.getByTestId('tooltip')
    expect(tooltip).toHaveAttribute('title', '7,500 7.5k stars')
    expect(screen.getByText('7.5k')).toBeInTheDocument()
  })

  it('handles zero value with proper tooltip content', () => {
    mockMillify.mockReturnValue('0')
    mockPluralize.mockReturnValue('0 items')

    render(<InfoItem icon={FaUser} unit="item" value={0} />)

    const tooltip = screen.getByTestId('tooltip')
    expect(tooltip).toHaveAttribute('title', 'No 0 items')
    expect(screen.getByText('0')).toBeInTheDocument()
  })
})

describe('TextInfoItem', () => {
  it('renders successfully with required props', () => {
    render(<TextInfoItem icon={FaUser} label="Author" value="John Doe" />)

    expect(screen.getByText('Author:')).toBeInTheDocument()
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(document.querySelector('svg')).toBeInTheDocument()
  })

  it('applies correct DOM structure and classes', () => {
    render(<TextInfoItem icon={FaUser} label="Role" value="Developer" />)

    const container = screen.getByText('Role:').closest('div')
    expect(container).toHaveClass(
      'flex',
      'items-center',
      'gap-2',
      'text-sm',
      'text-gray-600',
      'dark:text-gray-300'
    )

    const labelSpan = screen.getByText('Role:')
    expect(labelSpan).toHaveClass('font-medium')

    const icon = document.querySelector('svg')
    expect(icon).toBeInTheDocument()
    expect(icon).toHaveClass('text-xs')
  })

  it('handles empty value string', () => {
    render(<TextInfoItem icon={FaUser} label="Status" value="" />)

    expect(screen.getByText('Status:')).toBeInTheDocument()
  })

  it('handles long value strings', () => {
    const longValue = 'This is a very long value string that might be displayed'
    render(<TextInfoItem icon={FaUser} label="Description" value={longValue} />)

    expect(screen.getByText('Description:')).toBeInTheDocument()
    expect(screen.getByText(longValue)).toBeInTheDocument()
  })
})
