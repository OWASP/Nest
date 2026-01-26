import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import React from 'react'
import { Sponsor } from 'types/home'
import LogoCarousel from 'components/LogoCarousel'

jest.mock('next/link', () => {
  return function MockLink({
    href,
    children,
    target,
    rel,
    className,
  }: {
    href: string
    children: React.ReactNode
    target?: string
    rel?: string
    className?: string
  }) {
    return (
      <a href={href} target={target} rel={rel} className={className} data-testid="sponsor-link">
        {children}
      </a>
    )
  }
})

const mockSponsors: Sponsor[] = [
  {
    id: 'sponsor-1-a11y',
    name: 'Test Sponsor 1',
    imageUrl: 'https://example.com/logo1.png',
    url: 'https://sponsor1.com',
    sponsorType: 'Gold',
  },
  {
    id: 'sponsor-2-a11y',
    name: 'Test Sponsor 2',
    imageUrl: 'https://example.com/logo2.png',
    url: 'https://sponsor2.com',
    sponsorType: 'Silver',
  },
  {
    id: 'sponsor-3-a11y',
    name: 'Test Sponsor 3',
    imageUrl: '',
    url: 'https://sponsor3.com',
    sponsorType: 'Bronze',
  },
]

describe('LogoCarousel a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<LogoCarousel sponsors={mockSponsors} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
