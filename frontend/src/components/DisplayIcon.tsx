import { Tooltip } from 'react-tooltip'
import { IconType, tooltipStyle } from '../lib/constants'
import { IconKeys, Icons } from './data'
import FontAwesomeIconWrapper from '../lib/FontAwesomeIconWrapper'

export default function DisplayIcon({ item, icons }: { item: string; icons: IconType }) {
  return icons[item] ? (
    <div
      data-tooltip-id={`icon-tooltip-${item}`}
      data-tooltip-content={`${Icons[item as keyof typeof Icons]?.label}`}
      className=" flex flex-col justify-center items-center gap-1 px-4 "
    >
      <span className="value">{icons[item]}</span>
      <span>
        <FontAwesomeIconWrapper icon={Icons[item as IconKeys]?.icon} />
      </span>
      <Tooltip id={`icon-tooltip-${item}`} style={tooltipStyle} />
    </div>
  ) : null
}
