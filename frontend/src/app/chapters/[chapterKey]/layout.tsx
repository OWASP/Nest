import { Metadata } from 'next'
import React from 'react'
import { apolloClient } from 'server/apolloClient'
import { GET_CHAPTER_METADATA } from 'server/queries/chapterQueries'
import { generateSeoMetadata } from 'utils/metaconfig'

export async function generateMetadata({
  params,
}: {
  params: Promise<{ chapterKey: string }>
}): Promise<Metadata> {
  const { chapterKey } = await params
  const { data } = await apolloClient.query({
    query: GET_CHAPTER_METADATA,
    variables: {
      key: chapterKey,
    },
  })
  const chapter = data?.chapter

  return chapter
    ? generateSeoMetadata({
        canonicalPath: `/chapters/${chapterKey}`,
        description: chapter.summary ?? `${chapter.name} chapter details`,
        keywords: ['owasp', 'security', 'chapter', chapterKey, chapter.name],
        title: chapter.name,
      })
    : null
}

export default function ChapterDetailsLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return children
}
