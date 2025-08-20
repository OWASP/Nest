import { faCalendar, faFolderOpen } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { useRouter } from 'next/navigation';
import React from 'react';
import type { Issue } from 'types/issue';
import { formatDate } from 'utils/dateFormatter';
import { TruncatedText } from 'components/TruncatedText';

// Props interface
interface IssueMetadataProps {
  issue: Issue;
}

/**
 * Reusable component to display issue metadata (created date and repository link)
 */
export const IssueMetadata: React.FC<IssueMetadataProps> = ({ issue }) => {
  const router = useRouter();

  return (
    <div className="mt-2 flex flex-wrap items-center text-sm text-gray-600 dark:text-gray-400">
      {/* Created Date */}
      <div className="mr-4 flex items-center">
        <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
        <span>{formatDate(issue.createdAt)}</span>
      </div>

      {/* Repository Link */}
      {issue.repositoryName && (
        <div className="flex flex-1 items-center overflow-hidden">
          <FontAwesomeIcon icon={faFolderOpen} className="mr-2 h-5 w-4" />
          <button
            className="cursor-pointer overflow-hidden text-ellipsis whitespace-nowrap text-gray-600 hover:underline dark:text-gray-400"
            onClick={() =>
              router.push(
                `/organizations/${issue.organizationName}/repositories/${issue.repositoryName}`
              )
            }
          >
            <TruncatedText text={issue.repositoryName} />
          </button>
        </div>
      )}
    </div>
  );
};

export default IssueMetadata;