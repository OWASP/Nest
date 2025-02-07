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

const RepositoryDetailsPage = () => {
  const { projectKey, repositoryKey } = useParams()
  const [repository, setRepository] = useState(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const { data, error: graphQLRequestError } = useQuery(GET_REPOSITORY_DATA, {
    variables: { projectKey: `www-project-${projectKey}`, repositoryKey: repositoryKey },
  })
  useEffect(() => {
    if (data) {
      setRepository(data?.repository)
      setIsLoading(false)
    }
    if (graphQLRequestError) {
      toast({
        description: 'Unable to complete the requested operation.',
        title: 'GraphQL Request Failed',
        variant: 'destructive',
      })
      setIsLoading(false)
    }
  }, [data, graphQLRequestError, projectKey])

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner imageUrl="/img/owasp_icon_white_sm.png" />
      </div>
    )
  }

  if (!isLoading && !repository) {
    return (
      <ErrorDisplay
        message="Sorry, the Repository you're looking for doesn't exist"
        statusCode={404}
        title="Repository not found"
      />
    )
  }

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

  const RepositoryStats = [
    { icon: faHistory, value: `${repository?.commitsCount || 'No'} Commits` },
    { icon: faUsers, value: `${repository?.contributorsCount || 'No'} Contributors` },
    { icon: faCodeFork, value: `${repository?.forksCount || 'No'} Forks` },
    { icon: faExclamationCircle, value: `${repository?.openIssuesCount || 'No'} Issues` },
    { icon: faStar, value: `${repository?.starsCount || 'No'} Stars` },
  ]
  return (
    <DetailsCard
      details={repositoryDetails}
      languages={repository.languages}
      recentIssues={repository.issues}
      recentReleases={repository.releases}
      stats={RepositoryStats}
      summary={repository.description}
      title={repository.name}
      topContributors={repository.topContributors}
      topics={repository.topics}
      type="repository"
    />
  )
}
export default RepositoryDetailsPage
