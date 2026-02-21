/**
 * @jest-environment jsdom
 */

import { addToast } from '@heroui/toast'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { FaCalendarDay, FaCalendarPlus } from 'react-icons/fa6'
import getIcsFileUrl from 'utils/getIcsFileUrl'
import slugify from 'utils/slugify'
import CalendarButton from 'components/CalendarButton'

jest.mock('utils/getIcsFileUrl')

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

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
    jest.clearAllMocks()
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
      expect(createdLink.download).toBe(`${slugify(mockEvent.title)}.ics`)
      expect(appendSpy).toHaveBeenCalledWith(createdLink)
      expect(clickSpy).toHaveBeenCalled()

      expect(addToast).toHaveBeenCalledWith({
        description: 'Successfully downloaded ICS file',
        title: `${mockEvent.title}`,
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'success',
        variant: 'solid',
      })

      await waitFor(() => {
        expect(button).not.toBeDisabled()
      })

      expect(addToast).toHaveBeenCalledTimes(1)
    })

    it('handles errors gracefully when generation fails', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})
      const errorMock = new Error('Failed to generate')
      ;(getIcsFileUrl as jest.Mock).mockRejectedValueOnce(errorMock)

      render(<CalendarButton event={mockEvent} />)
      const button = screen.getByRole('button')

      fireEvent.click(button)

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith({
          description: 'Failed to download ICS file',
          title: 'Download Failed',
          timeout: 3000,
          shouldShowTimeoutProgress: true,
          color: 'danger',
          variant: 'solid',
        })
        expect(consoleSpy).toHaveBeenCalledWith(
          expect.stringContaining('Failed to download ICS file'),
          errorMock
        )
      })

      await waitFor(() => {
        expect(button).not.toBeDisabled()
      })

      expect(addToast).not.toHaveBeenCalledWith(
        expect.objectContaining({
          color: 'success',
          title: `${mockEvent.title}`,
        })
      )
      expect(addToast).toHaveBeenCalledTimes(1)
      consoleSpy.mockRestore()
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

    it('uses "event" as fallback when title is missing', () => {
      render(<CalendarButton event={{ ...mockEvent, title: '' }} />)
      const button = screen.getByRole('button')
      expect(button).toHaveAttribute('aria-label', 'Add event to Calendar')
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

  describe('hover state', () => {
    it('toggles icon on hover - shows FaCalendarPlus when hovering', async () => {
      render(<CalendarButton event={mockEvent} />)
      const button = screen.getByRole('button')

      // Initially should show FaCalendar (not hovered)
      const initialIconMarkup = button.querySelector('svg')?.outerHTML

      // Simulate mouse enter
      fireEvent.mouseEnter(button)
      await waitFor(() => {
        // After hover, FaCalendarPlus should be shown (different SVG)
        const hoveredIconMarkup = button.querySelector('svg')?.outerHTML
        expect(hoveredIconMarkup).not.toBe(initialIconMarkup)
      })
    })

    it('reverts to FaCalendar icon when mouse leaves', async () => {
      render(<CalendarButton event={mockEvent} />)
      const button = screen.getByRole('button')

      // Capture initial icon (FaCalendar)
      const initialIconHtml = button.innerHTML

      // Mouse enter - hover state true
      fireEvent.mouseEnter(button)

      await waitFor(() => {
        // Icon should change to FaCalendarPlus
        expect(button.innerHTML).not.toEqual(initialIconHtml)
      })

      // Mouse leave - hover state false
      fireEvent.mouseLeave(button)

      await waitFor(() => {
        // Icon should revert to FaCalendar
        expect(button.innerHTML).toEqual(initialIconHtml)
      })
    })

    it('maintains button functionality during hover state transitions', async () => {
      render(<CalendarButton event={mockEvent} />)
      const button = screen.getByRole('button')

      fireEvent.mouseEnter(button)
      fireEvent.mouseLeave(button)

      expect(button).not.toBeDisabled()

      fireEvent.click(button)
      expect(button).toBeDisabled()

      await waitFor(() => {
        expect(button).not.toBeDisabled()
      })
    })
  })
})
