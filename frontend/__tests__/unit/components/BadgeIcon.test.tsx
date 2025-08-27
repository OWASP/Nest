import React from 'react'
import { render, screen } from 'wrappers/testUtil'
import BadgeIcon from 'components/BadgeIcon'

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: ({ className }: { className?: string }) => (
    <span data-testid="fa-icon" className={className} />
  ),
}))

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}))

describe('BadgeIcon', () => {
  const mockBadge = {
    id: 'test-badge',
    name: 'Test Badge',
    description: 'A test badge',
    cssClass: 'fa-solid fa-star',
    weight: 1,
  }

  it('renders badge icon with correct cssClass', () => {
    render(<BadgeIcon badge={mockBadge} />)
    expect(screen.getByTestId('fa-icon')).toBeInTheDocument()
  })

  it('uses default medal icon when no cssClass provided', () => {
    const badgeWithoutCssClass = { ...mockBadge, cssClass: undefined }
    render(<BadgeIcon badge={badgeWithoutCssClass} />)
    expect(screen.getByTestId('fa-icon')).toBeInTheDocument()
  })

  it('applies custom className when provided', () => {
    render(<BadgeIcon badge={mockBadge} className="custom-class" />)
    const iconContainer = screen.getByTestId('fa-icon').parentElement
    expect(iconContainer).toHaveClass('custom-class')
  })
})
