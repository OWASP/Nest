import { IconProp } from '@fortawesome/fontawesome-svg-core'
import { Tooltip } from '@heroui/tooltip'
import Image from 'next/image'
import Link from 'next/link'
import { JSX } from 'react'
import { ProjectIssuesType, ProjectReleaseType } from 'types/project'
import { PullRequestsType } from 'types/user'
import SecondaryCard from './SecondaryCard'
import { TruncatedText } from './TruncatedText'

const ItemCardList = ({
  title,
  data,
  icon,
  renderDetails,
  showAvatar = true,
}: {
  title: string
  data: ProjectReleaseType[] | ProjectIssuesType[] | PullRequestsType[]
  icon?: IconProp
  showAvatar?: boolean
  renderDetails: (item: {
    createdAt: string
    commentsCount: number
    publishedAt: string
    repositoryName: string
    tagName: string
    author: {
      avatarUrl: string
      login: string
      name: string
    }
  }) => JSX.Element
}) => (
  <SecondaryCard icon={icon} title={title}>
    {data && data.length > 0 ? (
      <div className="overflow-y-auto pr-2">
        {data.map((item, index) => (
          <div key={index} className="mb-4 w-full rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
            <div className="flex w-full flex-col justify-between">
              <div className="flex w-full items-center">
                {showAvatar && (
                  <Tooltip
                    closeDelay={100}
                    content={item?.author?.name || item?.author?.login}
                    id={`avatar-tooltip-${index}`}
                    delay={100}
                    placement="bottom"
                    showArrow
                  >
                    <Link
                      className="flex-shrink-0 text-blue-400 hover:underline"
                      href={`/members/${item?.author?.login}`}
                    >
                      <Image
                        height={24}
                        width={24}
                        src={item?.author?.avatarUrl}
                        alt={item?.author?.name || ''}
                        className="mr-2 rounded-full"
                      />
                    </Link>
                  </Tooltip>
                )}
                <h3 className="flex-1 overflow-hidden text-ellipsis whitespace-nowrap font-semibold">
                  <Link
                    className="text-blue-400 hover:underline"
                    href={item?.url || ''}
                    target="_blank"
                  >
                    <TruncatedText text={item.title || item.name} />
                  </Link>
                </h3>
              </div>
              <div className="ml-0.5 w-full">{renderDetails(item)}</div>
            </div>
          </div>
        ))}
      </div>
    ) : (
      <p>No {title.toLowerCase()}.</p>
    )}
  </SecondaryCard>
)

export default ItemCardList
