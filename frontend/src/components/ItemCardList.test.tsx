import React from 'react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ItemCardList from './ItemCardList'
import '@testing-library/jest-dom'

const mockRenderDetails = () => <div>Details</div>

const mockData = [
  {
    title: 'Sample Issue',
    createdAt: '2025-01-01T00:00:00Z',
    commentsCount: 5,
    organizationName: 'Org1',
    publishedAt: '2025-01-01T00:00:00Z',
    repositoryName: 'repo1',
    tagName: 'bug',
    openIssuesCount: 10,
    closedIssuesCount: 2,
    author: {
      avatarUrl: 'https://via.placeholder.com/24',
      login: 'user123',
      name: 'User Name',
    },
    url: 'https://example.com',
  },
  {
    title: 'Another Issue',
    createdAt: '2025-02-01T00:00:00Z',
    commentsCount: 0,
    organizationName: 'Org2',
    publishedAt: '2025-02-01T00:00:00Z',
    repositoryName: 'repo2',
    tagName: '',
    openIssuesCount: 3,
    closedIssuesCount: 1,
    author: {
      avatarUrl: 'https://via.placeholder.com/24',
      login: 'user456',
      name: 'Another User',
    },
    url: 'https://example2.com',
  },
]

describe('ItemCardList', () => {
  test('renders successfully with minimal required props', () => {
    render(<ItemCardList title="Issues" data={mockData} renderDetails={mockRenderDetails} />)
    expect(screen.getByText('Issues')).toBeInTheDocument()
    expect(screen.getByText('Sample Issue')).toBeInTheDocument()
  })

  test('renders "Nothing to display" when data is empty', () => {
    render(<ItemCardList title="Empty Test" data={[]} renderDetails={mockRenderDetails} />)
    expect(screen.getByText('Nothing to display.')).toBeInTheDocument()
  })

  test('renders all data items', () => {
    render(<ItemCardList title="All Items" data={mockData} renderDetails={mockRenderDetails} />)
    expect(screen.getByText('Sample Issue')).toBeInTheDocument()
    expect(screen.getByText('Another Issue')).toBeInTheDocument()
  })

  test('renders author details correctly', () => {
    render(<ItemCardList title="Author Test" data={mockData} renderDetails={mockRenderDetails} />)
    expect(screen.getByAltText('User Name')).toBeInTheDocument()
    expect(screen.getByAltText('Another User')).toBeInTheDocument()
    expect(screen.getByText('user123')).toBeInTheDocument()
  })

  test('renders tag if tagName is present', () => {
    render(<ItemCardList title="Tag Test" data={mockData} renderDetails={mockRenderDetails} />)
    // Should display 'bug' tag for first item
    expect(screen.getByText('bug')).toBeInTheDocument()
    // For second item tagName is empty string, so tag should not be displayed
    expect(screen.queryByText('')).not.toBeInTheDocument()
  })

  test('renders links with correct href and opens in new tab', () => {
    render(<ItemCardList title="Link Test" data={mockData} renderDetails={mockRenderDetails} />)
    const link = screen.getByText('Sample Issue').closest('a')
    expect(link).toHaveAttribute('href', 'https://example.com')
    expect(link).toHaveAttribute('target', '_blank')
  })

  test('renders renderDetails output inside each item', () => {
    render(<ItemCardList title="Details Test" data={mockData} renderDetails={mockRenderDetails} />)
    // The mocked renderDetails component returns 'Details'
    expect(screen.getAllByText('Details').length).toBe(mockData.length)
  })

  // Add more tests here if your component supports more props or behaviors
})