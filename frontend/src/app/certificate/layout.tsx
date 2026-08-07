import { Metadata } from 'next'
import React from 'react'
import { generateSeoMetadata } from 'utils/metaconfig'

export const metadata: Metadata = generateSeoMetadata({
  title: 'My Certificate',
  description: 'View your OWASP Contributor Recognition Certificate.',
  canonicalPath: '/certificate',
})

export default function CertificateLayout({ children }: { children: React.ReactNode }) {
  return children
}
