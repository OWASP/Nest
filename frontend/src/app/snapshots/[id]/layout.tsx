import { Metadata } from 'next'
import React from 'react'
import { apolloClient } from 'server/apolloClient'
import { GetSnapshotDetailsMetadataDocument } from 'types/__generated__/snapshotQueries.generated'
import { generateSeoMetadata } from 'utils/metaconfig'

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>
}): Promise<Metadata> {
  const { id: snapshotKey } = await params
  const { data } = await apolloClient.query({
    query: GetSnapshotDetailsMetadataDocument,
    variables: { key: snapshotKey },
  })
  const snapshot = data?.snapshot

  return snapshot
    ? generateSeoMetadata({
        canonicalPath: `/snapshots/${snapshotKey}`,
        description: `${snapshot?.title} details.`,
        keywords: ['owasp', 'snapshot', snapshotKey, snapshot?.title],
        title: snapshot?.title,
      })
    : null
}
export default function SnapshotDetailsLayout({ children }: { children: React.ReactNode }) {
  return children
}
