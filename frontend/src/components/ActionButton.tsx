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
    'flex flex-nowrap text-nowrap justify-center self-end items-center gap-2 p-1 px-2 rounded-md bg-transparent hover:bg-[#0D6EFD] text-[#0D6EFD] hover:text-white border border-[#0D6EFD] dark:border-sky-600 dark:text-sky-600 dark:hover:bg-sky-100'

  return url ? (
    tooltipLabel ? (
      <Tooltip id="button-tooltip" content={tooltipLabel} recipe={TooltipRecipe}>
        <Link
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className={baseStyles}
          data-tooltip-id="button-tooltip"
          data-tooltip-content={tooltipLabel}
        >
          {children}
        </Link>
      </Tooltip>
    ) : (
      <Link href={url} target="_blank" rel="noopener noreferrer" className={baseStyles}>
        {children}
      </Link>
    )
  ) : tooltipLabel ? (
    <Tooltip id="button-tooltip" content={tooltipLabel} recipe={TooltipRecipe}>
      <Button
        onClick={onClick}
        className={baseStyles}
        data-tooltip-id="button-tooltip"
        data-tooltip-content={tooltipLabel}
      >
        {children}
      </Button>
    </Tooltip>
  ) : (
    <Button onClick={onClick} className={baseStyles}>
      {children}
    </Button>
  )
}

export default ActionButton
