import { Metadata } from 'next'
import React, { cache } from 'react'
import { apolloClient } from 'server/apolloClient'
import { GetRepositoryMetadataDocument } from 'types/__generated__/repositoryQueries.generated'
import { formatBreadcrumbTitle } from 'utils/breadcrumb'
import { generateSeoMetadata } from 'utils/metaconfig'
import PageLayout from 'components/PageLayout'

const getRepositoryMetadata = cache(async (organizationKey: string, repositoryKey: string) => {
  try {
    const { data } = await apolloClient.query({
      query: GetRepositoryMetadataDocument,
      variables: { organizationKey, repositoryKey },
    })
    return data
  } catch {
    return null
  }
})

export async function generateMetadata({
  params,
}: {
  params: Promise<{
    repositoryKey: string
    organizationKey: string
  }>
}): Promise<Metadata | undefined> {
  const { repositoryKey, organizationKey } = await params
  const data = await getRepositoryMetadata(organizationKey, repositoryKey)
  const repository = data?.repository

  if (!repository) {
    return {}
  }

  return generateSeoMetadata({
    canonicalPath: `/organizations/${organizationKey}/repositories/${repositoryKey}`,
    description: repository.description ?? `${repository.name} repository details`,
    keywords: ['owasp', 'repository', repositoryKey, repository.name],
    title: repository.name,
  })
}

export default async function RepositoryDetailsLayout({
  children,
  params,
}: Readonly<{
  children: React.ReactNode
  params: Promise<{ repositoryKey: string; organizationKey: string }>
}>) {
  const { repositoryKey, organizationKey } = await params
  const data = await getRepositoryMetadata(organizationKey, repositoryKey)
  const repoName = data?.repository?.name
    ? formatBreadcrumbTitle(data.repository.name)
    : formatBreadcrumbTitle(repositoryKey)

  return (
    <PageLayout
      title={repoName}
      path={`/organizations/${organizationKey}/repositories/${repositoryKey}`}
    >
      {children}
    </PageLayout>
  )
}
