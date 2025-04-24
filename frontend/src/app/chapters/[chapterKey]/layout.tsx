import { Metadata } from 'next'
import React from 'react'
import { GET_CHAPTER_DATA } from 'server/queries/chapterQueries'
import { apolloServerClient } from 'utils/helpers/apolloClientServer'
import { generateSeoMetadata } from 'utils/metaconfig'

type Params = Promise<{ chapterKey: string }>

export async function generateMetadata({ params }: { params: Params }): Promise<Metadata> {
  try {
    const { chapterKey } = await params
    const { data } = await apolloServerClient.query({
      query: GET_CHAPTER_DATA,
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
  } catch {
    return
  }
}

export default function ChapterDetailsLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return children
}
