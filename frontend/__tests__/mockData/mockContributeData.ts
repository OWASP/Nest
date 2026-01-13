import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime.js'

dayjs.extend(relativeTime)

export const mockContributeData = {
  issues: [
    {
      commentsCount: 1,
      createdAt: dayjs().subtract(4, 'months').unix(),
      hint: 'Hint',
      labels: [],
      objectID: '9180',
      projectKey: 'project-nest',
      projectName: 'Owasp Nest',
      repositoryLanguages: ['Python', 'TypeScript'],
      summary: 'This is a summary of Contribution 1',
      title: 'Contribution 1',
      updatedAt: 1734727031,
      url: 'https://github.com/OWASP/Nest/issues/225',
    },
  ],
}
