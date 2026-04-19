import { render, screen } from '@testing-library/react'
import React from 'react'
import '@testing-library/jest-dom'
import CardDetailsSummary from 'components/CardDetailsPage/CardDetailsSummary'

jest.mock('components/MarkdownWrapper', () => ({
  __esModule: true,
  default: ({ content }: { content: string }) => (
    <div data-testid="markdown-wrapper">{content}</div>
  ),
}))

jest.mock('components/SecondaryCard', () => ({
  __esModule: true,
  default: ({ title, children }: { title?: React.ReactNode; children: React.ReactNode }) => (
    <div data-testid="secondary-card">
      {title && <h3>{title}</h3>}
      <div>{children}</div>
    </div>
  ),
}))

jest.mock('components/AnchorTitle', () => ({
  __esModule: true,
  default: ({ title }: { title: string }) => <span data-testid="anchor-title">{title}</span>,
}))

jest.mock('react-icons/fa6', () => ({
  FaCircleInfo: () => <span data-testid="icon-info" />,
}))

describe('CardDetailsSummary', () => {
  it('renders nothing when no summary or userSummary provided', () => {
    const { container } = render(<CardDetailsSummary />)
    expect(container.firstChild).toBeNull()
  })

  it('renders summary section when summary prop is provided', () => {
    render(<CardDetailsSummary summary="This is a project summary" />)

    expect(screen.getByText('Summary')).toBeInTheDocument()
    expect(screen.getByText('This is a project summary')).toBeInTheDocument()
  })

  it('renders userSummary section when userSummary prop is provided', () => {
    const userSummary = <div>Custom user summary content</div>
    render(<CardDetailsSummary userSummary={userSummary} />)

    expect(screen.getByText('Custom user summary content')).toBeInTheDocument()
  })

  it('renders both summary and userSummary when both provided', () => {
    const userSummary = <div>User custom content</div>
    render(<CardDetailsSummary summary="Project summary text" userSummary={userSummary} />)

    expect(screen.getByText('Summary')).toBeInTheDocument()
    expect(screen.getByText('Project summary text')).toBeInTheDocument()
    expect(screen.getByText('User custom content')).toBeInTheDocument()
  })

  it('renders nothing when summary is empty string', () => {
    const { container } = render(<CardDetailsSummary summary="" />)
    expect(container.firstChild).toBeNull()
  })

  it('renders markdown wrapper with correct content', () => {
    const summaryText = 'This is **bold** text'
    render(<CardDetailsSummary summary={summaryText} />)

    expect(screen.getByTestId('markdown-wrapper')).toHaveTextContent(summaryText)
  })
})
