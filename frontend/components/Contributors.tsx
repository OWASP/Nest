import React from 'react';

export interface Contributor {
  id: string | number;
  name: string;
  avatar_url?: string;
  profile_url?: string;
  position?: string;
}

export interface ContributorsProps {
  projectId: string | number;
  contributors: Contributor[];
  className?: string;
}

const ContributorAvatar: React.FC<{ contributor: Contributor }> = ({ contributor }) => {
  if (contributor.avatar_url) {
    return (
      <img
        src={contributor.avatar_url}
        alt={contributor.name}
        className="h-8 w-8 rounded-full object-cover border border-gray-200"
        loading="lazy"
      />
    );
  }

  const initials = contributor.name
    ? contributor.name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
    : '?';

  return (
    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-200 text-gray-700 text-xs font-semibold border border-gray-300">
      {initials}
    </div>
  );
};

export const Contributors: React.FC<ContributorsProps> = ({
  projectId,
  contributors,
  className = ''
}) => {
  if (!contributors || contributors.length === 0) {
    return null;
  }

  return (
    <div className={`flex flex-wrap gap-2 ${className}`.trim()}>
      {contributors.map((contributor, index) => {
        // Fix for Issue #1065: Tooltip Collision for Contributors Across Multiple Projects.
        // Append projectId to ensure tooltip IDs and keys are uniquely scoped 
        // across multiple project cards on the same page.
        const uniqueKey = `project-${projectId}-contributor-${contributor.id}-pos-${index}`;
        const tooltipId = `tooltip-${uniqueKey}`;

        return (
          <div key={uniqueKey} className="relative group flex items-center justify-center">
            <div 
              data-tooltip-id={tooltipId}
              data-tooltip-content={`${contributor.name}${contributor.position ? ` - ${contributor.position}` : ''}`}
              aria-describedby={tooltipId}
            >
              {contributor.profile_url ? (
                <a 
                  href={contributor.profile_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block transition-transform hover:scale-105 focus:outline-none"
                >
                  <ContributorAvatar contributor={contributor} />
                </a>
              ) : (
                <div className="block transition-transform hover:scale-105">
                  <ContributorAvatar contributor={contributor} />
                </div>
              )}
            </div>

            {/* CSS-based fallback tooltip to guarantee unique behavior */}
            <div
              id={tooltipId}
              role="tooltip"
              className="pointer-events-none absolute bottom-full left-1/2 z-50 mb-2 -translate-x-1/2 whitespace-nowrap rounded bg-gray-900 px-2 py-1 text-xs text-white opacity-0 transition-opacity group-hover:opacity-100 group-focus-within:opacity-100"
            >
              <div className="text-center">
                <span className="font-medium">{contributor.name}</span>
                {contributor.position && (
                  <span className="block text-[10px] text-gray-300">{contributor.position}</span>
                )}
              </div>
              <div className="absolute left-1/2 top-full -translate-x-1/2 border-4 border-transparent border-t-gray-900" />
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default Contributors;