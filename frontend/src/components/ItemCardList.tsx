import { Tooltip } from '@heroui/tooltip'
import Image from 'next/image'
import Link from 'next/link'
import React, { JSX } from 'react'
import type { IconType } from 'react-icons'
import type { Issue } from 'types/issue'
import type { Milestone } from 'types/milestone'
import type { PullRequest } from 'types/pullRequest'
import type { Release } from 'types/release'
import SecondaryCard from 'components/SecondaryCard'
import { TruncatedText } from 'components/TruncatedText'

interface BaseItem {
  objectID?: string
  repositoryName?: string
  title?: string
  name?: string
  url?: string
  author?: {
    login: string
    name?: string
    avatarUrl: string
  }
}

type RenderItem = {
  createdAt?: string
  commentsCount?: number
  organizationName?: string
  publishedAt?: string
  repositoryName?: string
  tagName?: string
  openIssuesCount?: number
  closedIssuesCount?: number
  author?: {
    avatarUrl: string
    login: string
    name?: string
  }
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
  data: (Issue | Milestone | PullRequest | Release)[]
  icon?: IconType
  showAvatar?: boolean
  showSingleColumn?: boolean
  renderDetails: (item: RenderItem) => JSX.Element
}): React.ReactNode => (
  <SecondaryCard icon={icon} title={title}>
    {data && data.length > 0 ? (
      <div
        className={`grid ${showSingleColumn ? 'grid-cols-1' : 'gap-4 gap-y-0 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3'}`}
      >
        {data.map((item, index: number) => {
          const cardItem = item as RenderItem & BaseItem
          return (
            <div
              key={
                cardItem.objectID ||
                `${cardItem.repositoryName}-${cardItem.title || cardItem.name}-${cardItem.url}`
              }
              className="mb-4 w-full rounded-lg bg-gray-200 p-4 dark:bg-gray-700"
            >
              <div className="flex w-full flex-col justify-between">
                <div className="flex w-full items-center">
                  {showAvatar && (
                    <Tooltip
                      content={cardItem?.author?.name || cardItem?.author?.login}
                      id={`avatar-tooltip-${index}`}
                      placement="bottom"
                    >
                      <Link href={`/members/${cardItem?.author?.login}`}>
                        <Image
                          height={24}
                          width={24}
                          src={cardItem?.author?.avatarUrl || ''}
                          alt="avatar"
                          className="mr-2 rounded-full"
                        />
                      </Link>
                    </Tooltip>
                  )}
                  <h3 className="min-w-0 flex-1 overflow-hidden font-semibold text-ellipsis whitespace-nowrap">
                    <Link href={cardItem?.url || ''} target="_blank">
                      <TruncatedText text={cardItem.title || cardItem.name || ''} />
                    </Link>
                  </h3>
                </div>
                <div className="ml-0.5 w-full">{renderDetails(cardItem)}</div>
              </div>
            </div>
          )
        })}
      </div>
    ) : (
      <p>Nothing to display.</p>
    )}
  </SecondaryCard>
)

export default ItemCardList
