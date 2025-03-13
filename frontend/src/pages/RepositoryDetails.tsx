import { useQuery } from '@apollo/client'
import {
  faCodeFork,
  faExclamationCircle,
  faHistory,
  faStar,
  faUsers,
} from '@fortawesome/free-solid-svg-icons'
import { GET_REPOSITORY_DATA } from 'api/queries/repositoryQueries'
import { toaster } from 'components/ui/toaster'
import millify from 'millify'
import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { formatDate } from 'utils/dateFormatter'
import { pluralize } from 'utils/pluralize'
import { ErrorDisplay } from 'wrappers/ErrorWrapper'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'
import MetadataManager from 'components/MetadataManager'

const RepositoryDetailsPage = () => {
  const { projectKey, repositoryKey } = useParams()
  const [repository, setRepository] = useState(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const { data, error: graphQLRequestError } = useQuery(GET_REPOSITORY_DATA, {
    variables: { projectKey: projectKey, repositoryKey: repositoryKey },
  })
  useEffect(() => {
    if (data) {
      setRepository(data?.repository)
      setIsLoading(false)
    }
    if (graphQLRequestError) {
      toaster.create({
        description: 'Unable to complete the requested operation.',
        title: 'GraphQL Request Failed',
        type: 'error',
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
    {
      icon: faStar,
      value: `${
        repository.starsCount ? millify(repository.starsCount, { precision: 1 }) : 'No'
      } ${pluralize(repository.starsCount, 'Star')}`,
    },
    {
      icon: faCodeFork,
      value: `${
        repository.forksCount ? millify(repository.forksCount, { precision: 1 }) : 'No'
      } ${pluralize(repository.forksCount, 'Fork')}`,
    },
    {
      icon: faUsers,
      value: `${
        repository.contributorsCount
          ? millify(repository.contributorsCount, { precision: 1 })
          : 'No'
      } ${pluralize(repository.contributorsCount, 'Contributor')}`,
    },

    {
      icon: faExclamationCircle,
      value: `${
        repository.openIssuesCount ? millify(repository.openIssuesCount, { precision: 1 }) : 'No'
      } ${pluralize(repository.openIssuesCount, 'Issue')}`,
    },
    {
      icon: faHistory,
      value: `${
        repository.commitsCount ? millify(repository.commitsCount, { precision: 1 }) : 'No'
      } ${pluralize(repository.commitsCount, 'Commit')}`,
    },
  ]
  return (
    <MetadataManager
      description={repository.description}
      keywords={repository.topics}
      pageTitle={repository.name || repositoryKey}
      url={repository.url}
    >
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
    </MetadataManager>
  )
}
export default RepositoryDetailsPage
