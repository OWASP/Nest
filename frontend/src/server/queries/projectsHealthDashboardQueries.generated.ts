import * as Types from '../../types/__generated__/graphql';

export type GetProjectHealthStatsQueryVariables = Types.Exact<{ [key: string]: never; }>;


export type GetProjectHealthStatsQuery = { projectHealthStats: { __typename: 'ProjectHealthStatsNode', averageScore: number, monthlyOverallScores: Array<number>, monthlyOverallScoresMonths: Array<number>, projectsCountHealthy: number, projectsCountNeedAttention: number, projectsCountUnhealthy: number, projectsPercentageHealthy: number, projectsPercentageNeedAttention: number, projectsPercentageUnhealthy: number, totalContributors: number, totalForks: number, totalStars: number } };

export type GetProjectHealthMetricsQueryVariables = Types.Exact<{
  filters: Types.ProjectHealthMetricsFilter;
  pagination: Types.OffsetPaginationInput;
  ordering?: Types.InputMaybe<Array<Types.ProjectHealthMetricsOrder> | Types.ProjectHealthMetricsOrder>;
}>;


export type GetProjectHealthMetricsQuery = { projectHealthMetricsDistinctLength: number, projectHealthMetrics: Array<{ __typename: 'ProjectHealthMetricsNode', createdAt: unknown, contributorsCount: number, forksCount: number, id: string, projectKey: string, projectName: string, score: number | null, starsCount: number }> };

export type ProjectQueryVariables = Types.Exact<{
  projectKey: Types.Scalars['String']['input'];
}>;


export type ProjectQuery = { project: { __typename: 'ProjectNode', healthMetricsLatest: { __typename: 'ProjectHealthMetricsNode', ageDays: number, ageDaysRequirement: number, isFundingRequirementsCompliant: boolean, isLeaderRequirementsCompliant: boolean, lastCommitDays: number, lastCommitDaysRequirement: number, lastPullRequestDays: number, lastPullRequestDaysRequirement: number, lastReleaseDays: number, lastReleaseDaysRequirement: number, owaspPageLastUpdateDays: number, owaspPageLastUpdateDaysRequirement: number, projectName: string, score: number | null } | null, healthMetricsList: Array<{ __typename: 'ProjectHealthMetricsNode', contributorsCount: number, createdAt: unknown, forksCount: number, openIssuesCount: number, openPullRequestsCount: number, recentReleasesCount: number, starsCount: number, totalIssuesCount: number, totalReleasesCount: number, unassignedIssuesCount: number, unansweredIssuesCount: number }> } | null };
