import type { IconType } from 'react-icons'
import type { Contributor } from 'types/contributor'
import { getMemberUrl } from 'utils/urlFormatter'
import ContributorsList from 'components/ContributorsList'

interface TopContributorsListProps {
  contributors: Contributor[]
  label?: string
  maxInitialDisplay?: number
  icon?: IconType
}

const TopContributorsList = ({
  contributors,
  label = 'Top Contributors',
  maxInitialDisplay = 12,
  icon,
}: TopContributorsListProps) => (
  <ContributorsList
    contributors={contributors}
    label={label}
    maxInitialDisplay={maxInitialDisplay}
    icon={icon}
    getUrl={getMemberUrl}
  />
)

export default TopContributorsList
