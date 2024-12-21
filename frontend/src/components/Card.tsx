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
import Markdown from './Markdown'

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
    <div className="flex h-fit w-full flex-col items-start justify-normal gap-4 rounded-md border border-border py-6 pl-6 pt-0 md:max-w-6xl md:gap-2">
      <div className="flex w-full flex-wrap items-center justify-between gap-2">
        <div className="mt-4 flex items-center justify-center gap-2">
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
          <a href={url} target="_blank" rel="noopener noreferrer">
            <h1 className="text-2xl font-semibold dark:text-sky-600">{title}</h1>
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
      <p className="mr-8 mt-2 text-gray-600 dark:text-gray-300">
        <Markdown>{summary}</Markdown>
      </p>
      <h2>
        {leaders && (
          <span className="font-semibold text-gray-600 dark:text-gray-300">
            {leaders.length > 1 ? 'Leaders: ' : 'Leader: '}
          </span>
        )}
        {leaders &&
          leaders.map((leader, index) => (
            <span key={`${leader}-${index}`} className="text-gray-600 dark:text-gray-300">
              {index !== leaders.length - 1 ? `${leader}, ` : `${leader}`}
            </span>
          ))}
      </h2>
      <div className="flex w-full justify-between">
        <div className="align-content-center flex-auto justify-normal">
          <div className="flex w-full items-center justify-normal gap-1 pr-6">
            {topContributors &&
              topContributors.map((contributor, index) => (
                <ContributorAvatar
                  key={contributor.login || `contributor-${index}`}
                  contributor={contributor}
                />
              ))}
          </div>
          {projectName && (
            <a href={projectLink} target="_blank" rel="noopener noreferrer" className="font-bold">
              {projectName}
            </a>
          )}
          {(languages || (topics && topics.length > 0) || (social && social.length > 0)) && (
            <div className="flex w-full flex-col items-center justify-between pr-6 md:flex-row">
              <div className="flex max-w-4xl items-start justify-start pt-3">
                {languages && (
                  <div id="languages" className="flex flex-wrap items-center justify-normal gap-2">
                    {languages &&
                      languages
                        .slice(0, visibleLanguages)
                        .map((topic, index) => (
                          <TopicBadge
                            key={topic || `language-${index}`}
                            topic={topic}
                            tooltipLabel={`This repository uses ${topic}`}
                            type="language"
                          />
                        ))}
                    {languages && languages.length > 18 && (
                      <button
                        onClick={loadMoreLanguages}
                        className="text-gray-600 dark:text-gray-300"
                      >
                        {toggleLanguages ? 'Show more' : 'Show less'}
                      </button>
                    )}
                  </div>
                )}
                {topics && topics.length > 0 && (
                  <div id="topics" className="flex flex-wrap items-center justify-normal gap-2">
                    {topics &&
                      topics
                        .slice(0, visibleTopics)
                        .map((topic, index) => (
                          <TopicBadge
                            key={topic || `topic-${index}`}
                            topic={topic}
                            tooltipLabel={`This project is labeled as "${topic}"`}
                            type="topic"
                          />
                        ))}

                    {topics && topics.length > 18 && (
                      <button onClick={loadMoreTopics} className="text-gray-600 dark:text-gray-300">
                        {toggleTopics ? 'Show more' : 'Show less'}
                      </button>
                    )}
                  </div>
                )}
                {social && social.length > 0 && (
                  <div id="social" className="flex items-center justify-normal gap-2">
                    {social &&
                      social.map((item) => (
                        <a
                          key={`${item.title}-${item.url}`}
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center justify-center gap-1"
                        >
                          <FontAwesomeIcon icon={item.icon as FontAwesomeIconProps['icon']} />
                        </a>
                      ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
        <div className="w-38 content-end justify-items-center pr-6">
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
