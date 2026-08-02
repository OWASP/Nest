import { useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import {
  mockCertificate,
  mockMyCertificatesData,
  mockMyCertificatesMultipleData,
} from '@mockData/mockCertificateData'
import { act, fireEvent, screen, waitFor } from '@testing-library/react'
import { useSession } from 'next-auth/react'
import React from 'react'
import { render } from 'wrappers/testUtil'
import MyCertificatePage from 'app/certificate/page'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

jest.mock('next-auth/react', () => ({
  useSession: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: jest.fn(() => ({ push: jest.fn() })),
}))

jest.mock(
  'html-to-image',
  () => ({
    toPng: jest.fn().mockResolvedValue('data:image/png;base64,mockImageData'),
  }),
  { virtual: true }
)

jest.mock(
  'jspdf',
  () => ({
    jsPDF: jest.fn().mockImplementation(() => ({
      addImage: jest.fn(),
      link: jest.fn(),
      save: jest.fn(),
    })),
  }),
  { virtual: true }
)

jest.mock('components/CertificateCard', () => {
  const MockCertificateCard = jest.fn(
    ({
      certificate,
      isPublicView,
      cardRef,
    }: {
      certificate: { id: string; tier: string; githubUser?: { login: string } }
      isPublicView?: boolean
      cardRef?: React.RefObject<HTMLDivElement>
    }) => (
      <div data-testid="certificate-card" ref={cardRef} data-public-view={isPublicView}>
        <span data-testid="cert-id">{certificate.id}</span>
        <span data-testid="cert-tier">{certificate.tier}</span>
        <a
          data-github-link="true"
          href={`https://github.com/${certificate.githubUser?.login ?? 'testuser'}`}
        >
          @{certificate.githubUser?.login ?? 'testuser'}
        </a>
      </div>
    )
  )
  return {
    __esModule: true,
    // eslint-disable-next-line @typescript-eslint/naming-convention
    CertificateCard: MockCertificateCard,
    CERTIFICATE_LAYOUT: {
      width: 842,
      height: 595,
      verifyLink: { x: 560, y: 530, width: 260, height: 40 },
    },
  }
})

jest.mock('components/LoadingSpinner', () => {
  const MockLoadingSpinner = () => <div role="status" aria-label="Loading" />
  MockLoadingSpinner.displayName = 'MockLoadingSpinner'
  return { __esModule: true, default: MockLoadingSpinner }
})

jest.mock('components/AccessDeniedDisplay', () => {
  const MockAccessDeniedDisplay = ({ title, message }: { title: string; message: string }) => (
    <div data-testid="access-denied">
      <h2>{title}</h2>
      <p>{message}</p>
    </div>
  )
  MockAccessDeniedDisplay.displayName = 'MockAccessDeniedDisplay'
  return { __esModule: true, default: MockAccessDeniedDisplay }
})

jest.mock('components/PageLayout', () => {
  const MockPageLayout = ({
    children,
    title,
  }: {
    children: React.ReactNode
    title: string
    breadcrumbClassName?: string
  }) => (
    <div data-testid="page-layout">
      <h1>{title}</h1>
      {children}
    </div>
  )
  MockPageLayout.displayName = 'MockPageLayout'
  return { __esModule: true, default: MockPageLayout }
})

jest.mock('components/ActionButton', () => {
  const MockActionButton = ({
    children,
    onClick,
    isDisabled,
    className,
  }: {
    children: React.ReactNode
    onClick?: () => void
    isDisabled?: boolean
    className?: string
  }) => (
    <button onClick={onClick} disabled={isDisabled} className={className}>
      {children}
    </button>
  )
  MockActionButton.displayName = 'MockActionButton'
  return { __esModule: true, default: MockActionButton }
})

describe('MyCertificatePage', () => {
  const mockUseQuery = useQuery as unknown as jest.Mock
  const mockUseSession = useSession as jest.Mock

  beforeEach(() => {
    jest.clearAllMocks()
    mockUseSession.mockReturnValue({
      data: {
        user: { name: 'Test User', login: 'testuser' },
        expires: '2099-01-01',
      },
      status: 'authenticated',
    })
    mockUseQuery.mockReturnValue({
      data: mockMyCertificatesData,
      loading: false,
      error: null,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  describe('Loading States', () => {
    it('renders loading spinner while session is loading', () => {
      mockUseSession.mockReturnValue({ data: null, status: 'loading' })

      render(<MyCertificatePage />)

      expect(screen.getByRole('status')).toBeInTheDocument()
    })

    it('renders loading spinner while query is loading and there is no data yet', () => {
      mockUseQuery.mockReturnValue({ data: null, loading: true, error: null })

      render(<MyCertificatePage />)

      expect(screen.getByRole('status')).toBeInTheDocument()
    })
  })

  describe('Authentication Guard', () => {
    it('renders AccessDeniedDisplay when session is null', () => {
      mockUseSession.mockReturnValue({ data: null, status: 'unauthenticated' })

      render(<MyCertificatePage />)

      expect(screen.getByTestId('access-denied')).toBeInTheDocument()
      expect(screen.getByText('Authentication Required')).toBeInTheDocument()
      expect(
        screen.getByText('Please log in to view and manage your certificate.')
      ).toBeInTheDocument()
    })
  })

  describe('No Certificate State', () => {
    it('renders "No Certificate Found" message when certificates array is empty', async () => {
      mockUseQuery.mockReturnValue({
        data: { myCertificates: [] },
        loading: false,
        error: null,
      })

      render(<MyCertificatePage />)

      await waitFor(() => {
        expect(screen.getByText('No Certificate Found')).toBeInTheDocument()
        expect(screen.getByText('Start Contributing')).toBeInTheDocument()
      })
    })
  })

  describe('Certificate Display', () => {
    it('renders the CertificateCard for the current certificate', async () => {
      render(<MyCertificatePage />)

      await waitFor(() => {
        expect(screen.getByTestId('certificate-card')).toBeInTheDocument()
        expect(screen.getByText("Test User's Certificate")).toBeInTheDocument()
        expect(screen.getByText('Save as Image')).toBeInTheDocument()
      })

      expect(screen.getByTestId('cert-id')).toHaveTextContent('F9DD2BJ9ZYXW')
    })

    it('uses login as display name when githubUser.name is not provided', async () => {
      mockUseQuery.mockReturnValue({
        data: {
          myCertificates: [
            {
              ...mockCertificate,
              githubUser: { login: 'loginonly', name: undefined, avatarUrl: '/avatar.png' },
            },
          ],
        },
        loading: false,
        error: null,
      })

      render(<MyCertificatePage />)

      await waitFor(() => {
        expect(screen.getByText("loginonly's Certificate")).toBeInTheDocument()
      })
    })

    it('renders page content when query is loading but cached data exists', async () => {
      mockUseQuery.mockReturnValue({
        data: mockMyCertificatesData,
        loading: true,
        error: null,
      })

      render(<MyCertificatePage />)

      await waitFor(() => {
        expect(screen.getByTestId('certificate-card')).toBeInTheDocument()
      })
    })
  })

  describe('Multiple Certificates', () => {
    it('renders "Previous Certificates" section when there are multiple certificates', async () => {
      mockUseQuery.mockReturnValue({
        data: mockMyCertificatesMultipleData,
        loading: false,
        error: null,
      })

      render(<MyCertificatePage />)

      await waitFor(() => {
        expect(screen.getByText('Previous Certificates')).toBeInTheDocument()
        expect(screen.getByText('View Certificate')).toBeInTheDocument()
      })
    })

    it('does not render other certificates section with only one certificate', async () => {
      render(<MyCertificatePage />)

      await waitFor(() => {
        expect(screen.queryByText('Previous Certificates')).not.toBeInTheDocument()
      })
    })
  })

  describe('Error Handling', () => {
    it('calls addToast with danger color when query errors', async () => {
      mockUseQuery.mockReturnValue({
        data: null,
        loading: false,
        error: new Error('Network error'),
      })

      render(<MyCertificatePage />)

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith({
          title: 'Error',
          description: 'Failed to fetch your certificate.',
          color: 'danger',
        })
      })
    })
  })

  describe('Download and Export Actions', () => {
    it('saves certificate as image successfully', async () => {
      const clickSpy = jest.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})

      render(<MyCertificatePage />)

      const saveImageButton = await screen.findByText('Save as Image')
      fireEvent.click(saveImageButton)

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith({
          title: 'Downloaded',
          description: 'Certificate saved as PNG.',
          color: 'success',
        })
      })

      clickSpy.mockRestore()
    })

    it('handles error when saving certificate as image fails', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})
      // eslint-disable-next-line @typescript-eslint/no-require-imports
      const { toPng } = require('html-to-image')
      ;(toPng as jest.Mock).mockRejectedValueOnce(new Error('Canvas error'))

      render(<MyCertificatePage />)

      const saveImageButton = await screen.findByText('Save as Image')
      fireEvent.click(saveImageButton)

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith({
          title: 'Error',
          description: 'Failed to save certificate as image.',
          color: 'danger',
        })
      })
      consoleSpy.mockRestore()
    })

    it('saves certificate as PDF successfully', async () => {
      render(<MyCertificatePage />)

      const savePdfButton = await screen.findByText('Save as PDF')
      fireEvent.click(savePdfButton)

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith({
          title: 'Downloaded',
          description: 'Certificate saved as PDF.',
          color: 'success',
        })
      })
    })

    it('handles error when saving certificate as PDF fails', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})
      // eslint-disable-next-line @typescript-eslint/no-require-imports
      const { jsPDF } = require('jspdf')
      ;(jsPDF as jest.Mock).mockImplementationOnce(() => {
        throw new Error('PDF Generation error')
      })

      render(<MyCertificatePage />)

      const savePdfButton = await screen.findByText('Save as PDF')
      fireEvent.click(savePdfButton)

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith({
          title: 'Error',
          description: 'Failed to save certificate as PDF.',
          color: 'danger',
        })
      })
      consoleSpy.mockRestore()
    })

    it('handles error when cardRef.current is null during save as image', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})
      // eslint-disable-next-line @typescript-eslint/no-require-imports
      const { CertificateCard } = require('components/CertificateCard')
      CertificateCard.mockImplementationOnce(() => <div data-testid="certificate-card" />)

      render(<MyCertificatePage />)

      const saveImageButton = await screen.findByText('Save as Image')
      fireEvent.click(saveImageButton)

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith({
          title: 'Error',
          description: 'Failed to save certificate as image.',
          color: 'danger',
        })
      })
      consoleSpy.mockRestore()
    })

    it('copies certificate link to clipboard successfully', async () => {
      const writeTextMock = jest.fn().mockResolvedValue(undefined)
      Object.assign(navigator, {
        clipboard: { writeText: writeTextMock },
      })

      render(<MyCertificatePage />)

      const copyButton = await screen.findByText('Copy Link')
      fireEvent.click(copyButton)

      await waitFor(() => {
        expect(writeTextMock).toHaveBeenCalledWith(
          expect.stringContaining('/certificate/F9DD2BJ9ZYXW')
        )
        expect(addToast).toHaveBeenCalledWith({
          title: 'Link Copied',
          description: 'Shareable verification link copied to clipboard!',
          color: 'success',
        })
      })
    })

    it('handles clipboard copy failure gracefully', async () => {
      const writeTextMock = jest.fn().mockRejectedValue(new Error('Clipboard error'))
      Object.assign(navigator, {
        clipboard: { writeText: writeTextMock },
      })

      render(<MyCertificatePage />)

      const copyButton = await screen.findByText('Copy Link')
      fireEvent.click(copyButton)

      await waitFor(() => {
        expect(addToast).toHaveBeenCalledWith({
          title: 'Copy Failed',
          description: 'Could not copy link to clipboard.',
          color: 'danger',
        })
      })
    })

    it('opens LinkedIn share window with correct params when Add to LinkedIn is clicked', async () => {
      const openSpy = jest.spyOn(window, 'open').mockImplementation(() => null)

      render(<MyCertificatePage />)

      const linkedInButton = await screen.findByText('Add to LinkedIn')
      fireEvent.click(linkedInButton)

      expect(openSpy).toHaveBeenCalledWith(
        expect.stringContaining('linkedin.com/profile/add?'),
        '_blank',
        'noopener,noreferrer'
      )
      openSpy.mockRestore()
    })
  })

  describe('Multiple Certificates and Navigation', () => {
    it('redirects to /contribute when Start Contributing button is clicked in empty state', async () => {
      const mockPush = jest.fn()
      // eslint-disable-next-line @typescript-eslint/no-require-imports
      const { useRouter } = require('next/navigation')
      ;(useRouter as jest.Mock).mockReturnValue({ push: mockPush })

      mockUseQuery.mockReturnValue({
        data: { myCertificates: [] },
        loading: false,
        error: null,
      })

      render(<MyCertificatePage />)

      const contributeButton = await screen.findByText('Start Contributing')
      fireEvent.click(contributeButton)

      expect(mockPush).toHaveBeenCalledWith('/contribute')
    })

    it('selects another certificate and scrolls to top when clicked', async () => {
      const scrollToSpy = jest.spyOn(window, 'scrollTo').mockImplementation(() => {})

      mockUseQuery.mockReturnValue({
        data: mockMyCertificatesMultipleData,
        loading: false,
        error: null,
      })

      render(<MyCertificatePage />)

      await waitFor(() => {
        expect(screen.getByText('Previous Certificates')).toBeInTheDocument()
      })

      const secondCertText = screen.getByText('level 3')
      const secondCertButton = secondCertText.closest('button')
      expect(secondCertButton).not.toBeNull()

      if (secondCertButton) {
        fireEvent.click(secondCertButton)
      }

      await waitFor(() => {
        expect(screen.getByTestId('cert-id')).toHaveTextContent('R2ST6YC1ZYXW')
        expect(screen.getByText('Other Certificates')).toBeInTheDocument()
        expect(scrollToSpy).toHaveBeenCalledWith({ top: 0, behavior: 'smooth' })
      })

      scrollToSpy.mockRestore()
    })

    it('disables other certificate buttons when isDownloading or isSavingPdf is true', async () => {
      const clickSpy = jest.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})
      mockUseQuery.mockReturnValue({
        data: mockMyCertificatesMultipleData,
        loading: false,
        error: null,
      })

      // eslint-disable-next-line @typescript-eslint/no-require-imports
      const { toPng } = require('html-to-image')
      let resolveImg: ((v: string) => void) | null = null
      ;(toPng as jest.Mock).mockImplementationOnce(
        () =>
          new Promise((res) => {
            resolveImg = res
          })
      )

      render(<MyCertificatePage />)

      const saveImageButton = await screen.findByText('Save as Image')
      fireEvent.click(saveImageButton)

      const secondCertText = screen.getByText('level 3')
      const secondCertButton = secondCertText.closest('button')
      expect(secondCertButton).toBeDisabled()

      if (resolveImg) {
        await act(async () => {
          ;(resolveImg as (v: string) => void)('data:image/png;base64,mockImageData')
        })
      }

      clickSpy.mockRestore()
    })
  })
})
