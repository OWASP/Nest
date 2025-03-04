import { HStack, Link } from '@chakra-ui/react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { CardProps } from 'types/card'
import { Icons } from 'utils/data'
import { TooltipRecipe } from 'utils/theme'
import { getSocialIcon } from 'utils/urlIconMappings'
import { cn } from 'utils/utility'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import ActionButton from 'components/ActionButton'
import ContributorAvatar from 'components/ContributorAvatar'
import DisplayIcon from 'components/DisplayIcon'
import Markdown from 'components/MarkdownWrapper'
import { Tooltip } from 'components/ui/tooltip'

const Card = ({
  title,
  url,
  summary,
  level,
  icons,
  topContributors,
  button,
  projectName,
  projectLink,
  social,
  tooltipLabel,
}: CardProps) => {
  const hasSocial = social && social.length > 0
  const hasContributors = topContributors && topContributors.length > 0

  return (
    <div
      className={cn(
        'relative mb-4 mt-6 flex w-full flex-col items-start rounded-lg border border-border bg-white p-2 shadow-sm transition-all duration-300 dark:bg-slate-800 sm:p-3 md:max-w-6xl'
      )}
    >
      <div className="flex w-full flex-col items-start gap-1.5">
        <div className="flex w-full items-center gap-2">
          {level && (
            <Tooltip
              id="level-tooltip"
              content={`${level.level} project`}
              openDelay={100}
              closeDelay={100}
              recipe={TooltipRecipe}
              showArrow
            >
              <span
                className={cn(
                  'flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full text-xs shadow-md ring-2 ring-white dark:ring-slate-700 sm:text-sm'
                )}
                style={{ backgroundColor: level.color }}
              >
                <FontAwesomeIconWrapper icon={level.icon} className="text-white" />
              </span>
            </Tooltip>
          )}

          {/* Project Title */}
          <Link
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="group w-full flex-1 no-underline"
          >
            <h1 className="max-w-full text-lg font-bold text-gray-800 transition-colors duration-300 group-hover:text-blue-600 dark:text-white dark:group-hover:text-blue-400 sm:text-xl md:text-2xl">
              {title}
            </h1>
          </Link>
        </div>

        {projectName && (
          <Link
            href={projectLink}
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-xs font-medium text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 sm:text-sm"
          >
            <FontAwesomeIconWrapper icon="link" className="h-2.5 w-2.5 sm:h-3 sm:w-3" />
            {projectName}
          </Link>
        )}

        {/* Technology Icons*/}
        {icons && Object.keys(Icons).some((key) => icons[key]) && (
          <div className="-ml-1 mt-1 flex flex-wrap overflow-x-auto py-1 sm:-ml-1.5">
            {Object.keys(Icons).map((key, index) =>
              icons[key] ? (
                <DisplayIcon
                  key={`${key}-${index}`}
                  item={key}
                  icons={Object.fromEntries(Object.entries(icons).filter(([_, value]) => value))}
                />
              ) : null
            )}
          </div>
        )}

        {/* Summary section */}
        <div className={cn('my-1 w-full rounded-md bg-gray-50 p-1 dark:bg-slate-700/30 sm:p-3')}>
          <Markdown
            content={summary}
            className="prose prose-xs sm:prose-sm dark:prose-invert max-w-none text-gray-700 dark:text-gray-200"
          />
        </div>

        {/* Footer section */}
        {hasSocial ? (
          <div className="mt-2 w-full">
            {/* First row: Contributors only when social links are present */}
            {hasContributors && (
              <div className="mb-2">
                <div className="flex flex-col gap-1">
                  <span className="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
                    Contributors
                  </span>
                  <div className="flex flex-wrap items-center gap-1">
                    {topContributors.map((contributor, index) => (
                      <ContributorAvatar
                        key={contributor.login || `contributor-${index}`}
                        contributor={contributor}
                      />
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Second row: Social links and button on the same line */}
            <div className="flex w-full items-end justify-between">
              <div className="flex flex-col gap-1">
                <span className="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
                  Connect
                </span>
                <HStack className="flex-wrap">
                  {social.map((item) => (
                    <Link
                      key={`${item.title}-${item.url}`}
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex h-7 w-7 items-center justify-center rounded-full bg-gray-100 text-gray-600 transition-colors hover:bg-blue-100 hover:text-blue-600 dark:bg-slate-700 dark:text-gray-300 dark:hover:bg-blue-900 dark:hover:text-blue-300 sm:h-8 sm:w-8"
                    >
                      <FontAwesomeIcon icon={getSocialIcon(item.url)} className="h-5 w-5" />
                    </Link>
                  ))}
                </HStack>
              </div>
              <div className="flex-shrink-0 self-end">
                <ActionButton tooltipLabel={tooltipLabel} url={button.url} onClick={button.onclick}>
                  {button.icon}
                  {button.label}
                </ActionButton>
              </div>
            </div>
          </div>
        ) : (
          <div className="mt-2 flex w-full items-end justify-between">
            {hasContributors ? (
              <div className="flex flex-col gap-1">
                <span className="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
                  Contributors
                </span>
                <div className="flex flex-wrap items-center gap-1">
                  {topContributors.map((contributor, index) => (
                    <ContributorAvatar
                      key={contributor.login || `contributor-${index}`}
                      contributor={contributor}
                    />
                  ))}
                </div>
              </div>
            ) : (
              <div></div>
            )}
            <div className="flex-shrink-0 self-end">
              <ActionButton tooltipLabel={tooltipLabel} url={button.url} onClick={button.onclick}>
                {button.icon}
                {button.label}
              </ActionButton>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Card
