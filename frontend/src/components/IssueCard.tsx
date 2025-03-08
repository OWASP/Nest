import { faCalendarAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Issue } from "types/user";

export function IssueCard({ issue }: { issue: Issue }) {
  const issueUrl = `https://github.com/${issue.repository.ownerKey}/${issue.repository.key}/issues/${issue.number}`;
  const repoUrl = `https://github.com/${issue.repository.ownerKey}/${issue.repository.key}`;
  const formattedDate = issue.createdAt
    ? new Date(issue.createdAt * 1000).toLocaleDateString()
    : "Unknown date";

  return (
    <div className="cursor-pointer rounded-lg border border-gray-300 p-4 transition-all duration-200 hover:bg-gray-100 dark:border-gray-700 dark:hover:bg-gray-800">
      <div className="flex justify-between items-start">
        {/* Issue Title & Repo Link */}
        <div>
          <a
            href={issueUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="font-bold text-black underline decoration-dotted hover:text-blue-600 dark:text-white dark:hover:text-sky-400"
            title="View issue on GitHub"
            aria-label={`View issue: ${issue.title}`}
          >
            {issue.title}
          </a>

          {/* Issue Number & Repository Info */}
          <div className="mt-1 flex items-center gap-2 text-gray-600 dark:text-gray-400 text-sm">
            <span className="rounded-full bg-gray-200 px-2 py-1 dark:bg-gray-700">
              #{issue.number}
            </span>
            <span>•</span>
            <a
              href={repoUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="underline decoration-dotted hover:text-blue-600 dark:text-gray-300 dark:hover:text-sky-400"
              title="View repository on GitHub"
              aria-label={`View repository: ${issue.repository.ownerKey}/${issue.repository.key}`}
            >
              {issue.repository.ownerKey}/{issue.repository.key}
            </a>
          </div>
        </div>

        {/* Issue Creation Date */}
        <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          <FontAwesomeIcon icon={faCalendarAlt} className="h-4 w-4" />
          <span title="Issue created date">{formattedDate}</span>
        </div>
      </div>
    </div>
  );
}
