import { notFound, redirect } from 'next/navigation'
import { getServerSession } from 'next-auth'
import React from 'react'
import { IS_GITHUB_AUTH_ENABLED } from 'utils/env.server'

export default async function ApiKeysLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  if (!IS_GITHUB_AUTH_ENABLED) {
    notFound()
  }
  const session = await getServerSession()
  if (!session) {
    redirect('/auth/login')
  }

  return children
}
