import { Button } from '@heroui/button'
import { Tooltip } from '@heroui/tooltip'
import Link from 'next/link'
import React, { ReactNode } from 'react'

import { cn } from 'utils/utility'

interface ActionButtonProps {
  url?: string
  onClick?: () => void
  onKeyDown?: (e: React.KeyboardEvent<HTMLAnchorElement | HTMLButtonElement>) => void
  tooltipLabel?: string
  children: ReactNode
  className?: string
  isDisabled?: boolean
}

const ActionButton: React.FC<ActionButtonProps> = ({
  url,
  onClick,
  onKeyDown,
  tooltipLabel,
  children,
  className = '',
  isDisabled = false,
}) => {
  const baseStyles =
    'flex items-center gap-2 px-2 py-2 rounded-md border border-[#1D7BD7] transition-all whitespace-nowrap justify-center bg-transparent text-[#1D7BD7] hover:bg-[#1D7BD7] hover:text-white dark:hover:text-white'

  const disabledStyles = isDisabled ? 'opacity-50 cursor-not-allowed pointer-events-none' : ''
  const combinedStyles = cn(baseStyles, disabledStyles, className)

  return url ? (
    <TooltipWrapper tooltipLabel={tooltipLabel}>
      <Link
        href={isDisabled ? '#' : url}
        target={isDisabled ? undefined : '_blank'}
        rel={isDisabled ? undefined : 'noopener noreferrer'}
        className={combinedStyles}
        data-tooltip-id="button-tooltip"
        data-tooltip-content={tooltipLabel}
        onClick={onClick}
        onKeyDown={onKeyDown}
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
        onPress={onClick}
        onKeyDown={onKeyDown}
        className={combinedStyles}
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
