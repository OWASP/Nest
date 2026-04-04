import React from 'react';

export interface Contributor {
  id: string | number;
  login: string;
  avatar_url: string;
  html_url: string;
  name?: string;
}

export interface ContributorListProps {
  projectId: string | number;
  contributors: Contributor[];
}

const ContributorList: React.FC<ContributorListProps> = ({ projectId, contributors }) => {
  if (!contributors || contributors.length === 0) {
    return null;
  }

  return (
    <ul className="flex flex-wrap items-center gap-2 m-0 p-0 list-none">
      {contributors.map((contributor, index) => {
        // Fix for Issue #1065: Tooltip Collision for Contributors Across Multiple Projects
        // Strategy: Extend the unique key for contributor tooltips to include the project identifier
        const tooltipId = `tooltip-${projectId}-contributor-${contributor.id}-${index}`;
        const displayName = contributor.name || contributor.login;

        return (
          <li key={tooltipId} className="relative group">
            <a
              href={contributor.html_url}
              target="_blank"
              rel="noopener noreferrer"
              className="block focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-full"
              data-tooltip-id={tooltipId}
              aria-describedby={tooltipId}
            >
              <img
                src={contributor.avatar_url}
                alt={`${displayName}'s avatar`}
                className="w-8 h-8 rounded-full border border-gray-200 object-cover hover:border-blue-500 transition-colors"
                loading="lazy"
              />
            </a>
            {/* Tooltip element */}
            <div
              id={tooltipId}
              role="tooltip"
              className="invisible opacity-0 group-hover:visible group-hover:opacity-100 group-focus-within:visible group-focus-within:opacity-100 transition-opacity absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-800 text-white text-xs rounded whitespace-nowrap z-50 pointer-events-none"
            >
              {displayName}
              {/* Tooltip arrow */}
              <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-gray-800"></div>
            </div>
          </li>
        );
      })}
    </ul>
  );
};

export default ContributorList;