import { Metadata } from 'next'
import React from 'react'
import { generateSeoMetadata } from 'utils/metaconfig'

export const metadata: Metadata = generateSeoMetadata({
  title: 'My Certificate',
  description: 'View your OWASP Contributor Recognition Certificate.',
  canonicalPath: '/my/certificate',
})

export default function MyCertificateLayout({ children }: { children: React.ReactNode }) {
  return children
}
