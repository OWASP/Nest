import { render, screen, fireEvent } from '@testing-library/react'
import React from 'react'
import '@testing-library/jest-dom'
import MetricsScoreCircle from 'components/MetricsScoreCircle'
import userEvent from '@testing-library/user-event'

// Mock the Tooltip component from @heroui/tooltip
jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({
    children,
    content,
    placement,
  }: {
    children: React.ReactNode
    content: string
    placement: string
  }) => (
    <div data-testid="tooltip-wrapper" data-content={content} data-placement={placement}>
      {children}
    </div>
  ),
}))

describe('MetricsScoreCircle', () => {
  // Test 1: Renders successfully with minimal required props
  it('renders successfully with score prop', () => {
    render(<MetricsScoreCircle score={75} />)
    expect(screen.getByText('75')).toBeInTheDocument()
    expect(screen.getByText('Health')).toBeInTheDocument()
    expect(screen.getByText('Score')).toBeInTheDocument()
  })

  // Test 2: Text and content rendering
  it('displays the correct score value', () => {
    const score = 85
    render(<MetricsScoreCircle score={score} />)
    expect(screen.getByText(score.toString())).toBeInTheDocument()
  })

  it('displays static labels correctly', () => {
    render(<MetricsScoreCircle score={50} />)
    expect(screen.getByText('Health')).toBeInTheDocument()
    expect(screen.getByText('Score')).toBeInTheDocument()
  })

  // Test 3: Conditional rendering logic - Color schemes based on score
  describe('score-based styling', () => {
    it('applies green styling for high scores (>= 75)', () => {
      const { container } = render(<MetricsScoreCircle score={85} />)
      // Look for elements with green background classes
      const greenElement = container.querySelector('[class*="bg-green"]')
      expect(greenElement).toBeInTheDocument()
    })

    it('applies yellow styling for medium scores (50-74)', () => {
      const { container } = render(<MetricsScoreCircle score={65} />)
      // Look for elements with yellow background classes
      const yellowElement = container.querySelector('[class*="bg-yellow"]')
      expect(yellowElement).toBeInTheDocument()
    })

    it('applies red styling for low scores (< 50)', () => {
      const { container } = render(<MetricsScoreCircle score={25} />)
      // Look for elements with red background classes
      const redElement = container.querySelector('[class*="bg-red"]')
      expect(redElement).toBeInTheDocument()
    })

    it('applies correct styling at boundary values', () => {
      // Test score = 50 (should be yellow)
      const { container: container50 } = render(<MetricsScoreCircle score={50} />)
      expect(container50.querySelector('[class*="bg-yellow"]')).toBeInTheDocument()

      // Test score = 74 (should be yellow)
      const { container: container74 } = render(<MetricsScoreCircle score={74} />)
      expect(container74.querySelector('[class*="bg-yellow"]')).toBeInTheDocument()

      // Test score = 75 (should be green)
      const { container: container75 } = render(<MetricsScoreCircle score={75} />)
      expect(container75.querySelector('[class*="bg-green"]')).toBeInTheDocument()
    })
  })

  // Test 4: Conditional rendering - Pulse animation for very low scores
  it('shows pulse animation for scores below 30', () => {
    const { container } = render(<MetricsScoreCircle score={25} />)
    const pulseElement = container.querySelector('[class*="animate-pulse"]')
    expect(pulseElement).toBeInTheDocument()
  })

  it('does not show pulse animation for scores 30 and above', () => {
    const { container } = render(<MetricsScoreCircle score={30} />)
    const pulseElement = container.querySelector('[class*="animate-pulse"]')
    expect(pulseElement).not.toBeInTheDocument()
  })

  // Test 5: Tooltip functionality
  it('renders tooltip with correct content', () => {
    render(<MetricsScoreCircle score={75} />)
    const tooltipWrapper = screen.getByTestId('tooltip-wrapper')
    expect(tooltipWrapper).toHaveAttribute('data-content', 'Current Project Health Score')
    expect(tooltipWrapper).toHaveAttribute('data-placement', 'top')
  })

  // Test 6: DOM structure and classNames
  it('has correct DOM structure and classes', () => {
    const { container } = render(<MetricsScoreCircle score={75} />)

    // Check for main structural elements
    const tooltipWrapper = screen.getByTestId('tooltip-wrapper')
    expect(tooltipWrapper).toBeInTheDocument()

    // Check for elements with expected classes
    const circularElement = container.querySelector('[class*="rounded-full"]')
    expect(circularElement).toBeInTheDocument()

    const flexElement = container.querySelector('[class*="flex"]')
    expect(flexElement).toBeInTheDocument()
  })

  // Test 7: Handles edge cases and invalid inputs
  describe('edge cases', () => {
    it('handles score of 0', () => {
      render(<MetricsScoreCircle score={0} />)
      expect(screen.getByText('0')).toBeInTheDocument()
      // Should be red styling
      const { container } = render(<MetricsScoreCircle score={0} />)
      expect(container.querySelector('[class*="bg-red"]')).toBeInTheDocument()
    })

    it('handles score of 100', () => {
      render(<MetricsScoreCircle score={100} />)
      expect(screen.getByText('100')).toBeInTheDocument()
      // Should be green styling
      const { container } = render(<MetricsScoreCircle score={100} />)
      expect(container.querySelector('[class*="bg-green"]')).toBeInTheDocument()
    })

    it('handles negative scores', () => {
      render(<MetricsScoreCircle score={-10} />)
      expect(screen.getByText('-10')).toBeInTheDocument()
      // Should be red styling
      const { container } = render(<MetricsScoreCircle score={-10} />)
      expect(container.querySelector('[class*="bg-red"]')).toBeInTheDocument()
    })

    it('handles scores above 100', () => {
      render(<MetricsScoreCircle score={150} />)
      expect(screen.getByText('150')).toBeInTheDocument()
      // Should be green styling
      const { container } = render(<MetricsScoreCircle score={150} />)
      expect(container.querySelector('[class*="bg-green"]')).toBeInTheDocument()
    })

    it('handles decimal scores', () => {
      render(<MetricsScoreCircle score={75.5} />)
      expect(screen.getByText('75.5')).toBeInTheDocument()
    })
  })

  // Test 8: Accessibility
  it('has proper accessibility structure', () => {
    render(<MetricsScoreCircle score={75} />)

    // Check that the tooltip provides accessible description
    const tooltipWrapper = screen.getByTestId('tooltip-wrapper')
    expect(tooltipWrapper).toBeInTheDocument()

    // Verify text content is accessible
    expect(screen.getByText('75')).toBeInTheDocument()
    expect(screen.getByText('Health')).toBeInTheDocument()
    expect(screen.getByText('Score')).toBeInTheDocument()
  })

  // Test 9: Event handling - hover effects (visual testing through classes)
  it('has hover effect classes applied when clickable', () => {
    const { container } = render(<MetricsScoreCircle score={75} clickable={true} />)

    // Check for hover-related classes
    const hoverElement = container.querySelector('[class*="hover:"]')
    expect(hoverElement).toBeInTheDocument()
  })

  it('does not have hover effect classes when not clickable', () => {
    const { container } = render(<MetricsScoreCircle score={75} clickable={false} />)

    // Should not have hover-related classes
    const hoverElement = container.querySelector('[class*="hover:"]')
    expect(hoverElement).not.toBeInTheDocument()
  })

  // Test 10: Component integration test
  it('integrates all features correctly for a low score', () => {
    const { container } = render(<MetricsScoreCircle score={15} />)

    // Should have red styling
    expect(container.querySelector('[class*="bg-red"]')).toBeInTheDocument()

    // Should have pulse animation
    expect(container.querySelector('[class*="animate-pulse"]')).toBeInTheDocument()

    // Should display correct score
    expect(screen.getByText('15')).toBeInTheDocument()

    // Should have tooltip
    expect(screen.getByTestId('tooltip-wrapper')).toHaveAttribute(
      'data-content',
      'Current Project Health Score'
    )
  })

  it('integrates all features correctly for a high score', () => {
    const { container } = render(<MetricsScoreCircle score={90} />)

    // Should have green styling
    expect(container.querySelector('[class*="bg-green"]')).toBeInTheDocument()

    // Should NOT have pulse animation
    expect(container.querySelector('[class*="animate-pulse"]')).not.toBeInTheDocument()

    // Should display correct score
    expect(screen.getByText('90')).toBeInTheDocument()

    // Should have tooltip
    expect(screen.getByTestId('tooltip-wrapper')).toHaveAttribute(
      'data-content',
      'Current Project Health Score'
    )
  })

  // Test 11: Click handling functionality
  describe('click handling', () => {
    it('calls onClick when clickable and onClick provided', () => {
      const mockOnClick = jest.fn()
      render(<MetricsScoreCircle score={75} clickable={true} onClick={mockOnClick} />)

      const circleElement = screen.getByText('75').closest('.group')
      if (circleElement) {
        fireEvent.click(circleElement)
      }

      expect(mockOnClick).toHaveBeenCalledTimes(1)
    })

    it('does not call onClick when not clickable', () => {
      const mockOnClick = jest.fn()
      render(<MetricsScoreCircle score={75} clickable={false} onClick={mockOnClick} />)

      const circleElement = screen.getByText('75').closest('.group')
      if (circleElement) {
        fireEvent.click(circleElement)
      }

      expect(mockOnClick).not.toHaveBeenCalled()
    })

    it('does not call onClick when no onClick provided', () => {
      render(<MetricsScoreCircle score={75} clickable={true} />)

      const circleElement = screen.getByText('75').closest('.group')
      if (circleElement) {
        fireEvent.click(circleElement)
      }
      // Should not throw any errors - test passes if no exception is thrown
      expect(circleElement).toBeInTheDocument()
    })

    it('has cursor pointer when clickable', () => {
      const { container } = render(<MetricsScoreCircle score={75} clickable={true} />)

      const clickableElement = container.querySelector('[class*="cursor-pointer"]')
      expect(clickableElement).toBeInTheDocument()
    })

    it('does not have cursor pointer when not clickable', () => {
      const { container } = render(<MetricsScoreCircle score={75} clickable={false} />)

      const clickableElement = container.querySelector('[class*="cursor-pointer"]')
      expect(clickableElement).not.toBeInTheDocument()
    })
  })

  // Test 12: Accessibility for clickable component
  describe('accessibility for clickable component', () => {
    it('has button role when clickable', () => {
      render(<MetricsScoreCircle score={75} clickable={true} />)

      const buttonElement = screen.getByRole('button')
      expect(buttonElement).toBeInTheDocument()
    })

    it('does not have button role when not clickable', () => {
      render(<MetricsScoreCircle score={75} clickable={false} />)

      const buttonElement = screen.queryByRole('button')
      expect(buttonElement).not.toBeInTheDocument()
    })

    it('has tabIndex when clickable', () => {
      const { container } = render(<MetricsScoreCircle score={75} clickable={true} />)

      const clickableElement = container.querySelector('[tabindex="0"]')
      expect(clickableElement).toBeInTheDocument()
    })

    it('does not have tabIndex when not clickable', () => {
      const { container } = render(<MetricsScoreCircle score={75} clickable={false} />)

      const clickableElement = container.querySelector('[tabindex]')
      expect(clickableElement).not.toBeInTheDocument()
    })

    it('handles keyboard navigation when clickable', async() => {
      const mockOnClick = jest.fn()
      render(<MetricsScoreCircle score={75} clickable={true} onClick={mockOnClick} />)

      const buttonElement = screen.getByRole('button')
      const user= userEvent.setup()

      // Test Enter key
      buttonElement.focus()
      await user.keyboard('{Enter}')  
      expect(mockOnClick).toHaveBeenCalledTimes(1)

      // Test Space key
      await user.keyboard(' ')
      expect(mockOnClick).toHaveBeenCalledTimes(2)
    })

    it('does not handle keyboard navigation when not clickable', () => {
      const mockOnClick = jest.fn()
      render(<MetricsScoreCircle score={75} clickable={false} onClick={mockOnClick} />)

      const circleElement = screen.getByText('75').closest('.group')
      if (circleElement) {
        fireEvent.keyDown(circleElement, { key: 'Enter' })
        fireEvent.keyDown(circleElement, { key: ' ' })
      }

      expect(mockOnClick).not.toHaveBeenCalled()
    })
  })

  // Test 13: Maintains existing functionality with new props
  it('maintains all existing functionality when clickable is true', () => {
    const { container } = render(<MetricsScoreCircle score={25} clickable={true} />)

    // Should still have red styling
    expect(container.querySelector('[class*="bg-red"]')).toBeInTheDocument()

    // Should still have pulse animation
    expect(container.querySelector('[class*="animate-pulse"]')).toBeInTheDocument()

    // Should still display correct score
    expect(screen.getByText('25')).toBeInTheDocument()

    // Should still have tooltip
    expect(screen.getByTestId('tooltip-wrapper')).toHaveAttribute(
      'data-content',
      'Current Project Health Score'
    )

    // Should have hover effects
    expect(container.querySelector('[class*="hover:"]')).toBeInTheDocument()
  })

  it('maintains all existing functionality when clickable is false', () => {
    const { container } = render(<MetricsScoreCircle score={25} clickable={false} />)

    // Should still have red styling
    expect(container.querySelector('[class*="bg-red"]')).toBeInTheDocument()

    // Should still have pulse animation
    expect(container.querySelector('[class*="animate-pulse"]')).toBeInTheDocument()

    // Should still display correct score
    expect(screen.getByText('25')).toBeInTheDocument()

    // Should still have tooltip
    expect(screen.getByTestId('tooltip-wrapper')).toHaveAttribute(
      'data-content',
      'Current Project Health Score'
    )

    // Should NOT have hover effects
    expect(container.querySelector('[class*="hover:"]')).not.toBeInTheDocument()
  })
})
