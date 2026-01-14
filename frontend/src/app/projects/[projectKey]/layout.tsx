import { Metadata } from 'next'
import React, { cache } from 'react'
import { apolloClient } from 'server/apolloClient'
import { GetProjectMetadataDocument, GetProjectMetadataQuery } from 'types/__generated__/projectQueries.generated'
import { generateSeoMetadata } from 'utils/metaconfig'
import PageLayout from 'components/PageLayout'

const getProjectMetadata = cache(async (projectKey: string): Promise<GetProjectMetadataQuery | null> => {
  try {
    const { data } = await apolloClient.query<GetProjectMetadataQuery>({
      query: GetProjectMetadataDocument,
      variables: { key: projectKey },
    })

    if (data && typeof data === 'object' && 'project' in data && data.project) {
       return data as GetProjectMetadataQuery
    }

    return null
  } catch {
    return null
  }
})

export async function generateMetadata({
  params,
}: {
  params: Promise<{
    projectKey: string
  }>
}): Promise<Metadata> {
  const { projectKey } = await params
  const data = await getProjectMetadata(projectKey)
  const project = data?.project

  if (!project) return {}

  return generateSeoMetadata({
        canonicalPath: `/projects/${projectKey}`,
        description: project.summary ?? `${project.name} project details`,
        keywords: ['owasp', 'project', projectKey, project.name],
        title: project.name,
      })
}

export default async function ProjectDetailsLayout({
  children,
  params,
}: Readonly<{
  children: React.ReactNode
  params: Promise<{ projectKey: string }>
}>) {
  const { projectKey } = await params
  const data = await getProjectMetadata(projectKey)

  if (!data?.project) {
    return children
  }

  return <PageLayout title={data.project.name}>{children}</PageLayout>
}
