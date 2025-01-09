import { FontAwesomeIcon, FontAwesomeIconProps } from '@fortawesome/react-fontawesome'
import { useState, useEffect } from 'react'
import { Tooltip } from 'react-tooltip'
import { CardProps, tooltipStyle } from 'lib/constants'
import FontAwesomeIconWrapper from 'lib/FontAwesomeIconWrapper'
import { cn } from 'lib/utils'
import ActionButton from 'components/ActionButton'
import ContributorAvatar from 'components/ContributorAvatar'
import { Icons } from 'components/data'
import DisplayIcon from 'components/DisplayIcon'
import Markdown from 'components/MarkdownWrapper'
import TopicBadge from 'components/TopicBadge'

// Initial check for mobile screen size
const isMobileInitial = typeof window !== 'undefined' && window.innerWidth < 768

const Card = ({
  title,
  url,
  summary,
  level,
  icons,
  leaders,
  topContributors,
  topics,
  button,
  projectName,
  projectLink,
  languages,
  social,
  tooltipLabel,
}: CardProps) => {
  const [visibleLanguages, setVisibleLanguages] = useState(isMobileInitial ? 4 : 18)
  const [visibleTopics, setVisibleTopics] = useState(isMobileInitial ? 4 : 18)
  const [toggleLanguages, setToggleLanguages] = useState(false)
  const [toggleTopics, setToggleTopics] = useState(false)
  const [isMobile, setIsMobile] = useState(isMobileInitial)

  // Resize listener to adjust display based on screen width
  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth < 768
      setIsMobile(mobile)
      setVisibleLanguages(mobile ? 4 : 18)
      setVisibleTopics(mobile ? 4 : 18)
    }
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  const loadMoreLanguages = () => {
    setVisibleLanguages(toggleLanguages ? (isMobile ? 4 : 18) : languages?.length || 0)
    setToggleLanguages(!toggleLanguages)
  }

  const loadMoreTopics = () => {
    setVisibleTopics(toggleTopics ? (isMobile ? 4 : 18) : topics?.length || 0)
    setToggleTopics(!toggleTopics)
  }

  return (
    <div className="mb-2 mt-4 flex w-full flex-col items-start rounded-md border border-border bg-white pb-4 pl-4 transition-colors duration-300 ease-linear dark:bg-[#212529] md:max-w-6xl">
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
            <h1 className="max-w-full break-words text-base font-semibold dark:text-sky-600 sm:break-normal sm:text-lg lg:text-2xl">
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
        <a
          href={projectLink}
          rel="noopener noreferrer"
          className="mt-2 font-medium"
        >
          {projectName}
        </a>
      )}
      {/* Render project summary using Markdown */}
      <Markdown content={summary} className="py-2 pr-4 text-gray-600 dark:text-gray-300" />
      {/* Display leaders of the project */}
      {leaders && (
        <h2 className="py-1">
          <span className="font-semibold text-gray-600 dark:text-gray-300">
            {leaders.length > 1 ? 'Leaders: ' : 'Leader: '}
          </span>
          {leaders.map((leader, index) => (
            <span key={`${leader}-${index}`} className="text-gray-600 dark:text-gray-300">
              {index !== leaders.length - 1 ? `${leader}, ` : leader}
            </span>
          ))}
        </h2>
      )}
      <div className="flex w-full flex-col gap-4 pr-4">
        {/* Render top contributors as avatars */}
        <div className="flex w-full flex-wrap items-center gap-2">
          {topContributors?.map((contributor, index) => (
            <ContributorAvatar
              key={contributor.login || `contributor-${index}`}
              contributor={contributor}
            />
          ))}
        </div>
        <div
          className={cn(
            'flex w-full items-center justify-between gap-6',
            isMobile && (toggleLanguages || toggleTopics) && 'flex-col items-start'
          )}
        >
          {/* Render languages and topics with load more functionality */}
          <div
            className={cn(
              'flex flex-wrap items-center gap-4',
              isMobile && (toggleLanguages || toggleTopics) && 'w-full'
            )}
          >
            {languages && (
              <div id="languages" className="flex flex-wrap items-center gap-3">
                {languages.slice(0, visibleLanguages).map((language, index) => (
                  <TopicBadge
                    key={language || `language-${index}`}
                    topic={language}
                    tooltipLabel={`This repository uses ${language}`}
                    type="language"
                  />
                ))}
                {languages.length > 8 && (
                  <button
                    onClick={loadMoreLanguages}
                    className="mt-2 text-gray-600 dark:text-gray-300"
                  >
                    {toggleLanguages ? 'Show less' : 'Show more'}
                  </button>
                )}
              </div>
            )}
            {topics && topics.length > 0 && (
              <div id="topics" className="flex flex-wrap items-center gap-3">
                {topics.slice(0, visibleTopics).map((topic, index) => (
                  <TopicBadge
                    key={topic || `topic-${index}`}
                    topic={topic}
                    tooltipLabel={`This project is labeled as "${topic}"`}
                    type="topic"
                  />
                ))}
                {topics.length > 18 && (
                  <button
                    onClick={loadMoreTopics}
                    className="mt-2 text-gray-600 dark:text-gray-300"
                  >
                    {toggleTopics ? 'Show less' : 'Show more'}
                  </button>
                )}
              </div>
            )}
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
          </div>
          {/* Action button */}
          <div
            className={cn(
              'flex items-center',
              isMobile && (toggleLanguages || toggleTopics) && 'mt-4 w-full justify-end'
            )}
          >
            <ActionButton tooltipLabel={tooltipLabel} url={button.url} onClick={button.onclick}>
              {button.icon}
              {button.label}
            </ActionButton>
          </div>
        </div>
      </div>
      <Tooltip id="level-tooltip" style={tooltipStyle} />
    </div>
  )
}

export default Card
