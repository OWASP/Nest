import React from 'react'
import { getStaticMetadata } from 'utils/metaconfig'

export const metadata = getStaticMetadata('snapshots', '/snapshots')

export default function SnapshotsLayout({ children }: { children: React.ReactNode }) {
  return children
}
