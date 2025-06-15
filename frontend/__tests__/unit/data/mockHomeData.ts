export const mockGraphQLData = {
  recentProjects: [
    {
      createdAt: '2024-12-06T20:46:54+00:00',
      key: 'gamesec-framework',
      leaders: ['Project Leader1', 'Project Leader2'],
      name: 'OWASP GameSec Framework',
      type: 'Tool',
      url: `/projects/gamesec-framework`,
    },
    {
      createdAt: '2024-12-06T20:46:54+00:00',
      key: 'owasp-project-2',
      leaders: ['Project Leader1', 'Project Leader2'],
      name: 'OWASP project 2',
      type: 'Documentation',
      url: `/projects/owasp-project-2`,
    },
    {
      createdAt: '2024-12-06T20:46:54+00:00',
      key: 'owasp-project-3',
      leaders: ['Project Leader1', 'Project Leader2'],
      name: 'OWASP project 3',
      type: 'Code',
      url: `/projects/owasp-project-3`,
    },
    {
      createdAt: '2024-12-06T20:46:54+00:00',
      key: 'owasp-project-4',
      leaders: ['Project Leader1', 'Project Leader2'],
      name: 'OWASP project 4',
      type: 'Other',
      url: `/projects/owasp-project-4`,
    },
    {
      createdAt: '2024-12-06T20:46:54+00:00',
      key: 'owasp-project-5',
      leaders: ['Project Leader1', 'Project Leader2'],
      name: 'OWASP project 5',
      type: '',
      url: `/projects/owasp-project-5`,
    },
  ],
  recentPosts: [
    {
      authorName: 'Author 1',
      authorImageUrl: 'https://owasp.org/assets/images/people/author1.png',
      publishedAt: '2024-12-14T06:44:54+00:00',
      title: 'Post 1',
      url: 'https://owasp.org/blog/post-1.html',
    },
  ],
  sponsors: [
    {
      name: 'OWASP Foundation',
      imageUrl: 'https://avatars.githubusercontent.com/owasp-foundation.png',
    },
  ],
  recentChapters: [
    {
      createdAt: '2024-12-14T06:44:54+00:00',
      key: 'sivagangai',
      leaders: ['Chapter Leader1', 'Chapter Leader2'],
      name: 'OWASP Sivagangai',
      suggestedLocation: 'Sivagangai, Tamil Nadu, India',
      url: `/chapters/sivagangai`,
    },
  ],
  topContributors: [
    {
      name: 'OWASP Foundation',
      login: 'OWASPFoundation',
      contributionsCount: 27952,
      avatarUrl: 'https://avatars.githubusercontent.com/u/7461777?v=4',
    },
  ],
  recentIssues: [
    {
      createdAt: '2024-12-14T06:44:54+00:00',
      number: 177,
      title: 'Documentation : Project Setup Documentation Update',
      author: {
        avatarUrl: 'https://avatars.githubusercontent.com/u/134638667?v=4',
        url: 'https://github.com/arkid15r',
        name: 'Raj gupta',
      },
      url: 'https://github,com/owasp/owasp-nest/issues/177',
    },
  ],
  recentReleases: [
    {
      author: {
        avatarUrl: 'https://avatars.githubusercontent.com/u/134638667?v=4',
        login: 'user',
      },
      isPreRelease: false,
      name: 'v0.9.2',
      publishedAt: '2024-12-13T14:43:46+00:00',
      tagName: 'v0.9.2',
      url: 'https://github.com/owasp/owasp-nest/releases/tag/v0.9.2',
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
      repositoryName: 'Home Repo One',
      organizationName: 'OWASP',
      createdAt: '2025-03-01T10:00:00Z',
      url: 'https://github.com/OWASP/repo-one/milestone/1',
    },
  ],
  statsOverview: {
    activeChaptersStats: 250,
    activeProjectsStats: 90,
    countriesStats: 240,
    contributorsStats: 9600,
    slackWorkspaceStats: 31500,
  },
  upcomingEvents: [
    {
      category: 'Category 1',
      endDate: '2025-02-28',
      name: 'Event 1',
      startDate: '2025-02-27',
      summary: 'Event Summary',
      suggestedLocation: 'Location 1',
      url: 'https://nest.owasp.org/events/event-1',
    },
  ],
  recentPullRequests: [
    {
      createdAt: '2025-03-25T10:00:00Z',
      title: 'Fix authentication bug',
      author: {
        name: 'John Doe',
        avatarUrl: 'https://avatars.githubusercontent.com/u/58754215?v=4',
      },
      repositoryName: 'Test Repo 1',
      url: 'https://github.com/example/repo/pull/1',
    },
    {
      createdAt: '2025-03-24T15:30:00Z',
      title: 'Add new feature',
      author: {
        login: 'jane-smith',
        avatarUrl: 'https://avatars.githubusercontent.com/u/58754221?v=4',
      },
      repositoryName: 'Test Repo 2',
      url: 'https://github.com/example/repo/pull/2',
    },
  ],
}

export const mockAlgoliaData = {
  hits: [
    {
      objectID: '539',
      name: 'OWASP Nagoya',
      suggestedLocation: 'Nagoya, Aichi Prefecture, Japan',
      region: 'Asia',
      topContributors: [
        {
          avatarUrl: 'https://avatars.githubusercontent.com/u/58754211?v=4',
          contributionsCount: 286,
          login: 'isanori-sakanashi-owasp',
          name: 'Isanori Sakanashi',
        },
      ],
      _geoloc: {
        lat: 35.1851045,
        lng: 136.8998438,
      },
    },
  ],
  nbPages: 12,
}
