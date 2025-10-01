import { Metadata } from 'next'
import React from 'react'
import { apolloClient } from 'server/apolloClient'
import { GetCommitteeMetadataDocument } from 'types/__generated__/committeeQueries.generated'
import { generateSeoMetadata } from 'utils/metaconfig'

export async function generateMetadata({
  params,
}: {
  params: Promise<{ committeeKey: string }>
}): Promise<Metadata> {
  const { committeeKey } = await params
  const { data } = await apolloClient.query({
    query: GetCommitteeMetadataDocument,
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
