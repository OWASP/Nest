import { FaFolderOpen } from 'react-icons/fa6'
import type { Module } from 'types/mentorship'
import type { RepositoryCardProps } from 'types/project'
import AnchorTitle from 'components/AnchorTitle'
import type { CardType } from 'components/CardDetailsPage'
import ModuleCard from 'components/ModuleCard'
import RepositoryCard from 'components/RepositoryCard'
import SecondaryCard from 'components/SecondaryCard'

interface CardDetailsRepositoriesModulesProps {
  type: CardType
  programKey?: string
  accessLevel?: string
  repositories?: RepositoryCardProps[]
  modules?: Module[]
  admins?: Array<{ login: string }>
}

const CardDetailsRepositoriesModules = ({
  type,
  programKey,
  accessLevel,
  repositories = [],
  modules,
  admins,
}: CardDetailsRepositoriesModulesProps) => {
  return (
    <>
      {(type === 'project' || type === 'user' || type === 'organization') &&
        repositories.length > 0 && (
          <SecondaryCard icon={FaFolderOpen} title={<AnchorTitle title="Repositories" />}>
            <RepositoryCard maxInitialDisplay={4} repositories={repositories} />
          </SecondaryCard>
        )}
      {type === 'program' &&
        modules &&
        modules.length > 0 &&
        (() => {
          const modulesList = modules
          return (
            <>
              {modulesList.length === 1 ? (
                <div className="mb-8">
                  <ModuleCard
                    modules={modulesList}
                    accessLevel={accessLevel}
                    admins={admins}
                    programKey={programKey}
                  />
                </div>
              ) : (
                <SecondaryCard icon={FaFolderOpen} title={<AnchorTitle title="Modules" />}>
                  <ModuleCard
                    modules={modulesList}
                    accessLevel={accessLevel}
                    admins={admins}
                    programKey={programKey}
                  />
                </SecondaryCard>
              )}
            </>
          )
        })()}
    </>
  )
}

export default CardDetailsRepositoriesModules
