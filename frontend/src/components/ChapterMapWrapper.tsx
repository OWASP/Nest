import dynamic from 'next/dynamic'
import React from 'react'
import { ChapterMapFieldsFragment } from 'types/__generated__/chapterFragments.generated'

const ChapterMap = dynamic(() => import('./ChapterMap'), { ssr: false })

// TODO: Location markers not visible
const ChapterMapWrapper = (props: {
  geoLocData: ChapterMapFieldsFragment[]
  showLocal: boolean
  style: React.CSSProperties
}) => {
  return <ChapterMap {...props} />
}

export default ChapterMapWrapper
