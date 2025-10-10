export const mockChapterDetailsData = {
  chapter: {
    name: 'OWASP Test Chapter',
    suggestedLocation: 'Test City, Test Country',
    region: 'Test Region',
    isActive: true,
    updatedAt: 1652129718,
    url: 'https://owasp.org/test-chapter',
    relatedUrls: [
      'https://discord.com/test',
      'https://www.instagram.com/test',
      'https://www.linkedin.com/test',
      'https://www.youtube.com/test',
      'https://twitter.com/test',
      'https://meetup.com/test',
    ],
    summary: 'This is a test chapter summary.',
    geoLocation: {
      lat: 23.2584857,
      lng: 77.401989,
    },
    establishedYear: 2020,
    key: 'test-chapter',
    entityLeaders: [
      {
        description: 'Chapter Leader',
        memberName: 'Bob',
        member: {
          id: '2',
          login: 'bob',
          name: 'Bob',
          avatarUrl: 'https://avatars.githubusercontent.com/u/67890?v=4',
        },
      },
    ],
  },
  topContributors: Array.from({ length: 15 }, (_, i) => ({
    avatarUrl: `https://avatars.githubusercontent.com/avatar${i + 1}.jpg`,
    login: `contributor${i + 1}`,
    name: `Contributor ${i + 1}`,
  })),
}
