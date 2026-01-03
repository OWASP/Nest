import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { CSSProperties, ReactNode } from 'react'
import { Sponsor } from 'types/home'
import LogoCarousel from 'components/LogoCarousel'

expect.extend(toHaveNoViolations)

jest.mock('next/image', () => {
  return function MockImage({
    src,
    alt,
    style,
    fill,
  }: {
    src: string
    alt: string
    style?: CSSProperties
    fill?: boolean
  }) {
    // eslint-disable-next-line @next/next/no-img-element
    return <img src={src} alt={alt} style={style} data-testid="sponsor-image" data-fill={fill} />
  }
})

jest.mock('next/link', () => {
  return function MockLink({
    href,
    children,
    target,
    rel,
    className,
  }: {
    href: string
    children: ReactNode
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
    name: 'Test Sponsor 1',
    imageUrl: 'https://example.com/logo1.png',
    url: 'https://sponsor1.com',
    sponsorType: 'Gold',
  },
  {
    name: 'Test Sponsor 2',
    imageUrl: 'https://example.com/logo2.png',
    url: 'https://sponsor2.com',
    sponsorType: 'Silver',
  },
  {
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
