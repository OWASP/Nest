import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { ReactNode } from 'react'
import { Contributor } from 'types/contributor'
import TopContributorsList from 'components/TopContributorsList'

jest.mock('next/link', () => {
  return function MockLink({
    children,
    href,
    className,
    ...props
  }: {
    children: ReactNode
    href: string
    className?: string
    [key: string]: unknown
  }) {
    return (
      <a href={href} className={className} {...props}>
        {children}
      </a>
    )
  }
})

const mockContributors: Contributor[] = [
  {
    avatarUrl: 'https://github.com/developer1.avatar',
    login: 'developer1',
    name: 'Alex Developer',
    projectKey: 'project1',
    contributionsCount: 50,
  },
  {
    avatarUrl: 'https://github.com/contributor2.avatar',
    login: 'contributor2',
    name: 'Jane Developer',
    projectKey: 'project1',
    contributionsCount: 30,
  },
  {
    avatarUrl: 'https://github.com/user3.avatar',
    login: 'user3',
    name: '',
    projectKey: 'project1',
    contributionsCount: 20,
  },
]

describe('TopContributorsList Accessibility', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<TopContributorsList contributors={mockContributors} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
