import React from 'react'
import { render, screen } from 'wrappers/testUtil'
import type { UserCardProps } from 'types/card'
import UserCard from 'components/UserCard'

jest.mock('next/image', () => ({
  __esModule: true,
  default: ({ src, alt }: { src: string; alt: string }) => (
    // eslint-disable-next-line @next/next/no-img-element
    <img src={src} alt={alt} />
  ),
}))

jest.mock('@heroui/button', () => {
  const MockButton = ({
    children,
    onPress,
  }: {
    children: React.ReactNode
    onPress?: () => void
  }) => <button onClick={onPress}>{children}</button>
  return {
    __esModule: true,
    // eslint-disable-next-line @typescript-eslint/naming-convention
    Button: MockButton,
  }
})

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: ({ className }: { className?: string }) => (
    <span data-testid="fa-icon" className={className} />
  ),
}))

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}))

jest.mock('components/BadgeCount', () => ({
  __esModule: true,
  default: ({ badges }: { badges: { name: string }[] }) => {
    if (!badges || badges.length === 0) {
      return null
    }
    return <div data-testid="badge-count">{badges.length}</div>
  },
}))

describe('UserCard badges', () => {
  const baseProps: UserCardProps = {
    avatar: '',
    button: { label: 'View', onclick: () => {} },
    name: 'John',
  }

  it('shows medal icon with count when badges provided', () => {
    const badges: { name: string; cssClass: string }[] = [
      { name: 'A', cssClass: 'fa-solid fa-star' },
      { name: 'B', cssClass: 'fa-solid fa-bolt' },
    ]
    render(<UserCard {...baseProps} badges={badges} />)

    expect(screen.getByTestId('badge-count')).toHaveTextContent('2')
  })

  it('does not show badge count if no badges are provided', () => {
    render(<UserCard {...baseProps} badges={[]} />)
    expect(screen.queryByTestId('badge-count')).not.toBeInTheDocument()
  })
})
