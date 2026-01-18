import type { IconType } from 'react-icons'
import type { Contributor } from 'types/contributor'
import ContributorsList from 'components/ContributorsList'

interface MenteeContributorsListProps {
  contributors: Contributor[]
  label?: string
  maxInitialDisplay?: number
  icon?: IconType
  programKey: string
  moduleKey: string
}

const MenteeContributorsList = ({
  contributors,
  label = 'Mentees',
  maxInitialDisplay = 12,
  icon,
  programKey,
  moduleKey,
}: MenteeContributorsListProps) => {
  const getMenteeUrl = (login: string) =>
    `/my/mentorship/programs/${programKey}/modules/${moduleKey}/mentees/${login}`

  return (
    <ContributorsList
      contributors={contributors}
      label={label}
      maxInitialDisplay={maxInitialDisplay}
      icon={icon}
      getUrl={getMenteeUrl}
    />
  )
}

export default MenteeContributorsList
