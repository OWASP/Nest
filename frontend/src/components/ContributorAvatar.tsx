import { Tooltip } from 'react-tooltip';
import { topContributorsType } from 'types/contributor';
import { tooltipStyle } from 'utils/constants';

const ContributorAvatar = ({ contributor }: { contributor: topContributorsType }) => {
  // Fallback to username if name is unavailable
  const displayName = contributor.name || contributor.login || 'Anonymous';

  return (
    <a
      data-tooltip-id={`avatar-tooltip-${contributor.login}`}
      data-tooltip-content={`${contributor.contributions_count} contributions by ${displayName}`}
      href={`/community/users/${contributor.login}`}
      target="_blank"
    >
      <img
        className="h-[30px] w-[30px] rounded-full grayscale hover:grayscale-0"
        src={contributor.avatar_url}
        alt={`${displayName}'s avatar`}
      />
      <Tooltip id={`avatar-tooltip-${contributor.login}`} style={tooltipStyle} />
    </a>
  );
};

export default ContributorAvatar;
