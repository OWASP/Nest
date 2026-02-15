export const mockCommunityGraphQLData = {
  recentChapters: [
    {
      id: '1',
      createdAt: '2025-01-01T10:00:00Z',
      key: 'chapter-1',
      leaders: ['Leader 1', 'Leader 2'],
      name: 'OWASP Chapter 1',
      suggestedLocation: 'Location 1',
    },
    {
      id: '2',
      createdAt: '2025-01-02T10:00:00Z',
      key: 'chapter-2',
      leaders: ['Leader 3'],
      name: 'OWASP Chapter 2',
      suggestedLocation: 'Location 2',
    },
  ],
  recentOrganizations: [
    {
      id: 'org1',
      avatarUrl: 'https://example.com/org1.png',
      login: 'org1',
      name: 'Organization 1',
    },
    {
      id: 'org2',
      avatarUrl: 'https://example.com/org2.png',
      login: 'org2',
      name: 'Organization 2',
    },
  ],
  snapshots: [
    {
      id: 'snap1',
      key: 'snapshot-1',
      title: 'Snapshot 1',
      startAt: '2025-01-01',
      endAt: '2025-01-31',
    },
    {
      id: 'snap2',
      key: 'snapshot-2',
      title: 'Snapshot 2',
      startAt: '2025-02-01',
      endAt: '2025-02-28',
    },
  ],
  topContributors: [
    {
      id: 'user1',
      avatarUrl: 'https://example.com/user1.png',
      login: 'user1',
      name: 'User 1',
    },
    {
      id: 'user2',
      avatarUrl: 'https://example.com/user2.png',
      login: 'user2',
      name: 'User 2',
    },
  ],
  statsOverview: {
    activeChaptersStats: 150,
    activeProjectsStats: 50,
    countriesStats: 100,
    contributorsStats: 5000,
  },
}
