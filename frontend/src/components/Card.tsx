import { FontAwesomeIcon, FontAwesomeIconProps } from '@fortawesome/react-fontawesome'
import { useState } from 'react'
import { Tooltip } from 'react-tooltip'

import ActionButton from './ActionButton'
import ContributorAvatar from './ContributorAvatar'
import { Icons } from './data'
import DisplayIcon from './DisplayIcon'
import TopicBadge from './TopicBadge'
import { CardProps, tooltipStyle } from '../lib/constants'
import FontAwesomeIconWrapper from '../lib/FontAwesomeIconWrapper'
import { cn } from '../lib/utils'

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
  const [visibleLanguages, setVisibleLanguages] = useState(18)
  const [visibleTopics, setVisibleTopics] = useState(18)

  const [toggleLanguages, setToggleLanguages] = useState(true)
  const [toggleTopics, setToggleTopics] = useState(true)

  const loadMoreLanguages = () => {
    if (toggleLanguages) setVisibleLanguages(languages?.length as number)
    else setVisibleLanguages(18)
    setToggleLanguages(!toggleLanguages)
  }

  const loadMoreTopics = () => {
    if (toggleTopics) setVisibleTopics(topics?.length as number)
    else setVisibleTopics(18)
    setToggleTopics(!toggleTopics)
  }

  return (
    <div className="flex h-fit w-full flex-col items-start gap-4 rounded-md border border-border py-6 pl-4 pt-0 sm:pl-6 md:max-w-6xl md:gap-2">
      <div className="flex w-full flex-wrap items-center justify-between gap-2">
        <div className="mt-4 flex items-center justify-start gap-2">
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
          <a href={url} target="_blank" rel="noopener noreferrer" className="flex-1">
            <h1 className="text-lg font-semibold sm:text-2xl dark:text-sky-600">{title}</h1>
          </a>
        </div>
        <div className="flex min-w-[30%] flex-wrap items-center justify-end">
          {icons &&
            Object.keys(Icons).map((key, index) =>
              icons[key] !== undefined ? (
                <DisplayIcon key={`${key}-${index}`} item={key} icons={icons} idx={index} />
              ) : null
            )}
        </div>
      </div>
      <p className="mt-2 text-sm text-gray-600 sm:text-base dark:text-gray-300 mr-2">{summary}</p>
      <h2 className="text-sm sm:text-base">
        {leaders && (
          <span className="font-semibold text-gray-600 dark:text-gray-300">
            {leaders.length > 1 ? 'Leaders: ' : 'Leader: '}
          </span>
        )}
        {leaders &&
          leaders.map((leader, index) => (
            <span key={`${leader}-${index}`} className="text-gray-600 dark:text-gray-300 mr-2">
              {index !== leaders.length - 1 ? `${leader}, ` : `${leader}`}
            </span>
          ))}
      </h2>
      <div className="flex w-full flex-col justify-between sm:flex-row">
        <div className="flex-auto">
          <div className="flex flex-wrap items-center gap-2">
            {topContributors &&
              topContributors.map((contributor, index) => (
                <ContributorAvatar
                  key={contributor.login || `contributor-${index}`}
                  contributor={contributor}
                />
              ))}
          </div>
          {projectName && (
            <a
              href={projectLink}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm sm:text-base"
            >
              {projectName}
            </a>
          )}
          {(languages || (topics && topics.length > 0) || (social && social.length > 0)) && (
            <div className="mt-4 flex flex-col gap-3 md:flex-row">
              {languages && (
                <div className="flex flex-wrap gap-2">
                  {languages.slice(0, visibleLanguages).map((topic, index) => (
                    <TopicBadge
                      key={topic || `language-${index}`}
                      topic={topic}
                      tooltipLabel={`This repository uses ${topic}`}
                      type="language"
                    />
                  ))}
                  {languages.length > 18 && (
                    <button
                      onClick={loadMoreLanguages}
                      className="text-sm text-gray-600 dark:text-gray-300"
                    >
                      {toggleLanguages ? 'Show more' : 'Show less'}
                    </button>
                  )}
                </div>
              )}
              {topics && (
                <div className="flex flex-wrap gap-2 mr-2 md:mr-0">
                  {topics
                    .slice()
                    .sort((a, b) => a.length - b.length)
                    .slice(0, visibleTopics)
                    .map((topic, index) => (
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
                      className="text-sm text-gray-600 dark:text-gray-300"
                    >
                      {toggleTopics ? 'Show more' : 'Show less'}
                    </button>
                  )}
                </div>
              )}

              {social && (
                <div className="flex gap-2">
                  {social.map((item) => (
                    <a
                      key={`${item.title}-${item.url}`}
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-center text-sm"
                    >
                      <FontAwesomeIcon icon={item.icon as FontAwesomeIconProps['icon']} />
                    </a>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
        <div className="mt-4 w-full sm:mt-0 sm:w-auto">
          <ActionButton tooltipLabel={tooltipLabel} url={button.url} onClick={button.onclick}>
            {button.icon}
            {button.label}
          </ActionButton>
        </div>
      </div>
      <Tooltip id="level-tooltip" style={tooltipStyle} />
    </div>
  )
}

export default Card
