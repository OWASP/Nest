import { Metadata } from 'next'
import React from 'react'
import { IS_GITHUB_AUTH_ENABLED } from 'utils/credentials'
import { getStaticMetadata } from 'utils/metaconfig'
import ProjectsWrapper from 'components/ProjectsWrapper'
export const metadata: Metadata = getStaticMetadata('projects', '/projects')

export default function ProjectsLayout({ children }: { children: React.ReactNode }) {
  return IS_GITHUB_AUTH_ENABLED ? <ProjectsWrapper>{children}</ProjectsWrapper> : <>{children}</>
}
