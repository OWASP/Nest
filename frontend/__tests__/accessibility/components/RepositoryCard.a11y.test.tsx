import { fireEvent, render, screen } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { Organization } from 'types/organization'
import { RepositoryCardProps } from 'types/project'
import RepositoryCard from 'components/RepositoryCard'

expect.extend(toHaveNoViolations)

const createMockRepository = (index: number): RepositoryCardProps => ({
  contributorsCount: 10 + index,
  forksCount: 5 + index,
  key: `repo-${index}`,
  name: `Repository ${index}`,
  openIssuesCount: 3 + index,
  organization: {
    login: `org-${index}`,
    name: `Organization ${index}`,
    key: `org-${index}`,
    url: `https://github.com/org-${index}`,
    avatarUrl: `https://github.com/org-${index}.png`,
    description: `Organization ${index} description`,
    objectID: `org-${index}`,
    collaboratorsCount: 10,
    followersCount: 50,
    publicRepositoriesCount: 20,
    createdAt: Date.now(),
    updatedAt: Date.now(),
  } as Organization,
  starsCount: 100 + index,
  subscribersCount: 20 + index,
  url: `https://github.com/org-${index}/repo-${index}`,
})

describe('RepositoryCard a11y', () => {
  it('should not have any accessibility violations', async () => {
    const repositories = Array.from({ length: 6 }, (_, i) => createMockRepository(i))
    const { container } = render(<RepositoryCard repositories={repositories} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when expanded', async () => {
    const repositories = Array.from({ length: 6 }, (_, i) => createMockRepository(i))
    const { container } = render(<RepositoryCard repositories={repositories} />)

    const showMoreButton = screen.getByTestId('show-more-button')
    fireEvent.click(showMoreButton)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when containing atleast one archived repository', async () => {
    const repositories = Array.from({ length: 6 }, (_, i) => createMockRepository(i))
    repositories[2].isArchived = true
    const { container } = render(<RepositoryCard repositories={repositories} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
