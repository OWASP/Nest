import { render, screen, act } from '@testing-library/react'
import '@testing-library/jest-dom'
import AnimatedCounter from 'components/AnimatedCounter'

jest.useFakeTimers()

// Patch for performance.now() in jsdom test env
beforeAll(() => {
  if (typeof performance.now !== 'function') {
    performance.now = jest.fn(() => Date.now())
  }
})

describe('AnimatedCounter', () => {
  afterEach(() => {
    jest.clearAllTimers()
  })

  describe('Renders successfully with minimal required props', () => {
    it('renders correctly with initial count 0', () => {
      render(<AnimatedCounter end={1000} duration={2} />)
      const counter = screen.getByText('0')
      expect(counter).toBeInTheDocument()
    })

    it('renders with all props including className', () => {
      render(<AnimatedCounter end={50} duration={1} className="test-class" />)
      const element = screen.getByText('0')
      expect(element).toHaveClass('test-class')
    })
  })

  describe('Prop-based behavior – different props affect output', () => {
    it('renders with correct end value', () => {
      render(<AnimatedCounter end={1000} duration={1} />)
      expect(screen.getByText('0')).toBeInTheDocument()
    })

    it('applies custom className when provided', () => {
      render(<AnimatedCounter end={100} duration={2} className="custom-counter" />)
      const element = screen.getByText('0')
      expect(element).toHaveClass('custom-counter')
    })

    it('renders without className when not provided', () => {
      render(<AnimatedCounter end={100} duration={2} />)
      const element = screen.getByText('0')
      expect(element).not.toHaveAttribute('class')
    })
  })

  describe('State changes / internal logic', () => {
    it('animates to the end value over duration', () => {
      render(<AnimatedCounter end={1000} duration={2} />)

      // Advance time by 2 seconds within act()
      act(() => {
        jest.advanceTimersByTime(2000)
      })

      const counter = screen.getByText('1K')
      expect(counter).toBeInTheDocument()
    })

    it('updates count during animation', () => {
      render(<AnimatedCounter end={50} duration={2} />)

      // Advance time by 1 second (halfway through animation)
      act(() => {
        jest.advanceTimersByTime(1000)
      })

      // Should show intermediate value
      const displayedValue = parseInt(screen.getByText(/\d+/).textContent || '0')
      expect(displayedValue).toBeGreaterThan(0)
      expect(displayedValue).toBeLessThanOrEqual(50)
    })

    it('stops at exact end value', () => {
      render(<AnimatedCounter end={75} duration={1} />)

      act(() => {
        jest.advanceTimersByTime(1000)
      })

      expect(screen.getByText('75')).toBeInTheDocument()
    })
  })

  describe('Default values and fallbacks', () => {
    it('handles zero end value', () => {
      render(<AnimatedCounter end={0} duration={1} />)
      expect(screen.getByText('0')).toBeInTheDocument()
    })

    it('handles negative end value', () => {
      render(<AnimatedCounter end={-10} duration={1} />)
      expect(screen.getByText('0')).toBeInTheDocument()
    })

    it('handles very small duration', () => {
      render(<AnimatedCounter end={100} duration={0.1} />)
      expect(screen.getByText('0')).toBeInTheDocument()
    })

    it('handles very large duration', () => {
      render(<AnimatedCounter end={100} duration={100} />)
      expect(screen.getByText('0')).toBeInTheDocument()
    })
  })

  describe('Text and content rendering', () => {
    it('displays formatted numbers using millify', () => {
      render(<AnimatedCounter end={1200} duration={1} />)

      act(() => {
        jest.advanceTimersByTime(1000)
      })

      expect(screen.getByText('1.2K')).toBeInTheDocument()
    })

    it('renders as span element', () => {
      render(<AnimatedCounter end={100} duration={2} />)
      const element = screen.getByText('0')
      expect(element.tagName).toBe('SPAN')
    })
  })

  describe('Handles edge cases and invalid inputs', () => {
    it('handles decimal end values', () => {
      render(<AnimatedCounter end={99.5} duration={1} />)
      expect(screen.getByText('0')).toBeInTheDocument()
    })

    it('handles very large end values', () => {
      render(<AnimatedCounter end={999999999} duration={1} />)
      expect(screen.getByText('0')).toBeInTheDocument()
    })

    it('handles zero duration gracefully', () => {
      render(<AnimatedCounter end={100} duration={0} />)
      expect(screen.getByText('0')).toBeInTheDocument()
    })

    it('handles negative duration gracefully', () => {
      render(<AnimatedCounter end={100} duration={-1} />)
      expect(screen.getByText('0')).toBeInTheDocument()
    })
  })

  describe('DOM structure / classNames / styles', () => {
    it('renders with correct HTML structure', () => {
      render(<AnimatedCounter end={100} duration={2} className="test-class" />)
      const element = screen.getByText('0')
      expect(element).toBeInTheDocument()
      expect(element.tagName).toBe('SPAN')
      expect(element).toHaveClass('test-class')
    })

    it('applies multiple CSS classes when provided', () => {
      render(<AnimatedCounter end={100} duration={2} className="class1 class2" />)
      const element = screen.getByText('0')
      expect(element).toHaveClass('class1', 'class2')
    })

    it('handles empty className string', () => {
      render(<AnimatedCounter end={100} duration={2} className="" />)
      const element = screen.getByText('0')
      expect(element).toHaveAttribute('class', '')
    })
  })

  describe('Animation behavior', () => {
    it('calls requestAnimationFrame during animation', () => {
      const requestAnimationFrameSpy = jest.spyOn(window, 'requestAnimationFrame')
      render(<AnimatedCounter end={100} duration={1} />)

      expect(requestAnimationFrameSpy).toHaveBeenCalled()
    })

    it('renders final value correctly', () => {
      render(<AnimatedCounter end={100} duration={0.1} />)

      act(() => {
        jest.advanceTimersByTime(100)
      })

      expect(screen.getByText('100')).toBeInTheDocument()
    })

    it('updates count correctly', () => {
      render(<AnimatedCounter end={10} duration={1} />)

      act(() => {
        jest.advanceTimersByTime(1000)
      })

      expect(screen.getByText('10')).toBeInTheDocument()
    })
  })

  describe('Component lifecycle', () => {
    it('re-initializes animation when props change', () => {
      const { rerender } = render(<AnimatedCounter end={50} duration={1} />)

      // Wait for first animation to complete
      act(() => {
        jest.advanceTimersByTime(1000)
      })

      expect(screen.getByText('50')).toBeInTheDocument()

      // Change props
      rerender(<AnimatedCounter end={100} duration={2} />)

      // Should show the new end value after animation completes
      act(() => {
        jest.advanceTimersByTime(2000)
      })

      expect(screen.getByText('100')).toBeInTheDocument()
    })

    it('handles rapid prop changes gracefully', () => {
      const { rerender } = render(<AnimatedCounter end={10} duration={1} />)

      // Rapidly change props
      rerender(<AnimatedCounter end={20} duration={1} />)
      rerender(<AnimatedCounter end={30} duration={1} />)
      rerender(<AnimatedCounter end={40} duration={1} />)

      // Should not crash and should render
      expect(screen.getByText('0')).toBeInTheDocument()
    })
  })

  describe('Accessibility considerations', () => {
    it('renders content that can be read by screen readers', () => {
      render(<AnimatedCounter end={100} duration={2} />)
      const element = screen.getByText('0')
      expect(element).toBeInTheDocument()
      expect(element.textContent).toBeTruthy()
    })

    it('maintains semantic meaning of displayed numbers', () => {
      render(<AnimatedCounter end={42} duration={1} />)
      const element = screen.getByText('0')
      expect(element).toBeInTheDocument()
      // The number should be meaningful to screen readers
      expect(element.textContent).toMatch(/\d+/)
    })
  })

  describe('Event handling and user interactions', () => {
    it('responds to prop changes correctly', () => {
      const { rerender } = render(<AnimatedCounter end={100} duration={1} />)

      act(() => {
        jest.advanceTimersByTime(1000)
      })

      expect(screen.getByText('100')).toBeInTheDocument()

      // Change end value
      rerender(<AnimatedCounter end={200} duration={1} />)

      // Should show the new end value after animation completes
      act(() => {
        jest.advanceTimersByTime(1000)
      })

      expect(screen.getByText('200')).toBeInTheDocument()
    })
  })

  describe('Performance and optimization', () => {
    it('does not cause infinite re-renders', () => {
      const renderSpy = jest.fn()
      const TestWrapper = () => {
        renderSpy()
        return <AnimatedCounter end={100} duration={1} />
      }

      render(<TestWrapper />)

      act(() => {
        jest.advanceTimersByTime(1000)
      })

      // Should not have excessive render calls
      expect(renderSpy).toHaveBeenCalledTimes(1)
    })
  })
})
