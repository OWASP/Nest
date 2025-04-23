import { Metadata } from 'next'
import React from 'react'
import { GET_PROJECT_DATA } from 'server/queries/projectQueries'
import { apolloServerClient } from 'utils/helpers/apolloClientServer'
import { generateSeoMetadata } from 'utils/metaconfig'

export async function generateMetadata({
  params,
}: {
  params: Promise<{
    projectKey: string
  }>
}): Promise<Metadata> {
  try {
    const { projectKey } = await params
    const { data } = await apolloServerClient.query({
      query: GET_PROJECT_DATA,
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
      description: project.summary || 'Discover details about this OWASP project.',
      canonicalPath: `/projects/${projectKey}`,
      keywords: ['owasp', 'project', projectKey, project.name],
    })
  } catch {
    return
  }
}

export default function ProjectDetailsLayout({ children }: { children: React.ReactNode }) {
  return children
}
