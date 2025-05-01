import { Metadata } from 'next'
import React from 'react'
import { getStaticMetadata } from 'utils/metaconfig'

export const metadata: Metadata = getStaticMetadata('chapters', '/chapters')

export default function ChaptersLayout({ children }: { children: React.ReactNode }) {
  return children
}
