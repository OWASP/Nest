import { render, screen, fireEvent } from '@testing-library/react'
import SnapshotCard from 'components/SnapshotCard'
import { formatDate } from 'utils/dateFormatter'

describe('SnapshotCard', () => {
  const mockOnClick = jest.fn()

  const defaultProps = {
    title: 'Test Snapshot',
    button: { label: 'Open', onclick: mockOnClick },
    startAt: '2025-01-01T00:00:00Z',
    endAt: '2025-01-10T00:00:00Z',
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders successfully with minimal required props', () => {
    render(<SnapshotCard {...(defaultProps as any)} />)
    expect(screen.getByText(/Test Snapshot/i)).toBeInTheDocument()
  })

  it('renders the date range correctly', () => {
    render(<SnapshotCard {...(defaultProps as any)} />)
    const expected = `${formatDate(defaultProps.startAt)} - ${formatDate(defaultProps.endAt)}`
    expect(screen.getByText(expected)).toBeInTheDocument()
  })

  it('renders the "View Snapshot" text', () => {
    render(<SnapshotCard {...(defaultProps as any)} />)
    expect(screen.getByText(/View Snapshot/i)).toBeInTheDocument()
  })

  it('calls the onClick handler when clicked', () => {
    render(<SnapshotCard {...(defaultProps as any)} />)
    fireEvent.click(screen.getByRole('button'))
    expect(mockOnClick).toHaveBeenCalledTimes(1)
  })

  it('has correct accessibility role', () => {
    render(<SnapshotCard {...(defaultProps as any)} />)
    expect(screen.getByRole('button')).toBeInTheDocument()
  })

  it('handles empty title gracefully (edge case)', () => {
    render(<SnapshotCard {...(defaultProps as any)} title="" />)
    expect(screen.getByText(/View Snapshot/i)).toBeInTheDocument()
  })

  it('handles missing startAt or endAt (conditional rendering) - timezone safe', () => {
    const { rerender } = render(<SnapshotCard {...(defaultProps as any)} startAt="" />)
    const onlyEnd = formatDate(defaultProps.endAt)
    expect(screen.getByText(new RegExp(onlyEnd))).toBeInTheDocument()

    rerender(<SnapshotCard {...(defaultProps as any)} endAt="" />)
    const onlyStart = formatDate(defaultProps.startAt)
    expect(screen.getByText(new RegExp(onlyStart))).toBeInTheDocument()
  })

  it('applies expected DOM classes for styling', () => {
    render(<SnapshotCard {...(defaultProps as any)} />)
    const btn = screen.getByRole('button')
    expect(btn.className).toMatch(/flex/)
    expect(btn.className).toMatch(/rounded-lg/)
    expect(btn.className).toMatch(/hover:scale-105/)
  })
})