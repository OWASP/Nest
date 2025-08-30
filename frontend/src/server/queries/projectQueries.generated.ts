import * as Types from '../../types/__generated__/graphql';

export type GetProjectQueryVariables = Types.Exact<{
  key: Types.Scalars['String']['input'];
}>;


export type GetProjectQuery = { project: { __typename: 'ProjectNode', contributorsCount: number, forksCount: number, issuesCount: number, isActive: boolean, key: string, languages: Array<string>, leaders: Array<string>, level: string, name: string, repositoriesCount: number, starsCount: number, summary: string, topics: Array<string>, type: string, updatedAt: number, url: string, healthMetricsList: Array<{ __typename: 'ProjectHealthMetricsNode', createdAt: unknown, forksCount: number, lastCommitDays: number, lastCommitDaysRequirement: number, lastReleaseDays: number, lastReleaseDaysRequirement: number, openIssuesCount: number, openPullRequestsCount: number, score: number | null, starsCount: number, unassignedIssuesCount: number, unansweredIssuesCount: number }>, recentIssues: Array<{ __typename: 'IssueNode', createdAt: unknown, organizationName: string | null, repositoryName: string | null, title: string, url: string, author: { __typename: 'UserNode', avatarUrl: string, login: string, name: string, url: string } | null }>, recentReleases: Array<{ __typename: 'ReleaseNode', name: string, organizationName: string | null, publishedAt: unknown | null, repositoryName: string | null, tagName: string, url: string, author: { __typename: 'UserNode', avatarUrl: string, login: string, name: string } | null }>, repositories: Array<{ __typename: 'RepositoryNode', contributorsCount: number, forksCount: number, key: string, name: string, openIssuesCount: number, starsCount: number, subscribersCount: number, url: string, organization: { __typename: 'OrganizationNode', login: string } | null }>, recentMilestones: Array<{ __typename: 'MilestoneNode', title: string, openIssuesCount: number, closedIssuesCount: number, repositoryName: string | null, organizationName: string | null, createdAt: unknown, url: string, author: { __typename: 'UserNode', avatarUrl: string, login: string, name: string } | null }>, recentPullRequests: Array<{ __typename: 'PullRequestNode', createdAt: unknown, organizationName: string | null, repositoryName: string | null, title: string, url: string, author: { __typename: 'UserNode', avatarUrl: string, login: string, name: string } | null }> } | null, topContributors: Array<{ __typename: 'RepositoryContributorNode', avatarUrl: string, login: string, name: string }> };

export type GetProjectMetadataQueryVariables = Types.Exact<{
  key: Types.Scalars['String']['input'];
}>;


export type GetProjectMetadataQuery = { project: { __typename: 'ProjectNode', contributorsCount: number, forksCount: number, issuesCount: number, name: string, starsCount: number, summary: string, recentMilestones: Array<{ __typename: 'MilestoneNode', title: string, url: string, body: string, progress: number, state: string }> } | null };

export type GetTopContributorsQueryVariables = Types.Exact<{
  excludedUsernames?: Types.InputMaybe<Array<Types.Scalars['String']['input']> | Types.Scalars['String']['input']>;
  hasFullName?: Types.InputMaybe<Types.Scalars['Boolean']['input']>;
  key: Types.Scalars['String']['input'];
  limit?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type GetTopContributorsQuery = { topContributors: Array<{ __typename: 'RepositoryContributorNode', avatarUrl: string, login: string, name: string }> };

export type SearchProjectNamesQueryVariables = Types.Exact<{
  query: Types.Scalars['String']['input'];
}>;


export type SearchProjectNamesQuery = { searchProjects: Array<{ __typename: 'ProjectNode', id: string, name: string }> };
