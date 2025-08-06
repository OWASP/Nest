import { Button } from '@heroui/button'
import { Tooltip } from '@heroui/tooltip'
import Link from 'next/link'
import React, { ReactNode } from 'react'

interface ActionButtonProps {
  url?: string
  onClick?: () => void
  tooltipLabel?: string
  children: ReactNode
}

const ActionButton: React.FC<ActionButtonProps> = ({ url, onClick, tooltipLabel, children }) => {
  const baseStyles =
    'flex items-center gap-2 px-2 py-2 rounded-md border transition-all text-nowrap justify-center bg-transparent text-blue-600 border-[#1D7BD7] hover:bg-[#1D7BD7] text-[#1D7BD7] hover:text-white dark:hover:text-white'

  return url ? (
    <TooltipWrapper tooltipLabel={tooltipLabel}>
      <Link
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className={baseStyles}
        data-tooltip-id="button-tooltip"
        data-tooltip-content={tooltipLabel}
        onClick={onClick}
        aria-label={tooltipLabel}
      >
        {children}
      </Link>
    </TooltipWrapper>
  ) : (
    <TooltipWrapper tooltipLabel={tooltipLabel}>
      <Button onPress={onClick} className={baseStyles} aria-label={tooltipLabel}>
        {children}
      </Button>
    </TooltipWrapper>
  )
}

const TooltipWrapper: React.FC<{ tooltipLabel?: string; children: ReactNode }> = ({
  tooltipLabel,
  children,
}) =>
  tooltipLabel ? (
    <Tooltip id="button-tooltip" content={tooltipLabel}>
      {children}
    </Tooltip>
  ) : (
    <>{children}</>
  )

export default ActionButton
