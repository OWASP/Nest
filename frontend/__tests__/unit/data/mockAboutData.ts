export const mockAboutData = {
  project: {
    contributorsCount: 1200,
    issuesCount: 40,
    forksCount: 60,
    starsCount: 890,
    recentMilestones: [
      {
        title: 'NestBot title',
        body: 'NestBot Idea',
        url: 'http/github.com/milestones/5',
        progress: 58,
      },
      {
        title: 'Contribution Hub title',
        body: 'Contribution Hub Idea',
        url: 'http/github.com/milestones/8',
        progress: 75,
      },
      {
        title: 'Project Dashboard title',
        body: 'Project Dashboard Idea',
        url: 'http/github.com/milestones/10',
        progress: 80,
      },
    ],
  },
  topContributors: Array.from({ length: 15 }, (_, i) => ({
    avatarUrl: `https://avatars.githubusercontent.com/avatar${i + 1}.jpg`,
    login: `contributor${i + 1}`,
    name: `Contributor ${i + 1}`,
  })),
  users: {
    arkid15r: {
      avatarUrl: 'https://avatars.githubusercontent.com/u/2201626?v=4',
      login: 'arkid15r',
      name: 'Arkadii Yakovets',
    },
    kasya: {
      avatarUrl: 'https://avatars.githubusercontent.com/u/5873153?v=4',
      login: 'kasya',
      name: 'Kate Golovanova',
    },
    mamicidal: {
      avatarUrl: 'https://avatars.githubusercontent.com/u/112129498?v=4',
      login: 'mamicidal',
      name: 'Starr Brown',
    },
  },
}
