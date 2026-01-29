import { Metadata } from 'next'
import React, { cache } from 'react'
import { apolloClient } from 'server/apolloClient'
import { GetChapterMetadataDocument } from 'types/__generated__/chapterQueries.generated'
import { generateSeoMetadata } from 'utils/metaconfig'
import PageLayout from 'components/PageLayout'

const getChapterMetadata = cache(async (chapterKey: string) => {
  try {
    const { data } = await apolloClient.query({
      query: GetChapterMetadataDocument,
      variables: { key: chapterKey },
    })
    return data
  } catch {
    return null
  }
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
    : {
        title: 'Not Found',
      }
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
