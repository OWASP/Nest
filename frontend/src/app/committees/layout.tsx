import { Metadata } from 'next'
import React from 'react'
import { getStaticMetadata } from 'utils/metaconfig'

export const metadata: Metadata = getStaticMetadata('committees', '/committees')

export default function CommitteesLayout({ children }: { children: React.ReactNode }) {
  return children
}
