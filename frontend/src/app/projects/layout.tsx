import { Metadata } from 'next'
import React from 'react'
import { IS_GITHUB_AUTH_ENABLED } from 'utils/credentials'
import { getStaticMetadata } from 'utils/metaconfig'
import AccessProjectDashboardButton from 'components/AccessProjectDashboardButton'
export const metadata: Metadata = getStaticMetadata('projects', '/projects')

// TODO(ahmed): Create a project wrapper to show loading spinner for the whole page

export default function ProjectsLayout({ children }: { children: React.ReactNode }) {
  return IS_GITHUB_AUTH_ENABLED ? (
    <div className="flex flex-col items-center justify-center">
      <AccessProjectDashboardButton />
      {children}
    </div>
  ) : (
    children
  )
}
