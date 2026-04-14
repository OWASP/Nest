import type { Leader } from 'types/leader'
import Leaders from 'components/Leaders'

interface CardDetailsLeadersProps {
  entityLeaders?: Leader[] | null
}

export default function CardDetailsLeaders({ entityLeaders }: Readonly<CardDetailsLeadersProps>) {
  if (!entityLeaders || entityLeaders.length === 0) {
    return null
  }

  return (
    <div className="mb-8">
      <Leaders users={entityLeaders} />
    </div>
  )
}
