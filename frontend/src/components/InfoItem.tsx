import { IconDefinition } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Tooltip } from '@heroui/tooltip'
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
  const tooltipValue = value ? `${value.toLocaleString()} ${name}` : `No ${name}`

  return (
    <div className="flex items-center justify-between">
      <span className="flex items-center">
        <FontAwesomeIcon icon={icon} className="mr-2 h-4 w-4" />
        {name}
      </span>
      <Tooltip content={tooltipValue} delay={100} closeDelay={100} showArrow placement="top">
        <span className="font-medium">{formattedValue}</span>
      </Tooltip>
    </div>
  )
}

export const TextInfoItem = ({
  icon,
  label,
  value,
}: {
  icon: IconDefinition
  label: string
  value: string
}) => {
  return (
    <div className="flex items-center gap-2 text-sm text-gray-400">
      <FontAwesomeIcon icon={icon} className="text-xs" />
      <span className="font-medium">{label}:</span> {value}
    </div>
  )
}

export default InfoItem
