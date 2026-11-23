import { generateMetadata } from 'app/certificates/[certificateId]/layout'
import { apolloClient } from 'server/apolloClient'

jest.mock('server/apolloClient', () => ({
  apolloClient: { query: jest.fn() },
}))

const mockQuery = apolloClient.query as jest.Mock

const params = Promise.resolve({ certificateId: 'F9DD2BJ9ZYXW' })

describe('CertificateVerificationLayout generateMetadata', () => {
  afterEach(() => {
    jest.clearAllMocks()
  })

  it('returns certificate metadata with a canonical URL when the certificate exists', async () => {
    mockQuery.mockResolvedValue({
      data: {
        certificate: { githubUser: { login: 'testuser', name: 'Test User' } },
      },
    })

    const metadata = await generateMetadata({ params })

    expect(metadata.title).toBe("Test User's Certificate Verification – OWASP Nest")
    expect(metadata.alternates?.canonical).toBe('https://nest.owasp.org/certificates/F9DD2BJ9ZYXW')
  })

  it('returns empty metadata for an unknown certificate ID', async () => {
    mockQuery.mockResolvedValue({ data: { certificate: null } })

    await expect(generateMetadata({ params })).resolves.toEqual({})
  })

  it('returns empty metadata when the lookup fails', async () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})
    mockQuery.mockRejectedValue(new Error('Network error'))

    await expect(generateMetadata({ params })).resolves.toEqual({})
    expect(consoleSpy).toHaveBeenCalled()

    consoleSpy.mockRestore()
  })
})
