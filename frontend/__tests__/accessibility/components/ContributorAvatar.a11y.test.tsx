import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { ReactNode } from 'react'
import { Contributor } from 'types/contributor'
import ContributorAvatar from 'components/ContributorAvatar'

expect.extend(toHaveNoViolations)

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({ children, content, id }: { children: ReactNode; content: string; id: string }) => (
    <div data-testid={id}>
      <div aria-describedby={`${id}-tooltip`}>{children}</div>
      <div id={`${id}-tooltip`} role="tooltip">
        {content}
      </div>
    </div>
  ),
}))

jest.mock('next/link', () => {
  return ({
    children,
    href,
    target,
    rel,
  }: {
    children: ReactNode
    href: string
    target?: string
    rel?: string
  }) => (
    <a href={href} target={target} rel={rel} data-testid="contributor-link">
      {children}
    </a>
  )
})

const mockGitHubContributor: Contributor = {
  login: 'jane-doe',
  name: 'Jane Doe',
  avatarUrl: 'https://avatars.githubusercontent.com/u/12345',
  contributionsCount: 15,
  projectName: 'OWASP-Nest',
  projectKey: 'test-key',
}

describe('ContributorAvatar a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(
      <ContributorAvatar contributor={mockGitHubContributor} uniqueKey="test-key" />
    )

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
