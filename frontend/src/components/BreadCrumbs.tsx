import { Breadcrumbs, BreadcrumbItem as HeroUIBreadcrumbItem } from '@heroui/react'
import Link from 'next/link'
import { FaChevronRight } from 'react-icons/fa'
import type { BreadcrumbItem } from 'types/breadcrumb'
import { TruncatedText } from 'components/TruncatedText'

type BreadCrumbRendererProps = Readonly<{
  items: readonly BreadcrumbItem[]
}>

export default function BreadCrumbRenderer({ items }: BreadCrumbRendererProps) {
  return (
    <div className="mt-16 w-full pt-4">
      <div className="w-full px-8 sm:px-8 md:px-8 lg:px-8">
        <Breadcrumbs
          aria-label="breadcrumb"
          separator={<FaChevronRight className="mx-1 text-xs text-gray-400 dark:text-gray-500" />}
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
              <HeroUIBreadcrumbItem key={item.path}>
                {isLast ? (
                  <span
                    className="cursor-default font-semibold text-gray-800 dark:text-gray-300"
                    aria-current="page"
                  >
                    <TruncatedText
                      text={item.title}
                      className="max-w-xs sm:max-w-sm md:max-w-none"
                    />
                  </span>
                ) : (
                  <Link
                    href={item.path}
                    className="hover:text-blue-700 hover:underline dark:text-blue-300"
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
