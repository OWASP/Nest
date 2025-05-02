import { Metadata } from 'next'
import React from 'react'
import { apolloClient } from 'server/apolloClient'
import { GET_PROJECT_METADATA } from 'server/queries/projectQueries'
import { generateSeoMetadata } from 'utils/metaconfig'

export async function generateMetadata({
  params,
}: {
  params: Promise<{
    projectKey: string
  }>
}): Promise<Metadata> {
  const { projectKey } = await params
  const { data } = await apolloClient.query({
    query: GET_PROJECT_METADATA,
    variables: {
      key: projectKey,
    },
  })
  const project = data?.project

  return project
    ? generateSeoMetadata({
        canonicalPath: `/projects/${projectKey}`,
        description: project.summary ?? `${project.name} project details`,
        keywords: ['owasp', 'project', projectKey, project.name],
        title: project.name,
      })
    : null
}

export default function ProjectDetailsLayout({ children }: { children: React.ReactNode }) {
  return children
}
