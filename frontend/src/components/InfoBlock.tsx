import { Link } from '@chakra-ui/react'
import { IconProp } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

const InfoBlock = ({
  icon,
  label = '',
  value,
  isLink = false,
  className = '',
}: {
  icon: IconProp
  label?: string
  value: string
  isLink?: boolean
  className?: string
}) => (
  <div className={`flex ${className}`}>
    <FontAwesomeIcon icon={icon} className="mr-3 mt-1 w-5" />
    <div>
      <div className="text-sm md:text-base">
        {label && <div className="text-sm font-medium">{label}</div>}
        {isLink ? (
          <Link href={value} className="hover:underline dark:text-sky-600">
            {value}
          </Link>
        ) : (
          value
        )}
      </div>
    </div>
  </div>
)

export default InfoBlock
