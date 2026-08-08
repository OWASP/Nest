import { Popover, PopoverContent, PopoverTrigger } from '@heroui/react'
import { Tooltip } from '@heroui/tooltip'
import { useIsMobile } from 'hooks/useIsMobile'
import { useRouter } from 'next/navigation'
import { type HTMLAttributes, type ReactNode } from 'react'

import { ClaimStatusEnum } from 'types/__generated__/graphql'

type StatusStyle = {
  label: string
  mark: string
  badge: string
}

const STATUS_STYLES: Record<string, StatusStyle> = {
  [ClaimStatusEnum.Approved]: {
    label: 'Approved',
    mark: 'bg-green-200/70 text-green-900',
    badge: 'bg-green-100 text-green-800 dark:bg-green-800/50 dark:text-green-100',
  },
  [ClaimStatusEnum.Submitted]: {
    label: 'Submitted',
    mark: 'bg-yellow-200/70 text-yellow-900',
    badge: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800/50 dark:text-yellow-100',
  },
  [ClaimStatusEnum.Draft]: {
    label: 'Draft',
    mark: 'bg-gray-200/70 text-gray-800',
    badge: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-100',
  },
  [ClaimStatusEnum.Rejected]: {
    label: 'Rejected',
    mark: 'bg-red-200/70 text-red-900',
    badge: 'bg-red-100 text-red-800 dark:bg-red-800/50 dark:text-red-100',
  },
  [ClaimStatusEnum.Withdrawn]: {
    label: 'Withdrawn',
    mark: 'bg-gray-200/70 text-gray-800',
    badge: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-100',
  },
  [ClaimStatusEnum.Discarded]: {
    label: 'Discarded',
    mark: 'bg-gray-200/70 text-gray-800',
    badge: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-100',
  },
}

type ClaimHighlightProps = HTMLAttributes<HTMLElement> & {
  children?: ReactNode
  year: string
  login: string
  'data-claim-key'?: string
  'data-claim-name'?: string
  'data-claim-status'?: string
}

const ClaimHighlight = ({
  children,
  year,
  login,
  'data-claim-key': claimKey,
  'data-claim-name': claimName,
  'data-claim-status': claimStatus,
  ...rest
}: ClaimHighlightProps) => {
  const router = useRouter()
  const isMobile = useIsMobile()

  if (!claimKey) {
    return <span {...rest}>{children}</span>
  }

  const style = STATUS_STYLES[claimStatus ?? ''] ?? STATUS_STYLES[ClaimStatusEnum.Draft]
  const href = `/board/${year}/candidates/${login}/claims/${claimKey}`
  const navigate = () => router.push(href)

  const badge = (
    <span
      className={`inline-flex w-fit rounded-md px-1.5 py-0.5 text-[10px] font-semibold tracking-wide uppercase ${style.badge}`}
    >
      {style.label}
    </span>
  )
  const title = (
    <span className="text-sm font-semibold text-gray-900 dark:text-white">{claimName}</span>
  )

  const highlightClass = `cursor-pointer rounded px-0.5 transition-colors hover:brightness-95 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${style.mark}`
  const ariaLabel = `Claim: ${claimName ?? 'unnamed'}, status ${style.label}`

  if (isMobile) {
    return (
      <Popover placement="top" showArrow>
        <PopoverTrigger>
          <span className={highlightClass} tabIndex={0} role="button" aria-label={ariaLabel}>
            {children}
          </span>
        </PopoverTrigger>
        <PopoverContent>
          <div className="flex w-full max-w-xs min-w-48 flex-col items-start gap-2 px-2 py-2">
            {title}
            {badge}
            <button
              type="button"
              onClick={navigate}
              className="mt-1 inline-flex w-full items-center justify-center gap-1 rounded-md bg-blue-600 px-2.5 py-1.5 text-xs font-medium text-white hover:bg-blue-700"
            >
              View claim →
            </button>
          </div>
        </PopoverContent>
      </Popover>
    )
  }

  return (
    <Tooltip
      content={
        <div className="flex max-w-xs min-w-48 flex-col items-start gap-1.5 p-1">
          {title}
          {badge}
          <span className="text-xs text-gray-500 dark:text-gray-400">Click to view</span>
        </div>
      }
      placement="top"
    >
      <span
        className={highlightClass}
        onClick={navigate}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            navigate()
          }
        }}
        tabIndex={0}
        role="link"
        aria-label={ariaLabel}
      >
        {children}
      </span>
    </Tooltip>
  )
}

export default ClaimHighlight
