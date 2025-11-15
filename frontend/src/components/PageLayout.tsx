'use client'

import { useBreadcrumbs } from 'hooks/useBreadcrumbs'
import type { ReactNode } from 'react'
import BreadCrumbRenderer from 'components/BreadCrumbs'

interface PageLayoutProps {
  breadcrumbData?: {
    projectName?: string
    memberName?: string
    chapterName?: string
    committeeName?: string
    orgName?: string
    repoName?: string
  }
  children: ReactNode
}

export default function PageLayout({ breadcrumbData, children }: PageLayoutProps) {
  const breadcrumbItems = useBreadcrumbs(breadcrumbData)

  return (
    <>
      <BreadCrumbRenderer items={breadcrumbItems} />
      {children}
    </>
  )
}
