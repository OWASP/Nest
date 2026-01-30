import { Tooltip } from '@heroui/tooltip'
import Link from 'next/link'
import { FaCalendar } from 'react-icons/fa6'
import { IconWrapper } from 'wrappers/IconWrapper'
import type { CardProps } from 'types/card'
import { ICONS } from 'utils/data'
import { formatDateRange } from 'utils/dateFormatter'
import { getSocialIcon } from 'utils/urlIconMappings'
import ActionButton from 'components/ActionButton'
import ContributorAvatar from 'components/ContributorAvatar'
import DisplayIcon from 'components/DisplayIcon'
import { LabelList } from 'components/LabelList'
import Markdown from 'components/MarkdownWrapper'

const Card = ({
  button,
  cardKey,
  icons,
  labels,
  level,
  projectLink,
  projectName,
  social,
  summary,
  timeline,
  title,
  tooltipLabel,
  topContributors,
  url,
}: CardProps) => {
  return (
    <div className="mx-auto mt-4 mb-2 flex w-full max-w-[95%] flex-col items-start rounded-md border-1 border-gray-200 bg-white p-4 md:max-w-6xl dark:border-gray-700 dark:bg-[#212529]">
      {/* Card Header with Badge and Title */}
      <div className="w-full">
        <div className="flex items-center gap-3">
          {/* Display project level badge (if available) */}
          {level && (
            <Tooltip
              closeDelay={100}
              content={`${level.level} project`}
              id={`level-tooltip-${title}`}
              delay={100}
              placement="top"
              showArrow
            >
              <span
                className="flex h-8 w-8 min-w-8 items-center justify-center rounded-full text-xs shadow"
                style={{ backgroundColor: level.color }}
              >
                <IconWrapper icon={level.icon} className="text-white" />
              </span>
            </Tooltip>
          )}
          {/* Project title and link */}
          {url ? (
            <Link href={url} target="_blank" rel="noopener noreferrer" className="flex-1">
              <h1
                className="max-w-full text-base font-semibold break-words text-blue-400 hover:text-blue-600 sm:text-lg sm:break-normal lg:text-2xl"
                style={{
                  transition: 'color 0.3s ease',
                }}
              >
                {title}
              </h1>
            </Link>
          ) : (
            <div className="flex-1">
              <h1 className="max-w-full text-base font-semibold break-words text-gray-700 dark:text-gray-300 sm:text-lg sm:break-normal lg:text-2xl">
                {title}
              </h1>
            </div>
          )}
        </div>

        {/* Icons associated with the project */}
        {icons && Object.keys(ICONS).some((key) => icons[key]) && (
          <div className="mt-3 flex flex-wrap">
            {Object.keys(ICONS).map((key) =>
              icons[key] ? (
                <DisplayIcon
                  key={key}
                  item={key}
                  icons={Object.fromEntries(Object.entries(icons).filter(([_, value]) => value))}
                />
              ) : null
            )}
          </div>
        )}

        {/* Timeline Section (Optional) */}
        {timeline?.start && timeline?.end && (
          <div className="mt-2 text-sm text-gray-500 dark:text-gray-400">
            <FaCalendar className="mr-2 h-4 w-4" />
            <span>{formatDateRange(timeline.start, timeline.end)}</span>
          </div>
        )}
      </div>

      {/* Project name link (if provided) */}
      {projectName && (
        <Link
          href={projectLink || ''}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-3 font-medium text-gray-700 hover:text-blue-500 dark:text-gray-300"
        >
          {projectName}
        </Link>
      )}

      <Markdown
        content={summary}
        className="mt-2 w-full [overflow-wrap:anywhere] break-words text-gray-600 dark:text-gray-300 [&_a]:break-all [&_code]:break-all"
      />

      <div className="mt-4 w-full">
        {/* Social icons section */}
        {social && social.length > 0 && (
          <div className="mb-3 flex">
            <div className="flex flex-wrap gap-3">
              {social.map((item) => {
                const SocialIcon = getSocialIcon(item.url)
                return (
                  <Link
                    key={`${item.title}-${item.url}`}
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="transition-colors"
                    aria-label={item.title || 'Social media link'}
                  >
                    <SocialIcon className="h-5 w-5 text-blue-500 hover:text-gray-600 dark:hover:text-gray-400" />
                  </Link>
                )
              })}
            </div>
          </div>
        )}

        {/* Flexible bottom row with labels, contributors and action button */}
        <div className="flex w-full flex-col gap-3 sm:flex-row sm:items-center sm:justify-between sm:gap-0">
          {/* Labels Section */}
          {labels && labels.length > 0 && (
            <div className="flex flex-wrap gap-2">
              <LabelList entityKey={`${cardKey}-labels`} labels={labels} maxVisible={5} />
            </div>
          )}
          {/* Contributors section */}
          <div className="flex flex-wrap items-center gap-2">
            {topContributors?.map((contributor, index) => (
              <ContributorAvatar
                key={contributor.login || `contributor-${index}`}
                contributor={contributor}
                uniqueKey={index.toString()}
              />
            ))}
          </div>

          {/* Action Button */}
          <div className="flex sm:justify-end">
            <ActionButton
              tooltipLabel={tooltipLabel}
              url={button.url}
              onClick={button.onclick}
              onKeyDown={button.onkeydown}
            >
              {button.icon}
              {button.label}
            </ActionButton>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Card
