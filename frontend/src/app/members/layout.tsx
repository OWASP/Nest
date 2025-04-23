import { Metadata } from 'next'
import React from 'react'
import { getStaticMetadata } from 'utils/metaconfig'

export const metadata: Metadata = getStaticMetadata('members', '/members')

export default function UsersLayout({ children }: { children: React.ReactNode }) {
  return <div className="users-layout">{children}</div>
}
