import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
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

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('UserCard Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should not have any accessibility violations', async () => {
    const { baseElement } = render(<UserCard {...defaultProps} />)

    const results = await axe(baseElement)

    expect(results).toHaveNoViolations()
  })
})
