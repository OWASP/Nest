export const mockProjectDetailsData = {
  project: {
    contributorsCount: 1200,
    forksCount: 10,
    isActive: true,
    issuesCount: 10,
    key: 'example-project',
    languages: ['Python', 'GraphQL', 'JavaScript'],
    leaders: ['alice', 'bob'],
    level: 'Lab',
    name: 'Test Project',
    recentIssues: [
      {
        author: {
          avatarUrl: 'https://avatars.githubusercontent.com/avatar4.png',
          login: 'dave_debugger',
          name: 'Dave Debugger',
          url: 'https://github.com/arkid15r',
        },
        createdAt: '2025-02-05T15:20:30Z',
        repositoryName: 'test-repo',
        title: 'Fix authentication bug',
      },
    ],
    recentReleases: [
      {
        author: {
          avatarUrl: 'https://avatars.githubusercontent.com/avatar3.png',
          login: 'charlie_dev',
          name: 'Charlie Dev',
        },
        isPreRelease: false,
        name: 'v1.2.0',
        publishedAt: '2025-01-20T10:00:00Z',
        tagName: 'v1.2.0',
      },
    ],
    repositories: [
      {
        contributorsCount: 40,
        forksCount: 12,
        key: 'repo-1',
        name: 'Repo One',
        openIssuesCount: 6,
        organization: {
          login: 'OWASP',
        },
        starsCount: 95,
        subscribersCount: 15,
        url: 'https://github.com/example-project/repo-1',
      },
      {
        contributorsCount: 30,
        forksCount: 8,
        key: 'repo-2',
        name: 'Repo Two',
        openIssuesCount: 3,
        organization: {
          login: 'OWASP',
        },
        starsCount: 60,
        subscribersCount: 10,
        url: 'https://github.com/example-project/repo-2',
      },
    ],
    repositoriesCount: 3,
    starsCount: 2200,
    summary: 'An example project showcasing GraphQL and Django integration.',
    topContributors: Array.from({ length: 15 }, (_, i) => ({
      avatarUrl: `https://avatars.githubusercontent.com/avatar${i + 1}.jpg`,
      contributionsCount: 30 - i,
      login: `contributor${i + 1}`,
      name: `Contributor ${i + 1}`,
    })),
    topics: ['graphql', 'django', 'backend'],
    type: 'Tool',
    updatedAt: '2025-02-07T12:34:56Z',
    url: 'https://github.com/example-project',
    openMilestones: [
      {
        author: {
          avatarUrl: 'https://avatars.githubusercontent.com/u/33333?v=4',
          login: 'milestone-author1',
          name: 'Milestone Author 1',
        },
        title: 'v2.0.0 Release',
        openIssuesCount: 5,
        closedIssuesCount: 15,
        repositoryName: 'Project Repo One',
        organizationName: 'OWASP',
        createdAt: '2025-03-01T10:00:00Z',
        url: 'https://github.com/OWASP/repo-one/milestone/1',
      },
    ],
    closedMilestones: [
      {
        author: {
          avatarUrl: 'https://avatars.githubusercontent.com/u/66666?v=4',
          login: 'milestone-author4',
          name: 'Milestone Author 4',
        },
        title: 'Security Updates',
        openIssuesCount: 0,
        closedIssuesCount: 12,
        repositoryName: 'Project Repo Two',
        organizationName: 'OWASP',
        createdAt: '2024-11-15T16:45:00Z',
        url: 'https://github.com/OWASP/repo-two/milestone/4',
      },
    ],
  },
  recentPullRequests: [
    {
      author: {
        avatarUrl: 'https://avatars.githubusercontent.com/u/11111?v=4',
        login: 'user1',
      },
      createdAt: 1727390000,
      title: 'Test Pull Request 1',
      url: 'https://github.com/test-org/test-repo-1/pull/1',
    },
    {
      author: {
        avatarUrl: 'https://avatars.githubusercontent.com/u/22222?v=4',
        login: 'user2',
      },
      createdAt: 1727380000,
      title: 'Test Pull Request 2',
      url: 'https://github.com/test-org/test-repo-2/pull/2',
    },
  ],
}
