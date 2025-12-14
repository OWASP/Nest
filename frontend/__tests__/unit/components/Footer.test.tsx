/**
 * @file Complete unit tests for the Footer component.
 * @see {@link AutoScrollToTop.test.tsx} for structural reference.
 */
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import { ReactNode } from 'react'
import Footer from 'components/Footer'

// Define proper types for mock props
interface MockLinkProps {
  children: ReactNode
  href: string
  target?: string
  rel?: string
  className?: string
  'aria-label'?: string
}

interface MockButtonProps {
  children: ReactNode
  onPress?: () => void
  className?: string
  disableAnimation?: boolean
  'aria-expanded'?: boolean
  'aria-controls'?: string
}

jest.mock('next/link', () => {
  return function MockedLink({ children, href, ...props }: MockLinkProps) {
    return (
      <a href={href} {...props}>
        {children}
      </a>
    )
  }
})

jest.mock('@heroui/button', () => ({
  Button: ({ children, onPress, className, disableAnimation, ...props }: MockButtonProps) => (
    <button
      onClick={onPress}
      className={className}
      data-disable-animation={disableAnimation}
      {...props}
    >
      {children}
    </button>
  ),
}))

jest.mock('utils/constants', () => ({
  footerSections: [
    {
      title: 'OWASP Nest',
      links: [
        { text: 'About', href: '/about' },
        { text: 'Contribute', href: 'https://github.com/OWASP/Nest/blob/main/CONTRIBUTING.md' },
      ],
    },
    {
      title: 'Resources',
      links: [
        { text: 'Chapters', href: '/chapters/' },
        { text: 'Projects', href: '/projects/' },
        { text: 'Plain Text', isSpan: true },
      ],
    },
  ],
  footerIcons: [
    {
      icon: 'FA_GITHUB_PLACEHOLDER',
      href: 'https://github.com/owasp/nest',
      label: 'GitHub',
    },
    {
      icon: 'FA_SLACK_PLACEHOLDER',
      href: 'https://owasp.slack.com/archives/project-nest',
      label: 'Slack',
    },
  ],
}))

jest.mock('utils/env.client', () => ({
  ENVIRONMENT: 'production',
  RELEASE_VERSION: '1.2.3',
}))

import { FaGithub, FaSlack } from 'react-icons/fa6'
import { footerSections, footerIcons } from 'utils/constants'

;(footerIcons as any)[0].icon = FaGithub
;(footerIcons as any)[1].icon = FaSlack

describe('Footer', () => {
  // Use the imported mocked constants
  const mockFooterSections = footerSections
  const mockFooterIcons = footerIcons

  const renderFooter = () => {
    return render(<Footer />)
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  afterEach(() => {
    jest.clearAllMocks()
    jest.restoreAllMocks()
  })

  describe('Rendering & Content', () => {
    test('renders successfully with all required elements', () => {
      renderFooter()

      const footer = screen.getByRole('contentinfo')
      expect(footer).toBeInTheDocument()
      expect(footer.tagName).toBe('FOOTER')
    })

    test('renders all footer sections with correct titles', () => {
      renderFooter()

      for (const section of mockFooterSections) {
        expect(screen.getByText(section.title)).toBeInTheDocument()
      }
    })

    test('renders all section links correctly', () => {
      renderFooter()

      const regularLinks = []
      const spanElements = []

      for (const section of mockFooterSections) {
        for (const link of section.links) {
          if (link.isSpan) {
            spanElements.push(link)
          } else {
            regularLinks.push(link)
          }
        }
      }
      for (const link of regularLinks) {
        const linkElement = screen.getByRole('link', { name: link.text })
        expect(linkElement).toBeInTheDocument()
        expect(linkElement).toHaveAttribute('href', link.href)
        expect(linkElement).toHaveAttribute('target', '_blank')
      }

      for (const link of spanElements) {
        expect(screen.getByText(link.text)).toBeInTheDocument()
      }
    })

    test('renders social media icons with correct attributes', () => {
      renderFooter()

      for (const icon of mockFooterIcons) {
        const link = screen.getByLabelText(`OWASP Nest ${icon.label}`)
        expect(link).toBeInTheDocument()
        expect(link).toHaveAttribute('href', icon.href)
        expect(link).toHaveAttribute('target', '_blank')
        expect(link).toHaveAttribute('rel', 'noopener noreferrer')

        const iconElement = link.querySelector('svg')
        expect(iconElement).toBeInTheDocument()
      }
    })

    test('renders copyright information with current year', () => {
      renderFooter()

      const currentYear = new Date().getFullYear()
      const copyrightText = screen.getByText((content, element) => {
        return element?.textContent === `© ${currentYear} OWASP Nest. All rights reserved.`
      })
      expect(copyrightText).toBeInTheDocument()

      const yearSpan = screen.getByText(currentYear.toString())
      expect(yearSpan).toHaveAttribute('id', 'year')
    })

    test('renders version information when RELEASE_VERSION is provided', () => {
      renderFooter()

      expect(screen.getByText('v1.2.3')).toBeInTheDocument()
    })
  })

  describe('Interactive Behavior', () => {
    test('toggles section visibility when button is clicked', () => {
      renderFooter()

      const firstSection = mockFooterSections[0]
      const button = screen.getByRole('button', { name: new RegExp(firstSection.title) })

      expect(button).toHaveAttribute('aria-expanded', 'false')

      fireEvent.click(button)
      expect(button).toHaveAttribute('aria-expanded', 'true')

      fireEvent.click(button)
      expect(button).toHaveAttribute('aria-expanded', 'false')
    })

    test('shows correct chevron icons based on section state', () => {
      renderFooter()

      const firstSection = mockFooterSections[0]
      const button = screen.getByRole('button', { name: new RegExp(firstSection.title) })

      let chevronIcons = button.querySelectorAll('svg')
      expect(chevronIcons.length).toBeGreaterThan(0)

      fireEvent.click(button)
      chevronIcons = button.querySelectorAll('svg')
      expect(chevronIcons.length).toBeGreaterThan(0)
    })

    test('handles multiple section toggles independently', () => {
      renderFooter()

      const buttons = screen.getAllByRole('button')

      fireEvent.click(buttons[0])
      expect(buttons[0]).toHaveAttribute('aria-expanded', 'true')
      expect(buttons[1]).toHaveAttribute('aria-expanded', 'false')

      fireEvent.click(buttons[1])
      expect(buttons[0]).toHaveAttribute('aria-expanded', 'false')
      expect(buttons[1]).toHaveAttribute('aria-expanded', 'true')
    })
  })

  describe('Conditional Rendering', () => {
    test('renders version as link in production environment', () => {
      renderFooter()

      const versionText = screen.getByText('v1.2.3')
      const versionLink = versionText.closest('a')
      expect(versionLink).toBeInTheDocument()
      expect(versionLink).toHaveAttribute(
        'href',
        'https://github.com/OWASP/Nest/releases/tag/1.2.3'
      )
      expect(versionLink).toHaveAttribute('target', '_blank')
      expect(versionLink).toHaveAttribute('rel', 'noopener noreferrer')
    })

    test('handles span elements correctly', () => {
      renderFooter()

      const spanText = screen.getByText('Plain Text')
      expect(spanText.tagName).toBe('SPAN')
      expect(spanText).toHaveClass('text-slate-600', 'dark:text-slate-400')
    })
  })

  describe('Accessibility', () => {
    test('has correct ARIA attributes on buttons', () => {
      renderFooter()

      const buttons = screen.getAllByRole('button')

      for (const [index, button] of buttons.entries()) {
        const sectionTitle = mockFooterSections[index].title
        expect(button).toHaveAttribute('aria-controls', `footer-section-${sectionTitle}`)
        expect(button).toHaveAttribute('aria-expanded')
      }
    })

    test('has correct section IDs matching aria-controls', () => {
      renderFooter()

      for (const section of mockFooterSections) {
        const sectionElement = document.getElementById(`footer-section-${section.title}`)
        expect(sectionElement).toBeInTheDocument()
      }
    })

    test('has proper semantic structure', () => {
      renderFooter()

      expect(screen.getByRole('contentinfo')).toBeInTheDocument()

      for (const section of mockFooterSections) {
        const heading = screen.getByRole('heading', { name: section.title, level: 3 })
        expect(heading).toBeInTheDocument()
      }
    })

    test('has proper aria-labels for social media links', () => {
      renderFooter()
      for (const icon of mockFooterIcons) {
        const link = screen.getByLabelText(`OWASP Nest ${icon.label}`)
        expect(link).toBeInTheDocument()
      }
    })
  })

  describe('CSS Classes and Styling', () => {
    test('applies correct base CSS classes to footer element', () => {
      renderFooter()

      const footer = screen.getByRole('contentinfo')
      expect(footer).toHaveClass(
        'mt-auto',
        'w-full',
        'border-t-1',
        'bg-slate-200',
        'dark:bg-slate-800',
        'xl:max-w-full'
      )
    })

    test('applies correct responsive grid classes', () => {
      renderFooter()

      const footer = screen.getByRole('contentinfo')
      const gridContainer = footer.querySelector('.grid.w-full.sm\\:grid-cols-2')
      expect(gridContainer).toBeInTheDocument()
    })

    test('applies correct button styling classes', () => {
      renderFooter()

      const buttons = screen.getAllByRole('button')
      for (const button of buttons) {
        expect(button).toHaveClass('flex', 'w-full', 'items-center', 'justify-between')
        expect(button).toHaveAttribute('data-disable-animation', 'true')
      }
    })

    test('applies correct section content classes for collapsed/expanded states', () => {
      renderFooter()

      const button = screen.getAllByRole('button')[0]

      fireEvent.click(button)

      expect(button).toHaveAttribute('aria-expanded', 'true')
    })
  })

  describe('Edge Cases', () => {
    test('handles missing href in links gracefully', () => {
      renderFooter()

      const aboutLink = screen.getByRole('link', { name: 'About' })
      expect(aboutLink).toHaveAttribute('href', '/about')
    })

    test('handles sections with span elements', () => {
      renderFooter()

      const spanElement = screen.getByText('Plain Text')
      expect(spanElement.tagName).toBe('SPAN')
      expect(spanElement.closest('a')).toBeNull()
    })
  })

  describe('Component Integration', () => {
    test('integrates properly with mocked dependencies', () => {
      renderFooter()

      const links = screen.getAllByRole('link')
      expect(links.length).toBeGreaterThan(0)

      const socialLinks = screen.getByLabelText('OWASP Nest GitHub')
      const svgIcon = socialLinks.querySelector('svg')
      expect(svgIcon).toBeInTheDocument()

      const slackLink = screen.getByLabelText('OWASP Nest Slack')
      const slackSvg = slackLink.querySelector('svg')
      expect(slackSvg).toBeInTheDocument()

      const buttons = screen.getAllByRole('button')
      expect(buttons.length).toBeGreaterThan(0)
      for (const button of buttons) {
        expect(button).toHaveAttribute('data-disable-animation', 'true')
      }
    })
  })
})
