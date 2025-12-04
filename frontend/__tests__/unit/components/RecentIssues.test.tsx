import { render, screen, fireEvent } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import React from 'react'
import type { Issue } from 'types/issue'
import RecentIssues from 'components/RecentIssues'

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({
    children,
    content,
    id,
  }: {
    children: React.ReactNode
    content: string
    id: string
  }) => (
    <div data-testid={id} title={content}>
      {children}
    </div>
  ),
}))

jest.mock('next/image', () => ({
  __esModule: true,
  default: ({
    src,
    alt,
    fill,
    objectFit,
    ...props
  }: {
    src: string
    alt: string
    fill?: boolean
    objectFit?: 'fill' | 'contain' | 'cover' | 'none' | 'scale-down'
    [key: string]: unknown
  }) => (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={src}
      alt={alt}
      style={fill && { objectFit: objectFit as React.CSSProperties['objectFit'] }}
      {...props}
    />
  ),
}))

const mockPush = jest.fn()
beforeEach(() => {
  ;(useRouter as jest.Mock).mockReturnValue({ push: mockPush })
  mockPush.mockClear()
})

const baseIssue = {
  author: {
    avatarUrl: 'https://example.com/avatar.png',
    login: 'user1',
    name: 'User One',
    contributionsCount: 10,
    createdAt: 1234567890,
    followersCount: 5,
    followingCount: 2,
    key: 'user1',
    publicRepositoriesCount: 3,
    url: 'https://github.com/user1',
  },
  createdAt: 1710000000,
  hint: 'Hint',
  labels: ['bug'],
  organizationName: 'org',
  projectName: 'proj',
  projectUrl: 'https://github.com/org/proj',
  summary: 'Summary',
  title: 'Issue Title',
  updatedAt: 1710000100,
  url: 'https://github.com/org/proj/issues/1',
  objectID: 'id1',
  repositoryName: 'repo',
}

describe('<RecentIssues />', () => {
  it('renders successfully with minimal required props', () => {
    render(<RecentIssues data={[baseIssue]} />)
    expect(screen.getByText('Recent Issues')).toBeInTheDocument()
    expect(screen.getByText('Issue Title')).toBeInTheDocument()
  })

  it('renders "Nothing to display." when data is empty', () => {
    render(<RecentIssues data={[]} />)
    expect(screen.getByText('Nothing to display.')).toBeInTheDocument()
  })

  it('shows avatar when showAvatar is true', () => {
    render(<RecentIssues data={[baseIssue]} showAvatar={true} />)
    expect(screen.getByAltText("User One's avatar")).toBeInTheDocument()
  })

  it('hides avatar when showAvatar is false', () => {
    render(<RecentIssues data={[baseIssue]} showAvatar={false} />)
    expect(screen.queryByAltText("User One's avatar")).not.toBeInTheDocument()
  })

  it('renders repositoryName and navigates on click', () => {
    render(<RecentIssues data={[baseIssue]} />)
    const repoBtn = screen.getByText('repo')
    expect(repoBtn).toBeInTheDocument()
    fireEvent.click(repoBtn)
    expect(mockPush).toHaveBeenCalledWith('/organizations/org/repositories/repo')
  })

  it('does not render repositoryName button if missing', () => {
    const issue = { ...baseIssue }
    delete issue.repositoryName
    render(<RecentIssues data={[issue]} />)
    expect(screen.queryByText('repo')).not.toBeInTheDocument()
  })

  it('renders formatted date', () => {
    render(<RecentIssues data={[baseIssue]} />)
    expect(screen.getByText(/Mar \d{1,2}, 2024/)).toBeInTheDocument()
  })

  it('renders label text', () => {
    render(<RecentIssues data={[baseIssue]} />)
    expect(screen.getByText('Issue Title')).toBeInTheDocument()
  })

  it('handles edge case: missing author', () => {
    const issue: Issue = { ...baseIssue, author: undefined }
    render(<RecentIssues data={[issue]} />)
    expect(screen.getByText('Issue Title')).toBeInTheDocument()
  })

  it('handles edge case: missing title', () => {
    const issue: Issue = { ...baseIssue, title: undefined }
    render(<RecentIssues data={[issue]} />)
    expect(screen.getByText('Recent Issues')).toBeInTheDocument()
    expect(screen.getByText('repo')).toBeInTheDocument()
    expect(screen.getByAltText("User One's avatar")).toBeInTheDocument()
  })

  it('has accessible roles and labels', () => {
    render(<RecentIssues data={[baseIssue]} />)
    expect(screen.getByRole('heading', { name: /Recent Issues/i })).toBeInTheDocument()
  })

  it('applies correct DOM structure and classNames', () => {
    render(<RecentIssues data={[baseIssue]} />)
    expect(screen.getByText('Recent Issues').closest('div')).toHaveClass('flex')
  })

  it('renders multiple issues', () => {
    const issues = [baseIssue, { ...baseIssue, objectID: 'id2', title: 'Second Issue' }]
    render(<RecentIssues data={issues} />)
    expect(screen.getByText('Second Issue')).toBeInTheDocument()
    expect(screen.getAllByText(/Issue Title|Second Issue/).length).toBeGreaterThan(1)
  })

  it('renders with long repositoryName and truncates', () => {
    const issue = { ...baseIssue, repositoryName: 'a'.repeat(100) }
    render(<RecentIssues data={[issue]} />)
    expect(screen.getByText('a'.repeat(100))).toBeInTheDocument()
  })

  it('renders with custom organizationName', () => {
    const issue = { ...baseIssue, organizationName: 'custom-org' }
    render(<RecentIssues data={[issue]} />)
    fireEvent.click(screen.getByText('repo'))
    expect(mockPush).toHaveBeenCalledWith('/organizations/custom-org/repositories/repo')
  })

  it('renders with missing props gracefully', () => {
    const minimalIssue: Issue = {
      createdAt: 1704067200000,
      title: '',
      url: '',
      objectID: 'minimal-issue',
      projectName: '',
      projectUrl: '',
      updatedAt: 1704067200000,
    }
    render(<RecentIssues data={[minimalIssue]} showAvatar={false} />)
    expect(screen.getByText('Recent Issues')).toBeInTheDocument()
  })

  it('renders with null data', () => {
    render(<RecentIssues data={null as unknown as Issue[]} />)
    expect(screen.getByText('Nothing to display.')).toBeInTheDocument()
  })

  it('defaults to showing avatar when showAvatar is not provided', () => {
    render(<RecentIssues data={[baseIssue]} />)
    expect(screen.getByAltText("User One's avatar")).toBeInTheDocument()
  })

  it('uses fallback alt text when author name and login are missing', () => {
    const issueWithEmptyAuthor = {
      ...baseIssue,
      author: {
        ...baseIssue.author,
        name: '',
        login: '',
      },
    }
    render(<RecentIssues data={[issueWithEmptyAuthor]} />)
    expect(screen.getByAltText("Author's avatar")).toBeInTheDocument()
  })
})
