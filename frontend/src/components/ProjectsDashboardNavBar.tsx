'use client'

import { Navbar, NavbarItem, NavbarContent } from '@heroui/react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import React from 'react'
import { FaChartLine, FaChartBar } from 'react-icons/fa6'
import { IconWrapper } from 'wrappers/IconWrapper'

const NAVIGATION_ITEMS = [
  {
    label: 'Overview',
    icon: FaChartLine,
    href: '/projects/dashboard',
  },
  {
    label: 'Metrics',
    icon: FaChartBar,
    href: '/projects/dashboard/metrics',
  },
] as const

const ProjectsDashboardNavBar: React.FC = () => {
  const pathname = usePathname()
  const isActive = (path: string) => pathname === path
  return (
    <Navbar
      classNames={{
        base: 'flex md:w-64 md:flex-col flex-row items-start justify-start py-4',
        item: [
          'data-[active=true]:bg-gray-200',
          'dark:data-[active=true]:bg-gray-800',
          'data-[active=true]:text-align-left',
          'w-full',
          'data-[active=true]:rounded',
        ],
      }}
      position="static"
    >
      <NavbarContent className="flex h-full justify-center md:flex-col md:items-start">
        {NAVIGATION_ITEMS.map(({ href, label, icon }) => (
          <NavbarItem key={href} isActive={isActive(href)}>
            <Link
              href={href}
              aria-current={isActive(href) ? 'page' : undefined}
              className="text-blue-500 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-500"
            >
              <div className="flex w-full items-center gap-2 rounded p-2 transition-colors duration-200 hover:bg-gray-200 dark:hover:bg-gray-800">
                <IconWrapper icon={icon} className="text-xl" aria-hidden="true" />
                <span className="text-sm font-semibold">{label}</span>
              </div>
            </Link>
          </NavbarItem>
        ))}
      </NavbarContent>
    </Navbar>
  )
}
export default ProjectsDashboardNavBar
