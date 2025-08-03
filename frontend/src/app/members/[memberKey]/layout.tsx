import { Metadata } from 'next'
import React from 'react'
import { apolloClient } from 'server/apolloClient'
import { GET_USER_METADATA, GET_USER_DATA } from 'server/queries/userQueries'
import { generateSeoMetadata } from 'utils/metaconfig'
import { generateProfilePageStructuredData } from 'utils/structuredData'
import StructuredDataScript from 'components/StructuredDataScript'

export async function generateMetadata({
  params,
}: {
  params: Promise<{ memberKey: string }>
}): Promise<Metadata> {
  const { memberKey } = await params
  const { data } = await apolloClient.query({
    query: GET_USER_METADATA,
    variables: {
      key: memberKey,
    },
  })
  const user = data?.user
  const title = user?.name || user?.login

  return user
    ? generateSeoMetadata({
        canonicalPath: `/members/${memberKey}`,
        description: user.bio ?? `${title} OWASP community member details.`,
        keywords: [user.login, user.name, 'owasp', 'owasp community member'],
        title: title,
      })
    : null
}

export default async function UserDetailsLayout({
  children,
  params,
}: {
  children: React.ReactNode
  params: Promise<{ memberKey: string }>
}) {
  const { memberKey } = await params

  try {
    const { data } = await apolloClient.query({
      query: GET_USER_DATA,
      variables: {
        key: memberKey,
      },
    })

    const user = data?.user

    if (!user) {
      return children
    }

    if (user && user.login) {
      const structuredData = generateProfilePageStructuredData(user)

      return (
        <>
          <StructuredDataScript data={structuredData} />
          {children}
        </>
      )
    }
  } catch {
    return children
  }
}
