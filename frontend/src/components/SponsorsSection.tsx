import SponsorCard from 'components/SponsorCard'

interface SponsorsSectionProps {
  entityKey?: string
  projectName?: string
  title?: string
  type: string
}

const SponsorsSection = ({ entityKey, projectName, title, type }: SponsorsSectionProps) =>
  entityKey &&
  ['chapter', 'project', 'repository'].includes(type) && (
    <SponsorCard
      target={entityKey}
      title={projectName || title}
      type={type === 'chapter' ? 'chapter' : 'project'}
    />
  )

export default SponsorsSection;
