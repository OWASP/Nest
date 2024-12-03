/* eslint-disable @typescript-eslint/no-unused-vars */
import { useEffect, useState } from 'react'
import Card from './components/Card'
import ModeToggle from './components/ModeToggle'
import {
  IssuesDataType,
  project,
  ProjectDataType,
  IssueType,
  ChapterDataType,
  CommitteeDataType,
} from './lib/types'
import {
  MockChaptersData,
  MockContributeData,
  MockProjectData,
  MockCommitteeData,
} from './components/mockData'
import { getFilteredIcons, handleSocialUrls } from './lib/utils'
import FontAwesomeIconWrapper from './lib/FontAwesomeIconWrapper'
import { level } from './components/data'

export default function EntityExampleComponent() {
  const [projectData, setProjectData] = useState<ProjectDataType | null>(null)
  const [contributeData, setContributeData] = useState<IssuesDataType | null>(null)
  const [chapterData, setChapterData] = useState<ChapterDataType | null>(null)
  const [committeeData, setCommitteeData] = useState<CommitteeDataType | null>(null)

  useEffect(() => {
    function fetchProjectData<T = ProjectDataType>(mockData: T): Promise<T> {
      return new Promise((resolve) => {
        // Simulating network delay
        setTimeout(() => {
          resolve(mockData)
        }, 0)
      })
    }

    fetchProjectData(MockProjectData)
      .then((data) => setProjectData(data))
      .catch((error) => console.error(error))
    fetchProjectData(MockContributeData)
      .then((data) => setContributeData(data))
      .catch((error) => console.error(error))
    fetchProjectData(MockChaptersData)
      .then((data) => setChapterData(data))
      .catch((error) => console.error(error))
    fetchProjectData(MockCommitteeData)
      .then((data) => setCommitteeData(data))
      .catch((error) => console.error(error))
  }, [])

  const handleButtonClick = () => {
    console.log('Button clicked')
  }

  const SubmitButton = {
    label: 'Contribute',
    icon: <FontAwesomeIconWrapper icon="fa-solid fa-code-fork" />,
    onclick: handleButtonClick,
  }

  return (
    <div className=" w-full min-h-screen flex flex-col justify-normal items-center bg-background text-text p-5 md:p-20 ">
      {/* <ModeToggle className=" fixed top-0 right-0 " /> */}
      <div className=" w-full h-fit flex flex-col justify-normal items-center gap-4 ">
        {projectData &&
          projectData.projects.map((project) => {
            const params: string[] = [
              'idx_updated_at',
              'idx_forks_count',
              'idx_stars_count',
              'idx_contributors_count',
            ]
            // const params: string[] = ["idx_created_at", "idx_comments_count"];
            // const params: string[] = ["idx_updated_at"];
            const filteredIcons = getFilteredIcons(project, params)
            // const formattedUrls = handleSocialUrls(project.idx_related_urls);

            return (
              <Card
                key={project.objectID}
                title={project.idx_name}
                summary={project.idx_summary}
                level={level[`${project.idx_level as keyof typeof level}`]}
                icons={filteredIcons}
                leaders={project.idx_leaders}
                topContributors={project.idx_top_contributors}
                topics={project.idx_topics}
                button={SubmitButton}
                languages={project.idx_topics.slice(0, 3)}
                // social={formattedUrls}
              />
            )
          })}
      </div>
    </div>
  )
}
