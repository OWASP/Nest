import { Tooltip } from '@heroui/tooltip'
import millify from 'millify'
import type { IconType } from 'react-icons'
import { IconWrapper } from 'wrappers/IconWrapper'
import { pluralize } from 'utils/pluralize'

const InfoBlock = ({
  className = '',
  icon,
  pluralizedName,
  precision = 1,
  unit = '',
  value = 0,
}: {
  className?: string
  icon?: IconType
  label?: string
  pluralizedName?: string
  precision?: number
  unit?: string
  value?: number
}) => {
  const name = pluralizedName ? pluralize(value, unit, pluralizedName) : pluralize(value, unit)
  const formattedValue = value ? `${millify(value, { precision })} ${name}` : `No ${name}`
  const tooltipValue = value ? `${value.toLocaleString()} ${name}` : `No ${name}`

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {icon && <IconWrapper icon={icon} className="w-5 text-gray-500" />}
      <div className="text-base text-gray-600 dark:text-gray-300">
        <Tooltip content={tooltipValue} delay={100} closeDelay={100} showArrow placement="top">
          {formattedValue}
        </Tooltip>
      </div>
    </div>
  )
}

export default InfoBlock
