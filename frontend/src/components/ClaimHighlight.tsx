import { Button } from '@heroui/button'
import { Popover, PopoverContent, PopoverTrigger } from '@heroui/react'
import { useRouter } from 'next/navigation'
import { type ReactNode } from 'react'

import { ClaimStatusEnum } from 'types/__generated__/graphql'
import { type ProfileClaim } from 'components/AnnotatedProfile'

type StatusStyle = {
  publicLabel: string
  candidateLabel: string
  mark: string
  badge: string
}

const STATUS_STYLES: Record<string, StatusStyle> = {
  [ClaimStatusEnum.Approved]: {
    publicLabel: 'Verified',
    candidateLabel: 'Approved',
    mark: 'bg-green-200/70 text-green-900',
    badge: 'bg-green-100 text-green-800 dark:bg-green-800/50 dark:text-green-100',
  },
  [ClaimStatusEnum.Submitted]: {
    publicLabel: 'Under Review',
    candidateLabel: 'Submitted',
    mark: 'bg-gray-200/70 text-gray-800',
    badge: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-100',
  },
  [ClaimStatusEnum.Draft]: {
    publicLabel: 'Draft',
    candidateLabel: 'Draft',
    mark: 'bg-gray-200/70 text-gray-800',
    badge: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-100',
  },
  [ClaimStatusEnum.Rejected]: {
    publicLabel: 'Not Verified',
    candidateLabel: 'Rejected',
    mark: 'bg-red-200/70 text-red-900',
    badge: 'bg-red-100 text-red-800 dark:bg-red-800/50 dark:text-red-100',
  },
}

const CANDIDATE_BADGE_CLASS = 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-200'

type ClaimHighlightProps = {
  children?: ReactNode
  year: string
  login: string
  isCandidate: boolean
  claimsById: Map<string, ProfileClaim>
  'data-id'?: string
}

const ClaimHighlight = ({
  children,
  year,
  login,
  isCandidate,
  claimsById,
  'data-id': claimId,
}: ClaimHighlightProps) => {
  const router = useRouter()

  const claim = claimId ? claimsById.get(claimId) : undefined
  if (!claim) return <>{children}</>

  const style = STATUS_STYLES[claim.status] ?? STATUS_STYLES[ClaimStatusEnum.Draft]
  const href = `/board/${year}/candidates/${login}/claims/${claim.key}`
  const ariaLabel = `Claim: ${claim.name || 'unnamed'}, status ${style.publicLabel}`
  const highlightClass = `cursor-pointer rounded px-0.5 transition-colors hover:brightness-95 ${style.mark}`
  const badgeBaseClass =
    'inline-flex w-fit rounded-md px-1.5 py-0.5 text-[10px] font-semibold tracking-wide uppercase'

  return (
    <Popover placement="top" showArrow>
      <PopoverTrigger>
        <span data-claim-highlight="true" className={highlightClass} aria-label={ariaLabel}>
          {children}
        </span>
      </PopoverTrigger>
      <PopoverContent>
        <div className="flex w-full max-w-xs min-w-48 flex-col items-start gap-2 px-2 py-2">
          <span className="text-sm font-semibold text-gray-900 dark:text-white">{claim.name}</span>
          <div className="flex flex-wrap gap-1">
            <span className={`${badgeBaseClass} ${style.badge}`}>{style.publicLabel}</span>
            {isCandidate && style.candidateLabel !== style.publicLabel && (
              <span className={`${badgeBaseClass} ${CANDIDATE_BADGE_CLASS}`}>
                {style.candidateLabel}
              </span>
            )}
          </div>
          <Button
            color="primary"
            size="sm"
            className="mt-1 w-full font-medium"
            onPress={() => router.push(href)}
          >
            View claim →
          </Button>
        </div>
      </PopoverContent>
    </Popover>
  )
}

export default ClaimHighlight
