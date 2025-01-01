import { FontAwesomeIcon, FontAwesomeIconProps } from '@fortawesome/react-fontawesome';
import { useState, useEffect } from 'react';
import { Tooltip } from 'react-tooltip';
import { CardProps, tooltipStyle } from 'lib/constants';
import FontAwesomeIconWrapper from 'lib/FontAwesomeIconWrapper';
import { cn } from 'lib/utils';
import ActionButton from 'components/ActionButton';
import ContributorAvatar from 'components/ContributorAvatar';
import { Icons } from 'components/data';
import DisplayIcon from 'components/DisplayIcon';
import Markdown from 'components/MarkdownWrapper';
import TopicBadge from 'components/TopicBadge';

// Initial check for mobile screen size
const isMobileInitial = typeof window !== 'undefined' && window.innerWidth < 768;

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
  const [visibleLanguages, setVisibleLanguages] = useState(isMobileInitial ? 4 : 18);
  const [visibleTopics, setVisibleTopics] = useState(isMobileInitial ? 4 : 18);
  const [toggleLanguages, setToggleLanguages] = useState(false);
  const [toggleTopics, setToggleTopics] = useState(false);
  const [isMobile, setIsMobile] = useState(isMobileInitial);

  // Resize listener to adjust display based on screen width
  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      setVisibleLanguages(mobile ? 4 : 18);
      setVisibleTopics(mobile ? 4 : 18);
    };
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const loadMoreLanguages = () => {
    setVisibleLanguages(toggleLanguages ? (isMobile ? 4 : 18) : languages?.length || 0);
    setToggleLanguages(!toggleLanguages);
  };

  const loadMoreTopics = () => {
    setVisibleTopics(toggleTopics ? (isMobile ? 4 : 18) : topics?.length || 0);
    setToggleTopics(!toggleTopics);
  };

  return (
    <div className="mt-4 w-full flex flex-col items-start rounded-md border border-border bg-white mb-2 pl-4 pb-4 transition-colors duration-300 ease-linear md:max-w-6xl dark:bg-[#212529]">
      <div className="flex flex-col sm:flex-row w-full items-start sm:items-center gap-4 sm:gap-6 pt-2 md:pt-0">
        <div className="flex gap-3 items-center">
          {/* Display project level badge (if available) */}
          {level && (
            <span
              data-tooltip-id="level-tooltip"
              data-tooltip-content={`${level.level} project`}
              className={cn(
                'flex h-8 w-8 items-center justify-center rounded-full text-xs shadow'
              )}
              style={{ backgroundColor: level.color }}
            >
              <FontAwesomeIconWrapper icon={level.icon} className="text-white" />
            </span>
          )}
          {/* Project title and link */}
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1"
          >
            <h1 className="text-base font-semibold sm:text-lg lg:text-2xl dark:text-sky-600 break-words sm:break-normal max-w-full">
              {title}
            </h1>
          </a>
        </div>
        {/* Icons associated with the project */}
        <div className="flex flex-row items-center justify-end flex-grow overflow-auto min-w-[30%]">
          {icons &&
            Object.keys(Icons).map((key, index) =>
              icons[key] !== undefined ? (
                <DisplayIcon
                  key={`${key}-${index}`}
                  item={key}
                  icons={icons}
                  idx={Object.keys(icons).findIndex((e) => e === key) === Object.keys(icons).length - 1 ? -1 : Object.keys(icons).findIndex((e) => e === key)}
                />
              ) : null
            )}
        </div>
      </div>
      {/* Link to project name if provided */}
      {projectName && (
        <a href={projectLink} target="_blank" rel="noopener noreferrer" className="font-medium mt-2">
          {projectName}
        </a>
      )}
      {/* Render project summary using Markdown */}
      <Markdown content={summary} className="py-2 text-gray-600 dark:text-gray-300 pr-4" />
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
      <div className="flex flex-col gap-4 w-full pr-4">
        {/* Render top contributors as avatars */}
        <div className="w-full flex flex-wrap items-center gap-2">
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
          <div className={cn(
            'flex flex-wrap items-center gap-4',
            isMobile && (toggleLanguages || toggleTopics) && 'w-full'
          )}>
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
                    className="text-gray-600 dark:text-gray-300 mt-2"
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
                    className="text-gray-600 dark:text-gray-300 mt-2"
                  >
                    {toggleTopics ? 'Show less' : 'Show more'}
                  </button>
                )}
              </div>
            )}
            {/* Render social links if available */}
            {social && social.length > 0 && (
              <div id="social" className="flex items-center gap-3 mt-2">
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
          <div className={cn(
            'flex items-center',
            isMobile && (toggleLanguages || toggleTopics) && 'w-full justify-end mt-4'
          )}>
            <ActionButton tooltipLabel={tooltipLabel} url={button.url} onClick={button.onclick}>
              {button.icon}
              {button.label}
            </ActionButton>
          </div>
        </div>
      </div>
      <Tooltip id="level-tooltip" style={tooltipStyle} />
    </div>
  );
};

export default Card;
