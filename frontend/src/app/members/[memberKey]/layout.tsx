import { Metadata } from 'next'
import React from 'react'
import { apolloClient } from 'server/apolloClient'
import {
  GetUserDataDocument,
  GetUserMetadataDocument,
} from 'types/__generated__/userQueries.generated'
import { generateSeoMetadata } from 'utils/metaconfig'
import { generateProfilePageStructuredData } from 'utils/structuredData'
import PageLayout from 'components/PageLayout'
import StructuredDataScript from 'components/StructuredDataScript'

export async function generateMetadata({
  params,
}: {
  params: Promise<{ memberKey: string }>
}): Promise<Metadata> {
  const { memberKey } = await params
  const { data } = await apolloClient.query({
    query: GetUserMetadataDocument,
    variables: {
      key: memberKey,
    },
  })
  const user = data?.user
  const title = user?.name || user?.login || memberKey

  return user
    ? generateSeoMetadata({
        canonicalPath: `/members/${memberKey}`,
        description: user.bio ?? `${title} OWASP community member details.`,
        keywords: [user.login, user.name, 'owasp', 'owasp community member'],
        title: title,
      })
    : {}
}

export default async function UserDetailsLayout({
  children,
  params,
}: Readonly<{
  children: React.ReactNode
  params: Promise<{ memberKey: string }>
}>) {
  const { memberKey } = await params

  const { data } = await apolloClient.query({
    query: GetUserDataDocument,
    variables: {
      key: memberKey,
    },
  })

  if (!data?.user?.login) {
    return children
  }

  return (
    <PageLayout title={data?.user?.name || data?.user?.login || ''}>
      <StructuredDataScript data={generateProfilePageStructuredData(data.user)} />
      {children}
    </PageLayout>
  )
}
