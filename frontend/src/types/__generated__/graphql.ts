export type Maybe<T> = T | null;
export type InputMaybe<T> = Maybe<T>;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
export type MakeEmpty<T extends { [key: string]: unknown }, K extends keyof T> = { [_ in K]?: never };
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string; }
  String: { input: string; output: string; }
  Boolean: { input: boolean; output: boolean; }
  Int: { input: number; output: number; }
  Float: { input: number; output: number; }
  DateTime: { input: string; output: string; }
  UUID: { input: string; output: string; }
};

export type CreateModuleInput = {
  description?: InputMaybe<Scalars['String']['input']>;
  domains?: InputMaybe<Array<Scalars['String']['input']>>;
  endedAt?: InputMaybe<Scalars['DateTime']['input']>;
  experienceLevel?: InputMaybe<ExperienceLevelEnum>;
  key?: InputMaybe<Scalars['String']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  projectId?: InputMaybe<Scalars['String']['input']>;
  startedAt?: InputMaybe<Scalars['DateTime']['input']>;
  tags?: InputMaybe<Array<Scalars['String']['input']>>;
};

export type CreateProgramInput = {
  description?: InputMaybe<Scalars['String']['input']>;
  domains?: InputMaybe<Array<Scalars['String']['input']>>;
  endedAt?: InputMaybe<Scalars['DateTime']['input']>;
  key?: InputMaybe<Scalars['String']['input']>;
  menteesLimit?: InputMaybe<Scalars['Int']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  startedAt?: InputMaybe<Scalars['DateTime']['input']>;
  tags?: InputMaybe<Array<Scalars['String']['input']>>;
};

export enum ExperienceLevelEnum {
  Advanced = 'ADVANCED',
  Beginner = 'BEGINNER',
  Intermediate = 'INTERMEDIATE'
}

export type OffsetPaginationInput = {
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
};

export enum ProgramStatusEnum {
  Active = 'ACTIVE',
  Draft = 'DRAFT',
  Inactive = 'INACTIVE'
}

export type Project = {
  __typename?: 'Project';
  healthMetricsLatest?: Maybe<ProjectHealthMetric>;
  healthMetricsList: Array<ProjectHealthMetric>;
  id: Scalars['ID']['output'];
};


export type ProjectHealthMetricsListArgs = {
  limit?: InputMaybe<Scalars['Int']['input']>;
};

export type ProjectHealthMetric = {
  __typename?: 'ProjectHealthMetric';
  contributorsCount?: Maybe<Scalars['Int']['output']>;
  createdAt?: Maybe<Scalars['String']['output']>;
  forksCount?: Maybe<Scalars['Int']['output']>;
  id: Scalars['ID']['output'];
  openIssuesCount?: Maybe<Scalars['Int']['output']>;
  openPullRequestsCount?: Maybe<Scalars['Int']['output']>;
  projectKey?: Maybe<Scalars['String']['output']>;
  projectName?: Maybe<Scalars['String']['output']>;
  recentReleasesCount?: Maybe<Scalars['Int']['output']>;
  score?: Maybe<Scalars['Float']['output']>;
  starsCount?: Maybe<Scalars['Int']['output']>;
  totalIssuesCount?: Maybe<Scalars['Int']['output']>;
  totalReleasesCount?: Maybe<Scalars['Int']['output']>;
  unansweredIssuesCount?: Maybe<Scalars['Int']['output']>;
  unassignedIssuesCount?: Maybe<Scalars['Int']['output']>;
};

export type ProjectHealthMetricsFilter = {
  /** Dummy field to satisfy GraphQL spec for non-empty inputs */
  dummy?: InputMaybe<Scalars['Boolean']['input']>;
};

export enum ProjectHealthMetricsOrder {
  Dummy = 'DUMMY'
}

export type ProjectHealthStats = {
  __typename?: 'ProjectHealthStats';
  averageScore: Scalars['Float']['output'];
  monthlyOverallScores: Array<Scalars['Float']['output']>;
  monthlyOverallScoresMonths: Array<Scalars['String']['output']>;
  projectsCountHealthy: Scalars['Int']['output'];
  projectsCountNeedAttention: Scalars['Int']['output'];
  projectsCountUnhealthy: Scalars['Int']['output'];
  projectsPercentageHealthy: Scalars['Float']['output'];
  projectsPercentageNeedAttention: Scalars['Float']['output'];
  projectsPercentageUnhealthy: Scalars['Float']['output'];
  totalContributors: Scalars['Int']['output'];
  totalForks: Scalars['Int']['output'];
  totalStars: Scalars['Int']['output'];
};

/**
 * Minimal offline schema to allow GraphQL Codegen when backend is unavailable.
 * Only includes types used by unit tests and common queries.
 */
export type Query = {
  __typename?: 'Query';
  _placeholder?: Maybe<Scalars['Boolean']['output']>;
  project?: Maybe<Project>;
  projectHealthMetrics: Array<ProjectHealthMetric>;
  projectHealthMetricsDistinctLength: Scalars['Int']['output'];
  projectHealthStats: ProjectHealthStats;
};


/**
 * Minimal offline schema to allow GraphQL Codegen when backend is unavailable.
 * Only includes types used by unit tests and common queries.
 */
export type QueryProjectArgs = {
  key: Scalars['String']['input'];
};


/**
 * Minimal offline schema to allow GraphQL Codegen when backend is unavailable.
 * Only includes types used by unit tests and common queries.
 */
export type QueryProjectHealthMetricsArgs = {
  filters: ProjectHealthMetricsFilter;
  ordering?: InputMaybe<Array<ProjectHealthMetricsOrder>>;
  pagination: OffsetPaginationInput;
};


/**
 * Minimal offline schema to allow GraphQL Codegen when backend is unavailable.
 * Only includes types used by unit tests and common queries.
 */
export type QueryProjectHealthMetricsDistinctLengthArgs = {
  filters: ProjectHealthMetricsFilter;
};

export type UpdateModuleInput = {
  description?: InputMaybe<Scalars['String']['input']>;
  domains?: InputMaybe<Array<Scalars['String']['input']>>;
  endedAt?: InputMaybe<Scalars['DateTime']['input']>;
  experienceLevel?: InputMaybe<ExperienceLevelEnum>;
  key?: InputMaybe<Scalars['String']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  projectId?: InputMaybe<Scalars['String']['input']>;
  startedAt?: InputMaybe<Scalars['DateTime']['input']>;
  tags?: InputMaybe<Array<Scalars['String']['input']>>;
};

export type UpdateProgramInput = {
  description?: InputMaybe<Scalars['String']['input']>;
  domains?: InputMaybe<Array<Scalars['String']['input']>>;
  endedAt?: InputMaybe<Scalars['DateTime']['input']>;
  key?: InputMaybe<Scalars['String']['input']>;
  menteesLimit?: InputMaybe<Scalars['Int']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  startedAt?: InputMaybe<Scalars['DateTime']['input']>;
  status?: InputMaybe<ProgramStatusEnum>;
  tags?: InputMaybe<Array<Scalars['String']['input']>>;
};

export type UpdateProgramStatusInput = {
  key?: InputMaybe<Scalars['String']['input']>;
  status?: InputMaybe<ProgramStatusEnum>;
};
