import { HStack, Link } from '@chakra-ui/react'
import { FontAwesomeIcon, FontAwesomeIconProps } from '@fortawesome/react-fontawesome'
import { useState, useEffect } from 'react'
import { CardProps } from 'types/card'
import { desktopViewMinWidth } from 'utils/constants'
import { Icons } from 'utils/data'
import { TooltipRecipe } from 'utils/theme'
import { cn } from 'utils/utility'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import ActionButton from 'components/ActionButton'
import ContributorAvatar from 'components/ContributorAvatar'
import DisplayIcon from 'components/DisplayIcon'
import Markdown from 'components/MarkdownWrapper'
import { Tooltip } from 'components/ui/tooltip'

// Initial check for mobile screen size
const isMobileInitial = typeof window !== 'undefined' && window.innerWidth < desktopViewMinWidth

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
  const [isMobile, setIsMobile] = useState(isMobileInitial)

  // Resize listener to adjust display based on screen width
  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth < desktopViewMinWidth
      setIsMobile(mobile)
    }
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  return (
    <div className="mb-2 mt-4 flex w-full flex-col items-start rounded-md border border-border bg-white pb-4 pl-4 dark:bg-[#212529] md:max-w-6xl">
      <div className="mt-2 flex w-full flex-col items-start gap-4 pt-2 sm:flex-col sm:gap-4 md:pt-0">
        <div className="flex items-center gap-3">
          {/* Display project level badge (if available) */}
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
                  'flex h-8 w-8 items-center justify-center rounded-full text-xs shadow'
                )}
                style={{ backgroundColor: level.color }}
              >
                <FontAwesomeIconWrapper icon={level.icon} className="text-white" />
              </span>
            </Tooltip>
          )}
          {/* Project title and link */}
          <Link href={url} target="_blank" rel="noopener noreferrer" className="flex-1">
            <h1
              className="max-w-full break-words text-base font-semibold dark:text-sky-600 sm:break-normal sm:text-lg lg:text-2xl"
              style={{
                transition: 'color 0.3s ease',
              }}
            >
              {title}
            </h1>
          </Link>
        </div>
        {/* Icons associated with the project */}
        {icons && Object.keys(Icons).some((key) => icons[key]) ? (
          <div className="-ml-1.5 flex flex-grow">
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
        ) : null}
      </div>
      {/* Link to project name if provided */}
      {projectName && (
        <Link href={projectLink} rel="noopener noreferrer" className="mt-2 font-medium">
          {projectName}
        </Link>
      )}
      {/* Render project summary using Markdown */}
      <Markdown content={summary} className="py-2 pr-4 text-gray-600 dark:text-gray-300" />

      <div
        className={
          social && social.length > 0
            ? 'flex w-full flex-col gap-2 pr-4'
            : 'flex w-full items-center justify-between'
        }
      >
        {/* Render top contributors as avatars */}
        <div className="mt-3 flex w-full flex-wrap items-center gap-2">
          {topContributors?.map((contributor, index) => (
            <ContributorAvatar
              key={contributor.login || `contributor-${index}`}
              contributor={contributor}
            />
          ))}
        </div>
        {!social || social.length === 0 ? (
          <div
            className={cn(
              'mt-3 flex items-center pr-4',
              isMobile && 'mt-4 w-full justify-end pr-4'
            )}
          >
            <ActionButton tooltipLabel={tooltipLabel} url={button.url} onClick={button.onclick}>
              {button.icon}
              {button.label}
            </ActionButton>
          </div>
        ) : (
          <div
            className={cn(
              'flex w-full flex-wrap items-center justify-between gap-6',
              isMobile && 'items-start'
            )}
          >
            <div
              className={cn('flex w-full items-center justify-between', isMobile && 'flex-wrap')}
            >
              {/* Render social links if available */}
              {social && social.length > 0 && (
                <HStack id="social" mt={2}>
                  {social.map((item) => (
                    <Link
                      key={`${item.title}-${item.url}`}
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      display="flex"
                      alignItems="center"
                      gap={2}
                    >
                      <FontAwesomeIcon icon={item.icon as FontAwesomeIconProps['icon']} />
                    </Link>
                  ))}
                </HStack>
              )}

              {/* Action Button */}
              <div className="flex items-center">
                <ActionButton tooltipLabel={tooltipLabel} url={button.url} onClick={button.onclick}>
                  {button.icon}
                  {button.label}
                </ActionButton>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Card
