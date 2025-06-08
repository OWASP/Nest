import dynamic from 'next/dynamic'
import React from 'react'
import { ChapterType } from 'types/chapter'

const ChapterMap = dynamic(() => import('./ChapterMap'), { ssr: false })

const ChapterMapWrapper = (props: {
  geoLocData: ChapterType[]
  showLocal: boolean
  style: React.CSSProperties
}) => {
  return <ChapterMap {...props} />
}

export default ChapterMapWrapper
