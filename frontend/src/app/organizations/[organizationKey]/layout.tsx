import { Metadata } from 'next'
import Script from 'next/script'
import React from 'react'
import { apolloClient } from 'server/apolloClient'
import {
  GetOrganizationDataDocument,
  GetOrganizationMetadataDocument,
} from 'types/__generated__/organizationQueries.generated'
import { generateSeoMetadata } from 'utils/metaconfig'

export async function generateMetadata({
  params,
}: {
  params: Promise<{ organizationKey: string }>
}): Promise<Metadata> {
  const { organizationKey } = await params
  const { data } = await apolloClient.query({
    query: GetOrganizationMetadataDocument,
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

async function generateOrganizationStructuredData(organizationKey: string) {
  // https://developers.google.com/search/docs/appearance/structured-data/organization#structured-data-type-definitions

  const { data } = await apolloClient.query({
    query: GetOrganizationDataDocument,
    variables: {
      login: organizationKey,
    },
  })

  const organization = data?.organization
  if (!organization) return null

  return {
    '@context': 'https://schema.org' as const,
    '@type': 'Organization' as const,
    ...(organization.email && {
      contactPoint: {
        '@type': 'ContactPoint' as const,
        email: organization.email,
      },
    }),
    description: organization.description,
    email: organization.email,
    foundingDate: organization.createdAt,
    keywords: [
      organization.name,
      organization.login,
      'cybersecurity',
      'open source',
      'OWASP',
    ].filter(Boolean),
    ...(organization.location && {
      location: {
        '@type': 'Place' as const,
        name: organization.location,
      },
    }),
    ...(organization.avatarUrl && {
      logo: {
        '@type': 'ImageObject' as const,
        url: organization.avatarUrl,
      },
    }),
    ...(organization.login.toLowerCase() !== 'owasp' && {
      memberOf: {
        '@type': 'Organization' as const,
        name: 'OWASP Foundation',
        url: 'https://owasp.org',
      },
    }),
    name: organization.name || organization.login,
    sameAs: [organization.url].filter(Boolean),
    url: `https://nest.owasp.org/organizations/${organizationKey}`,
  }
}

export default async function OrganizationDetailsLayout({
  children,
  params,
}: Readonly<{
  children: Readonly<React.ReactNode>
  params: Promise<{ organizationKey: string }>
}>) {
  const { organizationKey } = await params
  const structuredData = await generateOrganizationStructuredData(organizationKey)

  return (
    <>
      {structuredData && (
        <Script
          id="organization-structured-data"
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(structuredData, null, 2),
          }}
        />
      )}
      {children}
    </>
  )
}
