import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Tooltip } from '@heroui/tooltip'
import Link from 'next/link'
import { useState, useEffect } from 'react'
import { CardProps } from 'types/card'
import { desktopViewMinWidth } from 'utils/constants'
import { Icons } from 'utils/data'
import { getSocialIcon } from 'utils/urlIconMappings'
import { cn } from 'utils/utility'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import ContributorAvatar from 'components/ContributorAvatar'
import ActionButton from './ActionButton'
import DisplayIcon from './DisplayIcon'
import Markdown from './MarkdownWrapper'

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
    <div className="mx-auto mb-2 mt-4 flex w-full max-w-[95%] flex-col items-start rounded-md border border-border bg-white px-4 pb-4 pl-4 dark:bg-[#212529] md:max-w-6xl">
      <div className="mt-2 flex w-full flex-col items-start gap-4 pt-2 sm:flex-col sm:gap-4 md:pt-0">
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
              className="max-w-full break-words text-base font-semibold text-blue-400 sm:break-normal sm:text-lg lg:text-2xl"
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
        <Link href={projectLink || ''} rel="noopener noreferrer" className="mt-2 font-medium">
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
              uniqueKey={index.toString()}
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
                <div id="social" className="mt-2 flex flex-row gap-1">
                  {social.map((item) => (
                    <Link
                      key={`${item.title}-${item.url}`}
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2"
                    >
                      <FontAwesomeIcon icon={getSocialIcon(item.url)} className="h-5 w-5" />
                    </Link>
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
    </div>
  )
}

export default Card
