import type { Metadata } from 'next'
import type React from 'react'
import { getStaticMetadata } from 'utils/metaconfig'

export const metadata: Metadata = getStaticMetadata('settings', '/settings')

export default function SettingsLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return children
}
