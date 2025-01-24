export const mockProjectDetailsData = {
  name: 'Test Project',
  description: 'This is a test project description',
  type: 'Tool',
  level: 'Flagship',
  organizations: 'OWASP',
  leaders: ['Leader 1', 'Leader 2'],
  updated_at: 1625097600,
  url: 'https://example.com',
  contributors_count: 50,
  forks_count: 20,
  stars_count: 100,
  issues_count: 10,
  is_active: true,
  repositories_count: 2,
  summary: 'This is a summary of the test project.',
  languages: Array.from({ length: 15 }, (_, i) => `Language ${i + 1}`),
  topics: Array.from({ length: 15 }, (_, i) => `Topic ${i + 1}`),
  top_contributors: Array.from({ length: 15 }, (_, i) => ({
    name: `Contributor ${i + 1}`,
    login: `contributor${i + 1}`,
    avatar_url: `https://example.com/avatar${i + 1}.jpg`,
    contributions_count: 30 - i,
  })),
  issues: [
    {
      title: 'Issue 1',
      author: { name: 'Author 1', avatar_url: 'https://example.com/author1.jpg' },
      created_at: 1625097600,
      comments_count: 5,
    },
  ],
  releases: [
    {
      name: 'Release 1.0',
      author: { name: 'Author 1', avatar_url: 'https://example.com/author1.jpg' },
      published_at: 1625097600,
      tag_name: 'v1.0',
    },
  ],
}
export const mockProjectDetailsDataGQL = {
  project: {
    name: 'Test Project',
    recentReleases: [
      {
        name: 'Release 1.0',
        tagName: 'v1.0',
        isPreRelease: false,
        publishedAt: '2023-01-01T00:00:00Z',
        author: {
          avatarUrl: 'https://example.com/avatar1.png',
          name: 'Author 1',
        },
      },
      {
        name: 'Release 2.0',
        tagName: 'v2.0',
        isPreRelease: true,
        publishedAt: '2023-06-01T00:00:00Z',
        author: {
          avatarUrl: 'https://example.com/avatar2.png',
          name: 'Author 2',
        },
      },
    ],
    recentIssues: [
      {
        title: 'Issue 1',
        commentsCount: 5,
        createdAt: '2023-05-01T12:00:00Z',
        author: {
          avatarUrl: 'https://example.com/avatar3.png',
          name: 'Author 3',
        },
      },
      {
        title: 'Issue 2',
        commentsCount: 2,
        createdAt: '2023-07-01T14:30:00Z',
        author: {
          avatarUrl: 'https://example.com/avatar4.png',
          name: 'Author 4',
        },
      },
    ],
  },
}
