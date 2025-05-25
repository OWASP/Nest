'use client'

import { faChevronRight } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Breadcrumbs, BreadcrumbItem } from '@heroui/react'
import _ from 'lodash'
import Link from 'next/link'

interface BCrumbItem {
  title: string
  href: string
}

interface BreadCrumbsProps {
  bcItems: BCrumbItem[]
}

export default function BreadCrumbs({ bcItems }: BreadCrumbsProps) {
  if (_.isEmpty(bcItems)) return null

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
            <Link href="/" className="hover:text-blue-700 hover:underline dark:text-blue-400">
              Home
            </Link>
          </BreadcrumbItem>

          {bcItems.map((item, index) => {
            const isLast = index === bcItems.length - 1
            return (
              <BreadcrumbItem key={item.href} isDisabled={isLast}>
                {isLast ? (
                  <span className="cursor-default font-semibold text-gray-600 dark:text-gray-300">
                    {item.title}
                  </span>
                ) : (
                  <Link
                    href={item.href}
                    className="hover:text-blue-700 hover:underline dark:text-blue-400"
                  >
                    {item.title}
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
