import { Metadata } from 'next'
import React from 'react'
import { apolloClient } from 'server/apolloClient'
import {
  GetCertificateDocument,
  type GetCertificateQuery,
} from 'types/__generated__/certificateQueries.generated'
import { generateSeoMetadata } from 'utils/metaconfig'

export async function generateMetadata({
  params,
}: {
  params: Promise<{ certificateId: string }>
}): Promise<Metadata> {
  const { certificateId } = await params
  let certificate: GetCertificateQuery['certificate'] | undefined
  try {
    const { data } = await apolloClient.query({
      query: GetCertificateDocument,
      variables: { id: certificateId },
    })
    certificate = data?.certificate
  } catch (error) {
    // eslint-disable-next-line no-console
    console.error('Error generating metadata for certificate verification:', error)
    // A transient failure must not mark a valid certificate as noindex.
    return {}
  }

  if (!certificate) {
    // The page renders a not-found message with a 200 status, so keep unknown IDs out of
    // search indexes explicitly.
    return { robots: { index: false, follow: false } }
  }

  const displayName = certificate.githubUser.name || certificate.githubUser.login
  return generateSeoMetadata({
    canonicalPath: `/certificates/${certificateId}`,
    description: `Verify the OWASP Contributor Recognition Certificate of ${displayName} (@${certificate.githubUser.login}).`,
    title: `${displayName}'s Certificate Verification`,
  })
}

export default function CertificateVerificationLayout({ children }: { children: React.ReactNode }) {
  return children
}
