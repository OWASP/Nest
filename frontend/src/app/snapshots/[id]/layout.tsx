import { Metadata } from 'next'
import React from 'react'
import { apolloServerClient } from 'server/apolloClientServer'
import { GET_SNAPSHOT_DETAILS_METADATA } from 'server/queries/snapshotQueries'
import { generateSeoMetadata } from 'utils/metaconfig'

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>
}): Promise<Metadata> {
  const { id: snapshotKey } = await params
  const { data } = await apolloServerClient.query({
    query: GET_SNAPSHOT_DETAILS_METADATA,
    variables: { key: snapshotKey },
  })
  const snapshot = data?.snapshot
  if (!snapshot) {
    return
  }
  return generateSeoMetadata({
    title: snapshot?.title,
    description: `Discover details about ${snapshot?.title} OWASP snapshot.`,
    canonicalPath: `/snapshots/${snapshotKey}`,
    keywords: ['owasp', 'snapshot', snapshotKey, snapshot?.title],
  })
}
export default function SnapshotDetailsLayout({ children }: { children: React.ReactNode }) {
  return children
}
