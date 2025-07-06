import React from 'react'
import ProjectsDashboardNavBar from 'components/ProjectsDashboardNavBar'

const ProjectsHealthDashboardLayout: React.FC<{ readonly children: React.ReactNode }> = ({
  children,
}) => {
  return (
    <div className="flex flex-col md:flex-row">
      <ProjectsDashboardNavBar />
      <main className="flex-1 p-4" role="main">
        {children}
      </main>
    </div>
  )
}

export default ProjectsHealthDashboardLayout
