import { IconProp } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import React from 'react'
import AnchorTitle from 'components/AnchorTitle'
import SecondaryCard from 'components/SecondaryCard'

const DashboardCard: React.FC<{
  readonly title: string
  readonly icon: IconProp
  readonly stats: string
}> = ({ title, icon, stats }) => {
  return (
    <SecondaryCard
      title={<AnchorTitle title={title} />}
      className="overflow-hidden transition-colors duration-300 hover:bg-blue-100 dark:hover:bg-blue-950"
    >
      <span className="flex items-center gap-2 text-2xl font-light">
        <FontAwesomeIcon icon={icon} />
        <p>{stats}</p>
      </span>
    </SecondaryCard>
  )
}

export default DashboardCard
