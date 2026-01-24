import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { ReactNode } from 'react'
import { Contributor } from 'types/contributor'
import { getMemberUrl } from 'utils/urlFormatter'
import ContributorsList from 'components/ContributorsList'

expect.extend(toHaveNoViolations)

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
    id: 'contributor-developer1-a11y',
    avatarUrl: 'https://github.com/developer1.avatar',
    login: 'developer1',
    name: 'Alex Developer',
    projectKey: 'project1',
    contributionsCount: 50,
  },
  {
    id: 'contributor-contributor2-a11y',
    avatarUrl: 'https://github.com/contributor2.avatar',
    login: 'contributor2',
    name: 'Jane Developer',
    projectKey: 'project1',
    contributionsCount: 30,
  },
  {
    id: 'contributor-user3-a11y',
    avatarUrl: 'https://github.com/user3.avatar',
    login: 'user3',
    name: '',
    projectKey: 'project1',
    contributionsCount: 20,
  },
]

describe('ContributorsList Accessibility', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(
      <ContributorsList contributors={mockContributors} getUrl={getMemberUrl} />
    )

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
