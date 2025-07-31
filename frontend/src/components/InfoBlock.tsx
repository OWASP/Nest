import type { IconProp } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Tooltip } from '@heroui/tooltip'
import millify from 'millify'
import { pluralize } from 'utils/pluralize'

const InfoBlock = ({
  className = '',
  icon,
  label = '',
  pluralizedName,
  precision = 1,
  unit,
  value,
}: {
  className?: string
  icon: IconProp
  label?: string
  pluralizedName?: string
  precision?: number
  unit?: string
  value: number
}) => {
  const name = pluralizedName ? pluralize(value, unit, pluralizedName) : pluralize(value, unit)
  const formattedValue = value ? `${millify(value, { precision })} ${name}` : `No ${name}`
  const tooltipValue = value ? `${value.toLocaleString()} ${name}` : `No ${name}`

  return (
    <div className={`flex ${className}`}>
      <FontAwesomeIcon icon={icon} className="mr-3 mt-1 w-5" />
      <div>
        <div className="text-sm md:text-base">
          {label && <div className="text-sm font-medium">{label}</div>}
          <Tooltip content={tooltipValue} delay={100} closeDelay={100} showArrow placement="top">
            {formattedValue}
          </Tooltip>
        </div>
      </div>
    </div>
  )
}

export default InfoBlock
