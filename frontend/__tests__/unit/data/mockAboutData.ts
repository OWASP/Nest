export const mockAboutData = {
  project: {
    contributorsCount: 1200,
    issuesCount: 40,
    forksCount: 60,
    starsCount: 890,
    key: 'nest',
    topContributors: Array.from({ length: 15 }, (_, i) => ({
      avatar_url: `https://example.com/avatar${i + 1}.jpg`,
      contributions_count: 30 - i,
      login: `contributor${i + 1}`,
      name: `Contributor ${i + 1}`,
    })),
    is_active: true,
    languages: ['Python', 'GraphQL', 'JavaScript'],
    level: 'Lab',
    name: 'Test Project',
    repositories_count: 3,
    summary: 'Test summary',
    topics: ['security', 'web'],
    type: 'Tool',
    url: 'https://github.com/test-project',
  },
  users: {
    arkid15r: {
      avatarUrl: 'https://avatars.githubusercontent.com/u/2201626?v=4',
      company: 'OWASP',
      name: 'Arkadii Yakovets',
      url: '/community/users/arkid15r',
    },
    kasya: {
      avatarUrl: 'https://avatars.githubusercontent.com/u/5873153?v=4',
      company: 'skillstruck',
      name: 'Kate Golovanova',
      url: '/community/users/kasya',
    },
    mamicidal: {
      avatarUrl: 'https://avatars.githubusercontent.com/u/112129498?v=4',
      company: 'OWASP',
      name: 'Starr Brown',
      url: '/community/users/mamicidal',
    },
  },
}
