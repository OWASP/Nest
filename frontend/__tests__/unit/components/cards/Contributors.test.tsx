import { render, screen } from '@testing-library/react'
import React from 'react'
import '@testing-library/jest-dom'
import { Contributor } from 'types/contributor'
import Contributors from 'components/cards/Contributors'

jest.mock('components/ContributorsList', () => ({
  __esModule: true,
  default: ({
    title,
    contributors,
    getUrl,
  }: {
    title: string
    contributors: Contributor[]
    getUrl?: (login: string) => string
  }) => (
    <div data-testid={`contributors-list-${title.toLowerCase().replaceAll(' ', '-')}`}>
      <h4>{title}</h4>
      <ul>
        {contributors.map((c) => (
          <li key={c.id}>{getUrl ? <a href={getUrl(c.login || '')}>{c.name}</a> : c.name}</li>
        ))}
      </ul>
    </div>
  ),
}))

jest.mock('next/link', () => {
  return ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  )
})

jest.mock('utils/urlFormatter', () => ({
  getMemberUrl: (login: string) => `/members/${login}`,
  getMenteeUrl: (programKey: string, entityKey: string, login: string) =>
    `/programs/${programKey}/mentees/${login}`,
}))

describe('Contributors', () => {
  const mockContributor: Contributor = {
    id: '1',
    name: 'John Doe',
    avatarUrl: 'https://example.com/avatar.jpg',
    login: 'john_doe',
    contributionsCount: 42,
  }

  const mockContributor2: Contributor = {
    id: '2',
    name: 'Jane Smith',
    avatarUrl: 'https://example.com/avatar2.jpg',
    login: 'jane_smith',
    contributionsCount: 35,
  }

  it('renders nothing when no contributors provided', () => {
    const { container } = render(<Contributors />)
    expect(container.firstChild).toBeNull()
  })

  it('renders top contributors when provided', () => {
    render(<Contributors topContributors={[mockContributor, mockContributor2]} />)

    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Jane Smith')).toBeInTheDocument()
  })

  it('renders admins list when provided', () => {
    render(<Contributors admins={[mockContributor]} />)

    expect(screen.getByText('Admins')).toBeInTheDocument()
    expect(screen.getByText('John Doe')).toBeInTheDocument()
  })

  it('does not render admins list when empty', () => {
    render(<Contributors admins={[]} />)

    expect(screen.queryByText('Admins')).not.toBeInTheDocument()
  })

  it('renders mentors list when provided', () => {
    render(<Contributors mentors={[mockContributor]} />)

    expect(screen.getByText('Mentors')).toBeInTheDocument()
    expect(screen.getByText('John Doe')).toBeInTheDocument()
  })

  it('renders mentees list when provided', () => {
    render(<Contributors mentees={[mockContributor]} />)

    expect(screen.getByText('Mentees')).toBeInTheDocument()
    expect(screen.getByText('John Doe')).toBeInTheDocument()
  })

  it('renders multiple contributor sections simultaneously', () => {
    render(
      <Contributors
        topContributors={[mockContributor]}
        mentors={[mockContributor2]}
        mentees={[
          {
            ...mockContributor,
            id: '3',
            name: 'Alice Wonder',
          },
        ]}
      />
    )

    expect(screen.getByText('Top Contributors')).toBeInTheDocument()
    expect(screen.getByText('Mentors')).toBeInTheDocument()
    expect(screen.getByText('Mentees')).toBeInTheDocument()
  })

  it('renders program admins and top contributors', () => {
    render(
      <Contributors
        admins={[mockContributor, mockContributor2]}
        topContributors={[mockContributor]}
      />
    )

    expect(screen.getByText('Admins')).toBeInTheDocument()
    expect(screen.getByText('Top Contributors')).toBeInTheDocument()
  })

  it('handles multiple contributor types correctly', () => {
    render(<Contributors topContributors={[mockContributor]} />)

    expect(screen.getByText('Top Contributors')).toBeInTheDocument()
  })

  it('renders empty when all arrays are empty', () => {
    const { container } = render(
      <Contributors topContributors={undefined} mentors={undefined} mentees={undefined} />
    )
    expect(container.firstChild).toBeNull()
  })

  it('handles all contributor types', () => {
    render(<Contributors topContributors={[mockContributor]} />)

    expect(screen.getByText('Top Contributors')).toBeInTheDocument()
  })

  it('does not render mentors when array is empty', () => {
    render(<Contributors mentors={[]} />)
    expect(screen.queryByText('Mentors')).not.toBeInTheDocument()
  })

  it('does not render mentees when array is empty', () => {
    render(<Contributors mentees={[]} />)
    expect(screen.queryByText('Mentees')).not.toBeInTheDocument()
  })

  it('does not render admins when array is empty', () => {
    render(<Contributors admins={[]} />)
    expect(screen.queryByText('Admins')).not.toBeInTheDocument()
  })

  it('renders all contributor types together', () => {
    render(
      <Contributors
        topContributors={[mockContributor]}
        admins={[mockContributor2]}
        mentors={[
          {
            ...mockContributor,
            id: '3',
            name: 'Mentor User',
          },
        ]}
        mentees={[
          {
            ...mockContributor,
            id: '4',
            name: 'Mentee User',
          },
        ]}
      />
    )

    expect(screen.getByText('Top Contributors')).toBeInTheDocument()
    expect(screen.getByText('Admins')).toBeInTheDocument()
    expect(screen.getByText('Mentors')).toBeInTheDocument()
    expect(screen.getByText('Mentees')).toBeInTheDocument()
  })

  it('does not render topContributors when undefined', () => {
    render(<Contributors topContributors={undefined} />)
    expect(screen.queryByText('Top Contributors')).not.toBeInTheDocument()
  })

  it('does not render mentors when undefined', () => {
    render(<Contributors mentors={undefined} />)
    expect(screen.queryByText('Mentors')).not.toBeInTheDocument()
  })

  it('does not render mentees when undefined', () => {
    render(<Contributors mentees={undefined} />)
    expect(screen.queryByText('Mentees')).not.toBeInTheDocument()
  })

  it('does not render admins with empty array', () => {
    render(<Contributors admins={[]} />)
    expect(screen.queryByText('Admins')).not.toBeInTheDocument()
  })

  it('renders only topContributors when other arrays are undefined', () => {
    render(
      <Contributors
        topContributors={[mockContributor]}
        admins={undefined}
        mentors={undefined}
        mentees={undefined}
      />
    )

    expect(screen.getByText('Top Contributors')).toBeInTheDocument()
    expect(screen.queryByText('Admins')).not.toBeInTheDocument()
    expect(screen.queryByText('Mentors')).not.toBeInTheDocument()
    expect(screen.queryByText('Mentees')).not.toBeInTheDocument()
  })

  it('handles different entity types with topContributors', () => {
    render(<Contributors topContributors={[mockContributor]} />)

    expect(screen.getByText('Top Contributors')).toBeInTheDocument()
  })

  it('renders mentees with programKey and entityKey', () => {
    render(
      <Contributors programKey="test-program" entityKey="test-entity" mentees={[mockContributor]} />
    )

    expect(screen.getByText('Mentees')).toBeInTheDocument()
    const menteeLink = screen.getByText('John Doe').closest('li')?.querySelector('a')
    expect(menteeLink?.href).toContain('/programs/test-program/mentees/')
  })

  it('renders mentees with empty programKey and entityKey', () => {
    render(<Contributors programKey="" entityKey="" mentees={[mockContributor]} />)

    expect(screen.getByText('Mentees')).toBeInTheDocument()
    const menteeLink = screen.getByText('John Doe').closest('li')?.querySelector('a')
    expect(menteeLink?.href).toContain('/programs//mentees/')
  })

  it('renders mentees without programKey and entityKey props', () => {
    render(<Contributors mentees={[mockContributor]} />)

    expect(screen.getByText('Mentees')).toBeInTheDocument()
    const menteeLink = screen.getByText('John Doe').closest('li')?.querySelector('a')
    expect(menteeLink?.href).toContain('/programs//mentees/')
  })

  it('renders multiple admins', () => {
    const mockAdmins = [mockContributor, mockContributor2]
    render(<Contributors admins={mockAdmins} />)

    expect(screen.getByText('Admins')).toBeInTheDocument()
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Jane Smith')).toBeInTheDocument()
  })

  it('renders multiple mentors', () => {
    const mockMentors = [mockContributor, mockContributor2]
    render(<Contributors mentors={mockMentors} />)

    expect(screen.getByText('Mentors')).toBeInTheDocument()
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Jane Smith')).toBeInTheDocument()
  })

  it('renders multiple mentees', () => {
    const mockMentees = [mockContributor, mockContributor2]
    render(<Contributors mentees={mockMentees} />)

    expect(screen.getByText('Mentees')).toBeInTheDocument()
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Jane Smith')).toBeInTheDocument()
  })
})
