import { Metadata } from 'next'
import React from 'react'
import { apolloServerClient } from 'server/apolloClientServer'
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
  const { data } = await apolloServerClient.query({
    query: GET_PROJECT_METADATA,
    variables: {
      key: projectKey,
    },
  })
  const project = data?.project
  if (!project) {
    return
  }
  return generateSeoMetadata({
    title: project.name,
    description: project.summary ?? 'Discover details about this OWASP project.',
    canonicalPath: `/projects/${projectKey}`,
    keywords: ['owasp', 'project', projectKey, project.name],
  })
}

export default function ProjectDetailsLayout({ children }: { children: React.ReactNode }) {
  return children
}
