import { faCalendarAlt, faTag } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Release } from 'types/user'

export function ReleaseCard({ release }: { release: Release }) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 transition-colors hover:bg-gray-50 dark:border-gray-600 dark:hover:bg-gray-700/50">
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1">
          <a
            href={`https://github.com/${release.repository.ownerKey}/${release.repository.key}/releases/tag/${release.tagName}`}
            className="font-medium text-gray-900 decoration-dotted underline-offset-2 hover:underline dark:text-white"
            target="_blank"
            rel="noopener noreferrer"
          >
            {release.name || release.tagName}
          </a>
          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
            <FontAwesomeIcon icon={faTag} className="h-4 w-4" />
            {release.tagName}
            {release.isPreRelease && (
              <>
                <span>•</span>
                <span className="rounded-full bg-gray-200 px-2 py-1 text-sm text-gray-800 dark:bg-gray-600 dark:text-gray-300">
                  Pre-release
                </span>
              </>
            )}
          </div>
          <a
            href={`https://github.com/${release.repository.ownerKey}/${release.repository.key}`}
            className="mt-2 text-sm text-gray-600 decoration-dotted underline-offset-2 hover:underline dark:text-gray-400"
            target="_blank"
            rel="noopener noreferrer"
          >
            {release.repository.ownerKey}/{release.repository.key}
          </a>
        </div>
        <div className="flex items-center gap-2 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
          <FontAwesomeIcon icon={faCalendarAlt} className="h-4 w-4" />
          {new Date(release.publishedAt * 1000).toLocaleDateString()}
        </div>
      </div>
    </div>
  )
}
