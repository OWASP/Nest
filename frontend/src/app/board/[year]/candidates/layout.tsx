import type { Metadata } from 'next'
import React from 'react'

export const metadata: Metadata = {
  title: 'Board Candidates | OWASP',
  description: 'OWASP Board of Directors election candidates',
}

export default function BoardCandidatesLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
