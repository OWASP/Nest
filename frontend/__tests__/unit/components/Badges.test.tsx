import React from 'react'
import { render, screen } from 'wrappers/testUtil'
import Badges from 'components/Badges'

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: ({ className }: { className?: string }) => (
    <span data-testid="fa-icon" className={className} />
  ),
}))

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}))

describe('Badges', () => {
  it('renders nothing when badges are empty', () => {
    const { container } = render(<Badges badges={[]} />)
    // HeroUI injects an overlay container by default; check that no badge content exists
    expect(container.querySelector('span[data-testid="fa-icon"]')).toBeNull()
  })

  it('renders up to max badges in compact mode and shows overflow count', () => {
    const badges = Array.from({ length: 8 }).map((_, i) => ({
      id: `badge-${i + 1}`,
      name: `Badge ${i + 1}`,
      cssClass: 'fa-solid fa-star',
    }))
    render(<Badges badges={badges} max={6} compact />)

    // 6 icons and +2 counter
    const icons = screen.getAllByTestId('fa-icon')
    expect(icons.length).toBe(6)
    expect(screen.getByText('+2')).toBeInTheDocument()
  })

  it('renders badges with FontAwesome icons', () => {
    const badges = [{ id: 'test-badge', name: 'Test Badge', cssClass: 'fa-solid fa-star' }]
    render(<Badges badges={badges} />)
    expect(screen.getByTestId('fa-icon')).toBeInTheDocument()
  })

  it('renders default medal icon when no cssClass provided', () => {
    const badges = [{ id: 'test-badge', name: 'Test Badge' }]
    render(<Badges badges={badges} />)
    expect(screen.getByTestId('fa-icon')).toBeInTheDocument()
  })
})
