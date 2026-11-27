import type { Leader } from 'types/leader'
import LeadersList from 'components/Leaders'

interface LeadersProps {
  entityLeaders?: Leader[] | null
}

export default function Leaders({ entityLeaders }: Readonly<LeadersProps>) {
  if (!entityLeaders || entityLeaders.length === 0) {
    return null
  }

  return (
    <div className="mb-8">
      <LeadersList users={entityLeaders} />
    </div>
  )
}
