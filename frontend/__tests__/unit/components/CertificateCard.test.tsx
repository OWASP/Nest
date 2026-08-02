import {
  mockCertificate,
  mockCertificateNoName,
  mockRevokedCertificate,
} from '@mockData/mockCertificateData'
import { act, cleanup, render, screen } from '@testing-library/react'
import React from 'react'
import { CERTIFICATE_LAYOUT, CertificateCard } from 'components/CertificateCard'

jest.mock('next/image', () => ({
  __esModule: true,
  default: ({ src, alt }: { src: string; alt: string }) => (
    // eslint-disable-next-line @next/next/no-img-element
    <img src={src} alt={alt} />
  ),
}))

jest.mock('react-icons/fa6', () => ({
  FaAward: (props: React.SVGProps<SVGSVGElement>) => <svg data-testid="icon-award" {...props} />,
  FaCalendarDays: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="icon-calendar" {...props} />
  ),
  FaChartBar: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="icon-chart-bar" {...props} />
  ),
  FaCircleCheck: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="icon-circle-check" {...props} />
  ),
  FaCircleXmark: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="icon-circle-xmark" {...props} />
  ),
  FaGithub: (props: React.SVGProps<SVGSVGElement>) => <svg data-testid="icon-github" {...props} />,
  FaGlobe: (props: React.SVGProps<SVGSVGElement>) => <svg data-testid="icon-globe" {...props} />,
  FaShieldHalved: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="icon-shield" {...props} />
  ),
}))

jest.mock('utils/dateFormatter', () => ({
  formatDate: jest.fn((date: string) => `Formatted: ${date}`),
}))

describe('CERTIFICATE_LAYOUT', () => {
  it('exports expected layout dimensions', () => {
    expect(CERTIFICATE_LAYOUT.width).toBe(842)
    expect(CERTIFICATE_LAYOUT.height).toBe(595)
  })

  it('exports verify link position values', () => {
    expect(CERTIFICATE_LAYOUT.verifyLink).toMatchObject({
      x: expect.any(Number),
      y: expect.any(Number),
      width: expect.any(Number),
      height: expect.any(Number),
    })
  })
})

describe('CertificateCard', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  afterEach(() => {
    cleanup()
  })

  describe('Essential Rendering', () => {
    it('renders without crashing with a valid certificate', () => {
      render(<CertificateCard certificate={mockCertificate} />)

      expect(screen.getByText('Certificate of Recognition')).toBeInTheDocument()
    })

    it('renders OWASP logo image', () => {
      render(<CertificateCard certificate={mockCertificate} />)

      const logo = screen.getByAltText('OWASP Logo')
      expect(logo).toBeInTheDocument()
      expect(logo).toHaveAttribute('src', '/img/OWASP_logo.svg')
    })

    it('renders certificate card with id attribute', () => {
      render(<CertificateCard certificate={mockCertificate} />)

      expect(document.getElementById('certificate-card')).toBeInTheDocument()
    })
  })

  describe('Recipient Section', () => {
    it('renders user display name when name is provided', () => {
      render(<CertificateCard certificate={mockCertificate} />)

      expect(screen.getByText('Test User')).toBeInTheDocument()
    })

    it('falls back to login when name is null or undefined', () => {
      render(<CertificateCard certificate={mockCertificateNoName} />)

      expect(screen.getByText('noname-user')).toBeInTheDocument()
    })

    it('renders GitHub link with correct href', () => {
      render(<CertificateCard certificate={mockCertificate} />)

      const githubLink = screen.getByRole('link', { name: /@testuser/i })
      expect(githubLink).toHaveAttribute('href', 'https://github.com/testuser')
      expect(githubLink).toHaveAttribute('target', '_blank')
      expect(githubLink).toHaveAttribute('rel', 'noopener noreferrer')
    })

    it('renders GitHub login with @ prefix', () => {
      render(<CertificateCard certificate={mockCertificate} />)

      expect(screen.getByText('@testuser')).toBeInTheDocument()
    })

    it('renders user avatar with correct src and alt', () => {
      render(<CertificateCard certificate={mockCertificate} />)

      const avatar = screen.getByAltText('Test User')
      expect(avatar).toBeInTheDocument()
      expect(avatar).toHaveAttribute('src', 'https://avatars.githubusercontent.com/u/1234567?v=4')
    })

    it('uses login as avatar alt text when name is not provided', () => {
      render(<CertificateCard certificate={mockCertificateNoName} />)

      const avatar = screen.getByAltText('noname-user')
      expect(avatar).toBeInTheDocument()
    })
  })

  describe('Metrics Section', () => {
    it('renders contribution score', () => {
      render(<CertificateCard certificate={mockCertificate} />)

      expect(screen.getByText('350')).toBeInTheDocument()
    })

    it('renders tier in uppercase', () => {
      render(<CertificateCard certificate={mockCertificate} />)

      expect(screen.getByText('LEVEL 1')).toBeInTheDocument()
    })

    it('renders metrics labels', () => {
      render(<CertificateCard certificate={mockCertificate} />)

      expect(screen.getByText('Contribution Score')).toBeInTheDocument()
      expect(screen.getByText('Achievement Tier')).toBeInTheDocument()
    })

    it('renders metric icons', () => {
      render(<CertificateCard certificate={mockCertificate} />)

      expect(screen.getByTestId('icon-chart-bar')).toBeInTheDocument()
      expect(screen.getByTestId('icon-award')).toBeInTheDocument()
    })
  })

  describe('Footer Section', () => {
    it('renders certificate ID', () => {
      render(<CertificateCard certificate={mockCertificate} />)

      expect(screen.getByText('F9DD2BJ9ZYXW')).toBeInTheDocument()
    })

    it('renders formatted issue date', () => {
      render(<CertificateCard certificate={mockCertificate} />)

      expect(screen.getByText('Formatted: 2024-08-07T03:47:53.000Z')).toBeInTheDocument()
    })

    it('renders verify certificate link pointing to correct path', () => {
      render(<CertificateCard certificate={mockCertificate} />)

      const verifyLink = screen.getByRole('link', { name: /nest\.owasp\.org/i })
      expect(verifyLink).toHaveAttribute('href', '/certificate/F9DD2BJ9ZYXW')
      expect(verifyLink).toHaveAttribute('target', '_blank')
    })

    it('renders footer icons', () => {
      render(<CertificateCard certificate={mockCertificate} />)

      expect(screen.getByTestId('icon-shield')).toBeInTheDocument()
      expect(screen.getByTestId('icon-calendar')).toBeInTheDocument()
      expect(screen.getByTestId('icon-globe')).toBeInTheDocument()
    })
  })

  describe('Recognition Text', () => {
    it('renders recognition paragraph', () => {
      render(<CertificateCard certificate={mockCertificate} />)

      expect(
        screen.getByText(
          /In recognition of exceptional contributions to the global OWASP open-source ecosystem/
        )
      ).toBeInTheDocument()
    })
  })

  describe('Verification Badge (isPublicView)', () => {
    it('renders VerificationBadge when isPublicView=true and certificate is verified', () => {
      render(<CertificateCard certificate={mockCertificate} isPublicView={true} />)

      expect(screen.getByText('Verified Certificate')).toBeInTheDocument()
      expect(screen.getByTestId('icon-circle-check')).toBeInTheDocument()
    })

    it('renders RevokedBadge when isPublicView=true and certificate is not verified', () => {
      render(<CertificateCard certificate={mockRevokedCertificate} isPublicView={true} />)

      expect(screen.getAllByText('Revoked').length).toBeGreaterThan(0)
      expect(screen.getByTestId('icon-circle-xmark')).toBeInTheDocument()
    })

    it('does not render VerificationBadge when isPublicView=false (default)', () => {
      render(<CertificateCard certificate={mockCertificate} />)

      expect(screen.queryByText('Verified Certificate')).not.toBeInTheDocument()
      expect(screen.queryByTestId('icon-circle-check')).not.toBeInTheDocument()
    })

    it('does not render RevokedBadge when isPublicView=false even if certificate is revoked', () => {
      render(<CertificateCard certificate={mockRevokedCertificate} />)

      expect(screen.queryByTestId('icon-circle-xmark')).not.toBeInTheDocument()
    })
  })

  describe('Revoked Watermark', () => {
    it('renders RevokedWatermark when certificate is not verified', () => {
      render(<CertificateCard certificate={mockRevokedCertificate} />)

      const watermarks = screen.getAllByText('Revoked')
      expect(watermarks.length).toBeGreaterThan(0)
    })

    it('does not render RevokedWatermark when certificate is verified', () => {
      render(<CertificateCard certificate={mockCertificate} />)

      expect(screen.queryByText('Revoked')).not.toBeInTheDocument()
    })
  })

  describe('Scaling and Responsive Behaviour', () => {
    it('renders the outer container with w-full class', () => {
      const { container } = render(<CertificateCard certificate={mockCertificate} />)

      const outerDiv = container.firstChild as HTMLElement
      expect(outerDiv).toHaveClass('w-full')
    })

    it('applies scale style to the certificate card element', () => {
      render(<CertificateCard certificate={mockCertificate} />)

      const card = document.getElementById('certificate-card')
      expect(card).toHaveStyle({ transform: 'scale(1)' })
    })

    it('handles container resize via ResizeObserver and window resize event', () => {
      let observerCallback: (() => void) | null = null
      const mockObserver = jest.fn().mockImplementation((cb) => {
        observerCallback = cb
        return { observe: jest.fn(), disconnect: jest.fn(), unobserve: jest.fn() }
      })
      const originalResizeObserver = globalThis.ResizeObserver
      globalThis.ResizeObserver = mockObserver as unknown as typeof ResizeObserver

      const { container, unmount } = render(<CertificateCard certificate={mockCertificate} />)
      const outerDiv = container.firstChild as HTMLElement

      Object.defineProperty(outerDiv, 'clientWidth', { value: 421, configurable: true })

      if (observerCallback) {
        act(() => {
          ;(observerCallback as () => void)()
        })
      }

      act(() => {
        window.dispatchEvent(new Event('resize'))
      })

      const card = document.getElementById('certificate-card')
      expect(card).toHaveStyle({ transform: 'scale(0.5)' })

      unmount()

      globalThis.ResizeObserver = originalResizeObserver
    })

    it('uses window.innerWidth fallback when container clientWidth is 0', () => {
      const originalInnerWidth = window.innerWidth
      Object.defineProperty(window, 'innerWidth', { value: 421, configurable: true })

      render(<CertificateCard certificate={mockCertificate} />)

      const card = document.getElementById('certificate-card')
      expect(card).toHaveStyle({ transform: 'scale(0.5)' })

      Object.defineProperty(window, 'innerWidth', { value: originalInnerWidth, configurable: true })
    })

    it('handles environment where ResizeObserver is not in window', () => {
      const originalResizeObserver = globalThis.ResizeObserver
      delete (globalThis as Record<string, unknown>).ResizeObserver

      const { unmount } = render(<CertificateCard certificate={mockCertificate} />)
      expect(screen.getByText('Certificate of Recognition')).toBeInTheDocument()

      unmount()
      globalThis.ResizeObserver = originalResizeObserver
    })

    it('handles resize callback when containerRef.current is null', () => {
      expect.assertions(0)
      let resizeHandler: (() => void) | null = null
      const spy = jest.spyOn(window, 'addEventListener').mockImplementation((event, handler) => {
        if (event === 'resize') resizeHandler = handler as () => void
      })

      const { unmount } = render(<CertificateCard certificate={mockCertificate} />)
      unmount()

      if (resizeHandler) {
        act(() => {
          ;(resizeHandler as () => void)()
        })
      }
      spy.mockRestore()
    })
  })

  describe('cardRef prop', () => {
    it('attaches cardRef to the inner certificate-card div', () => {
      const cardRef = React.createRef<HTMLDivElement>()
      render(<CertificateCard certificate={mockCertificate} cardRef={cardRef} />)

      expect(cardRef.current).not.toBeNull()
      expect(cardRef.current?.id).toBe('certificate-card')
    })
  })

  describe('Edge Cases', () => {
    it('renders correctly with a zero score', () => {
      const zeroScoreCert = { ...mockCertificate, score: 0 }
      render(<CertificateCard certificate={zeroScoreCert} />)

      expect(screen.getByText('0')).toBeInTheDocument()
    })

    it('renders tier text in uppercase for any lowercase tier value', () => {
      const lowerTierCert = { ...mockCertificate, tier: 'level 2' }
      render(<CertificateCard certificate={lowerTierCert} />)

      expect(screen.getByText('LEVEL 2')).toBeInTheDocument()
    })
  })
})
