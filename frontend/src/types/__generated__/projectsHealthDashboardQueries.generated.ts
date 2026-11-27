/** Internal type. DO NOT USE DIRECTLY. */
type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
/** Internal type. DO NOT USE DIRECTLY. */
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
import * as Types from './graphql';

import { TypedDocumentNode as DocumentNode } from '@graphql-typed-document-node/core';
export type FloatComparisonFilterLookup = {
  /** Exact match. Filter will be skipped on `null` value */
  exact?: number | null | undefined;
  /** Greater than. Filter will be skipped on `null` value */
  gt?: number | null | undefined;
  /** Greater than or equal to. Filter will be skipped on `null` value */
  gte?: number | null | undefined;
  /** Exact match of items in a given list. Filter will be skipped on `null` value */
  inList?: Array<number> | null | undefined;
  /** Assignment test. Filter will be skipped on `null` value */
  isNull?: boolean | null | undefined;
  /** Less than. Filter will be skipped on `null` value */
  lt?: number | null | undefined;
  /** Less than or equal to. Filter will be skipped on `null` value */
  lte?: number | null | undefined;
  /** Inclusive range test (between) */
  range?: FloatRangeLookup | null | undefined;
};

export type FloatRangeLookup = {
  end?: number | null | undefined;
  start?: number | null | undefined;
};

export type OffsetPaginationInput = {
  limit?: number | null | undefined;
  offset?: number;
};

export type Ordering =
  | 'ASC'
  | 'ASC_NULLS_FIRST'
  | 'ASC_NULLS_LAST'
  | 'DESC'
  | 'DESC_NULLS_FIRST'
  | 'DESC_NULLS_LAST';

export type ProjectHealthMetricsFilter = {
  AND?: ProjectHealthMetricsFilter | null | undefined;
  DISTINCT?: boolean | null | undefined;
  NOT?: ProjectHealthMetricsFilter | null | undefined;
  OR?: ProjectHealthMetricsFilter | null | undefined;
  level?: ProjectLevel | null | undefined;
  score?: FloatComparisonFilterLookup | null | undefined;
};

export type ProjectHealthMetricsOrder = {
  contributorsCount?: Ordering | null | undefined;
  createdAt?: Ordering | null | undefined;
  forksCount?: Ordering | null | undefined;
  project_Name?: Ordering | null | undefined;
  score?: Ordering | null | undefined;
  starsCount?: Ordering | null | undefined;
};

export type ProjectLevel =
  | 'FLAGSHIP'
  | 'INCUBATOR'
  | 'LAB'
  | 'OTHER'
  | 'PRODUCTION';

export type GetProjectHealthStatsQueryVariables = Exact<{ [key: string]: never; }>;


export type GetProjectHealthStatsQuery = { projectHealthStats: { __typename: 'ProjectHealthStatsNode', averageScore: number | null, monthlyOverallScores: Array<number>, monthlyOverallScoresMonths: Array<number>, projectsCountHealthy: number, projectsCountNeedAttention: number, projectsCountUnhealthy: number, projectsPercentageHealthy: number, projectsPercentageNeedAttention: number, projectsPercentageUnhealthy: number, totalContributors: number, totalForks: number, totalStars: number } };

export type GetProjectHealthMetricsQueryVariables = Exact<{
  filters: Types.ProjectHealthMetricsFilter;
  pagination: Types.OffsetPaginationInput;
  ordering?: Array<Types.ProjectHealthMetricsOrder> | Types.ProjectHealthMetricsOrder | null | undefined;
}>;


export type GetProjectHealthMetricsQuery = { projectHealthMetricsDistinctLength: number, projectHealthMetrics: Array<{ __typename: 'ProjectHealthMetricsNode', id: string, createdAt: any, contributorsCount: number, forksCount: number, projectKey: string, projectName: string, score: number | null, starsCount: number }> };

export type GetProjectHealthMetricsDetailsQueryVariables = Exact<{
  projectKey: string;
}>;


export type GetProjectHealthMetricsDetailsQuery = { project: { __typename: 'ProjectNode', id: string, healthMetricsLatest: { __typename: 'ProjectHealthMetricsNode', id: string, ageDays: number, ageDaysRequirement: number, isFundingRequirementsCompliant: boolean, isLeaderRequirementsCompliant: boolean, lastCommitDays: number, lastCommitDaysRequirement: number, lastPullRequestDays: number, lastPullRequestDaysRequirement: number, lastReleaseDays: number, lastReleaseDaysRequirement: number, owaspPageLastUpdateDays: number, owaspPageLastUpdateDaysRequirement: number, projectName: string, score: number | null } | null, healthMetricsList: Array<{ __typename: 'ProjectHealthMetricsNode', id: string, contributorsCount: number, createdAt: any, forksCount: number, openIssuesCount: number, openPullRequestsCount: number, recentReleasesCount: number, starsCount: number, totalIssuesCount: number, totalReleasesCount: number, unassignedIssuesCount: number, unansweredIssuesCount: number }> } | null };


export const GetProjectHealthStatsDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetProjectHealthStats"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"projectHealthStats"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"averageScore"}},{"kind":"Field","name":{"kind":"Name","value":"monthlyOverallScores"}},{"kind":"Field","name":{"kind":"Name","value":"monthlyOverallScoresMonths"}},{"kind":"Field","name":{"kind":"Name","value":"projectsCountHealthy"}},{"kind":"Field","name":{"kind":"Name","value":"projectsCountNeedAttention"}},{"kind":"Field","name":{"kind":"Name","value":"projectsCountUnhealthy"}},{"kind":"Field","name":{"kind":"Name","value":"projectsPercentageHealthy"}},{"kind":"Field","name":{"kind":"Name","value":"projectsPercentageNeedAttention"}},{"kind":"Field","name":{"kind":"Name","value":"projectsPercentageUnhealthy"}},{"kind":"Field","name":{"kind":"Name","value":"totalContributors"}},{"kind":"Field","name":{"kind":"Name","value":"totalForks"}},{"kind":"Field","name":{"kind":"Name","value":"totalStars"}}]}}]}}]} as unknown as DocumentNode<GetProjectHealthStatsQuery, GetProjectHealthStatsQueryVariables>;
export const GetProjectHealthMetricsDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetProjectHealthMetrics"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"filters"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"ProjectHealthMetricsFilter"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"pagination"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"OffsetPaginationInput"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"ordering"}},"type":{"kind":"ListType","type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"ProjectHealthMetricsOrder"}}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"projectHealthMetrics"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"filters"},"value":{"kind":"Variable","name":{"kind":"Name","value":"filters"}}},{"kind":"Argument","name":{"kind":"Name","value":"pagination"},"value":{"kind":"Variable","name":{"kind":"Name","value":"pagination"}}},{"kind":"Argument","name":{"kind":"Name","value":"ordering"},"value":{"kind":"Variable","name":{"kind":"Name","value":"ordering"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"contributorsCount"}},{"kind":"Field","name":{"kind":"Name","value":"forksCount"}},{"kind":"Field","name":{"kind":"Name","value":"projectKey"}},{"kind":"Field","name":{"kind":"Name","value":"projectName"}},{"kind":"Field","name":{"kind":"Name","value":"score"}},{"kind":"Field","name":{"kind":"Name","value":"starsCount"}}]}},{"kind":"Field","name":{"kind":"Name","value":"projectHealthMetricsDistinctLength"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"filters"},"value":{"kind":"Variable","name":{"kind":"Name","value":"filters"}}}]}]}}]} as unknown as DocumentNode<GetProjectHealthMetricsQuery, GetProjectHealthMetricsQueryVariables>;
export const GetProjectHealthMetricsDetailsDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetProjectHealthMetricsDetails"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"projectKey"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"project"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"key"},"value":{"kind":"Variable","name":{"kind":"Name","value":"projectKey"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"healthMetricsLatest"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"ageDays"}},{"kind":"Field","name":{"kind":"Name","value":"ageDaysRequirement"}},{"kind":"Field","name":{"kind":"Name","value":"isFundingRequirementsCompliant"}},{"kind":"Field","name":{"kind":"Name","value":"isLeaderRequirementsCompliant"}},{"kind":"Field","name":{"kind":"Name","value":"lastCommitDays"}},{"kind":"Field","name":{"kind":"Name","value":"lastCommitDaysRequirement"}},{"kind":"Field","name":{"kind":"Name","value":"lastPullRequestDays"}},{"kind":"Field","name":{"kind":"Name","value":"lastPullRequestDaysRequirement"}},{"kind":"Field","name":{"kind":"Name","value":"lastReleaseDays"}},{"kind":"Field","name":{"kind":"Name","value":"lastReleaseDaysRequirement"}},{"kind":"Field","name":{"kind":"Name","value":"owaspPageLastUpdateDays"}},{"kind":"Field","name":{"kind":"Name","value":"owaspPageLastUpdateDaysRequirement"}},{"kind":"Field","name":{"kind":"Name","value":"projectName"}},{"kind":"Field","name":{"kind":"Name","value":"score"}}]}},{"kind":"Field","name":{"kind":"Name","value":"healthMetricsList"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"limit"},"value":{"kind":"IntValue","value":"30"}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"contributorsCount"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"forksCount"}},{"kind":"Field","name":{"kind":"Name","value":"openIssuesCount"}},{"kind":"Field","name":{"kind":"Name","value":"openPullRequestsCount"}},{"kind":"Field","name":{"kind":"Name","value":"recentReleasesCount"}},{"kind":"Field","name":{"kind":"Name","value":"starsCount"}},{"kind":"Field","name":{"kind":"Name","value":"totalIssuesCount"}},{"kind":"Field","name":{"kind":"Name","value":"totalReleasesCount"}},{"kind":"Field","name":{"kind":"Name","value":"unassignedIssuesCount"}},{"kind":"Field","name":{"kind":"Name","value":"unansweredIssuesCount"}}]}}]}}]}}]} as unknown as DocumentNode<GetProjectHealthMetricsDetailsQuery, GetProjectHealthMetricsDetailsQueryVariables>;