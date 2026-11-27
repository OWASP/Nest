import { Metadata } from 'next'
import React from 'react'
import { generateSeoMetadata } from 'utils/metaconfig'

export const metadata: Metadata = generateSeoMetadata({
  title: 'My Certificates',
  description: 'View your OWASP Contributor Recognition Certificate.',
  canonicalPath: '/my/certificates',
})

export default function MyCertificateLayout({ children }: { children: React.ReactNode }) {
  return children
}
