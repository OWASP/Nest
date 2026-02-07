import Link from 'next/link'
import type { LeadersListProps } from 'types/leaders'
import { TruncatedText } from 'components/TruncatedText'

/**
 * Component that renders a list of project leaders as clickable links.
 * Takes a comma-separated string of leader names and renders each as a link
 * to their user profile page.
 *
 * @param {LeadersListProps} props - Component props
 * @param {string} props.leaders - Comma-separated string of leader names
 * @returns {JSX.Element} A list of leader links
 */

const LeadersList = ({ entityKey, leaders }: LeadersListProps) => {
  if (!leaders || leaders.trim() === '') return <>Unknown</>

  const leadersArray = leaders
    .split(',')
    .map((leader) => leader.trim())
    .filter((leader) => leader !== '')

  if (leadersArray.length === 0) return <>Unknown</>

  return (
    <TruncatedText>
      {leadersArray.map((leader, index) => (
        <span key={`${entityKey}-${leader}`}>
          <Link
            href={`/members?q=${encodeURIComponent(leader)}`}
            aria-label={`View profile of ${leader}`}
            className="text-gray-800 hover:underline dark:text-gray-200"
            title={leader}
          >
            {leader}
          </Link>
          {index < leadersArray.length - 1 && ', '}
        </span>
      ))}
    </TruncatedText>
  )
}

export default LeadersList
