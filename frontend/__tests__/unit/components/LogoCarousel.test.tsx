import { render, screen, fireEvent } from '@testing-library/react'
import React from 'react'
import { Sponsor } from 'types/home'
import MovingLogos from 'components/LogoCarousel'

jest.mock('next/image', () => {
  return function MockImage({
    src,
    alt,
    style,
    fill,
  }: {
    src: string
    alt: string
    style?: React.CSSProperties
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

const mockSponsorsWithoutImages: Sponsor[] = [
  {
    name: 'No Image Sponsor',
    imageUrl: '',
    url: 'https://noimage.com',
    sponsorType: 'Bronze',
  },
]

const mockEmptySponsors: Sponsor[] = []

describe('MovingLogos (LogoCarousel)', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Basic Rendering', () => {
    it('renders successfully with minimal required props', () => {
      render(<MovingLogos sponsors={mockSponsors} />)

      expect(screen.getAllByTestId('sponsor-link')).toHaveLength(8)
      expect(screen.getAllByTestId('sponsor-image')).toHaveLength(4)
    })

    it('renders with empty sponsors array', () => {
      render(<MovingLogos sponsors={mockEmptySponsors} />)

      expect(screen.getByText(/These logos represent the corporate supporters/)).toBeInTheDocument()
      expect(screen.getByText(/If you're interested in sponsoring/)).toBeInTheDocument()
    })
  })

  describe('Conditional Rendering Logic', () => {
    it('renders images when imageUrl is provided', () => {
      render(<MovingLogos sponsors={mockSponsors} />)

      const images = screen.getAllByTestId('sponsor-image')
      expect(images).toHaveLength(4)

      expect(images[0]).toHaveAttribute('src', 'https://example.com/logo1.png')
      expect(images[0]).toHaveAttribute('alt', "Test Sponsor 1's logo")
      expect(images[1]).toHaveAttribute('src', 'https://example.com/logo2.png')
      expect(images[1]).toHaveAttribute('alt', "Test Sponsor 2's logo")
    })

    it('renders empty div when imageUrl is not provided', () => {
      render(<MovingLogos sponsors={mockSponsorsWithoutImages} />)

      const images = screen.queryAllByTestId('sponsor-image')
      expect(images).toHaveLength(0)
      expect(screen.getAllByTestId('sponsor-link')).toHaveLength(4)
    })

    it('handles mixed sponsors with and without images', () => {
      render(<MovingLogos sponsors={mockSponsors} />)

      const images = screen.getAllByTestId('sponsor-image')
      expect(images).toHaveLength(4)
      expect(screen.getAllByTestId('sponsor-link')).toHaveLength(8)
    })
  })

  describe('Prop-based Behavior', () => {
    it('renders different sponsors based on props', () => {
      const customSponsors: Sponsor[] = [
        {
          name: 'Custom Sponsor',
          imageUrl: 'https://custom.com/logo.png',
          url: 'https://custom.com',
          sponsorType: 'Platinum',
        },
      ]

      render(<MovingLogos sponsors={customSponsors} />)

      const images = screen.getAllByTestId('sponsor-image')
      expect(images[0]).toHaveAttribute('src', 'https://custom.com/logo.png')

      const sponsorLinks = screen
        .getAllByTestId('sponsor-link')
        .filter((link) => link.getAttribute('href') === 'https://custom.com')
      expect(sponsorLinks).toHaveLength(2)
    })

    it('calculates animation duration based on sponsors length', () => {
      render(<MovingLogos sponsors={mockSponsors} />)

      const scroller = document.querySelector('.animate-scroll')
      expect(scroller).toHaveStyle('animation-duration: 6s')
    })

    it('updates animation duration when sponsors change', () => {
      const { rerender } = render(<MovingLogos sponsors={mockSponsors} />)

      let scroller = document.querySelector('.animate-scroll')
      expect(scroller).toHaveStyle('animation-duration: 6s')

      const newSponsors = [...mockSponsors, ...mockSponsors]
      rerender(<MovingLogos sponsors={newSponsors} />)

      scroller = document.querySelector('.animate-scroll')
      expect(scroller).toHaveStyle('animation-duration: 12s')
    })
  })

  describe('Event Handling', () => {
    it('handles link clicks correctly', () => {
      render(<MovingLogos sponsors={mockSponsors} />)

      const links = screen.getAllByTestId('sponsor-link')
      expect(links).toHaveLength(8)

      expect(links[0]).toHaveAttribute('href', 'https://sponsor1.com')
      expect(links[0]).toHaveAttribute('target', '_blank')
      expect(links[0]).toHaveAttribute('rel', 'noopener noreferrer')

      expect(links[1]).toHaveAttribute('href', 'https://sponsor2.com')
      expect(links[1]).toHaveAttribute('target', '_blank')
      expect(links[1]).toHaveAttribute('rel', 'noopener noreferrer')
    })

    it('handles footer link clicks', () => {
      render(<MovingLogos sponsors={mockSponsors} />)

      const supportersLink = screen.getByText('this page')
      const donateLink = screen.getByText('click here')

      expect(supportersLink.closest('a')).toHaveAttribute('href', 'https://owasp.org/supporters/')
      expect(supportersLink.closest('a')).toHaveAttribute('target', '_blank')
      expect(supportersLink.closest('a')).toHaveAttribute('rel', 'noopener noreferrer')

      expect(donateLink.closest('a')).toHaveAttribute(
        'href',
        'https://owasp.org/donate/?reponame=www-project-nest&title=OWASP+Nest'
      )
      expect(donateLink.closest('a')).toHaveAttribute('target', '_blank')
      expect(donateLink.closest('a')).toHaveAttribute('rel', 'noopener noreferrer')
    })

    it('simulates click events without errors', () => {
      render(<MovingLogos sponsors={mockSponsors} />)

      const links = screen.getAllByTestId('sponsor-link')

      expect(() => {
        fireEvent.click(links[0])
        fireEvent.click(links[1])
      }).not.toThrow()
    })
  })

  describe('State Changes and Internal Logic', () => {
    it('duplicates innerHTML on mount and when sponsors change', () => {
      const { rerender } = render(<MovingLogos sponsors={mockSponsors} />)

      const sponsorLinks = screen
        .getAllByTestId('sponsor-link')
        .filter(
          (link) =>
            link.getAttribute('href') === 'https://sponsor1.com' ||
            link.getAttribute('href') === 'https://sponsor2.com' ||
            link.getAttribute('href') === 'https://sponsor3.com'
        )
      expect(sponsorLinks).toHaveLength(6)

      const newSponsors = [
        ...mockSponsors,
        { name: 'New Sponsor', imageUrl: '', url: 'https://new.com', sponsorType: 'Bronze' },
      ]
      rerender(<MovingLogos sponsors={newSponsors} />)

      const newSponsorLinks = screen
        .getAllByTestId('sponsor-link')
        .filter((link) => link.getAttribute('href') === 'https://new.com')
      expect(newSponsorLinks).toHaveLength(2)

      expect(newSponsorLinks[0]).toHaveAttribute('href', 'https://new.com')
      expect(newSponsorLinks[0]).toHaveAttribute('target', '_blank')
      expect(newSponsorLinks[0]).toHaveAttribute('rel', 'noopener noreferrer')
    })

    it('uses ref correctly for DOM manipulation', () => {
      render(<MovingLogos sponsors={mockSponsors} />)

      const scroller = document.querySelector('.animate-scroll')
      expect(scroller).toBeInTheDocument()
      expect(scroller).toHaveClass('animate-scroll', 'flex', 'w-full', 'gap-6')
    })
  })

  describe('Default Values and Fallbacks', () => {
    it('handles sponsors with missing optional properties gracefully', () => {
      const incompleteSponsors: Partial<Sponsor>[] = [
        {
          name: 'Incomplete Sponsor',
          url: 'https://incomplete.com',
        },
      ]

      render(<MovingLogos sponsors={incompleteSponsors as Sponsor[]} />)

      const incompleteLinks = screen
        .getAllByTestId('sponsor-link')
        .filter((link) => link.getAttribute('href') === 'https://incomplete.com')
      expect(incompleteLinks).toHaveLength(2)
    })

    it('provides fallback for empty imageUrl', () => {
      render(<MovingLogos sponsors={mockSponsorsWithoutImages} />)

      const imageContainer = document.querySelector('.relative.mb-4')
      expect(imageContainer).toBeInTheDocument()
      expect(imageContainer?.querySelector('img')).not.toBeInTheDocument()
    })

    it('uses generic fallback alt text when sponsor name is missing', () => {
      const sponsorWithoutName: Sponsor[] = [
        {
          name: '',
          imageUrl: 'https://example.com/logo.png',
          url: 'https://example.com',
          sponsorType: 'Gold',
        },
      ]

      render(<MovingLogos sponsors={sponsorWithoutName} />)

      const images = screen.getAllByTestId('sponsor-image')
      expect(images[0]).toHaveAttribute('alt', 'Sponsor logo')
    })
  })

  describe('Text and Content Rendering', () => {
    it('renders all required text content', () => {
      render(<MovingLogos sponsors={mockSponsors} />)

      expect(screen.getByText(/These logos represent the corporate supporters/)).toBeInTheDocument()
      expect(
        screen.getByText(/whose contributions fuel OWASP Foundation security initiatives/)
      ).toBeInTheDocument()
      expect(screen.getByText(/Visit/)).toBeInTheDocument()
      expect(screen.getByText(/this page/)).toBeInTheDocument()
      expect(screen.getByText(/to become a corporate supporter/)).toBeInTheDocument()
      expect(
        screen.getByText(/If you're interested in sponsoring the OWASP Nest project/)
      ).toBeInTheDocument()
      expect(screen.getByText(/❤️/)).toBeInTheDocument()
      expect(screen.getByText(/click here/)).toBeInTheDocument()
    })

    it('renders sponsor names correctly in alt attributes', () => {
      render(<MovingLogos sponsors={mockSponsors} />)

      const images = screen.getAllByTestId('sponsor-image')
      expect(images[0]).toHaveAttribute('alt', "Test Sponsor 1's logo")
      expect(images[1]).toHaveAttribute('alt', "Test Sponsor 2's logo")
    })

    it('renders image alt text correctly', () => {
      render(<MovingLogos sponsors={mockSponsors} />)

      const images = screen.getAllByTestId('sponsor-image')
      expect(images[0]).toHaveAttribute('alt', "Test Sponsor 1's logo")
      expect(images[1]).toHaveAttribute('alt', "Test Sponsor 2's logo")
    })
  })

  describe('Edge Cases and Invalid Inputs', () => {
    it('handles null/undefined sponsors gracefully', () => {
      expect(() => render(<MovingLogos sponsors={null as unknown as Sponsor[]} />)).toThrow()
    })

    it('handles sponsors with very long names', () => {
      const longNameSponsors: Sponsor[] = [
        {
          name: 'A'.repeat(1000),
          imageUrl: 'https://example.com/logo.png',
          url: 'https://example.com',
          sponsorType: 'Gold',
        },
      ]

      render(<MovingLogos sponsors={longNameSponsors} />)

      const images = screen.getAllByTestId('sponsor-image')
      expect(images[0]).toHaveAttribute('alt', 'A'.repeat(1000) + "'s logo")
      expect(images[1]).toHaveAttribute('alt', 'A'.repeat(1000) + "'s logo")
    })

    it('handles sponsors with special characters in names', () => {
      const specialCharSponsors: Sponsor[] = [
        {
          name: 'Sponsor & Co. (Ltd.) - "Special" <Characters>',
          imageUrl: 'https://example.com/logo.png',
          url: 'https://example.com',
          sponsorType: 'Gold',
        },
      ]

      render(<MovingLogos sponsors={specialCharSponsors} />)

      const images = screen.getAllByTestId('sponsor-image')
      expect(images[0]).toHaveAttribute(
        'alt',
        'Sponsor & Co. (Ltd.) - "Special" <Characters>\'s logo'
      )
      expect(images[1]).toHaveAttribute(
        'alt',
        'Sponsor & Co. (Ltd.) - "Special" <Characters>\'s logo'
      )
    })

    it('handles invalid URLs gracefully', () => {
      const invalidUrlSponsors: Sponsor[] = [
        {
          name: 'Invalid URL Sponsor',
          imageUrl: 'not-a-valid-url',
          url: 'also-not-valid',
          sponsorType: 'Gold',
        },
      ]

      render(<MovingLogos sponsors={invalidUrlSponsors} />)

      const images = screen.getAllByTestId('sponsor-image')
      expect(images[0]).toHaveAttribute('src', 'not-a-valid-url')

      const invalidLinks = screen
        .getAllByTestId('sponsor-link')
        .filter((link) => link.getAttribute('href') === 'also-not-valid')
      expect(invalidLinks).toHaveLength(2)
    })

    it('handles very large number of sponsors', () => {
      const manySponsors: Sponsor[] = Array.from({ length: 100 }, (_, i) => ({
        name: `Sponsor ${i}`,
        imageUrl: `https://example.com/logo${i}.png`,
        url: `https://sponsor${i}.com`,
        sponsorType: 'Gold',
      }))

      render(<MovingLogos sponsors={manySponsors} />)

      expect(screen.getAllByTestId('sponsor-link')).toHaveLength(202)
      expect(screen.getAllByTestId('sponsor-image')).toHaveLength(200)

      const scroller = document.querySelector('.animate-scroll')
      expect(scroller).toHaveStyle('animation-duration: 200s')
    })
  })

  describe('Accessibility Roles and Labels', () => {
    it('provides proper alt text for images', () => {
      render(<MovingLogos sponsors={mockSponsors} />)

      const images = screen.getAllByTestId('sponsor-image')
      expect(images[0]).toHaveAttribute('alt', "Test Sponsor 1's logo")
      expect(images[1]).toHaveAttribute('alt', "Test Sponsor 2's logo")
      expect(images[2]).toHaveAttribute('alt', "Test Sponsor 1's logo")
      expect(images[3]).toHaveAttribute('alt', "Test Sponsor 2's logo")
    })

    it('uses proper link attributes for accessibility', () => {
      render(<MovingLogos sponsors={mockSponsors} />)

      const links = screen.getAllByTestId('sponsor-link')
      for (const link of links) {
        expect(link).toHaveAttribute('target', '_blank')
        expect(link).toHaveAttribute('rel', 'noopener noreferrer')
      }
    })

    it('maintains semantic structure for screen readers', () => {
      render(<MovingLogos sponsors={mockSponsors} />)

      const sponsorLinks = screen.getAllByTestId('sponsor-link')
      for (const link of sponsorLinks) {
        expect(link).toBeInTheDocument()
        expect(link.tagName).toBe('A')
      }
    })

    it('provides descriptive text for external links', () => {
      render(<MovingLogos sponsors={mockSponsors} />)

      const supportersLink = screen.getByText('this page')
      const donateLink = screen.getByText('click here')

      expect(supportersLink.closest('a')).toHaveAttribute('href', 'https://owasp.org/supporters/')
      expect(donateLink.closest('a')).toHaveAttribute(
        'href',
        'https://owasp.org/donate/?reponame=www-project-nest&title=OWASP+Nest'
      )
    })
  })

  describe('DOM Structure, ClassNames, and Styles', () => {
    it('applies correct CSS classes', () => {
      render(<MovingLogos sponsors={mockSponsors} />)

      const overflowContainer = document.querySelector('.relative.overflow-hidden.py-2')
      expect(overflowContainer).toBeInTheDocument()

      const scroller = document.querySelector('.animate-scroll.flex.w-full.gap-6')
      expect(scroller).toBeInTheDocument()

      const sponsorContainers = document.querySelectorAll('[class*="min-w-[220px]"]')
      expect(sponsorContainers).toHaveLength(6)
    })

    it('applies correct styles to images', () => {
      render(<MovingLogos sponsors={mockSponsors} />)

      const images = screen.getAllByTestId('sponsor-image')
      for (const image of images) {
        expect(image).toHaveAttribute('style', 'object-fit: contain;')
        expect(image).toHaveAttribute('data-fill', 'true')
      }
    })

    it('maintains proper DOM hierarchy', () => {
      render(<MovingLogos sponsors={mockSponsors} />)

      const overflowContainer = document.querySelector('.relative.overflow-hidden')
      expect(overflowContainer).toBeInTheDocument()

      const scroller = overflowContainer?.querySelector('.animate-scroll')
      expect(scroller).toBeInTheDocument()

      const sponsorContainer = scroller?.querySelector('[class*="min-w-[220px]"]')
      expect(sponsorContainer).toBeInTheDocument()

      const link = sponsorContainer?.querySelector('a')
      expect(link).toBeInTheDocument()

      const imageContainer = link?.querySelector('.relative.mb-4')
      expect(imageContainer).toBeInTheDocument()
    })

    it('applies correct footer styling', () => {
      render(<MovingLogos sponsors={mockSponsors} />)

      const footer = screen
        .getByText(/These logos represent the corporate supporters/)
        .closest('div')
      expect(footer).toHaveClass(
        'text-muted-foreground',
        'mt-4',
        'flex',
        'w-full',
        'flex-col',
        'items-center',
        'justify-center',
        'text-center',
        'text-sm'
      )
    })

    it('applies correct link styling in footer', () => {
      render(<MovingLogos sponsors={mockSponsors} />)

      const supportersLink = screen.getByText('this page').closest('a')
      const donateLink = screen.getByText('click here').closest('a')

      expect(supportersLink).toHaveClass('text-primary', 'font-medium', 'hover:underline')
      expect(donateLink).toHaveClass('text-primary', 'font-medium', 'hover:underline')
    })

    it('sets correct minimum width for sponsor containers', () => {
      render(<MovingLogos sponsors={mockSponsors} />)

      const sponsorContainers = document.querySelectorAll('[class*="min-w-[220px]"]')
      expect(sponsorContainers).toHaveLength(6)

      for (const container of sponsorContainers) {
        expect(container).toHaveClass('min-w-[220px]')
      }
    })
  })
})
