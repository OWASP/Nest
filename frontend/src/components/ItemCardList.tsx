import { JSX } from 'react'
import React from 'react'
import { ProjectIssuesType, ProjectReleaseType } from 'types/project'
import SecondaryCard from './SecondaryCard'

const ItemCardList = ({
  title,
  data,
  renderDetails,
}: {
  title: React.ReactNode
  data: ProjectReleaseType[] | ProjectIssuesType[]
  renderDetails: (item: {
    createdAt: string
    commentsCount: number
    publishedAt: string
    tagName: string
  }) => JSX.Element
}) => (
  <SecondaryCard title={title}>
    {data && data.length > 0 ? (
      <div className="h-64 overflow-y-auto pr-2">
        {data.map((item, index) => (
          <div key={index} className="mb-4 rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
            <h3 className="overflow-hidden text-ellipsis whitespace-nowrap font-semibold">
              <a href={item?.url} className="text-blue-500 hover:underline dark:text-blue-400">
                {item.title || item.name}
              </a>
            </h3>
            <div className="flex flex-grow-0 flex-col justify-between lg:flex-row">
              <div className="mt-2 flex items-center">
                <div className="flex items-center">
                  <img
                    src={item?.author?.avatarUrl}
                    alt={item?.author?.name}
                    className="mr-2 h-6 w-6 rounded-full"
                  />
                  <a
                    href={item?.author?.url}
                    className="text-blue-400 hover:underline dark:text-blue-200"
                  >
                    {item?.author?.name || item?.author?.login}
                  </a>
                </div>
              </div>
              <div>{renderDetails(item)}</div>
            </div>
          </div>
        ))}
      </div>
    ) : (
      <p>Currently , Nothing to Display . </p>
    )}
  </SecondaryCard>
)

export default ItemCardList
