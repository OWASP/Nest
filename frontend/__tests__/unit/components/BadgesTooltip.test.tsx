import React from 'react'
import { render, screen } from 'wrappers/testUtil'
import BadgesTooltip from 'components/BadgesTooltip'

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: ({ className }: { className?: string }) => (
    <span data-testid="fa-icon" className={className} />
  ),
}))

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}))

describe('BadgesTooltip', () => {
  it('renders nothing when no badges', () => {
    const { container } = render(<BadgesTooltip badges={[]} />)
    expect(container.querySelector('[data-testid="fa-icon"]')).toBeNull()
  })

  it('renders trigger icon when badges are present', () => {
    const badges = [{ name: 'A', cssClass: 'fa-solid fa-star' }]
    render(<BadgesTooltip badges={badges} />)
    expect(screen.getByTestId('fa-icon')).toBeInTheDocument()
  })
})
