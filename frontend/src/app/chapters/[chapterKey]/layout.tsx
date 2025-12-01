import { Metadata } from 'next'
import { cache } from 'react'
import React from 'react'
import { apolloClient } from 'server/apolloClient'
import { GetChapterMetadataDocument } from 'types/__generated__/chapterQueries.generated'
import { generateSeoMetadata } from 'utils/metaconfig'
import PageLayout from 'components/PageLayout'

const getChapterMetadata = cache(async (chapterKey: string) => {
  const { data } = await apolloClient.query({
    query: GetChapterMetadataDocument,
    variables: { key: chapterKey },
  })
  return data
})

export async function generateMetadata({
  params,
}: {
  params: Promise<{ chapterKey: string }>
}): Promise<Metadata> {
  const { chapterKey } = await params
  const data = await getChapterMetadata(chapterKey)
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

export default async function ChapterDetailsLayout({
  children,
  params,
}: Readonly<{
  children: React.ReactNode
  params: Promise<{ chapterKey: string }>
}>) {
  const { chapterKey } = await params
  const data = await getChapterMetadata(chapterKey)

  if (!data?.chapter) {
    return children
  }

  return <PageLayout title={data.chapter.name}>{children}</PageLayout>
}
