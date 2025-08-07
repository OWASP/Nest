import { Metadata } from 'next'
import React from 'react'
import { getStaticMetadata } from 'utils/metaconfig'
export const metadata: Metadata = getStaticMetadata('projects', '/projects')

export default function ProjectsLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
