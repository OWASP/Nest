import { Link } from 'react-router-dom'
import { LeadersListProps } from 'types/leaders'

/**
 * Component that renders a list of project leaders as clickable links.
 * Takes a comma-separated string of leader names and renders each as a link
 * to their user profile page.
 *
 * @param {LeadersListProps} props - Component props
 * @param {string} props.leaders - Comma-separated string of leader names
 * @returns {JSX.Element} A list of leader links
 */
import { TruncatedText } from './TruncatedText'

const LeadersList = ({ leaders }: LeadersListProps) => {
  if (!leaders || leaders.trim() === '') return <>Unknown</>

  const leadersArray = leaders.split(',').map((leader) => leader.trim())

  return (
    <span className="flex flex-wrap items-center gap-x-1">
      {leadersArray.map((leader, index) => (
        <span key={`${leader}-${index}`} className="flex items-center">
          <Link
            to={`/community/users?q=${encodeURIComponent(leader)}`}
            aria-label={`View profile of ${leader}`}
            className="hover:underline"
          >
            <TruncatedText text={leader} />
          </Link>
          {index < leadersArray.length - 1 && <span className="ml-1">, </span>}
        </span>
      ))}
    </span>
  )
}

export default LeadersList
