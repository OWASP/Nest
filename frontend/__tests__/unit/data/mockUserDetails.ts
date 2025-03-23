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
      },
    ],
    releases: [
      {
        isPreRelease: false,
        name: 'v1.0.0',
        publishedAt: 1723002473,
        tagName: '1.0.0',
        url: 'https://github.com/testuser/test-repo/releases/tag/1.0.0',
      },
    ],
  },
  recentPullRequests: [
    {
      createdAt: 1723002473,
      title: 'Test Pull Request',
      url: 'https://github.com/testuser/test-repo/pull/1',
    },
  ],
  topContributedRepositories: [
    {
      contributorsCount: 1,
      forksCount: 5,
      key: 'test-repo',
      name: 'Test Repo',
      openIssuesCount: 3,
      starsCount: 10,
      subscribersCount: 2,
      url: 'https://github.com/testuser/test-repo',
    },
  ],
}
