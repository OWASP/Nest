import { render, screen, act, waitFor } from '@testing-library/react'
import AnimatedCounter from 'components/AnimatedCounter'

jest.useFakeTimers()

describe('AnimatedCounter', () => {
  const defaultProps = {
    end: 1000,
    duration: 1000,
    className: 'test-counter',
    'aria-label': 'Animated count',
    onEnd: jest.fn(),
  }

  afterEach(() => {
    jest.clearAllTimers()
    jest.clearAllMocks()
  })

  it('renders successfully with minimal required props', () => {
    render(<AnimatedCounter end={100} duration={500} />)
    expect(screen.getByText('0')).toBeInTheDocument()
  })

  it('renders with custom className and aria-label', () => {
    render(<AnimatedCounter {...defaultProps} />)
    const counter = screen.getByLabelText('Animated count')
    expect(counter).toHaveClass('test-counter')
  })

  it('animates from 0 to given end value', () => {
    render(<AnimatedCounter end={1000} duration={1000} />)
    act(() => {
      jest.advanceTimersByTime(1000)
    })
    expect(screen.getByText('1K')).toBeInTheDocument()
  })

  it('calls onEnd when animation finishes', () => {
    const onEndMock = jest.fn()
    render(<AnimatedCounter end={500} duration={500} onEnd={onEndMock} />)
    act(() => {
      jest.advanceTimersByTime(500)
    })
    expect(onEndMock).toHaveBeenCalledTimes(1)
  })

  it('handles end = 0 and negative values', () => {
    const { rerender } = render(<AnimatedCounter end={0} duration={500} />)
    expect(screen.getByText('0')).toBeInTheDocument()

    rerender(<AnimatedCounter end={-10} duration={500} />)
    expect(screen.getByText('0')).toBeInTheDocument()
  })

  it('updates when end prop changes', () => {
    const { rerender } = render(<AnimatedCounter end={20} duration={500} />)
    act(() => {
      jest.advanceTimersByTime(500)
    })
    expect(screen.getByText('20')).toBeInTheDocument()

    rerender(<AnimatedCounter end={40} duration={300} />)
    act(() => {
      jest.advanceTimersByTime(300)
    })
    expect(screen.getByText('40')).toBeInTheDocument()
  })

  it('has role="timer" and aria-live="polite"', () => {
    render(<AnimatedCounter {...defaultProps} />)
    const counter = screen.getByRole('timer')
    expect(counter).toHaveAttribute('aria-live', 'polite')
  })

  it('renders as span element', () => {
    render(<AnimatedCounter {...defaultProps} />)
    const counter = screen.getByLabelText('Animated count')
    expect(counter.tagName.toLowerCase()).toBe('span')
  })

  it('renders the counter with correct value after animation', async () => {
    render(<AnimatedCounter end={42} duration={0.1} />)

    const counterElement = screen.getByLabelText(/animated count/i)
    expect(counterElement).toBeInTheDocument()

    await waitFor(() => {
      expect(counterElement.textContent).toBe('42')
    }, { timeout: 500 })
  })
})
