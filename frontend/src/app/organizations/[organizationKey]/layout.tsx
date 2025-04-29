import { Metadata } from 'next'
import React from 'react'
import { apolloClient } from 'server/apolloClient'
import { GET_ORGANIZATION_METADATA } from 'server/queries/organizationQueries'
import { generateSeoMetadata } from 'utils/metaconfig'

export async function generateMetadata({
  params,
}: {
  params: Promise<{ organizationKey: string }>
}): Promise<Metadata> {
  const { organizationKey } = await params
  const { data } = await apolloClient.query({
    query: GET_ORGANIZATION_METADATA,
    variables: {
      login: organizationKey,
    },
  })
  const organization = data?.organization
  const title = organization?.name ?? organization?.login

  return organization
    ? generateSeoMetadata({
        canonicalPath: `/organizations/${organizationKey}`,
        description: organization?.description ?? `${title} organization details`,
        title: title,
      })
    : null
}

export default function OrganizationDetailsLayout({ children }: { children: React.ReactNode }) {
  return children
}
