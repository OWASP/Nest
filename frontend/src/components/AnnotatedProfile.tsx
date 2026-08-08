'use client'

import { useProfileSelection } from 'hooks/useProfileSelection'
import Markdown from 'markdown-to-jsx'
import { useRouter } from 'next/navigation'
import { type ImgHTMLAttributes, type SourceHTMLAttributes, useMemo, useRef } from 'react'
import { FaPlus } from 'react-icons/fa6'

import { ClaimStatusEnum } from 'types/__generated__/graphql'
import ClaimHighlight from 'components/ClaimHighlight'

type ProfileClaim = {
  id: string
  key: string
  name: string
  sourceText: string
  status: ClaimStatusEnum
}

interface AnnotatedProfileProps {
  claims: ProfileClaim[]
  isCandidate: boolean
  isReviewer: boolean
  login: string
  rawMarkdown: string
  year: string
}

const STATUS_PRIORITY: Record<ClaimStatusEnum, number> = {
  [ClaimStatusEnum.Approved]: 5,
  [ClaimStatusEnum.Submitted]: 4,
  [ClaimStatusEnum.Draft]: 3,
  [ClaimStatusEnum.Rejected]: 2,
  [ClaimStatusEnum.Withdrawn]: 1,
  [ClaimStatusEnum.Discarded]: 0,
}

const escapeAttribute = (value: string): string =>
  value
    .replaceAll('&', '&amp;')
    .replaceAll('"', '&quot;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')

const resolveMediaSrc = <T,>(src: T, year: string): T | string => {
  if (typeof src !== 'string' || !src) return src
  try {
    return new URL(src, `https://owasp.org/www-board-candidates/${year}/`).href
  } catch {
    return src
  }
}

const wrapClaims = (markdown: string, claims: ProfileClaim[]): string => {
  const eligible = claims
    .filter((c) => c.sourceText && !c.sourceText.includes('\n\n'))
    .sort((a, b) => {
      const lengthDiff = b.sourceText.length - a.sourceText.length
      if (lengthDiff !== 0) return lengthDiff
      return (STATUS_PRIORITY[b.status] ?? 0) - (STATUS_PRIORITY[a.status] ?? 0)
    })

  const ranges: Array<{ start: number; end: number; claim: ProfileClaim }> = []
  for (const claim of eligible) {
    const start = markdown.indexOf(claim.sourceText)
    if (start < 0) continue
    const end = start + claim.sourceText.length
    if (ranges.some((r) => start < r.end && end > r.start)) continue
    ranges.push({ start, end, claim })
  }

  return ranges
    .sort((a, b) => b.start - a.start)
    .reduce((acc, { start, end, claim }) => {
      const open =
        `<span data-claim-key="${escapeAttribute(claim.key)}"` +
        ` data-claim-name="${escapeAttribute(claim.name)}"` +
        ` data-claim-status="${claim.status}">`
      return `${acc.slice(0, start)}${open}${acc.slice(start, end)}</span>${acc.slice(end)}`
    }, markdown)
}

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

  const wrapped = useMemo(() => wrapClaims(rawMarkdown, claims), [rawMarkdown, claims])

  const markdownOptions = useMemo(
    () => ({
      overrides: {
        span: {
          component: ClaimHighlight,
          props: { year, login },
        },
        img: {
          component: (props: ImgHTMLAttributes<HTMLImageElement>) => (
            // eslint-disable-next-line @next/next/no-img-element, jsx-a11y/alt-text -- candidate markdown may reference arbitrary hosts and set alt itself
            <img {...props} src={resolveMediaSrc(props.src, year)} />
          ),
        },
        source: {
          component: (props: SourceHTMLAttributes<HTMLSourceElement>) => (
            <source {...props} src={resolveMediaSrc(props.src, year)} />
          ),
        },
      },
    }),
    [year, login]
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
        className="md-wrapper rounded-xl bg-white p-6 text-gray-700 shadow-sm"
      >
        <Markdown options={markdownOptions}>{wrapped}</Markdown>
      </div>

      {isCandidate && selection && (
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
