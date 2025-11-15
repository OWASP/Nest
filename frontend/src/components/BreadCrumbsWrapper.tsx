'use client'

import { faChevronRight } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Breadcrumbs, BreadcrumbItem as HeroUIBreadcrumbItem } from '@heroui/react'
import upperFirst from 'lodash/upperFirst'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

const ROUTES_WITH_PAGE_LAYOUT = [
  /^\/members\/[^/]+$/,
  /^\/projects\/[^/]+$/,
  /^\/chapters\/[^/]+$/,
  /^\/committees\/[^/]+$/,
  /^\/organizations\/[^/]+$/,
  /^\/organizations\/[^/]+\/repositories\/[^/]+$/,
]

export default function BreadCrumbsWrapper() {
  const pathname = usePathname()

  if (pathname === '/') return null

  const usesPageLayout = ROUTES_WITH_PAGE_LAYOUT.some((pattern) => pattern.test(pathname))
  if (usesPageLayout) return null

  const segments = pathname.split('/').filter(Boolean)
  const items = [
    { title: 'Home', path: '/' },
    ...segments.map((segment, index) => ({
      title: upperFirst(segment).replaceAll('-', ' '),
      path: '/' + segments.slice(0, index + 1).join('/'),
    })),
  ]

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
          {items.map((item, index) => {
            const isLast = index === items.length - 1

            return (
              <HeroUIBreadcrumbItem key={item.path} isDisabled={isLast}>
                {isLast ? (
                  <span className="cursor-default font-semibold text-gray-600 dark:text-gray-300">
                    {item.title}
                  </span>
                ) : (
                  <Link
                    href={item.path}
                    className="hover:text-blue-700 hover:underline dark:text-blue-400"
                  >
                    {item.title}
                  </Link>
                )}
              </HeroUIBreadcrumbItem>
            )
          })}
        </Breadcrumbs>
      </div>
    </div>
  )
}
