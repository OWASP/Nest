import Link from 'next/link'
import { LeadersListProps } from 'types/leaders'

const LeadersList = ({ leaders }: LeadersListProps) => {
  if (!leaders || leaders.trim() === '') return <>Unknown</>

  const leadersArray = leaders.split(',').map((leader) => leader.trim())

  return (
    <>
      {leadersArray.map((leader, index) => (
        <span key={`${leader}-${index}`}>
          <Link
            href={`/community/users?q=${encodeURIComponent(leader)}`}
            aria-label={`View profile of ${leader}`}
          >
            {leader}
          </Link>
          {index < leadersArray.length - 1 && ', '}
        </span>
      ))}
    </>
  )
}

export default LeadersList
