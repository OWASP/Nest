import { IconDefinition } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import millify from 'millify'
import { pluralize } from 'utils/pluralize'

const InfoItem = ({
  icon,
  pluralizedName,
  precision = 1,
  unit,
  value,
}: {
  icon: IconDefinition
  pluralizedName?: string
  precision?: number
  unit: string
  value: number
}) => {
  const name = pluralizedName ? pluralize(value, unit, pluralizedName) : pluralize(value, unit)
  const formattedValue = millify(value, { precision })

  return (
    <div className="flex items-center justify-between">
      <span className="flex items-center">
        <FontAwesomeIcon icon={icon} className="mr-2 h-4 w-4" />
        {name}
      </span>
      <span className="font-medium">{formattedValue}</span>
    </div>
  )
}

export default InfoItem
