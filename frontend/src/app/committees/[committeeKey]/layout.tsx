import { Metadata } from 'next'
import React, { cache } from 'react'
import { apolloClient } from 'server/apolloClient'
import { GetCommitteeMetadataDocument } from 'types/__generated__/committeeQueries.generated'
import { generateSeoMetadata } from 'utils/metaconfig'
import PageLayout from 'components/PageLayout'

const getCommitteeMetadata = cache(async (committeeKey: string) => {
  try {
    const { data } = await apolloClient.query({
      query: GetCommitteeMetadataDocument,
      variables: { key: committeeKey },
    })
    return data
  } catch {
    return null
  }
})

export async function generateMetadata({
  params,
}: {
  params: Promise<{ committeeKey: string }>
}): Promise<Metadata> {
  const { committeeKey } = await params
  const data = await getCommitteeMetadata(committeeKey)
  const committee = data?.committee

  return committee
    ? generateSeoMetadata({
        canonicalPath: `/committees/${committeeKey}`,
        description: committee.summary ?? `${committee.name} details`,
        keywords: ['owasp', 'security', 'committee', committeeKey, committee.name],
        title: committee.name,
      })
    : {
        title: 'Not Found',
      }
}

export default async function CommitteeDetailsLayout({
  children,
  params,
}: Readonly<{
  children: React.ReactNode
  params: Promise<{ committeeKey: string }>
}>) {
  const { committeeKey } = await params
  const data = await getCommitteeMetadata(committeeKey)

  if (!data?.committee) {
    return children
  }

  return <PageLayout title={data.committee.name}>{children}</PageLayout>
}
