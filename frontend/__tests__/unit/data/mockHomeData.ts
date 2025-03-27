export const mockGraphQLData = {
  recentProjects: [
    {
      createdAt: '2024-12-06T20:46:54+00:00',
      key: 'gamesec-framework',
      leaders: ['Project Leader1', 'Project Leader2'],
      name: 'OWASP GameSec Framework',
      type: 'documentation',
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
      imageUrl: 'https://example.com/owasp-foundation.png',
    },
  ],
  recentChapters: [
    {
      createdAt: '2024-12-14T06:44:54+00:00',
      key: 'sivagangai',
      leaders: ['Chapter Leader1', 'Chapter Leader2'],
      name: 'OWASP Sivagangai',
      suggestedLocation: 'Sivagangai, Tamil Nadu, India',
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
      commentsCount: 1,
      createdAt: '2024-12-14T06:44:54+00:00',
      number: 177,
      title: 'Documentation : Project Setup Documentation Update',
      author: {
        avatarUrl: 'https://avatars.githubusercontent.com/u/134638667?v=4',
        url: 'https://github.com/arkid15r',
        name: 'Raj gupta',
      },
    },
  ],
  recentReleases: [
    {
      author: null,
      isPreRelease: false,
      name: 'v0.9.2',
      publishedAt: '2024-12-13T14:43:46+00:00',
      tagName: 'v0.9.2',
    },
  ],
  statsOverview: {
    activeChaptersStats: 540,
    activeProjectsStats: 95,
    countriesStats: 245,
    contributorsStats: 9673,
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
}

export const mockAlgoliaData = {
  hits: [
    {
      objectID: '539',
      idx_name: 'OWASP Nagoya',
      idx_suggested_location: 'Nagoya, Aichi Prefecture, Japan',
      idx_region: 'Asia',
      idx_top_contributors: [
        {
          avatar_url: 'https://avatars.githubusercontent.com/u/58754211?v=4',
          contributions_count: 286,
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
