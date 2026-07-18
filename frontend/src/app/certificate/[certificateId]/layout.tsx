import { Metadata } from 'next'
import React from 'react'
import { apolloClient } from 'server/apolloClient'
import { GetCertificateDocument } from 'types/__generated__/certificateQueries.generated'
import { generateSeoMetadata } from 'utils/metaconfig'

export async function generateMetadata({
  params,
}: {
  params: Promise<{ certificateId: string }>
}): Promise<Metadata> {
  const { certificateId } = await params
  try {
    const { data } = await apolloClient.query({
      query: GetCertificateDocument,
      variables: { id: certificateId },
    })
    const certificate = data?.certificate
    if (certificate) {
      const displayName = certificate.githubUser.name || certificate.githubUser.login
      return generateSeoMetadata({
        canonicalPath: `/certificate/${certificateId}`,
        description: `Verify the OWASP Contributor Recognition Certificate of ${displayName} (@${certificate.githubUser.login}).`,
        title: `${displayName}'s Certificate Verification`,
      })
    }
  } catch (error) {
    // eslint-disable-next-line no-console
    console.error('Error generating metadata for certificate verification:', error)
  }

  return generateSeoMetadata({
    canonicalPath: `/certificate/${certificateId}`,
    description: 'Verify OWASP Contributor Recognition Certificate.',
    title: 'Certificate Verification',
  })
}

export default function CertificateVerificationLayout({ children }: { children: React.ReactNode }) {
  return children
}
