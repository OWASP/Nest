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
          <div key={index} className="mb-4  rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
            <h3 className="font-semibold text-ellipsis overflow-hidden whitespace-nowrap">{item.title || item.name}</h3>
            <div className='flex flex-grow-0 flex-col lg:flex-row justify-between'>
              <div className="mt-2 flex items-center">
                {item?.author?.name && <img
                  src={item?.author?.avatarUrl}
                  alt={item?.author?.name}
                  className="mr-2 h-6 w-6 rounded-full"
                />}
                <span>{item?.author?.name || item?.author?.login}</span>
              </div>
               <div>{renderDetails(item)}</div>
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
