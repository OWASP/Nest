import { useQuery } from '@apollo/client'
import {
  faUserPlus,
  faCodeBranch,
  faUser,
} from '@fortawesome/free-solid-svg-icons'
import { GET_USER_DATA } from 'api/queries/userQueries'
import { toast } from 'hooks/useToast'
import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { UserDetailsProps } from 'types/user'
import { formatDate } from 'utils/dateFormatter'
import { pluralize } from 'utils/pluralize'
import { ErrorDisplay } from 'wrappers/ErrorWrapper'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'
import MetadataManager from 'components/MetadataManager'

const UserDetailsPage = () => {
  const { userKey } = useParams()
  const [user, setUser] = useState<UserDetailsProps | null>()
  const [isLoading, setIsLoading] = useState<boolean>(true)

  const { data, error: graphQLRequestError } = useQuery(GET_USER_DATA, {
    variables: { key: userKey },
  })

  useEffect(() => {
    if (data) {
      setUser(data?.user)
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
  }, [data, graphQLRequestError, userKey])

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner imageUrl="/img/owasp_icon_white_sm.png" />
      </div>
    )
  }

  if (user === null && !isLoading)
    return (
      <ErrorDisplay
        statusCode={404}
        title="User not found"
        message="Sorry, the user you're looking for doesn't exist"
      />
    )

  const UserDetails = [
    { label: 'Summary', value: (user.bio)},
    { label: 'Joined', value: formatDate(user.createdAt) },
    { label: 'Company', value: (user.company) },
    { label: 'Email', value: (user.email)}
  ].filter(detail => detail.value);

  const userStats = [
      {
        icon: faUser,
        value: `${user?.publicRepositoriesCount || 'No'} ${pluralize(user?.publicRepositoriesCount, 'Follower')}`,
      },
      {
        icon: faUserPlus,
        value: `${user?.followersCount || 'No'} ${pluralize(user?.followersCount, 'Following')}`,
      },
      {
        icon: faCodeBranch,
        value: `${user?.publicRepositoriesCount || 'No'} ${pluralize(user?.publicRepositoriesCount, 'Repository', 'Repositories')}`,
      },
    ]

  return (
    <MetadataManager
    pageTitle={user.name || userKey}
    url={user.url}
    >
      <DetailsCard
        details={UserDetails}
        avatarUrl={user?.avatarUrl}
        name={user?.name}
        title={user?.name || user?.login}
        stats={userStats}
        topContributors={[]}
        type="user"
      />
    </MetadataManager>
  )
}


export default UserDetailsPage
