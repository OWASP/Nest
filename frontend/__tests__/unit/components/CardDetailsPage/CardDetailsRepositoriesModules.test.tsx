import { render, screen } from '@testing-library/react'
import React from 'react'
import '@testing-library/jest-dom'
import { Module } from 'types/mentorship'
import { RepositoryCardProps } from 'types/project'
import CardDetailsRepositoriesModules from 'components/CardDetailsPage/CardDetailsRepositoriesModules'

jest.mock('components/ModuleCard', () => ({
  __esModule: true,
  default: ({ modules }: { modules: Module[] }) => (
    <div data-testid="module-card">{modules.map((m) => m.name).join(', ')}</div>
  ),
}))

jest.mock('components/RepositoryCard', () => ({
  __esModule: true,
  default: ({ repositories }: { repositories: RepositoryCardProps[] }) => (
    <div data-testid="repository-card">{repositories.map((r) => r.name).join(', ')}</div>
  ),
}))

jest.mock('components/SecondaryCard', () => ({
  __esModule: true,
  default: ({
    title,
    children,
    additionalAction,
  }: {
    title?: string
    children: React.ReactNode
    additionalAction?: React.ReactNode
  }) => (
    <div data-testid="secondary-card">
      {title && <h3>{title}</h3>}
      {additionalAction && <div data-testid="additional-action">{additionalAction}</div>}
      <div>{children}</div>
    </div>
  ),
}))

jest.mock('next-auth/react', () => ({
  useSession: jest.fn(() => ({
    data: {
      user: { role: 'admin' },
    },
  })),
}))

jest.mock('next/link', () => {
  return ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  )
})

describe('CardDetailsRepositoriesModules', () => {
  const mockRepository: RepositoryCardProps = {
    id: '1',
    name: 'test-repo',
    url: 'https://github.com/test-repo',
    language: 'TypeScript',
    stars: 100,
    forks: 50,
  }

  const mockModule: Module = {
    id: '1',
    name: 'auth-module',
    description: 'Authentication module',
    programId: 'program-1',
  }

  it('renders nothing when no repositories or modules provided', () => {
    const { container } = render(<CardDetailsRepositoriesModules type="project" />)
    expect(container.firstChild).toBeNull()
  })

  it('renders repositories for project type', () => {
    render(<CardDetailsRepositoriesModules type="project" repositories={[mockRepository]} />)

    expect(screen.getByTestId('repository-card')).toBeInTheDocument()
    expect(screen.getByText('test-repo')).toBeInTheDocument()
  })

  it('renders modules for program type', () => {
    render(
      <CardDetailsRepositoriesModules
        type="program"
        modules={[mockModule]}
        programKey="test-program"
      />
    )

    expect(screen.getByTestId('module-card')).toBeInTheDocument()
    expect(screen.getByText('auth-module')).toBeInTheDocument()
  })

  it('renders both repositories and modules when provided', () => {
    render(<CardDetailsRepositoriesModules type="project" repositories={[mockRepository]} />)

    expect(screen.getByTestId('repository-card')).toBeInTheDocument()
    expect(screen.getByText('test-repo')).toBeInTheDocument()
  })

  it('renders multiple repositories in one card', () => {
    const repos = [
      mockRepository,
      { ...mockRepository, id: '2', name: 'another-repo' },
      { ...mockRepository, id: '3', name: 'third-repo' },
    ]

    render(<CardDetailsRepositoriesModules type="project" repositories={repos} />)

    expect(screen.getByText('test-repo, another-repo, third-repo')).toBeInTheDocument()
  })

  it('renders multiple modules', () => {
    const modules = [
      mockModule,
      { ...mockModule, id: '2', name: 'payment-module' },
      { ...mockModule, id: '3', name: 'logging-module' },
    ]

    render(
      <CardDetailsRepositoriesModules type="program" modules={modules} programKey="test-program" />
    )

    expect(screen.getByText('auth-module, payment-module, logging-module')).toBeInTheDocument()
  })

  it('does not render repositories when empty', () => {
    const { container } = render(
      <CardDetailsRepositoriesModules type="project" repositories={[]} />
    )
    expect(container.firstChild).toBeNull()
  })

  it('does not render modules when empty', () => {
    const { container } = render(<CardDetailsRepositoriesModules type="program" modules={[]} />)
    expect(container.firstChild).toBeNull()
  })

  it('renders for user type with repositories', () => {
    render(<CardDetailsRepositoriesModules type="user" repositories={[mockRepository]} />)

    expect(screen.getByTestId('repository-card')).toBeInTheDocument()
  })

  it('renders for organization type with repositories', () => {
    render(<CardDetailsRepositoriesModules type="organization" repositories={[mockRepository]} />)

    expect(screen.getByTestId('repository-card')).toBeInTheDocument()
  })

  it('does not render repositories for non-allowed types', () => {
    const { container } = render(
      <CardDetailsRepositoriesModules type="chapter" repositories={[mockRepository]} />
    )
    expect(container.firstChild).toBeNull()
  })

  it('does not render repositories for program type', () => {
    const { container } = render(
      <CardDetailsRepositoriesModules type="program" repositories={[mockRepository]} />
    )
    expect(container.firstChild).toBeNull()
  })

  it('does not render modules for non-program types', () => {
    const { container } = render(
      <CardDetailsRepositoriesModules type="project" modules={[mockModule]} />
    )
    expect(container.firstChild).toBeNull()
  })
})
