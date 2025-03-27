import { HStack, Link } from '@chakra-ui/react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useState, useEffect } from 'react'
import { CardProps } from 'types/card'
import { desktopViewMinWidth } from 'utils/constants'
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

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < desktopViewMinWidth)
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  return (
    <div className="mx-auto mb-2 mt-4 w-full max-w-[95%] rounded-md border border-border bg-white px-4 pb-4 dark:bg-[#212529] md:max-w-6xl">
      <div className="mt-2 flex w-full flex-col gap-4 pt-2 sm:flex-col md:pt-0">
        <div className="flex items-center gap-3">
          {level && (
            <Tooltip
              closeDelay={100}
              content={`${level.level} project`}
              id={`level-tooltip-${title}`}
              openDelay={100}
              positioning={{ placement: 'top' }}
              recipe={TooltipRecipe}
              showArrow
            >
              <span
                className="flex h-8 w-8 items-center justify-center rounded-full shadow"
                style={{ backgroundColor: level.color }}
              >
                <FontAwesomeIconWrapper icon={level.icon} className="text-white" />
              </span>
            </Tooltip>
          )}

          <Link href={url} target="_blank" rel="noopener noreferrer" className="flex-1">
            <h1 className="break-words text-base font-semibold dark:text-sky-600 sm:text-lg lg:text-2xl transition-colors hover:text-blue-500">
              {title}
            </h1>
          </Link>
        </div>

        {icons && Object.keys(Icons).some((key) => icons[key]) && (
          <div className="flex flex-wrap items-center gap-2">
            {Object.keys(Icons).map(
              (key, index) =>
                icons[key] && (
                  <DisplayIcon
                    key={`${key}-${index}`}
                    item={key}
                    icons={Object.fromEntries(Object.entries(icons).filter(([_, value]) => value))}
                  />
                )
            )}
          </div>
        )}
      </div>

      {projectName && (
        <Link href={projectLink} rel="noopener noreferrer" className="mt-2 font-medium text-blue-600 hover:underline">
          {projectName}
        </Link>
      )}

      <Markdown content={summary} className="py-2 pr-4 text-gray-600 dark:text-gray-300" />

      <div className={cn(social?.length ? 'flex w-full flex-col gap-2 pr-4' : 'flex w-full items-center justify-between')}>
        {topContributors && topContributors.length > 0 && (
          <div className="mt-3 flex w-full flex-wrap items-center gap-2">
            {topContributors.map((contributor, index) => (
              <ContributorAvatar
                key={contributor.login || `contributor-${index}`}
                contributor={contributor}
                uniqueKey={index.toString()}
              />
            ))}
          </div>
        )}

        {!social || social.length === 0 ? (
          <div className={cn('mt-3 flex items-center pr-4', isMobile && 'mt-4 w-full justify-end')}>
            <ActionButton tooltipLabel={tooltipLabel} url={button.url} onClick={button.onclick}>
              <FontAwesomeIconWrapper icon={button.icon} /> {button.label}
            </ActionButton>
          </div>
        ) : (
          <div className={cn('flex w-full flex-wrap items-center justify-between gap-6', isMobile && 'items-start')}>
            <div className={cn('flex w-full items-center justify-between', isMobile && 'flex-wrap')}>
              {social && social.length > 0 && (
                <HStack id="social" mt={2}>
                  {social.map((item) => (
                    <Tooltip
                      key={`${item.title}-${item.url}`}
                      content={item.title}
                      recipe={TooltipRecipe}
                      openDelay={150}
                      closeDelay={100}
                      showArrow
                      positioning={{ placement: 'top' }}
                    >
                      <Link
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="transition-transform duration-300 hover:scale-110"
                      >
                        <FontAwesomeIcon
                          icon={getSocialIcon(item.url)}
                          className={`h-5 w-5 transition-colors duration-300 ${
                            {
                              discord: 'text-[#5865F2] hover:text-[#5865F2]',
                              instagram: 'text-[#E4405F] hover:text-[#E4405F]',
                              linkedin: 'text-[#0077B5] hover:text-[#0077B5]',
                              youtube: 'text-[#FF0000] hover:text-[#FF0000]',
                            }[item.title.toLowerCase()] || 'text-gray-500'
                          }`}
                        />
                      </Link>
                    </Tooltip>
                  ))}
                </HStack>
              )}

              <div className="flex items-center">
                <ActionButton tooltipLabel={tooltipLabel} url={button.url} onClick={button.onclick}>
                  <FontAwesomeIconWrapper icon={button.icon} /> {button.label}
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
