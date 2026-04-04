import React from 'react';

export interface Contributor {
  id?: string | number;
  login?: string;
  name?: string;
  avatar_url?: string;
  html_url?: string;
  profile_url?: string;
}

export interface ContributorsProps {
  contributors: Contributor[];
  projectId: string | number;
}

const Contributors: React.FC<ContributorsProps> = ({ contributors, projectId }) => {
  if (!contributors || !Array.isArray(contributors) || contributors.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      {contributors.map((contributor, index) => {
        // Strategy: Extend the unique key for contributor tooltips to include the project identifier
        // to prevent collisions when the same contributor appears in multiple projects on the same page.
        const identifier = contributor.id || contributor.login || index;
        const uniqueKey = `project-${projectId}-contributor-${identifier}-pos-${index}`;
        const tooltipId = `tooltip-${uniqueKey}`;
        
        const displayName = contributor.name || contributor.login || 'Contributor';
        const profileUrl = contributor.html_url || contributor.profile_url || '#';

        return (
          <div key={uniqueKey} className="relative group flex items-center justify-center">
            <a
              href={profileUrl}
              target={profileUrl !== '#' ? '_blank' : undefined}
              rel={profileUrl !== '#' ? 'noopener noreferrer' : undefined}
              className="inline-block transition-transform hover:scale-110 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-full"
              aria-describedby={tooltipId}
            >
              {contributor.avatar_url ? (
                <img
                  src={contributor.avatar_url}
                  alt={displayName}
                  className="w-8 h-8 rounded-full border border-gray-200 shadow-sm object-cover bg-white"
                  loading="lazy"
                />
              ) : (
                <div className="w-8 h-8 rounded-full bg-gray-200 border border-gray-300 shadow-sm flex items-center justify-center text-gray-700 text-xs font-semibold">
                  {displayName.charAt(0).toUpperCase()}
                </div>
              )}
            </a>
            
            {/* Tooltip */}
            <div
              id={tooltipId}
              role="tooltip"
              className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-50 px-2.5 py-1 text-xs font-medium text-white bg-gray-900 rounded-md shadow-sm whitespace-nowrap"
            >
              {displayName}
              <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-px border-4 border-transparent border-t-gray-900"></div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default Contributors;