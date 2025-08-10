import { notFound } from 'next/navigation'
import React from 'react'
import { IS_GITHUB_AUTH_ENABLED } from 'utils/credentials'
import DashboardWrapper from 'components/DashboardWrapper'
import FontLoaderWrapper from 'components/FontLoaderWrapper'
import ProjectsDashboardNavBar from 'components/ProjectsDashboardNavBar'

const ProjectsHealthDashboardLayout: React.FC<{ readonly children: React.ReactNode }> = ({
  children,
}) => {
  if (!IS_GITHUB_AUTH_ENABLED) {
    notFound()
  }
  return (
    <FontLoaderWrapper>
      <DashboardWrapper>
        <div className="flex flex-col md:flex-row">
          <ProjectsDashboardNavBar />
          <main className="flex-1 p-4">{children}</main>
        </div>
      </DashboardWrapper>
    </FontLoaderWrapper>
  )
}

export default ProjectsHealthDashboardLayout
