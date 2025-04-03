import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime.js'

dayjs.extend(relativeTime)

export const mockContributeData = {
  issues: [
    {
      comments_count: 1,
      created_at: dayjs().subtract(4, 'months').unix(),
      hint: 'Hint',
      labels: [],
      objectID: '9180',
      project_name: 'Owasp Nest',
      project_url: 'https://owasp.org/www-project-nest',
      repository_languages: ['Python', 'TypeScript'],
      summary: 'This is a summary of Contribution 1',
      title: 'Contribution 1',
      updated_at: 1734727031,
      url: 'https://github.com/OWASP/Nest/issues/225',
    },
  ],
}
