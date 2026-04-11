import { Metadata } from 'next'
import React from 'react'
import { getStaticMetadata } from 'utils/metaconfig'
export const metadata: Metadata = getStaticMetadata('sponsors', '/sponsors')

export default function SponsorsLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return <div className="flex min-h-0 w-full flex-1 flex-col">{children}</div>
}
