import { Link } from '@chakra-ui/react'
import { LeaderLinksProps } from 'types/leader'

const LeaderLinks = ({ leaders }: LeaderLinksProps) => {
  return (
    <span>
      {leaders.map((leader, index) => (
        <span key={leader}>
          <Link
            href={`/community/users?q=${encodeURIComponent(leader)}`}
            target="_blank"
            className="text-blue-600 hover:underline dark:text-blue-400"
          >
            {leader}
          </Link>
          {index < leaders.length - 1 && ', '}
        </span>
      ))}
    </span>
  )
}

export default LeaderLinks
