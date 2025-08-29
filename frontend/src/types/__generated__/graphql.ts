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
  Date: { input: unknown; output: unknown; }
  DateTime: { input: unknown; output: unknown; }
  JSON: { input: unknown; output: unknown; }
  UUID: { input: unknown; output: unknown; }
};

export type ApiKeyNode = Node & {
  __typename: 'ApiKeyNode';
  createdAt: Scalars['DateTime']['output'];
  expiresAt: Scalars['DateTime']['output'];
  /** The Globally Unique ID of this object */
  id: Scalars['ID']['output'];
  isRevoked: Scalars['Boolean']['output'];
  name: Scalars['String']['output'];
  uuid: Scalars['UUID']['output'];
};

export type AuthUserNode = Node & {
  __typename: 'AuthUserNode';
  /** The Globally Unique ID of this object */
  id: Scalars['ID']['output'];
  isOwaspStaff: Scalars['Boolean']['output'];
  username: Scalars['String']['output'];
};

export type ChapterNode = Node & {
  __typename: 'ChapterNode';
  country: Scalars['String']['output'];
  createdAt: Scalars['Float']['output'];
  geoLocation: Maybe<GeoLocationType>;
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
  suggestedLocation: Maybe<Scalars['String']['output']>;
  summary: Scalars['String']['output'];
  tags: Scalars['JSON']['output'];
  topContributors: Array<RepositoryContributorNode>;
  updatedAt: Scalars['Float']['output'];
  url: Scalars['String']['output'];
};

export type CommitteeNode = Node & {
  __typename: 'CommitteeNode';
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
  __typename: 'CreateApiKeyResult';
  apiKey: Maybe<ApiKeyNode>;
  code: Maybe<Scalars['String']['output']>;
  message: Maybe<Scalars['String']['output']>;
  ok: Scalars['Boolean']['output'];
  rawKey: Maybe<Scalars['String']['output']>;
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
  __typename: 'EventNode';
  category: Scalars['String']['output'];
  description: Scalars['String']['output'];
  endDate: Maybe<Scalars['Date']['output']>;
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
  __typename: 'GeoLocationType';
  lat: Scalars['Float']['output'];
  lng: Scalars['Float']['output'];
};

export type GitHubAuthResult = {
  __typename: 'GitHubAuthResult';
  message: Scalars['String']['output'];
  ok: Scalars['Boolean']['output'];
  user: Maybe<AuthUserNode>;
};

export type IssueNode = Node & {
  __typename: 'IssueNode';
  author: Maybe<UserNode>;
  createdAt: Scalars['DateTime']['output'];
  /** The Globally Unique ID of this object */
  id: Scalars['ID']['output'];
  organizationName: Maybe<Scalars['String']['output']>;
  repositoryName: Maybe<Scalars['String']['output']>;
  state: Scalars['String']['output'];
  title: Scalars['String']['output'];
  url: Scalars['String']['output'];
};

export type LogoutResult = {
  __typename: 'LogoutResult';
  code: Maybe<Scalars['String']['output']>;
  message: Maybe<Scalars['String']['output']>;
  ok: Scalars['Boolean']['output'];
};

export type MentorNode = {
  __typename: 'MentorNode';
  avatarUrl: Scalars['String']['output'];
  id: Scalars['ID']['output'];
  login: Scalars['String']['output'];
  name: Scalars['String']['output'];
};

export type MilestoneNode = Node & {
  __typename: 'MilestoneNode';
  author: Maybe<UserNode>;
  body: Scalars['String']['output'];
  closedIssuesCount: Scalars['Int']['output'];
  createdAt: Scalars['DateTime']['output'];
  /** The Globally Unique ID of this object */
  id: Scalars['ID']['output'];
  openIssuesCount: Scalars['Int']['output'];
  organizationName: Maybe<Scalars['String']['output']>;
  progress: Scalars['Float']['output'];
  repositoryName: Maybe<Scalars['String']['output']>;
  state: Scalars['String']['output'];
  title: Scalars['String']['output'];
  url: Scalars['String']['output'];
};

export type ModuleNode = {
  __typename: 'ModuleNode';
  description: Scalars['String']['output'];
  domains: Maybe<Array<Scalars['String']['output']>>;
  endedAt: Scalars['DateTime']['output'];
  experienceLevel: ExperienceLevelEnum;
  id: Scalars['ID']['output'];
  key: Scalars['String']['output'];
  mentors: Array<MentorNode>;
  name: Scalars['String']['output'];
  program: Maybe<ProgramNode>;
  projectId: Maybe<Scalars['ID']['output']>;
  projectName: Maybe<Scalars['String']['output']>;
  startedAt: Scalars['DateTime']['output'];
  tags: Maybe<Array<Scalars['String']['output']>>;
};

export type Mutation = {
  __typename: 'Mutation';
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
  __typename: 'OrganizationNode';
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
  __typename: 'OrganizationStatsNode';
  totalContributors: Scalars['Int']['output'];
  totalForks: Scalars['Int']['output'];
  totalIssues: Scalars['Int']['output'];
  totalRepositories: Scalars['Int']['output'];
  totalStars: Scalars['Int']['output'];
};

export type PaginatedPrograms = {
  __typename: 'PaginatedPrograms';
  currentPage: Scalars['Int']['output'];
  programs: Array<ProgramNode>;
  totalPages: Scalars['Int']['output'];
};

export type PostNode = Node & {
  __typename: 'PostNode';
  authorImageUrl: Scalars['String']['output'];
  authorName: Scalars['String']['output'];
  /** The Globally Unique ID of this object */
  id: Scalars['ID']['output'];
  publishedAt: Scalars['DateTime']['output'];
  title: Scalars['String']['output'];
  url: Scalars['String']['output'];
};

export type ProgramNode = {
  __typename: 'ProgramNode';
  admins: Maybe<Array<MentorNode>>;
  description: Scalars['String']['output'];
  domains: Maybe<Array<Scalars['String']['output']>>;
  endedAt: Scalars['DateTime']['output'];
  experienceLevels: Maybe<Array<ExperienceLevelEnum>>;
  id: Scalars['ID']['output'];
  key: Scalars['String']['output'];
  menteesLimit: Maybe<Scalars['Int']['output']>;
  name: Scalars['String']['output'];
  startedAt: Scalars['DateTime']['output'];
  status: ProgramStatusEnum;
  tags: Maybe<Array<Scalars['String']['output']>>;
  userRole: Maybe<Scalars['String']['output']>;
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
  __typename: 'ProjectHealthMetricsNode';
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
  score: Maybe<Scalars['Float']['output']>;
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
  __typename: 'ProjectHealthStatsNode';
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
  __typename: 'ProjectNode';
  contributorsCount: Scalars['Int']['output'];
  createdAt: Maybe<Scalars['DateTime']['output']>;
  forksCount: Scalars['Int']['output'];
  healthMetricsLatest: Maybe<ProjectHealthMetricsNode>;
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
  __typename: 'PullRequestNode';
  author: Maybe<UserNode>;
  createdAt: Scalars['DateTime']['output'];
  /** The Globally Unique ID of this object */
  id: Scalars['ID']['output'];
  organizationName: Maybe<Scalars['String']['output']>;
  repositoryName: Maybe<Scalars['String']['output']>;
  title: Scalars['String']['output'];
  url: Scalars['String']['output'];
};

export type Query = {
  __typename: 'Query';
  activeApiKeyCount: Scalars['Int']['output'];
  apiKeys: Array<ApiKeyNode>;
  chapter: Maybe<ChapterNode>;
  committee: Maybe<CommitteeNode>;
  getModule: ModuleNode;
  getProgram: ProgramNode;
  getProgramModules: Array<ModuleNode>;
  getProjectModules: Array<ModuleNode>;
  isMentor: Scalars['Boolean']['output'];
  isProjectLeader: Scalars['Boolean']['output'];
  myPrograms: PaginatedPrograms;
  organization: Maybe<OrganizationNode>;
  project: Maybe<ProjectNode>;
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
  repository: Maybe<RepositoryNode>;
  searchProjects: Array<ProjectNode>;
  snapshot: Maybe<SnapshotNode>;
  snapshots: Array<SnapshotNode>;
  sponsors: Array<SponsorNode>;
  statsOverview: StatsNode;
  topContributedRepositories: Array<RepositoryNode>;
  topContributors: Array<RepositoryContributorNode>;
  upcomingEvents: Array<EventNode>;
  user: Maybe<UserNode>;
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
  __typename: 'ReleaseNode';
  author: Maybe<UserNode>;
  /** The Globally Unique ID of this object */
  id: Scalars['ID']['output'];
  isPreRelease: Scalars['Boolean']['output'];
  name: Scalars['String']['output'];
  organizationName: Maybe<Scalars['String']['output']>;
  projectName: Maybe<Scalars['String']['output']>;
  publishedAt: Maybe<Scalars['DateTime']['output']>;
  repositoryName: Maybe<Scalars['String']['output']>;
  tagName: Scalars['String']['output'];
  url: Scalars['String']['output'];
};

export type RepositoryContributorNode = {
  __typename: 'RepositoryContributorNode';
  avatarUrl: Scalars['String']['output'];
  contributionsCount: Scalars['Int']['output'];
  login: Scalars['String']['output'];
  name: Scalars['String']['output'];
  projectKey: Scalars['String']['output'];
  projectName: Scalars['String']['output'];
};

export type RepositoryNode = Node & {
  __typename: 'RepositoryNode';
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
  organization: Maybe<OrganizationNode>;
  ownerKey: Scalars['String']['output'];
  project: Maybe<ProjectNode>;
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
  __typename: 'RevokeApiKeyResult';
  code: Maybe<Scalars['String']['output']>;
  message: Maybe<Scalars['String']['output']>;
  ok: Scalars['Boolean']['output'];
};

export type SnapshotNode = Node & {
  __typename: 'SnapshotNode';
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
  __typename: 'SponsorNode';
  /** The Globally Unique ID of this object */
  id: Scalars['ID']['output'];
  imageUrl: Scalars['String']['output'];
  name: Scalars['String']['output'];
  sponsorType: Scalars['String']['output'];
  url: Scalars['String']['output'];
};

export type StatsNode = {
  __typename: 'StatsNode';
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
  __typename: 'UserNode';
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

export type UpdateModuleMutationVariables = Exact<{
  input: UpdateModuleInput;
}>;


export type UpdateModuleMutation = { updateModule: { __typename: 'ModuleNode', id: string, key: string, name: string, description: string, experienceLevel: ExperienceLevelEnum, startedAt: unknown, endedAt: unknown, tags: Array<string> | null, domains: Array<string> | null, projectId: string | null, mentors: Array<{ __typename: 'MentorNode', login: string, name: string, avatarUrl: string }> } };

export type CreateModuleMutationVariables = Exact<{
  input: CreateModuleInput;
}>;


export type CreateModuleMutation = { createModule: { __typename: 'ModuleNode', id: string, key: string, name: string, description: string, experienceLevel: ExperienceLevelEnum, startedAt: unknown, endedAt: unknown, domains: Array<string> | null, tags: Array<string> | null, projectId: string | null, mentors: Array<{ __typename: 'MentorNode', login: string, name: string, avatarUrl: string }> } };

export type UpdateProgramMutationVariables = Exact<{
  input: UpdateProgramInput;
}>;


export type UpdateProgramMutation = { updateProgram: { __typename: 'ProgramNode', key: string, name: string, description: string, status: ProgramStatusEnum, menteesLimit: number | null, startedAt: unknown, endedAt: unknown, tags: Array<string> | null, domains: Array<string> | null, admins: Array<{ __typename: 'MentorNode', login: string }> | null } };

export type CreateProgramMutationVariables = Exact<{
  input: CreateProgramInput;
}>;


export type CreateProgramMutation = { createProgram: { __typename: 'ProgramNode', id: string, key: string, name: string, description: string, menteesLimit: number | null, startedAt: unknown, endedAt: unknown, tags: Array<string> | null, domains: Array<string> | null, admins: Array<{ __typename: 'MentorNode', login: string, name: string, avatarUrl: string }> | null } };

export type UpdateProgramStatusMutationVariables = Exact<{
  inputData: UpdateProgramStatusInput;
}>;


export type UpdateProgramStatusMutation = { updateProgramStatus: { __typename: 'ProgramNode', key: string, status: ProgramStatusEnum } };

export type GetApiKeysQueryVariables = Exact<{ [key: string]: never; }>;


export type GetApiKeysQuery = { activeApiKeyCount: number, apiKeys: Array<{ __typename: 'ApiKeyNode', createdAt: unknown, expiresAt: unknown, isRevoked: boolean, name: string, uuid: unknown }> };

export type CreateApiKeyMutationVariables = Exact<{
  name: Scalars['String']['input'];
  expiresAt: Scalars['DateTime']['input'];
}>;


export type CreateApiKeyMutation = { createApiKey: { __typename: 'CreateApiKeyResult', code: string | null, message: string | null, ok: boolean, rawKey: string | null, apiKey: { __typename: 'ApiKeyNode', createdAt: unknown, expiresAt: unknown, isRevoked: boolean, name: string, uuid: unknown } | null } };

export type RevokeApiKeyMutationVariables = Exact<{
  uuid: Scalars['UUID']['input'];
}>;


export type RevokeApiKeyMutation = { revokeApiKey: { __typename: 'RevokeApiKeyResult', code: string | null, message: string | null, ok: boolean } };

export type LogoutDjangoMutationVariables = Exact<{ [key: string]: never; }>;


export type LogoutDjangoMutation = { logoutUser: { __typename: 'LogoutResult', code: string | null, message: string | null, ok: boolean } };

export type SyncDjangoSessionMutationVariables = Exact<{
  accessToken: Scalars['String']['input'];
}>;


export type SyncDjangoSessionMutation = { githubAuth: { __typename: 'GitHubAuthResult', message: string, ok: boolean, user: { __typename: 'AuthUserNode', isOwaspStaff: boolean } | null } };

export type GetChapterDataQueryVariables = Exact<{
  key: Scalars['String']['input'];
}>;


export type GetChapterDataQuery = { chapter: { __typename: 'ChapterNode', isActive: boolean, key: string, name: string, region: string, relatedUrls: Array<string>, suggestedLocation: string | null, summary: string, updatedAt: number, url: string, geoLocation: { __typename: 'GeoLocationType', lat: number, lng: number } | null } | null, topContributors: Array<{ __typename: 'RepositoryContributorNode', avatarUrl: string, login: string, name: string }> };

export type GetChapterMetadataQueryVariables = Exact<{
  key: Scalars['String']['input'];
}>;


export type GetChapterMetadataQuery = { chapter: { __typename: 'ChapterNode', name: string, summary: string } | null };

export type GetCommitteeDataQueryVariables = Exact<{
  key: Scalars['String']['input'];
}>;


export type GetCommitteeDataQuery = { committee: { __typename: 'CommitteeNode', contributorsCount: number, createdAt: number, forksCount: number, issuesCount: number, leaders: Array<string>, name: string, relatedUrls: Array<string>, repositoriesCount: number, starsCount: number, summary: string, updatedAt: number, url: string } | null, topContributors: Array<{ __typename: 'RepositoryContributorNode', avatarUrl: string, login: string, name: string }> };

export type GetCommitteeMetadataQueryVariables = Exact<{
  key: Scalars['String']['input'];
}>;


export type GetCommitteeMetadataQuery = { committee: { __typename: 'CommitteeNode', name: string, summary: string } | null };

export type GetMainPageDataQueryVariables = Exact<{
  distinct?: InputMaybe<Scalars['Boolean']['input']>;
}>;


export type GetMainPageDataQuery = { recentProjects: Array<{ __typename: 'ProjectNode', createdAt: unknown | null, key: string, leaders: Array<string>, name: string, openIssuesCount: number, repositoriesCount: number, type: string }>, recentPosts: Array<{ __typename: 'PostNode', authorName: string, authorImageUrl: string, publishedAt: unknown, title: string, url: string }>, recentChapters: Array<{ __typename: 'ChapterNode', createdAt: number, key: string, leaders: Array<string>, name: string, suggestedLocation: string | null }>, topContributors: Array<{ __typename: 'RepositoryContributorNode', avatarUrl: string, login: string, name: string }>, recentIssues: Array<{ __typename: 'IssueNode', createdAt: unknown, organizationName: string | null, repositoryName: string | null, title: string, url: string, author: { __typename: 'UserNode', avatarUrl: string, login: string, name: string } | null }>, recentPullRequests: Array<{ __typename: 'PullRequestNode', createdAt: unknown, organizationName: string | null, repositoryName: string | null, title: string, url: string, author: { __typename: 'UserNode', avatarUrl: string, login: string, name: string } | null }>, recentReleases: Array<{ __typename: 'ReleaseNode', name: string, organizationName: string | null, publishedAt: unknown | null, repositoryName: string | null, tagName: string, url: string, author: { __typename: 'UserNode', avatarUrl: string, login: string, name: string } | null }>, sponsors: Array<{ __typename: 'SponsorNode', imageUrl: string, name: string, sponsorType: string, url: string }>, statsOverview: { __typename: 'StatsNode', activeChaptersStats: number, activeProjectsStats: number, contributorsStats: number, countriesStats: number, slackWorkspaceStats: number }, upcomingEvents: Array<{ __typename: 'EventNode', category: string, endDate: unknown | null, key: string, name: string, startDate: unknown, summary: string, suggestedLocation: string, url: string }>, recentMilestones: Array<{ __typename: 'MilestoneNode', title: string, openIssuesCount: number, closedIssuesCount: number, repositoryName: string | null, organizationName: string | null, createdAt: unknown, url: string, author: { __typename: 'UserNode', avatarUrl: string, login: string, name: string } | null }> };

export type IsProjectLeaderQueryVariables = Exact<{
  login: Scalars['String']['input'];
}>;


export type IsProjectLeaderQuery = { isProjectLeader: boolean };

export type IsMentorQueryVariables = Exact<{
  login: Scalars['String']['input'];
}>;


export type IsMentorQuery = { isMentor: boolean };

export type GetModulesByProgramQueryVariables = Exact<{
  programKey: Scalars['String']['input'];
}>;


export type GetModulesByProgramQuery = { getProgramModules: Array<{ __typename: 'ModuleNode', id: string, key: string, name: string, description: string, experienceLevel: ExperienceLevelEnum, startedAt: unknown, endedAt: unknown, projectId: string | null, projectName: string | null, mentors: Array<{ __typename: 'MentorNode', id: string, login: string, avatarUrl: string }> }> };

export type GetModuleByIdQueryVariables = Exact<{
  moduleKey: Scalars['String']['input'];
  programKey: Scalars['String']['input'];
}>;


export type GetModuleByIdQuery = { getModule: { __typename: 'ModuleNode', id: string, key: string, name: string, description: string, tags: Array<string> | null, domains: Array<string> | null, experienceLevel: ExperienceLevelEnum, startedAt: unknown, endedAt: unknown, mentors: Array<{ __typename: 'MentorNode', login: string, name: string, avatarUrl: string }> } };

export type GetProgramAdminsAndModulesQueryVariables = Exact<{
  programKey: Scalars['String']['input'];
  moduleKey: Scalars['String']['input'];
}>;


export type GetProgramAdminsAndModulesQuery = { getProgram: { __typename: 'ProgramNode', id: string, admins: Array<{ __typename: 'MentorNode', login: string, name: string, avatarUrl: string }> | null }, getModule: { __typename: 'ModuleNode', id: string, key: string, name: string, description: string, tags: Array<string> | null, projectId: string | null, projectName: string | null, domains: Array<string> | null, experienceLevel: ExperienceLevelEnum, startedAt: unknown, endedAt: unknown, mentors: Array<{ __typename: 'MentorNode', login: string, name: string, avatarUrl: string }> } };

export type GetOrganizationDataQueryVariables = Exact<{
  login: Scalars['String']['input'];
}>;


export type GetOrganizationDataQuery = { organization: { __typename: 'OrganizationNode', avatarUrl: string, collaboratorsCount: number, company: string, createdAt: unknown, description: string, email: string, followersCount: number, location: string, login: string, name: string, updatedAt: unknown, url: string, stats: { __typename: 'OrganizationStatsNode', totalContributors: number, totalForks: number, totalIssues: number, totalRepositories: number, totalStars: number } } | null, topContributors: Array<{ __typename: 'RepositoryContributorNode', avatarUrl: string, login: string, name: string }>, recentPullRequests: Array<{ __typename: 'PullRequestNode', createdAt: unknown, organizationName: string | null, repositoryName: string | null, title: string, url: string, author: { __typename: 'UserNode', avatarUrl: string, login: string, name: string } | null }>, recentReleases: Array<{ __typename: 'ReleaseNode', name: string, organizationName: string | null, publishedAt: unknown | null, repositoryName: string | null, tagName: string, url: string, author: { __typename: 'UserNode', avatarUrl: string, login: string, name: string } | null }>, recentMilestones: Array<{ __typename: 'MilestoneNode', title: string, openIssuesCount: number, closedIssuesCount: number, repositoryName: string | null, organizationName: string | null, createdAt: unknown, url: string, author: { __typename: 'UserNode', avatarUrl: string, login: string, name: string } | null }>, repositories: Array<{ __typename: 'RepositoryNode', contributorsCount: number, forksCount: number, key: string, name: string, openIssuesCount: number, starsCount: number, url: string, organization: { __typename: 'OrganizationNode', login: string } | null }>, recentIssues: Array<{ __typename: 'IssueNode', createdAt: unknown, organizationName: string | null, repositoryName: string | null, title: string, url: string, author: { __typename: 'UserNode', avatarUrl: string, login: string, name: string } | null }> };

export type GetOrganizationMetadataQueryVariables = Exact<{
  login: Scalars['String']['input'];
}>;


export type GetOrganizationMetadataQuery = { organization: { __typename: 'OrganizationNode', description: string, login: string, name: string } | null };

export type GetMyProgramsQueryVariables = Exact<{
  search?: InputMaybe<Scalars['String']['input']>;
  page?: InputMaybe<Scalars['Int']['input']>;
  limit?: InputMaybe<Scalars['Int']['input']>;
}>;


export type GetMyProgramsQuery = { myPrograms: { __typename: 'PaginatedPrograms', currentPage: number, totalPages: number, programs: Array<{ __typename: 'ProgramNode', id: string, key: string, name: string, description: string, startedAt: unknown, endedAt: unknown, userRole: string | null }> } };

export type GetProgramDetailsQueryVariables = Exact<{
  programKey: Scalars['String']['input'];
}>;


export type GetProgramDetailsQuery = { getProgram: { __typename: 'ProgramNode', id: string, key: string, name: string, description: string, status: ProgramStatusEnum, menteesLimit: number | null, experienceLevels: Array<ExperienceLevelEnum> | null, startedAt: unknown, endedAt: unknown, domains: Array<string> | null, tags: Array<string> | null, admins: Array<{ __typename: 'MentorNode', login: string, name: string, avatarUrl: string }> | null } };

export type GetProgramAndModulesQueryVariables = Exact<{
  programKey: Scalars['String']['input'];
}>;


export type GetProgramAndModulesQuery = { getProgram: { __typename: 'ProgramNode', id: string, key: string, name: string, description: string, status: ProgramStatusEnum, menteesLimit: number | null, experienceLevels: Array<ExperienceLevelEnum> | null, startedAt: unknown, endedAt: unknown, domains: Array<string> | null, tags: Array<string> | null, admins: Array<{ __typename: 'MentorNode', login: string, name: string, avatarUrl: string }> | null }, getProgramModules: Array<{ __typename: 'ModuleNode', id: string, key: string, name: string, description: string, experienceLevel: ExperienceLevelEnum, startedAt: unknown, endedAt: unknown, mentors: Array<{ __typename: 'MentorNode', login: string, name: string, avatarUrl: string }> }> };

export type GetProgramAdminDetailsQueryVariables = Exact<{
  programKey: Scalars['String']['input'];
}>;


export type GetProgramAdminDetailsQuery = { getProgram: { __typename: 'ProgramNode', id: string, key: string, name: string, admins: Array<{ __typename: 'MentorNode', login: string, name: string, avatarUrl: string }> | null } };

export type GetProjectQueryVariables = Exact<{
  key: Scalars['String']['input'];
}>;


export type GetProjectQuery = { project: { __typename: 'ProjectNode', contributorsCount: number, forksCount: number, issuesCount: number, isActive: boolean, key: string, languages: Array<string>, leaders: Array<string>, level: string, name: string, repositoriesCount: number, starsCount: number, summary: string, topics: Array<string>, type: string, updatedAt: number, url: string, healthMetricsList: Array<{ __typename: 'ProjectHealthMetricsNode', createdAt: unknown, forksCount: number, lastCommitDays: number, lastCommitDaysRequirement: number, lastReleaseDays: number, lastReleaseDaysRequirement: number, openIssuesCount: number, openPullRequestsCount: number, score: number | null, starsCount: number, unassignedIssuesCount: number, unansweredIssuesCount: number }>, recentIssues: Array<{ __typename: 'IssueNode', createdAt: unknown, organizationName: string | null, repositoryName: string | null, title: string, url: string, author: { __typename: 'UserNode', avatarUrl: string, login: string, name: string, url: string } | null }>, recentReleases: Array<{ __typename: 'ReleaseNode', name: string, organizationName: string | null, publishedAt: unknown | null, repositoryName: string | null, tagName: string, url: string, author: { __typename: 'UserNode', avatarUrl: string, login: string, name: string } | null }>, repositories: Array<{ __typename: 'RepositoryNode', contributorsCount: number, forksCount: number, key: string, name: string, openIssuesCount: number, starsCount: number, subscribersCount: number, url: string, organization: { __typename: 'OrganizationNode', login: string } | null }>, recentMilestones: Array<{ __typename: 'MilestoneNode', title: string, openIssuesCount: number, closedIssuesCount: number, repositoryName: string | null, organizationName: string | null, createdAt: unknown, url: string, author: { __typename: 'UserNode', avatarUrl: string, login: string, name: string } | null }>, recentPullRequests: Array<{ __typename: 'PullRequestNode', createdAt: unknown, organizationName: string | null, repositoryName: string | null, title: string, url: string, author: { __typename: 'UserNode', avatarUrl: string, login: string, name: string } | null }> } | null, topContributors: Array<{ __typename: 'RepositoryContributorNode', avatarUrl: string, login: string, name: string }> };

export type GetProjectMetadataQueryVariables = Exact<{
  key: Scalars['String']['input'];
}>;


export type GetProjectMetadataQuery = { project: { __typename: 'ProjectNode', contributorsCount: number, forksCount: number, issuesCount: number, name: string, starsCount: number, summary: string, recentMilestones: Array<{ __typename: 'MilestoneNode', title: string, url: string, body: string, progress: number, state: string }> } | null };

export type GetTopContributorsQueryVariables = Exact<{
  excludedUsernames?: InputMaybe<Array<Scalars['String']['input']> | Scalars['String']['input']>;
  hasFullName?: InputMaybe<Scalars['Boolean']['input']>;
  key: Scalars['String']['input'];
  limit?: InputMaybe<Scalars['Int']['input']>;
}>;


export type GetTopContributorsQuery = { topContributors: Array<{ __typename: 'RepositoryContributorNode', avatarUrl: string, login: string, name: string }> };

export type SearchProjectNamesQueryVariables = Exact<{
  query: Scalars['String']['input'];
}>;


export type SearchProjectNamesQuery = { searchProjects: Array<{ __typename: 'ProjectNode', id: string, name: string }> };

export type GetProjectHealthStatsQueryVariables = Exact<{ [key: string]: never; }>;


export type GetProjectHealthStatsQuery = { projectHealthStats: { __typename: 'ProjectHealthStatsNode', averageScore: number, monthlyOverallScores: Array<number>, monthlyOverallScoresMonths: Array<number>, projectsCountHealthy: number, projectsCountNeedAttention: number, projectsCountUnhealthy: number, projectsPercentageHealthy: number, projectsPercentageNeedAttention: number, projectsPercentageUnhealthy: number, totalContributors: number, totalForks: number, totalStars: number } };

export type GetProjectHealthMetricsQueryVariables = Exact<{
  filters: ProjectHealthMetricsFilter;
  pagination: OffsetPaginationInput;
  ordering?: InputMaybe<Array<ProjectHealthMetricsOrder> | ProjectHealthMetricsOrder>;
}>;


export type GetProjectHealthMetricsQuery = { projectHealthMetricsDistinctLength: number, projectHealthMetrics: Array<{ __typename: 'ProjectHealthMetricsNode', createdAt: unknown, contributorsCount: number, forksCount: number, id: string, projectKey: string, projectName: string, score: number | null, starsCount: number }> };

export type ProjectQueryVariables = Exact<{
  projectKey: Scalars['String']['input'];
}>;


export type ProjectQuery = { project: { __typename: 'ProjectNode', healthMetricsLatest: { __typename: 'ProjectHealthMetricsNode', ageDays: number, ageDaysRequirement: number, isFundingRequirementsCompliant: boolean, isLeaderRequirementsCompliant: boolean, lastCommitDays: number, lastCommitDaysRequirement: number, lastPullRequestDays: number, lastPullRequestDaysRequirement: number, lastReleaseDays: number, lastReleaseDaysRequirement: number, owaspPageLastUpdateDays: number, owaspPageLastUpdateDaysRequirement: number, projectName: string, score: number | null } | null, healthMetricsList: Array<{ __typename: 'ProjectHealthMetricsNode', contributorsCount: number, createdAt: unknown, forksCount: number, openIssuesCount: number, openPullRequestsCount: number, recentReleasesCount: number, starsCount: number, totalIssuesCount: number, totalReleasesCount: number, unassignedIssuesCount: number, unansweredIssuesCount: number }> } | null };

export type GetRepositoryDataQueryVariables = Exact<{
  repositoryKey: Scalars['String']['input'];
  organizationKey: Scalars['String']['input'];
}>;


export type GetRepositoryDataQuery = { repository: { __typename: 'RepositoryNode', commitsCount: number, contributorsCount: number, createdAt: unknown, description: string, forksCount: number, key: string, languages: Array<string>, license: string, name: string, openIssuesCount: number, size: number, starsCount: number, topics: Array<string>, updatedAt: unknown, url: string, issues: Array<{ __typename: 'IssueNode', organizationName: string | null, repositoryName: string | null, createdAt: unknown, title: string, author: { __typename: 'UserNode', avatarUrl: string, login: string, name: string } | null }>, organization: { __typename: 'OrganizationNode', login: string } | null, project: { __typename: 'ProjectNode', key: string, name: string } | null, releases: Array<{ __typename: 'ReleaseNode', isPreRelease: boolean, name: string, organizationName: string | null, publishedAt: unknown | null, repositoryName: string | null, tagName: string, author: { __typename: 'UserNode', avatarUrl: string, name: string, login: string } | null }>, recentMilestones: Array<{ __typename: 'MilestoneNode', title: string, openIssuesCount: number, closedIssuesCount: number, repositoryName: string | null, organizationName: string | null, createdAt: unknown, url: string, author: { __typename: 'UserNode', avatarUrl: string, login: string, name: string } | null }> } | null, topContributors: Array<{ __typename: 'RepositoryContributorNode', avatarUrl: string, login: string, name: string }>, recentPullRequests: Array<{ __typename: 'PullRequestNode', createdAt: unknown, organizationName: string | null, repositoryName: string | null, title: string, url: string, author: { __typename: 'UserNode', avatarUrl: string, login: string, name: string } | null }> };

export type GetRepositoryMetadataQueryVariables = Exact<{
  repositoryKey: Scalars['String']['input'];
  organizationKey: Scalars['String']['input'];
}>;


export type GetRepositoryMetadataQuery = { repository: { __typename: 'RepositoryNode', description: string, name: string } | null };

export type GetSnapshotDetailsQueryVariables = Exact<{
  key: Scalars['String']['input'];
}>;


export type GetSnapshotDetailsQuery = { snapshot: { __typename: 'SnapshotNode', endAt: unknown, key: string, startAt: unknown, title: string, newReleases: Array<{ __typename: 'ReleaseNode', name: string, publishedAt: unknown | null, tagName: string, projectName: string | null }>, newProjects: Array<{ __typename: 'ProjectNode', key: string, name: string, summary: string, starsCount: number, forksCount: number, contributorsCount: number, level: string, isActive: boolean, repositoriesCount: number, topContributors: Array<{ __typename: 'RepositoryContributorNode', avatarUrl: string, login: string, name: string }> }>, newChapters: Array<{ __typename: 'ChapterNode', key: string, name: string, createdAt: number, suggestedLocation: string | null, region: string, summary: string, updatedAt: number, url: string, relatedUrls: Array<string>, isActive: boolean, topContributors: Array<{ __typename: 'RepositoryContributorNode', avatarUrl: string, login: string, name: string }>, geoLocation: { __typename: 'GeoLocationType', lat: number, lng: number } | null }> } | null };

export type GetSnapshotDetailsMetadataQueryVariables = Exact<{
  key: Scalars['String']['input'];
}>;


export type GetSnapshotDetailsMetadataQuery = { snapshot: { __typename: 'SnapshotNode', title: string } | null };

export type GetCommunitySnapshotsQueryVariables = Exact<{ [key: string]: never; }>;


export type GetCommunitySnapshotsQuery = { snapshots: Array<{ __typename: 'SnapshotNode', key: string, title: string, startAt: unknown, endAt: unknown }> };

export type GetLeaderDataQueryVariables = Exact<{
  key: Scalars['String']['input'];
}>;


export type GetLeaderDataQuery = { user: { __typename: 'UserNode', avatarUrl: string, login: string, name: string } | null };

export type GetUserDataQueryVariables = Exact<{
  key: Scalars['String']['input'];
}>;


export type GetUserDataQuery = { recentIssues: Array<{ __typename: 'IssueNode', createdAt: unknown, organizationName: string | null, repositoryName: string | null, title: string, url: string }>, recentMilestones: Array<{ __typename: 'MilestoneNode', title: string, openIssuesCount: number, closedIssuesCount: number, repositoryName: string | null, organizationName: string | null, createdAt: unknown, url: string }>, recentPullRequests: Array<{ __typename: 'PullRequestNode', createdAt: unknown, organizationName: string | null, repositoryName: string | null, title: string, url: string }>, recentReleases: Array<{ __typename: 'ReleaseNode', isPreRelease: boolean, name: string, publishedAt: unknown | null, organizationName: string | null, repositoryName: string | null, tagName: string, url: string }>, topContributedRepositories: Array<{ __typename: 'RepositoryNode', contributorsCount: number, forksCount: number, key: string, name: string, openIssuesCount: number, starsCount: number, subscribersCount: number, url: string, organization: { __typename: 'OrganizationNode', login: string } | null }>, user: { __typename: 'UserNode', avatarUrl: string, bio: string, company: string, contributionsCount: number, createdAt: number, email: string, followersCount: number, followingCount: number, issuesCount: number, location: string, login: string, name: string, publicRepositoriesCount: number, releasesCount: number, updatedAt: number, url: string } | null };

export type GetUserMetadataQueryVariables = Exact<{
  key: Scalars['String']['input'];
}>;


export type GetUserMetadataQuery = { user: { __typename: 'UserNode', bio: string, login: string, name: string } | null };
