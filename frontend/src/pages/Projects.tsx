import Card from '../components/Card'
import { level } from '../components/data'
import SearchBar from '../components/Search'
import { useSearchQuery } from '../hooks/useSearchquery'
import FontAwesomeIconWrapper from '../lib/FontAwesomeIconWrapper'
import { ProjectDataType } from '../lib/types'
import { getFilteredIcons } from '../lib/utils'
import { API_URL } from '../utils/credentials'

export default function Projects() {
  const {
    data: projectData,
    setData: setProjectData,
    defaultData: defaultProjects,
    initialQuery,
  } = useSearchQuery<ProjectDataType>({
    apiUrl: `${API_URL}/owasp/search/project`,
    entityKey: 'projects',
    initialTitle: 'OWASP Projects',
  })

  return (
    <div className="flex min-h-screen w-full flex-col items-center justify-normal p-5 text-text">
      <div className="flex h-fit w-full flex-col items-center justify-normal gap-4">
        <SearchBar
          placeholder="Search for OWASP projects..."
          searchEndpoint={`${API_URL}/owasp/search/project`}
          onSearchResult={setProjectData}
          defaultResults={defaultProjects}
          initialQuery={initialQuery}
        />
        {projectData?.projects?.map((project, index) => {
          const params: string[] = [
            'idx_updated_at',
            'idx_forks_count',
            'idx_stars_count',
            'idx_contributors_count',
          ]
          const filteredIcons = getFilteredIcons(project, params)

          const handleButtonClick = () => {
            window.open(`/projects/contribute?q=${project.idx_name}`, '_blank')
          }

          const SubmitButton = {
            label: 'Contribute',
            icon: <FontAwesomeIconWrapper icon="fa-solid fa-code-fork" />,
            onclick: handleButtonClick,
          }

          return (
            <Card
              key={project.objectID || `project-${index}`}
              title={project.idx_name}
              url={project.idx_url}
              summary={project.idx_summary}
              level={level[`${project.idx_level as keyof typeof level}`]}
              icons={filteredIcons}
              leaders={project.idx_leaders}
              topContributors={project.idx_top_contributors}
              topics={project.idx_topics}
              button={SubmitButton}
              tooltipLabel={`Contribute to ${project.idx_name}`}
            />
          )
        })}
      </div>
    </div>
  )
}
