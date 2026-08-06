import { Button } from '@heroui/button'
import { Tooltip } from '@heroui/tooltip'
import Link from 'next/link'
import React, { ReactNode } from 'react'

interface ActionButtonProps {
  url?: string
  onClick?: () => void
  onKeyDown?: (e: React.KeyboardEvent<HTMLAnchorElement | HTMLButtonElement>) => void
  tooltipLabel?: string
  isDisabled?: boolean
  children: ReactNode
}

const ActionButton: React.FC<ActionButtonProps> = ({
  url,
  onClick,
  onKeyDown,
  tooltipLabel,
  isDisabled,
  children,
}) => {
  const baseStyles =
    'flex items-center gap-2 px-2 py-2 rounded-md border border-[#1D7BD7] transition-all whitespace-nowrap justify-center bg-transparent text-[#1D7BD7] hover:bg-[#1D7BD7] hover:text-white dark:hover:text-white'

  return url ? (
    <TooltipWrapper tooltipLabel={tooltipLabel}>
      <Link
        href={isDisabled ? '#' : url}
        target={isDisabled ? undefined : '_blank'}
        rel="noopener noreferrer"
        className={`${baseStyles} ${
          isDisabled ? 'pointer-events-none cursor-not-allowed opacity-50' : ''
        }`}
        data-tooltip-id="button-tooltip"
        data-tooltip-content={tooltipLabel}
        onClick={isDisabled ? (e) => e.preventDefault() : onClick}
        onKeyDown={isDisabled ? undefined : onKeyDown}
        aria-label={tooltipLabel}
        aria-disabled={isDisabled}
        tabIndex={isDisabled ? -1 : undefined}
      >
        {children}
      </Link>
    </TooltipWrapper>
  ) : (
    <TooltipWrapper tooltipLabel={tooltipLabel}>
      <Button
        onPress={isDisabled ? undefined : onClick}
        onKeyDown={isDisabled ? undefined : onKeyDown}
        className={`${baseStyles} ${isDisabled ? 'cursor-not-allowed' : ''}`}
        aria-label={tooltipLabel}
        isDisabled={isDisabled}
      >
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
