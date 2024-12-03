import { cn } from '../lib/utils'
import { CardProps } from '../lib/constants'
import ContributorAvatar from './ContributorAvatar'
import TopicBadge from './TopicBadge'
import ActionButton from './ActionButton'
import { Icons } from './data'
import DisplayIcon from './DisplayIcon'
import { Tooltip } from 'react-tooltip'
import { tooltipStyle } from '../lib/constants'
import { FontAwesomeIcon, FontAwesomeIconProps } from '@fortawesome/react-fontawesome'
import FontAwesomeIconWrapper from '../lib/FontAwesomeIconWrapper'

const Card = ({
  title,
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
}: CardProps) => {
  return (
    <div className=" w-full md:max-w-6xl  h-fit flex flex-col justify-normal items-start gap-4 md:gap-2 p-4 px-6 border border-border rounded-md ">
      <div className=" w-full flex justify-between items-center flex-wrap gap-2 ">
        <div className=" flex justify-center items-center gap-2 ">
          {level && (
            <span
              data-tooltip-id="level-tooltip"
              data-tooltip-content={`${level.level} project`}
              className={cn(
                'text-xs rounded-full w-8 h-8 flex justify-center items-center shadow '
              )}
              style={{ backgroundColor: level.color }}
            >
              <FontAwesomeIconWrapper icon={level.icon} className="text-white" />
            </span>
          )}
          <a href="#">
            <h1 className=" text-2xl font-semibold ">{title}</h1>
          </a>
        </div>

        <div className="min-w-[30%] flex justify-end items-center md:gap-8 flex-wrap ">
          {icons &&
            Object.keys(Icons).map((key) =>
              icons[key] !== undefined ? <DisplayIcon key={key} item={key} icons={icons} /> : null
            )}
        </div>
      </div>
      <h2>
        {leaders && (
          <span className=" font-bold "> {leaders.length > 1 ? 'Leaders: ' : 'Leader: '} </span>
        )}
        {leaders &&
          leaders.map((leader, index) => (
            <span key={leader} className=" font-semibold ">
              {' '}
              {index != leaders.length - 1 ? `${leader},` : `${leader}`}{' '}
            </span>
          ))}
      </h2>
      <div className=" w-full flex justify-normal items-center gap-1 ">
        {topContributors &&
          topContributors.map((contributor) => (
            <ContributorAvatar key={contributor.login} contributor={contributor} />
          ))}
      </div>
      {projectName && (
        <a href={projectLink} target="_blank" rel="noopener noreferrer">
          {' '}
          {projectName}
        </a>
      )}
      <p className=" mr-8 text-gray-600 dark:text-gray-200 ">{summary}</p>
      <div className=" w-full flex md:flex-row flex-col justify-between items-center ">
        <div className=" flex flex-col justify-normal items-start gap-2 ">
          <div className=" flex justify-normal items-center gap-2 ">
            {languages &&
              languages.map((topic) => (
                <TopicBadge
                  key={topic}
                  topic={topic}
                  tooltipLabel={`This repository uses ${topic}`}
                />
              ))}
          </div>
          <div className=" flex justify-normal items-center gap-2 flex-wrap ">
            {topics &&
              topics.map((topic) => (
                <TopicBadge
                  key={topic}
                  topic={topic}
                  tooltipLabel={`This project is labeled as ${topic}`}
                />
              ))}
          </div>
          <div className=" flex justify-normal items-center gap-2 my-2 ">
            {social &&
              social.map((item) => (
                <a
                  key={item.title}
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className=" flex justify-center items-center gap-1 "
                >
                  {/* {item.icon} */}
                  <FontAwesomeIcon icon={item.icon as FontAwesomeIconProps['icon']} />
                </a>
              ))}
          </div>
        </div>
        <ActionButton link={button.link} onClick={button.onclick}>
          {button.icon}
          {button.label}
        </ActionButton>
      </div>
      <Tooltip id="level-tooltip" style={tooltipStyle} />
    </div>
  )
}

export default Card
