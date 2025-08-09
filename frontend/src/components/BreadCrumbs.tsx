'use client'

import { faChevronRight } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Breadcrumbs, BreadcrumbItem } from '@heroui/react'
import _ from 'lodash'
import Link from 'next/link'
import { memo } from 'react'

export interface BreadCrumbItem {
  title: string
  path: string
}

export interface BreadCrumbsProps {
  breadcrumbItems: BreadCrumbItem[]
  'aria-label'?: string
}

function validateBreadcrumbItems(items: BreadCrumbItem[]): BreadCrumbItem[] {
  return items.filter((item) => {
    if (!item.title || !item.path) {
      return false
    }
    return true
  })
}

const BreadCrumbs = memo(function BreadCrumbs({
  breadcrumbItems,
  'aria-label': ariaLabel = 'breadcrumb',
}: BreadCrumbsProps) {
  // Validate and filter breadcrumb items
  const validBreadcrumbItems = validateBreadcrumbItems(breadcrumbItems)

  // Don't render if no valid breadcrumb items
  if (_.isEmpty(validBreadcrumbItems)) return null

  return (
    <nav className="mt-16 w-full pt-4" aria-label={ariaLabel} role="navigation">
      <div className="w-full px-8 sm:px-8 md:px-8 lg:px-8">
        <Breadcrumbs
          aria-label={ariaLabel}
          separator={
            <FontAwesomeIcon
              icon={faChevronRight}
              className="mx-1 text-xs text-gray-400 dark:text-gray-500"
              aria-hidden="true"
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
              href="/"
              className="rounded hover:text-blue-700 hover:underline focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:text-blue-400"
              aria-label="Go to home page"
            >
              Home
            </Link>
          </BreadcrumbItem>

          {validBreadcrumbItems.map((item, index) => {
            const isLast = index === validBreadcrumbItems.length - 1
            const itemKey = `${item.path}-${index}`

            return (
              <BreadcrumbItem key={itemKey} isDisabled={isLast}>
                {isLast ? (
                  <span
                    className="cursor-default font-semibold text-gray-600 dark:text-gray-300"
                    aria-current="page"
                  >
                    {item.title}
                  </span>
                ) : (
                  <Link
                    href={item.path}
                    className="rounded hover:text-blue-700 hover:underline focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:text-blue-400"
                    aria-label={`Go to ${item.title}`}
                  >
                    {item.title}
                  </Link>
                )}
              </BreadcrumbItem>
            )
          })}
        </Breadcrumbs>
      </div>
    </nav>
  )
})

export default BreadCrumbs
