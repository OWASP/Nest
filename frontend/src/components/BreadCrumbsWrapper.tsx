'use client'

import { faChevronRight } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Breadcrumbs, BreadcrumbItem as HeroUIBreadcrumbItem } from '@heroui/react'
import { useBreadcrumbs } from 'hooks/useBreadcrumbs'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

export default function BreadCrumbsWrapper() {
  const pathname = usePathname()
  const items = useBreadcrumbs()

  if (pathname === '/' || items.length <= 1) return null

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
                  <span className="cursor-default font-semibold text-gray-800 dark:text-gray-100">
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
