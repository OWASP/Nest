'use client'
import { useQuery } from '@apollo/client'
import { IconProp } from '@fortawesome/fontawesome-svg-core'
import { useRouter } from 'next/navigation'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import { GET_LEADER_DATA } from 'server/queries/userQueries'
import { LeadersListBlockProps } from 'types/leaders'
import { User } from 'types/user'
import AnchorTitle from 'components/AnchorTitle'
import SecondaryCard from 'components/SecondaryCard'
import UserCard from 'components/UserCard'

const LeadersListBlock = ({
  leaders,
  label = 'Leaders',
  icon,
}: {
  leaders: LeadersListBlockProps
  label?: string
  icon?: IconProp
}) => {
  return (
    <SecondaryCard icon={icon} title={<AnchorTitle title={label} />}>
      <div className="flex w-full flex-col items-center justify-around overflow-hidden md:flex-row">
        {Object.keys(leaders).map((username) => (
          <div key={username}>
            <LeaderData username={username} leaders={leaders} />
          </div>
        ))}
      </div>
    </SecondaryCard>
  )
}

const LeaderData = ({
  username,
  leaders,
}: {
  username: string
  leaders: LeadersListBlockProps
}) => {
  const { data, loading, error } = useQuery(GET_LEADER_DATA, {
    variables: { key: username },
  })
  const router = useRouter()

  if (loading) return <p>Loading {username}...</p>
  if (error) return <p>Error loading {username}'s data</p>

  const user = data?.user

  if (!user) {
    return <p>No data available for {username}</p>
  }

  const handleButtonClick = (user: User) => {
    router.push(`/members/${user.login}`)
  }

  return (
    <UserCard
      avatar={user.avatarUrl}
      button={{
        icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
        label: 'View Profile',
        onclick: () => handleButtonClick(user),
      }}
      className="w-42 h-64 bg-inherit"
      company={user.company}
      description={leaders[user.login]}
      location={user.location}
      name={user.name || username}
    />
  )
}

export default LeadersListBlock
