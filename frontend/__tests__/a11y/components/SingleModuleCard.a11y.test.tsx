import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import React from 'react'
import { ExperienceLevelEnum, ProgramStatusEnum } from 'types/__generated__/graphql'
import { Module } from 'types/mentorship'
import SingleModuleCard from 'components/SingleModuleCard'

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
      id: 'mentor-user1-a11y',
      name: 'user1',
      login: 'user1',
      avatarUrl: 'https://example.com/avatar1.jpg',
    },
    {
      id: 'mentor-user2-a11y',
      name: 'user2',
      login: 'user2',
      avatarUrl: 'https://example.com/avatar2.jpg',
    },
  ],
  startedAt: 1704067200,
  endedAt: 1735689599,
  domains: ['frontend', 'backend'],
  tags: ['react', 'nodejs'],
  labels: ['good first issue', 'bug'],
}

describe('SingleModuleCard a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<SingleModuleCard module={mockModule} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
