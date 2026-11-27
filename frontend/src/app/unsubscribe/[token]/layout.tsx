import { Metadata } from 'next'
import React from 'react'
import { generateSeoMetadata } from 'utils/metaconfig'
import { METADATA_CONFIG } from 'utils/metadata'

const { description, keywords, pageTitle } = METADATA_CONFIG.unsubscribe

// Only token-specific /unsubscribe/[token] URLs exist, so no canonical URL is emitted. The token
// can read or delete a subscription, so keep these URLs out of search indexes.
export const metadata: Metadata = {
  ...generateSeoMetadata({ description, keywords, title: pageTitle }),
  robots: { index: false, follow: false },
}

export default function UnsubscribeLayout({ children }: { children: React.ReactNode }) {
  return children
}
