import { useQuery } from '@apollo/client/react'
import {
  mockGetCertificateData,
  mockGetRevokedCertificateData,
} from '@mockData/mockCertificateData'
import { screen, waitFor } from '@testing-library/react'
import React from 'react'
import { render } from 'wrappers/testUtil'
import CertificateVerificationPage from 'app/certificates/[certificateId]/page'

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useQuery: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useParams: jest.fn(() => ({ certificateId: 'F9DD2BJ9ZYXW' })),
}))

jest.mock('components/CertificateCard', () => {
  const MockCertificateCard = ({
    certificate,
    isPublicView,
  }: {
    certificate: { id: string; tier: string }
    isPublicView?: boolean
  }) => (
    <div data-testid="certificate-card" data-public-view={String(isPublicView)}>
      <span data-testid="cert-id">{certificate.id}</span>
      <span data-testid="cert-tier">{certificate.tier}</span>
    </div>
  )
  MockCertificateCard.displayName = 'MockCertificateCard'
  return {
    __esModule: true,
    // eslint-disable-next-line @typescript-eslint/naming-convention
    CertificateCard: MockCertificateCard,
    CERTIFICATE_LAYOUT: { width: 842, height: 595 },
  }
})

jest.mock('components/LoadingSpinner', () => {
  const MockLoadingSpinner = () => <div role="status" aria-label="Loading" />
  MockLoadingSpinner.displayName = 'MockLoadingSpinner'
  return { __esModule: true, default: MockLoadingSpinner }
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

jest.mock('app/global-error', () => ({
  ErrorDisplay: ({
    statusCode,
    title,
    message,
  }: {
    statusCode: number
    title: string
    message: string
  }) => (
    <div data-testid="error-display" data-status-code={statusCode}>
      <h2>{title}</h2>
      <p>{message}</p>
    </div>
  ),
}))

describe('CertificateVerificationPage', () => {
  const mockUseQuery = useQuery as unknown as jest.Mock

  beforeEach(() => {
    jest.clearAllMocks()
    mockUseQuery.mockReturnValue({
      data: mockGetCertificateData,
      loading: false,
      error: null,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  describe('Loading State', () => {
    it('renders loading spinner when loading=true and no data', () => {
      mockUseQuery.mockReturnValue({ data: null, loading: true, error: null })

      render(<CertificateVerificationPage />)

      expect(screen.getByRole('status')).toBeInTheDocument()
    })

    it('does not render loading spinner when data is available', async () => {
      render(<CertificateVerificationPage />)

      await waitFor(() => {
        expect(screen.queryByRole('status')).not.toBeInTheDocument()
      })
    })
  })

  describe('Error State', () => {
    it('renders ErrorDisplay with 500 when query errors and no data', async () => {
      mockUseQuery.mockReturnValue({
        data: null,
        loading: false,
        error: new Error('GraphQL error'),
      })

      render(<CertificateVerificationPage />)

      await waitFor(() => {
        expect(screen.getByTestId('error-display')).toBeInTheDocument()
      })

      expect(screen.getByTestId('error-display')).toHaveAttribute('data-status-code', '500')
      expect(screen.getByText('Verification Error')).toBeInTheDocument()
      expect(
        screen.getByText('An error occurred while verifying the certificate.')
      ).toBeInTheDocument()
    })

    it('renders certificate even when there is an error but data is present', async () => {
      mockUseQuery.mockReturnValue({
        data: mockGetCertificateData,
        loading: false,
        error: new Error('Partial error'),
      })

      render(<CertificateVerificationPage />)

      await waitFor(() => {
        expect(screen.getByTestId('certificate-card')).toBeInTheDocument()
      })

      expect(screen.queryByTestId('error-display')).not.toBeInTheDocument()
    })
  })

  describe('Not Found State', () => {
    it('renders 404 ErrorDisplay when certificate is null in data', async () => {
      mockUseQuery.mockReturnValue({
        data: { certificate: null },
        loading: false,
        error: null,
      })

      render(<CertificateVerificationPage />)

      await waitFor(() => {
        expect(screen.getByTestId('error-display')).toBeInTheDocument()
      })

      expect(screen.getByTestId('error-display')).toHaveAttribute('data-status-code', '404')
      expect(screen.getByText('Certificate Not Found')).toBeInTheDocument()
      expect(
        screen.getByText(
          'The certificate verification link is invalid or the certificate does not exist.'
        )
      ).toBeInTheDocument()
    })

    it('renders 404 ErrorDisplay when data is undefined', async () => {
      mockUseQuery.mockReturnValue({ data: undefined, loading: false, error: null })

      render(<CertificateVerificationPage />)

      await waitFor(() => {
        expect(screen.getByTestId('error-display')).toBeInTheDocument()
      })

      expect(screen.getByTestId('error-display')).toHaveAttribute('data-status-code', '404')
    })
  })

  describe('Certificate Display', () => {
    it('renders CertificateCard with the fetched certificate', async () => {
      render(<CertificateVerificationPage />)

      await waitFor(() => {
        expect(screen.getByTestId('certificate-card')).toBeInTheDocument()
      })

      expect(screen.getByTestId('cert-id')).toHaveTextContent('F9DD2BJ9ZYXW')
      expect(screen.getByTestId('cert-tier')).toHaveTextContent('level 1')
    })

    it('passes isPublicView=true to CertificateCard', async () => {
      render(<CertificateVerificationPage />)

      await waitFor(() => {
        const card = screen.getByTestId('certificate-card')
        expect(card).toHaveAttribute('data-public-view', 'true')
      })
    })

    it('renders page title with user display name when name is provided', async () => {
      render(<CertificateVerificationPage />)

      await waitFor(() => {
        expect(screen.getByText("Verify Test User's Certificate")).toBeInTheDocument()
      })
    })

    it('uses login as display name in title when githubUser.name is not provided', async () => {
      mockUseQuery.mockReturnValue({
        data: {
          certificate: {
            ...mockGetCertificateData.certificate,
            githubUser: {
              login: 'loginonly',
              name: undefined,
              avatarUrl: '/avatar.png',
            },
          },
        },
        loading: false,
        error: null,
      })

      render(<CertificateVerificationPage />)

      await waitFor(() => {
        expect(screen.getByText("Verify loginonly's Certificate")).toBeInTheDocument()
      })
    })

    it('renders the certificate inside a PageLayout', async () => {
      render(<CertificateVerificationPage />)

      await waitFor(() => {
        expect(screen.getByTestId('page-layout')).toBeInTheDocument()
      })
    })
  })

  describe('Revoked Certificate', () => {
    it('renders revoked certificate card via CertificateCard (isPublicView=true)', async () => {
      mockUseQuery.mockReturnValue({
        data: mockGetRevokedCertificateData,
        loading: false,
        error: null,
      })

      render(<CertificateVerificationPage />)

      await waitFor(() => {
        const card = screen.getByTestId('certificate-card')
        expect(card).toBeInTheDocument()
        expect(card).toHaveAttribute('data-public-view', 'true')
      })

      expect(screen.getByTestId('cert-id')).toHaveTextContent('X7KP3MN2FOSS')
    })
  })

  describe('Query Integration', () => {
    it('passes the certificateId from params to the query', () => {
      render(<CertificateVerificationPage />)

      expect(mockUseQuery).toHaveBeenCalledWith(
        expect.anything(),
        expect.objectContaining({
          variables: { id: 'F9DD2BJ9ZYXW' },
        })
      )
    })

    it('uses cache-and-network fetch policy', () => {
      render(<CertificateVerificationPage />)

      expect(mockUseQuery).toHaveBeenCalledWith(
        expect.anything(),
        expect.objectContaining({
          fetchPolicy: 'cache-and-network',
        })
      )
    })
  })
})
