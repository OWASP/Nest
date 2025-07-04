import { Navbar, NavbarBrand, NavbarItem, NavbarContent } from '@heroui/react'
import Link from 'next/link'
import React from 'react'

export default function ProjectsHealthDashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen">
      <Navbar className="h-full w-64 flex-col items-start justify-start">
        <NavbarContent className="flex h-full flex-col items-start justify-start">
          <NavbarBrand>
            <Link href="/projects/dashboard">Overview</Link>
          </NavbarBrand>
          <NavbarItem>
            <Link href="/projects/dashboard/metrics">Metrics</Link>
          </NavbarItem>
        </NavbarContent>
      </Navbar>
      <div className="flex-1 p-4">{children}</div>
    </div>
  )
}
