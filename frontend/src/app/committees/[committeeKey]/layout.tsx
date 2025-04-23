import { Metadata } from 'next'
import React from 'react'
import { GET_COMMITTEE_DATA } from 'server/queries/committeeQueries'
import { apolloServerClient } from 'utils/helpers/apolloClientServer'
import { generateSeoMetadata } from 'utils/metaconfig'

export async function generateMetadata({
  params,
}: {
  params: Promise<{ committeeKey: string }>
}): Promise<Metadata> {
  try {
    const { committeeKey } = await params
    const { data } = await apolloServerClient.query({
      query: GET_COMMITTEE_DATA,
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
      description: committee.summary || 'Discover details about this OWASP committee.',
      canonicalPath: `/committees/${committeeKey}`,
      keywords: ['owasp', 'security', 'committee', committeeKey, committee.name],
    })
  } catch {
    return
  }
}

export default function CommitteeDetailsLayout({ children }: { children: React.ReactNode }) {
  return <div className="committee-layout">{children}</div>
}
