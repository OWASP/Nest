export const mockAboutData = {
  project: {
    contributors_count: 1200,
    issues_count: 40,
    forks_count: 60,
    stars_count: 890,
    key: 'nest',
    top_contributors: Array.from({ length: 15 }, (_, i) => ({
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
}
