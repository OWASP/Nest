import React from 'react'
import ProjectsDashboardNavBar from 'components/ProjectsDashboardNavBar'

const ProjectsHealthDashboardLayout: React.FC<{ readonly children: React.ReactNode }> = ({
  children,
}) => {
  return (
    <div className="flex flex-col md:flex-row">
      <ProjectsDashboardNavBar />
      <div className="flex-1 p-4">{children}</div>
    </div>
  )
}

export default ProjectsHealthDashboardLayout
