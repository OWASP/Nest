import { Metadata } from 'next'
import React from 'react'
import { apolloServerClient } from 'server/apolloClientServer'
import { GET_USER_METADATA } from 'server/queries/userQueries'
import { generateSeoMetadata } from 'utils/metaconfig'

export async function generateMetadata({
  params,
}: {
  params: Promise<{ memberKey: string }>
}): Promise<Metadata> {
  const { memberKey } = await params
  const { data } = await apolloServerClient.query({
    query: GET_USER_METADATA,
    variables: {
      key: memberKey,
    },
  })
  const user = data?.user
  const title = user?.name ?? user?.login

  return user
    ? generateSeoMetadata({
        canonicalPath: `/members/${memberKey}`,
        description: user.bio ?? `${title} OWASP community member details.`,
        keywords: [user.login, user.name, 'owasp', 'owasp community member'],
        title: title,
      })
    : null
}

export default function UserDetailsLayout({ children }: { children: React.ReactNode }) {
  return children
}
