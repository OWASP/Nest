import { faCalendarAlt } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Issue } from 'types/user'

export function IssueCard({ issue }: { issue: Issue }) {
  return (
    <div className="cursor-pointer rounded-lg border border-gray-300 p-4 transition-colors hover:bg-gray-100 dark:border-gray-700 dark:hover:bg-gray-800">
      <div className="flex justify-between">
        <div>
          <a
            href={`https://github.com/${issue.repository.ownerKey}/${issue.repository.key}/issues/${issue.number}`}
            target="_blank"
            rel="noopener noreferrer"
            className="font-bold text-black underline decoration-dotted dark:text-white hover:cursor-pointer"
          >
            {issue.title}
          </a>

          <div className="mt-1 flex items-center gap-2 text-gray-600 dark:text-gray-400">
            <span className="rounded-full bg-gray-200 px-2 py-1 text-sm dark:bg-gray-700">
              #{issue.number}
            </span>
            <span>•</span>
            <a
              href={`https://github.com/${issue.repository.ownerKey}/${issue.repository.key}`}
              target="_blank"
              rel="noopener noreferrer"
              className="underline decoration-dotted dark:text-gray-300"
            >
              {issue.repository.ownerKey}/{issue.repository.key}
            </a>
          </div>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          <FontAwesomeIcon icon={faCalendarAlt} className="h-4 w-4" />
          {new Date(issue.createdAt * 1000).toLocaleDateString()}
        </div>
      </div>
    </div>
  )
}
