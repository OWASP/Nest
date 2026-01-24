import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { UserCardProps } from 'types/card'
import UserCard from 'components/UserCard'

const defaultProps: UserCardProps = {
  name: 'John Doe',
  avatar: '',
  button: {
    label: 'View Profile',
    onclick: jest.fn(),
  },
  className: '',
  company: '',
  description: 'This is a sample description',
  email: 'test@test.com',
  followersCount: 100,
  location: '',
  repositoriesCount: 12,
  badgeCount: 3,
}

describe('UserCard Accessibility', () => {
  it('should not have any accessibility violations', async () => {
    const { baseElement } = render(<UserCard {...defaultProps} />)

    const results = await axe(baseElement)

    expect(results).toHaveNoViolations()
  })
})
