import { Tooltip } from '@heroui/tooltip'
import millify from 'millify'
import type { IconType } from 'react-icons'
import { IconWrapper } from 'wrappers/IconWrapper'
import { pluralize } from 'utils/pluralize'

const InfoItem = ({
  icon,
  pluralizedName,
  precision = 1,
  unit,
  value,
}: {
  icon: IconType
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
        <IconWrapper icon={icon} className="mr-2 h-4 w-4" />
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
  icon: IconType
  label: string
  value: string
}) => {
  return (
    <div className="flex items-center gap-2 text-sm text-gray-800 dark:text-gray-300">
      <IconWrapper icon={icon} className="text-xs" />
      <span className="font-medium">{label}:</span> {value}
    </div>
  )
}

export default InfoItem
