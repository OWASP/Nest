import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import { ClaimStatusEnum } from 'types/__generated__/graphql'
import AnnotatedProfile, {
  computeHighlightRanges,
  overlapsExistingClaim,
  resolveMediaUrl,
  visibleStatuses,
} from 'components/AnnotatedProfile'
import type { VisibleClaim } from 'components/AnnotatedProfile'

const claim = (overrides: Partial<VisibleClaim> = {}): VisibleClaim => ({
  id: 'claim-1',
  key: 'claim-1',
  name: 'Claim One',
  sourceText: 'OWASP projects',
  status: ClaimStatusEnum.Approved,
  ...overrides,
})

describe('visibleStatuses', () => {
  it('returns approved and rejected for public viewers', () => {
    expect(visibleStatuses(false, false)).toEqual([
      ClaimStatusEnum.Approved,
      ClaimStatusEnum.Rejected,
    ])
  })

  it('adds submitted for reviewers', () => {
    expect(visibleStatuses(false, true)).toEqual([
      ClaimStatusEnum.Approved,
      ClaimStatusEnum.Rejected,
      ClaimStatusEnum.Submitted,
    ])
  })

  it('adds submitted and draft for candidates', () => {
    expect(visibleStatuses(true, false)).toEqual([
      ClaimStatusEnum.Approved,
      ClaimStatusEnum.Rejected,
      ClaimStatusEnum.Submitted,
      ClaimStatusEnum.Draft,
    ])
  })

  it('never includes withdrawn', () => {
    for (const [isCandidate, isReviewer] of [
      [false, false],
      [false, true],
      [true, false],
      [true, true],
    ]) {
      expect(visibleStatuses(isCandidate, isReviewer)).not.toContain(ClaimStatusEnum.Withdrawn)
    }
  })
})

describe('overlapsExistingClaim', () => {
  it('returns true when the selection equals a claimed text', () => {
    expect(overlapsExistingClaim('OWASP projects', ['OWASP projects'])).toBe(true)
  })

  it('returns true when the selection contains a claimed text', () => {
    expect(overlapsExistingClaim('I support OWASP projects daily', ['OWASP projects'])).toBe(true)
  })

  it('returns true when the selection is contained by a claimed text', () => {
    expect(overlapsExistingClaim('OWASP projects', ['support OWASP projects daily'])).toBe(true)
  })

  it('returns false when there is no overlap', () => {
    expect(overlapsExistingClaim('leadership experience', ['OWASP projects'])).toBe(false)
  })

  it('returns false for an empty selection', () => {
    expect(overlapsExistingClaim('   ', ['OWASP projects'])).toBe(false)
  })

  it('ignores empty claimed texts', () => {
    expect(overlapsExistingClaim('OWASP projects', ['', '   '])).toBe(false)
  })

  it('trims whitespace on both sides', () => {
    expect(overlapsExistingClaim('  OWASP projects  ', ['OWASP projects'])).toBe(true)
  })
})

describe('resolveMediaUrl', () => {
  it('resolves a relative src against the board candidates page base', () => {
    expect(resolveMediaUrl('../assets/images/arkid15r/photo.jpg', '2025')).toBe(
      'https://owasp.org/www-board-candidates/assets/images/arkid15r/photo.jpg'
    )
  })

  it('resolves a root-relative src against the base', () => {
    expect(resolveMediaUrl('/www-board-candidates/assets/images/a.png', '2025')).toBe(
      'https://owasp.org/www-board-candidates/assets/images/a.png'
    )
  })

  it('resolves a same-directory src into the year subpath', () => {
    expect(resolveMediaUrl('b.mp4', '2025')).toBe(
      'https://owasp.org/www-board-candidates/2025/b.mp4'
    )
  })

  it('leaves absolute external URLs untouched', () => {
    const src = 'https://raw.githubusercontent.com/org/repo/a.png'
    expect(resolveMediaUrl(src, '2025')).toBe(src)
  })

  it('leaves invalid src values untouched', () => {
    expect(resolveMediaUrl('http://[invalid', '2025')).toBe('http://[invalid')
  })
})

describe('computeHighlightRanges', () => {
  it('returns an empty list when no source text matches', () => {
    expect(computeHighlightRanges('Hi OWASP Community!', [claim({ sourceText: 'nope' })])).toEqual(
      []
    )
  })

  it('finds all occurrences of a source text', () => {
    const ranges = computeHighlightRanges('OWASP projects are great. OWASP projects matter.', [
      claim(),
    ])
    expect(ranges).toHaveLength(2)
  })

  it('gives approved higher priority than draft on an identical overlap', () => {
    const draft = claim({ key: 'draft', status: ClaimStatusEnum.Draft })
    const approved = claim({ key: 'approved', status: ClaimStatusEnum.Approved })
    const [range] = computeHighlightRanges('OWASP projects are open source.', [draft, approved])
    expect(range.claim.key).toBe('approved')
  })

  it('drops a partially-overlapping range instead of splitting either', () => {
    const first = claim({ key: 'first', sourceText: 'OWASP proj' })
    const second = claim({ key: 'second', sourceText: 'projects are' })
    const ranges = computeHighlightRanges('OWASP projects are great.', [first, second])
    expect(ranges).toHaveLength(1)
  })

  it('keeps a lower-priority draft range over a partial approved overlap', () => {
    const draft = claim({
      key: 'draft',
      sourceText: 'officer',
      status: ClaimStatusEnum.Draft,
    })
    const approved = claim({
      key: 'approved',
      sourceText: 'officer leads',
    })
    const ranges = computeHighlightRanges('The officer leads the squad.', [draft, approved])
    expect(ranges).toHaveLength(1)
    expect(ranges[0].claim.key).toBe('draft')
  })

  it('keeps both non-overlapping ranges', () => {
    const draft = claim({
      key: 'draft',
      sourceText: 'OWASP projects',
      status: ClaimStatusEnum.Draft,
    })
    const approved = claim({ key: 'approved', sourceText: 'leadership' })
    const ranges = computeHighlightRanges('OWASP projects and leadership', [draft, approved])
    expect(ranges.map((r) => r.claim.key).sort()).toEqual(['approved', 'draft'])
  })

  it('skips an inner range fully contained in a previously added one', () => {
    const outer = claim({ key: 'outer', sourceText: 'OWASP projects' })
    const inner = claim({ key: 'inner', sourceText: 'projects' })
    const ranges = computeHighlightRanges('OWASP projects matter.', [outer, inner])
    expect(ranges).toHaveLength(1)
    expect(ranges[0].claim.key).toBe('outer')
  })

  it('matches source text that spans typographer-transformed curly quotes', () => {
    const ranges = computeHighlightRanges('He said “Welcome home” loudly.', [
      claim({ key: 'quoted', sourceText: 'He said "Welcome home" loudly.' }),
    ])
    expect(ranges).toHaveLength(1)
    expect(ranges[0].claim.key).toBe('quoted')
  })

  it('ignores claims with empty source text', () => {
    expect(computeHighlightRanges('plain text', [claim({ sourceText: '' })])).toEqual([])
  })
})

describe('AnnotatedProfile component', () => {
  const mockPush = jest.fn()

  const renderProfile = (
    props: {
      claims?: VisibleClaim[]
      isCandidate?: boolean
      isReviewer?: boolean
      login?: string
      rawMarkdown?: string
      year?: string
    } = {}
  ) =>
    render(
      <AnnotatedProfile
        claims={props.claims ?? []}
        isCandidate={props.isCandidate ?? false}
        isReviewer={props.isReviewer ?? false}
        login={props.login ?? 'arkid15r'}
        rawMarkdown={props.rawMarkdown ?? '### About Me\nHi OWASP Community!'}
        year={props.year ?? '2025'}
      />
    )

  beforeEach(() => {
    jest.useFakeTimers()
    mockPush.mockClear()
    ;(useRouter as jest.Mock).mockReturnValue({ push: mockPush })
  })

  afterEach(() => {
    cleanup()
    jest.restoreAllMocks()
    jest.useRealTimers()
  })

  it('renders the raw markdown as HTML', () => {
    renderProfile({ rawMarkdown: 'Hello **bold** world' })
    expect(screen.getByText(/Hello/)).toBeInTheDocument()
    expect(screen.getByText('bold')).toBeInTheDocument()
  })

  it('renders markdown content when no claims exist', () => {
    const { container } = renderProfile({ rawMarkdown: 'Hi OWASP Community!' })
    expect(container.textContent).toContain('Hi OWASP Community!')
  })

  it('resolves relative image src against the board candidates base', () => {
    const { container } = renderProfile({
      rawMarkdown: '![photo](../assets/images/photo.png)',
    })
    const img = container.querySelector('img')
    expect(img?.getAttribute('src')).toBe(
      'https://owasp.org/www-board-candidates/assets/images/photo.png'
    )
  })

  it('renders visible claims as mark elements with dataset attributes', () => {
    const { container } = renderProfile({
      claims: [claim()],
      rawMarkdown: 'OWASP projects are great.',
    })
    const mark = container.querySelector('[data-claim-key="claim-1"]')
    expect(mark).not.toBeNull()
    expect(mark?.getAttribute('data-claim-name')).toBe('Claim One')
    expect(mark?.getAttribute('data-claim-status')).toBe('APPROVED')
  })

  it('filters out claims whose status is not visible', () => {
    const { container } = renderProfile({
      claims: [claim({ status: ClaimStatusEnum.Withdrawn })],
      rawMarkdown: 'OWASP projects are great.',
    })
    expect(container.querySelector('[data-claim-key]')).toBeNull()
  })

  it('does not show the tooltip until a highlight is hovered', () => {
    const { container } = renderProfile({ claims: [claim()], rawMarkdown: 'OWASP projects.' })
    expect(container.querySelector('[data-tooltip]')).toBeNull()
  })

  it('shows the tooltip when hovering a highlight', () => {
    const { container } = renderProfile({ claims: [claim()], rawMarkdown: 'OWASP projects.' })
    const mark = container.querySelector('[data-claim-key]')
    expect(mark).not.toBeNull()
    fireEvent.mouseOver(mark as Element)
    expect(screen.getByText('Claim One')).toBeInTheDocument()
    expect(screen.getByText('Approved')).toBeInTheDocument()
  })

  it('keeps the tooltip open while hovering it', () => {
    const { container } = renderProfile({ claims: [claim()], rawMarkdown: 'OWASP projects.' })
    const mark = container.querySelector('[data-claim-key]')
    fireEvent.mouseOver(mark as Element)
    const tooltip = container.querySelector('[data-tooltip]')
    expect(tooltip).not.toBeNull()
    fireEvent.mouseEnter(tooltip as Element)
    act(() => {
      jest.advanceTimersByTime(500)
    })
    expect(container.querySelector('[data-tooltip]')).not.toBeNull()
  })

  it('hides the tooltip when the mouse leaves the profile', () => {
    const { container } = renderProfile({ claims: [claim()], rawMarkdown: 'OWASP projects.' })
    const mark = container.querySelector('[data-claim-key]')
    fireEvent.mouseOver(mark as Element)
    expect(screen.getByText('Claim One')).toBeInTheDocument()
    fireEvent.mouseLeave(container.querySelector('.relative') as Element)
    act(() => {
      jest.advanceTimersByTime(500)
    })
    expect(container.querySelector('[data-tooltip]')).toBeNull()
  })

  it('hides the tooltip when the page is scrolled', () => {
    const { container } = renderProfile({ claims: [claim()], rawMarkdown: 'OWASP projects.' })
    const mark = container.querySelector('[data-claim-key]')
    fireEvent.mouseOver(mark as Element)
    expect(screen.getByText('Claim One')).toBeInTheDocument()
    fireEvent.scroll(window)
    expect(container.querySelector('[data-tooltip]')).toBeNull()
  })

  it('navigates to the claim page when the tooltip is clicked', () => {
    const { container } = renderProfile({
      claims: [claim()],
      login: 'arkid15r',
      rawMarkdown: 'OWASP projects.',
      year: '2025',
    })
    const mark = container.querySelector('[data-claim-key]')
    fireEvent.mouseOver(mark as Element)
    const tooltipButton = container.querySelector('[data-tooltip] button')
    fireEvent.click(tooltipButton as Element)
    expect(mockPush).toHaveBeenCalledWith('/board/2025/candidates/arkid15r/claims/claim-1')
    expect(container.querySelector('[data-tooltip]')).toBeNull()
  })

  describe('highlight-to-claim selection popup', () => {
    const mockSelection = (text: string) => {
      const wrapperNode = () => document.querySelector('.md-wrapper') as Node | null
      jest.spyOn(window, 'getSelection').mockReturnValue({
        isCollapsed: false,
        rangeCount: 1,
        removeAllRanges: () => {},
        addRange: () => {},
        toString: () => text,
        getRangeAt: () => ({
          startContainer: wrapperNode(),
          endContainer: wrapperNode(),
          getBoundingClientRect: () => ({
            left: 100,
            right: 300,
            top: 50,
            bottom: 70,
            width: 200,
            height: 20,
            x: 100,
            y: 50,
            toJSON: () => ({}),
          }),
        }),
      } as unknown as Selection)
    }

    const mouseUpOnProfile = (container: HTMLElement) => {
      const wrapper = container.querySelector('.md-wrapper')
      fireEvent.mouseUp(wrapper as Element)
    }

    it('shows the Create Claim popup for the owner on a non-overlapping selection', () => {
      mockSelection('leadership experience')
      const { container } = renderProfile({ isCandidate: true })
      mouseUpOnProfile(container)
      expect(screen.getByText('Create Claim')).toBeInTheDocument()
    })

    it('does not show the popup for a non-owner', () => {
      mockSelection('leadership experience')
      const { container } = renderProfile({ isCandidate: false })
      mouseUpOnProfile(container)
      expect(screen.queryByText('Create Claim')).not.toBeInTheDocument()
    })

    it('does not show the popup when the selection overlaps an existing claim', () => {
      mockSelection('OWASP projects are great')
      const { container } = renderProfile({
        claims: [claim()],
        isCandidate: true,
        rawMarkdown: 'OWASP projects are great.',
      })
      mouseUpOnProfile(container)
      expect(screen.queryByText('Create Claim')).not.toBeInTheDocument()
    })

    it('does not show the popup for an empty selection', () => {
      mockSelection('   ')
      const { container } = renderProfile({ isCandidate: true })
      mouseUpOnProfile(container)
      expect(screen.queryByText('Create Claim')).not.toBeInTheDocument()
    })

    it('navigates to the create claim page with the encoded source text', () => {
      mockSelection('leadership experience')
      const { container } = renderProfile({
        isCandidate: true,
        login: 'arkid15r',
        year: '2025',
      })
      mouseUpOnProfile(container)
      fireEvent.click(screen.getByText('Create Claim'))
      expect(mockPush).toHaveBeenCalledWith(
        '/board/2025/candidates/arkid15r/claims/create?sourceText=leadership%20experience'
      )
    })
  })
})
