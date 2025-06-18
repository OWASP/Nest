export const mockProjectData = {
  projects: [
    {
      healthMetrics: {
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
      objectID: '1',
      name: 'Project 1',
      url: 'https://avatars.githubusercontent.com/project1',
      summary: 'This is a summary of Project 1.',
      level: '1',
      leaders: ['Leader 1'],
      topContributors: [
        {
          avatarUrl: 'https://avatars.githubusercontent.com/avatar1.png',
          contributionsCount: 10,
          login: 'contributor1',
          name: 'Contributor 1',
          projectKey: 'project1',
          projectName: 'Project 1',
        },
      ],
      topics: ['Topic 1'],
      updatedAt: '2023-10-01',
      forksCount: 10,
      key: 'project_1',
      starsCount: 20,
      contributorsCount: 5,
      isActive: true,
    },
  ],
}

export default mockProjectData
