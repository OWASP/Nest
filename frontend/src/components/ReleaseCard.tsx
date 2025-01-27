import { faCalendarAlt, faTag } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { Release } from 'types/user';

export function ReleaseCard({ release }: { release: Release }) {
  return (
    <div className="p-4 hover:bg-gray-50 transition-colors dark:hover:bg-gray-700/50 border border-gray-200 dark:border-gray-600 rounded-lg">
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1">
          <a
            href={`https://github.com/${release.repository.owner_key}/${release.repository.key}/releases/tag/${release.tag_name}`}
            className="font-medium hover:underline decoration-dotted underline-offset-2 text-gray-900 dark:text-white"
            target="_blank"
            rel="noopener noreferrer"
          >
            {release.name || release.tag_name}
          </a>
          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
            <FontAwesomeIcon icon={faTag} className="w-4 h-4" />
            {release.tag_name}
            {release.is_pre_release && (
              <>
                <span>•</span>
                <span className="bg-gray-200 dark:bg-gray-600 text-sm px-2 py-1 rounded-full text-gray-800 dark:text-gray-300">
                  Pre-release
                </span>
              </>
            )}
          </div>
          <a
            href={`https://github.com/${release.repository.owner_key}/${release.repository.key}`}
            className="text-sm text-gray-600 dark:text-gray-400 hover:underline decoration-dotted underline-offset-2 mt-2"
            target="_blank"
            rel="noopener noreferrer"
          >
            {release.repository.owner_key}/{release.repository.key}
          </a>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 whitespace-nowrap">
          <FontAwesomeIcon icon={faCalendarAlt} className="w-4 h-4" />
          {new Date(release.published_at * 1000).toLocaleDateString()}
        </div>
      </div>
    </div>
  );
}
