import { faCalendarDay, faCalendarPlus } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { render, screen } from '@testing-library/react'
import CalendarButton from 'components/CalendarButton'

const mockEvent = {
  title: 'Test Event',
  description: 'Test description',
  location: 'Test Location',
  startDate: '2025-12-01',
  endDate: '2025-12-02',
}

describe('CalendarButton', () => {
  describe('rendering', () => {
    it('renders without crashing', () => {
      render(<CalendarButton event={mockEvent} />)
      const link = screen.getByRole('link')
      expect(link).toBeInTheDocument()
    })

    it('renders as an anchor element', () => {
      render(<CalendarButton event={mockEvent} />)
      const link = screen.getByRole('link')
      expect(link.tagName).toBe('A')
    })

    it('renders default FontAwesome calendar-plus icon', () => {
      render(<CalendarButton event={mockEvent} />)
      const svg = document.querySelector('svg')
      expect(svg).toBeInTheDocument()
    })

    it('renders custom icon when provided', () => {
      render(
        <CalendarButton
          event={mockEvent}
          icon={<FontAwesomeIcon icon={faCalendarDay} data-testid="custom-icon" />}
        />
      )
      expect(screen.getByTestId('custom-icon')).toBeInTheDocument()
    })

    it('renders custom JSX element as icon', () => {
      render(<CalendarButton event={mockEvent} icon={<span data-testid="custom-span">📅</span>} />)
      expect(screen.getByTestId('custom-span')).toBeInTheDocument()
      expect(screen.getByText('📅')).toBeInTheDocument()
    })
  })

  describe('link attributes', () => {
    it('has correct href with Google Calendar URL', () => {
      render(<CalendarButton event={mockEvent} />)
      const link = screen.getByRole('link')
      expect(link).toHaveAttribute('href')
      expect(link.getAttribute('href')).toContain('calendar.google.com')
    })

    it('opens in new tab', () => {
      render(<CalendarButton event={mockEvent} />)
      const link = screen.getByRole('link')
      expect(link).toHaveAttribute('target', '_blank')
    })

    it('has security attributes for external link', () => {
      render(<CalendarButton event={mockEvent} />)
      const link = screen.getByRole('link')
      expect(link).toHaveAttribute('rel', 'noopener noreferrer')
    })
  })

  describe('accessibility', () => {
    it('has aria-label with event title', () => {
      render(<CalendarButton event={mockEvent} />)
      const link = screen.getByRole('link')
      expect(link).toHaveAttribute('aria-label', 'Add Test Event to Google Calendar')
    })

    it('has title attribute for tooltip', () => {
      render(<CalendarButton event={mockEvent} />)
      const link = screen.getByRole('link')
      expect(link).toHaveAttribute('title', 'Add Test Event to Google Calendar')
    })

    it('uses fallback for events without explicit title', () => {
      render(<CalendarButton event={{ ...mockEvent, title: 'Untitled' }} />)
      const link = screen.getByRole('link')
      expect(link).toHaveAttribute('aria-label', 'Add Untitled to Google Calendar')
    })
  })

  describe('className prop', () => {
    it('applies className to anchor', () => {
      render(<CalendarButton event={mockEvent} className="custom-class" />)
      const link = screen.getByRole('link')
      expect(link).toHaveClass('custom-class')
    })

    it('applies multiple classes', () => {
      render(<CalendarButton event={mockEvent} className="class-one class-two" />)
      const link = screen.getByRole('link')
      expect(link).toHaveClass('class-one')
      expect(link).toHaveClass('class-two')
    })

    it('handles empty className', () => {
      render(<CalendarButton event={mockEvent} className="" />)
      const link = screen.getByRole('link')
      expect(link).toBeInTheDocument()
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
      expect(screen.queryByText('Add to Google Calendar')).not.toBeInTheDocument()
    })

    it('shows default label when showLabel is true', () => {
      render(<CalendarButton event={mockEvent} showLabel />)
      expect(screen.getByText('Add to Google Calendar')).toBeInTheDocument()
    })

    it('shows custom label when provided', () => {
      render(<CalendarButton event={mockEvent} showLabel label="Save Event" />)
      expect(screen.getByText('Save Event')).toBeInTheDocument()
      expect(screen.queryByText('Add to Google Calendar')).not.toBeInTheDocument()
    })
  })

  describe('label prop', () => {
    it('uses custom label text', () => {
      render(<CalendarButton event={mockEvent} showLabel label="Add to Calendar" />)
      expect(screen.getByText('Add to Calendar')).toBeInTheDocument()
    })

    it('label is not rendered without showLabel', () => {
      render(<CalendarButton event={mockEvent} label="Hidden Label" />)
      expect(screen.queryByText('Hidden Label')).not.toBeInTheDocument()
    })
  })

  describe('icon prop extensibility', () => {
    it('accepts FontAwesome icon as JSX', () => {
      render(
        <CalendarButton
          event={mockEvent}
          icon={<FontAwesomeIcon icon={faCalendarPlus} className="custom-icon-class" />}
        />
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

    it('accepts emoji as icon', () => {
      render(<CalendarButton event={mockEvent} icon={<span>📅</span>} />)
      expect(screen.getByText('📅')).toBeInTheDocument()
    })

    it('accepts custom element as icon', () => {
      render(
        <CalendarButton
          event={mockEvent}
          icon={<span data-testid="custom-element-icon">🗓️</span>}
        />
      )
      expect(screen.getByTestId('custom-element-icon')).toBeInTheDocument()
    })
  })

  describe('event data handling', () => {
    it('handles minimal event data', () => {
      render(
        <CalendarButton
          event={{
            title: 'Minimal Event',
            startDate: '2025-12-01',
          }}
        />
      )
      const link = screen.getByRole('link')
      expect(link.getAttribute('href')).toContain('text=Minimal')
    })

    it('handles full event data', () => {
      render(
        <CalendarButton
          event={{
            title: 'Full Event',
            description: 'Full description',
            location: 'Full location',
            startDate: '2025-12-01T10:00:00',
            endDate: '2025-12-01T11:00:00',
          }}
        />
      )
      const link = screen.getByRole('link')
      const href = link.getAttribute('href') || ''
      expect(href).toContain('text=Full')
      expect(href).toContain('details=')
      expect(href).toContain('location=')
    })

    it('handles Date objects', () => {
      render(
        <CalendarButton
          event={{
            title: 'Date Object Event',
            startDate: new Date('2025-12-01T10:00:00'),
            endDate: new Date('2025-12-01T11:00:00'),
          }}
        />
      )
      const link = screen.getByRole('link')
      expect(link.getAttribute('href')).toContain('calendar.google.com')
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
      const link = screen.getByRole('link')
      expect(link).toHaveClass('text-gray-600')
      expect(link).toHaveClass('dark:text-gray-400')
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
      const link = screen.getByRole('link')
      expect(link).toHaveClass('btn-primary')
    })

    it('works with custom styled icon', () => {
      render(
        <CalendarButton
          event={mockEvent}
          icon={
            <FontAwesomeIcon
              icon={faCalendarPlus}
              className="h-6 w-6 text-blue-500 hover:text-blue-700"
            />
          }
        />
      )
      const svg = document.querySelector('svg')
      expect(svg).toHaveClass('h-6')
      expect(svg).toHaveClass('text-blue-500')
    })
  })
})
