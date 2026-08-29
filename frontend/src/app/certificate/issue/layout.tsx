import { Metadata } from 'next'
import React from 'react'
import { generateSeoMetadata } from 'utils/metaconfig'

export const metadata: Metadata = generateSeoMetadata({
  title: 'Issue Certificate',
  description:
    'Issue an OWASP Contributor Recognition Certificate to project or chapter contributors.',
  canonicalPath: '/certificate/issue',
})

export default function IssueCertificateLayout({ children }: { children: React.ReactNode }) {
  return children
}
