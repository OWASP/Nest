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
  Date: { input: any; output: any; }
  DateTime: { input: any; output: any; }
  JSON: { input: any; output: any; }
  UUID: { input: any; output: any; }
};

export type ApiKeyNode = Node & {
  __typename?: 'ApiKeyNode';
  createdAt: Scalars['DateTime']['output'];
  expiresAt: Scalars['DateTime']['output'];
  /** The Globally Unique ID of this object */
  id: Scalars['ID']['output'];
  isRevoked: Scalars['Boolean']['output'];
  name: Scalars['String']['output'];
  uuid: Scalars['UUID']['output'];
};

export type AuthUserNode = Node & {
  __typename?: 'AuthUserNode';
  /** The Globally Unique ID of this object */
  id: Scalars['ID']['output'];
  isOwaspStaff: Scalars['Boolean']['output'];
  username: Scalars['String']['output'];
};

export type ChapterNode = Node & {
  __typename?: 'ChapterNode';
  country: Scalars['String']['output'];
  createdAt: Scalars['Float']['output'];
  geoLocation?: Maybe<GeoLocationType>;
  /** The Globally Unique ID of this object */
  id: Scalars['ID']['output'];
  isActive: Scalars['Boolean']['output'];
  key: Scalars['String']['output'];
  leaders: Array<Scalars['String']['output']>;
  meetupGroup: Scalars['String']['output'];
  name: Scalars['String']['output'];
  postalCode: Scalars['String']['output'];
  region: Scalars['String']['output'];
  relatedUrls: Array<Scalars['String']['output']>;
  suggestedLocation?: Maybe<Scalars['String']['output']>;
  summary: Scalars['String']['output'];
  tags: Scalars['JSON']['output'];
  topContributors: Array<RepositoryContributorNode>;
  updatedAt: Scalars['Float']['output'];
  url: Scalars['String']['output'];
};

export type CommitteeNode = Node & {
  __typename?: 'CommitteeNode';
  contributorsCount: Scalars['Int']['output'];
  createdAt: Scalars['Float']['output'];
  forksCount: Scalars['Int']['output'];
  /** The Globally Unique ID of this object */
  id: Scalars['ID']['output'];
  issuesCount: Scalars['Int']['output'];
  leaders: Array<Scalars['String']['output']>;
  name: Scalars['String']['output'];
  relatedUrls: Array<Scalars['String']['output']>;
  repositoriesCount: Scalars['Int']['output'];
  starsCount: Scalars['Int']['output'];
  summary: Scalars['String']['output'];
  topContributors: Array<RepositoryContributorNode>;
  updatedAt: Scalars['Float']['output'];
  url: Scalars['String']['output'];
};

export type CreateApiKeyResult = {
  __typename?: 'CreateApiKeyResult';
  apiKey?: Maybe<ApiKeyNode>;
  code?: Maybe<Scalars['String']['output']>;
  message?: Maybe<Scalars['String']['output']>;
  ok: Scalars['Boolean']['output'];
  rawKey?: Maybe<Scalars['String']['output']>;
};

export type CreateModuleInput = {
  description: Scalars['String']['input'];
  domains?: Array<Scalars['String']['input']>;
  endedAt: Scalars['DateTime']['input'];
  experienceLevel: ExperienceLevelEnum;
  mentorLogins?: InputMaybe<Array<Scalars['String']['input']>>;
  name: Scalars['String']['input'];
  programKey: Scalars['String']['input'];
  projectId: Scalars['ID']['input'];
  projectName: Scalars['String']['input'];
  startedAt: Scalars['DateTime']['input'];
  tags?: Array<Scalars['String']['input']>;
};

export type CreateProgramInput = {
  description: Scalars['String']['input'];
  domains?: Array<Scalars['String']['input']>;
  endedAt: Scalars['DateTime']['input'];
  menteesLimit: Scalars['Int']['input'];
  name: Scalars['String']['input'];
  startedAt: Scalars['DateTime']['input'];
  tags?: Array<Scalars['String']['input']>;
};

export type EventNode = Node & {
  __typename?: 'EventNode';
  category: Scalars['String']['output'];
  description: Scalars['String']['output'];
  endDate?: Maybe<Scalars['Date']['output']>;
  /** The Globally Unique ID of this object */
  id: Scalars['ID']['output'];
  key: Scalars['String']['output'];
  name: Scalars['String']['output'];
  startDate: Scalars['Date']['output'];
  suggestedLocation: Scalars['String']['output'];
  summary: Scalars['String']['output'];
  url: Scalars['String']['output'];
};

export enum ExperienceLevelEnum {
  Advanced = 'ADVANCED',
  Beginner = 'BEGINNER',
  Expert = 'EXPERT',
  Intermediate = 'INTERMEDIATE'
}

export type FloatComparisonFilterLookup = {
  /** Exact match. Filter will be skipped on `null` value */
  exact?: InputMaybe<Scalars['Float']['input']>;
  /** Greater than. Filter will be skipped on `null` value */
  gt?: InputMaybe<Scalars['Float']['input']>;
  /** Greater than or equal to. Filter will be skipped on `null` value */
  gte?: InputMaybe<Scalars['Float']['input']>;
  /** Exact match of items in a given list. Filter will be skipped on `null` value */
  inList?: InputMaybe<Array<Scalars['Float']['input']>>;
  /** Assignment test. Filter will be skipped on `null` value */
  isNull?: InputMaybe<Scalars['Boolean']['input']>;
  /** Less than. Filter will be skipped on `null` value */
  lt?: InputMaybe<Scalars['Float']['input']>;
  /** Less than or equal to. Filter will be skipped on `null` value */
  lte?: InputMaybe<Scalars['Float']['input']>;
  /** Inclusive range test (between) */
  range?: InputMaybe<FloatRangeLookup>;
};

export type FloatRangeLookup = {
  end?: InputMaybe<Scalars['Float']['input']>;
  start?: InputMaybe<Scalars['Float']['input']>;
};

export type GeoLocationType = {
  __typename?: 'GeoLocationType';
  lat: Scalars['Float']['output'];
  lng: Scalars['Float']['output'];
};

export type GitHubAuthResult = {
  __typename?: 'GitHubAuthResult';
  message: Scalars['String']['output'];
  ok: Scalars['Boolean']['output'];
  user?: Maybe<AuthUserNode>;
};

export type IssueNode = Node & {
  __typename?: 'IssueNode';
  author?: Maybe<UserNode>;
  createdAt: Scalars['DateTime']['output'];
  /** The Globally Unique ID of this object */
  id: Scalars['ID']['output'];
  organizationName?: Maybe<Scalars['String']['output']>;
  repositoryName?: Maybe<Scalars['String']['output']>;
  state: Scalars['String']['output'];
  title: Scalars['String']['output'];
  url: Scalars['String']['output'];
};

export type LogoutResult = {
  __typename?: 'LogoutResult';
  code?: Maybe<Scalars['String']['output']>;
  message?: Maybe<Scalars['String']['output']>;
  ok: Scalars['Boolean']['output'];
};

export type MentorNode = {
  __typename?: 'MentorNode';
  avatarUrl: Scalars['String']['output'];
  id: Scalars['ID']['output'];
  login: Scalars['String']['output'];
  name: Scalars['String']['output'];
};

export type MilestoneNode = Node & {
  __typename?: 'MilestoneNode';
  author?: Maybe<UserNode>;
  body: Scalars['String']['output'];
  closedIssuesCount: Scalars['Int']['output'];
  createdAt: Scalars['DateTime']['output'];
  /** The Globally Unique ID of this object */
  id: Scalars['ID']['output'];
  openIssuesCount: Scalars['Int']['output'];
  organizationName?: Maybe<Scalars['String']['output']>;
  progress: Scalars['Float']['output'];
  repositoryName?: Maybe<Scalars['String']['output']>;
  state: Scalars['String']['output'];
  title: Scalars['String']['output'];
  url: Scalars['String']['output'];
};

export type ModuleNode = {
  __typename?: 'ModuleNode';
  description: Scalars['String']['output'];
  domains?: Maybe<Array<Scalars['String']['output']>>;
  endedAt: Scalars['DateTime']['output'];
  experienceLevel: ExperienceLevelEnum;
  id: Scalars['ID']['output'];
  key: Scalars['String']['output'];
  mentors: Array<MentorNode>;
  name: Scalars['String']['output'];
  program?: Maybe<ProgramNode>;
  projectId?: Maybe<Scalars['ID']['output']>;
  projectName?: Maybe<Scalars['String']['output']>;
  startedAt: Scalars['DateTime']['output'];
  tags?: Maybe<Array<Scalars['String']['output']>>;
};

export type Mutation = {
  __typename?: 'Mutation';
  createApiKey: CreateApiKeyResult;
  createModule: ModuleNode;
  createProgram: ProgramNode;
  githubAuth: GitHubAuthResult;
  logoutUser: LogoutResult;
  revokeApiKey: RevokeApiKeyResult;
  updateModule: ModuleNode;
  updateProgram: ProgramNode;
  updateProgramStatus: ProgramNode;
};


export type MutationCreateApiKeyArgs = {
  expiresAt: Scalars['DateTime']['input'];
  name: Scalars['String']['input'];
};


export type MutationCreateModuleArgs = {
  inputData: CreateModuleInput;
};


export type MutationCreateProgramArgs = {
  inputData: CreateProgramInput;
};


export type MutationGithubAuthArgs = {
  accessToken: Scalars['String']['input'];
};


export type MutationRevokeApiKeyArgs = {
  uuid: Scalars['UUID']['input'];
};


export type MutationUpdateModuleArgs = {
  inputData: UpdateModuleInput;
};


export type MutationUpdateProgramArgs = {
  inputData: UpdateProgramInput;
};


export type MutationUpdateProgramStatusArgs = {
  inputData: UpdateProgramStatusInput;
};

/** An object with a Globally Unique ID */
export type Node = {
  /** The Globally Unique ID of this object */
  id: Scalars['ID']['output'];
};

export type OffsetPaginationInput = {
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: Scalars['Int']['input'];
};

export enum Ordering {
  Asc = 'ASC',
  AscNullsFirst = 'ASC_NULLS_FIRST',
  AscNullsLast = 'ASC_NULLS_LAST',
  Desc = 'DESC',
  DescNullsFirst = 'DESC_NULLS_FIRST',
  DescNullsLast = 'DESC_NULLS_LAST'
}

export type OrganizationNode = Node & {
  __typename?: 'OrganizationNode';
  avatarUrl: Scalars['String']['output'];
  collaboratorsCount: Scalars['Int']['output'];
  company: Scalars['String']['output'];
  createdAt: Scalars['DateTime']['output'];
  description: Scalars['String']['output'];
  email: Scalars['String']['output'];
  followersCount: Scalars['Int']['output'];
  /** The Globally Unique ID of this object */
  id: Scalars['ID']['output'];
  location: Scalars['String']['output'];
  login: Scalars['String']['output'];
  name: Scalars['String']['output'];
  stats: OrganizationStatsNode;
  updatedAt: Scalars['DateTime']['output'];
  url: Scalars['String']['output'];
};

export type OrganizationStatsNode = {
  __typename?: 'OrganizationStatsNode';
  totalContributors: Scalars['Int']['output'];
  totalForks: Scalars['Int']['output'];
  totalIssues: Scalars['Int']['output'];
  totalRepositories: Scalars['Int']['output'];
  totalStars: Scalars['Int']['output'];
};

export type PaginatedPrograms = {
  __typename?: 'PaginatedPrograms';
  currentPage: Scalars['Int']['output'];
  programs: Array<ProgramNode>;
  totalPages: Scalars['Int']['output'];
};

export type PostNode = Node & {
  __typename?: 'PostNode';
  authorImageUrl: Scalars['String']['output'];
  authorName: Scalars['String']['output'];
  /** The Globally Unique ID of this object */
  id: Scalars['ID']['output'];
  publishedAt: Scalars['DateTime']['output'];
  title: Scalars['String']['output'];
  url: Scalars['String']['output'];
};

export type ProgramNode = {
  __typename?: 'ProgramNode';
  admins?: Maybe<Array<MentorNode>>;
  description: Scalars['String']['output'];
  domains?: Maybe<Array<Scalars['String']['output']>>;
  endedAt: Scalars['DateTime']['output'];
  experienceLevels?: Maybe<Array<ExperienceLevelEnum>>;
  id: Scalars['ID']['output'];
  key: Scalars['String']['output'];
  menteesLimit?: Maybe<Scalars['Int']['output']>;
  name: Scalars['String']['output'];
  startedAt: Scalars['DateTime']['output'];
  status: ProgramStatusEnum;
  tags?: Maybe<Array<Scalars['String']['output']>>;
  userRole?: Maybe<Scalars['String']['output']>;
};

export enum ProgramStatusEnum {
  Completed = 'COMPLETED',
  Draft = 'DRAFT',
  Published = 'PUBLISHED'
}

export type ProjectHealthMetricsFilter = {
  AND?: InputMaybe<ProjectHealthMetricsFilter>;
  DISTINCT?: InputMaybe<Scalars['Boolean']['input']>;
  NOT?: InputMaybe<ProjectHealthMetricsFilter>;
  OR?: InputMaybe<ProjectHealthMetricsFilter>;
  level?: InputMaybe<Scalars['String']['input']>;
  score?: InputMaybe<FloatComparisonFilterLookup>;
};

export type ProjectHealthMetricsNode = Node & {
  __typename?: 'ProjectHealthMetricsNode';
  ageDays: Scalars['Int']['output'];
  ageDaysRequirement: Scalars['Int']['output'];
  contributorsCount: Scalars['Int']['output'];
  createdAt: Scalars['DateTime']['output'];
  forksCount: Scalars['Int']['output'];
  /** The Globally Unique ID of this object */
  id: Scalars['ID']['output'];
  isFundingRequirementsCompliant: Scalars['Boolean']['output'];
  isLeaderRequirementsCompliant: Scalars['Boolean']['output'];
  lastCommitDays: Scalars['Int']['output'];
  lastCommitDaysRequirement: Scalars['Int']['output'];
  lastPullRequestDays: Scalars['Int']['output'];
  lastPullRequestDaysRequirement: Scalars['Int']['output'];
  lastReleaseDays: Scalars['Int']['output'];
  lastReleaseDaysRequirement: Scalars['Int']['output'];
  openIssuesCount: Scalars['Int']['output'];
  openPullRequestsCount: Scalars['Int']['output'];
  owaspPageLastUpdateDays: Scalars['Int']['output'];
  owaspPageLastUpdateDaysRequirement: Scalars['Int']['output'];
  projectKey: Scalars['String']['output'];
  projectName: Scalars['String']['output'];
  recentReleasesCount: Scalars['Int']['output'];
  score?: Maybe<Scalars['Float']['output']>;
  starsCount: Scalars['Int']['output'];
  totalIssuesCount: Scalars['Int']['output'];
  totalReleasesCount: Scalars['Int']['output'];
  unansweredIssuesCount: Scalars['Int']['output'];
  unassignedIssuesCount: Scalars['Int']['output'];
};

export type ProjectHealthMetricsOrder = {
  project_Name?: InputMaybe<Ordering>;
  score?: InputMaybe<Ordering>;
};

export type ProjectHealthStatsNode = {
  __typename?: 'ProjectHealthStatsNode';
  averageScore: Scalars['Float']['output'];
  monthlyOverallScores: Array<Scalars['Float']['output']>;
  monthlyOverallScoresMonths: Array<Scalars['Int']['output']>;
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

export type ProjectNode = Node & {
  __typename?: 'ProjectNode';
  contributorsCount: Scalars['Int']['output'];
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  forksCount: Scalars['Int']['output'];
  healthMetricsLatest?: Maybe<ProjectHealthMetricsNode>;
  healthMetricsList: Array<ProjectHealthMetricsNode>;
  id: Scalars['ID']['output'];
  isActive: Scalars['Boolean']['output'];
  issuesCount: Scalars['Int']['output'];
  key: Scalars['String']['output'];
  languages: Array<Scalars['String']['output']>;
  leaders: Array<Scalars['String']['output']>;
  level: Scalars['String']['output'];
  name: Scalars['String']['output'];
  openIssuesCount: Scalars['Int']['output'];
  recentIssues: Array<IssueNode>;
  recentMilestones: Array<MilestoneNode>;
  recentPullRequests: Array<PullRequestNode>;
  recentReleases: Array<ReleaseNode>;
  relatedUrls: Array<Scalars['String']['output']>;
  repositories: Array<RepositoryNode>;
  repositoriesCount: Scalars['Int']['output'];
  starsCount: Scalars['Int']['output'];
  summary: Scalars['String']['output'];
  topContributors: Array<RepositoryContributorNode>;
  topics: Array<Scalars['String']['output']>;
  type: Scalars['String']['output'];
  updatedAt: Scalars['Float']['output'];
  url: Scalars['String']['output'];
};


export type ProjectNodeHealthMetricsListArgs = {
  limit?: Scalars['Int']['input'];
};


export type ProjectNodeRecentMilestonesArgs = {
  limit?: Scalars['Int']['input'];
};

export type PullRequestNode = Node & {
  __typename?: 'PullRequestNode';
  author?: Maybe<UserNode>;
  createdAt: Scalars['DateTime']['output'];
  /** The Globally Unique ID of this object */
  id: Scalars['ID']['output'];
  organizationName?: Maybe<Scalars['String']['output']>;
  repositoryName?: Maybe<Scalars['String']['output']>;
  title: Scalars['String']['output'];
  url: Scalars['String']['output'];
};

export type Query = {
  __typename?: 'Query';
  activeApiKeyCount: Scalars['Int']['output'];
  apiKeys: Array<ApiKeyNode>;
  chapter?: Maybe<ChapterNode>;
  committee?: Maybe<CommitteeNode>;
  getModule: ModuleNode;
  getProgram: ProgramNode;
  getProgramModules: Array<ModuleNode>;
  getProjectModules: Array<ModuleNode>;
  isMentor: Scalars['Boolean']['output'];
  isProjectLeader: Scalars['Boolean']['output'];
  myPrograms: PaginatedPrograms;
  organization?: Maybe<OrganizationNode>;
  project?: Maybe<ProjectNode>;
  /** List of project health metrics. */
  projectHealthMetrics: Array<ProjectHealthMetricsNode>;
  projectHealthMetricsDistinctLength: Scalars['Int']['output'];
  projectHealthStats: ProjectHealthStatsNode;
  recentChapters: Array<ChapterNode>;
  recentIssues: Array<IssueNode>;
  recentMilestones: Array<MilestoneNode>;
  recentPosts: Array<PostNode>;
  recentProjects: Array<ProjectNode>;
  recentPullRequests: Array<PullRequestNode>;
  recentReleases: Array<ReleaseNode>;
  repositories: Array<RepositoryNode>;
  repository?: Maybe<RepositoryNode>;
  searchProjects: Array<ProjectNode>;
  snapshot?: Maybe<SnapshotNode>;
  snapshots: Array<SnapshotNode>;
  sponsors: Array<SponsorNode>;
  statsOverview: StatsNode;
  topContributedRepositories: Array<RepositoryNode>;
  topContributors: Array<RepositoryContributorNode>;
  upcomingEvents: Array<EventNode>;
  user?: Maybe<UserNode>;
};


export type QueryChapterArgs = {
  key: Scalars['String']['input'];
};


export type QueryCommitteeArgs = {
  key: Scalars['String']['input'];
};


export type QueryGetModuleArgs = {
  moduleKey: Scalars['String']['input'];
  programKey: Scalars['String']['input'];
};


export type QueryGetProgramArgs = {
  programKey: Scalars['String']['input'];
};


export type QueryGetProgramModulesArgs = {
  programKey: Scalars['String']['input'];
};


export type QueryGetProjectModulesArgs = {
  projectKey: Scalars['String']['input'];
};


export type QueryIsMentorArgs = {
  login: Scalars['String']['input'];
};


export type QueryIsProjectLeaderArgs = {
  login: Scalars['String']['input'];
};


export type QueryMyProgramsArgs = {
  limit?: Scalars['Int']['input'];
  page?: Scalars['Int']['input'];
  search?: Scalars['String']['input'];
};


export type QueryOrganizationArgs = {
  login: Scalars['String']['input'];
};


export type QueryProjectArgs = {
  key: Scalars['String']['input'];
};


export type QueryProjectHealthMetricsArgs = {
  filters?: InputMaybe<ProjectHealthMetricsFilter>;
  ordering?: InputMaybe<Array<ProjectHealthMetricsOrder>>;
  pagination?: InputMaybe<OffsetPaginationInput>;
};


export type QueryProjectHealthMetricsDistinctLengthArgs = {
  filters?: InputMaybe<ProjectHealthMetricsFilter>;
};


export type QueryRecentChaptersArgs = {
  limit?: Scalars['Int']['input'];
};


export type QueryRecentIssuesArgs = {
  distinct?: Scalars['Boolean']['input'];
  limit?: Scalars['Int']['input'];
  login?: InputMaybe<Scalars['String']['input']>;
  organization?: InputMaybe<Scalars['String']['input']>;
};


export type QueryRecentMilestonesArgs = {
  distinct?: Scalars['Boolean']['input'];
  limit?: Scalars['Int']['input'];
  login?: InputMaybe<Scalars['String']['input']>;
  organization?: InputMaybe<Scalars['String']['input']>;
  state?: Scalars['String']['input'];
};


export type QueryRecentPostsArgs = {
  limit?: Scalars['Int']['input'];
};


export type QueryRecentProjectsArgs = {
  limit?: Scalars['Int']['input'];
};


export type QueryRecentPullRequestsArgs = {
  distinct?: Scalars['Boolean']['input'];
  limit?: Scalars['Int']['input'];
  login?: InputMaybe<Scalars['String']['input']>;
  organization?: InputMaybe<Scalars['String']['input']>;
  project?: InputMaybe<Scalars['String']['input']>;
  repository?: InputMaybe<Scalars['String']['input']>;
};


export type QueryRecentReleasesArgs = {
  distinct?: Scalars['Boolean']['input'];
  limit?: Scalars['Int']['input'];
  login?: InputMaybe<Scalars['String']['input']>;
  organization?: InputMaybe<Scalars['String']['input']>;
};


export type QueryRepositoriesArgs = {
  limit?: Scalars['Int']['input'];
  organization: Scalars['String']['input'];
};


export type QueryRepositoryArgs = {
  organizationKey: Scalars['String']['input'];
  repositoryKey: Scalars['String']['input'];
};


export type QuerySearchProjectsArgs = {
  query: Scalars['String']['input'];
};


export type QuerySnapshotArgs = {
  key: Scalars['String']['input'];
};


export type QuerySnapshotsArgs = {
  limit?: Scalars['Int']['input'];
};


export type QueryTopContributedRepositoriesArgs = {
  login: Scalars['String']['input'];
};


export type QueryTopContributorsArgs = {
  chapter?: InputMaybe<Scalars['String']['input']>;
  committee?: InputMaybe<Scalars['String']['input']>;
  excludedUsernames?: InputMaybe<Array<Scalars['String']['input']>>;
  hasFullName?: Scalars['Boolean']['input'];
  limit?: Scalars['Int']['input'];
  organization?: InputMaybe<Scalars['String']['input']>;
  project?: InputMaybe<Scalars['String']['input']>;
  repository?: InputMaybe<Scalars['String']['input']>;
};


export type QueryUpcomingEventsArgs = {
  limit?: Scalars['Int']['input'];
};


export type QueryUserArgs = {
  login: Scalars['String']['input'];
};

export type ReleaseNode = Node & {
  __typename?: 'ReleaseNode';
  author?: Maybe<UserNode>;
  /** The Globally Unique ID of this object */
  id: Scalars['ID']['output'];
  isPreRelease: Scalars['Boolean']['output'];
  name: Scalars['String']['output'];
  organizationName?: Maybe<Scalars['String']['output']>;
  projectName?: Maybe<Scalars['String']['output']>;
  publishedAt?: Maybe<Scalars['DateTime']['output']>;
  repositoryName?: Maybe<Scalars['String']['output']>;
  tagName: Scalars['String']['output'];
  url: Scalars['String']['output'];
};

export type RepositoryContributorNode = {
  __typename?: 'RepositoryContributorNode';
  avatarUrl: Scalars['String']['output'];
  contributionsCount: Scalars['Int']['output'];
  id: Scalars['ID']['output'];
  login: Scalars['String']['output'];
  name: Scalars['String']['output'];
  projectKey: Scalars['String']['output'];
  projectName: Scalars['String']['output'];
};

export type RepositoryNode = Node & {
  __typename?: 'RepositoryNode';
  commitsCount: Scalars['Int']['output'];
  contributorsCount: Scalars['Int']['output'];
  createdAt: Scalars['DateTime']['output'];
  description: Scalars['String']['output'];
  forksCount: Scalars['Int']['output'];
  /** The Globally Unique ID of this object */
  id: Scalars['ID']['output'];
  issues: Array<IssueNode>;
  key: Scalars['String']['output'];
  languages: Array<Scalars['String']['output']>;
  latestRelease: Scalars['String']['output'];
  license: Scalars['String']['output'];
  name: Scalars['String']['output'];
  openIssuesCount: Scalars['Int']['output'];
  organization?: Maybe<OrganizationNode>;
  ownerKey: Scalars['String']['output'];
  project?: Maybe<ProjectNode>;
  recentMilestones: Array<MilestoneNode>;
  releases: Array<ReleaseNode>;
  size: Scalars['Int']['output'];
  starsCount: Scalars['Int']['output'];
  subscribersCount: Scalars['Int']['output'];
  topContributors: Array<RepositoryContributorNode>;
  topics: Array<Scalars['String']['output']>;
  updatedAt: Scalars['DateTime']['output'];
  url: Scalars['String']['output'];
};


export type RepositoryNodeRecentMilestonesArgs = {
  limit?: Scalars['Int']['input'];
};

export type RevokeApiKeyResult = {
  __typename?: 'RevokeApiKeyResult';
  code?: Maybe<Scalars['String']['output']>;
  message?: Maybe<Scalars['String']['output']>;
  ok: Scalars['Boolean']['output'];
};

export type SnapshotNode = Node & {
  __typename?: 'SnapshotNode';
  createdAt: Scalars['DateTime']['output'];
  endAt: Scalars['DateTime']['output'];
  /** The Globally Unique ID of this object */
  id: Scalars['ID']['output'];
  key: Scalars['String']['output'];
  leaders: Array<Scalars['String']['output']>;
  newChapters: Array<ChapterNode>;
  newIssues: Array<IssueNode>;
  newProjects: Array<ProjectNode>;
  newReleases: Array<ReleaseNode>;
  newUsers: Array<UserNode>;
  relatedUrls: Array<Scalars['String']['output']>;
  startAt: Scalars['DateTime']['output'];
  title: Scalars['String']['output'];
  topContributors: Array<RepositoryContributorNode>;
  updatedAt: Scalars['Float']['output'];
  url: Scalars['String']['output'];
};

export type SponsorNode = Node & {
  __typename?: 'SponsorNode';
  /** The Globally Unique ID of this object */
  id: Scalars['ID']['output'];
  imageUrl: Scalars['String']['output'];
  name: Scalars['String']['output'];
  sponsorType: Scalars['String']['output'];
  url: Scalars['String']['output'];
};

export type StatsNode = {
  __typename?: 'StatsNode';
  activeChaptersStats: Scalars['Int']['output'];
  activeProjectsStats: Scalars['Int']['output'];
  contributorsStats: Scalars['Int']['output'];
  countriesStats: Scalars['Int']['output'];
  slackWorkspaceStats: Scalars['Int']['output'];
};

export type UpdateModuleInput = {
  description: Scalars['String']['input'];
  domains?: Array<Scalars['String']['input']>;
  endedAt: Scalars['DateTime']['input'];
  experienceLevel: ExperienceLevelEnum;
  key: Scalars['String']['input'];
  mentorLogins?: InputMaybe<Array<Scalars['String']['input']>>;
  name: Scalars['String']['input'];
  programKey: Scalars['String']['input'];
  projectId: Scalars['ID']['input'];
  projectName: Scalars['String']['input'];
  startedAt: Scalars['DateTime']['input'];
  tags?: Array<Scalars['String']['input']>;
};

export type UpdateProgramInput = {
  adminLogins?: InputMaybe<Array<Scalars['String']['input']>>;
  description: Scalars['String']['input'];
  domains?: InputMaybe<Array<Scalars['String']['input']>>;
  endedAt: Scalars['DateTime']['input'];
  key: Scalars['String']['input'];
  menteesLimit: Scalars['Int']['input'];
  name: Scalars['String']['input'];
  startedAt: Scalars['DateTime']['input'];
  status: ProgramStatusEnum;
  tags?: InputMaybe<Array<Scalars['String']['input']>>;
};

export type UpdateProgramStatusInput = {
  key: Scalars['String']['input'];
  name: Scalars['String']['input'];
  status: ProgramStatusEnum;
};

export type UserNode = {
  __typename?: 'UserNode';
  avatarUrl: Scalars['String']['output'];
  bio: Scalars['String']['output'];
  company: Scalars['String']['output'];
  contributionsCount: Scalars['Int']['output'];
  createdAt: Scalars['Float']['output'];
  email: Scalars['String']['output'];
  followersCount: Scalars['Int']['output'];
  followingCount: Scalars['Int']['output'];
  id: Scalars['ID']['output'];
  isOwaspStaff: Scalars['Boolean']['output'];
  issuesCount: Scalars['Int']['output'];
  location: Scalars['String']['output'];
  login: Scalars['String']['output'];
  name: Scalars['String']['output'];
  publicRepositoriesCount: Scalars['Int']['output'];
  releasesCount: Scalars['Int']['output'];
  updatedAt: Scalars['Float']['output'];
  url: Scalars['String']['output'];
};
