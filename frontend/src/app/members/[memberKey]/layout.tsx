import { Metadata } from 'next'
import React from 'react'
import { GET_USER_DATA } from 'server/queries/userQueries'
import { apolloServerClient } from 'utils/helpers/apolloClientServer'
import { generateSeoMetadata } from 'utils/metaconfig'

export async function generateMetadata({
  params,
}: {
  params: Promise<{ memberKey: string }>
}): Promise<Metadata> {
  try {
    const { memberKey } = await params
    const { data } = await apolloServerClient.query({
      query: GET_USER_DATA,
      variables: {
        key: memberKey,
      },
    })
    const user = data?.user
    if (!user) {
      return
    }
    return generateSeoMetadata({
      title: user.name || user.login,
      description: user.bio || 'Discover details about this OWASP community member.',
      canonicalPath: `/members/${memberKey}`,
      keywords: [user.login, user.name, 'owasp', 'owasp community member'],
    })
  } catch {
    return
  }
}

export default function UserDetailsLayout({ children }: { children: React.ReactNode }) {
  return <div className="user-details-layout">{children}</div>
}
