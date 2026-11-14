import { screen, render, cleanup } from '@testing-library/react'
import React from 'react'
import ShareButtons from 'components/ShareButtons'

jest.mock('next/link', () => {
  return ({
    children,
    href,
    target,
    rel,
    ...rest
  }: {
    children: React.ReactNode
    href: string
    target?: string
    rel?: string
    'aria-label'?: string
    className?: string
  }) => (
    <a href={href} target={target} rel={rel} aria-label={rest['aria-label']}>
      {children}
    </a>
  )
})

jest.mock('react-icons/fa6', () => ({
  FaLinkedinIn: () => <span data-testid="linkedin-icon" />,
  FaXTwitter: () => <span data-testid="x-twitter-icon" />,
}))

describe('ShareButtons', () => {
  afterEach(() => {
    cleanup()
    jest.clearAllMocks()
  })

  it('renders both share links', () => {
    render(
      <ShareButtons
        title="Test Snapshot"
        url="https://nest.owasp.org/community/snapshots/2025-01"
      />
    )

    const links = screen.getAllByRole('link')
    expect(links).toHaveLength(2)
  })

  it('renders X/Twitter share link with correct URL', () => {
    render(
      <ShareButtons
        title="Test Snapshot"
        url="https://nest.owasp.org/community/snapshots/2025-01"
      />
    )

    const xLink = screen.getByLabelText('Share on X')
    expect(xLink).toHaveAttribute(
      'href',
      'https://x.com/intent/tweet?url=https%3A%2F%2Fnest.owasp.org%2Fcommunity%2Fsnapshots%2F2025-01&text=Test%20Snapshot'
    )
  })

  it('renders LinkedIn share link with correct URL', () => {
    render(
      <ShareButtons
        title="Test Snapshot"
        url="https://nest.owasp.org/community/snapshots/2025-01"
      />
    )

    const linkedinLink = screen.getByLabelText('Share on LinkedIn')
    expect(linkedinLink).toHaveAttribute(
      'href',
      'https://www.linkedin.com/sharing/share-offsite/?url=https%3A%2F%2Fnest.owasp.org%2Fcommunity%2Fsnapshots%2F2025-01'
    )
  })

  it('opens links in a new tab', () => {
    render(<ShareButtons title="Test Snapshot" url="https://nest.owasp.org/test" />)

    const links = screen.getAllByRole('link')
    links.forEach((link) => {
      expect(link).toHaveAttribute('target', '_blank')
      expect(link).toHaveAttribute('rel', 'noopener noreferrer')
    })
  })

  it('renders X/Twitter icon', () => {
    render(<ShareButtons title="Test" url="https://nest.owasp.org/test" />)

    expect(screen.getByTestId('x-twitter-icon')).toBeInTheDocument()
  })

  it('renders LinkedIn icon', () => {
    render(<ShareButtons title="Test" url="https://nest.owasp.org/test" />)

    expect(screen.getByTestId('linkedin-icon')).toBeInTheDocument()
  })

  it('encodes special characters in title and URL', () => {
    render(
      <ShareButtons title="Test & Snapshot <2025>" url="https://nest.owasp.org/path?a=1&b=2" />
    )

    const xLink = screen.getByLabelText('Share on X')
    expect(xLink.getAttribute('href')).toContain('Test%20%26%20Snapshot%20%3C2025%3E')
    expect(xLink.getAttribute('href')).toContain('url=')
  })

  it('has proper aria-labels for accessibility', () => {
    render(<ShareButtons title="Test" url="https://nest.owasp.org/test" />)

    expect(screen.getByLabelText('Share on X')).toBeInTheDocument()
    expect(screen.getByLabelText('Share on LinkedIn')).toBeInTheDocument()
  })
})
