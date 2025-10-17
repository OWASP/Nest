import { faUsers } from '@fortawesome/free-solid-svg-icons'
import TopContributorsList from 'components/TopContributorsList'
import type { Contributor } from 'types/contributor'

interface ContributorsSectionProps {
  topContributors?: Contributor[]
  mentors?: Contributor[]
  admins?: Contributor[]
  type: string
}

const ContributorsSection = ({
  topContributors,
  admins,
  mentors,
  type,
}: ContributorsSectionProps ) => (
  <>
    {topContributors && (
      <TopContributorsList contributors={topContributors} icon={faUsers} maxInitialDisplay={12} />
    )}
    {admins && admins.length > 0 && type === 'program' && (
      <TopContributorsList
        icon={faUsers}
        contributors={admins}
        maxInitialDisplay={6}
        label="Admins"
      />
    )}
    {mentors && mentors.length > 0 && (
      <TopContributorsList
        icon={faUsers}
        contributors={mentors}
        maxInitialDisplay={6}
        label="Mentors"
      />
    )}
  </>
)

export default ContributorsSection;
