export const mockSnapshotDetailsData = {
  snapshot: {
    title: 'New Snapshot',
    key: '2024-12',
    updatedAt: '2025-03-02T20:33:46.880330+00:00',
    createdAt: '2025-03-01T22:00:34.361937+00:00',
    startAt: '2024-12-01T00:00:00+00:00',
    endAt: '2024-12-31T22:00:30+00:00',
    status: 'completed',
    errorMessage: '',
    newReleases: [
      {
        name: 'v0.9.2',
        publishedAt: '2024-12-13T14:43:46+00:00',
        tagName: 'v0.9.2',
        projectName: 'test-project-1',
      },
      {
        name: 'Latest pre-release',
        publishedAt: '2024-12-13T13:17:30+00:00',
        tagName: 'pre-release',
        projectName: 'test-project-2',
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
            contributionsCount: 170,
            login: 'arkid15r',
            name: 'Arkadii Yakovets',
          },
          {
            avatarUrl: 'https://avatars.githubusercontent.com/u/97700473?v=4',
            contributionsCount: 5,
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
        createdAt: '2024-07-30T10:07:33+00:00',
        suggestedLocation: 'Sivagangai, Tamil Nadu, India',
        region: 'Asia',
        summary:
          'OWASP Sivagangai is a new local chapter that focuses on AI and application security...',
        topContributors: [
          {
            avatarUrl: 'https://avatars.githubusercontent.com/u/95969896?v=4',
            contributionsCount: 14,
            login: 'acs-web-tech',
            name: 'P.ARUN',
          },
          {
            avatarUrl: 'https://avatars.githubusercontent.com/u/56408064?v=4',
            contributionsCount: 1,
            login: 'test-user-1',
            name: '',
          },
        ],
        updatedAt: 1727353371.0,
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
      startAt: '2024-12-01T00:00:00+00:00',
      endAt: '2024-12-31T22:00:30+00:00',
    },
  ],
}
