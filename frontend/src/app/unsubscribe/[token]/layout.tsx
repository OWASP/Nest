import React from 'react'
import { getStaticMetadata } from 'utils/metaconfig'

export const metadata = getStaticMetadata('unsubscribe', '/unsubscribe')

export default function UnsubscribeLayout({ children }: { children: React.ReactNode }) {
  return children
}
