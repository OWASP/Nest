import React from 'react'
import { render, screen } from 'wrappers/testUtil'
import Badges from 'components/Badges'

jest.mock('next/image', () => ({
  __esModule: true,
  default: ({ src, alt }: { src: string; alt: string }) => (
    // eslint-disable-next-line @next/next/no-img-element
    <img src={src} alt={alt} />
  ),
}))

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
    expect(container.querySelector('img, span[data-testid="fa-icon"]')).toBeNull()
  })

  it('renders up to max badges in compact mode and shows overflow count', () => {
    const badges = Array.from({ length: 8 }).map((_, i) => ({
      name: `Badge ${i + 1}`,
      cssClass: 'fa-solid fa-star',
    }))
    render(<Badges badges={badges} max={6} compact />)

    // 6 icons and +2 counter
    const icons = screen.getAllByTestId('fa-icon')
    expect(icons.length).toBe(6)
    expect(screen.getByText('+2')).toBeInTheDocument()
  })

  it('supports local icons via cssClass local: prefix', () => {
    const badges = [{ name: 'OWASP', cssClass: 'local:owasp' }]
    render(<Badges badges={badges} />)

    const img = screen.getByRole('img') as HTMLImageElement
    expect(img.src).toContain('/images/icons/owasp.svg')
  })
})
