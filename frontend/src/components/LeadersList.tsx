import { Link } from 'react-router-dom'
import { LeadersListProps } from 'types/leaders'

const LeadersList = ({ leaders }: LeadersListProps) => {
  if (!leaders || leaders.trim() === '') return <>Unknown</>

  const leadersArray = leaders.split(',').map((leader) => leader.trim())

  return (
    <>
      {leadersArray.map((leader, index) => (
        <span key={leader}>
          <Link to={`/community/users?q=${encodeURIComponent(leader)}`}>{leader}</Link>
          {index < leadersArray.length - 1 && ', '}
        </span>
      ))}
    </>
  )
}

export default LeadersList
