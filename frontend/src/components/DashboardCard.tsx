import { IconProp } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import SecondaryCard from 'components/SecondaryCard'
export default function DashboardCard({
  title,
  icon,
  stats,
}: {
  title: string
  icon: IconProp
  stats: number | string
}) {
  return (
    <SecondaryCard
      title={title}
      className="transition-colors duration-300 hover:bg-blue-200 dark:hover:bg-blue-700"
    >
      <span className="flex items-start gap-2 text-3xl font-light">
        <FontAwesomeIcon icon={icon} />
        <p>{stats}</p>
      </span>
    </SecondaryCard>
  )
}
