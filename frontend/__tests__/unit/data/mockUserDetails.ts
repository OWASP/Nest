export const mockUserDetailsData = {
  user: {
    login: 'testuser',
    name: 'Test User',
    avatarUrl: 'https://example.com/avatar.jpg',
    url: 'https://github.com/testuser',
    bio: 'Test @User',
    company: 'Test Company',
    location: 'Test Location',
    email: 'testuser@example.com',
    followersCount: 10,
    followingCount: 5,
    publicRepositoriesCount: 3,
    createdAt: 1723002473,
    issues: [
      {
        title: 'Test Issue',
        createdAt: 1723002473,
        commentsCount: 5,
        url: 'https://github.com/OWASP/Nest/issues/798',
        repository: {
          key: 'test-repo',
          ownerKey: 'testuser',
        },
      },
    ],
    releases: [
      {
        name: 'v1.0.0',
        tagName: '1.0.0',
        isPreRelease: false,
        publishedAt: 1723002473,
        repository: {
          key: 'test-repo',
          ownerKey: 'testuser',
        },
        url: 'https://github.com/testuser/test-repo/releases/tag/1.0.0',
      },
    ],
  },
  recentPullRequests: [
    {
      title: 'Test Pull Request',
      createdAt: 1723002473,
      url: 'https://github.com/testuser/test-repo/pull/1',
    },
  ],
  topContributedRepositories: [
    {
      key: 'test-repo',
      name: 'Test Repo',
      url: 'https://github.com/testuser/test-repo',
      starsCount: 10,
      forksCount: 5,
      openIssuesCount: 3,
      subscribersCount: 2,
      contributorsCount: 1,
    },
  ],
}
