import React, { ReactNode } from 'react';
import { Tooltip } from 'react-tooltip';
import { tooltipStyle } from '../lib/constants';

interface ActionButtonProps {
  url?: string;
  onClick?: () => void;
  tooltipLabel?: string;
  children: ReactNode;
}

const ActionButton: React.FC<ActionButtonProps> = ({ url, onClick, tooltipLabel, children }) => {
  const baseStyles = "flex justify-center items-center gap-2 p-1 px-2 rounded-md bg-transparent hover:bg-[#0D6EFD] text-[#0D6EFD] hover:text-white dark:text-white border border-[#0D6EFD] dark:border-0 ";

  return url ? (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className={baseStyles}
      data-tooltip-id="button-tooltip"
      data-tooltip-content={tooltipLabel}
    >
      {children}
      <Tooltip id="button-tooltip" style={tooltipStyle}  />
    </a>
  ) : (
    <button
      onClick={onClick}
      className={baseStyles}
      data-tooltip-id="button-tooltip"
      data-tooltip-content={tooltipLabel}
    >
      {children}
      <Tooltip id="button-tooltip" style={tooltipStyle}  />
    </button>
  )
}

export default ActionButton
