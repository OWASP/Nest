import { useEffect, useState } from 'react'

import Card from '../components/Card'
import { Modal } from '../components/Modal/Modal'
import FontAwesomeIconWrapper from '../lib/FontAwesomeIconWrapper'
import { IssuesDataType } from '../lib/types'
import { getFilteredIcons } from '../lib/utils'
import { API_URL } from '../utils/credentials'
import { logger } from '../utils/logger'

export default function ContributePage() {
  const [contributeData, setContributeData] = useState<IssuesDataType | null>(null)
  const [modalOpenIndex, setModalOpenIndex] = useState<number | null>(null)

  useEffect(() => {
    document.title = 'OWASP Issues'
    const fetchApiData = async () => {
      try {
        const response = await fetch(`${API_URL}/owasp/search/issue`)
        const data = await response.json()
        setContributeData(data)
      } catch (error) {
        logger.error(error)
      }
    }
    fetchApiData()
  }, [])

  return (
    <div className="flex min-h-screen w-full flex-col items-center justify-normal p-5 text-text md:p-20">
      <div className="flex h-fit w-full flex-col items-center justify-normal gap-4">
        {contributeData &&
          contributeData.issues.map((issue, index) => {
            const params: string[] = ['idx_created_at', 'idx_comments_count']
            const filteredIcons = getFilteredIcons(issue, params)

            const SubmitButton = {
              label: 'Read More',
              icon: <FontAwesomeIconWrapper icon="fa-solid fa-wand-magic-sparkles" />,
              onclick: () => setModalOpenIndex(index),
            }

            return (
              <>
                <Card
                  key={issue.objectID || `issue-${index}`}
                  title={issue.idx_title}
                  url={issue.idx_url}
                  projectName={issue.idx_project_name}
                  projectLink={issue.idx_project_url}
                  summary={issue.idx_summary}
                  languages={issue.idx_repository_languages}
                  icons={filteredIcons}
                  button={SubmitButton}
                />
                <Modal
                  isOpen={modalOpenIndex === index}
                  onClose={() => setModalOpenIndex(null)}
                  title={issue.idx_title}
                  summary={issue.idx_summary}
                  hint={issue.idx_hint}
                ></Modal>
              </>
            )
          })}
      </div>
    </div>
  )
}
