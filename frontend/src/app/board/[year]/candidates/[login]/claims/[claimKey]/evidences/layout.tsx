'use client'

import { BreadcrumbProvider } from 'contexts/BreadcrumbContext'
import { useParams } from 'next/navigation'
import type { ReactNode } from 'react'

export default function EvidencesLayout({ children }: Readonly<{ children: ReactNode }>) {
  const { year, login, claimKey } = useParams<{ year: string; login: string; claimKey: string }>()

  return (
    <BreadcrumbProvider
      item={{
        title: 'Evidences',
        path: `/board/${year}/candidates/${login}/claims/${claimKey}/evidences`,
        hidden: true,
      }}
    >
      {children}
    </BreadcrumbProvider>
  )
}
