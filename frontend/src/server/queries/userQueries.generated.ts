import * as Types from '../../types/__generated__/graphql';

export type GetLeaderDataQueryVariables = Types.Exact<{
  key: Types.Scalars['String']['input'];
}>;


export type GetLeaderDataQuery = { user: { __typename: 'UserNode', avatarUrl: string, login: string, name: string } | null };

export type GetUserDataQueryVariables = Types.Exact<{
  key: Types.Scalars['String']['input'];
}>;


export type GetUserDataQuery = { recentIssues: Array<{ __typename: 'IssueNode', createdAt: unknown, organizationName: string | null, repositoryName: string | null, title: string, url: string }>, recentMilestones: Array<{ __typename: 'MilestoneNode', title: string, openIssuesCount: number, closedIssuesCount: number, repositoryName: string | null, organizationName: string | null, createdAt: unknown, url: string }>, recentPullRequests: Array<{ __typename: 'PullRequestNode', createdAt: unknown, organizationName: string | null, repositoryName: string | null, title: string, url: string }>, recentReleases: Array<{ __typename: 'ReleaseNode', isPreRelease: boolean, name: string, publishedAt: unknown | null, organizationName: string | null, repositoryName: string | null, tagName: string, url: string }>, topContributedRepositories: Array<{ __typename: 'RepositoryNode', contributorsCount: number, forksCount: number, key: string, name: string, openIssuesCount: number, starsCount: number, subscribersCount: number, url: string, organization: { __typename: 'OrganizationNode', login: string } | null }>, user: { __typename: 'UserNode', avatarUrl: string, bio: string, company: string, contributionsCount: number, createdAt: number, email: string, followersCount: number, followingCount: number, issuesCount: number, location: string, login: string, name: string, publicRepositoriesCount: number, releasesCount: number, updatedAt: number, url: string } | null };

export type GetUserMetadataQueryVariables = Types.Exact<{
  key: Types.Scalars['String']['input'];
}>;


export type GetUserMetadataQuery = { user: { __typename: 'UserNode', bio: string, login: string, name: string } | null };
