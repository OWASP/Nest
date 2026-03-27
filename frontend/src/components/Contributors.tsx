import React from 'react';

export interface Contributor {
  id?: string | number;
  login: string;
  name?: string;
  avatar_url: string;
  html_url: string;
  contributions?: number;
}

export interface ContributorsProps {
  contributors: Contributor[];
  projectId: string | number;
}

export const Contributors: React.FC<ContributorsProps> = ({ contributors, projectId }) => {
  if (!contributors || contributors.length === 0) {
    return null;
  }

  return (
    <div className="flex -space-x-2 overflow-visible py-1">
      {contributors.map((contributor, index) => {
        // Strategy: Append the project ID to the unique key used for contributor tooltips 
        // to prevent collisions across multiple project cards on the same page.
        const uniqueKey = `contributor-${projectId}-${contributor.id || contributor.login}-${index}`;
        const tooltipId = `tooltip-${uniqueKey}`;
        const displayName = contributor.name || contributor.login;

        return (
          <div key={uniqueKey} className="relative group inline-block">
            <a
              href={contributor.html_url}
              target="_blank"
              rel="noopener noreferrer"
              aria-describedby={tooltipId}
              data-tooltip-id={tooltipId}
              data-tooltip-content={displayName}
              className="inline-block rounded-full ring-2 ring-white dark:ring-gray-800 transition-transform hover:scale-110 hover:z-10 focus:z-10 bg-white"
            >
              <img
                src={contributor.avatar_url}
                alt={displayName}
                className="h-8 w-8 rounded-full bg-gray-200 dark:bg-gray-700 object-cover"
                loading="lazy"
              />
            </a>
            
            {/* Native CSS Fallback Tooltip */}
            <div
              id={tooltipId}
              role="tooltip"
              className="invisible group-hover:visible opacity-0 group-hover:opacity-100 absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded whitespace-nowrap z-50 transition-opacity duration-200 pointer-events-none shadow-lg"
            >
              <span className="font-medium">{displayName}</span>
              {contributor.contributions !== undefined && (
                <span className="block text-gray-300 text-[10px] mt-0.5">
                  {contributor.contributions} contribution{contributor.contributions !== 1 && 's'}
                </span>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default Contributors;