import * as Types from '../../types/__generated__/graphql';

export type GetRepositoryDataQueryVariables = Types.Exact<{
  repositoryKey: Types.Scalars['String']['input'];
  organizationKey: Types.Scalars['String']['input'];
}>;


export type GetRepositoryDataQuery = { repository: { __typename: 'RepositoryNode', commitsCount: number, contributorsCount: number, createdAt: unknown, description: string, forksCount: number, key: string, languages: Array<string>, license: string, name: string, openIssuesCount: number, size: number, starsCount: number, topics: Array<string>, updatedAt: unknown, url: string, issues: Array<{ __typename: 'IssueNode', organizationName: string | null, repositoryName: string | null, createdAt: unknown, title: string, author: { __typename: 'UserNode', avatarUrl: string, login: string, name: string } | null }>, organization: { __typename: 'OrganizationNode', login: string } | null, project: { __typename: 'ProjectNode', key: string, name: string } | null, releases: Array<{ __typename: 'ReleaseNode', isPreRelease: boolean, name: string, organizationName: string | null, publishedAt: unknown | null, repositoryName: string | null, tagName: string, author: { __typename: 'UserNode', avatarUrl: string, name: string, login: string } | null }>, recentMilestones: Array<{ __typename: 'MilestoneNode', title: string, openIssuesCount: number, closedIssuesCount: number, repositoryName: string | null, organizationName: string | null, createdAt: unknown, url: string, author: { __typename: 'UserNode', avatarUrl: string, login: string, name: string } | null }> } | null, topContributors: Array<{ __typename: 'RepositoryContributorNode', avatarUrl: string, login: string, name: string }>, recentPullRequests: Array<{ __typename: 'PullRequestNode', createdAt: unknown, organizationName: string | null, repositoryName: string | null, title: string, url: string, author: { __typename: 'UserNode', avatarUrl: string, login: string, name: string } | null }> };

export type GetRepositoryMetadataQueryVariables = Types.Exact<{
  repositoryKey: Types.Scalars['String']['input'];
  organizationKey: Types.Scalars['String']['input'];
}>;


export type GetRepositoryMetadataQuery = { repository: { __typename: 'RepositoryNode', description: string, name: string } | null };
