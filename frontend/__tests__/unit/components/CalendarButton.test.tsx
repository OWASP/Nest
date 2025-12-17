/**
 * @jest-environment jsdom
 */

import { faCalendarDay, faCalendarPlus } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import getIcsFileUrl from 'utils/getIcsFileUrl'
import CalendarButton from 'components/CalendarButton'

jest.mock('utils/getIcsFileUrl')

const mockEvent = {
  title: 'Test Event',
  description: 'Test description',
  location: 'Test Location',
  startDate: '2025-12-01',
  endDate: '2025-12-02',
}

describe('CalendarButton', () => {
  const mockUrl = 'blob:http://localhost/mock-file'

  let appendSpy: jest.SpyInstance
  let clickSpy: jest.SpyInstance
  let createSpy: jest.SpyInstance

  beforeEach(() => {
    globalThis.URL.createObjectURL = jest.fn(() => 'mock-url')
    globalThis.URL.revokeObjectURL = jest.fn()
  })

  beforeEach(() => {
    globalThis.URL.createObjectURL = jest.fn(() => 'mock-url')
    globalThis.URL.revokeObjectURL = jest.fn()
    ;(getIcsFileUrl as jest.Mock).mockResolvedValue(mockUrl)

    appendSpy = jest.spyOn(document.body, 'appendChild')
    createSpy = jest.spyOn(document, 'createElement')

    clickSpy = jest.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})

    jest.spyOn(globalThis, 'alert').mockImplementation(() => {})
  })

  afterEach(() => {
    jest.restoreAllMocks()
  })

  describe('rendering', () => {
    it('renders without crashing', () => {
      render(<CalendarButton event={mockEvent} />)
      const button = screen.getByRole('button')
      expect(button).toBeInTheDocument()
    })

    it('renders as a button element', () => {
      render(<CalendarButton event={mockEvent} />)
      const button = screen.getByRole('button')
      expect(button.tagName).toBe('BUTTON')
    })

    it('renders default calendar-plus icon', () => {
      render(<CalendarButton event={mockEvent} />)
      const svg = document.querySelector('svg')
      expect(svg).toBeInTheDocument()
    })

    it('renders custom icon when provided', () => {
      render(
        <CalendarButton event={mockEvent} icon={<FaCalendarDay data-testid="custom-icon" />} />
      )
      expect(screen.getByTestId('custom-icon')).toBeInTheDocument()
    })

    it('renders custom JSX element as icon', () => {
      render(<CalendarButton event={mockEvent} icon={<span data-testid="custom-span">📅</span>} />)
      expect(screen.getByTestId('custom-span')).toBeInTheDocument()
      expect(screen.getByText('📅')).toBeInTheDocument()
    })
  })

  describe('functionality (download)', () => {
    it('generates ICS file and triggers download on click', async () => {
      render(<CalendarButton event={mockEvent} />)
      const button = screen.getByRole('button')

      fireEvent.click(button)

      expect(button).toBeDisabled()

      await waitFor(() => {
        expect(getIcsFileUrl).toHaveBeenCalledWith(mockEvent)
      })

      expect(createSpy).toHaveBeenCalledWith('a')

      const createdLink = createSpy.mock.results.find(
        (call) => call.value instanceof HTMLAnchorElement && call.value.href === mockUrl
      )?.value

      expect(createdLink).toBeDefined()
      expect(createdLink.download).toBe('invite.ics')

      expect(appendSpy).toHaveBeenCalledWith(createdLink)

      expect(clickSpy).toHaveBeenCalled()

      await waitFor(() => {
        expect(button).not.toBeDisabled()
      })
    })

    it('handles errors gracefully when generation fails', async () => {
      const errorMock = new Error('Failed to generate')
      ;(getIcsFileUrl as jest.Mock).mockRejectedValueOnce(errorMock)

      render(<CalendarButton event={mockEvent} />)
      const button = screen.getByRole('button')

      fireEvent.click(button)

      await waitFor(() => {
        expect(globalThis.alert).toHaveBeenCalledWith('Could not download calendar file.')
      })

      expect(button).not.toBeDisabled()
    })
  })

  describe('accessibility', () => {
    it('has aria-label with event title', () => {
      render(<CalendarButton event={mockEvent} />)
      const button = screen.getByRole('button')
      expect(button).toHaveAttribute('aria-label', 'Add Test Event to Calendar')
    })

    it('uses fallback for events without explicit title', () => {
      render(<CalendarButton event={{ ...mockEvent, title: 'Untitled' }} />)
      const button = screen.getByRole('button')
      expect(button).toHaveAttribute('aria-label', 'Add Untitled to Calendar')
    })
  })

  describe('className prop', () => {
    it('applies className to button', () => {
      render(<CalendarButton event={mockEvent} className="custom-class" />)
      const button = screen.getByRole('button')
      expect(button).toHaveClass('custom-class')
    })

    it('applies multiple classes', () => {
      render(<CalendarButton event={mockEvent} className="class-one class-two" />)
      const button = screen.getByRole('button')
      expect(button).toHaveClass('class-one')
      expect(button).toHaveClass('class-two')
    })

    it('handles empty className', () => {
      render(<CalendarButton event={mockEvent} className="" />)
      const button = screen.getByRole('button')
      expect(button).toBeInTheDocument()
    })
  })

  describe('iconClassName prop', () => {
    it('applies iconClassName to default icon', () => {
      render(<CalendarButton event={mockEvent} iconClassName="h-4 w-4 text-blue-500" />)
      const svg = document.querySelector('svg')
      expect(svg).toHaveClass('h-4')
      expect(svg).toHaveClass('w-4')
      expect(svg).toHaveClass('text-blue-500')
    })

    it('applies different size classes correctly', () => {
      const { rerender } = render(<CalendarButton event={mockEvent} iconClassName="h-4 w-4" />)
      let svg = document.querySelector('svg')
      expect(svg).toHaveClass('h-4', 'w-4')

      rerender(<CalendarButton event={mockEvent} iconClassName="h-6 w-6" />)
      svg = document.querySelector('svg')
      expect(svg).toHaveClass('h-6', 'w-6')
      expect(svg).not.toHaveClass('h-4')
    })

    it('uses default iconClassName when not provided', () => {
      render(<CalendarButton event={mockEvent} />)
      const svg = document.querySelector('svg')
      expect(svg).toHaveClass('h-4', 'w-4')
    })

    it('does not apply iconClassName when custom icon is provided', () => {
      render(
        <CalendarButton
          event={mockEvent}
          iconClassName="should-not-apply"
          icon={<span data-testid="custom">Icon</span>}
        />
      )
      const customIcon = screen.getByTestId('custom')
      expect(customIcon).not.toHaveClass('should-not-apply')
    })
  })

  describe('showLabel prop', () => {
    it('does not show label by default', () => {
      render(<CalendarButton event={mockEvent} />)
      expect(screen.queryByText('Add to Calendar')).not.toBeInTheDocument()
    })

    it('shows default label when showLabel is true', () => {
      render(<CalendarButton event={mockEvent} showLabel />)
      expect(screen.getByText('Add to Calendar')).toBeInTheDocument()
    })

    it('shows custom label when provided', () => {
      render(<CalendarButton event={mockEvent} showLabel label="Save Event" />)
      expect(screen.getByText('Save Event')).toBeInTheDocument()
      expect(screen.queryByText('Add to Calendar')).not.toBeInTheDocument()
    })
  })

  describe('label prop', () => {
    it('uses custom label text', () => {
      render(<CalendarButton event={mockEvent} showLabel label="Export ICS" />)
      expect(screen.getByText('Export ICS')).toBeInTheDocument()
    })

    it('label is not rendered without showLabel', () => {
      render(<CalendarButton event={mockEvent} label="Hidden Label" />)
      expect(screen.queryByText('Hidden Label')).not.toBeInTheDocument()
    })
  })

  describe('icon prop extensibility', () => {
    it('accepts icon as JSX', () => {
      render(
        <CalendarButton event={mockEvent} icon={<FaCalendarPlus className="custom-icon-class" />} />
      )
      const svg = document.querySelector('svg')
      expect(svg).toHaveClass('custom-icon-class')
    })

    it('accepts any React component as icon', () => {
      const CustomIcon = () => <div data-testid="react-component">Custom</div>
      render(<CalendarButton event={mockEvent} icon={<CustomIcon />} />)
      expect(screen.getByTestId('react-component')).toBeInTheDocument()
    })

    it('accepts SVG element as icon', () => {
      render(
        <CalendarButton
          event={mockEvent}
          icon={
            <svg data-testid="svg-icon" viewBox="0 0 24 24">
              <path d="M0 0h24v24H0z" />
            </svg>
          }
        />
      )
      expect(screen.getByTestId('svg-icon')).toBeInTheDocument()
    })
  })

  describe('reusability scenarios', () => {
    it('works in homepage event card context', () => {
      render(
        <CalendarButton
          event={{
            title: 'OWASP BeNeLux 2025',
            description: 'Annual conference',
            location: 'Belgium',
            startDate: '2025-12-02',
            endDate: '2025-12-03',
          }}
          className="text-gray-600 hover:text-gray-800 dark:text-gray-400"
          iconClassName="h-4 w-4"
        />
      )
      const button = screen.getByRole('button')
      expect(button).toHaveClass('text-gray-600')
      expect(button).toHaveClass('dark:text-gray-400')
    })

    it('works in poster page context with label', () => {
      render(
        <CalendarButton
          event={{
            title: 'Poster Event',
            startDate: '2025-12-15',
          }}
          showLabel
          label="Save to Calendar"
          className="btn btn-primary flex items-center gap-2"
        />
      )
      expect(screen.getByText('Save to Calendar')).toBeInTheDocument()
      const button = screen.getByRole('button')
      expect(button).toHaveClass('btn-primary')
    })
  })

  describe('long title overflow handling', () => {
    it('remains accessible with very long event titles', () => {
      const longTitle =
        'This Is A Very Long Event Title That Extends Beyond Normal Length With Additional Description'
      render(
        <CalendarButton
          event={{
            title: longTitle,
            startDate: '2026-06-22',
            endDate: '2026-06-26',
          }}
          className="flex-shrink-0"
        />
      )
      const button = screen.getByRole('button')
      expect(button).toBeInTheDocument()
      expect(button).toHaveAttribute('aria-label', `Add ${longTitle} to Calendar`)
    })

    it('maintains visibility with flex-shrink-0 class', () => {
      render(
        <CalendarButton
          event={{
            title: 'Very Long Event Title That Could Potentially Cause Overflow Issues',
            startDate: '2025-12-01',
          }}
          className="flex-shrink-0 text-gray-600"
        />
      )
      const button = screen.getByRole('button')
      expect(button).toHaveClass('flex-shrink-0')
      expect(button).toBeVisible()
    })

    it('works correctly in flex container with long text sibling', () => {
      const { container } = render(
        <div className="flex items-center justify-between gap-2">
          <button className="min-w-0 flex-1 truncate">
            This Is A Really Long Event Title That Should Be Truncated Properly
          </button>
          <CalendarButton
            event={{
              title: 'Event',
              startDate: '2025-12-01',
            }}
            className="flex-shrink-0"
          />
        </div>
      )
      const button = container.querySelector('button[aria-label="Add Event to Calendar"]')
      expect(button).toBeInTheDocument()
      expect(button).toHaveClass('flex-shrink-0')
    })
  })
})
