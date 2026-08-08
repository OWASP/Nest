import { fireEvent, render, screen } from '@testing-library/react'
import { useProfileSelection } from 'hooks/useProfileSelection'
import { useRouter } from 'next/navigation'
import React from 'react'

import { ClaimStatusEnum } from 'types/__generated__/graphql'
import AnnotatedProfile from 'components/AnnotatedProfile'

jest.mock('hooks/useProfileSelection', () => ({
  useProfileSelection: jest.fn(() => null),
}))

jest.mock(
  'components/ClaimHighlight',
  () =>
    function MockClaimHighlight({
      children,
      'data-claim-key': claimKey,
      'data-claim-name': claimName,
      'data-claim-status': claimStatus,
      ...rest
    }: {
      children?: React.ReactNode
      'data-claim-key'?: string
      'data-claim-name'?: string
      'data-claim-status'?: string
    } & Record<string, unknown>) {
      if (!claimKey) return <span {...rest}>{children}</span>
      return (
        <span
          data-testid="claim-highlight"
          data-claim-highlight="true"
          data-claim-key={claimKey}
          data-claim-name={claimName}
          data-claim-status={claimStatus}
        >
          {children}
        </span>
      )
    }
)

const mockUseProfileSelection = useProfileSelection as jest.Mock

const baseProps = {
  claims: [],
  isCandidate: false,
  isReviewer: false,
  login: 'alice',
  rawMarkdown: 'Hello world.',
  year: '2025',
}

describe('AnnotatedProfile', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockUseProfileSelection.mockReturnValue(null)
  })

  it('renders plain markdown when there are no claims', () => {
    render(<AnnotatedProfile {...baseProps} rawMarkdown="**Hello** world" />)
    expect(screen.getByText('Hello')).toBeInTheDocument()
    expect(document.querySelector('strong')?.textContent).toBe('Hello')
  })

  it('wraps a claim sourceText in a highlight span with data attributes', () => {
    render(
      <AnnotatedProfile
        {...baseProps}
        rawMarkdown="Line one. This is my claim. Line three."
        claims={[
          {
            id: '1',
            key: 'claim-key',
            name: 'A Claim',
            sourceText: 'This is my claim.',
            status: ClaimStatusEnum.Approved,
          },
        ]}
      />
    )
    const mark = screen.getByTestId('claim-highlight')
    expect(mark).toHaveAttribute('data-claim-key', 'claim-key')
    expect(mark).toHaveAttribute('data-claim-name', 'A Claim')
    expect(mark).toHaveAttribute('data-claim-status', ClaimStatusEnum.Approved)
    expect(mark.textContent).toBe('This is my claim.')
  })

  it('skips claims whose sourceText contains a blank line', () => {
    render(
      <AnnotatedProfile
        {...baseProps}
        rawMarkdown="para one\n\npara two"
        claims={[
          {
            id: '1',
            key: 'cross',
            name: 'Cross Block',
            sourceText: 'one\n\npara',
            status: ClaimStatusEnum.Draft,
          },
        ]}
      />
    )
    expect(screen.queryByTestId('claim-highlight')).not.toBeInTheDocument()
  })

  it('drops claims whose sourceText is not found', () => {
    render(
      <AnnotatedProfile
        {...baseProps}
        rawMarkdown="Line one. Line two."
        claims={[
          {
            id: '1',
            key: 'missing',
            name: 'Missing',
            sourceText: 'nowhere to be found',
            status: ClaimStatusEnum.Draft,
          },
        ]}
      />
    )
    expect(screen.queryByTestId('claim-highlight')).not.toBeInTheDocument()
  })

  it('gives longer sourceText priority when two claims overlap', () => {
    render(
      <AnnotatedProfile
        {...baseProps}
        rawMarkdown="Overlap area here."
        claims={[
          {
            id: 'short',
            key: 'short',
            name: 'Short',
            sourceText: 'Overlap',
            status: ClaimStatusEnum.Draft,
          },
          {
            id: 'long',
            key: 'long',
            name: 'Long',
            sourceText: 'Overlap area',
            status: ClaimStatusEnum.Draft,
          },
        ]}
      />
    )
    const marks = screen.getAllByTestId('claim-highlight')
    expect(marks).toHaveLength(1)
    expect(marks[0]).toHaveTextContent('Overlap area')
    expect(marks[0]).toHaveAttribute('data-claim-key', 'long')
  })

  it('escapes special characters in claim attributes without breaking the markup', () => {
    render(
      <AnnotatedProfile
        {...baseProps}
        rawMarkdown="the text is here."
        claims={[
          {
            id: '1',
            key: 'a"b<c>',
            name: 'name & "quote"',
            sourceText: 'text is here',
            status: ClaimStatusEnum.Draft,
          },
        ]}
      />
    )
    const mark = screen.getByTestId('claim-highlight')
    expect(mark.textContent).toBe('text is here')
    expect(mark).toHaveAttribute('data-claim-status', ClaimStatusEnum.Draft)
  })

  it('rewrites relative image URLs against the owasp.org base', () => {
    render(
      <AnnotatedProfile
        {...baseProps}
        rawMarkdown={'<img src="../assets/images/alice/photo.jpg" alt="alice">'}
      />
    )
    const img = document.querySelector('img')
    expect(img?.getAttribute('src')).toBe(
      'https://owasp.org/www-board-candidates/assets/images/alice/photo.jpg'
    )
  })

  it('rewrites <source> src attributes too', () => {
    render(
      <AnnotatedProfile
        {...baseProps}
        rawMarkdown={'<video><source src="../assets/videos/talk.mp4" type="video/mp4"></video>'}
      />
    )
    const source = document.querySelector('source')
    expect(source?.getAttribute('src')).toBe(
      'https://owasp.org/www-board-candidates/assets/videos/talk.mp4'
    )
  })

  it('leaves absolute image URLs unchanged', () => {
    render(
      <AnnotatedProfile
        {...baseProps}
        rawMarkdown={'<img src="https://example.com/pic.jpg" alt="x">'}
      />
    )
    expect(document.querySelector('img')?.getAttribute('src')).toBe('https://example.com/pic.jpg')
  })

  it('does not render the Create claim button when there is no selection', () => {
    render(<AnnotatedProfile {...baseProps} isCandidate />)
    expect(screen.queryByRole('button', { name: /Create claim/i })).not.toBeInTheDocument()
  })

  it('does not render the Create claim button for non-candidates', () => {
    mockUseProfileSelection.mockReturnValue({
      text: 'Hello world.',
      rect: { top: 100, left: 50, width: 80 } as DOMRect,
    })
    render(<AnnotatedProfile {...baseProps} />)
    expect(screen.queryByRole('button', { name: /Create claim/i })).not.toBeInTheDocument()
  })

  it('renders the Create claim button when a candidate has an active selection', () => {
    mockUseProfileSelection.mockReturnValue({
      text: 'Hello world.',
      rect: { top: 100, left: 50, width: 80 } as DOMRect,
    })
    render(<AnnotatedProfile {...baseProps} isCandidate />)
    expect(screen.getByRole('button', { name: /Create claim/i })).toBeInTheDocument()
  })

  it('hides the Create claim button when the selection is not an exact substring of rawMarkdown', () => {
    mockUseProfileSelection.mockReturnValue({
      text: 'I lead OWASP Nest',
      rect: { top: 100, left: 50, width: 80 } as DOMRect,
    })
    render(
      <AnnotatedProfile
        {...baseProps}
        isCandidate
        rawMarkdown="I lead [OWASP Nest](https://nest.owasp.org)."
      />
    )
    expect(screen.queryByRole('button', { name: /Create claim/i })).not.toBeInTheDocument()
  })

  it('navigates to the create-claim page with the encoded selection', () => {
    const push = (useRouter() as unknown as { push: jest.Mock }).push
    mockUseProfileSelection.mockReturnValue({
      text: 'Hello world.',
      rect: { top: 100, left: 50, width: 80 } as DOMRect,
    })
    render(<AnnotatedProfile {...baseProps} isCandidate />)
    fireEvent.click(screen.getByRole('button', { name: /Create claim/i }))
    expect(push).toHaveBeenCalledWith(
      '/board/2025/candidates/alice/claims/create?sourceText=Hello+world.'
    )
  })
})
