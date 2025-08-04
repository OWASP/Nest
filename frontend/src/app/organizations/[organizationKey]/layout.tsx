import { Metadata } from 'next'
import Script from 'next/script'
import React from 'react'
import { apolloClient } from 'server/apolloClient'
import {
  GET_ORGANIZATION_METADATA,
  GET_ORGANIZATION_DATA,
} from 'server/queries/organizationQueries'
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

async function generateOrganizationStructuredData(organizationKey: string) {
  // https://developers.google.com/search/docs/appearance/structured-data/organization#structured-data-type-definitions

  try {
    const { data } = await apolloClient.query({
      query: GET_ORGANIZATION_DATA,
      variables: {
        login: organizationKey,
      },
    })

    const organization = data?.organization
    if (!organization) return null

    const structuredData = {
      '@context': 'https://schema.org' as const,
      '@type': 'Organization' as const,
      contactPoint: organization.email
        ? {
            '@type': 'ContactPoint' as const,
            email: organization.email,
            contactType: 'general inquiry',
          }
        : undefined,
      description: organization.description,
      email: organization.email,
      foundingDate: organization.createdAt,
      keywords: [
        organization.name,
        organization.login,
        'cybersecurity',
        'application security',
        'open source',
        'OWASP',
      ].filter(Boolean),
      location: organization.location
        ? {
            '@type': 'Place' as const,
            name: organization.location,
          }
        : undefined,
      logo: organization.avatarUrl
        ? {
            '@type': 'ImageObject' as const,
            url: organization.avatarUrl,
          }
        : undefined,
      memberOf: {
        '@type': 'Organization' as const,
        name: 'OWASP Foundation',
        url: 'https://owasp.org',
      },
      name: organization.name || organization.login,
      sameAs: [organization.url].filter(Boolean),
      url: `https://nest.owasp.org/organizations/${organizationKey}`,
    }

    // Remove undefined properties
    Object.keys(structuredData).forEach(
      (key) => structuredData[key] === undefined && delete structuredData[key]
    )

    return structuredData
  } catch {
    return null
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
