import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { CSSProperties } from 'react'
import { UserCardProps } from 'types/card'
import UserCard from 'components/UserCard'

expect.extend(toHaveNoViolations)

jest.mock('next/image', () => ({
  __esModule: true,
  default: ({
    src,
    alt,
    fill,
    objectFit,
    ...props
  }: {
    src: string
    alt: string
    fill?: boolean
    objectFit?: 'fill' | 'contain' | 'cover' | 'none' | 'scale-down'
    [key: string]: unknown
  }) => (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={src}
      alt={alt}
      style={fill ? { objectFit: objectFit as CSSProperties['objectFit'] } : undefined}
      data-testid="user-avatar"
      {...props}
    />
  ),
}))

const defaultProps: UserCardProps = {
  name: 'John Doe',
  avatar: '',
  button: {
    label: 'View Profile',
    onclick: jest.fn(),
  },
  className: '',
  company: '',
  description: '',
  email: '',
  followersCount: 0,
  location: '',
  repositoriesCount: 0,
  badgeCount: 0,
}

describe('UserCard Accessibility', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<UserCard {...defaultProps} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
