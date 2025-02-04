import { Link } from '@chakra-ui/react'
import React, { ReactNode } from 'react'
import { TooltipRecipe } from 'utils/theme'
import { Button } from 'components/ui/button'
import { Tooltip } from 'components/ui/tooltip'

interface ActionButtonProps {
  url?: string
  onClick?: () => void
  tooltipLabel?: string
  children: ReactNode
}

const ActionButton: React.FC<ActionButtonProps> = ({ url, onClick, tooltipLabel, children }) => {
  const baseStyles =
    'flex items-center gap-2 px-2 py-2 rounded-md border transition-all text-nowrap justify-center bg-transparent text-blue-600 border-[#0D6EFD] hover:bg-[#0D6EFD] text-[#0D6EFD] hover:text-white dark:border-sky-600 dark:text-sky-600 dark:hover:bg-sky-100'

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
      <Button
        focusVisibleRing={'none'}
        focusRingColor={'currentBg'}
        onClick={onClick}
        className={baseStyles}
        aria-label={tooltipLabel}
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
    <Tooltip id="button-tooltip" content={tooltipLabel} recipe={TooltipRecipe}>
      {children}
    </Tooltip>
  ) : (
    <>{children}</>
  )

export default ActionButton
