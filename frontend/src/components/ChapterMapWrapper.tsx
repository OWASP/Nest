import dynamic from 'next/dynamic'

const ChapterMap = dynamic(() => import('./ChapterMap'), { ssr: false })

const ChapterMapWrapper = (props: any) => {
  return <ChapterMap {...props} />
}

export default ChapterMapWrapper
