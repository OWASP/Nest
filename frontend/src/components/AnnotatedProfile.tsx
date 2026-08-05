'use client'

import DOMPurify from 'dompurify'
import { upperFirst, toLower } from 'lodash'
import markdownit from 'markdown-it'
import { useRouter } from 'next/navigation'
import { useEffect, useMemo, useRef, useState } from 'react'
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

export function escapeAttr(value: string): string {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('"', '&quot;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
}

type HighlightRange = {
  start: number
  end: number
  claim: VisibleClaim
}

function toHighlightRanges(markdown: string, claim: VisibleClaim): HighlightRange[] {
  if (!claim.sourceText) return []

  const ranges: HighlightRange[] = []
  let searchFrom = 0
  while (searchFrom < markdown.length) {
    const start = markdown.indexOf(claim.sourceText, searchFrom)
    if (start === -1) break
    ranges.push({ start, end: start + claim.sourceText.length, claim })
    searchFrom = start + 1
  }
  return ranges
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

export function injectHighlights(markdown: string, claims: VisibleClaim[]): string {
  // Iterate lowest priority first so that a higher-priority claim replaces an
  // identical range, while a partially overlapping one is skipped entirely.
  const ranges = claims
    .filter((c) => (PRIORITY_ORDER as readonly ClaimStatusEnum[]).includes(c.status))
    .sort(
      (a, b) =>
        (PRIORITY_ORDER as readonly ClaimStatusEnum[]).indexOf(a.status) -
        (PRIORITY_ORDER as readonly ClaimStatusEnum[]).indexOf(b.status)
    )
    .flatMap((claim) => toHighlightRanges(markdown, claim))
    .reduce((acc, range) => {
      addHighlightRange(acc, range)
      return acc
    }, [] as HighlightRange[])

  ranges.sort((a, b) => a.start - b.start)

  const parts: string[] = []
  let cursor = 0
  for (const { start, end, claim } of ranges) {
    if (start > cursor) parts.push(markdown.slice(cursor, start))
    parts.push(renderSegment(markdown.slice(start, end), claim))
    cursor = end
  }
  if (cursor < markdown.length) parts.push(markdown.slice(cursor))
  return parts.join('')
}

function renderSegment(text: string, claim: VisibleClaim | null): string {
  if (!claim) return text
  return (
    `<mark class="${STATUS_COLOR[claim.status]} rounded px-0.5" ` +
    `data-claim-key="${escapeAttr(claim.key)}" ` +
    `data-claim-name="${escapeAttr(claim.name)}" ` +
    `data-claim-status="${escapeAttr(claim.status)}">${text}</mark>`
  )
}

export function resolveMediaUrls(html: string, year: string): string {
  const baseUrl = `https://owasp.org/www-board-candidates/${year}/`
  const doc = new DOMParser().parseFromString(html, 'text/html')
  for (const element of Array.from(doc.querySelectorAll('[src]'))) {
    try {
      element.setAttribute('src', new URL(element.getAttribute('src') ?? '', baseUrl).href)
    } catch {
      // Leave invalid src values untouched for DOMPurify to handle.
    }
  }
  return doc.body.innerHTML
}

// CommonMark treats 4+ space indented lines as code.
export function normalizeIndentedHtml(markdown: string): string {
  return markdown.replace(/^ {4}(?=<)/gm, '')
}

export function renderMarkdown(rawMarkdown: string, claims: VisibleClaim[], year: string): string {
  const md = markdownit({
    breaks: false,
    html: true,
    linkify: true,
    typographer: true,
  })
  const annotated = injectHighlights(normalizeIndentedHtml(rawMarkdown), claims)
  return DOMPurify.sanitize(resolveMediaUrls(md.render(annotated), year), {
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
    () => renderMarkdown(rawMarkdown, filteredClaims, year),
    [rawMarkdown, filteredClaims, year]
  )

  const scheduleHide = (delay = 400) => {
    if (hideTimerRef.current) clearTimeout(hideTimerRef.current)
    hideTimerRef.current = window.setTimeout(() => setTooltip(null), delay)
  }

  useEffect(() => {
    const el = containerRef.current
    if (!el) return

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
    const onMouseLeave = () => scheduleHide()
    const onScroll = () => {
      if (hideTimerRef.current) clearTimeout(hideTimerRef.current)
      setTooltip(null)
      setSelection(null)
    }
    const onMouseUp = (e: MouseEvent) => {
      if (!isCandidate) return
      const target = e.target as HTMLElement
      if (target.closest('[data-tooltip]')) return
      const sel = window.getSelection()
      if (!sel || sel.isCollapsed || !sel.rangeCount || sel.toString().trim() === '') {
        setSelection(null)
        return
      }
      const text = sel.toString().trim()
      if (!text || overlapsExistingClaim(text, claimedTexts)) {
        setSelection(null)
        return
      }
      const range = sel.getRangeAt(0)
      const rect = range.getBoundingClientRect()
      setTooltip(null)
      setSelection({ text, x: rect.left, y: rect.top, width: rect.width, range })
    }

    el.addEventListener('mouseover', onMouseOver)
    el.addEventListener('mouseleave', onMouseLeave)
    el.addEventListener('mouseup', onMouseUp)
    window.addEventListener('scroll', onScroll, true)
    return () => {
      el.removeEventListener('mouseover', onMouseOver)
      el.removeEventListener('mouseleave', onMouseLeave)
      el.removeEventListener('mouseup', onMouseUp)
      window.removeEventListener('scroll', onScroll, true)
      if (hideTimerRef.current) clearTimeout(hideTimerRef.current)
    }
  }, [html, isCandidate, claimedTexts])

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
        <div
          data-tooltip
          className="fixed z-50 -translate-x-1/2 -translate-y-full pb-2"
          style={{
            left: Math.min(
              Math.max(selection.x + selection.width / 2, 112),
              window.innerWidth - 112
            ),
            top: selection.y,
          }}
        >
          <button
            type="button"
            onClick={handleCreateClaimClick}
            className="block w-56 cursor-pointer rounded-lg border border-gray-300 bg-white px-3 py-2 text-left text-xs text-gray-800 shadow-xl transition-colors hover:bg-slate-100 dark:border-slate-600 dark:bg-slate-800 dark:text-white dark:hover:bg-slate-700"
          >
            <span className="flex items-center gap-2">
              <FaPlus className="h-3 w-3" aria-hidden="true" />
              <span className="truncate font-semibold">Create Claim</span>
            </span>
            <span className="mt-1 line-clamp-2 text-gray-500 dark:text-gray-400">
              "{selection.text}"
            </span>
          </button>
          <div className="flex justify-center">
            <div className="h-2 w-2 -translate-y-1 rotate-45 border-r border-b border-gray-300 bg-white dark:border-slate-600 dark:bg-slate-800" />
          </div>
        </div>
      )}
      {tooltip && (
        <div
          data-tooltip
          className="fixed z-50"
          style={{
            left: Math.min(Math.max(tooltip.x + tooltip.width / 2, 112), window.innerWidth - 112),
            top: tooltip.y - 56,
            transform: 'translateX(-50%)',
          }}
          onMouseEnter={handleTooltipEnter}
          onMouseLeave={handleTooltipLeave}
        >
          <button
            type="button"
            onClick={handleTooltipClick}
            className="block w-56 cursor-pointer rounded-lg border border-gray-300 bg-white px-3 py-2 text-left text-xs text-gray-800 shadow-xl transition-colors hover:bg-slate-100 dark:border-slate-600 dark:bg-slate-800 dark:text-white dark:hover:bg-slate-700"
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
          </button>
          <div className="flex justify-center">
            <div className="h-2 w-2 -translate-y-1 rotate-45 border-r border-b border-gray-300 bg-white dark:border-slate-600 dark:bg-slate-800" />
          </div>
        </div>
      )}
    </div>
  )
}

export default AnnotatedProfile
