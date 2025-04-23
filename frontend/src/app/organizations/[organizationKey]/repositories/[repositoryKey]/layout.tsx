import { Metadata } from 'next'
import React from 'react'
import { GET_REPOSITORY_DATA } from 'server/queries/repositoryQueries'
import { apolloServerClient } from 'utils/helpers/apolloClientServer'
import { generateSeoMetadata } from 'utils/metaconfig'

export async function generateMetadata({
  params,
}: {
  params: Promise<{
    repositoryKey: string
    organizationKey: string
  }>
}): Promise<Metadata> {
  try {
    const { repositoryKey, organizationKey } = await params
    const { data } = await apolloServerClient.query({
      query: GET_REPOSITORY_DATA,
      variables: { repositoryKey: repositoryKey, organizationKey: organizationKey },
    })
    const repository = data?.repository
    if (!repository) {
      return
    }
    return generateSeoMetadata({
      title: repository.name,
      description: repository.description || 'Discover details about this OWASP repository.',
      canonicalPath: `/organizations/${organizationKey}/repositories/${repositoryKey}`,
      keywords: ['owasp', 'repository', repositoryKey, repository.name],
    })
  } catch {
    return
  }
}

export default function RepositoryDetailsLayout({ children }: { children: React.ReactNode }) {
  return children
}
