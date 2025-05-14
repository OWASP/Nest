export const mockRepositoryData = {
  repository: {
    name: 'Test Repo',
    updatedAt: '2024-01-01T00:00:00Z',
    license: 'MIT',
    size: 1200,
    url: 'https://github.com/test-repo',
    commitsCount: 10,
    contributorsCount: 5,
    forksCount: 3000,
    openIssuesCount: 2,
    starsCount: 50000,
    languages: ['JavaScript', 'TypeScript'],
    topics: ['web', 'security'],
    description: 'A sample test repository',
    createdAt: '2023-12-15T00:00:00Z',
    issues: [
      {
        title: 'Bug fix required',
        createdAt: '2024-01-02T10:00:00Z',
        repositoryName: 'test-repo-2',
        author: {
          avatarUrl: 'https://avatars.githubusercontent.com/avatar.jpg',
          name: 'Test User 1',
          login: 'user1',
        },
      },
    ],
    releases: [
      {
        name: 'v1.0.0',
        tagName: 'v1.0.0',
        isPreRelease: false,
        publishedAt: '2024-01-01T12:00:00Z',
        author: {
          avatarUrl: 'https://avatars.githubusercontent.com/avatar.jpg',
          name: 'Test User 2',
          login: 'user2',
        },
      },
    ],
  },
  recentPullRequests: [
    {
      title: 'Test Pull Request 1',
      createdAt: 1727390000,
      url: 'https://github.com/test-org/test-repo-1/pull/1',
      author: {
        login: 'user1',
        avatarUrl: 'https://avatars.githubusercontent.com/u/11111?v=4',
      },
    },
    {
      title: 'Test Pull Request 2',
      createdAt: 1727380000,
      url: 'https://github.com/test-org/test-repo-2/pull/2',
      author: {
        login: 'user2',
        avatarUrl: 'https://avatars.githubusercontent.com/u/22222?v=4',
      },
    },
  ],
  topContributors: Array.from({ length: 15 }, (_, i) => ({
    avatarUrl: `https://avatars.githubusercontent.com/avatar${i + 1}.jpg`,
    contributionsCount: 30 - i,
    login: `contributor${i + 1}`,
    name: `Contributor ${i + 1}`,
  })),
}
