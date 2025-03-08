import { millify } from "millify";
import { IconType } from "types/icon";
import { IconKeys, Icons } from "utils/data";
import { TooltipRecipe } from "utils/theme";
import FontAwesomeIconWrapper from "wrappers/FontAwesomeIconWrapper";
import { Tooltip } from "components/ui/tooltip";

export default function DisplayIcon({ item, icons }: { item: string; icons: IconType }) {

  const normalizedItem = item.replace(/_/g, "").toLowerCase();
   const containerClassName = [
    "flex flex-row-reverse items-center justify-center gap-1 px-4 pb-1 -ml-2",
    ["starscount"].includes(normalizedItem) ? "rotate-container" : "",
    ["forkscount", "contributorscount", "contributioncount"].includes(normalizedItem) ? "flip-container" : "",
  ]
    .filter(Boolean)
    .join(" ");
  const iconClassName = [
    "text-gray-600 dark:text-gray-300",
    ["starscount"].includes(normalizedItem) ? "icon-rotate" : "",
    ["forkscount", "contributorscount", "contributioncount"].includes(normalizedItem) ? "icon-flip" : "",
  ]
    .filter(Boolean)
    .join(" ");

  return icons[item] ? (
    <Tooltip
      content={Icons[item as IconKeys]?.label || "Info"}
      recipe={TooltipRecipe}
      openDelay={150}
      closeDelay={100}
      showArrow
      positioning={{ placement: "top" }}
    >
      <div className={containerClassName}>
        {/* Display formatted number if the value is numeric */}
        <span className="text-gray-600 dark:text-gray-300">
          {typeof icons[item] === "number" ? millify(icons[item], { precision: 1 }) : icons[item]}
        </span>
        <span>
          <FontAwesomeIconWrapper className={iconClassName} icon={Icons[item as IconKeys]?.icon} />
        </span>
      </div>
    </Tooltip>
  ) : null;
}
