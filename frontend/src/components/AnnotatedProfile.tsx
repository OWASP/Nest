'use client'

import { useProfileSelection } from 'hooks/useProfileSelection'
import Markdown from 'markdown-to-jsx'
import { useRouter } from 'next/navigation'
import { type ImgHTMLAttributes, type SourceHTMLAttributes, useMemo, useRef } from 'react'
import { FaPlus } from 'react-icons/fa6'

import { ClaimStatusEnum } from 'types/__generated__/graphql'
import ClaimHighlight from 'components/ClaimHighlight'

export type ProfileClaim = {
  id: string
  key: string
  name: string
  sourceText: string
  status: ClaimStatusEnum
}

interface AnnotatedProfileProps {
  claims: ProfileClaim[]
  isCandidate: boolean
  login: string
  rawMarkdown: string
  year: string
}

const STATUS_PRIORITY: Partial<Record<ClaimStatusEnum, number>> = {
  [ClaimStatusEnum.Approved]: 3,
  [ClaimStatusEnum.Submitted]: 2,
  [ClaimStatusEnum.Draft]: 1,
  [ClaimStatusEnum.Rejected]: 0,
}

const VISIBLE_STATUSES = new Set(Object.keys(STATUS_PRIORITY) as ClaimStatusEnum[])

const resolveMediaSrc = <T,>(src: T, year: string): T | string => {
  if (typeof src !== 'string' || !src) return src
  try {
    return new URL(src, `https://owasp.org/www-board-candidates/${year}/`).href
  } catch {
    return src
  }
}

type WrapResult = { wrapped: string; claimsById: Map<string, ProfileClaim> }

const wrapClaims = (markdown: string, claims: ProfileClaim[]): WrapResult => {
  const eligible = claims
    .filter((c) => c.sourceText && !c.sourceText.includes('\n\n') && VISIBLE_STATUSES.has(c.status))
    .toSorted((a, b) => {
      const lengthDiff = b.sourceText.length - a.sourceText.length
      if (lengthDiff !== 0) return lengthDiff
      return (STATUS_PRIORITY[b.status] ?? 0) - (STATUS_PRIORITY[a.status] ?? 0)
    })

  const ranges: Array<{ start: number; end: number; claim: ProfileClaim }> = []
  for (const claim of eligible) {
    let searchFrom = 0
    while (searchFrom < markdown.length) {
      const start = markdown.indexOf(claim.sourceText, searchFrom)
      if (start < 0) break
      const end = start + claim.sourceText.length
      if (!ranges.some((r) => start < r.end && end > r.start)) {
        ranges.push({ start, end, claim })
      }
      searchFrom = end
    }
  }

  const claimsById = new Map<string, ProfileClaim>()
  const orderedRanges = ranges.toSorted((a, b) => b.start - a.start)
  const wrapped = orderedRanges.reduce((acc, { start, end, claim }) => {
    claimsById.set(claim.id, claim)
    const open = `<claim-highlight data-id="${claim.id}">`
    return `${acc.slice(0, start)}${open}${acc.slice(start, end)}</claim-highlight>${acc.slice(end)}`
  }, markdown)
  return { wrapped, claimsById }
}

type MediaImgProps = ImgHTMLAttributes<HTMLImageElement> & { year: string }

const MediaImg = ({ year, ...props }: MediaImgProps) => (
  // eslint-disable-next-line @next/next/no-img-element, jsx-a11y/alt-text -- candidate markdown may reference arbitrary hosts and set alt itself
  <img {...props} src={resolveMediaSrc(props.src, year)} />
)

type MediaSourceProps = SourceHTMLAttributes<HTMLSourceElement> & { year: string }

const MediaSource = ({ year, ...props }: MediaSourceProps) => (
  <source {...props} src={resolveMediaSrc(props.src, year)} />
)

const AnnotatedProfile = ({
  claims,
  isCandidate,
  login,
  rawMarkdown,
  year,
}: AnnotatedProfileProps) => {
  const router = useRouter()
  const containerRef = useRef<HTMLDivElement>(null)
  const selection = useProfileSelection(containerRef, isCandidate)

  const { wrapped, claimsById } = useMemo(
    () => wrapClaims(rawMarkdown, claims),
    [rawMarkdown, claims]
  )
  const canCreateClaim = isCandidate && selection !== null && rawMarkdown.includes(selection.text)

  const markdownOptions = useMemo(
    () => ({
      overrides: {
        'claim-highlight': {
          component: ClaimHighlight,
          props: { year, login, isCandidate, claimsById },
        },
        img: { component: MediaImg, props: { year } },
        source: { component: MediaSource, props: { year } },
      },
    }),
    [year, login, isCandidate, claimsById]
  )

  const handleCreateFromSelection = () => {
    if (!selection) return
    const params = new URLSearchParams({ sourceText: selection.text })
    router.push(`/board/${year}/candidates/${login}/claims/create?${params}`)
  }

  return (
    <div className="relative">
      <div
        ref={containerRef}
        className="md-wrapper md-neutralized rounded-xl bg-white p-6 text-gray-700 shadow-sm dark:bg-slate-800 dark:text-gray-300"
      >
        <Markdown options={markdownOptions}>{wrapped}</Markdown>
      </div>

      {canCreateClaim && selection && (
        <button
          type="button"
          onMouseDown={(e) => e.preventDefault()}
          onClick={handleCreateFromSelection}
          style={{
            top: `${Math.max(8, selection.rect.top - 44)}px`,
            left: `${selection.rect.left + selection.rect.width / 2}px`,
          }}
          className="fixed z-50 inline-flex -translate-x-1/2 items-center gap-1.5 rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white shadow-lg transition-colors hover:bg-blue-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400"
        >
          <FaPlus className="h-3 w-3" />
          Create claim
        </button>
      )}
    </div>
  )
}

export default AnnotatedProfile
