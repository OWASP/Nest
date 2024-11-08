import { Tooltip } from "react-tooltip";
import { IconType, tooltipStyle } from "../lib/constants";
import { cn } from "../lib/utils";
import { Icons } from "./data";



export default function DisplayIcon({ item,icons }: { item: string, icons: IconType }) {
    return ( icons[item] ?
      <div
        data-tooltip-id={`icon-tooltip-${item}`}
        data-tooltip-content={`${Icons[item as keyof typeof Icons]?.label}`}
        className=" flex flex-col justify-center items-center gap-1 px-4 ">
          <span className="value">{icons[item]}</span>
        {/* <span>{Icons[item as keyof typeof Icons]?.label}</span> */}
        <span><i className={cn( Icons[item as keyof typeof Icons]?.icon)}></i></span>
        <Tooltip id={`icon-tooltip-${item}`} style={tooltipStyle}  />
      </div> : null
    )
  }
