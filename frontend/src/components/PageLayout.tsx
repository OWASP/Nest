import _ from 'lodash'
import { usePathname } from 'next/navigation'
import React from 'react'
import BreadCrumbs, { BreadCrumbItem } from 'components/BreadCrumbs'

export interface PageLayoutProps {
  breadcrumbItems?: BreadCrumbItem[]
  children: React.ReactNode
}

function generateBreadcrumbs(pathname: string, excludeLast = false): BreadCrumbItem[] {
  let segments = _.filter(_.split(pathname || '', '/'))
  if (excludeLast && segments.length > 0) {
    segments = segments.slice(0, -1)
  }
  let path = ''
  return segments.map((segment) => {
    path += `/${segment}`
    return {
      title: segment.charAt(0).toUpperCase() + segment.slice(1),
      path,
    }
  })
}

export default function PageLayout({ breadcrumbItems, children }: PageLayoutProps) {
  const pathname = usePathname()
  const autoBreadcrumbs = generateBreadcrumbs(pathname, !_.isEmpty(breadcrumbItems))
  const allBreadcrumbs = breadcrumbItems
    ? [...autoBreadcrumbs, ...breadcrumbItems]
    : autoBreadcrumbs

  return (
    <>
      <BreadCrumbs breadcrumbItems={allBreadcrumbs} />
      <main>{children}</main>
    </>
  )
}
