import { IconName, findIconDefinition } from '@fortawesome/fontawesome-svg-core'
import { Tooltip } from '@heroui/tooltip'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'

type BadgeProps = {
  name: string
  cssClass: string
  showTooltip?: boolean
}

const Badges = ({ name, cssClass, showTooltip = true }: BadgeProps) => {
  if (!cssClass || typeof cssClass !== 'string') {
    return (
      <div className="inline-flex items-center">
        <Tooltip content={name} isDisabled={!showTooltip}>
          <FontAwesomeIconWrapper icon={'fa-medal'} className="h-4 w-4" />
        </Tooltip>
      </div>
    )
  }

  const iconDef = findIconDefinition({
    prefix: 'fas',
    iconName: cssClass.split(' ').pop().replace('fa-', '') as IconName,
  })

  return (
    <div className="inline-flex items-center">
      <Tooltip content={name} isDisabled={!showTooltip}>
        <FontAwesomeIconWrapper
          icon={iconDef ? `${prefix} fa-${iconName}` : 'fa-solid fa-question'}
          className="h-4 w-4"
        />
      </Tooltip>
    </div>
  )
    </div>
  )
}

export default Badges
