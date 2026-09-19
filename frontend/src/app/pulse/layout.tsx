import { Metadata } from 'next'
import React from 'react'
import { getStaticMetadata } from 'utils/metaconfig'

export const metadata: Metadata = getStaticMetadata('pulse', '/pulse')

export default function PulseLayout({ children }: { children: React.ReactNode }) {
  return children
}
