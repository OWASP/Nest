export const mockProjectData = {
  projects: [
    {
      objectID: '1',
      name: 'Project 1',
      url: 'https://avatars.githubusercontent.com/project1',
      summary: 'This is a summary of Project 1.',
      level: '1',
      leaders: ['Leader 1'],
      top_contributors: [
        {
          avatarUrl: 'https://avatars.githubusercontent.com/avatar1.png',
          contributionsCount: 10,
          login: 'contributor1',
          name: 'Contributor 1',
          projectName: 'Project 1',
          projectUrl: 'https://avatars.githubusercontent.com/project1',
        },
      ],
      topics: ['Topic 1'],
      updated_at: '2023-10-01',
      forks_count: 10,
      key: 'project_1',
      stars_count: 20,
      contributors_count: 5,
      is_active: true,
    },
  ],
}

export default mockProjectData
