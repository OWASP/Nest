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
    const { container } = render(<CardDetailsContributors type="project" />)
    expect(container.firstChild).toBeNull()
  })

  it('renders top contributors when provided for project type', () => {
    render(
      <CardDetailsContributors
        type="project"
        topContributors={[mockContributor, mockContributor2]}
      />
    )

    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Jane Smith')).toBeInTheDocument()
  })

  it('renders admins list for program type', () => {
    render(<CardDetailsContributors type="program" admins={[mockContributor]} />)

    expect(screen.getByText('Admins')).toBeInTheDocument()
    expect(screen.getByText('John Doe')).toBeInTheDocument()
  })

  it('does not render admins list for non-program types', () => {
    render(<CardDetailsContributors type="project" admins={[mockContributor]} />)

    expect(screen.queryByText('Admins')).not.toBeInTheDocument()
  })

  it('renders mentors list when provided', () => {
    render(<CardDetailsContributors type="project" mentors={[mockContributor]} />)

    expect(screen.getByText('Mentors')).toBeInTheDocument()
    expect(screen.getByText('John Doe')).toBeInTheDocument()
  })

  it('renders mentees list when provided', () => {
    render(<CardDetailsContributors type="project" mentees={[mockContributor]} />)

    expect(screen.getByText('Mentees')).toBeInTheDocument()
    expect(screen.getByText('John Doe')).toBeInTheDocument()
  })

  it('renders multiple contributor sections simultaneously', () => {
    render(
      <CardDetailsContributors
        type="project"
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

  it('renders program admins when program type', () => {
    render(
      <CardDetailsContributors
        type="program"
        admins={[mockContributor, mockContributor2]}
        topContributors={[mockContributor]}
      />
    )

    expect(screen.getByText('Admins')).toBeInTheDocument()
    expect(screen.getByText('Top Contributors')).toBeInTheDocument()
  })

  it('handles repository type correctly', () => {
    render(
      <CardDetailsContributors
        type="repository"
        topContributors={[mockContributor]}
        admins={[mockContributor2]}
      />
    )

    expect(screen.getByText('Top Contributors')).toBeInTheDocument()
    expect(screen.queryByText('Admins')).not.toBeInTheDocument()
  })

  it('renders empty contributor list when all arrays are empty', () => {
    const { container } = render(
      <CardDetailsContributors type="project" topContributors={[]} mentors={[]} mentees={[]} />
    )
    const ul = container.querySelector('ul')
    expect(ul).toBeEmptyDOMElement()
  })

  it('handles chapter type correctly', () => {
    render(<CardDetailsContributors type="chapter" topContributors={[mockContributor]} />)

    expect(screen.getByText('Top Contributors')).toBeInTheDocument()
  })

  it('does not render mentors when array is empty', () => {
    render(<CardDetailsContributors type="project" mentors={[]} />)
    expect(screen.queryByText('Mentors')).not.toBeInTheDocument()
  })

  it('does not render mentees when array is empty', () => {
    render(<CardDetailsContributors type="project" mentees={[]} />)
    expect(screen.queryByText('Mentees')).not.toBeInTheDocument()
  })

  it('does not render admins when array is empty even for program type', () => {
    render(<CardDetailsContributors type="program" admins={[]} />)
    expect(screen.queryByText('Admins')).not.toBeInTheDocument()
  })

  it('renders all contributor types for program type', () => {
    render(
      <CardDetailsContributors
        type="program"
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
    render(<CardDetailsContributors type="project" topContributors={undefined} />)
    expect(screen.queryByText('Top Contributors')).not.toBeInTheDocument()
  })

  it('does not render mentors when undefined', () => {
    render(<CardDetailsContributors type="project" mentors={undefined} />)
    expect(screen.queryByText('Mentors')).not.toBeInTheDocument()
  })

  it('does not render mentees when undefined', () => {
    render(<CardDetailsContributors type="project" mentees={undefined} />)
    expect(screen.queryByText('Mentees')).not.toBeInTheDocument()
  })

  it('rendersAdmins with empty array when type is program', () => {
    render(<CardDetailsContributors type="program" admins={[]} />)
    expect(screen.queryByText('Admins')).not.toBeInTheDocument()
  })

  it('renders only topContributors when other arrays are undefined', () => {
    render(
      <CardDetailsContributors
        type="project"
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

  it('handles user type correctly', () => {
    render(<CardDetailsContributors type="user" topContributors={[mockContributor]} />)

    expect(screen.getByText('Top Contributors')).toBeInTheDocument()
  })

  it('handles organization type correctly', () => {
    render(<CardDetailsContributors type="organization" topContributors={[mockContributor]} />)

    expect(screen.getByText('Top Contributors')).toBeInTheDocument()
  })

  it('handles committee type correctly', () => {
    render(<CardDetailsContributors type="committee" topContributors={[mockContributor]} />)

    expect(screen.getByText('Top Contributors')).toBeInTheDocument()
  })

  it('handles module type correctly', () => {
    render(<CardDetailsContributors type="module" topContributors={[mockContributor]} />)

    expect(screen.getByText('Top Contributors')).toBeInTheDocument()
  })

  it('renders mentees with programKey and entityKey', () => {
    render(
      <CardDetailsContributors
        type="project"
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
    render(
      <CardDetailsContributors
        type="project"
        programKey=""
        entityKey=""
        mentees={[mockContributor]}
      />
    )

    expect(screen.getByText('Mentees')).toBeInTheDocument()
    const menteeLink = screen.getByText('John Doe').closest('li')?.querySelector('a')
    expect(menteeLink?.href).toContain('/programs//mentees/')
  })

  it('renders mentees without programKey and entityKey props', () => {
    render(<CardDetailsContributors type="project" mentees={[mockContributor]} />)

    expect(screen.getByText('Mentees')).toBeInTheDocument()
    const menteeLink = screen.getByText('John Doe').closest('li')?.querySelector('a')
    expect(menteeLink?.href).toContain('/programs//mentees/')
  })

  it('renders multiple admins for program type', () => {
    const mockAdmins = [mockContributor, mockContributor2]
    render(<CardDetailsContributors type="program" admins={mockAdmins} />)

    expect(screen.getByText('Admins')).toBeInTheDocument()
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Jane Smith')).toBeInTheDocument()
  })

  it('renders multiple mentors', () => {
    const mockMentors = [mockContributor, mockContributor2]
    render(<CardDetailsContributors type="project" mentors={mockMentors} />)

    expect(screen.getByText('Mentors')).toBeInTheDocument()
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Jane Smith')).toBeInTheDocument()
  })

  it('renders multiple mentees', () => {
    const mockMentees = [mockContributor, mockContributor2]
    render(<CardDetailsContributors type="project" mentees={mockMentees} />)

    expect(screen.getByText('Mentees')).toBeInTheDocument()
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Jane Smith')).toBeInTheDocument()
  })
})
