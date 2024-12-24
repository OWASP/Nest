import { Tooltip } from 'react-tooltip'

import { IconKeys, Icons } from './data'
import { IconType, tooltipStyle } from 'lib/constants'
import FontAwesomeIconWrapper from 'lib/FontAwesomeIconWrapper'

export default function DisplayIcon({
  item,
  icons,
  idx,
}: {
  item: string
  icons: IconType
  idx: number
}) {
  return icons[item] ? (
    <div
      data-tooltip-id={`icon-tooltip-${item}`}
      data-tooltip-content={`${Icons[item as keyof typeof Icons]?.label}`}
      className={`flex flex-col items-center justify-center gap-1 border-b border-l border-border px-4 pb-1 ${idx == 0 ? 'rounded-bl-md' : ''}`}
    >
      <span className="text-gray-600 dark:text-gray-300">{icons[item]}</span>
      <span>
        <FontAwesomeIconWrapper
          className="text-gray-600 dark:text-gray-300"
          icon={Icons[item as IconKeys]?.icon}
        />
      </span>
      <Tooltip id={`icon-tooltip-${item}`} style={tooltipStyle} />
    </div>
  ) : null
}
