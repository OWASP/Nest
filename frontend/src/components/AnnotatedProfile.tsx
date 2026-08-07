'use client'

import DOMPurify from 'isomorphic-dompurify'
import { upperFirst, toLower } from 'lodash'
import markdownit from 'markdown-it'
import { useRouter } from 'next/navigation'
import { useEffect, useMemo, useRef, useState, type ReactNode } from 'react'
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
  '\u2018': "'",
  '\u2019': "'",
  '\u201C': '"',
  '\u201D': '"',
}

const CURLY_QUOTE_RE = /[\u2018\u2019\u201C\u201D]/g

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

function addHighlightRange(ranges: HighlightRange[], next: HighlightRange): void {
  const overlapIndex = ranges.findIndex(
    (existing) => existing.start < next.end && existing.end > next.start
  )
  if (overlapIndex === -1) {
    ranges.push(next)
  } else if (ranges[overlapIndex].start === next.start && ranges[overlapIndex].end === next.end) {
    ranges[overlapIndex] = next
  }
}

function priorityOf(status: ClaimStatusEnum): number {
  return (PRIORITY_ORDER as readonly ClaimStatusEnum[]).indexOf(status)
}

function normalizeForMatch(text: string): string {
  return text.replace(CURLY_QUOTE_RE, (ch) => CURLY_QUOTE_MAP[ch])
}

function computeHighlightRanges(text: string, claims: VisibleClaim[]): HighlightRange[] {
  const normalizedText = normalizeForMatch(text)
  // Iterate lowest priority first so that a higher-priority claim replaces an
  // identical range, while a partially overlapping one is skipped entirely.
  return claims
    .filter((c) => (PRIORITY_ORDER as readonly ClaimStatusEnum[]).includes(c.status))
    .sort((a, b) => priorityOf(a.status) - priorityOf(b.status))
    .flatMap((claim) => {
      const sourceText = normalizeForMatch(claim.sourceText)
      if (!sourceText) return []

      const ranges: HighlightRange[] = []
      let searchFrom = 0
      while (searchFrom < normalizedText.length) {
        const start = normalizedText.indexOf(sourceText, searchFrom)
        if (start === -1) break
        ranges.push({ start, end: start + sourceText.length, claim })
        searchFrom = start + 1
      }
      return ranges
    })
    .reduce((acc, range) => {
      addHighlightRange(acc, range)
      return acc
    }, [] as HighlightRange[])
}

function collectTextNodes(root: Node): Text[] {
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT)
  const nodes: Text[] = []
  let node: Node | null
  while ((node = walker.nextNode())) nodes.push(node as Text)
  return nodes
}

function wrapRangeInMark(
  root: Node,
  rangeStart: number,
  rangeEnd: number,
  claim: VisibleClaim
): void {
  let cursor = 0
  // Re-walk per range: earlier ranges may have split text nodes, and the
  // total flat text length is unchanged so range offsets stay valid.
  for (const text of collectTextNodes(root)) {
    const length = text.length
    const nodeStart = cursor
    const nodeEnd = cursor + length
    cursor = nodeEnd
    if (nodeEnd <= rangeStart) continue
    if (nodeStart >= rangeEnd) break
    const parent = text.parentNode
    if (!parent) continue

    const middle = text.splitText(Math.max(0, rangeStart - nodeStart))
    middle.splitText(Math.min(length, rangeEnd - nodeStart) - Math.max(0, rangeStart - nodeStart))

    const mark = text.ownerDocument.createElement('mark')
    mark.className = `${STATUS_COLOR[claim.status] ?? 'bg-gray-400'} rounded px-0.5`
    mark.dataset.claimKey = claim.key
    mark.dataset.claimName = claim.name
    mark.dataset.claimStatus = claim.status
    mark.tabIndex = 0
    parent.replaceChild(mark, middle)
    mark.appendChild(middle)
  }
}

export function injectHighlights(html: string, claims: VisibleClaim[]): string {
  if (typeof document === 'undefined') return html

  const template = document.createElement('template')
  template.innerHTML = html
  const flatText = collectTextNodes(template.content)
    .map((n) => n.textContent ?? '')
    .join('')
  for (const { start, end, claim } of computeHighlightRanges(flatText, claims)) {
    wrapRangeInMark(template.content, start, end, claim)
  }
  return template.innerHTML
}

export function resolveMediaUrls(html: string, year: string): string {
  if (typeof DOMParser === 'undefined') return html
  const baseUrl = `https://owasp.org/www-board-candidates/${year}/`
  const doc = new DOMParser().parseFromString(html, 'text/html')
  for (const el of doc.querySelectorAll('[src]')) {
    try {
      el.setAttribute('src', new URL(el.getAttribute('src') ?? '', baseUrl).href)
    } catch {
      // Leave invalid src values untouched for DOMPurify to handle.
    }
  }
  return doc.body.innerHTML
}

export function renderMarkdown(rawMarkdown: string, year: string): string {
  const md = markdownit({
    breaks: false,
    html: true,
    linkify: true,
    typographer: true,
  }).disable('code')
  const rendered = md.render(rawMarkdown)
  return DOMPurify.sanitize(resolveMediaUrls(rendered, year), {
    ADD_ATTR: ['data-claim-key', 'data-claim-name', 'data-claim-status'],
    ADD_TAGS: ['mark'],
  })
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
  const hideTimerRef = useRef<number | null>(null)
  const [tooltip, setTooltip] = useState<{
    claimKey: string
    claimName: string
    claimStatus: string
    x: number
    y: number
    width: number
  } | null>(null)
  const [selection, setSelection] = useState<{
    text: string
    x: number
    y: number
    width: number
    range: Range
  } | null>(null)

  const filteredClaims = useMemo(
    () => claims.filter((c) => visibleStatuses(isCandidate, isReviewer).includes(c.status)),
    [claims, isCandidate, isReviewer]
  )

  const claimedTexts = useMemo(
    () => filteredClaims.map((c) => c.sourceText).filter(Boolean),
    [filteredClaims]
  )

  const html = useMemo(
    () => injectHighlights(renderMarkdown(rawMarkdown, year), filteredClaims),
    [rawMarkdown, year, filteredClaims]
  )

  const scheduleHide = (delay = 400) => {
    if (hideTimerRef.current) clearTimeout(hideTimerRef.current)
    hideTimerRef.current = window.setTimeout(() => setTooltip(null), delay)
  }

  useEffect(() => {
    const el = containerRef.current
    if (!el) return
    const wrapper = el.querySelector<HTMLElement>('.md-wrapper')

    const showTooltipForMark = (mark: HTMLElement) => {
      if (hideTimerRef.current) clearTimeout(hideTimerRef.current)
      setSelection(null)
      const rect = mark.getBoundingClientRect()
      setTooltip({
        claimKey: mark.dataset.claimKey ?? '',
        claimName: mark.dataset.claimName ?? '',
        claimStatus: mark.dataset.claimStatus ?? '',
        x: rect.left,
        y: rect.top,
        width: rect.width,
      })
    }

    const onMouseOver = (e: MouseEvent) => {
      const target = e.target as HTMLElement
      if (target.closest('[data-tooltip]')) {
        if (hideTimerRef.current) clearTimeout(hideTimerRef.current)
        return
      }
      const mark = target.closest<HTMLElement>('mark[data-claim-key]')
      if (!mark) {
        scheduleHide()
        return
      }
      showTooltipForMark(mark)
    }
    const onMouseLeave = () => scheduleHide()
    const onScroll = () => {
      if (hideTimerRef.current) clearTimeout(hideTimerRef.current)
      setTooltip(null)
      setSelection(null)
    }
    const onMouseUp = (e: MouseEvent) => {
      const target = e.target as HTMLElement
      if (target.closest('[data-tooltip]')) return
      showSelectionPopup()
    }
    const onFocusIn = (e: FocusEvent) => {
      const target = e.target as HTMLElement
      const mark = target.closest<HTMLElement>('mark[data-claim-key]')
      if (!mark) return
      showTooltipForMark(mark)
    }
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key !== 'Enter') return
      const target = e.target as HTMLElement
      const mark = target.closest<HTMLElement>('mark[data-claim-key]')
      if (!mark) return
      const claimKey = mark.dataset.claimKey
      if (!claimKey) return
      e.preventDefault()
      setTooltip(null)
      router.push(`/board/${year}/candidates/${login}/claims/${claimKey}`)
    }
    const onKeyUp = () => {
      showSelectionPopup()
    }
    const showSelectionPopup = () => {
      if (!isCandidate || !wrapper) return
      const sel = window.getSelection()
      if (!sel || sel.isCollapsed || !sel.rangeCount || sel.toString().trim() === '') {
        setSelection(null)
        return
      }
      const range = sel.getRangeAt(0)
      if (!wrapper.contains(range.startContainer) || !wrapper.contains(range.endContainer)) {
        return
      }
      const text = sel.toString().trim()
      if (!text || overlapsExistingClaim(text, claimedTexts)) {
        setSelection(null)
        return
      }
      const rect = range.getBoundingClientRect()
      setTooltip(null)
      setSelection({ text, x: rect.left, y: rect.top, width: rect.width, range })
    }

    el.addEventListener('mouseover', onMouseOver)
    el.addEventListener('mouseleave', onMouseLeave)
    el.addEventListener('mouseup', onMouseUp)
    el.addEventListener('focusin', onFocusIn)
    el.addEventListener('keydown', onKeyDown)
    el.addEventListener('keyup', onKeyUp)
    window.addEventListener('scroll', onScroll, true)
    return () => {
      el.removeEventListener('mouseover', onMouseOver)
      el.removeEventListener('mouseleave', onMouseLeave)
      el.removeEventListener('mouseup', onMouseUp)
      el.removeEventListener('focusin', onFocusIn)
      el.removeEventListener('keydown', onKeyDown)
      el.removeEventListener('keyup', onKeyUp)
      window.removeEventListener('scroll', onScroll, true)
      if (hideTimerRef.current) clearTimeout(hideTimerRef.current)
    }
  }, [isCandidate, claimedTexts, login, router, year])

  const handleTooltipEnter = () => {
    if (hideTimerRef.current) clearTimeout(hideTimerRef.current)
  }
  const handleTooltipLeave = () => scheduleHide()
  const handleTooltipClick = () => {
    if (!tooltip) return
    setTooltip(null)
    router.push(`/board/${year}/candidates/${login}/claims/${tooltip.claimKey}`)
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
      <div
        className="md-wrapper rounded-xl bg-white p-6 text-gray-600"
        dangerouslySetInnerHTML={{ __html: html }}
      />
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
              className={`h-2.5 w-2.5 shrink-0 rounded-full ${STATUS_DOT[tooltip.claimStatus as ClaimStatusEnum] ?? 'bg-gray-400'}`}
            />
            <span className="truncate font-semibold">{tooltip.claimName || 'Claim'}</span>
          </span>
          <span className="mt-1 flex items-center gap-1 text-gray-500 dark:text-gray-400">
            <span>{upperFirst(toLower(tooltip.claimStatus))}</span>
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
      className="block w-56 cursor-pointer rounded-lg border border-gray-300 bg-white px-3 py-2 text-left text-xs text-gray-800 shadow-xl transition-colors hover:bg-slate-100 dark:border-slate-600 dark:bg-slate-800 dark:text-white dark:hover:bg-slate-700"
    >
      {children}
    </button>
    <div className="flex justify-center">
      <div className="h-2 w-2 -translate-y-1 rotate-45 border-r border-b border-gray-300 bg-white dark:border-slate-600 dark:bg-slate-800" />
    </div>
  </div>
)

export default AnnotatedProfile
