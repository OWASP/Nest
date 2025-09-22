import dynamic from 'next/dynamic'
import React from 'react'
import type { Chapter } from 'types/chapter'

const ChapterMap = dynamic(() => import('./ChapterMap'), { ssr: false })

const ChapterMapWrapper = (props: {
  geoLocData: Chapter[]
  showLocal: boolean
  style: React.CSSProperties
}) => {
  return <ChapterMap {...props} />
}

export default ChapterMapWrapper
