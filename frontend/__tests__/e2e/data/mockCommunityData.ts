export const mockCommunityData = {
  data: {
    recentChapters: [
      {
        id: '1',
        createdAt: '2025-03-18T01:03:09+00:00',
        key: 'chapter_1',
        leaders: ['Leader 1', 'Leader 3'],
        name: 'Chapter 1',
        suggestedLocation: 'Pune, Maharashtra, India',
      },
      {
        id: '2',
        createdAt: '2025-03-13T00:01:01+00:00',
        key: 'chapter_2',
        leaders: ['Leader 1', 'Leader 2'],
        name: 'Chapter 2',
        suggestedLocation: 'Location 2',
      },
      {
        id: '3',
        createdAt: '2025-02-25T02:04:57+00:00',
        key: 'chapter_3',
        leaders: ['Leader 1', 'Leader 2'],
        name: 'Chapter 3',
        suggestedLocation: 'Location 3',
      },
    ],
    recentOrganizations: [
      {
        id: '1',
        avatarUrl: 'https://avatars.githubusercontent.com/u/1?v=4',
        login: 'org_1',
        name: 'Organization 1',
      },
      {
        id: '2',
        avatarUrl: 'https://avatars.githubusercontent.com/u/2?v=4',
        login: 'org_2',
        name: 'Organization 2',
      },
    ],
    snapshots: [
      {
        id: '1',
        key: 'snapshot_1',
        title: 'Snapshot 1',
        startAt: '2025-01-01',
        endAt: '2025-01-31',
      },
      {
        id: '2',
        key: 'snapshot_2',
        title: 'Snapshot 2',
        startAt: '2025-02-01',
        endAt: '2025-02-28',
      },
    ],
    topContributors: [
      {
        name: 'Contributor 1',
        login: 'contributor_1',
        avatarUrl: 'https://avatars.githubusercontent.com/u/3531020?v=4',
      },
      {
        name: 'Contributor 2',
        login: 'contributor_2',
        avatarUrl: 'https://avatars.githubusercontent.com/u/862914?v=4',
      },
    ],
    statsOverview: {
      activeChaptersStats: 150,
      activeProjectsStats: 50,
      contributorsStats: 5000,
      countriesStats: 100,
      slackWorkspaceStats: 35000,
    },
  },
}
