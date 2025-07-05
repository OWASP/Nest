import React from 'react'
import ProjectsDashboardNavBar from 'components/ProjectsDashboardNavBar'

const ProjectsHealthDashboardLayout: React.FC<{ readonly children: React.ReactNode }> = ({
  children,
}) => {
  return (
    <div className="flex">
      <ProjectsDashboardNavBar />
      <div className="flex-1 p-4">{children}</div>
    </div>
  )
}

export default ProjectsHealthDashboardLayout
