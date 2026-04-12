import { Metadata } from 'next'
import React from 'react'
import { getStaticMetadata } from 'utils/metaconfig'

export const metadata: Metadata = getStaticMetadata('sponsors', '/sponsors')

export default function SponsorsLayout({ children }: { children: React.ReactNode }) {
  return children
}
