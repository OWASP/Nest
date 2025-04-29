import { Metadata } from 'next'
import React from 'react'
import { apolloServerClient } from 'server/apolloClientServer'
import { GET_ORGANIZATION_METADATA } from 'server/queries/organizationQueries'
import { generateSeoMetadata } from 'utils/metaconfig'

export async function generateMetadata({
  params,
}: {
  params: Promise<{ organizationKey: string }>
}): Promise<Metadata> {
  const { organizationKey } = await params
  const { data } = await apolloServerClient.query({
    query: GET_ORGANIZATION_METADATA,
    variables: {
      login: organizationKey,
    },
  })
  const organization = data?.organization
  if (!organization) {
    return
  }
  return generateSeoMetadata({
    title: organization?.name ?? organization?.login,
    description: organization?.description ?? 'Discover details about this OWASP organization.',
    canonicalPath: `/organizations/${organizationKey}`,
  })
}

export default function OrganizationDetailsLayout({ children }: { children: React.ReactNode }) {
  return children
}
