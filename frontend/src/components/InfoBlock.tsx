import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

const InfoBlock = ({ icon, label = '', value, isLink = false, className = '' }) => (
  <div className={`flex ${className}`}>
    <FontAwesomeIcon icon={icon} className="mt-1 mr-3 w-5" />
    <div>
      <div className="text-sm md:text-base">
        {label && <div className="text-sm font-medium">{label}</div>}
        {isLink ? (
          <a href={value} className="hover:underline dark:text-sky-600">
            {value}
          </a>
        ) : (
          value
        )}
      </div>
    </div>
  </div>
)

export default InfoBlock
