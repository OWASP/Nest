import { faFolderOpen } from '@fortawesome/free-solid-svg-icons'
import SecondaryCard from 'components/SecondaryCard'
import AnchorTitle from 'components/AnchorTitle'
import ModuleCard from 'components/ModuleCard'
import { Contributor } from 'types/contributor'
import type { Module } from 'types/mentorship'

interface ModulesSectionProps {
  modules?: Module[]
  accessLevel: string
  admins?: Contributor[]
  type: string
}

const ModulesSection = ({ modules, accessLevel, admins, type }: ModulesSectionProps) =>
  type === 'program' &&
  modules.length > 0 && (
    <SecondaryCard
      icon={faFolderOpen}
      title={<AnchorTitle title={modules.length === 1 ? 'Module' : 'Modules'} />}
    >
      <ModuleCard modules={modules} accessLevel={accessLevel} admins={admins} />
    </SecondaryCard>
  )

export default ModulesSection;
