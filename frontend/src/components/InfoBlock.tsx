import { Tooltip } from '@heroui/tooltip'
import millify from 'millify'
import type { IconType } from 'react-icons'
import { IconWrapper } from 'wrappers/IconWrapper'
import { pluralize } from 'utils/pluralize'

const InfoBlock = ({
  className = '',
  icon,
  label = '',
  pluralizedName,
  precision = 1,
  unit = '',
  value = 0,
}: {
  className?: string
  icon: IconType
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
      <IconWrapper icon={icon} className="mt-1 mr-3 w-5" />
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
