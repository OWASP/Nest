'use client'

import _ from 'lodash'
import { usePathname } from 'next/navigation'
import React from 'react'
import BreadCrumbs, { BreadCrumbItem } from 'components/BreadCrumbs'

export interface crumbItem {
  title: string
}

export interface PageLayoutProps {
  breadcrumbItems?: crumbItem | crumbItem[]
  children: React.ReactNode
}

function generateAutoBreadcrumbs(pathname: string, excludeLast = false): BreadCrumbItem[] {
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

function generateBreadcrumbsFromItems(items: crumbItem[], pathname: string): BreadCrumbItem[] {
  const segments = _.compact(_.split(pathname, '/'))
  return items.map((item, index) => {
    const path = '/' + _.join(_.slice(segments, 0, index + 1), '/')
    return {
      title: item.title,
      path,
    }
  })
}

export default function PageLayout({ breadcrumbItems, children }: PageLayoutProps) {
  const pathname = usePathname()
  const isBreadCrumbItemsEmpty = _.isEmpty(breadcrumbItems)
  let allBreadcrumbs: BreadCrumbItem[]
  if (_.isArray(breadcrumbItems)) {
    allBreadcrumbs = generateBreadcrumbsFromItems(breadcrumbItems, pathname)
  } else {
    const autoBreadcrumbs = generateAutoBreadcrumbs(pathname, !isBreadCrumbItemsEmpty)
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
