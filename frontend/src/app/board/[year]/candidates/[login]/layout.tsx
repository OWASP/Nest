'use client'

import { BreadcrumbProvider } from 'contexts/BreadcrumbContext'
import { useParams } from 'next/navigation'
import type { ReactNode } from 'react'

export default function BoardCandidateLoginLayout({ children }: Readonly<{ children: ReactNode }>) {
  const { year, login } = useParams<{ year: string; login: string }>()

  return (
    <BreadcrumbProvider
      item={{ title: String(login), path: `/board/${year}/candidates/${login}`, hidden: true }}
    >
      {children}
    </BreadcrumbProvider>
  )
}
