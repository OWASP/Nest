import { sendGTMEvent } from '@next/third-parties/google'
import { render, screen, fireEvent } from '@testing-library/react'
import SearchBar from 'components/Search'

jest.mock('@next/third-parties/google', () => ({
  sendGTMEvent: jest.fn(),
}))

jest.mock('lodash/debounce', () => {
  return (fn: (...args: unknown[]) => unknown, delay: number) => {
    let tid: ReturnType<typeof setTimeout>
    const debounced = (...a: unknown[]) => {
      clearTimeout(tid)
      tid = setTimeout(() => fn(...a), delay)
    }
    debounced.cancel = () => clearTimeout(tid)
    return debounced
  }
})

describe('SearchBar Component', () => {
  const mockOnSearch = jest.fn()
  const defaultProps = {
    isLoaded: false,
    onSearch: mockOnSearch,
    placeholder: 'Search projects...',
  }

  beforeEach(() => {
    jest.clearAllMocks()
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.clearAllTimers()
    jest.useRealTimers()
  })

  describe('Renders successfully with minimal required props', () => {
    it('renders input with placeholder', () => {
      render(<SearchBar {...defaultProps} />)
      const input = screen.getByPlaceholderText('Search projects...')
      expect(input).toBeInTheDocument()
      expect(input).toHaveAttribute('type', 'text')
    })

    it('renders with correct input value', () => {
      render(<SearchBar {...defaultProps} />)
      const input = screen.getByPlaceholderText('Search projects...')
      expect(input).toHaveValue('')
    })
  })

  describe('Conditional rendering logic', () => {
    it('shows skeleton when isLoaded is true', () => {
      const { container } = render(<SearchBar {...defaultProps} isLoaded={true} />)
      const skeleton = container.querySelector('.h-12.rounded-lg:not(input)')
      const input = screen.queryByPlaceholderText('Search projects...')
      expect(input).not.toBeInTheDocument()
      expect(skeleton).toBeInTheDocument()
      expect(skeleton).toHaveClass('h-12 rounded-lg')
    })

    it('shows input when isLoaded is false', () => {
      const { container } = render(<SearchBar {...defaultProps} isLoaded={false} />)
      const skeleton = container.querySelector('.h-12.rounded-lg:not(input)')
      const input = screen.getByPlaceholderText('Search projects...')
      expect(skeleton).not.toBeInTheDocument()
      expect(input).toBeInTheDocument()
    })

    it('does not show clear button when searchQuery is empty', () => {
      const { container } = render(<SearchBar {...defaultProps} isLoaded={false} />)
      const input = screen.getByPlaceholderText('Search projects...')
      expect(input).toHaveValue('')
      const clearButton = container.querySelector('button.absolute.rounded-full[class*="right-2"]')
      expect(clearButton).not.toBeInTheDocument()
    })

    it('shows clear button when searchQuery is not empty', () => {
      const { container } = render(<SearchBar {...defaultProps} isLoaded={false} />)
      const input = screen.getByPlaceholderText('Search projects...')
      fireEvent.change(input, { target: { value: 'test' } })
      const clearButton = container.querySelector('button.absolute.rounded-full[class*="right-2"]')
      expect(clearButton).toBeInTheDocument()
    })
  })

  describe('Prop-based behavior – different props affect output', () => {
    it('uses initialValue prop as default search query', async () => {
      const initialValue = 'default search'
      render(<SearchBar {...defaultProps} isLoaded={false} initialValue={initialValue} />)
      const input = screen.getByPlaceholderText('Search projects...')

      expect(input).toHaveValue(initialValue)

      jest.advanceTimersByTime(750)

      expect(mockOnSearch).not.toHaveBeenCalled()
      expect(sendGTMEvent).not.toHaveBeenCalled()
    })

    it('renders with custom placeholder text', () => {
      const customPlaceholder = 'Search for anything...'
      render(<SearchBar {...defaultProps} placeholder={customPlaceholder} />)
      const input = screen.getByPlaceholderText(customPlaceholder)
      expect(input).toBeInTheDocument()
      expect(input).toHaveAttribute('placeholder', customPlaceholder)
    })
  })

  describe('Auto-focus functionality', () => {
    it('should auto-focus on initial render', () => {
      render(<SearchBar {...defaultProps} isLoaded={false} />)
      const input = screen.getByPlaceholderText('Search projects...')
      expect(input).toHaveFocus()
    })

    it('should not lose focus on re-renders', () => {
      const { rerender } = render(<SearchBar {...defaultProps} isLoaded={false} />)
      const input = screen.getByPlaceholderText('Search projects...')
      expect(input).toHaveFocus()
      
      rerender(<SearchBar {...defaultProps} isLoaded={false} placeholder="New placeholder" />)
      expect(input).toHaveFocus()
    })
  })

  describe('Event handling – simulate user actions and verify callbacks', () => {
    it('calls onSearch with debounced input value', async () => {
      render(<SearchBar {...defaultProps} isLoaded={false} />)
      const input = screen.getByPlaceholderText('Search projects...')

      fireEvent.change(input, { target: { value: 'test' } })

      expect(mockOnSearch).not.toHaveBeenCalled()

      jest.advanceTimersByTime(750)

      expect(mockOnSearch).toHaveBeenCalledWith('test')
    })

    it('clears input when clear button is clicked', async () => {
      const { container } = render(<SearchBar {...defaultProps} isLoaded={false} />)
      const input = screen.getByPlaceholderText('Search projects...')
      fireEvent.change(input, { target: { value: 'test' } })
      expect(input).toHaveValue('test')
      const clearButton = container.querySelector('button.absolute.rounded-full[class*="right-2"]')
      fireEvent.click(clearButton)
      expect(input).toHaveValue('')
    })

    it('calls onSearch when input value changes', async () => {
      render(<SearchBar {...defaultProps} isLoaded={false} />)
      const input = screen.getByPlaceholderText('Search projects...')
      fireEvent.change(input, { target: { value: 'test' } })

      expect(mockOnSearch).not.toHaveBeenCalled()

      jest.advanceTimersByTime(750)
      expect(mockOnSearch).toHaveBeenCalledWith('test')

      fireEvent.change(input, { target: { value: 'phase' } })

      jest.advanceTimersByTime(750)

      expect(mockOnSearch).toHaveBeenCalledWith('phase')
    })

    it('maintains focus management', async () => {
      render(<SearchBar {...defaultProps} />)

      const input = screen.getByPlaceholderText('Search projects...')
      fireEvent.focus(input)
      expect(input).toHaveFocus()
    })

    it('sends GTM event when search query is not empty', async () => {
      render(<SearchBar {...defaultProps} isLoaded={false} />)
      const input = screen.getByPlaceholderText('Search projects...')

      fireEvent.change(input, { target: { value: 'test' } })

      jest.advanceTimersByTime(750)

      expect(sendGTMEvent).toHaveBeenCalledWith({
        event: 'search',
        path: window.location.pathname,
        value: 'test',
      })
    })
  })

  describe('State changes / internal logic', () => {
    it('updates searchQuery state when input value changes', async () => {
      render(<SearchBar {...defaultProps} isLoaded={false} />)
      const input = screen.getByPlaceholderText('Search projects...')

      fireEvent.change(input, { target: { value: 'new query' } })

      expect(input).toHaveValue('new query')
      jest.advanceTimersByTime(750)
      expect(mockOnSearch).toHaveBeenCalledWith('new query')
      expect(sendGTMEvent).toHaveBeenCalledWith({
        event: 'search',
        path: window.location.pathname,
        value: 'new query',
      })

      fireEvent.change(input, { target: { value: 'change query' } })

      expect(input).toHaveValue('change query')
      jest.advanceTimersByTime(750)
      expect(mockOnSearch).toHaveBeenCalledWith('change query')
      expect(sendGTMEvent).toHaveBeenCalledWith({
        event: 'search',
        path: window.location.pathname,
        value: 'change query',
      })
    })

    it('maintains internal state correctly during rapid input changes', () => {
      render(<SearchBar {...defaultProps} isLoaded={false} />)
      const input = screen.getByPlaceholderText('Search projects...')

      fireEvent.change(input, { target: { value: 'a' } })
      fireEvent.change(input, { target: { value: 'ab' } })
      fireEvent.change(input, { target: { value: 'abc' } })

      expect(input).toHaveValue('abc')
    })
  })

  describe('Default values and fallbacks', () => {
    it('uses default empty string when no initialValue provided', () => {
      render(<SearchBar {...defaultProps} isLoaded={false} />)
      const input = screen.getByPlaceholderText('Search projects...')
      expect(input).toHaveValue('')
    })

    it('handles undefined props gracefully', () => {
      const minimalProps = {
        isLoaded: false,
        onSearch: mockOnSearch,
        placeholder: 'Search projects...',
      }
      render(<SearchBar {...minimalProps} />)
      const input = screen.getByPlaceholderText('Search projects...')
      expect(input).toBeInTheDocument()
      expect(input).toHaveValue('')
    })
  })

  describe('Text and content rendering', () => {
    it('renders the correct placeholder text', () => {
      render(<SearchBar {...defaultProps} isLoaded={false} />)
      const input = screen.getByPlaceholderText('Search projects...')
      expect(input).toBeInTheDocument()
      expect(input).toHaveAttribute('placeholder', 'Search projects...')
      expect(input).toHaveValue('')

      fireEvent.change(input, { target: { value: 'test' } })
      expect(input).toHaveValue('test')
    })

    it('displays typed text correctly in input', () => {
      render(<SearchBar {...defaultProps} isLoaded={false} />)
      const input = screen.getByPlaceholderText('Search projects...')

      const testValue = 'search term'
      fireEvent.change(input, { target: { value: testValue } })
      expect(input).toHaveValue(testValue)
    })
  })

  describe('Handles edge cases and invalid inputs', () => {
    it('handles empty input gracefully', () => {
      render(<SearchBar {...defaultProps} isLoaded={false} />)
      const input = screen.getByPlaceholderText('Search projects...')

      fireEvent.change(input, { target: { value: '' } })

      expect(input).toHaveValue('')
      expect(mockOnSearch).not.toHaveBeenCalled()
      expect(sendGTMEvent).not.toHaveBeenCalled()
    })

    it('handles special characters in input', () => {
      render(<SearchBar {...defaultProps} isLoaded={false} />)
      const input = screen.getByPlaceholderText('Search projects...')

      const specialChars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
      fireEvent.change(input, { target: { value: specialChars } })

      expect(input).toHaveValue(specialChars)
    })

    it('handles very long input strings', () => {
      render(<SearchBar {...defaultProps} isLoaded={false} />)
      const input = screen.getByPlaceholderText('Search projects...')

      const longString = 'balance'.repeat(140)
      fireEvent.change(input, { target: { value: longString } })

      expect(input).toHaveValue(longString)
    })

    it('cancels pending debounced search when clear button is clicked', async () => {
      const { container } = render(<SearchBar {...defaultProps} isLoaded={false} />)
      const input = screen.getByPlaceholderText('Search projects...')

      fireEvent.change(input, { target: { value: 'edge case' } })
      expect(mockOnSearch).not.toHaveBeenCalled()

      const clearButton = container.querySelector('button.absolute.rounded-full[class*="right-2"]')
      fireEvent.click(clearButton)

      jest.advanceTimersByTime(750)

      expect(mockOnSearch).toHaveBeenCalledTimes(1)
      expect(mockOnSearch).toHaveBeenCalledWith('')
      expect(mockOnSearch).not.toHaveBeenCalledWith('edge case')

      expect(input).toHaveValue('')
      expect(input).toHaveFocus()
    })
  })

  describe('Accessibility roles and labels', () => {
    it('has the correct accessibility labels', () => {
      const { container } = render(<SearchBar {...defaultProps} isLoaded={false} />)
      const input = screen.getByPlaceholderText('Search projects...')
      expect(input).toBeInTheDocument()
      expect(input).toHaveAttribute('type', 'text')
      let clearButton = container.querySelector('button.absolute.rounded-full[class*="right-2"]')
      expect(clearButton).not.toBeInTheDocument()
      fireEvent.change(input, { target: { value: 'test' } })
      clearButton = container.querySelector('button.absolute.rounded-full[class*="right-2"]')
      expect(clearButton).toBeInTheDocument()
    })

    it('provides proper ARIA attributes for screen readers', () => {
      render(<SearchBar {...defaultProps} isLoaded={false} />)
      const input = screen.getByPlaceholderText('Search projects...')
      expect(input).toHaveAttribute('type', 'text')
      expect(input).toHaveAttribute('placeholder', 'Search projects...')
    })
  })

  describe('DOM structure / classNames / styles', () => {
    it('has the correct class names and styles for input', () => {
      render(<SearchBar {...defaultProps} isLoaded={false} />)
      const input = screen.getByPlaceholderText('Search projects...')
      expect(input).toHaveClass(
        'h-12 w-full rounded-lg border-1 border-gray-300 pl-10 pr-10 text-lg text-black focus:border-blue-500 focus:outline-hidden focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:focus:border-blue-300 dark:focus:ring-blue-300'
      )
    })

    it('has the correct class names for skeleton', () => {
      const { container } = render(<SearchBar {...defaultProps} isLoaded={true} />)
      const skeleton = container.querySelector('.h-12.rounded-lg:not(input)')
      expect(skeleton).toHaveClass('h-12 rounded-lg')
    })

    it('has the correct class names for clear button', () => {
      const { container } = render(<SearchBar {...defaultProps} isLoaded={false} />)
      const input = screen.getByPlaceholderText('Search projects...')
      fireEvent.change(input, { target: { value: 'test' } })
      const clearButton = container.querySelector('button.absolute.rounded-full[class*="right-2"]')
      expect(clearButton).toHaveClass(
        'absolute right-2 top-1/2 -translate-y-1/2 rounded-full p-1 hover:bg-gray-100 focus:outline-hidden focus:ring-2 focus:ring-gray-300'
      )
    })

    it('has the correct class names for search icon', () => {
      render(<SearchBar {...defaultProps} isLoaded={false} />)
      const searchIcon = screen.getByRole('img', { hidden: true })
      expect(searchIcon).toHaveClass(
        'pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400'
      )
    })

    it('maintains proper DOM structure with all elements', () => {
      render(<SearchBar {...defaultProps} isLoaded={false} />)
      const input = screen.getByPlaceholderText('Search projects...')
      const searchIcon = screen.getByRole('img', { hidden: true })

      expect(input).toBeInTheDocument()
      expect(searchIcon).toBeInTheDocument()
    })
  })
})
