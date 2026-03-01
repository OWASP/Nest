export const mockProjectDetailsData = {
  project: {
    contributorsCount: 1200,
    entityLeaders: [
      {
        description: 'Project Leader',
        memberName: 'Alice',
        member: {
          id: '1',
          login: 'alice',
          name: 'Alice',
          avatarUrl: 'https://avatars.githubusercontent.com/u/12345?v=4',
        },
      },
    ],
    entityChannels: [
      {
        name: 'project-security',
        slackChannelId: 'C456DEF',
      },
    ],
    forksCount: 10,
    healthMetricsList: [
      {
        openIssuesCount: 5,
        unassignedIssuesCount: 2,
        unansweredIssuesCount: 1,
        openPullRequestsCount: 3,
        starsCount: 20,
        forksCount: 10,
        lastCommitDays: 5,
        lastReleaseDays: 10,
        score: 85,
      },
    ],
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
    topics: ['graphql', 'django', 'backend'],
    type: 'Tool',
    updatedAt: '2025-02-07T12:34:56Z',
    url: 'https://github.com/example-project',
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
        repositoryName: 'Project Repo 1',
        organizationName: 'OWASP',
        createdAt: '2025-03-01T10:00:00Z',
        url: 'https://github.com/OWASP/repo-one/milestone/1',
      },
    ],
    recentPullRequests: [
      {
        id: 'mock-project-pr-1',
        author: {
          avatarUrl: 'https://avatars.githubusercontent.com/u/11111?v=4',
          login: 'user1',
        },
        createdAt: 1727390000,
        title: 'Test Pull Request 1',
        url: 'https://github.com/test-org/test-repo-1/pull/1',
      },
      {
        id: 'mock-project-pr-2',
        author: {
          avatarUrl: 'https://avatars.githubusercontent.com/u/22222?v=4',
          login: 'user2',
        },
        createdAt: 1727380000,
        title: 'Test Pull Request 2',
        url: 'https://github.com/test-org/test-repo-2/pull/2',
      },
    ],
  },
  topContributors: Array.from({ length: 15 }, (_, i) => ({
    avatarUrl: `https://avatars.githubusercontent.com/avatar${i + 1}.jpg`,
    login: `contributor${i + 1}`,
    name: `Contributor ${i + 1}`,
  })),
}
