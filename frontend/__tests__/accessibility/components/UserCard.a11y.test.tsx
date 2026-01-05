import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { UserCardProps } from 'types/card'
import UserCard from 'components/UserCard'

expect.extend(toHaveNoViolations)

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
