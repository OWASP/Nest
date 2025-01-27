import { FontAwesomeIcon, FontAwesomeIconProps } from '@fortawesome/react-fontawesome'
import { useState, useEffect } from 'react'
import { Tooltip } from 'react-tooltip'
import { CardProps } from 'types/card'
import { desktopViewMinWidth, tooltipStyle } from 'utils/constants'
import { Icons } from 'utils/data'
import { cn } from 'utils/utility'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import ActionButton from 'components/ActionButton'
import ContributorAvatar from 'components/ContributorAvatar'
import DisplayIcon from 'components/DisplayIcon'
import Markdown from 'components/MarkdownWrapper'

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
    <div className="border-border mt-4 mb-2 flex w-full flex-col items-start rounded-md border bg-white pb-4 pl-4 transition-colors duration-300 ease-linear md:max-w-6xl dark:bg-[#212529]">
      <div className="flex w-full flex-col items-start gap-4 pt-2 sm:flex-row sm:items-center sm:gap-6 md:pt-0">
        <div className="flex items-center gap-3">
          {/* Display project level badge (if available) */}
          {level && (
            <span
              data-tooltip-id="level-tooltip"
              data-tooltip-content={`${level.level} project`}
              className={cn('flex h-8 w-8 items-center justify-center rounded-full text-xs shadow')}
              style={{ backgroundColor: level.color }}
            >
              <FontAwesomeIconWrapper icon={level.icon} className="text-white" />
            </span>
          )}
          {/* Project title and link */}
          <a href={url} target="_blank" rel="noopener noreferrer" className="flex-1">
            <h1
              className="max-w-full text-base font-semibold break-words sm:text-lg sm:break-normal lg:text-2xl dark:text-sky-600"
              style={{
                transition: 'color 0.3s ease',
              }}
            >
              {title}
            </h1>
          </a>
        </div>
        {/* Icons associated with the project */}
        <div className="flex min-w-[30%] flex-grow flex-row items-center justify-end overflow-auto">
          {icons &&
            Object.keys(Icons).map((key, index) =>
              icons[key] ? (
                <DisplayIcon
                  key={`${key}-${index}`}
                  item={key}
                  icons={Object.fromEntries(Object.entries(icons).filter(([_, value]) => value))} // only pass in truthy meta data
                  idx={
                    Object.keys(icons).findIndex((e) => e === key) ===
                    Object.keys(icons).filter((key) => icons[key]).length - 1
                      ? -1
                      : Object.keys(icons).findIndex((e) => e === key)
                  }
                />
              ) : null
            )}
        </div>
      </div>
      {/* Link to project name if provided */}
      {projectName && (
        <a href={projectLink} rel="noopener noreferrer" className="mt-2 font-medium">
          {projectName}
        </a>
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
                <div id="social" className="mt-2 flex items-center gap-3">
                  {social.map((item) => (
                    <a
                      key={`${item.title}-${item.url}`}
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2"
                    >
                      <FontAwesomeIcon icon={item.icon as FontAwesomeIconProps['icon']} />
                    </a>
                  ))}
                </div>
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
      <Tooltip id="level-tooltip" style={tooltipStyle} />
    </div>
  )
}

export default Card
