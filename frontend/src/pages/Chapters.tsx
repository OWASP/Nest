import { useEffect, useState } from 'react'

import Card from '../components/Card'
import SearchBar from '../components/Search'
import FontAwesomeIconWrapper from '../lib/FontAwesomeIconWrapper'
import { ChapterDataType } from '../lib/types'
import { handleSocialUrls } from '../lib/utils'
import { API_URL } from '../utils/credentials'

export default function Chapters() {
  const [chapterData, setChapterData] = useState<ChapterDataType | null>(null)
  const [defaultChapter, setDefaultChapter] = useState<ChapterDataType | null>(null)

  useEffect(() => {
    document.title = 'OWASP Chapters'
    const fetchApiData = async () => {
      try {
        const response = await fetch(`${API_URL}/owasp/search/chapter`)
        const data = await response.json()
        setChapterData(data)
        setDefaultChapter(data)
      } catch (error) {
        console.error(error)
      }
    }
    fetchApiData()
  }, [])

  return (
    <div className="flex min-h-screen w-full flex-col items-center justify-normal p-5 text-text">
      <div className="-mt-6 flex h-fit w-full flex-col items-center justify-normal gap-4">
        <SearchBar
          placeholder={`Search through ${defaultChapter?.active_chapters_count || 'OWASP'} chapters around the world...`}
          searchEndpoint={`${API_URL}/owasp/search/chapter`}
          onSearchResult={setChapterData}
          defaultResults={defaultChapter}
        />
        {chapterData &&
          chapterData.chapters.map((chapter, index) => {
            const formattedUrls = handleSocialUrls(chapter.idx_related_urls)

            const SubmitButton = {
              label: 'Join',
              icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
              url: chapter.idx_url,
            }

            return (
              <Card
                key={chapter.objectID || `chapter-${index}`}
                title={chapter.idx_name}
                url={chapter.idx_url}
                summary={chapter.idx_summary}
                leaders={chapter.idx_leaders}
                topContributors={chapter.idx_top_contributors}
                button={SubmitButton}
                social={formattedUrls}
              />
            )
          })}
      </div>
    </div>
  )
}
