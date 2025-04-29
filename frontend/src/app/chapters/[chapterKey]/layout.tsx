import { Metadata } from 'next'
import React from 'react'
import { apolloServerClient } from 'server/apolloClientServer'
import { GET_CHAPTER_METADATA } from 'server/queries/chapterQueries'
import { generateSeoMetadata } from 'utils/metaconfig'

export async function generateMetadata({
  params,
}: {
  params: Promise<{ chapterKey: string }>
}): Promise<Metadata> {
  const { chapterKey } = await params
  const { data } = await apolloServerClient.query({
    query: GET_CHAPTER_METADATA,
    variables: {
      key: chapterKey,
    },
  })
  const chapter = data?.chapter
  if (!chapter) {
    return
  }
  return generateSeoMetadata({
    title: chapter.name,
    description: chapter.summary ?? 'Discover details about this OWASP chapter.',
    canonicalPath: `/chapters/${chapterKey}`,
    keywords: ['owasp', 'security', 'chapter', chapterKey, chapter.name],
  })
}

export default function ChapterDetailsLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return children
}
