import React from 'react'
import { getStaticMetadata } from 'utils/metaconfig'

export const metadata = getStaticMetadata('contribute', '/contribute')

export default function ContributeLayout({ children }: { children: React.ReactNode }) {
  return children
}
