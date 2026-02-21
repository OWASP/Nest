'use client'

import { BreadcrumbProvider, BreadcrumbStyleProvider } from 'contexts/BreadcrumbContext'
import { usePathname } from 'next/navigation'
import type { ReactNode } from 'react'

type PageLayoutProps = Readonly<{
  title: string
  path?: string
  breadcrumbClassName?: string
  children: ReactNode
}>

const defaultBreadcrumbClassName = 'bg-white dark:bg-[#212529]'

export default function PageLayout({
  title,
  path,
  breadcrumbClassName = defaultBreadcrumbClassName,
  children,
}: PageLayoutProps) {
  const pathname = usePathname()
  const breadcrumbPath = path ?? pathname

  const content = (
    <BreadcrumbProvider item={{ title, path: breadcrumbPath }}>{children}</BreadcrumbProvider>
  )

  return (
    <BreadcrumbStyleProvider className={breadcrumbClassName}>{content}</BreadcrumbStyleProvider>
  )
}
