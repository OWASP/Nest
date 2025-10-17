import { faChartPie } from '@fortawesome/free-solid-svg-icons'
import SecondaryCard from 'components/SecondaryCard'
import AnchorTitle from 'components/AnchorTitle'
import InfoBlock from 'components/InfoBlock'
import type { IconDefinition } from '@fortawesome/free-solid-svg-icons'

type Stats = {
  icon: IconDefinition
  pluralizedName?: string
  unit?: string
  value: number
}


interface MetricsSectionProps {
  stats?: Stats[]
  type: string
}

const MetricsSection = ({ stats, type }: MetricsSectionProps) =>
  (type === 'project' ||
    type === 'repository' ||
    type === 'committee' ||
    type === 'user' ||
    type === 'organization') && (
    <SecondaryCard
      icon={faChartPie}
      title={<AnchorTitle title="Statistics" />}
      className="md:col-span-2"
    >
      {stats.map((stat, index) => (
        <div key={index}>
          <InfoBlock
            className="pb-1"
            icon={stat.icon}
            pluralizedName={stat.pluralizedName}
            unit={stat.unit}
            value={stat.value}
          />
        </div>
      ))}
    </SecondaryCard>
  )

export default MetricsSection;
