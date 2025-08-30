import * as Types from '../../types/__generated__/graphql';

export type GetOrganizationDataQueryVariables = Types.Exact<{
  login: Types.Scalars['String']['input'];
}>;


export type GetOrganizationDataQuery = { organization: { __typename: 'OrganizationNode', avatarUrl: string, collaboratorsCount: number, company: string, createdAt: unknown, description: string, email: string, followersCount: number, location: string, login: string, name: string, updatedAt: unknown, url: string, stats: { __typename: 'OrganizationStatsNode', totalContributors: number, totalForks: number, totalIssues: number, totalRepositories: number, totalStars: number } } | null, topContributors: Array<{ __typename: 'RepositoryContributorNode', avatarUrl: string, login: string, name: string }>, recentPullRequests: Array<{ __typename: 'PullRequestNode', createdAt: unknown, organizationName: string | null, repositoryName: string | null, title: string, url: string, author: { __typename: 'UserNode', avatarUrl: string, login: string, name: string } | null }>, recentReleases: Array<{ __typename: 'ReleaseNode', name: string, organizationName: string | null, publishedAt: unknown | null, repositoryName: string | null, tagName: string, url: string, author: { __typename: 'UserNode', avatarUrl: string, login: string, name: string } | null }>, recentMilestones: Array<{ __typename: 'MilestoneNode', title: string, openIssuesCount: number, closedIssuesCount: number, repositoryName: string | null, organizationName: string | null, createdAt: unknown, url: string, author: { __typename: 'UserNode', avatarUrl: string, login: string, name: string } | null }>, repositories: Array<{ __typename: 'RepositoryNode', contributorsCount: number, forksCount: number, key: string, name: string, openIssuesCount: number, starsCount: number, url: string, organization: { __typename: 'OrganizationNode', login: string } | null }>, recentIssues: Array<{ __typename: 'IssueNode', createdAt: unknown, organizationName: string | null, repositoryName: string | null, title: string, url: string, author: { __typename: 'UserNode', avatarUrl: string, login: string, name: string } | null }> };

export type GetOrganizationMetadataQueryVariables = Types.Exact<{
  login: Types.Scalars['String']['input'];
}>;


export type GetOrganizationMetadataQuery = { organization: { __typename: 'OrganizationNode', description: string, login: string, name: string } | null };
