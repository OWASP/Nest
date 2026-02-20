import DOMPurify from 'isomorphic-dompurify'
import { Metadata } from 'next'
import Script from 'next/script'
import React from 'react'
import { apolloClient } from '../../../lib/apolloClient'
import {
  GetOrganizationDataDocument,
  GetOrganizationMetadataDocument,
} from 'types/__generated__/organizationQueries.generated'
import { generateSeoMetadata } from 'utils/metaconfig'
import PageLayout from 'components/PageLayout'

export async function generateMetadata({
  params,
}: {
  params: Promise<{ organizationKey: string }>
}): Promise<Metadata | undefined> {
  const { organizationKey } = await params
  const { data } = await apolloClient.query({
    query: GetOrganizationMetadataDocument,
    variables: {
      login: organizationKey,
    },
  })
  const organization = data?.organization
  const title = organization?.name ?? organization?.login ?? ''

  return organization
    ? generateSeoMetadata({
        canonicalPath: `/organizations/${organizationKey}`,
        description: organization?.description ?? `${title} organization details`,
        title: title,
      })
    : undefined
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

  if (!/^[a-zA-Z0-9._-]+$/.test(organizationKey)) {
    return (
      <PageLayout title="Invalid Organization" path="/organizations">
        <div>Invalid Organization Key</div>
      </PageLayout>
    )
  }
  const structuredData = await generateOrganizationStructuredData(organizationKey)

  const jsonLdString = structuredData
    ? DOMPurify.sanitize(JSON.stringify(structuredData, null, 2))
    : null

  // Fetch organization name for breadcrumb
  const { data } = await apolloClient.query({
    query: GetOrganizationMetadataDocument,
    variables: { login: organizationKey },
  })
  const orgName = data?.organization?.name || data?.organization?.login || organizationKey

  return (
    <PageLayout title={orgName} path={`/organizations/${organizationKey}`}>
      {jsonLdString && (
        <Script
          id="organization-structured-data"
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: jsonLdString,
          }}
        />
      )}
      {children}
    </PageLayout>
  )
}
