import { screen, waitFor, fireEvent } from '@testing-library/react'

export const assertRepoDetails = async ({
  heading,
  license,
  stars,
  forks,
  commits,
  contributors,
  issues,
}: {
  heading: string
  license: string
  stars: string
  forks: string
  commits?: string
  contributors?: string
  issues: string
}) => {
  await waitFor(() => {
    const title = screen.getByRole('heading', { name: heading })
    expect(title).toBeInTheDocument()
    expect(screen.getByText(license)).toBeInTheDocument()
  })
  expect(screen.getByText(stars)).toBeInTheDocument()
  expect(screen.getByText(forks)).toBeInTheDocument()
  if (commits) expect(screen.getByText(commits)).toBeInTheDocument()
  if (contributors) expect(screen.getByText(contributors)).toBeInTheDocument()
  expect(screen.getByText(issues)).toBeInTheDocument()
}

export const assertHeadingsAndTexts = async ({
  headingText,
  texts,
}: {
  headingText: string
  texts: string[]
}) => {
  await waitFor(() => {
    const heading = screen.getByRole('heading', { name: headingText })
    expect(heading).toBeInTheDocument()
  })

  texts.forEach((text) => {
    expect(screen.getByText(text)).toBeInTheDocument()
  })
}

export const assertContributorToggle = async (initial: string, others: string[]) => {
  await waitFor(() => {
    expect(screen.getByText(initial)).toBeInTheDocument()
    expect(screen.queryByText('Contributor 10')).not.toBeInTheDocument()
  })

  const showMoreButton = screen.getByRole('button', { name: /Show more/i })
  fireEvent.click(showMoreButton)

  await waitFor(() => {
    others.forEach((name) => {
      expect(screen.getByText(name)).toBeInTheDocument()
    })
  })

  const showLessButton = screen.getByRole('button', { name: /Show less/i })
  fireEvent.click(showLessButton)

  await waitFor(() => {
    expect(screen.queryByText('Contributor 10')).not.toBeInTheDocument()
  })
}
