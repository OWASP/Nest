import { millify } from "millify";
import { IconType } from "types/icon";
import { IconKeys, Icons } from "utils/data";
import { TooltipRecipe } from "utils/theme";
import FontAwesomeIconWrapper from "wrappers/FontAwesomeIconWrapper";
import { Tooltip } from "components/ui/tooltip";

export default function DisplayIcon({ item, icons }: { item: string; icons: IconType }) {
  // Preserve underscores to prevent spelling issues
  const normalizedItem = item.toLowerCase();

  // Define container class names dynamically
  const containerClassName = [
    "flex flex-row-reverse items-center justify-center gap-1 px-4 pb-1 -ml-2",
    ["stars_count"].includes(normalizedItem) ? "rotate-container" : "",
    ["forks_count", "contributors_count", "contribution_count"].includes(normalizedItem) ? "flip-container" : "",
  ]
    .filter(Boolean)
    .join(" ");

  // Define icon class names dynamically
  const iconClassName = [
    "text-gray-600 dark:text-gray-300",
    ["stars_count"].includes(normalizedItem) ? "icon-rotate" : "",
    ["forks_count", "contributors_count", "contribution_count"].includes(normalizedItem) ? "icon-flip" : "",
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
