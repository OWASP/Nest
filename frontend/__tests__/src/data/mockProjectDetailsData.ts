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
        publishedAt: '2023-09-10T20:52:27+00:00',
        author: {
          avatarUrl: 'https://example.com/avatar1.png',
          name: 'Author One',
          __typename: 'UserType',
        },
        __typename: 'ReleaseType',
      },
      {
        name: 'Release 2.0',
        tagName: 'v2.0',
        isPreRelease: false,
        publishedAt: '2023-08-17T20:44:12+00:00',
        author: {
          avatarUrl: 'https://example.com/avatar2.png',
          name: 'Author Two',
          __typename: 'UserType',
        },
        __typename: 'ReleaseType',
      },
      {
        name: 'Release 3.0',
        tagName: 'v3.0',
        isPreRelease: false,
        publishedAt: '2023-07-29T02:37:39+00:00',
        author: {
          avatarUrl: 'https://example.com/avatar3.png',
          name: 'Author Three',
          __typename: 'UserType',
        },
        __typename: 'ReleaseType',
      },
    ],
    recentIssues: [
      {
        title: 'Issue 1: Bug in Feature A',
        commentsCount: 0,
        createdAt: '2024-12-11T07:41:50+00:00',
        author: {
          avatarUrl: 'https://example.com/issue-author1.png',
          name: 'Issue Author One',
          __typename: 'UserType',
        },
        __typename: 'IssueType',
      },
      {
        title: 'Issue 2: Error in Module B',
        commentsCount: 3,
        createdAt: '2024-11-08T18:16:54+00:00',
        author: {
          avatarUrl: 'https://example.com/issue-author2.png',
          name: 'Issue Author Two',
          __typename: 'UserType',
        },
        __typename: 'IssueType',
      },
      {
        title: 'Issue 3: Request for Enhancement',
        commentsCount: 1,
        createdAt: '2024-10-31T17:36:46+00:00',
        author: {
          avatarUrl: 'https://example.com/issue-author3.png',
          name: 'Issue Author Three',
          __typename: 'UserType',
        },
        __typename: 'IssueType',
      },
    ],
    __typename: 'ProjectType',
  },
}
