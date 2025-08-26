import { notFound, redirect } from 'next/navigation'
import { getServerSession } from 'next-auth'
import React from 'react'
import { isGithubAuthEnabled } from 'utils/credentials'

export default async function ApiKeysLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  if (!isGithubAuthEnabled()) {
    notFound()
  }
  const session = await getServerSession()
  if (!session) {
    redirect('/auth/login')
  }

  return children
}
