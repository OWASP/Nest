import { Metadata } from 'next'
import React from 'react'
import { apolloClient } from 'server/apolloClient'
import {
  GetSnapshotDetailsMetadataDocument,
  GetSnapshotDetailsMetadataQuery,
} from 'types/__generated__/snapshotQueries.generated'
import { generateSeoMetadata } from 'utils/metaconfig'

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>
}): Promise<Metadata> {
  const { id: snapshotKey } = await params
  const { data } = await apolloClient.query<GetSnapshotDetailsMetadataQuery>({
    query: GetSnapshotDetailsMetadataDocument,
    variables: { key: snapshotKey },
  })
  const snapshot = (data as GetSnapshotDetailsMetadataQuery)?.snapshot

  if (!snapshot) {
    return {}
  }

  return generateSeoMetadata({
    canonicalPath: `/community/snapshots/${snapshotKey}`,
    description: `${snapshot.title} details.`,
    keywords: ['owasp', 'snapshot', snapshotKey, snapshot.title],
    title: snapshot.title,
  })
}
export default function SnapshotDetailsLayout({ children }: { children: React.ReactNode }) {
  return children
}
