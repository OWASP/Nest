import { Metadata } from 'next'
import React from 'react'
import { apolloServerClient } from 'server/apolloClientServer'
import { GET_COMMITTEE_METADATA } from 'server/queries/committeeQueries'
import { generateSeoMetadata } from 'utils/metaconfig'

export async function generateMetadata({
  params,
}: {
  params: Promise<{ committeeKey: string }>
}): Promise<Metadata> {
  const { committeeKey } = await params
  const { data } = await apolloServerClient.query({
    query: GET_COMMITTEE_METADATA,
    variables: {
      key: committeeKey,
    },
  })
  const committee = data?.committee
  if (!committee) {
    return
  }
  return generateSeoMetadata({
    title: committee.name,
    description: committee.summary ?? 'Discover details about this OWASP committee.',
    canonicalPath: `/committees/${committeeKey}`,
    keywords: ['owasp', 'security', 'committee', committeeKey, committee.name],
  })
}

export default function CommitteeDetailsLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return children
}
