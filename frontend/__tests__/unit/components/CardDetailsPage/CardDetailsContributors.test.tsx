import { render, screen } from '@testing-library/react'
import React from 'react'
import '@testing-library/jest-dom'
import { Contributor } from 'types/contributor'
import CardDetailsContributors from 'components/CardDetailsPage/CardDetailsContributors'

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

describe('CardDetailsContributors', () => {
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
    const { container } = render(<CardDetailsContributors />)
    expect(container.firstChild).toBeNull()
  })

  it('renders top contributors when provided', () => {
    render(<CardDetailsContributors topContributors={[mockContributor, mockContributor2]} />)

    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Jane Smith')).toBeInTheDocument()
  })

  it('renders admins list when provided', () => {
    render(<CardDetailsContributors admins={[mockContributor]} />)

    expect(screen.getByText('Admins')).toBeInTheDocument()
    expect(screen.getByText('John Doe')).toBeInTheDocument()
  })

  it('does not render admins list when empty', () => {
    render(<CardDetailsContributors admins={[]} />)

    expect(screen.queryByText('Admins')).not.toBeInTheDocument()
  })

  it('renders mentors list when provided', () => {
    render(<CardDetailsContributors mentors={[mockContributor]} />)

    expect(screen.getByText('Mentors')).toBeInTheDocument()
    expect(screen.getByText('John Doe')).toBeInTheDocument()
  })

  it('renders mentees list when provided', () => {
    render(<CardDetailsContributors mentees={[mockContributor]} />)

    expect(screen.getByText('Mentees')).toBeInTheDocument()
    expect(screen.getByText('John Doe')).toBeInTheDocument()
  })

  it('renders multiple contributor sections simultaneously', () => {
    render(
      <CardDetailsContributors
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
      <CardDetailsContributors
        admins={[mockContributor, mockContributor2]}
        topContributors={[mockContributor]}
      />
    )

    expect(screen.getByText('Admins')).toBeInTheDocument()
    expect(screen.getByText('Top Contributors')).toBeInTheDocument()
  })

  it('handles multiple contributor types correctly', () => {
    render(<CardDetailsContributors topContributors={[mockContributor]} />)

    expect(screen.getByText('Top Contributors')).toBeInTheDocument()
  })

  it('renders empty when all arrays are empty', () => {
    const { container } = render(
      <CardDetailsContributors
        topContributors={undefined}
        mentors={undefined}
        mentees={undefined}
      />
    )
    expect(container.firstChild).toBeNull()
  })

  it('handles all contributor types', () => {
    render(<CardDetailsContributors topContributors={[mockContributor]} />)

    expect(screen.getByText('Top Contributors')).toBeInTheDocument()
  })

  it('does not render mentors when array is empty', () => {
    render(<CardDetailsContributors mentors={[]} />)
    expect(screen.queryByText('Mentors')).not.toBeInTheDocument()
  })

  it('does not render mentees when array is empty', () => {
    render(<CardDetailsContributors mentees={[]} />)
    expect(screen.queryByText('Mentees')).not.toBeInTheDocument()
  })

  it('does not render admins when array is empty', () => {
    render(<CardDetailsContributors admins={[]} />)
    expect(screen.queryByText('Admins')).not.toBeInTheDocument()
  })

  it('renders all contributor types together', () => {
    render(
      <CardDetailsContributors
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
    render(<CardDetailsContributors topContributors={undefined} />)
    expect(screen.queryByText('Top Contributors')).not.toBeInTheDocument()
  })

  it('does not render mentors when undefined', () => {
    render(<CardDetailsContributors mentors={undefined} />)
    expect(screen.queryByText('Mentors')).not.toBeInTheDocument()
  })

  it('does not render mentees when undefined', () => {
    render(<CardDetailsContributors mentees={undefined} />)
    expect(screen.queryByText('Mentees')).not.toBeInTheDocument()
  })

  it('does not render admins with empty array', () => {
    render(<CardDetailsContributors admins={[]} />)
    expect(screen.queryByText('Admins')).not.toBeInTheDocument()
  })

  it('renders only topContributors when other arrays are undefined', () => {
    render(
      <CardDetailsContributors
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
    render(<CardDetailsContributors topContributors={[mockContributor]} />)

    expect(screen.getByText('Top Contributors')).toBeInTheDocument()
  })

  it('renders mentees with programKey and entityKey', () => {
    render(
      <CardDetailsContributors
        programKey="test-program"
        entityKey="test-entity"
        mentees={[mockContributor]}
      />
    )

    expect(screen.getByText('Mentees')).toBeInTheDocument()
    const menteeLink = screen.getByText('John Doe').closest('li')?.querySelector('a')
    expect(menteeLink?.href).toContain('/programs/test-program/mentees/')
  })

  it('renders mentees with empty programKey and entityKey', () => {
    render(<CardDetailsContributors programKey="" entityKey="" mentees={[mockContributor]} />)

    expect(screen.getByText('Mentees')).toBeInTheDocument()
    const menteeLink = screen.getByText('John Doe').closest('li')?.querySelector('a')
    expect(menteeLink?.href).toContain('/programs//mentees/')
  })

  it('renders mentees without programKey and entityKey props', () => {
    render(<CardDetailsContributors mentees={[mockContributor]} />)

    expect(screen.getByText('Mentees')).toBeInTheDocument()
    const menteeLink = screen.getByText('John Doe').closest('li')?.querySelector('a')
    expect(menteeLink?.href).toContain('/programs//mentees/')
  })

  it('renders multiple admins', () => {
    const mockAdmins = [mockContributor, mockContributor2]
    render(<CardDetailsContributors admins={mockAdmins} />)

    expect(screen.getByText('Admins')).toBeInTheDocument()
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Jane Smith')).toBeInTheDocument()
  })

  it('renders multiple mentors', () => {
    const mockMentors = [mockContributor, mockContributor2]
    render(<CardDetailsContributors mentors={mockMentors} />)

    expect(screen.getByText('Mentors')).toBeInTheDocument()
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Jane Smith')).toBeInTheDocument()
  })

  it('renders multiple mentees', () => {
    const mockMentees = [mockContributor, mockContributor2]
    render(<CardDetailsContributors mentees={mockMentees} />)

    expect(screen.getByText('Mentees')).toBeInTheDocument()
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Jane Smith')).toBeInTheDocument()
  })
})
