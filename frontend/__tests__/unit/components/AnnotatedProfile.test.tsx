import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import { ClaimStatusEnum } from 'types/__generated__/graphql'
import AnnotatedProfile, {
  escapeAttr,
  injectHighlights,
  normalizeIndentedHtml,
  overlapsExistingClaim,
  renderMarkdown,
  resolveMediaUrls,
  visibleStatuses,
} from 'components/AnnotatedProfile'
import type { VisibleClaim } from 'components/AnnotatedProfile'

jest.mock('dompurify', () => ({
  sanitize: (html: string) => html,
}))

jest.mock('markdown-it', () => {
  const markdownIt = jest.requireActual<typeof import('markdown-it')>('markdown-it')
  return { __esModule: true, default: markdownIt }
})

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

describe('escapeAttr', () => {
  it('escapes ampersands, quotes, and angle brackets', () => {
    expect(escapeAttr('a&b"c<d>e')).toBe('a&amp;b&quot;c&lt;d&gt;e')
  })

  it('leaves plain text unchanged', () => {
    expect(escapeAttr('plain text')).toBe('plain text')
  })
})

describe('overlapsExistingClaim', () => {
  it('returns false when the selection equals a claimed text', () => {
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

describe('resolveMediaUrls', () => {
  it('resolves a relative src against the board candidates page base', () => {
    const html = '<img src="../assets/images/arkid15r/photo.jpg" alt="Arkadii Yakovets">'
    expect(resolveMediaUrls(html, '2025')).toBe(
      '<img src="https://owasp.org/www-board-candidates/assets/images/arkid15r/photo.jpg" alt="Arkadii Yakovets">'
    )
  })

  it('resolves every media tag with a src attribute', () => {
    const html = '<img src="/www-board-candidates/assets/images/a.png"><source src="b.mp4">'
    const resolved = resolveMediaUrls(html, '2025')
    expect(resolved).toContain('https://owasp.org/www-board-candidates/assets/images/a.png')
    expect(resolved).toContain('https://owasp.org/www-board-candidates/2025/b.mp4')
  })

  it('leaves absolute external URLs untouched', () => {
    const html = '<img src="https://raw.githubusercontent.com/org/repo/a.png">'
    expect(resolveMediaUrls(html, '2025')).toBe(html)
  })

  it('leaves invalid src values untouched', () => {
    const html = '<img src="http://[invalid">'
    expect(resolveMediaUrls(html, '2025')).toBe(html)
  })
})

describe('renderMarkdown', () => {
  it('splits paragraphs on blank lines', () => {
    expect(renderMarkdown('one\n\ntwo', [], '2025')).toBe('<p>one</p>\n<p>two</p>\n')
  })

  it('renders headings and emphasis', () => {
    expect(renderMarkdown('### Title\n\n**bold** text', [], '2025')).toBe(
      '<h3>Title</h3>\n<p><strong>bold</strong> text</p>\n'
    )
  })

  it('renders markdown links', () => {
    expect(renderMarkdown('[OWASP](https://owasp.org)', [], '2025')).toBe(
      '<p><a href="https://owasp.org">OWASP</a></p>\n'
    )
  })

  it('resolves relative image paths to the board candidates site', () => {
    expect(renderMarkdown('<img src="../assets/images/photo.png" alt="photo">', [], '2025')).toBe(
      '<img src="https://owasp.org/www-board-candidates/assets/images/photo.png" alt="photo">'
    )
  })

  it('renders indented block-level html as markup instead of a code block', () => {
    const markdown = ['    <div>', '      Global Engagement', '    </div>'].join('\n')
    const result = renderMarkdown(markdown, [], '2025')
    expect(result).not.toContain('<pre>')
    expect(result).toContain('<div>')
  })

  it('wraps matching source text in a mark tag', () => {
    const result = renderMarkdown('I support OWASP projects and more.', [claim()], '2025')
    expect(result).toContain('<mark class="bg-green-200 text-green-950 rounded px-0.5"')
    expect(result).toContain('data-claim-key="claim-1"')
    expect(result).toContain('data-claim-name="Claim One"')
    expect(result).toContain('data-claim-status="APPROVED"')
  })
})

describe('normalizeIndentedHtml', () => {
  it('de-indents only lines that start with a tag', () => {
    const markdown = ['    <div>', '      nested content', '    </div>', '    plain text'].join(
      '\n'
    )
    expect(normalizeIndentedHtml(markdown)).toBe(
      ['<div>', '      nested content', '</div>', '    plain text'].join('\n')
    )
  })

  it('leaves genuine indented code blocks untouched', () => {
    const markdown = ['Before.', '', '    def hello():', '        print("hi")', '', 'After.'].join(
      '\n'
    )
    expect(normalizeIndentedHtml(markdown)).toBe(markdown)
  })

  it('does not de-indent lines indented more than 4 spaces', () => {
    expect(normalizeIndentedHtml('        <span>deep</span>')).toBe('        <span>deep</span>')
  })

  it('leaves unindented content and empty strings unchanged', () => {
    expect(normalizeIndentedHtml('<div>\n  <p>Hello</p>\n</div>')).toBe(
      '<div>\n  <p>Hello</p>\n</div>'
    )
    expect(normalizeIndentedHtml('')).toBe('')
  })
})

describe('injectHighlights', () => {
  it('returns the markdown unchanged when there are no claims', () => {
    const markdown = 'Hi OWASP Community!'
    expect(injectHighlights(markdown, [])).toBe(markdown)
  })

  it('returns the markdown unchanged when no source text matches', () => {
    const markdown = 'Hi OWASP Community!'
    expect(injectHighlights(markdown, [claim({ sourceText: 'no match here' })])).toBe(markdown)
  })

  it('wraps a matching occurrence in a mark tag with dataset attributes', () => {
    const markdown = 'I support OWASP projects and more.'
    expect(injectHighlights(markdown, [claim()])).toBe(
      'I support <mark class="bg-green-200 text-green-950 rounded px-0.5" data-claim-key="claim-1" ' +
        'data-claim-name="Claim One" data-claim-status="APPROVED">OWASP projects</mark> and more.'
    )
  })

  it('preserves text before, between, and after highlights', () => {
    const markdown = 'aaa OWASP projects bbb OWASP projects ccc'
    const result = injectHighlights(markdown, [claim()])
    expect(result.startsWith('aaa ')).toBe(true)
    expect(result.endsWith(' ccc')).toBe(true)
    expect(result.match(/<mark/g)).toHaveLength(2)
  })

  it('highlights all occurrences of a source text', () => {
    const markdown = 'OWASP projects are great. OWASP projects matter.'
    expect(injectHighlights(markdown, [claim()]).match(/<mark/g)).toHaveLength(2)
  })

  it('gives approved higher priority than draft on overlap', () => {
    const markdown = 'OWASP projects are open source.'
    const draft = claim({ key: 'draft', name: 'Draft', status: ClaimStatusEnum.Draft })
    const approved = claim({ key: 'approved', name: 'Approved', status: ClaimStatusEnum.Approved })
    const result = injectHighlights(markdown, [draft, approved])
    expect(result).toContain('data-claim-key="approved"')
    expect(result).not.toContain('data-claim-key="draft"')
  })

  it('does not create partially overlapping partial marks', () => {
    const markdown = 'OWASP projects are great.'
    const first = claim({ key: 'first', sourceText: 'OWASP proj' })
    const second = claim({ key: 'second', sourceText: 'projects are' })
    expect(injectHighlights(markdown, [first, second]).match(/<mark/g)).toHaveLength(1)
  })

  it('keeps a lower-priority draft range over a partial approved overlap', () => {
    const markdown = 'The officer leads the squad.'
    const draft = claim({
      key: 'draft',
      name: 'Draft',
      sourceText: 'officer',
      status: ClaimStatusEnum.Draft,
    })
    const approved = claim({
      key: 'approved',
      name: 'Approved',
      sourceText: 'officer leads',
    })
    const result = injectHighlights(markdown, [draft, approved])
    expect(result).toContain('data-claim-key="draft"')
    expect(result).not.toContain('data-claim-key="approved"')
    expect(result.match(/<mark/g)).toHaveLength(1)
  })

  it('keeps both non-overlapping ranges of different priorities', () => {
    const markdown = 'OWASP projects and leadership'
    const draft = claim({
      key: 'draft',
      sourceText: 'OWASP projects',
      status: ClaimStatusEnum.Draft,
    })
    const approved = claim({ key: 'approved', sourceText: 'leadership' })
    const result = injectHighlights(markdown, [draft, approved])
    expect(result).toContain('data-claim-key="draft"')
    expect(result).toContain('data-claim-key="approved"')
  })

  it('skips an inner range fully contained in a previously added one', () => {
    const markdown = 'OWASP projects matter.'
    const outer = claim({ key: 'outer', sourceText: 'OWASP projects' })
    const inner = claim({ key: 'inner', sourceText: 'projects' })
    const result = injectHighlights(markdown, [outer, inner])
    expect(result.match(/<mark/g)).toHaveLength(1)
    expect(result).toContain('data-claim-key="outer"')
    expect(result).not.toContain('data-claim-key="inner"')
  })

  it('escapes special characters in attribute values', () => {
    const special = claim({ key: 'a&b"c', name: 'Name with "quotes"' })
    const result = injectHighlights('OWASP projects', [special])
    expect(result).toContain('data-claim-key="a&amp;b&quot;c"')
    expect(result).toContain('data-claim-name="Name with &quot;quotes&quot;"')
  })

  it('ignores empty source text', () => {
    expect(injectHighlights('plain text content', [claim({ sourceText: '' })])).toBe(
      'plain text content'
    )
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

  it('renders visible claims as mark elements with dataset attributes', () => {
    const { container } = renderProfile({
      claims: [claim()],
      rawMarkdown: 'OWASP projects are great.',
    })
    const mark = container.querySelector('mark[data-claim-key="claim-1"]')
    expect(mark).not.toBeNull()
    expect(mark?.getAttribute('data-claim-name')).toBe('Claim One')
    expect(mark?.getAttribute('data-claim-status')).toBe('APPROVED')
  })

  it('filters out claims whose status is not visible', () => {
    const { container } = renderProfile({
      claims: [claim({ status: ClaimStatusEnum.Withdrawn })],
      rawMarkdown: 'OWASP projects are great.',
    })
    expect(container.querySelector('mark[data-claim-key]')).toBeNull()
  })

  it('does not show the tooltip until a highlight is hovered', () => {
    const { container } = renderProfile({ claims: [claim()], rawMarkdown: 'OWASP projects.' })
    expect(container.querySelector('[data-tooltip]')).toBeNull()
  })

  it('shows the tooltip when hovering a highlight', () => {
    const { container } = renderProfile({ claims: [claim()], rawMarkdown: 'OWASP projects.' })
    const mark = container.querySelector('mark[data-claim-key]')
    expect(mark).not.toBeNull()
    fireEvent.mouseOver(mark as Element)
    expect(screen.getByText('Claim One')).toBeInTheDocument()
    expect(screen.getByText('Approved')).toBeInTheDocument()
  })

  it('keeps the tooltip open while hovering it', () => {
    const { container } = renderProfile({ claims: [claim()], rawMarkdown: 'OWASP projects.' })
    const mark = container.querySelector('mark[data-claim-key]')
    fireEvent.mouseOver(mark as Element)
    const tooltip = container.querySelector('[data-tooltip]')
    expect(tooltip).not.toBeNull()
    fireEvent.mouseOver(tooltip as Element)
    act(() => {
      jest.advanceTimersByTime(500)
    })
    expect(container.querySelector('[data-tooltip]')).not.toBeNull()
  })

  it('hides the tooltip when the mouse leaves the profile', () => {
    const { container } = renderProfile({ claims: [claim()], rawMarkdown: 'OWASP projects.' })
    const mark = container.querySelector('mark[data-claim-key]')
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
    const mark = container.querySelector('mark[data-claim-key]')
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
    const mark = container.querySelector('mark[data-claim-key]')
    fireEvent.mouseOver(mark as Element)
    const button = screen.getByRole('button')
    fireEvent.click(button)
    expect(mockPush).toHaveBeenCalledWith('/board/2025/candidates/arkid15r/claims/claim-1')
    expect(container.querySelector('[data-tooltip]')).toBeNull()
  })

  describe('highlight-to-claim selection popup', () => {
    const mockSelection = (text: string) => {
      jest.spyOn(window, 'getSelection').mockReturnValue({
        isCollapsed: false,
        rangeCount: 1,
        removeAllRanges: () => {},
        addRange: () => {},
        toString: () => text,
        getRangeAt: () => ({
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
