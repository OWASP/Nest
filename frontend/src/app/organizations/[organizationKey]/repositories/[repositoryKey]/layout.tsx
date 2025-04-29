import { Metadata } from 'next'
import React from 'react'
import { apolloClient } from 'server/apolloClient'
import { GET_REPOSITORY_METADATA } from 'server/queries/repositoryQueries'
import { generateSeoMetadata } from 'utils/metaconfig'

export async function generateMetadata({
  params,
}: {
  params: Promise<{
    repositoryKey: string
    organizationKey: string
  }>
}): Promise<Metadata> {
  const { repositoryKey, organizationKey } = await params
  const { data } = await apolloClient.query({
    query: GET_REPOSITORY_METADATA,
    variables: { organizationKey: organizationKey, repositoryKey: repositoryKey },
  })
  const repository = data?.repository

  return repository
    ? generateSeoMetadata({
        canonicalPath: `/organizations/${organizationKey}/repositories/${repositoryKey}`,
        description: repository.description ?? `${repository.name} repository details`,
        keywords: ['owasp', 'repository', repositoryKey, repository.name],
        title: repository.name,
      })
    : null
}

export default function RepositoryDetailsLayout({ children }: { children: React.ReactNode }) {
  return children
}
