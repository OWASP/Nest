import { Metadata } from 'next'
import { METADATA_CONFIG } from 'utils/metadata'

interface SeoMetadataProps {
  title: string
  description: string
  canonicalPath?: string
  ogImage?: string
  keywords?: string[]
  type?: 'website' | 'article' | 'profile'
  locale?: string
  siteName?: string
  twitterHandle?: string
}

export function generateSeoMetadata({
  title,
  description,
  canonicalPath,
  ogImage = 'https://nest.owasp.org/img/nest_1200x630_light.png',
  keywords = [],
  type = 'website',
  locale = 'en_US',
  siteName = 'OWASP Nest',
  twitterHandle = '@owasp',
}: SeoMetadataProps): Metadata {
  const baseUrl = 'https://nest.owasp.org'
  const formattedTitle = title.includes('OWASP Nest') ? title : `${title} – OWASP Nest`
  const canonicalUrl = canonicalPath ? `${baseUrl}${canonicalPath}` : undefined

  return {
    metadataBase: new URL(baseUrl),
    title: formattedTitle,
    description,
    ...(keywords.length > 0 && { keywords: keywords.join(', ') }),
    ...(canonicalUrl && {
      alternates: {
        canonical: canonicalUrl,
      },
    }),
    openGraph: {
      title: formattedTitle,
      description,
      ...(canonicalUrl && { url: canonicalUrl }),
      siteName,
      images: [
        {
          url: ogImage,
          width: 1200,
          height: 630,
          alt: `${siteName} Logo`,
        },
      ],
      locale,
      type,
    },
    twitter: {
      card: 'summary_large_image',
      title: formattedTitle,
      description,
      images: [ogImage],
      creator: twitterHandle,
      site: twitterHandle,
    },
  }
}

export function getStaticMetadata(
  pageKey: keyof typeof METADATA_CONFIG,
  canonicalPath?: string
): Metadata {
  if (!METADATA_CONFIG[pageKey]) {
    throw new Error(`No metadata configuration found for key: ${pageKey}`)
  }
  const config = METADATA_CONFIG[pageKey]

  return generateSeoMetadata({
    canonicalPath: canonicalPath || `/${pageKey.toLowerCase()}`,
    description: config.description,
    keywords: config.keywords,
    title: config.pageTitle,
    type: config.type as 'website' | 'article' | 'profile',
  })
}
