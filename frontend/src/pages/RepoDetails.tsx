import { useQuery } from '@apollo/client'
import {
  faCodeFork,
  faExclamationCircle,
  faHistory,
  faStar,
  faUsers,
} from '@fortawesome/free-solid-svg-icons'
import { GET_REPOSITORY_DATA } from 'api/queries/repositoryQueries'
import { toast } from 'hooks/useToast'
import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { formatDate } from 'utils/dateFormatter'
import { ErrorDisplay } from 'wrappers/ErrorWrapper'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'

const RepoDetailsPage = () => {
  const { projectKey, repositoryKey } = useParams()
  const [repository, setRepository] = useState(null)

  const {
    data,
    loading: isGraphQlDataLoading,
    error: graphQLRequestError,
  } = useQuery(GET_REPOSITORY_DATA, {
    variables: { projectKey: `www-project-${projectKey}`, repoKey: repositoryKey },
  })

  useEffect(() => {
    if (data) {
      setRepository(data.project.repositories[0])
    }
    if (graphQLRequestError) {
      toast({
        variant: 'destructive',
        title: 'GraphQL Request Failed',
        description: 'Unable to complete the requested operation.',
      })
    }
  }, [data, graphQLRequestError, projectKey])

  if (isGraphQlDataLoading)
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner imageUrl="/img/owasp_icon_white_sm.png" />
      </div>
    )

  if (!isGraphQlDataLoading && !repository)
    return (
      <ErrorDisplay
        statusCode={404}
        title="Repository not found"
        message="Sorry, the Repository you're looking for doesn't exist"
      />
    )

  const repositoryDetails = [
    {
      label: 'Last Updated',
      value: formatDate(repository.updatedAt),
    },
    {
      label: 'License',
      value: repository.license,
    },
    {
      label: 'Size',
      value: `${repository.size} KB`,
    },
    {
      label: 'URL',
      value: (
        <a href={repository.url} className="hover:underline dark:text-sky-600">
          {repository.url}
        </a>
      ),
    },
  ]

  const RepoStats = [
    { icon: faHistory, value: `${repository?.commitsCount || 'No'} Commits` },
    { icon: faUsers, value: `${repository?.contributorsCount || 'No'} Contributors` },
    { icon: faCodeFork, value: `${repository?.forksCount || 'No'} Forks` },
    { icon: faExclamationCircle, value: `${repository?.openIssuesCount || 'No'} Issues` },
    { icon: faStar, value: `${repository?.starsCount || 'No'} Stars` },
  ]
  return (
    <DetailsCard
      title={repository.name}
      details={repositoryDetails}
      summary={repository.description}
      type="repository"
      stats={RepoStats}
      topContributors={repository.topContributors}
      languages={repository.languages}
      topics={repository.topics}
      recentIssues={repository.issues}
      recentReleases={repository.releases}
    />
  )
}
export default RepoDetailsPage
