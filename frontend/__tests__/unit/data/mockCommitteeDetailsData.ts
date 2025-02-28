export const mockCommitteeDetailsData = {
  committee: {
    name: 'Test Committee',
    updatedAt: 1734103212.0,
    leaders: ['Leader 1', 'Leader 2'],
    url: 'https://owasp.org/test-committee',
    summary: 'This is a test committee summary.',
    topContributors: [
      {
        avatarUrl: 'https://avatars.githubusercontent.com/u/7319658?v=4',
        contributionsCount: 2157,
        login: 'contributor1',
        name: 'Contributor 1',
        __typename: 'UserNode',
      },
      {
        avatarUrl: 'https://avatars.githubusercontent.com/u/321605?v=4',
        contributionsCount: 309,
        login: 'contributor2',
        name: 'Contributor 2',
        __typename: 'UserNode',
      },
    ],
    relatedUrls: ['https://twitter.com/testcommittee', 'https://github.com/testcommittee'],
    __typename: 'CommitteeNode',
  },
}
