import { Metadata } from 'next'
import React, { cache } from 'react'
import { apolloClient } from 'server/apolloClient'
import { GetProjectMetadataDocument } from 'types/__generated__/projectQueries.generated'
import { generateSeoMetadata } from 'utils/metaconfig'
import PageLayout from 'components/PageLayout'

const getProjectMetadata = cache(async (projectKey: string) => {
  try {
    const { data } = await apolloClient.query({
      query: GetProjectMetadataDocument,
      variables: { key: projectKey },
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
    projectKey: string
  }>
}): Promise<Metadata | undefined> {
  const { projectKey } = await params
  const data = await getProjectMetadata(projectKey)
  const project = data?.project

  return project
    ? generateSeoMetadata({
        canonicalPath: `/projects/${projectKey}`,
        description: project.summary ?? `${project.name} project details`,
        keywords: ['owasp', 'project', projectKey, project.name],
        title: project.name,
      })
    : undefined
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

  return (
    <PageLayout title={data.project.name} breadcrumbClassName="bg-white dark:bg-[#212529]">
      {children}
    </PageLayout>
  )
}
