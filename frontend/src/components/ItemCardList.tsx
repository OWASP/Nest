import { JSX } from 'react'
import { ProjectIssuesType, ProjectReleaseType } from 'types/project'
import SecondaryCard from './SecondaryCard'

const ItemCardList = ({
  title,
  data,
  renderDetails,
}: {
  title: string
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
          <div key={index} className="mb-4 w-full rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
            <div className="flex w-full flex-col justify-between">
              <div className="flex w-full items-center">
                <a
                  href={`/community/users/${item?.author?.login}`}
                  className="flex-shrink-0 text-blue-400 hover:underline dark:text-blue-200"
                >
                  <img
                    src={item?.author?.avatarUrl}
                    alt={item?.author?.name}
                    className="mr-2 h-6 w-6 rounded-full"
                  />
                </a>
                <h3 className="flex-1 overflow-hidden text-ellipsis whitespace-nowrap font-semibold">
                  <a href={item?.url} className="text-blue-500 hover:underline dark:text-blue-400">
                    {item.title || item.name}
                  </a>
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
