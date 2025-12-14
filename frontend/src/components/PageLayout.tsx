'use client'

import { BreadcrumbProvider } from 'contexts/BreadcrumbContext'
import { usePathname } from 'next/navigation'
import type { ReactNode } from 'react'

type PageLayoutProps = Readonly<{
  title: string
  path?: string
  children: ReactNode
}>

export default function PageLayout({ title, path, children }: PageLayoutProps) {
  const pathname = usePathname()
  const breadcrumbPath = path ?? pathname

  return <BreadcrumbProvider item={{ title, path: breadcrumbPath }}>{children}</BreadcrumbProvider>
}
