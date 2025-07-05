'use client'

import { faChartLine, faChartBar } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Navbar, NavbarItem, NavbarContent } from '@heroui/react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

export default function ProjectsDashboardNavBar() {
  const pathname = usePathname()
  const isActive = (path: string) => pathname === path
  return (
    <Navbar
      classNames={{
        base: 'h-full w-64 flex-col items-start justify-start py-4',
        item: [
          'data-[active=true]:bg-gray-200',
          'data-[active=true]:dark:bg-gray-800',
          'data-[active=true]:text-align-left',
          'w-full',
          'data-[active=true]:rounded',
        ],
      }}
    >
      <NavbarContent className="flex h-full flex-col items-start justify-start">
        <NavbarItem isActive={isActive('/projects/dashboard')}>
          <Link href="/projects/dashboard">
            <div className="flex w-full items-center gap-2 rounded p-2 transition-colors duration-200 hover:bg-gray-200 dark:hover:bg-gray-800">
              <FontAwesomeIcon icon={faChartLine} className="text-xl" />
              <span className="text-sm font-semibold">Overview</span>
            </div>
          </Link>
        </NavbarItem>
        <NavbarItem isActive={isActive('/projects/dashboard/metrics')}>
          <Link href="/projects/dashboard/metrics">
            <div className="flex w-full items-center gap-2 rounded p-2 transition-colors duration-200 hover:bg-gray-200 dark:hover:bg-gray-800">
              <FontAwesomeIcon icon={faChartBar} className="text-xl" />
              <span className="text-sm font-semibold">Metrics</span>
            </div>
          </Link>
        </NavbarItem>
      </NavbarContent>
    </Navbar>
  )
}
