export const mockProjectDetailsData = {
  project: {
    contributorsCount: 120,
    forksCount: 10,
    issuesCount: 10,
    isActive: true,
    key: "example-project",
    languages: ["Python", "GraphQL", "JavaScript"],
    leaders: ["alice", "bob"],
    level: "Intermediate",
    name: "Test Project",
    repositoriesCount: 3,
    starsCount: 10,
    summary: "An example project showcasing GraphQL and Django integration.",
    topContributors: Array.from({ length: 15 }, (_, i) => ({
      avatarUrl: `https://example.com/avatar${i + 1}.jpg`,
      contributionsCount: 30 - i,
      login: `contributor${i + 1}`,
      name: `Contributor ${i + 1}`,
    })),
    topics: ["graphql", "django", "backend"],
    type: "Open Source",
    updatedAt: "2025-02-07T12:34:56Z",
    url: "https://github.com/example-project",
    recentReleases: [
      {
        name: "v1.2.0",
        tagName: "v1.2.0",
        isPreRelease: false,
        publishedAt: "2025-01-20T10:00:00Z",
        author: {
          avatarUrl: "https://example.com/avatar3.png",
          login: "charlie_dev",
          name: "Charlie Dev"
        }
      }
    ],
    recentIssues: [
      {
        title: "Fix authentication bug",
        commentsCount: 5,
        createdAt: "2025-02-05T15:20:30Z",
        author: {
          avatarUrl: "https://example.com/avatar4.png",
          login: "dave_debugger",
          name: "Dave Debugger"
        }
      }
    ],
    repositories: [
      {
        contributorsCount: 40,
        forksCount: 12,
        key: "repo-1",
        name: "Repo One",
        openIssuesCount: 6,
        starsCount: 95,
        subscribersCount: 15,
        url: "https://github.com/example-project/repo-1"
      },
      {
        contributorsCount: 30,
        forksCount: 8,
        key: "repo-2",
        name: "Repo Two",
        openIssuesCount: 3,
        starsCount: 60,
        subscribersCount: 10,
        url: "https://github.com/example-project/repo-2"
      }
    ]
  }
};
