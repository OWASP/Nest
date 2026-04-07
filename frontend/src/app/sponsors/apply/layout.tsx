import { Metadata } from 'next'
import React from 'react'
import { generateSeoMetadata } from 'utils/metaconfig'

export const metadata: Metadata = generateSeoMetadata({
  title: 'Become a Sponsor',
  description: 'Apply to become an OWASP Nest sponsor and support open source security.',
  canonicalPath: '/sponsors/apply',
  keywords: ['OWASP sponsor', 'sponsorship', 'open source security', 'support OWASP'],
})

export default function SponsorApplyLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return <>{children}</>
}
