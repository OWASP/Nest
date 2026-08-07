'use client'

import { upperFirst, toLower } from 'lodash'
import { compiler } from 'markdown-to-jsx/react'
import { useRouter } from 'next/navigation'
import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactElement,
  type ReactNode,
} from 'react'
import { FaArrowRight, FaPlus } from 'react-icons/fa6'

import { ClaimStatusEnum } from 'types/__generated__/graphql'

type VisibleClaim = {
  id: string
  key: string
  name: string
  sourceText: string
  status: ClaimStatusEnum
}

export type { VisibleClaim }

interface AnnotatedProfileProps {
  claims: VisibleClaim[]
  isCandidate: boolean
  isReviewer: boolean
  login: string
  rawMarkdown: string
  year: string
}

export const PRIORITY_ORDER = [
  ClaimStatusEnum.Draft,
  ClaimStatusEnum.Submitted,
  ClaimStatusEnum.Rejected,
  ClaimStatusEnum.Approved,
] as const

const CURLY_QUOTE_MAP: Record<string, string> = {
  '‘': "'",
  '’': "'",
  '“': '"',
  '”': '"',
}
const CURLY_QUOTE_RE = /[‘’“”]/g

export function visibleStatuses(isCandidate: boolean, isReviewer: boolean): ClaimStatusEnum[] {
  return [
    ClaimStatusEnum.Approved,
    ClaimStatusEnum.Rejected,
    ...(isCandidate || isReviewer ? [ClaimStatusEnum.Submitted] : []),
    ...(isCandidate ? [ClaimStatusEnum.Draft] : []),
  ]
}

export function overlapsExistingClaim(selectedText: string, claimedTexts: string[]): boolean {
  const sel = selectedText.trim()
  if (!sel) return false
  return claimedTexts.some((raw) => {
    const claimed = raw.trim()
    if (!claimed) return false
    return sel.includes(claimed) || claimed.includes(sel)
  })
}

export const STATUS_COLOR: Record<ClaimStatusEnum, string> = {
  [ClaimStatusEnum.Approved]: 'bg-green-200 text-green-950',
  [ClaimStatusEnum.Discarded]: 'bg-gray-200 text-gray-950',
  [ClaimStatusEnum.Draft]: 'bg-gray-200 text-gray-950',
  [ClaimStatusEnum.Rejected]: 'bg-red-200 text-red-950',
  [ClaimStatusEnum.Submitted]: 'bg-amber-200 text-amber-950',
  [ClaimStatusEnum.Withdrawn]: 'bg-gray-200 text-gray-950',
}

const STATUS_DOT: Record<ClaimStatusEnum, string> = {
  [ClaimStatusEnum.Approved]: 'bg-green-400',
  [ClaimStatusEnum.Discarded]: 'bg-gray-400',
  [ClaimStatusEnum.Draft]: 'bg-gray-400',
  [ClaimStatusEnum.Rejected]: 'bg-red-400',
  [ClaimStatusEnum.Submitted]: 'bg-amber-400',
  [ClaimStatusEnum.Withdrawn]: 'bg-gray-400',
}

type HighlightRange = {
  start: number
  end: number
  claim: VisibleClaim
}

function normalizeForMatch(text: string): string {
  return text.replace(CURLY_QUOTE_RE, (ch) => CURLY_QUOTE_MAP[ch])
}

function priorityOf(status: ClaimStatusEnum): number {
  return (PRIORITY_ORDER as readonly ClaimStatusEnum[]).indexOf(status)
}

export function computeHighlightRanges(text: string, claims: VisibleClaim[]): HighlightRange[] {
  const normalized = normalizeForMatch(text)
  const chosen: HighlightRange[] = []

  const sortedClaims = claims
    .filter((c) => (PRIORITY_ORDER as readonly ClaimStatusEnum[]).includes(c.status))
    .sort((a, b) => priorityOf(a.status) - priorityOf(b.status))

  for (const claim of sortedClaims) {
    const source = normalizeForMatch(claim.sourceText)
    if (!source) continue

    let from = 0
    while (true) {
      const start = normalized.indexOf(source, from)
      if (start === -1) break
      const next = { start, end: start + source.length, claim }
      const overlapIdx = chosen.findIndex((r) => r.start < next.end && r.end > next.start)
      if (overlapIdx === -1) {
        chosen.push(next)
      } else if (chosen[overlapIdx].start === start && chosen[overlapIdx].end === next.end) {
        chosen[overlapIdx] = next
      }
      from = start + 1
    }
  }
  return chosen.sort((a, b) => a.start - b.start)
}

export function resolveMediaUrl(src: string, year: string): string {
  try {
    return new URL(src, `https://owasp.org/www-board-candidates/${year}/`).href
  } catch {
    return src
  }
}

function flatTextOf(node: ReactNode): string {
  if (typeof node === 'string') return node
  if (typeof node === 'number') return String(node)
  if (Array.isArray(node)) return node.map(flatTextOf).join('')
  if (React.isValidElement(node)) {
    const el = node as ReactElement<{ children?: ReactNode }>
    return el.props?.children != null ? flatTextOf(el.props.children) : ''
  }
  return ''
}

type RenderMark = (claim: VisibleClaim, children: ReactNode, key: string) => ReactElement

function injectMarks(
  node: ReactNode,
  ranges: HighlightRange[],
  cursor: { value: number },
  renderMark: RenderMark
): ReactNode {
  if (typeof node === 'string') {
    const textStart = cursor.value
    cursor.value += node.length
    const inside = ranges.filter((r) => r.start < cursor.value && r.end > textStart)
    if (!inside.length) return node

    const parts: ReactNode[] = []
    let idx = 0
    inside.forEach((r, i) => {
      const from = Math.max(0, r.start - textStart)
      const to = Math.min(node.length, r.end - textStart)
      if (from > idx) parts.push(node.slice(idx, from))
      parts.push(renderMark(r.claim, node.slice(from, to), `${textStart}-${i}`))
      idx = to
    })
    if (idx < node.length) parts.push(node.slice(idx))
    return <>{parts}</>
  }
  if (Array.isArray(node)) {
    return node.map((child, i) => (
      // eslint-disable-next-line react/no-array-index-key
      <React.Fragment key={i}>{injectMarks(child, ranges, cursor, renderMark)}</React.Fragment>
    ))
  }
  if (React.isValidElement(node)) {
    const el = node as ReactElement<{ children?: ReactNode }>
    if (el.props?.children == null) return el
    return React.cloneElement(el, {}, injectMarks(el.props.children, ranges, cursor, renderMark))
  }
  return node
}

const AnnotatedProfile = ({
  claims,
  isCandidate,
  isReviewer,
  login,
  rawMarkdown,
  year,
}: AnnotatedProfileProps) => {
  const router = useRouter()
  const containerRef = useRef<HTMLDivElement>(null)
  const wrapperRef = useRef<HTMLDivElement>(null)
  const hideTimerRef = useRef<number | null>(null)
  const [tooltip, setTooltip] = useState<{
    claim: VisibleClaim
    x: number
    y: number
    width: number
  } | null>(null)
  const [selection, setSelection] = useState<{
    text: string
    x: number
    y: number
    width: number
  } | null>(null)

  const filteredClaims = useMemo(
    () => claims.filter((c) => visibleStatuses(isCandidate, isReviewer).includes(c.status)),
    [claims, isCandidate, isReviewer]
  )

  const claimedTexts = useMemo(
    () => filteredClaims.map((c) => c.sourceText).filter(Boolean),
    [filteredClaims]
  )

  const scheduleHide = useCallback((delay = 400) => {
    if (hideTimerRef.current) clearTimeout(hideTimerRef.current)
    hideTimerRef.current = window.setTimeout(() => setTooltip(null), delay)
  }, [])

  const showTooltip = useCallback((claim: VisibleClaim, el: HTMLElement) => {
    if (hideTimerRef.current) clearTimeout(hideTimerRef.current)
    setSelection(null)
    const rect = el.getBoundingClientRect()
    setTooltip({ claim, x: rect.left, y: rect.top, width: rect.width })
  }, [])

  const renderMark = useCallback<RenderMark>(
    (claim, children, key) => (
      <span
        key={key}
        role="button"
        aria-label={`Claim: ${claim.name} (${toLower(claim.status)})`}
        className={`${STATUS_COLOR[claim.status] ?? 'bg-gray-400'} rounded px-0.5`}
        data-claim-key={claim.key}
        data-claim-name={claim.name}
        data-claim-status={claim.status}
        tabIndex={0}
        onMouseOver={(e) => showTooltip(claim, e.currentTarget)}
        onFocus={(e) => showTooltip(claim, e.currentTarget)}
        onKeyDown={(e) => {
          if (e.key !== 'Enter') return
          e.preventDefault()
          setTooltip(null)
          router.push(`/board/${year}/candidates/${login}/claims/${claim.key}`)
        }}
      >
        {children}
      </span>
    ),
    [showTooltip, router, year, login]
  )

  const content = useMemo(() => {
    const compiled = compiler(rawMarkdown, {
      overrides: {
        img: (props: React.ImgHTMLAttributes<HTMLImageElement>) => {
          const src = typeof props.src === 'string' ? resolveMediaUrl(props.src, year) : props.src
          // eslint-disable-next-line @next/next/no-img-element -- candidate markdown may reference arbitrary hosts
          return <img alt="" {...props} src={src} />
        },
        source: (props: React.SourceHTMLAttributes<HTMLSourceElement>) => {
          const src = typeof props.src === 'string' ? resolveMediaUrl(props.src, year) : props.src
          return <source {...props} src={src} />
        },
      },
    })
    const ranges = computeHighlightRanges(flatTextOf(compiled), filteredClaims)
    return injectMarks(compiled, ranges, { value: 0 }, renderMark)
  }, [rawMarkdown, year, filteredClaims, renderMark])

  const handleSelectionCheck = useCallback(() => {
    if (!isCandidate) return
    const wrapper = wrapperRef.current
    if (!wrapper) return
    const sel = window.getSelection()
    if (!sel || sel.isCollapsed || !sel.rangeCount || sel.toString().trim() === '') {
      setSelection(null)
      return
    }
    const range = sel.getRangeAt(0)
    if (!wrapper.contains(range.startContainer) || !wrapper.contains(range.endContainer)) return
    const text = sel.toString().trim()
    if (!text || overlapsExistingClaim(text, claimedTexts)) {
      setSelection(null)
      return
    }
    const rect = range.getBoundingClientRect()
    setTooltip(null)
    setSelection({ text, x: rect.left, y: rect.top, width: rect.width })
  }, [isCandidate, claimedTexts])

  useEffect(() => {
    const container = containerRef.current
    const wrapper = wrapperRef.current
    const onScroll = () => {
      if (hideTimerRef.current) clearTimeout(hideTimerRef.current)
      setTooltip(null)
      setSelection(null)
    }
    const onMouseLeave = () => scheduleHide()
    window.addEventListener('scroll', onScroll, true)
    container?.addEventListener('mouseleave', onMouseLeave)
    wrapper?.addEventListener('mouseup', handleSelectionCheck)
    wrapper?.addEventListener('keyup', handleSelectionCheck)
    return () => {
      window.removeEventListener('scroll', onScroll, true)
      container?.removeEventListener('mouseleave', onMouseLeave)
      wrapper?.removeEventListener('mouseup', handleSelectionCheck)
      wrapper?.removeEventListener('keyup', handleSelectionCheck)
      if (hideTimerRef.current) clearTimeout(hideTimerRef.current)
    }
  }, [scheduleHide, handleSelectionCheck])

  const handleTooltipEnter = () => {
    if (hideTimerRef.current) clearTimeout(hideTimerRef.current)
  }
  const handleTooltipLeave = () => scheduleHide()
  const handleTooltipClick = () => {
    if (!tooltip) return
    setTooltip(null)
    router.push(`/board/${year}/candidates/${login}/claims/${tooltip.claim.key}`)
  }

  const handleCreateClaimClick = () => {
    if (!selection) return
    const text = selection.text
    setSelection(null)
    router.push(
      `/board/${year}/candidates/${login}/claims/create?sourceText=${encodeURIComponent(text)}`
    )
  }

  return (
    <div ref={containerRef} className="relative">
      <div ref={wrapperRef} className="md-wrapper rounded-xl bg-white p-6 text-gray-600">
        {content}
      </div>
      {selection && isCandidate && (
        <AnchoredPopup anchor={selection} onClick={handleCreateClaimClick}>
          <span className="flex items-center gap-2">
            <FaPlus className="h-3 w-3" aria-hidden="true" />
            <span className="truncate font-semibold">Create Claim</span>
          </span>
          <span className="mt-1 line-clamp-2 text-gray-500 dark:text-gray-400">
            "{selection.text}"
          </span>
        </AnchoredPopup>
      )}
      {tooltip && (
        <AnchoredPopup
          anchor={tooltip}
          onClick={handleTooltipClick}
          onMouseEnter={handleTooltipEnter}
          onMouseLeave={handleTooltipLeave}
        >
          <span className="flex items-center gap-2">
            <span
              className={`h-2.5 w-2.5 shrink-0 rounded-full ${STATUS_DOT[tooltip.claim.status] ?? 'bg-gray-400'}`}
            />
            <span className="truncate font-semibold">{tooltip.claim.name || 'Claim'}</span>
          </span>
          <span className="mt-1 flex items-center gap-1 text-gray-500 dark:text-gray-400">
            <span>{upperFirst(toLower(tooltip.claim.status))}</span>
            <FaArrowRight className="ml-auto h-3 w-3" aria-hidden="true" />
          </span>
        </AnchoredPopup>
      )}
    </div>
  )
}

const POPUP_HALF_WIDTH = 112

type AnchoredPopupProps = {
  anchor: { x: number; y: number; width: number }
  onClick: () => void
  onMouseEnter?: () => void
  onMouseLeave?: () => void
  children: ReactNode
}

const AnchoredPopup = ({
  anchor,
  onClick,
  onMouseEnter,
  onMouseLeave,
  children,
}: AnchoredPopupProps) => (
  <div
    data-tooltip
    className="fixed z-50 -translate-x-1/2 -translate-y-full pb-2"
    style={{
      left: Math.min(
        Math.max(anchor.x + anchor.width / 2, POPUP_HALF_WIDTH),
        window.innerWidth - POPUP_HALF_WIDTH
      ),
      top: anchor.y,
    }}
    onMouseEnter={onMouseEnter}
    onMouseLeave={onMouseLeave}
  >
    <button
      type="button"
      onClick={onClick}
      className="peer block w-56 cursor-pointer rounded-lg border border-gray-300 bg-white px-3 py-2 text-left text-xs text-gray-800 shadow-xl transition-colors hover:bg-slate-100 dark:border-slate-600 dark:bg-slate-800 dark:text-white dark:hover:bg-slate-700"
    >
      {children}
    </button>
    <div className="mx-auto h-2 w-2 -translate-y-1 rotate-45 border-r border-b border-gray-300 bg-white transition-colors peer-hover:bg-slate-100 dark:border-slate-600 dark:bg-slate-800 dark:peer-hover:bg-slate-700" />
  </div>
)

export default AnnotatedProfile
