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
          <div key={index} className="mb-4 rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
            <h3 className="font-semibold">
              <a href={item?.url} className="text-blue-400 hover:underline">
                {item.title || item.name}
              </a>
            </h3>
            <div className="mt-2 flex items-center">
              <img
                src={item?.author?.avatarUrl}
                alt={item?.author?.name}
                className="mr-2 h-6 w-6 rounded-full"
              />
              <a href={item?.author?.url} className="text-blue-200 hover:underline">
                {item?.author?.name || item?.author?.login}
              </a>
            </div>
            {renderDetails(item)}
          </div>
        ))}
      </div>
    ) : (
      <p>No {title.toLowerCase()}.</p>
    )}
  </SecondaryCard>
)

export default ItemCardList
