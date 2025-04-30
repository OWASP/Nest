import { Metadata } from 'next'
import React from 'react'
import { apolloClient } from 'server/apolloClient'
import { GET_COMMITTEE_METADATA } from 'server/queries/committeeQueries'
import { generateSeoMetadata } from 'utils/metaconfig'

export async function generateMetadata({
  params,
}: {
  params: Promise<{ committeeKey: string }>
}): Promise<Metadata> {
  const { committeeKey } = await params
  const { data } = await apolloClient.query({
    query: GET_COMMITTEE_METADATA,
    variables: {
      key: committeeKey,
    },
  })
  const committee = data?.committee

  return committee
    ? generateSeoMetadata({
        canonicalPath: `/committees/${committeeKey}`,
        description: committee.summary ?? `${committee.name} details`,
        keywords: ['owasp', 'security', 'committee', committeeKey, committee.name],
        title: committee.name,
      })
    : null
}

export default function CommitteeDetailsLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return children
}
