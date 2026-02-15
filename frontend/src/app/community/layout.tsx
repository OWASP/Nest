import { Metadata } from 'next'
import React from 'react'
import { getStaticMetadata } from 'utils/metaconfig'

export const metadata: Metadata = getStaticMetadata('community', '/community')

export default function CommunityLayout({ children }: { children: React.ReactNode }) {
  return children
}
