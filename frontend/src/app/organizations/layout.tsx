import { Metadata } from 'next'
import React from 'react'
import { getStaticMetadata } from 'utils/metaconfig'

export const metadata: Metadata = getStaticMetadata('organizations', '/organizations')

export default function OrganizationsLayout({ children }: { children: React.ReactNode }) {
  return <div className="organizations-layout">{children}</div>
}
