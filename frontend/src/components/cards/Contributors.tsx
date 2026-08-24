import { HiUserGroup } from 'react-icons/hi'
import type { Contributor } from 'types/contributor'
import { getMemberUrl, getMenteeUrl } from 'utils/urlFormatter'
import ContributorsList from 'components/ContributorsList'

interface ContributorsProps {
  entityKey?: string
  programKey?: string
  topContributors?: Contributor[]
  admins?: Contributor[]
  mentors?: Contributor[]
  mentees?: Contributor[]
}

const Contributors = ({
  entityKey,
  programKey,
  topContributors,
  admins,
  mentors,
  mentees,
}: ContributorsProps) => {
  return (
    <>
      {topContributors && (
        <ContributorsList
          contributors={topContributors}
          icon={HiUserGroup}
          maxInitialDisplay={12}
          title="Top Contributors"
          getUrl={getMemberUrl}
        />
      )}
      {admins && admins.length > 0 && (
        <ContributorsList
          icon={HiUserGroup}
          contributors={admins}
          maxInitialDisplay={6}
          title="Admins"
          getUrl={getMemberUrl}
        />
      )}
      {mentors && mentors.length > 0 && (
        <ContributorsList
          icon={HiUserGroup}
          contributors={mentors}
          maxInitialDisplay={6}
          title="Mentors"
          getUrl={getMemberUrl}
        />
      )}
      {mentees && mentees.length > 0 && (
        <ContributorsList
          icon={HiUserGroup}
          contributors={mentees}
          maxInitialDisplay={6}
          title="Mentees"
          getUrl={(login) => getMenteeUrl(programKey || '', entityKey || '', login)}
        />
      )}
    </>
  )
}

export default Contributors
