import { Tooltip } from '@heroui/tooltip'
import Image from 'next/image'
import Link from 'next/link'
import React, { JSX } from 'react'
import type { IconType } from 'react-icons'
import { FaUser } from 'react-icons/fa'
import type { Issue } from 'types/issue'
import type { Milestone } from 'types/milestone'
import type { PullRequest } from 'types/pullRequest'
import type { Release } from 'types/release'
import SecondaryCard from 'components/SecondaryCard'
import { TruncatedText } from 'components/TruncatedText'

interface AuthorAvatarProps {
  author: {
    avatarUrl: string
    login: string
    name: string
  }
}

const AuthorAvatar = ({ author }: AuthorAvatarProps): JSX.Element => {
  const hasAuthorInfo = author?.name || author?.login
  const hasLogin = author?.login
  const hasAvatarUrl = Boolean(author?.avatarUrl)

  const fallbackAvatar = (
    <div className="mr-2 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-gray-300 dark:bg-gray-600">
      <FaUser className="h-4 w-4 text-gray-400" />
    </div>
  )

  if (hasAuthorInfo) {
    const avatarContent = hasAvatarUrl ? (
      <Image
        height={24}
        width={24}
        src={author.avatarUrl}
        alt={`${author.name || author.login}'s avatar`}
        className="mr-2 rounded-full"
      />
    ) : (
      fallbackAvatar
    )

    if (hasLogin) {
      return (
        <Link className="shrink-0 text-blue-400 hover:underline" href={`/members/${author.login}`}>
          {avatarContent}
        </Link>
      )
    }
    return <div className="shrink-0">{avatarContent}</div>
  }

  return <div className="shrink-0">{fallbackAvatar}</div>
}

const ItemCardList = ({
  title,
  data,
  icon,
  renderDetails,
  showAvatar = true,
  showSingleColumn = true,
}: {
  title: React.ReactNode
  data: Issue[] | Milestone[] | PullRequest[] | Release[]
  icon?: IconType
  showAvatar?: boolean
  showSingleColumn?: boolean
  renderDetails: (item: {
    createdAt: number
    commentsCount: number
    organizationName: string
    publishedAt: number
    repositoryName: string
    tagName: string
    openIssuesCount: number
    closedIssuesCount: number
    author: {
      avatarUrl: string
      login: string
      name: string
    }
  }) => JSX.Element
}) => (
  <SecondaryCard icon={icon} title={title}>
    {data && data.length > 0 ? (
      <div
        className={`grid ${showSingleColumn ? 'grid-cols-1' : 'gap-4 gap-y-0 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3'}`}
      >
        {data.map((item, index) => (
          <div
            key={item.objectID || `${item.repositoryName}-${item.title || item.name}-${item.url}`}
            className="mb-4 w-full rounded-lg bg-gray-200 p-4 dark:bg-gray-700"
          >
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
                    <AuthorAvatar author={item.author} />
                  </Tooltip>
                )}
                <h3 className="min-w-0 flex-1 overflow-hidden font-semibold text-ellipsis whitespace-nowrap">
                  <Link
                    className="text-blue-400 hover:underline"
                    href={item?.url || ''}
                    rel="noopener noreferrer"
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
      <p>Nothing to display.</p>
    )}
  </SecondaryCard>
)

export default ItemCardList
