import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { FaCalendarAlt } from 'react-icons/fa'
import CalendarButton from 'components/CalendarButton'

const mockEvent = {
  title: 'Test Event',
  description: 'Test description',
  location: 'Test Location',
  startDate: '2025-12-01',
  endDate: '2025-12-02',
}

describe('CalendarButton Accessibility', () => {
  it('should not have any accessibility violations as an icon-only button', async () => {
    const { container } = render(<CalendarButton event={mockEvent} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when showLabel is enabled', async () => {
    const { container } = render(<CalendarButton event={mockEvent} showLabel />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when custom icon is provided', async () => {
    const { container } = render(<CalendarButton event={mockEvent} icon={<FaCalendarAlt />} />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
