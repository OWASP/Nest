import { faCalendarAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Issue } from "types/user";

export function IssueCard({ issue }: { issue: Issue }) {
  return (
    <div
      className="p-4 border border-gray-300 rounded-lg transition-colors cursor-pointer hover:bg-gray-100 dark:border-gray-700 dark:hover:bg-gray-800"
    >
      <div className="flex justify-between">
        <div>
          <a
            href={`https://github.com/${issue.repository.owner_key}/${issue.repository.key}/issues/${issue.number}`}
            target="_blank"
            rel="noopener noreferrer"
            className="font-bold text-black underline decoration-dotted dark:text-white"
          >
            {issue.title}
          </a>
          <div className="flex items-center gap-2 mt-1 text-gray-600 dark:text-gray-400">
            <span className="px-2 py-1 text-sm bg-gray-200 rounded-full dark:bg-gray-700">
              #{issue.number}
            </span>
            <span>•</span>
            <a
              href={`https://github.com/${issue.repository.owner_key}/${issue.repository.key}`}
              target="_blank"
              rel="noopener noreferrer"
              className="underline decoration-dotted dark:text-gray-300"
            >
              {issue.repository.owner_key}/{issue.repository.key}
            </a>
          </div>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          <FontAwesomeIcon icon={faCalendarAlt} className="w-4 h-4" />
          {new Date(issue.created_at * 1000).toLocaleDateString()}
        </div>
      </div>
    </div>
  );
}
