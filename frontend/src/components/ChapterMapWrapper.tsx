import dynamic from 'next/dynamic'
import React from 'react'
import { GeoLocDataAlgolia, GeoLocDataGraphQL } from 'types/chapter'

const ChapterMap = dynamic(() => import('./ChapterMap'), { ssr: false })

const ChapterMapWrapper = (props: {
  geoLocData: GeoLocDataGraphQL[] | GeoLocDataAlgolia[]
  showLocal: boolean
  style: React.CSSProperties
}) => {
  return <ChapterMap {...props} />
}

export default ChapterMapWrapper
