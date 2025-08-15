import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons'
import { fireEvent, render, screen } from '@testing-library/react'
import React from 'react'
import ModuleList from 'components/ModuleList'

// Mock FontAwesome icons
jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: ({ icon, className }: { icon: unknown; className?: string }) => (
    <span
      data-testid={`icon-${icon === faChevronDown ? 'chevron-down' : icon === faChevronUp ? 'chevron-up' : 'unknown'}`}
      className={className}
    />
  ),
}))

// Mock HeroUI Button component
jest.mock('@heroui/button', () => ({
  Button: ({
    children,
    onPress,
    className,
    'aria-label': ariaLabel,
    disableAnimation: _disableAnimation,
    ..._props
  }: {
    children: React.ReactNode
    onPress: () => void
    className?: string
    'aria-label'?: string
    disableAnimation?: boolean
    [key: string]: unknown
  }) => (
    <button
      onClick={onPress}
      className={className}
      aria-label={ariaLabel}
      data-testid="hero-button"
    >
      {children}
    </button>
  ),
}))

describe('ModuleList', () => {
  describe('Empty and Null Cases', () => {
    it('returns null when modules array is empty', () => {
      const { container } = render(<ModuleList modules={[]} />)
      expect(container.firstChild).toBeNull()
    })

    it('returns null when modules is undefined', () => {
      const { container } = render(<ModuleList modules={undefined} />)
      expect(container.firstChild).toBeNull()
    })

    it('returns null when modules is null', () => {
      const { container } = render(<ModuleList modules={null} />)
      expect(container.firstChild).toBeNull()
    })
  })

  describe('Rendering with Different Module Counts', () => {
    it('renders all modules when count is less than 5', () => {
      const modules = ['Module 1', 'Module 2', 'Module 3']
      render(<ModuleList modules={modules} />)

      expect(screen.getByText('Module 1')).toBeInTheDocument()
      expect(screen.getByText('Module 2')).toBeInTheDocument()
      expect(screen.getByText('Module 3')).toBeInTheDocument()

      // Should not show "Show more" button
      expect(screen.queryByText('Show more')).not.toBeInTheDocument()
    })

    it('renders all modules when count is exactly 5', () => {
      const modules = ['Module 1', 'Module 2', 'Module 3', 'Module 4', 'Module 5']
      render(<ModuleList modules={modules} />)

      modules.forEach((module) => {
        expect(screen.getByText(module)).toBeInTheDocument()
      })

      // Should not show "Show more" button
      expect(screen.queryByText('Show more')).not.toBeInTheDocument()
    })

    it('renders only first 5 modules when count is greater than 5', () => {
      const modules = [
        'Module 1',
        'Module 2',
        'Module 3',
        'Module 4',
        'Module 5',
        'Module 6',
        'Module 7',
      ]
      render(<ModuleList modules={modules} />)

      // First 5 should be visible
      expect(screen.getByText('Module 1')).toBeInTheDocument()
      expect(screen.getByText('Module 2')).toBeInTheDocument()
      expect(screen.getByText('Module 3')).toBeInTheDocument()
      expect(screen.getByText('Module 4')).toBeInTheDocument()
      expect(screen.getByText('Module 5')).toBeInTheDocument()

      // Last 2 should not be visible initially
      expect(screen.queryByText('Module 6')).not.toBeInTheDocument()
      expect(screen.queryByText('Module 7')).not.toBeInTheDocument()

      // Should show "Show more" button
      expect(screen.getByText('Show more')).toBeInTheDocument()
    })
  })

  describe('Show More/Less Functionality', () => {
    const manyModules = Array.from({ length: 8 }, (_, i) => `Module ${i + 1}`)

    it('shows "Show more" button with correct aria-label initially', () => {
      render(<ModuleList modules={manyModules} />)

      const button = screen.getByRole('button', { name: 'Show more modules' })
      expect(button).toBeInTheDocument()
      expect(screen.getByText('Show more')).toBeInTheDocument()
      expect(screen.getByTestId('icon-chevron-down')).toBeInTheDocument()
    })

    it('expands to show all modules when "Show more" is clicked', () => {
      render(<ModuleList modules={manyModules} />)

      // Initially only first 5 are visible
      expect(screen.getByText('Module 1')).toBeInTheDocument()
      expect(screen.getByText('Module 5')).toBeInTheDocument()
      expect(screen.queryByText('Module 6')).not.toBeInTheDocument()

      // Click "Show more"
      const showMoreButton = screen.getByText('Show more')
      fireEvent.click(showMoreButton)

      // Now all modules should be visible
      expect(screen.getByText('Module 6')).toBeInTheDocument()
      expect(screen.getByText('Module 7')).toBeInTheDocument()
      expect(screen.getByText('Module 8')).toBeInTheDocument()
    })

    it('changes to "Show less" button after expanding', () => {
      render(<ModuleList modules={manyModules} />)

      const showMoreButton = screen.getByText('Show more')
      fireEvent.click(showMoreButton)

      // Button should change to "Show less"
      expect(screen.getByText('Show less')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Show fewer modules' })).toBeInTheDocument()
      expect(screen.getByTestId('icon-chevron-up')).toBeInTheDocument()
      expect(screen.queryByText('Show more')).not.toBeInTheDocument()
    })

    it('collapses back to 5 modules when "Show less" is clicked', () => {
      render(<ModuleList modules={manyModules} />)

      // Expand first
      const showMoreButton = screen.getByText('Show more')
      fireEvent.click(showMoreButton)

      // Verify all are visible
      expect(screen.getByText('Module 8')).toBeInTheDocument()

      // Click "Show less"
      const showLessButton = screen.getByText('Show less')
      fireEvent.click(showLessButton)

      // Should be back to first 5 only
      expect(screen.getByText('Module 5')).toBeInTheDocument()
      expect(screen.queryByText('Module 6')).not.toBeInTheDocument()
      expect(screen.queryByText('Module 8')).not.toBeInTheDocument()

      // Button should be back to "Show more"
      expect(screen.getByText('Show more')).toBeInTheDocument()
    })
  })

  describe('Module Text Truncation', () => {
    it('truncates module names longer than 50 characters', () => {
      const longModuleName = 'A'.repeat(60) // 60 characters
      const modules = [longModuleName, 'Short Module']

      render(<ModuleList modules={modules} />)

      const expectedTruncated = 'A'.repeat(50) + '...'
      expect(screen.getByText(expectedTruncated)).toBeInTheDocument()
      expect(screen.queryByText(longModuleName)).not.toBeInTheDocument()
    })

    it('does not truncate module names 50 characters or shorter', () => {
      const exactlyFiftyChars = 'A'.repeat(50)
      const modules = [exactlyFiftyChars, 'Short']

      render(<ModuleList modules={modules} />)

      expect(screen.getByText(exactlyFiftyChars)).toBeInTheDocument()
      expect(screen.getByText('Short')).toBeInTheDocument()
    })

    it('adds title attribute for truncated modules', () => {
      const longModuleName =
        'This is a very long module name that exceeds fifty characters and should be truncated'
      const modules = [longModuleName]

      render(<ModuleList modules={modules} />)

      const truncatedButton = screen.getByRole('button', {
        name: /This is a very long module name that exceeds/,
      })
      expect(truncatedButton).toHaveAttribute('title', longModuleName)
    })

    it('does not add title attribute for non-truncated modules', () => {
      const shortModuleName = 'Short Module'
      const modules = [shortModuleName]

      render(<ModuleList modules={modules} />)

      const button = screen.getByRole('button', { name: shortModuleName })
      expect(button).not.toHaveAttribute('title')
    })
  })

  describe('Module Button Properties', () => {
    it('renders module buttons with correct classes', () => {
      const modules = ['Test Module']
      render(<ModuleList modules={modules} />)

      const button = screen.getByRole('button', { name: 'Test Module' })
      expect(button).toHaveClass(
        'rounded-lg',
        'border',
        'border-gray-400',
        'px-3',
        'py-1',
        'text-sm',
        'transition-all',
        'duration-200',
        'ease-in-out',
        'hover:scale-105',
        'hover:bg-gray-200',
        'dark:border-gray-300',
        'dark:hover:bg-gray-700'
      )
    })

    it('sets correct button type', () => {
      const modules = ['Test Module']
      render(<ModuleList modules={modules} />)

      const button = screen.getByRole('button', { name: 'Test Module' })
      expect(button).toHaveAttribute('type', 'button')
    })

    it('generates unique keys for modules with same name', () => {
      const modules = ['Same Name', 'Same Name', 'Different Name']
      render(<ModuleList modules={modules} />)

      const sameNameButtons = screen.getAllByText('Same Name')
      expect(sameNameButtons).toHaveLength(2)
      expect(screen.getByText('Different Name')).toBeInTheDocument()
    })
  })

  describe('Container Structure', () => {
    it('renders with correct container classes', () => {
      const modules = ['Module 1']
      const { container } = render(<ModuleList modules={modules} />)

      const outerDiv = container.firstChild as HTMLElement
      expect(outerDiv).toHaveClass('mt-3')

      const innerDiv = outerDiv.firstChild as HTMLElement
      expect(innerDiv).toHaveClass('flex', 'flex-wrap', 'items-center', 'gap-2')
    })
  })

  describe('Edge Cases', () => {
    it('handles modules with empty strings', () => {
      const modules = ['', 'Valid Module', '']
      render(<ModuleList modules={modules} />)

      const buttons = screen.getAllByRole('button')
      // Should render 3 buttons (including empty string ones)
      expect(buttons).toHaveLength(3)
      expect(screen.getByText('Valid Module')).toBeInTheDocument()
    })

    it('handles exactly 6 modules (edge case for show more)', () => {
      const modules = Array.from({ length: 6 }, (_, i) => `Module ${i + 1}`)
      render(<ModuleList modules={modules} />)

      // First 5 should be visible
      expect(screen.getByText('Module 5')).toBeInTheDocument()
      expect(screen.queryByText('Module 6')).not.toBeInTheDocument()

      // Should show "Show more" button
      expect(screen.getByText('Show more')).toBeInTheDocument()

      // Click to expand
      fireEvent.click(screen.getByText('Show more'))
      expect(screen.getByText('Module 6')).toBeInTheDocument()
    })
  })
})
