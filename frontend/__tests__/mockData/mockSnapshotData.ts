export const mockSnapshotDetailsData = {
  snapshot: {
    title: 'New Snapshot',
    key: '2024-12',
    updatedAt: 1740944026, // 2025-03-02T20:33:46Z
    createdAt: 1740865234, // 2025-03-01T22:00:34Z
    startAt: 1733011200,
    endAt: 1735689630,
    status: 'completed',
    errorMessage: '',
    newReleases: [
      {
        name: 'v0.9.2',
        publishedAt: 1734101026, // 2024-12-13T14:43:46Z
        tagName: 'v0.9.2',
        projectName: 'test-project-1',
        organizationName: 'owasp',
        repositoryName: 'test-project-1',
        author: {
          id: '1',
          avatarUrl: 'https://avatars.githubusercontent.com/u/2201626?v=4',
          login: 'arkid15r',
          name: 'Arkadii Yakovets',
        },
      },
      {
        name: 'Latest pre-release',
        publishedAt: 1734095850, // 2024-12-13T13:17:30Z
        tagName: 'pre-release',
        projectName: 'test-project-2',
        organizationName: 'owasp',
        repositoryName: 'test-project-2',
        author: {
          id: '2',
          avatarUrl: 'https://avatars.githubusercontent.com/u/97700473?v=4',
          login: 'test-user',
          name: 'test user',
        },
      },
    ],
    newProjects: [
      {
        key: 'nest',
        name: 'OWASP Nest',
        summary:
          'OWASP Nest is a code project aimed at improving how OWASP manages its collection of projects...',
        starsCount: 14,
        forksCount: 19,
        contributorsCount: 14,
        level: 'INCUBATOR',
        isActive: true,
        repositoriesCount: 2,
        topContributors: [
          {
            avatarUrl: 'https://avatars.githubusercontent.com/u/2201626?v=4',
            login: 'arkid15r',
            name: 'Arkadii Yakovets',
          },
          {
            avatarUrl: 'https://avatars.githubusercontent.com/u/97700473?v=4',
            login: 'test-user',
            name: 'test user',
          },
        ],
      },
    ],
    newChapters: [
      {
        key: 'sivagangai',
        name: 'OWASP Sivagangai',
        createdAt: 1722334053, // 2024-07-30T10:07:33Z
        suggestedLocation: 'Sivagangai, Tamil Nadu, India',
        region: 'Asia',
        summary:
          'OWASP Sivagangai is a new local chapter that focuses on AI and application security...',
        topContributors: [
          {
            avatarUrl: 'https://avatars.githubusercontent.com/u/95969896?v=4',
            login: 'acs-web-tech',
            name: 'P.ARUN',
          },
          {
            avatarUrl: 'https://avatars.githubusercontent.com/u/56408064?v=4',
            login: 'test-user-1',
            name: '',
          },
        ],
        updatedAt: 1727353371,
        url: 'https://owasp.org/www-chapter-sivagangai',
        relatedUrls: [],
        geoLocation: {
          lat: 9.9650599,
          lng: 78.7204283237222,
        },
        isActive: true,
      },
    ],
  },
}

export const mockSnapshotData = {
  snapshots: [
    {
      title: 'New Snapshot',
      key: '2024-12',
      startAt: 1733011200,
      endAt: 1735689630,
    },
  ],
}
