'use client'

import { Breadcrumbs, BreadcrumbsItem as HeroUIBreadcrumbItem } from '@heroui/react'
import { useBreadcrumbClassName } from 'contexts/BreadcrumbContext'
import { useBreadcrumbs } from 'hooks/useBreadcrumbs'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { FaChevronRight } from 'react-icons/fa6'
import { TruncatedText } from 'components/TruncatedText'

export default function BreadCrumbsWrapper() {
  const pathname = usePathname()
  const items = useBreadcrumbs()
  const breadcrumbClassName = useBreadcrumbClassName()

  if (pathname === '/' || items.length <= 1) return null

  return (
    <div className={`mt-16 w-full pt-4 ${breadcrumbClassName}`}>
      <div className="w-full px-8 sm:px-8 md:px-8 lg:px-8">
        <Breadcrumbs
          aria-label="breadcrumb"
          separator={<FaChevronRight className="mx-1 text-xs text-gray-400 dark:text-gray-500" />}
          className="text-gray-800 dark:text-gray-200"
        >
          {items.map((item, index) => {
            const isLast = index === items.length - 1

            return (
              <HeroUIBreadcrumbItem
                key={item.path}
                isDisabled={isLast}
                className="transition-colors duration-200 min-w-0 text-sm font-medium"
              >
                {isLast ? (
                  <span className="cursor-default font-semibold text-gray-800 dark:text-gray-100">
                    <TruncatedText
                      text={item.title}
                      className="max-w-xs sm:max-w-sm md:max-w-none"
                    />
                  </span>
                ) : (
                  <Link
                    href={item.path}
                    className="hover:text-blue-700 hover:underline dark:text-blue-400"
                  >
                    <TruncatedText
                      text={item.title}
                      className="max-w-xs sm:max-w-sm md:max-w-none"
                    />
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
