import { FaFolderOpen } from 'react-icons/fa6'
import type { Module } from 'types/mentorship'
import type { RepositoryCardProps } from 'types/project'
import AnchorTitle from 'components/AnchorTitle'
import ModuleCard from 'components/ModuleCard'
import RepositoryCard from 'components/RepositoryCard'
import SecondaryCard from 'components/SecondaryCard'

interface RepositoriesModulesProps {
  programKey?: string
  accessLevel?: string
  repositories?: RepositoryCardProps[]
  modules?: Module[]
  admins?: Array<{ login: string }>
}

const RepositoriesModules = ({
  programKey,
  accessLevel,
  repositories = [],
  modules,
  admins,
}: RepositoriesModulesProps) => {
  return (
    <>
      {repositories.length > 0 && (
        <SecondaryCard icon={FaFolderOpen} title={<AnchorTitle title="Repositories" />}>
          <RepositoryCard maxInitialDisplay={6} repositories={repositories} />
        </SecondaryCard>
      )}
      {modules &&
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

export default RepositoriesModules
