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
    project: {
      key: 'test-project',
      name: 'Test Project',
    },
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
    recentMilestones: [
      {
        author: {
          avatarUrl: 'https://avatars.githubusercontent.com/u/33333?v=4',
          login: 'milestone-author1',
          name: 'Milestone Author 1',
        },
        title: 'v2.0.0 Release',
        openIssuesCount: 5,
        closedIssuesCount: 15,
        repositoryName: 'Repo One',
        organizationName: 'OWASP',
        createdAt: '2025-03-01T10:00:00Z',
        url: 'https://github.com/OWASP/repo-one/milestone/1',
      },
    ],
  },
  recentPullRequests: [
    {
      id: 'mock-repo-pr-1',
      title: 'Test Pull Request 1',
      createdAt: 1727390000,
      url: 'https://github.com/test-org/test-repo-1/pull/1',
      author: {
        login: 'user1',
        avatarUrl: 'https://avatars.githubusercontent.com/u/11111?v=4',
      },
    },
    {
      id: 'mock-repo-pr-2',
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
    login: `contributor${i + 1}`,
    name: `Contributor ${i + 1}`,
  })),
}
