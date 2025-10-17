import { faFolderOpen } from '@fortawesome/free-solid-svg-icons'
import SecondaryCard from 'components/SecondaryCard'
import AnchorTitle from 'components/AnchorTitle'
import RepositoriesCard from 'components/RepositoriesCard'
import type { RepositoryCardProps } from 'types/project'

interface RepositoriesSectionProps {
  repositories?: RepositoryCardProps[]
  type: string
}

const RepositoriesSection = ({ repositories, type }: RepositoriesSectionProps) =>
  (type === 'project' || type === 'user' || type === 'organization') &&
  repositories.length > 0 && (
    <SecondaryCard icon={faFolderOpen} title={<AnchorTitle title="Repositories" />}>
      <RepositoriesCard maxInitialDisplay={4} repositories={repositories} />
    </SecondaryCard>
  )

export default RepositoriesSection;
