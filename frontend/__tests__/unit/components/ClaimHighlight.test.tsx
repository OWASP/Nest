import { fireEvent, render, screen } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import React from 'react'

import { ClaimStatusEnum } from 'types/__generated__/graphql'
import { type ProfileClaim } from 'components/AnnotatedProfile'
import ClaimHighlight from 'components/ClaimHighlight'

jest.mock('@heroui/react', () => ({
  Popover: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  PopoverTrigger: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  PopoverContent: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="popover-content">{children}</div>
  ),
}))

jest.mock('@heroui/button', () => ({
  Button: ({
    children,
    onPress,
    className,
  }: {
    children: React.ReactNode
    onPress?: () => void
    className?: string
  }) => (
    <button type="button" onClick={onPress} className={className}>
      {children}
    </button>
  ),
}))

const defaultClaim: ProfileClaim = {
  id: 'claim-1',
  key: 'my-claim',
  name: 'My Claim',
  sourceText: 'claimed text',
  status: ClaimStatusEnum.Approved,
}

const renderHighlight = (overrides: Partial<ProfileClaim> = {}) => {
  const claim = { ...defaultClaim, ...overrides }
  const claimsById = new Map([[claim.id, claim]])
  return render(
    <ClaimHighlight year="2025" login="alice" claimsById={claimsById} data-id={claim.id}>
      claimed text
    </ClaimHighlight>
  )
}

describe('ClaimHighlight', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders children only when the claim id is not in the map', () => {
    const { container } = render(
      <ClaimHighlight year="2025" login="alice" claimsById={new Map()} data-id="missing">
        plain text
      </ClaimHighlight>
    )
    expect(container.textContent).toBe('plain text')
    expect(screen.queryByTestId('popover-content')).not.toBeInTheDocument()
  })

  it('renders children only when no data-id is provided', () => {
    const { container } = render(
      <ClaimHighlight year="2025" login="alice" claimsById={new Map()}>
        plain text
      </ClaimHighlight>
    )
    expect(container.textContent).toBe('plain text')
    expect(screen.queryByTestId('popover-content')).not.toBeInTheDocument()
  })

  it('renders a popover with claim name, status badge, and View claim button', () => {
    renderHighlight()
    const popover = screen.getByTestId('popover-content')
    expect(popover).toHaveTextContent('My Claim')
    expect(popover).toHaveTextContent('Approved')
    expect(screen.getByRole('button', { name: /View claim/i })).toBeInTheDocument()
  })

  it('navigates when the View claim button is clicked', () => {
    const push = (useRouter() as unknown as { push: jest.Mock }).push
    renderHighlight()
    fireEvent.click(screen.getByRole('button', { name: /View claim/i }))
    expect(push).toHaveBeenCalledWith('/board/2025/candidates/alice/claims/my-claim')
  })

  it('falls back to Draft style when status is unknown', () => {
    renderHighlight({ status: 'MYSTERY' as ClaimStatusEnum })
    expect(screen.getByTestId('popover-content')).toHaveTextContent('Draft')
  })

  it('exposes the claim in the aria-label on the trigger', () => {
    renderHighlight()
    expect(screen.getByLabelText('Claim: My Claim, status Approved')).toBeInTheDocument()
  })

  it('falls back to unnamed in aria-label when name is empty', () => {
    renderHighlight({ name: '', status: ClaimStatusEnum.Draft })
    expect(screen.getByLabelText('Claim: unnamed, status Draft')).toBeInTheDocument()
  })
})
