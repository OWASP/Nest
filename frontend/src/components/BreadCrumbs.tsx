'use client'

import { faChevronRight } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Breadcrumbs, BreadcrumbItem } from '@heroui/react'
import upperFirst from 'lodash/upperFirst'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

export default function BreadCrumbs() {
  const homeRoute = '/'
  const pathname = usePathname()
  const segments = pathname.split(homeRoute).filter(Boolean)

  if (pathname === homeRoute) return null

  return (
    <div className="mt-16 w-full pt-4">
      <div className="w-full px-8 sm:px-8 md:px-8 lg:px-8">
        <Breadcrumbs
          aria-label="breadcrumb"
          separator={
            <FontAwesomeIcon
              icon={faChevronRight}
              className="mx-1 text-xs text-gray-400 dark:text-gray-500"
            />
          }
          className="text-gray-800 dark:text-gray-200"
          itemClasses={{
            base: 'transition-colors duration-200',
            item: 'text-sm font-medium',
            separator: 'flex items-center',
          }}
        >
          <BreadcrumbItem>
            <Link
              href={homeRoute}
              className="hover:text-blue-700 hover:underline dark:text-blue-400"
            >
              Home
            </Link>
          </BreadcrumbItem>

          {segments.map((segment, index) => {
            const href = homeRoute + segments.slice(0, index + 1).join(homeRoute)
            const label = upperFirst(segment).replaceAll(/-/g, ' ')
            const isLast = index === segments.length - 1

            return (
              <BreadcrumbItem key={href} isDisabled={isLast}>
                {isLast ? (
                  <span className="cursor-default font-semibold text-gray-600 dark:text-gray-300">
                    {label}
                  </span>
                ) : (
                  <Link
                    href={href}
                    className="hover:text-blue-700 hover:underline dark:text-blue-400"
                  >
                    {label}
                  </Link>
                )}
              </BreadcrumbItem>
            )
          })}
        </Breadcrumbs>
      </div>
    </div>
  )
}
