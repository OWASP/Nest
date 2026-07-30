'use client'

import { BreadcrumbProvider } from 'contexts/BreadcrumbContext'
import { useParams } from 'next/navigation'
import type { ReactNode } from 'react'

export default function BoardYearLayout({ children }: Readonly<{ children: ReactNode }>) {
  const { year } = useParams<{ year: string }>()

  return (
    <BreadcrumbProvider item={{ title: String(year), path: `/board/${year}`, hidden: true }}>
      {children}
    </BreadcrumbProvider>
  )
}
