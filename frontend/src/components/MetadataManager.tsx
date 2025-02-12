import React from 'react'
import { DefaultMetadata, MetadataManagerProps } from 'types/seo'

const DEFAULT_METADATA: DefaultMetadata = {
  siteName: 'OWASP Nest',
  baseUrl: 'https://nest.owasp.dev/',
  defaultDescription:
    'OWASP Nest is a comprehensive platform designed to enhance collaboration and contribution within the OWASP community.',
  twitterHandle: '@owasp',
  defaultIcon: '/img/owasp_icon_white_background.png',
}

const MetadataManager: React.FC<MetadataManagerProps> = ({
  pageTitle,
  description,
  image,
  url,
  type = 'website',
  keywords = [],
  children,
}) => {
  const metaDescription = description ? description : DEFAULT_METADATA.defaultDescription
  const metaImage = image ? image : DEFAULT_METADATA.defaultIcon
  const metaUrl = url ? url : DEFAULT_METADATA.baseUrl
  const title = `${pageTitle} | ${DEFAULT_METADATA.siteName}`

  return (
    <>
      <title>{title}</title>
      <meta name="description" content={metaDescription} />
      {keywords.length > 0 && <meta name="keywords" content={keywords.join(',')} />}

      <meta property="og:title" content={title} />
      <meta property="og:description" content={metaDescription} />
      <meta property="og:image" content={metaImage} />
      <meta property="og:url" content={metaUrl} />
      <meta property="og:type" content={type} />
      <meta property="og:site_name" content={DEFAULT_METADATA.siteName} />
      <meta property="og:locale" content="en_US" />
      <meta property="og:image:alt" content="OWASP logo" />
      <meta property="og:image:width" content="1200" />
      <meta property="og:image:height" content="630" />
      <meta property="og:image:type" content="image/png" />

      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:site" content={DEFAULT_METADATA.twitterHandle} />
      <meta name="twitter:creator" content={DEFAULT_METADATA.twitterHandle} />
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={metaDescription} />
      <meta name="twitter:image" content={metaImage} />
      <meta name="twitter:image:alt" content="OWASP Nest logo" />
      <meta name="twitter:url" content={metaUrl} />

      {children}
    </>
  )
}

export default MetadataManager
