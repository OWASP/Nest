export const mockUserDetailsData = {
  user: {
    login: 'testuser',
    name: 'Test User',
    avatarUrl: 'https://avatars.githubusercontent.com/avatar.jpg',
    url: 'https://github.com/testuser',
    bio: 'Test @User',
    company: 'Test Company',
    location: 'Test Location',
    email: 'testuser@example.com',
    followersCount: 10,
    followingCount: 5,
    publicRepositoriesCount: 3,
    createdAt: 1723002473,
    contributionsCount: 100,
    badges: [
      {
        id: '1',
        name: 'Contributor',
        cssClass: 'fa-medal',
        description: 'Active contributor to OWASP projects',
        weight: 1,
      },
      {
        id: '2',
        name: 'Security Expert',
        cssClass: 'fa-shield-alt',
        description: 'Security expertise demonstrated',
        weight: 2,
      },
    ],
    badgeCount: 2,
  },
  recentIssues: [
    {
      title: 'Test Issue',
      createdAt: 1723002473,
      repositoryName: 'test-repo-1',
      url: 'https://github.com/OWASP/Nest/issues/798',
    },
  ],
  recentMilestones: [
    {
      title: 'v2.0.0 Release',
      openIssuesCount: 5,
      closedIssuesCount: 15,
      repositoryName: 'Project Repo 1',
      organizationName: 'OWASP',
      createdAt: '2025-03-01T10:00:00Z',
      url: 'https://github.com/OWASP/repo-one/milestone/1',
    },
  ],
  recentReleases: [
    {
      isPreRelease: false,
      name: 'v1.0.0',
      publishedAt: 1723002473,
      repositoryName: 'test-repo-2',
      tagName: '1.0.0',
      url: 'https://github.com/testuser/test-repo/releases/tag/1.0.0',
    },
  ],
  recentPullRequests: [
    {
      id: 'mock-user-pr-1',
      createdAt: 1723002473,
      repositoryName: 'test-repo-3',
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
