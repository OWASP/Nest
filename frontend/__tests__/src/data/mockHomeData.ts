export const mockGraphQLData = {
  recentProjects: [
    {
      name: 'OWASP GameSec Framework',
      type: 'DOCUMENTATION',
      createdAt: '2024-12-06T20:46:54+00:00',
      key: 'gamesec-framework',
      openIssuesCount: 0,
      repositoriesCount: 1,
      __typename: 'ProjectNode',
    },
  ],
  recentChapters: [
    {
      name: 'OWASP Sivagangai',
      suggestedLocation: 'Sivagangai, Tamil Nadu, India',
      region: 'Asia',
      key: 'sivagangai',
      createdAt: '2024-12-14T06:44:54+00:00',
      topContributors: [
        {
          name: 'P.ARUN',
          __typename: 'RepositoryContributorNode',
        },
      ],
      __typename: 'ChapterNode',
    },
  ],
  topContributors: [
    {
      name: 'OWASP Foundation',
      login: 'OWASPFoundation',
      contributionsCount: 27952,
      avatarUrl: 'https://avatars.githubusercontent.com/u/7461777?v=4',
      __typename: 'RepositoryContributorNode',
    },
  ],
  recentIssue: [
    {
      commentsCount: 1,
      createdAt: '2024-12-14T06:44:54+00:00',
      number: 177,
      title: 'Documentation : Project Setup Documentation Update',
      author: {
        avatarUrl: 'https://avatars.githubusercontent.com/u/134638667?v=4',
        name: 'Raj gupta',
        __typename: 'UserNode',
      },
      __typename: 'IssueNode',
    },
  ],
  recentRelease: [
    {
      author: null,
      isPreRelease: false,
      name: 'v0.9.2',
      publishedAt: '2024-12-13T14:43:46+00:00',
      tagName: 'v0.9.2',
      __typename: 'ReleaseNode',
    },
  ],
  countsOverview: {
    chaptersCount: 540,
    countriesCount: 95,
    activeProjectsCount: 245,
    contributorsCount: 9673,
    __typename: 'CountsType',
  },
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
