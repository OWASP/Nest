import React from 'react'
import ProjectsDashboardNavBar from 'components/ProjectsDashboardNavBar'

export default function ProjectsHealthDashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex">
      <ProjectsDashboardNavBar />
      <div className="flex-1 p-4">{children}</div>
    </div>
  )
}
