import _ from 'lodash'
import { usePathname } from 'next/navigation'
import React from 'react'
import BreadCrumbs, { BreadCrumbItem } from 'components/BreadCrumbs'

export interface crumbItem {
  title: string
}

export interface customBreadcrumbItem {
  title: string
  path: string
}

export interface PageLayoutProps {
  breadcrumbItems?: crumbItem
  customBreadcrumbs?: customBreadcrumbItem[]
  children: React.ReactNode
}

function generateBreadcrumbs(pathname: string, excludeLast = false): BreadCrumbItem[] {
  let segments = _.compact(_.split(pathname, '/'))
  if (excludeLast) {
    segments = _.dropRight(segments)
  }

  return _.map(segments, (segment, index) => {
    const path = '/' + _.join(_.slice(segments, 0, index + 1), '/')
    return {
      title: _.capitalize(segment),
      path,
    }
  })
}

export default function PageLayout({
  breadcrumbItems,
  customBreadcrumbs,
  children,
}: PageLayoutProps) {
  const pathname = usePathname()

  let allBreadcrumbs: BreadCrumbItem[]

  if (customBreadcrumbs && customBreadcrumbs.length > 0) {
    allBreadcrumbs = customBreadcrumbs
  } else {
    const isBreadCrumbItemsEmpty = _.isEmpty(breadcrumbItems)
    const autoBreadcrumbs = generateBreadcrumbs(pathname, !isBreadCrumbItemsEmpty)
    allBreadcrumbs = isBreadCrumbItemsEmpty
      ? autoBreadcrumbs
      : [...autoBreadcrumbs, { title: _.get(breadcrumbItems, 'title', ''), path: pathname }]
  }

  return (
    <>
      <BreadCrumbs breadcrumbItems={allBreadcrumbs} />
      <main>{children}</main>
    </>
  )
}
