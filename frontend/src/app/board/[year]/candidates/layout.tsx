import type { Metadata } from 'next'
import React from 'react'
import PageLayout from 'components/PageLayout'

export const metadata: Metadata = {
  title: 'Board Candidates | OWASP',
  description: 'OWASP Board of Directors election candidates',
}

export default async function BoardCandidatesLayout({
  children,
  params,
}: Readonly<{ children: React.ReactNode; params: Promise<{ year: string }> }>) {
  const { year } = await params

  return (
    <PageLayout title={`${year} Board Candidates`} path={`/board/${year}/candidates`}>
      {children}
    </PageLayout>
  )
}
