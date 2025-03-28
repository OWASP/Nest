import { IconProp } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import millify from 'millify'
import { pluralize } from 'utils/pluralize'

const InfoBlock = ({
  icon,
  label = '',
  value,
  precision = 1,
  unit,
  pluralizedName,
  className = '',
}: {
  icon: IconProp
  label?: string
  value: number
  className?: string
  precision?: number
  unit?: string
  pluralizedName?: string
}) => {
  const name = pluralizedName ? pluralize(value, unit, pluralizedName) : pluralize(value, unit)

  const formattedValue = value ? `${millify(value, { precision })} ${name}` : `No ${name}`

  return (
    <div className={`flex ${className}`}>
      <FontAwesomeIcon icon={icon} className="mr-3 mt-1 w-5" />
      <div>
        <div className="text-sm md:text-base">
          {label && <div className="text-sm font-medium">{label}</div>}
          {formattedValue}
        </div>
      </div>
    </div>
  )
}

export default InfoBlock
