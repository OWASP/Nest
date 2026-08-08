import { fireEvent, render, screen } from '@testing-library/react'
import { useIsMobile } from 'hooks/useIsMobile'
import { useRouter } from 'next/navigation'
import React from 'react'

import { ClaimStatusEnum } from 'types/__generated__/graphql'
import ClaimHighlight from 'components/ClaimHighlight'

jest.mock('hooks/useIsMobile', () => ({
  useIsMobile: jest.fn(() => false),
}))

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({ content, children }: { content: React.ReactNode; children: React.ReactNode }) => (
    <>
      <div data-testid="tooltip-content">{content}</div>
      {children}
    </>
  ),
}))

jest.mock('@heroui/react', () => ({
  Popover: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  PopoverTrigger: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  PopoverContent: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="popover-content">{children}</div>
  ),
}))

const mockUseIsMobile = useIsMobile as jest.Mock

const renderHighlight = (extra: Record<string, unknown> = {}) =>
  render(
    <ClaimHighlight
      year="2025"
      login="alice"
      data-claim-key="my-claim"
      data-claim-name="My Claim"
      data-claim-status={ClaimStatusEnum.Approved}
      {...extra}
    >
      claimed text
    </ClaimHighlight>
  )

describe('ClaimHighlight', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockUseIsMobile.mockReturnValue(false)
  })

  it('renders a plain span when no claim key is present', () => {
    const { container } = render(
      <ClaimHighlight year="2025" login="alice" className="foo">
        plain text
      </ClaimHighlight>
    )
    const span = container.querySelector('span')
    expect(span).not.toBeNull()
    expect(span?.className).toBe('foo')
    expect(span?.textContent).toBe('plain text')
    expect(screen.queryByTestId('tooltip-content')).not.toBeInTheDocument()
  })

  it('renders desktop tooltip with claim name and status badge', () => {
    renderHighlight()
    const tooltip = screen.getByTestId('tooltip-content')
    expect(tooltip).toHaveTextContent('My Claim')
    expect(tooltip).toHaveTextContent('Approved')
    expect(tooltip).toHaveTextContent('Click to view')
    expect(screen.getByRole('link', { name: /Claim: My Claim, status Approved/i })).toBeVisible()
  })

  it('navigates on click when in desktop mode', () => {
    const push = (useRouter() as unknown as { push: jest.Mock }).push
    renderHighlight()
    fireEvent.click(screen.getByRole('link'))
    expect(push).toHaveBeenCalledWith('/board/2025/candidates/alice/claims/my-claim')
  })

  it('navigates on Enter key press', () => {
    const push = (useRouter() as unknown as { push: jest.Mock }).push
    renderHighlight()
    fireEvent.keyDown(screen.getByRole('link'), { key: 'Enter' })
    expect(push).toHaveBeenCalledWith('/board/2025/candidates/alice/claims/my-claim')
  })

  it('navigates on Space key press', () => {
    const push = (useRouter() as unknown as { push: jest.Mock }).push
    renderHighlight()
    fireEvent.keyDown(screen.getByRole('link'), { key: ' ' })
    expect(push).toHaveBeenCalledWith('/board/2025/candidates/alice/claims/my-claim')
  })

  it('ignores unrelated keys', () => {
    const push = (useRouter() as unknown as { push: jest.Mock }).push
    renderHighlight()
    fireEvent.keyDown(screen.getByRole('link'), { key: 'a' })
    expect(push).not.toHaveBeenCalled()
  })

  it('falls back to Draft style when status is unknown', () => {
    renderHighlight({ 'data-claim-status': 'MYSTERY' })
    expect(screen.getByTestId('tooltip-content')).toHaveTextContent('Draft')
  })

  it('falls back to unnamed in aria-label when name is missing', () => {
    render(
      <ClaimHighlight
        year="2025"
        login="alice"
        data-claim-key="my-claim"
        data-claim-status={ClaimStatusEnum.Draft}
      >
        text
      </ClaimHighlight>
    )
    expect(screen.getByLabelText('Claim: unnamed, status Draft')).toBeInTheDocument()
  })

  describe('mobile', () => {
    beforeEach(() => {
      mockUseIsMobile.mockReturnValue(true)
    })

    it('renders a popover with a View claim button', () => {
      renderHighlight()
      const popover = screen.getByTestId('popover-content')
      expect(popover).toHaveTextContent('My Claim')
      expect(popover).toHaveTextContent('Approved')
      expect(screen.getByRole('button', { name: /View claim/i })).toBeInTheDocument()
      expect(screen.queryByRole('link')).not.toBeInTheDocument()
    })

    it('navigates when the View claim button is clicked', () => {
      const push = (useRouter() as unknown as { push: jest.Mock }).push
      renderHighlight()
      fireEvent.click(screen.getByRole('button', { name: /View claim/i }))
      expect(push).toHaveBeenCalledWith('/board/2025/candidates/alice/claims/my-claim')
    })

    it('does not navigate on click of the highlight trigger', () => {
      const push = (useRouter() as unknown as { push: jest.Mock }).push
      renderHighlight()
      fireEvent.click(screen.getByRole('button', { name: /Claim: My Claim, status Approved/i }))
      expect(push).not.toHaveBeenCalled()
    })
  })
})
