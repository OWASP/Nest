import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import React from 'react'
import { ExperienceLevelEnum, ProgramStatusEnum } from 'types/__generated__/graphql'
import { Module } from 'types/mentorship'
import SingleModuleCard from 'components/SingleModuleCard'

expect.extend(toHaveNoViolations)

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    back: jest.fn(),
    forward: jest.fn(),
    refresh: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
  usePathname: () => '/my/mentorship/programs/test-program',
}))

jest.mock('next-auth/react', () => ({
  useSession: () => ({
    data: null,
    status: 'unauthenticated',
    update: jest.fn(),
  }),
}))

jest.mock('next/link', () => ({
  __esModule: true,
  default: ({
    children,
    href,
    target,
    rel,
    className,
    ...props
  }: {
    children: React.ReactNode
    href: string
    target?: string
    rel?: string
    className?: string
    [key: string]: unknown
  }) => (
    <a
      href={href}
      target={target}
      rel={rel}
      className={className}
      {...props}
      data-testid="module-link"
    >
      {children}
    </a>
  ),
}))

const mockModule: Module = {
  id: '1',
  key: 'test-module',
  name: 'Test Module',
  description: 'This is a test module description',
  status: ProgramStatusEnum.Published,
  experienceLevel: ExperienceLevelEnum.Intermediate,
  mentors: [
    {
      name: 'user1',
      login: 'user1',
      avatarUrl: 'https://example.com/avatar1.jpg',
    },
    {
      name: 'user2',
      login: 'user2',
      avatarUrl: 'https://example.com/avatar2.jpg',
    },
  ],
  startedAt: '2024-01-01T00:00:00Z',
  endedAt: '2024-12-31T23:59:59Z',
  domains: ['frontend', 'backend'],
  tags: ['react', 'nodejs'],
  labels: ['good first issue', 'bug'],
}

const mockAdmins = [{ login: 'admin1' }, { login: 'admin2' }]

describe('SingleModuleCard a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(
      <SingleModuleCard module={mockModule} accessLevel="admin" admins={mockAdmins} />
    )

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
