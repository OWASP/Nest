import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faCode, faTag } from '@fortawesome/free-solid-svg-icons'
import { Tooltip } from '@heroui/tooltip'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import type { CardProps } from 'types/card'
import { Icons } from 'utils/data'
import { getSocialIcon } from 'utils/urlIconMappings'
import ActionButton from 'components/ActionButton'
import ContributorAvatar from 'components/ContributorAvatar'
import DisplayIcon from 'components/DisplayIcon'
import Markdown from 'components/MarkdownWrapper'

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
  labels,
  languages,
}: CardProps) => {
  const router = useRouter()
  const [showAllLabels, setShowAllLabels] = useState(false)
  const [showAllLanguages, setShowAllLanguages] = useState(false)

  const handleLabelClick = (label: string) => {
    router.push(`/contribute?q=${encodeURIComponent(label)}`)
  }

  const handleLanguageClick = (language: string) => {
    router.push(`/contribute?q=${encodeURIComponent(language)}`)
  }

  return (
    <div className="mx-auto mb-2 mt-4 flex w-full max-w-[95%] flex-col items-start rounded-md border border-border bg-white p-4 dark:bg-[#212529] md:max-w-6xl">
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
                <FontAwesomeIconWrapper icon={level.icon} className="text-white" />
              </span>
            </Tooltip>
          )}
          {/* Project title and link */}
          <Link href={url} target="_blank" rel="noopener noreferrer" className="flex-1">
            <h1
              className="max-w-full break-words text-base font-semibold text-blue-400 hover:text-blue-600 sm:break-normal sm:text-lg lg:text-2xl"
              style={{
                transition: 'color 0.3s ease',
              }}
            >
              {title}
            </h1>
          </Link>
        </div>

        {/* Icons associated with the project */}
        {icons && Object.keys(Icons).some((key) => icons[key as keyof typeof icons]) && (
          <div className="mt-3 flex flex-wrap">
            {Object.keys(Icons).map((key, index) => {
              const iconKey = key as keyof typeof icons;
              return icons[iconKey] ? (
                <DisplayIcon
                  key={`${key}-${index}`}
                  item={key}
                  icons={Object.fromEntries(
                    Object.entries(icons).filter(([_, value]) => Boolean(value))
                  )}
                />
              ) : null;
            })}
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

      {/* Labels */}
      {labels && labels.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-2">
          {(showAllLabels ? labels : labels.slice(0, 3)).map((label, index) => (
            <button
              key={index}
              onClick={() => handleLabelClick(label)}
              className="inline-flex items-center rounded-lg border border-gray-300 bg-gray-50 px-3 py-1 text-sm transition-all duration-200 ease-in-out hover:scale-105 hover:bg-gray-100 dark:border-gray-600 dark:bg-gray-800 dark:hover:bg-gray-700"
            >
              <FontAwesomeIcon icon={faTag} className="mr-1 h-3 w-3" />
              {label}
            </button>
          ))}
          {labels.length > 3 && (
            <button
              onClick={() => setShowAllLabels(!showAllLabels)}
              className="inline-flex items-center rounded-lg border border-gray-300 bg-gray-50 px-3 py-1 text-sm text-gray-600 transition-all duration-200 ease-in-out hover:bg-gray-100 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700"
            >
              {showAllLabels ? 'Show less' : `+${labels.length - 3} more`}
            </button>
          )}
        </div>
      )}

      {/* Programming Languages */}
      {languages && languages.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-2">
          {(showAllLanguages ? languages : languages.slice(0, 3)).map((language, index) => (
            <button
              key={index}
              onClick={() => handleLanguageClick(language)}
              className="inline-flex items-center rounded-lg border border-blue-300 bg-blue-50 px-3 py-1 text-sm text-blue-700 transition-all duration-200 ease-in-out hover:scale-105 hover:bg-blue-100 dark:border-blue-600 dark:bg-blue-900/30 dark:text-blue-300 dark:hover:bg-blue-800/40"
            >
              <FontAwesomeIcon icon={faCode} className="mr-1 h-3 w-3" />
              {language}
            </button>
          ))}
          {languages.length > 3 && (
            <button
              onClick={() => setShowAllLanguages(!showAllLanguages)}
              className="inline-flex items-center rounded-lg border border-blue-300 bg-blue-50 px-3 py-1 text-sm text-blue-600 transition-all duration-200 ease-in-out hover:bg-blue-100 dark:border-blue-600 dark:bg-blue-900/30 dark:text-blue-400 dark:hover:bg-blue-800/40"
            >
              {showAllLanguages ? 'Show less' : `+${languages.length - 3} more`}
            </button>
          )}
        </div>
      )}

      {/* Project summary */}
      <Markdown content={summary} className="mt-2 w-full text-gray-600 dark:text-gray-300" />

      {/* Bottom section with social links, contributors and action button */}
      <div className="mt-4 w-full">
        {/* Social icons section */}
        {social && social.length > 0 && (
          <div className="mb-3 flex">
            <div className="flex flex-wrap gap-3">
              {social.map((item) => (
                <Link
                  key={`${item.title}-${item.url}`}
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="transition-colors"
                >
                  <FontAwesomeIcon
                    icon={getSocialIcon(item.url)}
                    className="h-5 w-5 text-blue-500 hover:text-gray-600 dark:hover:dark:text-gray-400"
                  />
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Flexible bottom row with contributors and action button */}
        <div className="flex w-full flex-col space-y-3 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
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
            <ActionButton tooltipLabel={tooltipLabel} url={button.url} onClick={button.onclick}>
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
