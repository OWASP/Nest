import { useQuery } from '@apollo/client'
import { GET_LEADER_DATA } from 'server/queries/userQueries'
import UserCard from 'components/UserCard'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import SecondaryCard from 'components/SecondaryCard'
import { faArrowUpRightFromSquare } from '@fortawesome/free-solid-svg-icons'

interface LeaderInfo {
  [username: string]: string;
}

interface ProjectLeadersProps {
  leaders: LeaderInfo;
  icon?: any;
  title?: string;
}

const LeaderData = ({ username }: { username: string; description: string }) => {
  const { data, loading, error } = useQuery(GET_LEADER_DATA, {
    variables: { key: username },
  })

  if (loading) return <p>Loading {username}...</p>
  if (error) return <p>Error loading {username}'s data</p>

  const user = data?.user

  if (!user) {
    return <p>No data available for {username}</p>
  }

  return (
    <UserCard
      avatar={user.avatarUrl}
      button={{
        icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
        label: 'View Profile',
        onclick: () => window.open(`/members/${username}`, '_blank', 'noopener,noreferrer'),
      }}
      className="h-64 w-40 bg-inherit"
      company={user.company}
      location={user.location}
      name={user.name || username}
    />
  )
}

const ProjectLeaders = ({ leaders, icon = faArrowUpRightFromSquare, title = "Leaders" }: ProjectLeadersProps) => {
  return (
    <SecondaryCard icon={icon} title={title}>
      <div className="flex w-full flex-col items-center justify-around overflow-hidden md:flex-row">
        {Object.keys(leaders).map((username) => (
          <div key={username}>
            <LeaderData username={username} description={leaders[username]} />
          </div>
        ))}
      </div>
    </SecondaryCard>
  )
}

export default ProjectLeaders
